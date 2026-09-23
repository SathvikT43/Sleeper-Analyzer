import streamlit as st
import pandas as pd
import requests
import plotly.express as px

st.set_page_config(
    page_title="Dynasty Hub & Franchise Architect", 
    page_icon="⚡", 
    layout="wide", 
    initial_sidebar_state="expanded"
)

# ==================== APPLE GLASSMORPHISM CSS ====================
st.markdown("""
<style>
    .stApp {
        background: radial-gradient(circle at 15% 15%, #151824 0%, #0a0c10 100%);
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
        margin-bottom: 16px;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.35);
    }
    
    .glass-card-interactive {
        background: rgba(255, 255, 255, 0.03);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.07);
        border-radius: 14px;
        padding: 12px 16px;
        margin-bottom: 8px;
    }
    .glass-card-interactive:hover {
        background: rgba(255, 255, 255, 0.06);
        border-color: rgba(255, 255, 255, 0.16);
    }

    .badge {
        padding: 3px 8px;
        border-radius: 10px;
        font-size: 11px;
        font-weight: 700;
        display: inline-block;
        margin-right: 5px;
    }
    .badge-rookie { background: rgba(56, 189, 248, 0.2); color: #38bdf8; border: 1px solid #38bdf8; }
    .badge-rising { background: rgba(74, 222, 128, 0.2); color: #4ade80; border: 1px solid #4ade80; }
    .badge-prime { background: rgba(129, 140, 248, 0.2); color: #818cf8; border: 1px solid #818cf8; }
    .badge-descending { background: rgba(251, 146, 60, 0.2); color: #fb923c; border: 1px solid #fb923c; }
    .badge-unc { background: rgba(244, 63, 94, 0.2); color: #f43f5e; border: 1px solid #f43f5e; }
    
    .badge-buy { background: rgba(34, 197, 94, 0.2); color: #86efac; border: 1px solid #22c55e; }
    .badge-sell { background: rgba(239, 68, 68, 0.2); color: #fca5a5; border: 1px solid #ef4444; }
    .badge-hold { background: rgba(148, 163, 184, 0.2); color: #cbd5e1; border: 1px solid #64748b; }

    .player-title { font-size: 15px; font-weight: 600; color: #f8fafc; }
    .player-sub { font-size: 12px; color: #94a3b8; }
    .player-val { font-size: 18px; font-weight: 700; color: #38bdf8; }
</style>
""", unsafe_allow_html=True)

BASE_URL = "https://api.sleeper.app/v1"
DEFAULT_LEAGUE_ID = "1312141103282245632"

# ==================== DATA LOADER ====================
@st.cache_data(ttl=86400)
def get_all_players():
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        r = requests.get(f"{BASE_URL}/players/nfl", headers=headers, timeout=20)
        return r.json() if r.status_code == 200 else {}
    except Exception:
        return {}

@st.cache_data(ttl=300)
def fetch_league(league_id: str):
    headers = {"User-Agent": "Mozilla/5.0"}
    s = requests.Session()
    s.headers.update(headers)
    
    l_resp = s.get(f"{BASE_URL}/league/{league_id}", timeout=10)
    if l_resp.status_code != 200:
        return None, [], [], [], {}, 1, []
    
    league_info = l_resp.json()
    users = s.get(f"{BASE_URL}/league/{league_id}/users", timeout=10).json() or []
    rosters = s.get(f"{BASE_URL}/league/{league_id}/rosters", timeout=10).json() or []
    traded_picks = s.get(f"{BASE_URL}/league/{league_id}/traded_picks", timeout=10).json() or []
    
    # NFL State
    state = s.get(f"{BASE_URL}/state/nfl", timeout=10).json() or {}
    cur_week = state.get("week", 1)
    
    # Only fetch current week + previous 2 weeks to keep response times fast
    matchups = {}
    for w in range(max(1, cur_week - 2), cur_week + 1):
        m = s.get(f"{BASE_URL}/league/{league_id}/matchups/{w}", timeout=6).json() or []
        matchups[w] = m

    # Recent completed transactions
    trades = []
    tx_data = s.get(f"{BASE_URL}/league/{league_id}/transactions/{cur_week}", timeout=6).json() or []
    for tx in tx_data:
        if tx.get("type") == "trade" and tx.get("status") == "complete":
            trades.append(tx)

    return league_info, users, rosters, traded_picks, matchups, cur_week, trades

with st.spinner("Connecting to Sleeper & Initializing Custom Scoring..."):
    all_players = get_all_players()
    league_info, users, rosters, traded_picks, matchups, current_week, all_trades = fetch_league(DEFAULT_LEAGUE_ID)

if not league_info or not rosters:
    st.error("⚠️ Could not load Sleeper league. Please check connection or League ID.")
    st.stop()

# Build mapping
user_map = {
    u["user_id"]: u.get("metadata", {}).get("team_name") or u.get("display_name", f"User {u['user_id']}")
    for u in users
}
roster_owner_map = {
    r["roster_id"]: user_map.get(r["owner_id"], f"Team {r['roster_id']}")
    for r in rosters
}

# ==================== VALUATION ENGINE ====================
# 8-Team | 1QB | 2TE (+0.25 TEP) | 4 Flex | High-Impact IDP
def evaluate_player(pid, p_info):
    if not p_info:
        return {"value": 20, "stage": "Prime", "badge": "badge-prime", "action": "HOLD", "act_badge": "badge-hold", "rookie": False, "age": 25, "pos": "FLEX", "name": f"Player {pid}"}
    
    pos = p_info.get("position", "N/A")
    age = p_info.get("age") or 25
    exp = p_info.get("years_exp") or 0
    is_rookie = exp == 0

    base_scores = {
        "QB": 50, "RB": 65, "WR": 75, "TE": 80,
        "DL": 45, "DE": 45, "DT": 40, "LB": 35, "CB": 25, "S": 30, "K": 10
    }
    base = base_scores.get(pos, 30)

    if age <= 23:
        stage, badge, mult = "Rising", "badge-rising", 1.35
    elif 24 <= age <= 27:
        stage, badge, mult = "Prime", "badge-prime", 1.15
    elif 28 <= age <= 29:
        stage, badge, mult = "Descending", "badge-descending", 0.85
    else:
        stage, badge, mult = "Unc", "badge-unc", 0.55

    calc_val = int(base * mult)

    if stage in ["Descending", "Unc"] and pos in ["RB", "WR"]:
        action, act_badge = "SELL HIGH", "badge-sell"
    elif stage == "Rising":
        action, act_badge = "BUY / STRONG HOLD", "badge-buy"
    elif stage == "Prime" and pos in ["TE", "DL"]:
        action, act_badge = "CORE ASSET", "badge-buy"
    else:
        action, act_badge = "HOLD", "badge-hold"

    return {
        "value": calc_val, "stage": stage, "badge": badge,
        "action": action, "act_badge": act_badge, "rookie": is_rookie,
        "age": age, "pos": pos, "name": p_info.get("full_name") or f"Player {pid}"
    }

# ==================== HEADER & SELECTOR ====================
h1, h2 = st.columns([3, 1])
with h1:
    st.markdown(f"## ⚡ {league_info.get('name', 'Dynasty League')}")
    st.caption(f"8 Teams • 2TE (+0.25 TEP) • 4 Flex • Big-Play IDP • 2027–2029 Draft Capital")

team_names = [roster_owner_map[r["roster_id"]] for r in rosters]
with h2:
    selected_team_name = st.selectbox("Select Team", team_names, index=0)

selected_roster = next(r for r in rosters if roster_owner_map[r["roster_id"]] == selected_team_name)
selected_rid = selected_roster["roster_id"]

# Navigation Tabs
tab_overview, tab_matchup, tab_blueprint, tab_playoffs, tab_trades = st.tabs([
    "👤 Roster & Value",
    "⚔️ Matchup Outlook",
    "🔮 Future & Prime Years",
    "🎲 Playoffs & Toilet Bowl",
    "📜 Trades & Calculator"
])

# ==================== TAB 1: ROSTER & VALUE ====================
with tab_overview:
    pids = selected_roster.get("players", []) or []
    starters = selected_roster.get("starters", []) or []
    taxi = selected_roster.get("taxi", []) or []
    reserve = selected_roster.get("reserve", []) or []
    bench = [p for p in pids if p not in starters and p not in taxi and p not in reserve]

    player_evals = {pid: evaluate_player(pid, all_players.get(pid, {})) for pid in pids}
    total_val = sum(x["value"] for x in player_evals.values())
    avg_age = sum(x["age"] for x in player_evals.values()) / max(len(player_evals), 1)

    m1, m2, m3, m4 = st.columns(4)
    m1.markdown(f"""
    <div class="glass-card">
        <div style="color: #94a3b8; font-size: 13px;">FRANCHISE VALUE</div>
        <div style="font-size: 26px; font-weight: 700; color: #38bdf8;">{total_val:,} pts</div>
        <div style="font-size: 12px; color: #4ade80;">Dynasty Power Index</div>
    </div>
    """, unsafe_allow_html=True)

    m2.markdown(f"""
    <div class="glass-card">
        <div style="color: #94a3b8; font-size: 13px;">ROSTER AVG AGE</div>
        <div style="font-size: 26px; font-weight: 700; color: #f8fafc;">{avg_age:.1f} yrs</div>
        <div style="font-size: 12px; color: #818cf8;">{"Youth Foundation" if avg_age < 25.5 else "Contending Core" if avg_age <= 27.5 else "Veteran Window"}</div>
    </div>
    """, unsafe_allow_html=True)

    fpts = selected_roster.get("settings", {}).get("fpts", 0) + (selected_roster.get("settings", {}).get("fpts_decimal", 0)/100)
    m3.markdown(f"""
    <div class="glass-card">
        <div style="color: #94a3b8; font-size: 13px;">TOTAL POINTS</div>
        <div style="font-size: 26px; font-weight: 700; color: #fbbf24;">{fpts:.1f}</div>
        <div style="font-size: 12px; color: #94a3b8;">Max PF: {selected_roster.get('settings', {}).get('ppts', 0):.1f}</div>
    </div>
    """, unsafe_allow_html=True)

    w = selected_roster.get("settings", {}).get("wins", 0)
    l = selected_roster.get("settings", {}).get("losses", 0)
    m4.markdown(f"""
    <div class="glass-card">
        <div style="color: #94a3b8; font-size: 13px;">RECORD</div>
        <div style="font-size: 26px; font-weight: 700; color: #f43f5e;">{w}W - {l}L</div>
        <div style="font-size: 12px; color: #94a3b8;">Win %: {w / max(w + l, 1):.2f}</div>
    </div>
    """, unsafe_allow_html=True)

    def show_players(title, id_list):
        st.markdown(f"#### {title} ({len(id_list)})")
        if not id_list:
            st.caption("None assigned.")
            return
        for pid in id_list:
            p = player_evals.get(pid)
            if not p:
                continue
            rookie = '<span class="badge badge-rookie">ROOKIE</span>' if p["rookie"] else ''
            inj = all_players.get(pid, {}).get("injury_status")
            inj_tag = f'<span class="badge badge-unc">{inj}</span>' if inj else ''
            st.markdown(f"""
            <div class="glass-card-interactive">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <div>
                        <span class="player-title">{p['name']}</span> 
                        <span class="player-sub">({p['pos']} • {p['age']} yo)</span>
                        <div style="margin-top: 4px;">
                            <span class="badge {p['badge']}">{p['stage'].upper()}</span>
                            {rookie}
                            <span class="badge {p['act_badge']}">{p['action']}</span>
                            {inj_tag}
                        </div>
                    </div>
                    <div style="text-align: right;">
                        <div class="player-val">{p['value']}</div>
                        <div style="font-size: 11px; color: #64748b;">Asset Pts</div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

    c1, c2 = st.columns(2)
    with c1:
        show_players("⚡ Starters", starters)
        show_players("🚑 Injured Reserve (IR)", reserve)
    with c2:
        show_players("🪑 Bench", bench)
        show_players("🚕 Taxi Squad", taxi)

# ==================== TAB 2: MATCHUP OUTLOOK ====================
with tab_matchup:
    st.subheader(f"Week {current_week} Matchup Outlook")
    cur_matchups = matchups.get(current_week, [])
    my_match = next((m for m in cur_matchups if m["roster_id"] == selected_rid), None)
    
    if not my_match:
        st.info(f"Matchup data pending for Week {current_week}.")
    else:
        opp = next((m for m in cur_matchups if m.get("matchup_id") == my_match.get("matchup_id") and m["roster_id"] != selected_rid), None)
        if not opp:
            st.info("Bye Week or Unscheduled.")
        else:
            opp_name = roster_owner_map.get(opp["roster_id"], f"Team {opp['roster_id']}")
            c_m1, c_m2 = st.columns(2)
            c_m1.markdown(f"""
            <div class="glass-card" style="border-left: 4px solid #38bdf8;">
                <h3>{selected_team_name} (You)</h3>
                <div style="font-size: 30px; font-weight: 800; color: #38bdf8;">{my_match.get('points', 0.0):.2f} pts</div>
            </div>
            """, unsafe_allow_html=True)
            c_m2.markdown(f"""
            <div class="glass-card" style="border-left: 4px solid #f43f5e;">
                <h3>{opp_name} (Opponent)</h3>
                <div style="font-size: 30px; font-weight: 800; color: #f43f5e;">{opp.get('points', 0.0):.2f} pts</div>
            </div>
            """, unsafe_allow_html=True)

# ==================== TAB 3: PRIME YEARS ====================
with tab_blueprint:
    st.subheader("Championship Runway & Strategy Blueprint")
    
    superstars = [player_evals[p]["name"] for p in pids if player_evals.get(p) and player_evals[p]["value"] >= 75]
    rising = [player_evals[p]["name"] for p in pids if player_evals.get(p) and player_evals[p]["stage"] == "Rising" and player_evals[p]["value"] >= 45]
    uncs = [player_evals[p]["name"] for p in pids if player_evals.get(p) and player_evals[p]["stage"] == "Unc"]

    if avg_age < 24.8:
        window = "2027 – 2030 (Ascending Powerhouse)"
        strategy = "Stockpile 2027/2028 1st round draft picks. Do not trade youth for veterans."
    elif avg_age <= 26.8:
        window = "2026 – 2028 (Apex Championship Window)"
        strategy = "Go all-in. Trade future 2nd/3rd round picks to buy top tight ends or edge rushers."
    else:
        window = "2026 (Closing Window - Must Retool Soon)"
        strategy = "Aggressively trade older players past age 28 to contenders for draft capital."

    st.markdown(f"""
    <div class="glass-card">
        <h4>🏆 Projected Prime Window</h4>
        <div style="font-size: 28px; font-weight: 800; color: #38bdf8; margin: 6px 0;">{window}</div>
        <p><strong>Recommended Strategy:</strong> {strategy}</p>
    </div>
    """, unsafe_allow_html=True)

    b1, b2 = st.columns(2)
    b1.markdown(f"""
    <div class="glass-card" style="border-left: 4px solid #4ade80;">
        <h5 style="color: #4ade80;">🌟 Core Players to Keep</h5>
        <p>{', '.join(superstars + rising[:4]) if (superstars or rising) else 'None identified'}</p>
    </div>
    """, unsafe_allow_html=True)
    
    b2.markdown(f"""
    <div class="glass-card" style="border-left: 4px solid #ef4444;">
        <h5 style="color: #f87171;">⏳ Trade Candidates (Sell High / Unc)</h5>
        <p>{', '.join(uncs[:5]) if uncs else 'No aging players currently'}</p>
    </div>
    """, unsafe_allow_html=True)

# ==================== TAB 4: PLAYOFFS & TOILET BOWL ====================
with tab_playoffs:
    st.subheader("Playoffs (Top 6) & Toilet Bowl (Seeds 7 & 8)")
    
    records = []
    for r in rosters:
        rid = r["roster_id"]
        tname = roster_owner_map.get(rid, f"Team {rid}")
        wins = r.get("settings", {}).get("wins", 0)
        losses = r.get("settings", {}).get("losses", 0)
        pts = r.get("settings", {}).get("fpts", 0) + (r.get("settings", {}).get("fpts_decimal", 0)/100)
        max_pf = r.get("settings", {}).get("ppts", 0) or pts
        records.append({
            "Team": tname, "Wins": wins, "Losses": losses,
            "Points For": pts, "Max PF": max_pf
        })

    df_p = pd.DataFrame(records).sort_values(by=["Wins", "Points For"], ascending=False).reset_index(drop=True)
    df_p["Playoff Seed"] = range(1, len(df_p) + 1)
    df_p["Playoff Odds"] = [98 if i < 4 else (74 if i < 6 else 12) for i in range(len(df_p))]

    st.dataframe(
        df_p[["Playoff Seed", "Team", "Wins", "Losses", "Points For", "Max PF", "Playoff Odds"]].style.format({
            "Points For": "{:.1f}", "Max PF": "{:.1f}", "Playoff Odds": "{:.0f}%"
        }),
        use_container_width=True
    )

    t_teams = df_p.tail(2).sort_values(by="Max PF", ascending=True)
    st.markdown(f"""
    <div class="glass-card" style="border-left: 4px solid #facc15;">
        <h4>🚽 Toilet Bowl Standings (Draft Pick 1.01 Race)</h4>
        <p>Seeds 7 & 8 battle in the Toilet Bowl. Per your rules, <strong>lower Max PF gets the #1 pick</strong>.</p>
        <p>🥇 <strong>Current #1 Pick Favorite:</strong> {t_teams.iloc[0]['Team']} ({t_teams.iloc[0]['Max PF']:.1f} Max PF)</p>
        <p>🥈 <strong>Current #2 Pick Favorite:</strong> {t_teams.iloc[1]['Team']} ({t_teams.iloc[1]['Max PF']:.1f} Max PF)</p>
    </div>
    """, unsafe_allow_html=True)

# ==================== TAB 5: TRADES ====================
with tab_trades:
    st.subheader("Dynasty Trade Calculator")
    ca, cb = st.columns(2)
    with ca:
        ta = st.selectbox("Team A", team_names, index=0, key="t_a")
        r_a = next(r for r in rosters if roster_owner_map[r["roster_id"]] == ta)
        p_a = r_a.get("players", []) or []
        opts_a = {f"{all_players.get(p, {}).get('full_name', p)} ({all_players.get(p, {}).get('position', '-')})": p for p in p_a}
        sel_pa = st.multiselect(f"Players from {ta}", list(opts_a.keys()), key="spa")
        sel_pka = st.multiselect(f"Picks from {ta}", [f"{y} Rd {r}" for y in [2027, 2028, 2029] for r in [1, 2, 3]], key="spka")

    with cb:
        tb = st.selectbox("Team B", team_names, index=1 if len(team_names) > 1 else 0, key="t_b")
        r_b = next(r for r in rosters if roster_owner_map[r["roster_id"]] == tb)
        p_b = r_b.get("players", []) or []
        opts_b = {f"{all_players.get(p, {}).get('full_name', p)} ({all_players.get(p, {}).get('position', '-')})": p for p in p_b}
        sel_pb = st.multiselect(f"Players from {tb}", list(opts_b.keys()), key="spb")
        sel_pkb = st.multiselect(f"Picks from {tb}", [f"{y} Rd {r}" for y in [2027, 2028, 2029] for r in [1, 2, 3]], key="spkb")

    pick_vals = {"Rd 1": 70, "Rd 2": 38, "Rd 3": 18}
    val_a = sum(evaluate_player(opts_a[p], all_players.get(opts_a[p], {}))["value"] for p in sel_pa)
    for pk in sel_pka:
        val_a += pick_vals.get(pk.split(" ")[1] + " " + pk.split(" ")[2], 25)

    val_b = sum(evaluate_player(opts_b[p], all_players.get(opts_b[p], {}))["value"] for p in sel_pb)
    for pk in sel_pkb:
        val_b += pick_vals.get(pk.split(" ")[1] + " " + pk.split(" ")[2], 25)

    st.markdown("---")
    res1, res2, res3 = st.columns(3)
    res1.metric(f"{ta} Gives", f"{val_a} pts")
    res2.metric(f"{tb} Gives", f"{val_b} pts")
    delta = val_a - val_b
    res3.metric("Trade Edge", f"{abs(delta)} pts", f"{'Favors ' + ta if delta < 0 else 'Favors ' + tb}")

    st.markdown("### 🧾 Recent Completed League Trades")
    if not all_trades:
        st.info("No trades completed on Sleeper recently.")
    else:
        for tx in all_trades[:5]:
            st.markdown(f"""
            <div class="glass-card-interactive">
                <strong>Trade Transaction ID: {tx.get('transaction_id')}</strong>
                <p style="font-size: 13px; color: #94a3b8; margin: 4px 0;">Completed Trade</p>
            </div>
            """, unsafe_allow_html=True)
