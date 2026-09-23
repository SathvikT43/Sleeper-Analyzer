import streamlit as st
import pandas as pd
import requests

st.set_page_config(
    page_title="Dynasty Hub & Lineup Architect", 
    page_icon="⚡", 
    layout="wide", 
    initial_sidebar_state="collapsed"
)

# ==================== MODERN DARK UI CSS ====================
st.markdown("""
<style>
    .stApp {
        background-color: #090c10;
        color: #f1f5f9;
        font-family: -apple-system, BlinkMacSystemFont, "SF Pro Text", "Segoe UI", Roboto, sans-serif;
    }
    
    .metric-card {
        background: #11151f;
        border: 1px solid #1c2333;
        border-radius: 12px;
        padding: 14px 18px;
        margin-bottom: 16px;
    }

    .lineup-row {
        display: flex;
        align-items: center;
        justify-content: space-between;
        background: #10141d;
        border: 1px solid #181e2b;
        border-radius: 8px;
        padding: 7px 12px;
        margin-bottom: 5px;
        transition: background 0.12s ease, border-color 0.12s ease;
    }
    .lineup-row:hover {
        background: #151a26;
        border-color: #273248;
    }

    .pos-slot {
        width: 38px;
        height: 24px;
        line-height: 24px;
        font-size: 10px;
        font-weight: 800;
        color: #94a3b8;
        text-align: center;
        background: #181f2e;
        border-radius: 5px;
        margin-right: 10px;
        flex-shrink: 0;
        border: 1px solid #232c3f;
    }
    
    .player-avatar {
        width: 34px;
        height: 34px;
        border-radius: 50%;
        object-fit: cover;
        background: #19202f;
        border: 1px solid #283348;
        margin-right: 10px;
        flex-shrink: 0;
    }

    .badge {
        padding: 1px 6px;
        border-radius: 5px;
        font-size: 9px;
        font-weight: 700;
        display: inline-block;
        margin-right: 3px;
    }
    .badge-rookie { background: rgba(56, 189, 248, 0.15); color: #38bdf8; border: 1px solid rgba(56, 189, 248, 0.4); }
    .badge-rising { background: rgba(74, 222, 128, 0.15); color: #4ade80; border: 1px solid rgba(74, 222, 128, 0.4); }
    .badge-prime { background: rgba(129, 140, 248, 0.15); color: #818cf8; border: 1px solid rgba(129, 140, 248, 0.4); }
    .badge-descending { background: rgba(251, 146, 60, 0.15); color: #fb923c; border: 1px solid rgba(251, 146, 60, 0.4); }
    .badge-unc { background: rgba(244, 63, 94, 0.15); color: #f43f5e; border: 1px solid rgba(244, 63, 94, 0.4); }
    
    .badge-buy { background: rgba(34, 197, 94, 0.15); color: #86efac; border: 1px solid rgba(34, 197, 94, 0.35); }
    .badge-sell { background: rgba(239, 68, 68, 0.15); color: #fca5a5; border: 1px solid rgba(239, 68, 68, 0.35); }
    .badge-hold { background: rgba(148, 163, 184, 0.12); color: #cbd5e1; border: 1px solid rgba(148, 163, 184, 0.25); }

    .insight-card {
        background: #11151f;
        border: 1px solid #1c2333;
        border-radius: 12px;
        padding: 14px 16px;
        margin-bottom: 12px;
    }

    .section-header {
        font-size: 15px;
        font-weight: 700;
        color: #f1f5f9;
        margin-top: 16px;
        margin-bottom: 8px;
    }
</style>
""", unsafe_allow_html=True)

BASE_URL = "https://api.sleeper.app/v1"
PERMANENT_LEAGUE_ID = "1312141303219249152"

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

# User / Roster Maps
user_map = {
    u["user_id"]: u.get("metadata", {}).get("team_name") or u.get("display_name", f"User {u['user_id']}")
    for u in users
}
roster_owner_map = {
    r["roster_id"]: user_map.get(r["owner_id"], f"Team {r['roster_id']}")
    for r in rosters
}

# ==================== VALUATION ENGINE ====================
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

    base_scores = {
        "WR": 550, "RB": 520, "TE": 600, "QB": 420,
        "DL": 380, "DE": 380, "DT": 330, "LB": 310, "CB": 210, "S": 240, "K": 80
    }
    base = base_scores.get(pos, 250)

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

# ==================== DRAFT PICK INVENTORY & PROJECTIONS ====================
pick_value_base = {1: 650, 2: 320, 3: 140}

# Projected draft order by Max PF (Lowest Max PF gets 1.01 in Toilet Bowl)
max_pf_sorted = sorted(rosters, key=lambda r: (r.get("settings", {}).get("ppts", 0) or r.get("settings", {}).get("fpts", 0)))
projected_pick_slot = {r["roster_id"]: idx + 1 for idx, r in enumerate(max_pf_sorted)}

# Build full pick ownership (2027 to 2029)
team_picks = {r["roster_id"]: [] for r in rosters}
for r in rosters:
    rid = r["roster_id"]
    for yr in [2027, 2028, 2029]:
        yr_short = str(yr)[2:]
        for rd in [1, 2, 3]:
            traded = False
            for tp in traded_picks:
                if str(tp.get("season")) == str(yr) and tp.get("round") == rd and tp.get("roster_id") == rid:
                    traded = True
                    break
            if not traded:
                proj_slot = projected_pick_slot.get(rid, 4)
                team_picks[rid].append({
                    "year": yr, "round": rd, "original_rid": rid,
                    "desc": f"{yr} Rd {rd} (Proj '{yr_short}.0{proj_slot})",
                    "proj_slot": proj_slot,
                    "value": int(pick_value_base[rd] * (1.25 if proj_slot <= 2 else (1.0 if proj_slot <= 5 else 0.85)))
                })

for tp in traded_picks:
    new_owner = tp.get("owner_id")
    orig_roster = tp.get("roster_id")
    try:
        yr = int(tp.get("season", 2027))
    except Exception:
        yr = 2027
    yr_short = str(yr)[2:]
    rd = int(tp.get("round", 1))
    proj_slot = projected_pick_slot.get(orig_roster, 4)
    if new_owner in team_picks:
        team_picks[new_owner].append({
            "year": yr, "round": rd, "original_rid": orig_roster,
            "desc": f"{yr} Rd {rd} via {roster_owner_map.get(orig_roster, 'Team')} (Proj '{yr_short}.0{proj_slot})",
            "proj_slot": proj_slot,
            "value": int(pick_value_base.get(rd, 200) * (1.25 if proj_slot <= 2 else (1.0 if proj_slot <= 5 else 0.85)))
        })

# Sort each team's picks by Year, then Round, then Slot
for rid in team_picks:
    team_picks[rid] = sorted(team_picks[rid], key=lambda x: (x["year"], x["round"], x["proj_slot"]))

# ==================== LEAGUE-WIDE AGGREGATION & 3-YEAR PROJECTIONS ====================
league_stats = []
for r in rosters:
    rid = r["roster_id"]
    tname = roster_owner_map.get(rid, f"Team {rid}")
    p_ids = r.get("players", []) or []
    evals = [evaluate_player(p, all_players.get(p, {})) for p in p_ids]
    
    player_val = sum(x["value"] for x in evals)
    pick_val = sum(p["value"] for p in team_picks.get(rid, []))
    total_dynasty_val = player_val + pick_val
    t_age = sum(x["age"] for x in evals) / max(len(evals), 1)
    
    fpts = r.get("settings", {}).get("fpts", 0) + (r.get("settings", {}).get("fpts_decimal", 0) / 100)
    ppts = r.get("settings", {}).get("ppts", 0) or fpts
    eff_pct = (fpts / ppts * 100) if ppts > 0 else 0.0
    wins = r.get("settings", {}).get("wins", 0)
    losses = r.get("settings", {}).get("losses", 0)

    # 2026 Current Year Title Score (Heavily weighted on 2026 PPG & current W-L)
    win_pct = wins / max(wins + losses, 1)
    title_score_2026 = (win_pct * 45.0) + ((fpts / max(current_week, 1)) * 0.5) + (player_val * 0.001)
    if wins == 0 and current_week >= 2:
        title_score_2026 *= 0.30

    # 2027 Projected Title Score (Youth maturing + 2027 draft capital arriving)
    youth_bonus_2027 = max(0, (26.5 - t_age) * 15)
    picks_2027_val = sum(p["value"] for p in team_picks.get(rid, []) if p["year"] == 2027)
    title_score_2027 = (player_val * 0.03) + youth_bonus_2027 + (picks_2027_val * 0.04)

    # 2028 Projected Title Score (Long runway + full pick stash)
    youth_bonus_2028 = max(0, (26.0 - t_age) * 22)
    picks_2028_val = sum(p["value"] for p in team_picks.get(rid, []) if p["year"] <= 2028)
    title_score_2028 = (player_val * 0.025) + youth_bonus_2028 + (picks_2028_val * 0.05)

    league_stats.append({
        "roster_id": rid,
        "team_name": tname,
        "player_value": player_val,
        "pick_value": pick_val,
        "total_value": total_dynasty_val,
        "avg_age": t_age,
        "points_for": fpts,
        "max_pf": ppts,
        "efficiency": eff_pct,
        "wins": wins,
        "losses": losses,
        "score_2026": title_score_2026,
        "score_2027": title_score_2027,
        "score_2028": title_score_2028
    })

df_league = pd.DataFrame(league_stats)
df_league["rank_val"] = df_league["total_value"].rank(ascending=False, method="min").astype(int)
df_league["rank_age"] = df_league["avg_age"].rank(ascending=True, method="min").astype(int)
df_league["rank_eff"] = df_league["efficiency"].rank(ascending=False, method="min").astype(int)
df_league["rank_standings"] = df_league.sort_values(by=["wins", "points_for"], ascending=[False, False]).reset_index().index + 1

# Calibrate Title Odds % for 2026, 2027, 2028
df_league["odds_2026"] = ((df_league["score_2026"] / max(df_league["score_2026"].sum(), 1.0)) * 100).round(1)
df_league["odds_2027"] = ((df_league["score_2027"] / max(df_league["score_2027"].sum(), 1.0)) * 100).round(1)
df_league["odds_2028"] = ((df_league["score_2028"] / max(df_league["score_2028"].sum(), 1.0)) * 100).round(1)

# ==================== HEADER & SELECTOR ====================
h1, h2 = st.columns([3, 1])
with h1:
    st.markdown(f"## ⚡ {league_info.get('name', 'Dynasty Hub')}")
    st.caption("8 Teams • 1QB • 2TE (+0.25 TEP) • 4 Flex • Big-Play IDP • 2027–2029 Draft Picks")

team_names = [roster_owner_map[r["roster_id"]] for r in rosters]
with h2:
    selected_team_name = st.selectbox("Select Your Franchise", team_names, index=0)

selected_roster = next(r for r in rosters if roster_owner_map[r["roster_id"]] == selected_team_name)
selected_rid = selected_roster["roster_id"]
my_row = df_league[df_league["roster_id"] == selected_rid].iloc[0]

tab_overview, tab_matchup, tab_blueprint, tab_playoffs, tab_trades = st.tabs([
    "👤 Roster & Insights",
    "⚔️ Matchup Outlook",
    "🔮 Future & Prime Years",
    "🎲 Playoffs & Toilet Bowl",
    "📜 Trades & Calculator"
])

# ==================== TAB 1: SPLIT SCREEN ====================
with tab_overview:
    m1, m2, m3, m4 = st.columns(4)
    m1.markdown(f"""
    <div class="metric-card">
        <div style="color: #94a3b8; font-size: 11px; font-weight: 700; letter-spacing: 0.5px;">TOTAL FRANCHISE VALUE</div>
        <div style="font-size: 24px; font-weight: 800; color: #38bdf8; margin: 2px 0;">{my_row['total_value']:,} pts</div>
        <div style="font-size: 11px; color: #4ade80; font-weight: 600;">Rank #{my_row['rank_val']} of 8 ({my_row['pick_value']:,} in Picks)</div>
    </div>
    """, unsafe_allow_html=True)

    m2.markdown(f"""
    <div class="metric-card">
        <div style="color: #94a3b8; font-size: 11px; font-weight: 700; letter-spacing: 0.5px;">ROSTER AVG AGE</div>
        <div style="font-size: 24px; font-weight: 800; color: #f8fafc; margin: 2px 0;">{my_row['avg_age']:.1f} yrs</div>
        <div style="font-size: 11px; color: #818cf8; font-weight: 600;">Rank #{my_row['rank_age']} of 8 (Youth)</div>
    </div>
    """, unsafe_allow_html=True)

    m3.markdown(f"""
    <div class="metric-card">
        <div style="color: #94a3b8; font-size: 11px; font-weight: 700; letter-spacing: 0.5px;">START EFFICIENCY</div>
        <div style="font-size: 24px; font-weight: 800; color: #fbbf24; margin: 2px 0;">{my_row['efficiency']:.1f}%</div>
        <div style="font-size: 11px; color: #94a3b8; font-weight: 600;">Rank #{my_row['rank_eff']} of 8 ({my_row['points_for']:.1f} PF)</div>
    </div>
    """, unsafe_allow_html=True)

    m4.markdown(f"""
    <div class="metric-card">
        <div style="color: #94a3b8; font-size: 11px; font-weight: 700; letter-spacing: 0.5px;">RECORD & STANDINGS</div>
        <div style="font-size: 24px; font-weight: 800; color: #f43f5e; margin: 2px 0;">{my_row['wins']}W - {my_row['losses']}L</div>
        <div style="font-size: 11px; color: #94a3b8; font-weight: 600;">Rank #{my_row['rank_standings']} of 8 overall</div>
    </div>
    """, unsafe_allow_html=True)

    pids = selected_roster.get("players", []) or []
    starters = selected_roster.get("starters", []) or []
    taxi = selected_roster.get("taxi", []) or []
    reserve = selected_roster.get("reserve", []) or []
    bench = [p for p in pids if p not in starters and p not in taxi and p not in reserve]
    player_evals = {pid: evaluate_player(pid, all_players.get(pid, {})) for pid in pids}

    # Split Screen
    col_roster, col_insights = st.columns([1.2, 0.8], gap="medium")

    # ----- LEFT COLUMN: LINEUP -----
    with col_roster:
        def render_compact_lineup(title, player_list, slot_label="BN"):
            st.markdown(f'<div class="section-header">{title} <span style="font-size: 12px; color: #94a3b8; font-weight: 400;">({len(player_list)})</span></div>', unsafe_allow_html=True)
            if not player_list:
                st.caption("No players assigned.")
                return

            league_slots = league_info.get("roster_positions", [])
            for idx, pid in enumerate(player_list):
                p = player_evals.get(pid)
                if not p:
                    continue
                
                if slot_label == "START":
                    raw_slot = league_slots[idx] if idx < len(league_slots) else "FLEX"
                    pos_display = "IDP" if "IDP" in raw_slot else ("DL" if raw_slot in ["DL", "DE", "DT"] else raw_slot)
                else:
                    pos_display = slot_label

                rookie_html = '<span class="badge badge-rookie">ROOKIE</span>' if p["rookie"] else ''
                
                row_html = (
                    f'<div class="lineup-row">'
                    f'  <div style="display: flex; align-items: center; min-width: 0;">'
                    f'      <div class="pos-slot">{pos_display}</div>'
                    f'      <img src="{p["img"]}" class="player-avatar" onerror="this.onerror=null;this.src=\'https://sleepercdn.com/images/v2/icons/player_default.webp\';">'
                    f'      <div style="white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">'
                    f'          <div style="font-size: 13px; font-weight: 600; color: #f8fafc;">{p["name"]} '
                    f'              <span style="font-size: 11px; color: #94a3b8; font-weight: 400;">{p["pos"]} • {p["age"]}yo</span>'
                    f'          </div>'
                    f'          <div style="margin-top: 2px;">'
                    f'              <span class="badge {p["badge"]}">{p["stage"].upper()}</span>'
                    f'              {rookie_html}'
                    f'              <span class="badge {p["act_badge"]}">{p["action"]}</span>'
                    f'          </div>'
                    f'      </div>'
                    f'  </div>'
                    f'  <div style="text-align: right; flex-shrink: 0; margin-left: 8px;">'
                    f'      <div style="font-size: 15px; font-weight: 800; color: #38bdf8;">{p["value"]:,}</div>'
                    f'      <div style="font-size: 10px; color: #64748b;">Dynasty Index</div>'
                    f'  </div>'
                    f'</div>'
                )
                st.markdown(row_html, unsafe_allow_html=True)

        render_compact_lineup("⚡ Starters", starters, slot_label="START")
        render_compact_lineup("🪑 Bench", bench, slot_label="BN")
        render_compact_lineup("🚑 Injured Reserve (IR)", reserve, slot_label="IR")
        render_compact_lineup("🚕 Taxi Squad", taxi, slot_label="TAXI")

    # ----- RIGHT COLUMN: FRANCHISE INTELLIGENCE -----
    with col_insights:
        st.markdown('<div class="section-header">🧠 Franchise Intelligence</div>', unsafe_allow_html=True)
        
        # 1. EXPANDED 3-YEAR PRIME WINDOW & TITLE ODDS
        if my_row["avg_age"] < 24.8:
            prime_window = "2027 – 2030 (Ascending Young Core)"
            strategy_text = "Stockpile draft capital. Your young roster will peak strongly in 1-2 years."
        elif my_row["avg_age"] <= 26.8:
            prime_window = "2026 – 2028 (Apex Prime Window)"
            strategy_text = "Championship caliber core. Optimize starting slots for high-impact weeks."
        else:
            prime_window = "2026 (Closing Window)"
            strategy_text = "Sell players past age 28 for future 1sts before values fall."

        st.markdown(f"""
        <div class="insight-card">
            <div style="color: #94a3b8; font-size: 11px; font-weight: 700;">CHAMPIONSHIP PRIME WINDOW</div>
            <div style="font-size: 20px; font-weight: 800; color: #38bdf8; margin: 3px 0;">{prime_window}</div>
            <p style="font-size: 12px; color: #cbd5e1; margin-bottom: 8px;">{strategy_text}</p>
        </div>
        """, unsafe_allow_html=True)

        # 3-Year Title Odds Interactive Viewer
        st.markdown("""
        <div style="font-size: 12px; font-weight: 700; color: #94a3b8; margin-bottom: 4px;">
            🏆 3-YEAR CHAMPIONSHIP PROBABILITY (ALL TEAMS)
        </div>
        """, unsafe_allow_html=True)
        
        selected_year = st.radio("Season", ["2026 (Current)", "2027 (Next)", "2028 (Year 3)"], horizontal=True, label_visibility="collapsed")
        
        if "2026" in selected_year:
            year_col = "odds_2026"
        elif "2027" in selected_year:
            year_col = "odds_2027"
        else:
            year_col = "odds_2028"

        odds_display_df = df_league[["team_name", year_col]].rename(columns={
            "team_name": "Team", year_col: "Title Chance %"
        }).sort_values(by="Title Chance %", ascending=False)
        
        st.dataframe(
            odds_display_df.style.format({"Title Chance %": "{:.1f}%"}),
            use_container_width=True,
            height=210
        )

        # 2. 2026 Playoff Odds
        playoff_odds = 45 if my_row["wins"] == 0 else (98 if my_row["rank_standings"] <= 4 else 75)
        st.markdown(f"""
        <div class="insight-card">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <div>
                    <div style="color: #94a3b8; font-size: 11px; font-weight: 700;">2026 PLAYOFF ODDS</div>
                    <div style="font-size: 22px; font-weight: 800; color: {'#4ade80' if playoff_odds >= 70 else '#fbbf24'};">{playoff_odds}%</div>
                </div>
                <div style="text-align: right;">
                    <div style="color: #94a3b8; font-size: 11px; font-weight: 700;">2026 TITLE CHANCE</div>
                    <div style="font-size: 22px; font-weight: 800; color: {'#38bdf8' if my_row['odds_2026'] >= 15 else '#f43f5e'};">{my_row['odds_2026']}%</div>
                </div>
            </div>
            <div style="font-size: 11px; color: #64748b; margin-top: 5px;">Reflects 0-2 start, scoring pacing, and 8-team competition.</div>
        </div>
        """, unsafe_allow_html=True)

        # 3. Deduplicated Keepers and Sell Candidates
        superstars = list(dict.fromkeys([player_evals[p]["name"] for p in pids if player_evals.get(p) and player_evals[p]["value"] >= 650]))
        rising = list(dict.fromkeys([player_evals[p]["name"] for p in pids if player_evals.get(p) and player_evals[p]["stage"] == "Rising" and player_evals[p]["value"] >= 450]))
        uncs = list(dict.fromkeys([player_evals[p]["name"] for p in pids if player_evals.get(p) and player_evals[p]["stage"] == "Unc"]))

        st.markdown(f"""
        <div class="insight-card" style="border-left: 3px solid #4ade80;">
            <div style="color: #4ade80; font-size: 11px; font-weight: 700;">🟢 CORNERSTONE KEEPERS</div>
            <p style="font-size: 12px; color: #f1f5f9; margin-top: 3px; margin-bottom: 0;">{', '.join((superstars + rising)[:6]) if (superstars or rising) else 'None identified'}</p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown(f"""
        <div class="insight-card" style="border-left: 3px solid #f43f5e;">
            <div style="color: #f43f5e; font-size: 11px; font-weight: 700;">🔴 TRADE CANDIDATES (SELL HIGH / UNC)</div>
            <p style="font-size: 12px; color: #f1f5f9; margin-top: 3px; margin-bottom: 0;">{', '.join(uncs[:5]) if uncs else 'No aging assets currently'}</p>
        </div>
        """, unsafe_allow_html=True)

        # 4. Toilet Bowl Projection
        tb_leader = df_league.sort_values(by="max_pf").iloc[0]
        st.markdown(f"""
        <div class="insight-card" style="border-left: 3px solid #facc15;">
            <div style="color: #facc15; font-size: 11px; font-weight: 700;">🚽 TOILET BOWL (PICK 1.01 FAVORITE)</div>
            <div style="font-size: 12px; color: #cbd5e1; margin-top: 3px;">
                Lowest Max PF gets Pick 1.01.<br>
                🥇 <strong>Current Leader:</strong> {tb_leader['team_name']} ({tb_leader['max_pf']:.1f} Max PF)
            </div>
        </div>
        """, unsafe_allow_html=True)

        # 5. DRAFT CAPITAL (ALL PICKS AT VERY BOTTOM, GROUPED BY YEAR)
        my_picks = team_picks.get(selected_rid, [])
        st.markdown(f"""
        <div class="insight-card" style="border-left: 3px solid #38bdf8;">
            <div style="color: #38bdf8; font-size: 12px; font-weight: 700;">🎯 DRAFT CAPITAL & PROJECTIONS ({len(my_picks)} TOTAL PICKS)</div>
            <div style="font-size: 11px; color: #94a3b8; margin-bottom: 8px;">Sorted by Draft Year • Projections based on current Max PF order</div>
        """, unsafe_allow_html=True)
        
        if not my_picks:
            st.caption("No picks currently owned.")
        else:
            for yr in [2027, 2028, 2029]:
                yr_picks = [p for p in my_picks if p["year"] == yr]
                if yr_picks:
                    st.markdown(f"<div style='font-size: 12px; font-weight: 700; color: #f8fafc; margin-top: 6px;'>📅 {yr} Picks:</div>", unsafe_allow_html=True)
                    for p in yr_picks:
                        st.markdown(f"""
                        <div style="font-size: 12px; color: #cbd5e1; padding-left: 10px; margin-bottom: 2px;">
                            • <strong>{p['desc']}</strong> <span style="color: #38bdf8; font-weight: 600;">({p['value']:,} pts)</span>
                        </div>
                        """, unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)

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

# ==================== TAB 3: PRIME YEARS BLUEPRINT ====================
with tab_blueprint:
    st.subheader("Championship Runway & 3-Year Trajectories")
    st.dataframe(
        df_league[["team_name", "total_value", "player_value", "pick_value", "avg_age", "odds_2026", "odds_2027", "odds_2028"]].rename(columns={
            "team_name": "Team", "total_value": "Total Dynasty Pts", "player_value": "Roster Pts", "pick_value": "Picks Pts",
            "avg_age": "Avg Age", "odds_2026": "2026 Title %", "odds_2027": "2027 Title %", "odds_2028": "2028 Title %"
        }).style.format({
            "Total Dynasty Pts": "{:,}", "Roster Pts": "{:,}", "Picks Pts": "{:,}", 
            "Avg Age": "{:.1f}", "2026 Title %": "{:.1f}%", "2027 Title %": "{:.1f}%", "2028 Title %": "{:.1f}%"
        }),
        use_container_width=True
    )

# ==================== TAB 4: PLAYOFFS & TOILET BOWL ====================
with tab_playoffs:
    st.subheader("Playoffs (Top 6) & Toilet Bowl (Seeds 7 & 8)")
    st.dataframe(
        df_league[["rank_standings", "team_name", "wins", "losses", "points_for", "max_pf", "odds_2026"]].rename(columns={
            "rank_standings": "Seed", "team_name": "Team", "wins": "W", "losses": "L",
            "points_for": "Points For", "max_pf": "Max PF", "odds_2026": "2026 Title Odds %"
        }).sort_values(by="Seed").style.format({
            "Points For": "{:.1f}", "Max PF": "{:.1f}", "2026 Title Odds %": "{:.1f}%"
        }),
        use_container_width=True
    )

# ==================== TAB 5: TRADES & CALCULATOR ====================
with tab_trades:
    st.subheader("Dynasty Trade Calculator (Incorporates 2027–2029 Picks)")
    ca, cb = st.columns(2)
    with ca:
        ta = st.selectbox("Team A", team_names, index=0, key="t_a")
        r_a = next(r for r in rosters if roster_owner_map[r["roster_id"]] == ta)
        p_a = r_a.get("players", []) or []
        opts_a = {f"{all_players.get(p, {}).get('full_name', p)} ({all_players.get(p, {}).get('position', '-')})": p for p in p_a}
        sel_pa = st.multiselect(f"Players from {ta}", list(opts_a.keys()), key="spa")
        
        my_picks_a = team_picks.get(r_a["roster_id"], [])
        opts_pka = {p["desc"]: p["value"] for p in my_picks_a}
        sel_pka = st.multiselect(f"Draft Picks from {ta}", list(opts_pka.keys()), key="spka")

    with cb:
        tb = st.selectbox("Team B", team_names, index=1 if len(team_names) > 1 else 0, key="t_b")
        r_b = next(r for r in rosters if roster_owner_map[r["roster_id"]] == tb)
        p_b = r_b.get("players", []) or []
        opts_b = {f"{all_players.get(p, {}).get('full_name', p)} ({all_players.get(p, {}).get('position', '-')})": p for p in p_b}
        sel_pb = st.multiselect(f"Players from {tb}", list(opts_b.keys()), key="spb")
        
        my_picks_b = team_picks.get(r_b["roster_id"], [])
        opts_pkb = {p["desc"]: p["value"] for p in my_picks_b}
        sel_pkb = st.multiselect(f"Draft Picks from {tb}", list(opts_pkb.keys()), key="spkb")

    val_a = sum(evaluate_player(opts_a[p], all_players.get(opts_a[p], {}))["value"] for p in sel_pa) + sum(opts_pka[p] for p in sel_pka)
    val_b = sum(evaluate_player(opts_b[p], all_players.get(opts_b[p], {}))["value"] for p in sel_pb) + sum(opts_pkb[p] for p in sel_pkb)

    st.markdown("---")
    res1, res2, res3 = st.columns(3)
    res1.metric(f"{ta} Gives", f"{val_a:,} pts")
    res2.metric(f"{tb} Gives", f"{val_b:,} pts")
    delta = val_a - val_b
    res3.metric("Trade Edge", f"{abs(delta):,} pts", f"{'Favors ' + ta if delta < 0 else 'Favors ' + tb}")
