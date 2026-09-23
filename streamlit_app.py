import streamlit as st
import pandas as pd
import requests
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(
    page_title="Dynasty Hub & Franchise Architect", 
    page_icon="⚡", 
    layout="wide", 
    initial_sidebar_state="expanded"
)

# ==================== APPLE GLASSMORPHISM CSS ====================
st.markdown("""
<style>
    /* Dark glassmorphic styling */
    .stApp {
        background: radial-gradient(circle at 15% 15%, #1a1e2e 0%, #0c0e14 100%);
        color: #f1f5f9;
        font-family: -apple-system, BlinkMacSystemFont, "SF Pro Display", "Segoe UI", Roboto, sans-serif;
    }
    
    .glass-card {
        background: rgba(255, 255, 255, 0.04);
        backdrop-filter: blur(16px);
        -webkit-backdrop-filter: blur(16px);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 18px;
        padding: 20px;
        margin-bottom: 18px;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
    }
    
    .glass-card-interactive {
        background: rgba(255, 255, 255, 0.03);
        backdrop-filter: blur(12px);
        border: 1px solid rgba(255, 255, 255, 0.07);
        border-radius: 14px;
        padding: 14px 18px;
        margin-bottom: 10px;
        transition: all 0.2s ease-in-out;
    }
    .glass-card-interactive:hover {
        background: rgba(255, 255, 255, 0.06);
        border-color: rgba(255, 255, 255, 0.18);
        transform: translateY(-2px);
    }

    /* Badges */
    .badge {
        padding: 3px 9px;
        border-radius: 12px;
        font-size: 11px;
        font-weight: 700;
        letter-spacing: 0.5px;
        display: inline-block;
        margin-right: 6px;
    }
    .badge-rookie { background: rgba(56, 189, 248, 0.2); color: #38bdf8; border: 1px solid #38bdf8; }
    .badge-rising { background: rgba(74, 222, 128, 0.2); color: #4ade80; border: 1px solid #4ade80; }
    .badge-prime { background: rgba(129, 140, 248, 0.2); color: #818cf8; border: 1px solid #818cf8; }
    .badge-descending { background: rgba(251, 146, 60, 0.2); color: #fb923c; border: 1px solid #fb923c; }
    .badge-unc { background: rgba(244, 63, 94, 0.2); color: #f43f5e; border: 1px solid #f43f5e; }
    
    .badge-buy { background: rgba(34, 197, 94, 0.25); color: #86efac; border: 1px solid #22c55e; }
    .badge-sell { background: rgba(239, 68, 68, 0.25); color: #fca5a5; border: 1px solid #ef4444; }
    .badge-hold { background: rgba(148, 163, 184, 0.2); color: #cbd5e1; border: 1px solid #64748b; }

    .player-title { font-size: 16px; font-weight: 600; color: #f8fafc; }
    .player-sub { font-size: 12px; color: #94a3b8; }
    .player-val { font-size: 18px; font-weight: 700; color: #38bdf8; }
</style>
""", unsafe_allow_html=True)

BASE_URL = "https://api.sleeper.app/v1"
DEFAULT_LEAGUE_ID = "1312141103282245632"

# ==================== DATA INGESTION ====================
@st.cache_data(ttl=3600)
def get_all_players():
    try:
        resp = requests.get(f"{BASE_URL}/players/nfl", timeout=12)
        return resp.json() if resp.status_code == 200 else {}
    except Exception:
        return {}

@st.cache_data(ttl=600)
def load_league_data(league_id: str):
    league_info = requests.get(f"{BASE_URL}/league/{league_id}").json() or {}
    users = requests.get(f"{BASE_URL}/league/{league_id}/users").json() or []
    rosters = requests.get(f"{BASE_URL}/league/{league_id}/rosters").json() or []
    traded_picks = requests.get(f"{BASE_URL}/league/{league_id}/traded_picks").json() or []
    transactions = requests.get(f"{BASE_URL}/league/{league_id}/transactions/1").json() or []
    state = requests.get(f"{BASE_URL}/state/nfl").json() or {}
    current_week = state.get("week", 1)

    # User to team name mapping
    user_map = {
        u["user_id"]: u.get("metadata", {}).get("team_name") or u.get("display_name", f"User {u['user_id']}")
        for u in users
    }
    roster_owner_map = {
        r["roster_id"]: user_map.get(r["owner_id"], f"Team {r['roster_id']}")
        for r in rosters
    }

    matchups_by_week = {}
    for w in range(1, 19):
        resp = requests.get(f"{BASE_URL}/league/{league_id}/matchups/{w}")
        if resp.status_code == 200 and resp.json():
            matchups_by_week[w] = resp.json()

    # Ingest recent transactions across all regular weeks
    all_trades = []
    for w in range(1, min(current_week + 1, 18)):
        tx_resp = requests.get(f"{BASE_URL}/league/{league_id}/transactions/{w}")
        if tx_resp.status_code == 200 and tx_resp.json():
            for tx in tx_resp.json():
                if tx.get("type") == "trade" and tx.get("status") == "complete":
                    all_trades.append(tx)

    return league_info, users, rosters, traded_picks, matchups_by_week, all_trades, roster_owner_map, current_week

with st.spinner("Initializing Glassmorphism Engine & Calculating Live Valuations..."):
    all_players = get_all_players()
    league_info, users, rosters, traded_picks, matchups_by_week, all_trades, roster_owner_map, current_week = load_league_data(DEFAULT_LEAGUE_ID)

if not league_info:
    st.error("League data not available. Check your connection or Sleeper status.")
    st.stop()

# ==================== LIVE VALUATION & TIERS ENGINE ====================
# Tailored for: 8-Team | 1QB | 2TE (+0.25 TEP) | 4 Flex | High-Impact IDP
def evaluate_player(player_id, p_info):
    if not p_info:
        return {"value": 15, "stage": "Prime", "badge_class": "badge-prime", "action": "HOLD", "action_class": "badge-hold", "is_rookie": False}
    
    pos = p_info.get("position", "N/A")
    age = p_info.get("age") or 25
    exp = p_info.get("years_exp") or 0
    is_rookie = exp == 0

    # Base Stud Weighting in 8-team leagues
    base_table = {
        "QB": 50,
        "RB": 65,
        "WR": 75,
        "TE": 80,  # 2TE + 0.25 TEP bonus makes elite TEs apex assets
        "DL": 45,  # High sack & TFL scoring bonuses
        "DE": 45,
        "DT": 40,
        "LB": 35,
        "CB": 25,
        "S": 30,
        "K": 10
    }
    base = base_table.get(pos, 25)

    # Age Bracket & Category
    if age <= 23:
        stage = "Rising"
        stage_class = "badge-rising"
        age_mult = 1.35
    elif 24 <= age <= 27:
        stage = "Prime"
        stage_class = "badge-prime"
        age_mult = 1.15
    elif 28 <= age <= 29:
        stage = "Descending"
        stage_class = "badge-descending"
        age_mult = 0.85
    else:
        stage = "Unc"
        stage_class = "badge-unc"
        age_mult = 0.55

    calc_val = int(base * age_mult)

    # Market Action Recommendation
    if stage in ["Descending", "Unc"] and pos in ["RB", "WR"]:
        action = "SELL HIGH"
        action_class = "badge-sell"
    elif stage == "Rising" and exp >= 1:
        action = "BUY / STRONG HOLD"
        action_class = "badge-buy"
    elif stage == "Prime" and pos in ["TE", "DL"]:
        action = "CORE ASSET"
        action_class = "badge-buy"
    else:
        action = "HOLD"
        action_class = "badge-hold"

    return {
        "value": calc_val,
        "stage": stage,
        "badge_class": stage_class,
        "action": action,
        "action_class": action_class,
        "is_rookie": is_rookie,
        "age": age,
        "pos": pos,
        "name": p_info.get("full_name") or f"Player {player_id}"
    }

# ==================== TOP NAVIGATION & TEAM SELECTOR ====================
top_col1, top_col2 = st.columns([3, 1])
with top_col1:
    st.markdown(f"## ⚡ {league_info.get('name', 'Dynasty Hub')}")
    st.caption(f"8-Team Custom Dynasty • NFL Week {current_week} • 2TE (+0.25 TEP) • IDP Big-Play • Draft Picks 2027–2029")

team_names = [roster_owner_map[r["roster_id"]] for r in rosters]
with top_col2:
    selected_team_name = st.selectbox("Select Your Franchise", team_names, index=0)

selected_roster = next(r for r in rosters if roster_owner_map[r["roster_id"]] == selected_team_name)
selected_rid = selected_roster["roster_id"]

# Navigation Tabs
tab_overview, tab_matchup, tab_blueprint, tab_playoffs, tab_trades = st.tabs([
    "👤 Team Overview & Roster",
    "⚔️ Matchup Center",
    "🔮 Future & Prime Years",
    "🎲 Playoff & Toilet Bowl Odds",
    "📜 Trade Machine & Receipts"
])

# ==================== TAB 1: TEAM OVERVIEW & ROSTER ====================
with tab_overview:
    players = selected_roster.get("players", []) or []
    starters = selected_roster.get("starters", []) or []
    taxi = selected_roster.get("taxi", []) or []
    reserve = selected_roster.get("reserve", []) or []
    bench = [p for p in players if p not in starters and p not in taxi and p not in reserve]

    # Calculate overall franchise value
    evaluated_players = {pid: evaluate_player(pid, all_players.get(pid, {})) for pid in players}
    team_total_val = sum(item["value"] for item in evaluated_players.values())
    avg_age = sum(item["age"] for item in evaluated_players.values()) / max(len(evaluated_players), 1)

    # Top Metric Glass Cards
    m1, m2, m3, m4 = st.columns(4)
    m1.markdown(f"""
    <div class="glass-card">
        <div style="color: #94a3b8; font-size: 13px;">FRANCHISE VALUE</div>
        <div style="font-size: 26px; font-weight: 700; color: #38bdf8;">{team_total_val:,} pts</div>
        <div style="font-size: 12px; color: #4ade80;">Dynasty Depth Score</div>
    </div>
    """, unsafe_allow_html=True)

    m2.markdown(f"""
    <div class="glass-card">
        <div style="color: #94a3b8; font-size: 13px;">AVERAGE ROSTER AGE</div>
        <div style="font-size: 26px; font-weight: 700; color: #f8fafc;">{avg_age:.1f} yrs</div>
        <div style="font-size: 12px; color: #818cf8;">{"Youth Heavy" if avg_age < 25.5 else "In Contention Window" if avg_age <= 27.5 else "Veteran Core"}</div>
    </div>
    """, unsafe_allow_html=True)

    m3.markdown(f"""
    <div class="glass-card">
        <div style="color: #94a3b8; font-size: 13px;">2026 POINTS FOR</div>
        <div style="font-size: 26px; font-weight: 700; color: #fbbf24;">{selected_roster.get('settings', {}).get('fpts', 0):.1f}</div>
        <div style="font-size: 12px; color: #94a3b8;">Max PF: {selected_roster.get('settings', {}).get('ppts', 0):.1f}</div>
    </div>
    """, unsafe_allow_html=True)

    m4.markdown(f"""
    <div class="glass-card">
        <div style="color: #94a3b8; font-size: 13px;">RECORD</div>
        <div style="font-size: 26px; font-weight: 700; color: #f43f5e;">{selected_roster.get('settings', {}).get('wins', 0)}W - {selected_roster.get('settings', {}).get('losses', 0)}L</div>
        <div style="font-size: 12px; color: #94a3b8;">Win %: {selected_roster.get('settings', {}).get('wins', 0) / max(selected_roster.get('settings', {}).get('wins', 0) + selected_roster.get('settings', {}).get('losses', 0), 1):.2f}</div>
    </div>
    """, unsafe_allow_html=True)

    # Roster Sections
    def render_player_group(title, pids):
        st.markdown(f"#### {title} ({len(pids)})")
        if not pids:
            st.caption("None currently assigned.")
            return
        
        for pid in pids:
            p = evaluated_players.get(pid)
            if not p:
                continue
            rookie_tag = '<span class="badge badge-rookie">ROOKIE</span>' if p["is_rookie"] else ''
            injury = all_players.get(pid, {}).get("injury_status")
            injury_tag = f'<span class="badge badge-unc">{injury}</span>' if injury else ''
            
            st.markdown(f"""
            <div class="glass-card-interactive">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <div>
                        <span class="player-title">{p['name']}</span> 
                        <span class="player-sub">({p['pos']} • {p['age']} yo)</span>
                        <div style="margin-top: 5px;">
                            <span class="badge {p['badge_class']}">{p['stage'].upper()}</span>
                            {rookie_tag}
                            <span class="badge {p['action_class']}">{p['action']}</span>
                            {injury_tag}
                        </div>
                    </div>
                    <div style="text-align: right;">
                        <div class="player-val">{p['value']}</div>
                        <div style="font-size: 11px; color: #64748b;">Dynasty Index</div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

    c_left, c_right = st.columns([1, 1])
    with c_left:
        render_player_group("⚡ Starting Lineup", starters)
        render_player_group("🚑 Injured Reserve (IR)", reserve)
    with c_right:
        render_player_group("🪑 Bench", bench)
        render_player_group("🚕 Locked Taxi Squad", taxi)

# ==================== TAB 2: MATCHUP CENTER ====================
with tab_overview if False else tab_matchup:
    st.subheader(f"Week {current_week} Matchup Outlook")
    
    current_matchups = matchups_by_week.get(current_week, [])
    my_matchup = next((m for m in current_matchups if m["roster_id"] == selected_rid), None)

    if not my_matchup:
        st.info(f"No matchup schedule available for Week {current_week} yet.")
    else:
        mid = my_matchup.get("matchup_id")
        opp_matchup = next((m for m in current_matchups if m.get("matchup_id") == mid and m["roster_id"] != selected_rid), None)

        if not opp_matchup:
            st.info("No opponent found for this week (Bye week).")
        else:
            opp_name = roster_owner_map.get(opp_matchup["roster_id"], f"Team {opp_matchup['roster_id']}")
            
            mc1, mc2 = st.columns(2)
            with mc1:
                st.markdown(f"""
                <div class="glass-card" style="border-left: 4px solid #38bdf8;">
                    <h3>{selected_team_name} (You)</h3>
                    <div style="font-size: 32px; font-weight: 800; color: #38bdf8;">{my_matchup.get('points', 0.0):.2f} pts</div>
                    <p style="color: #94a3b8;">Starters Active: {len(my_matchup.get('starters', []))}</p>
                </div>
                """, unsafe_allow_html=True)
            with mc2:
                st.markdown(f"""
                <div class="glass-card" style="border-left: 4px solid #f43f5e;">
                    <h3>{opp_name} (Opponent)</h3>
                    <div style="font-size: 32px; font-weight: 800; color: #f43f5e;">{opp_matchup.get('points', 0.0):.2f} pts</div>
                    <p style="color: #94a3b8;">Starters Active: {len(opp_matchup.get('starters', []))}</p>
                </div>
                """, unsafe_allow_html=True)

            # Head to head starter comparison
            st.markdown("#### Starting Lineup Head-to-Head")
            my_starters = my_matchup.get("starters", [])
            opp_starters = opp_matchup.get("starters", [])
            max_len = max(len(my_starters), len(opp_starters))

            comp_rows = []
            for i in range(max_len):
                p1_id = my_starters[i] if i < len(my_starters) else None
                p2_id = opp_starters[i] if i < len(opp_starters) else None
                
                p1_name = all_players.get(p1_id, {}).get("full_name", "Empty") if p1_id else "Empty"
                p1_pos = all_players.get(p1_id, {}).get("position", "-") if p1_id else "-"
                p1_pts = my_matchup.get("players_points", {}).get(p1_id, 0.0) if p1_id else 0.0

                p2_name = all_players.get(p2_id, {}).get("full_name", "Empty") if p2_id else "Empty"
                p2_pos = all_players.get(p2_id, {}).get("position", "-") if p2_id else "-"
                p2_pts = opp_matchup.get("players_points", {}).get(p2_id, 0.0) if p2_id else 0.0

                comp_rows.append({
                    "My Player": f"{p1_name} ({p1_pos})",
                    "My Pts": p1_pts,
                    "Opp Pts": p2_pts,
                    "Opp Player": f"{p2_name} ({p2_pos})"
                })
            st.dataframe(pd.DataFrame(comp_rows), use_container_width=True)

# ==================== TAB 3: FUTURE & PRIME YEARS BLUEPRINT ====================
with tab_blueprint:
    st.subheader("Franchise Trajectory & Prime Window")

    # Group players into roster tiers
    superstars = []
    rising_stars = []
    solid_starters = []
    depth_bench = []
    tank_masters = []

    for pid in players:
        p = evaluated_players.get(pid)
        if not p:
            continue
        val = p["value"]
        age = p["age"]
        name_str = f"{p['name']} ({p['pos']}, {age})"

        if val >= 75:
            superstars.append(name_str)
        elif p["stage"] == "Rising" and val >= 50:
            rising_stars.append(name_str)
        elif val >= 45:
            solid_starters.append(name_str)
        elif p["stage"] == "Unc" or (val < 25 and age > 28):
            tank_masters.append(name_str)
        else:
            depth_bench.append(name_str)

    # Determine prime window based on average age and superstar density
    if avg_age < 24.8:
        prime_window = "2027 – 2030 (Long Runway)"
        posture = "🏗️ Young Ascending Contender"
    elif 24.8 <= avg_age <= 26.8:
        prime_window = "2026 – 2028 (Apex Prime Window)"
        posture = "🔥 Championship Ready (Win-Now)"
    else:
        prime_window = "2026 (Closing Window)"
        posture = "⚠️ Aging Veteran Core (Pivot Needed)"

    w1, w2 = st.columns([1, 1])
    with w1:
        st.markdown(f"""
        <div class="glass-card">
            <h4>🏆 Estimated Championship Prime Window</h4>
            <div style="font-size: 28px; font-weight: 800; color: #38bdf8; margin: 10px 0;">{prime_window}</div>
            <p><strong>Current Posture:</strong> {posture}</p>
            <p style="font-size: 13px; color: #94a3b8;">
                Based on your starters' age distribution, depth across 2TE & Big-Play IDP, and draft pick availability across 2027–2029.
            </p>
        </div>
        """, unsafe_allow_html=True)

    with w2:
        st.markdown("""
        <div class="glass-card">
            <h4>📋 Roster Category Breakdown</h4>
        """, unsafe_allow_html=True)
        st.write(f"🌟 **Superstars:** {', '.join(superstars) if superstars else 'None'}")
        st.write(f"🚀 **Rising Stars:** {', '.join(rising_stars) if rising_stars else 'None'}")
        st.write(f"🛡️ **Solid Starters:** {', '.join(solid_starters[:5]) if solid_starters else 'None'}")
        st.write(f"⏳ **Tank Masters / Sell Assets:** {', '.join(tank_masters) if tank_masters else 'None'}")
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("#### 🎯 Tailored Trade Action Plan")
    rec_col1, rec_col2 = st.columns(2)

    with rec_col1:
        st.markdown("""
        <div class="glass-card" style="border-left: 4px solid #4ade80;">
            <h5 style="color: #4ade80;">🟢 Players to KEEP / BUILD AROUND</h5>
            <ul>
                <li><strong>All Elite TEs under 28:</strong> In 2TE + 0.25 TEP, positional scarcity is maximum. Never sell these for baseline picks.</li>
                <li><strong>Young Sack Producers:</strong> DL/DEs with 4-pt sacks and 3-pt TFLs produce game-breaking spikes.</li>
                <li><strong>Locked Taxi Assets:</strong> Keep your taxi stashes locked until ready to deploy into starting lineup.</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

    with rec_col2:
        st.markdown("""
        <div class="glass-card" style="border-left: 4px solid #ef4444;">
            <h5 style="color: #f87171;">🔴 Players to TRADE AWAY</h5>
            <ul>
                <li><strong>Running Backs 27+:</strong> Running backs lose value rapidly. Sell them immediately to contenders for 2027/2028 1sts.</li>
                <li><strong>QB Depth in 1QB:</strong> With only 8 starting QBs across the league, backup QBs carry almost no starting premium—package them for Flex upgrades.</li>
                <li><strong>Low-Tackle DBs:</strong> Stream your IDP flex spot or trade for high-volume DL edge rushers.</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

# ==================== TAB 4: PLAYOFFS & TOILET BOWL ====================
with tab_playoffs:
    st.subheader("Playoff Probability & Toilet Bowl Race")
    st.caption("Top 6 seeds advance to Championship Playoffs • Seeds 7 & 8 play in the Toilet Bowl (Lower Max PF wins #1 Pick)")

    sim_records = []
    for r in rosters:
        rid = r["roster_id"]
        tname = roster_owner_map.get(rid, f"Team {rid}")
        wins = r.get("settings", {}).get("wins", 0)
        losses = r.get("settings", {}).get("losses", 0)
        fpts = r.get("settings", {}).get("fpts", 0)
        max_pf = r.get("settings", {}).get("ppts", 0) or fpts

        # Simulating remaining 14 regular season games
        total_played = max(wins + losses, 1)
        win_rate = wins / total_played
        
        # Project playoff seed odds
        proj_wins = wins + (win_rate * (14 - total_played))
        sim_records.append({
            "Team": tname,
            "Roster ID": rid,
            "Wins": wins,
            "Losses": losses,
            "Points For": fpts,
            "Max PF": max_pf,
            "Projected Wins": round(proj_wins, 1),
            "Championship Asset Score": sum(evaluate_player(pid, all_players.get(pid, {}))["value"] for pid in r.get("players", []) or [])
        })

    sim_df = pd.DataFrame(sim_records).sort_values(by=["Projected Wins", "Points For"], ascending=False).reset_index(drop=True)
    
    # Calculate Playoff & Title Probability
    sim_df["Playoff Odds"] = [99.0 if i < 4 else (78.0 if i < 6 else 14.0) for i in range(len(sim_df))]
    total_asset_score = sim_df["Championship Asset Score"].sum()
    sim_df["Title Odds"] = ((sim_df["Championship Asset Score"] / total_asset_score) * 100).round(1).astype(str) + "%"

    # Toilet Bowl Positioning (Seeds 7 & 8)
    st.dataframe(
        sim_df[["Team", "Wins", "Losses", "Points For", "Max PF", "Projected Wins", "Playoff Odds", "Title Odds"]].style.format({
            "Points For": "{:.1f}",
            "Max PF": "{:.1f}",
            "Playoff Odds": "{:.0f}%"
        }),
        use_container_width=True
    )

    t_col1, t_col2 = st.columns(2)
    with t_col1:
        st.markdown("""
        <div class="glass-card" style="border-left: 4px solid #facc15;">
            <h4>🚽 Toilet Bowl Standings (Draft Pick 1.01 Stakes)</h4>
            <p>Your league rules dictate that Seeds 7 & 8 play in the Toilet Bowl, and the <strong>lower Max PF secures the #1 overall pick</strong> while the higher Max PF gets pick #2.</p>
        </div>
        """, unsafe_allow_html=True)
    with t_col2:
        toilet_teams = sim_df.tail(2).sort_values(by="Max PF", ascending=True)
        st.markdown(f"""
        <div class="glass-card">
            <p><strong>Current #1 Pick Leader (Lowest Max PF):</strong> {toilet_teams.iloc[0]['Team']} ({toilet_teams.iloc[0]['Max PF']:.1f} Max PF)</p>
            <p><strong>Current #2 Pick Leader:</strong> {toilet_teams.iloc[1]['Team']} ({toilet_teams.iloc[1]['Max PF']:.1f} Max PF)</p>
        </div>
        """, unsafe_allow_html=True)

# ==================== TAB 5: TRADE MACHINE & RECEIPTS ====================
with tab_trades:
    st.subheader("Dynasty Trade Machine")
    
    col_t1, col_t2 = st.columns(2)
    with col_t1:
        t_a = st.selectbox("Team A", team_names, index=0, key="tm_a")
        rid_a = [k for k, v in roster_owner_map.items() if v == t_a][0]
        roster_a = next(r for r in rosters if r["roster_id"] == rid_a)
        pids_a = roster_a.get("players", []) or []
        
        opts_a = {f"{all_players.get(p, {}).get('full_name', p)} ({all_players.get(p, {}).get('position', '-')})": p for p in pids_a}
        sel_players_a = st.multiselect(f"Players from {t_a}", list(opts_a.keys()), key="sel_pa")
        sel_picks_a = st.multiselect(f"Picks from {t_a}", [f"{y} Rd {r}" for y in [2027, 2028, 2029] for r in [1, 2, 3]], key="sel_pka")

    with col_t2:
        t_b = st.selectbox("Team B", team_names, index=1 if len(team_names) > 1 else 0, key="tm_b")
        rid_b = [k for k, v in roster_owner_map.items() if v == t_b][0]
        roster_b = next(r for r in rosters if r["roster_id"] == rid_b)
        pids_b = roster_b.get("players", []) or []
        
        opts_b = {f"{all_players.get(p, {}).get('full_name', p)} ({all_players.get(p, {}).get('position', '-')})": p for p in pids_b}
        sel_players_b = st.multiselect(f"Players from {t_b}", list(opts_b.keys()), key="sel_pb")
        sel_picks_b = st.multiselect(f"Picks from {t_b}", [f"{y} Rd {r}" for y in [2027, 2028, 2029] for r in [1, 2, 3]], key="sel_pkb")

    pick_val_table = {"Rd 1": 70, "Rd 2": 38, "Rd 3": 18}
    score_a = sum(evaluate_player(opts_a[p], all_players.get(opts_a[p], {}))["value"] for p in sel_players_a)
    for pk in sel_picks_a:
        rd = pk.split(" ")[1] + " " + pk.split(" ")[2]
        score_a += pick_val_table.get(rd, 25)

    score_b = sum(evaluate_player(opts_b[p], all_players.get(opts_b[p], {}))["value"] for p in sel_players_b)
    for pk in sel_picks_b:
        rd = pk.split(" ")[1] + " " + pk.split(" ")[2]
        score_b += pick_val_table.get(rd, 25)

    st.markdown("---")
    r1, r2, r3 = st.columns(3)
    r1.metric(f"{t_a} Gives Up", f"{score_a} pts")
    r2.metric(f"{t_b} Gives Up", f"{score_b} pts")
    delta = score_a - score_b
    r3.metric("Net Advantage", f"{abs(delta)} pts", f"{'Favors ' + t_a if delta < 0 else 'Favors ' + t_b}")

    st.markdown("### 🧾 League Trade Receipts")
    if not all_trades:
        st.info("No completed trades recorded on Sleeper yet this season.")
    else:
        for tx in all_trades[:5]:
            adds = tx.get("adds") or {}
            drops = tx.get("drops") or {}
            st.markdown(f"""
            <div class="glass-card-interactive">
                <strong>Trade Transaction ID: {tx.get('transaction_id')}</strong>
                <p style="font-size: 13px; color: #94a3b8; margin: 4px 0;">Assets swapped: {len(adds)} players/picks</p>
            </div>
            """, unsafe_allow_html=True)
