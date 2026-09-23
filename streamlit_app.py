import streamlit as st
import pandas as pd
import requests

st.set_page_config(
    page_title="Dynasty Hub & Lineup Architect", 
    page_icon="⚡", 
    layout="wide", 
    initial_sidebar_state="expanded"
)

# ==================== MODERN SLEEK DARK CSS ====================
st.markdown("""
<style>
    .stApp {
        background-color: #0b0e14;
        color: #f1f5f9;
        font-family: -apple-system, BlinkMacSystemFont, "SF Pro Text", "Segoe UI", Roboto, sans-serif;
    }
    
    /* Top Summary Cards */
    .metric-card {
        background: #121622;
        border: 1px solid #1e2638;
        border-radius: 12px;
        padding: 16px 20px;
        margin-bottom: 20px;
    }

    /* Single Row Lineup Styling */
    .lineup-row {
        display: flex;
        align-items: center;
        justify-content: space-between;
        background: #11151f;
        border: 1px solid #1a202e;
        border-radius: 10px;
        padding: 10px 18px;
        margin-bottom: 6px;
        transition: background 0.15s ease, border-color 0.15s ease;
    }
    .lineup-row:hover {
        background: #161b27;
        border-color: #2b354c;
    }

    .pos-slot {
        width: 44px;
        height: 28px;
        line-height: 28px;
        font-size: 11px;
        font-weight: 800;
        color: #94a3b8;
        text-align: center;
        background: #192030;
        border-radius: 6px;
        margin-right: 14px;
        flex-shrink: 0;
        border: 1px solid #242d42;
    }
    
    .player-avatar {
        width: 42px;
        height: 42px;
        border-radius: 50%;
        object-fit: cover;
        background: #1a2233;
        border: 1px solid #2e384d;
        margin-right: 14px;
        flex-shrink: 0;
    }

    .badge {
        padding: 2px 7px;
        border-radius: 6px;
        font-size: 10px;
        font-weight: 700;
        display: inline-block;
        margin-right: 4px;
    }
    .badge-rookie { background: rgba(56, 189, 248, 0.15); color: #38bdf8; border: 1px solid rgba(56, 189, 248, 0.4); }
    .badge-rising { background: rgba(74, 222, 128, 0.15); color: #4ade80; border: 1px solid rgba(74, 222, 128, 0.4); }
    .badge-prime { background: rgba(129, 140, 248, 0.15); color: #818cf8; border: 1px solid rgba(129, 140, 248, 0.4); }
    .badge-descending { background: rgba(251, 146, 60, 0.15); color: #fb923c; border: 1px solid rgba(251, 146, 60, 0.4); }
    .badge-unc { background: rgba(244, 63, 94, 0.15); color: #f43f5e; border: 1px solid rgba(244, 63, 94, 0.4); }
    
    .badge-buy { background: rgba(34, 197, 94, 0.15); color: #86efac; border: 1px solid rgba(34, 197, 94, 0.35); }
    .badge-sell { background: rgba(239, 68, 68, 0.15); color: #fca5a5; border: 1px solid rgba(239, 68, 68, 0.35); }
    .badge-hold { background: rgba(148, 163, 184, 0.12); color: #cbd5e1; border: 1px solid rgba(148, 163, 184, 0.25); }

    .section-header {
        font-size: 17px;
        font-weight: 700;
        color: #f1f5f9;
        margin-top: 24px;
        margin-bottom: 10px;
        display: flex;
        align-items: center;
        gap: 8px;
    }
</style>
""", unsafe_allow_html=True)

BASE_URL = "https://api.sleeper.app/v1"
PERMANENT_LEAGUE_ID = "1312141303219249152"

# League selector / override in sidebar
st.sidebar.title("⚡ League Controls")
league_id = st.sidebar.text_input("Active League ID", value=PERMANENT_LEAGUE_ID)

@st.cache_data(ttl=86400)
def get_all_players():
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        r = requests.get(f"{BASE_URL}/players/nfl", headers=headers, timeout=20)
        return r.json() if r.status_code == 200 else {}
    except Exception:
        return {}

@st.cache_data(ttl=300)
def fetch_league(l_id: str):
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        league_info = requests.get(f"{BASE_URL}/league/{l_id}", headers=headers, timeout=10).json()
        users = requests.get(f"{BASE_URL}/league/{l_id}/users", headers=headers, timeout=10).json() or []
        rosters = requests.get(f"{BASE_URL}/league/{l_id}/rosters", headers=headers, timeout=10).json() or []
        traded_picks = requests.get(f"{BASE_URL}/league/{l_id}/traded_picks", headers=headers, timeout=10).json() or []
        
        state = requests.get(f"{BASE_URL}/state/nfl", headers=headers, timeout=10).json() or {}
        cur_week = state.get("week", 1)
        
        matchups = {}
        for w in range(max(1, cur_week - 2), cur_week + 1):
            m_resp = requests.get(f"{BASE_URL}/league/{l_id}/matchups/{w}", headers=headers, timeout=6)
            if m_resp.status_code == 200:
                matchups[w] = m_resp.json() or []

        trades = []
        tx_resp = requests.get(f"{BASE_URL}/league/{l_id}/transactions/{cur_week}", headers=headers, timeout=6)
        if tx_resp.status_code == 200:
            for tx in tx_resp.json() or []:
                if tx.get("type") == "trade" and tx.get("status") == "complete":
                    trades.append(tx)

        return league_info, users, rosters, traded_picks, matchups, cur_week, trades
    except Exception:
        return None, [], [], [], {}, 1, []

all_players = get_all_players()
league_info, users, rosters, traded_picks, matchups, current_week, all_trades = fetch_league(league_id)

if not league_info or not rosters:
    st.error(f"⚠️ Could not load Sleeper league for ID: `{league_id}`.")
    st.stop()

# Maps
user_map = {
    u["user_id"]: u.get("metadata", {}).get("team_name") or u.get("display_name", f"User {u['user_id']}")
    for u in users
}
roster_owner_map = {
    r["roster_id"]: user_map.get(r["owner_id"], f"Team {r['roster_id']}")
    for r in rosters
}

# ==================== ENHANCED 0–1,000 DYNASTY VALUE ENGINE ====================
# Scaled for: 8-Team | 1QB | 2TE (+0.25 TEP) | 4 Flex | High-Impact IDP
def evaluate_player(pid, p_info):
    if not p_info:
        return {
            "value": 150, "stage": "Prime", "badge": "badge-prime",
            "action": "HOLD", "act_badge": "badge-hold", "rookie": False,
            "age": 25, "pos": "FLEX", "name": f"Player {pid}", "team": "FA",
            "img": f"https://sleepercdn.com/content/nfl/players/{pid}.jpg"
        }
    
    pos = p_info.get("position", "N/A")
    age = p_info.get("age") or 25
    exp = p_info.get("years_exp") or 0
    is_rookie = exp == 0
    team = p_info.get("team") or "FA"

    # Baseline on 0–1000 point scale tailored to 8-team formats
    # In 8-team leagues, studs dominate; TEs are apex assets due to 2TE + 0.25 TEP
    base_scores = {
        "WR": 550,
        "RB": 520,
        "TE": 600,   # High demand (16 starting TEs across 8 teams)
        "QB": 420,   # 1QB lowers baseline QB replacement value
        "DL": 380,   # Big-play IDP scoring rewards top sack generators
        "DE": 380,
        "DT": 330,
        "LB": 310,
        "CB": 210,
        "S": 240,
        "K": 80
    }
    base = base_scores.get(pos, 250)

    # Age and Dynasty Trajectory Multipliers
    if age <= 22:
        stage, badge, mult = "Rising", "badge-rising", 1.55
    elif age <= 24:
        stage, badge, mult = "Rising", "badge-rising", 1.40
    elif 25 <= age <= 27:
        stage, badge, mult = "Prime", "badge-prime", 1.15
    elif 28 <= age <= 29:
        stage, badge, mult = "Descending", "badge-descending", 0.75
    else:
        stage, badge, mult = "Unc", "badge-unc", 0.42

    calc_val = int(base * mult)

    # Actionable Trade Status
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
        "age": age, "pos": pos, "team": team,
        "name": p_info.get("full_name") or f"Player {pid}",
        "img": f"https://sleepercdn.com/content/nfl/players/{pid}.jpg"
    }

# ==================== HEADER & TEAM SELECTOR ====================
h1, h2 = st.columns([3, 1])
with h1:
    st.markdown(f"## ⚡ {league_info.get('name', 'Dynasty Hub')}")
    st.caption("8 Teams • 1QB • 2TE (+0.25 TEP) • 4 Flex • Big-Play IDP • 2027–2029 Draft Picks")

team_names = [roster_owner_map[r["roster_id"]] for r in rosters]
with h2:
    selected_team_name = st.selectbox("Select Your Franchise", team_names, index=0)

selected_roster = next(r for r in rosters if roster_owner_map[r["roster_id"]] == selected_team_name)
selected_rid = selected_roster["roster_id"]

tab_overview, tab_matchup, tab_blueprint, tab_playoffs, tab_trades = st.tabs([
    "👤 Roster & Lineup",
    "⚔️ Matchup Outlook",
    "🔮 Future & Prime Years",
    "🎲 Playoffs & Toilet Bowl",
    "📜 Trades & Calculator"
])

# ==================== TAB 1: VERTICAL ROSTER & LINEUP ====================
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
    <div class="metric-card">
        <div style="color: #94a3b8; font-size: 12px; font-weight: 600; letter-spacing: 0.5px;">FRANCHISE VALUE</div>
        <div style="font-size: 26px; font-weight: 800; color: #38bdf8; margin: 4px 0;">{total_val:,} pts</div>
        <div style="font-size: 12px; color: #4ade80;">Dynasty Power Index</div>
    </div>
    """, unsafe_allow_html=True)

    m2.markdown(f"""
    <div class="metric-card">
        <div style="color: #94a3b8; font-size: 12px; font-weight: 600; letter-spacing: 0.5px;">AVERAGE ROSTER AGE</div>
        <div style="font-size: 26px; font-weight: 800; color: #f8fafc; margin: 4px 0;">{avg_age:.1f} yrs</div>
        <div style="font-size: 12px; color: #818cf8;">{"Youth Foundation" if avg_age < 25.5 else "Contending Core" if avg_age <= 27.5 else "Veteran Core"}</div>
    </div>
    """, unsafe_allow_html=True)

    fpts = selected_roster.get("settings", {}).get("fpts", 0) + (selected_roster.get("settings", {}).get("fpts_decimal", 0)/100)
    m3.markdown(f"""
    <div class="metric-card">
        <div style="color: #94a3b8; font-size: 12px; font-weight: 600; letter-spacing: 0.5px;">TOTAL POINTS</div>
        <div style="font-size: 26px; font-weight: 800; color: #fbbf24; margin: 4px 0;">{fpts:.1f}</div>
        <div style="font-size: 12px; color: #94a3b8;">Max PF: {selected_roster.get('settings', {}).get('ppts', 0):.1f}</div>
    </div>
    """, unsafe_allow_html=True)

    w = selected_roster.get("settings", {}).get("wins", 0)
    l = selected_roster.get("settings", {}).get("losses", 0)
    m4.markdown(f"""
    <div class="metric-card">
        <div style="color: #94a3b8; font-size: 12px; font-weight: 600; letter-spacing: 0.5px;">RECORD</div>
        <div style="font-size: 26px; font-weight: 800; color: #f43f5e; margin: 4px 0;">{w}W - {l}L</div>
        <div style="font-size: 12px; color: #94a3b8;">Win Rate: {w / max(w + l, 1):.2f}</div>
    </div>
    """, unsafe_allow_html=True)

    # Vertical Lineup Section Renderer
    def render_vertical_lineup(title, player_list, slot_label="BN"):
        st.markdown(f'<div class="section-header">{title} <span style="font-size: 13px; color: #94a3b8; font-weight: 400;">({len(player_list)})</span></div>', unsafe_allow_html=True)
        if not player_list:
            st.caption("No players in this section.")
            return

        league_slots = league_info.get("roster_positions", [])
        
        for idx, pid in enumerate(player_list):
            p = player_evals.get(pid)
            if not p:
                continue
            
            if slot_label == "START":
                pos_display = league_slots[idx] if idx < len(league_slots) else "FLEX"
            else:
                pos_display = slot_label

            rookie_html = '<span class="badge badge-rookie">ROOKIE</span>' if p["rookie"] else ''
            
            row_html = (
                f'<div class="lineup-row">'
                f'  <div style="display: flex; align-items: center; gap: 4px;">'
                f'      <div class="pos-slot">{pos_display}</div>'
                f'      <img src="{p["img"]}" class="player-avatar" onerror="this.onerror=null;this.src=\'https://sleepercdn.com/images/v2/icons/player_default.webp\';">'
                f'      <div>'
                f'          <div style="font-size: 15px; font-weight: 600; color: #f8fafc;">{p["name"]} '
                f'              <span style="font-size: 12px; color: #94a3b8; font-weight: 400;">{p["pos"]} - {p["team"]} • {p["age"]}yo</span>'
                f'          </div>'
                f'          <div style="margin-top: 3px;">'
                f'              <span class="badge {p["badge"]}">{p["stage"].upper()}</span>'
                f'              {rookie_html}'
                f'              <span class="badge {p["act_badge"]}">{p["action"]}</span>'
                f'          </div>'
                f'      </div>'
                f'  </div>'
                f'  <div style="text-align: right;">'
                f'      <div style="font-size: 18px; font-weight: 800; color: #38bdf8;">{p["value"]:,}</div>'
                f'      <div style="font-size: 11px; color: #64748b;">Dynasty Index</div>'
                f'  </div>'
                f'</div>'
            )
            st.markdown(row_html, unsafe_allow_html=True)

    # Render ALL segments in ONE vertical top-to-bottom layout
    render_vertical_lineup("⚡ Starters", starters, slot_label="START")
    render_vertical_lineup("🪑 Bench", bench, slot_label="BN")
    render_vertical_lineup("🚑 Injured Reserve (IR)", reserve, slot_label="IR")
    render_vertical_lineup("🚕 Taxi Squad", taxi, slot_label="TAXI")

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
            <div class="metric-card" style="border-left: 4px solid #38bdf8;">
                <h3>{selected_team_name} (You)</h3>
                <div style="font-size: 30px; font-weight: 800; color: #38bdf8;">{my_match.get('points', 0.0):.2f} pts</div>
            </div>
            """, unsafe_allow_html=True)
            c_m2.markdown(f"""
            <div class="metric-card" style="border-left: 4px solid #f43f5e;">
                <h3>{opp_name} (Opponent)</h3>
                <div style="font-size: 30px; font-weight: 800; color: #f43f5e;">{opp.get('points', 0.0):.2f} pts</div>
            </div>
            """, unsafe_allow_html=True)

# ==================== TAB 3: PRIME YEARS ====================
with tab_blueprint:
    st.subheader("Championship Runway & Strategy Blueprint")
    
    superstars = [player_evals[p]["name"] for p in pids if player_evals.get(p) and player_evals[p]["value"] >= 650]
    rising = [player_evals[p]["name"] for p in pids if player_evals.get(p) and player_evals[p]["stage"] == "Rising" and player_evals[p]["value"] >= 450]
    uncs = [player_evals[p]["name"] for p in pids if player_evals.get(p) and player_evals[p]["stage"] == "Unc"]

    if avg_age < 24.8:
        window = "2027 – 2030 (Ascending Powerhouse)"
        strategy = "Stockpile 2027/2028 1st round draft picks. Do not trade away youth for short-term fixes."
    elif avg_age <= 26.8:
        window = "2026 – 2028 (Apex Championship Window)"
        strategy = "Go all-in. Trade future 2nd/3rd round picks to buy top tight ends or edge rushers."
    else:
        window = "2026 (Closing Window - Must Retool Soon)"
        strategy = "Aggressively trade older players past age 28 to contenders for 2027–2029 draft capital."

    st.markdown(f"""
    <div class="metric-card">
        <h4>🏆 Projected Prime Window</h4>
        <div style="font-size: 28px; font-weight: 800; color: #38bdf8; margin: 6px 0;">{window}</div>
        <p><strong>Recommended Strategy:</strong> {strategy}</p>
    </div>
    """, unsafe_allow_html=True)

    b1, b2 = st.columns(2)
    b1.markdown(f"""
    <div class="metric-card" style="border-left: 4px solid #4ade80;">
        <h5 style="color: #4ade80;">🌟 Core Players to Keep</h5>
        <p>{', '.join(superstars + rising[:4]) if (superstars or rising) else 'None identified'}</p>
    </div>
    """, unsafe_allow_html=True)
    
    b2.markdown(f"""
    <div class="metric-card" style="border-left: 4px solid #ef4444;">
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
    <div class="metric-card" style="border-left: 4px solid #facc15;">
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

    # Scaled Draft Pick Values
    pick_vals = {"Rd 1": 650, "Rd 2": 320, "Rd 3": 140}
    val_a = sum(evaluate_player(opts_a[p], all_players.get(opts_a[p], {}))["value"] for p in sel_pa)
    for pk in sel_pka:
        val_a += pick_vals.get(pk.split(" ")[1] + " " + pk.split(" ")[2], 200)

    val_b = sum(evaluate_player(opts_b[p], all_players.get(opts_b[p], {}))["value"] for p in sel_pb)
    for pk in sel_pkb:
        val_b += pick_vals.get(pk.split(" ")[1] + " " + pk.split(" ")[2], 200)

    st.markdown("---")
    res1, res2, res3 = st.columns(3)
    res1.metric(f"{ta} Gives", f"{val_a:,} pts")
    res2.metric(f"{tb} Gives", f"{val_b:,} pts")
    delta = val_a - val_b
    res3.metric("Trade Edge", f"{abs(delta):,} pts", f"{'Favors ' + ta if delta < 0 else 'Favors ' + tb}")

    st.markdown("### 🧾 Recent Completed League Trades")
    if not all_trades:
        st.info("No trades completed on Sleeper recently.")
    else:
        for tx in all_trades[:5]:
            st.markdown(f"""
            <div class="lineup-row">
                <div>
                    <strong>Trade Transaction ID: {tx.get('transaction_id')}</strong>
                    <div style="font-size: 12px; color: #94a3b8;">Completed Trade</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
