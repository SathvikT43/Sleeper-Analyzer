import streamlit as st
import pandas as pd
import requests

st.set_page_config(
    page_title="Dynasty Hub & Lineup Architect", 
    page_icon="⚡", 
    layout="wide", 
    initial_sidebar_state="collapsed"
)

# ==================== MODERN DARK THEME CSS ====================
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
    
    .rank-slot {
        width: 36px;
        font-size: 12px;
        font-weight: 800;
        color: #64748b;
        text-align: center;
        margin-right: 10px;
        flex-shrink: 0;
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
    .badge-owner { background: rgba(168, 85, 247, 0.15); color: #d8b4fe; border: 1px solid rgba(168, 85, 247, 0.35); }
    .badge-fa { background: rgba(100, 116, 139, 0.15); color: #94a3b8; border: 1px solid rgba(100, 116, 139, 0.35); }

    .insight-card {
        background: #11151f;
        border: 1px solid #1c2333;
        border-radius: 12px;
        padding: 14px 16px;
        margin-bottom: 12px;
    }

    .odds-row {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 6px 10px;
        background: #10141d;
        border: 1px solid #181e2b;
        border-radius: 7px;
        margin-bottom: 4px;
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

# Maps
user_map = {
    u["user_id"]: u.get("metadata", {}).get("team_name") or u.get("display_name", f"User {u['user_id']}")
    for u in users
}
roster_owner_map = {
    r["roster_id"]: user_map.get(r["owner_id"], f"Team {r['roster_id']}")
    for r in rosters
}

player_owner_map = {}
all_rostered_players = set()
for r in rosters:
    owner_name = roster_owner_map.get(r["roster_id"], f"Team {r['roster_id']}")
    p_list = r.get("players", []) or []
    for pid in p_list:
        player_owner_map[pid] = owner_name
        all_rostered_players.add(pid)

# ==================== TRUE TALENT & QUALITY DYNASTY ENGINE ====================
# Accurately values top tier studs (Josh Allen, CeeDee Lamb, Bijan Robinson, etc.)
# Incorporates Sleeper search rank + depth chart order + positional premiums
def evaluate_player(pid, p_info):
    if not p_info:
        return {
            "pid": str(pid), "value": 100, "stage": "Prime", "badge": "badge-prime",
            "action": "HOLD", "act_badge": "badge-hold", "rookie": False,
            "age": 25, "pos": "FLEX", "name": f"Player {pid}", "team": "FA",
            "owner": player_owner_map.get(str(pid), "Free Agent"),
            "img": f"https://sleepercdn.com/content/nfl/players/{pid}.jpg"
        }
    
    pos = p_info.get("position", "N/A")
    age = p_info.get("age") or 25
    exp = p_info.get("years_exp") or 0
    is_rookie = exp == 0
    team = p_info.get("team") or "FA"
    owner = player_owner_map.get(str(pid), "Free Agent")
    depth_order = p_info.get("depth_chart_order")
    search_rank = p_info.get("search_rank")

    # 1. BASE TALENT SCORE: Derived from actual NFL status & consensus market ranking
    # Search rank <= 100 is an elite fantasy superstar (Josh Allen, Jefferson, Chase, etc.)
    if search_rank and search_rank > 0:
        if search_rank <= 12:       # Elite tier 1 overall
            talent_score = 920 - (search_rank * 8)
        elif search_rank <= 40:     # Top tier starters
            talent_score = 800 - ((search_rank - 12) * 5)
        elif search_rank <= 100:    # High end starters
            talent_score = 660 - ((search_rank - 40) * 3)
        elif search_rank <= 250:    # Core starters & rotation pieces
            talent_score = 480 - ((search_rank - 100) * 1.5)
        elif search_rank <= 500:    # Depth & backups
            talent_score = 250 - ((search_rank - 250) * 0.5)
        else:                       # Bench depth / waiver flyers
            talent_score = max(50, 130 - ((search_rank - 500) * 0.05))
    else:
        # Fallback based on depth chart if search rank is missing
        if depth_order == 1:
            talent_score = 420
        elif depth_order == 2:
            talent_score = 160
        else:
            talent_score = 70

    # 2. POSITION WEIGHTING FOR YOUR SPECIFIC LEAGUE FORMAT:
    # 8 Teams | 1QB | 2TE (+0.25 TEP) | 4 Flex | Big Play IDP
    pos_multiplier = 1.0
    if pos == "TE":
        # 16 required TE starters across 8 teams + 0.25 TEP boost
        pos_multiplier = 1.28
    elif pos == "QB":
        # Elite QBs (Allen, Mahomes, Lamar) produce massive weekly advantages
        if search_rank and search_rank <= 30:
            pos_multiplier = 1.25
        elif depth_order and depth_order >= 2:
            # Backup QBs in 1QB have essentially ZERO trade/starting value
            pos_multiplier = 0.25
        else:
            pos_multiplier = 0.90
    elif pos in ["DL", "DE"]:
        # Sacks (4 pts) and TFL (3 pts) reward premier edge rushers
        pos_multiplier = 1.10
    elif pos in ["CB", "S", "DB"]:
        pos_multiplier = 0.75

    # 3. AGE CURVES BASED ON LONGEVITY:
    if pos == "QB":
        if age <= 25:
            stage, badge, age_mult = "Rising", "badge-rising", 1.15
        elif age <= 32:
            stage, badge, age_mult = "Prime", "badge-prime", 1.05
        elif age <= 35:
            stage, badge, age_mult = "Descending", "badge-descending", 0.85
        else:
            stage, badge, age_mult = "Unc", "badge-unc", 0.60
    elif pos in ["RB"]:
        if age <= 23:
            stage, badge, age_mult = "Rising", "badge-rising", 1.25
        elif age <= 26:
            stage, badge, age_mult = "Prime", "badge-prime", 1.05
        elif age <= 28:
            stage, badge, age_mult = "Descending", "badge-descending", 0.70
        else:
            stage, badge, age_mult = "Unc", "badge-unc", 0.35
    elif pos in ["WR", "TE"]:
        if age <= 24:
            stage, badge, age_mult = "Rising", "badge-rising", 1.20
        elif age <= 28:
            stage, badge, age_mult = "Prime", "badge-prime", 1.05
        elif age <= 30:
            stage, badge, age_mult = "Descending", "badge-descending", 0.80
        else:
            stage, badge, age_mult = "Unc", "badge-unc", 0.45
    else:  # IDP
        if age <= 24:
            stage, badge, age_mult = "Rising", "badge-rising", 1.15
        elif age <= 28:
            stage, badge, age_mult = "Prime", "badge-prime", 1.00
        else:
            stage, badge, age_mult = "Descending", "badge-descending", 0.70

    # Final Uncapped Value
    final_val = int(talent_score * pos_multiplier * age_mult)

    # Dynamic Action Tags
    if final_val >= 750:
        action, act_badge = "CORNERSTONE", "badge-buy"
    elif stage in ["Descending", "Unc"] and pos in ["RB", "WR"]:
        action, act_badge = "SELL HIGH", "badge-sell"
    elif stage == "Rising" and final_val >= 400:
        action, act_badge = "BUY / STRONG HOLD", "badge-buy"
    elif final_val >= 450:
        action, act_badge = "CORE STARTER", "badge-hold"
    else:
        action, act_badge = "HOLD / DEPTH", "badge-hold"

    return {
        "pid": str(pid), "value": max(final_val, 25), "stage": stage, "badge": badge,
        "action": action, "act_badge": act_badge, "rookie": is_rookie,
        "age": age, "pos": pos, "team": team, "owner": owner,
        "name": p_info.get("full_name") or f"Player {pid}",
        "img": f"https://sleepercdn.com/content/nfl/players/{pid}.jpg"
    }

# ==================== DRAFT PICK INVENTORY & PROJECTIONS ====================
pick_value_base = {1: 750, 2: 360, 3: 160}
max_pf_sorted = sorted(rosters, key=lambda r: (r.get("settings", {}).get("ppts", 0) or r.get("settings", {}).get("fpts", 0)))
projected_pick_slot = {r["roster_id"]: idx + 1 for idx, r in enumerate(max_pf_sorted)}

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
                    "value": int(pick_value_base[rd] * (1.35 if proj_slot <= 2 else (1.0 if proj_slot <= 5 else 0.85)))
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
            "value": int(pick_value_base.get(rd, 200) * (1.35 if proj_slot <= 2 else (1.0 if proj_slot <= 5 else 0.85)))
        })

for rid in team_picks:
    team_picks[rid] = sorted(team_picks[rid], key=lambda x: (x["year"], x["round"], x["proj_slot"]))

# ==================== LEAGUE-WIDE AGGREGATION ====================
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

    win_pct = wins / max(wins + losses, 1)
    title_score_2026 = (win_pct * 50.0) + ((fpts / max(current_week, 1)) * 0.5) + (player_val * 0.0008)
    if wins == 0 and current_week >= 2:
        title_score_2026 *= 0.25

    picks_2027_val = sum(p["value"] for p in team_picks.get(rid, []) if p["year"] == 2027)
    age_factor_2027 = max(0.6, 1.4 - (max(0, t_age - 24.5) * 0.15))
    title_score_2027 = (player_val * age_factor_2027 * 0.01) + (picks_2027_val * 0.006)

    all_future_picks = sum(p["value"] for p in team_picks.get(rid, []))
    age_factor_2028 = max(0.4, 1.6 - (max(0, t_age - 24.0) * 0.25))
    title_score_2028 = (player_val * age_factor_2028 * 0.01) + (all_future_picks * 0.008)

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

df_league["odds_2026"] = ((df_league["score_2026"] / max(df_league["score_2026"].sum(), 1.0)) * 100).round(1)
df_league["odds_2027"] = ((df_league["score_2027"] / max(df_league["score_2027"].sum(), 1.0)) * 100).round(1)
df_league["odds_2028"] = ((df_league["score_2028"] / max(df_league["score_2028"].sum(), 1.0)) * 100).round(1)

# ==================== POOL OF PLAYERS ====================
@st.cache_data(ttl=600)
def generate_rankings_pool(p_dict, r_set):
    pool = []
    for pid in r_set:
        p_info = p_dict.get(pid, {})
        pool.append(evaluate_player(pid, p_info))
    
    for pid, p_info in p_dict.items():
        if pid not in r_set:
            pos = p_info.get("position")
            team = p_info.get("team")
            status = p_info.get("status")
            if team and status != "Inactive" and pos in ["QB", "RB", "WR", "TE", "DL", "DE", "DT", "LB", "CB", "S", "DB"]:
                pool.append(evaluate_player(pid, p_info))
    return pd.DataFrame(pool)

df_all_ranked = generate_rankings_pool(all_players, all_rostered_players)

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

tab_overview, tab_rankings, tab_blueprint, tab_playoffs, tab_trades = st.tabs([
    "👤 Roster & Insights",
    "📈 Overall Dynasty Rankings",
    "🔮 Future & Prime Years",
    "🎲 Playoffs & Toilet Bowl",
    "📜 Trades & Calculator"
])

# ==================== TAB 1: SPLIT SCREEN (ROSTER + INTELLIGENCE) ====================
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

    total_games = my_row['wins'] + my_row['losses']
    win_pct_display = my_row['wins'] / total_games if total_games > 0 else 0.0
    m4.markdown(f"""
    <div class="metric-card">
        <div style="color: #94a3b8; font-size: 11px; font-weight: 700; letter-spacing: 0.5px;">RECORD & STANDINGS</div>
        <div style="font-size: 24px; font-weight: 800; color: #f43f5e; margin: 2px 0;">{my_row['wins']}W - {my_row['losses']}L</div>
        <div style="font-size: 11px; color: #94a3b8; font-weight: 600;">Win Rate: {win_pct_display:.2f}</div>
    </div>
    """, unsafe_allow_html=True)

    pids = selected_roster.get("players", []) or []
    starters = selected_roster.get("starters", []) or []
    taxi = selected_roster.get("taxi", []) or []
    reserve = selected_roster.get("reserve", []) or []
    bench = [p for p in pids if p not in starters and p not in taxi and p not in reserve]
    player_evals = {pid: evaluate_player(pid, all_players.get(pid, {})) for pid in pids}

    # Split: Left (Lineup) | Right (Insights)
    col_roster, col_insights = st.columns([1.2, 0.8], gap="medium")

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

    with col_insights:
        st.markdown('<div class="section-header">🧠 Franchise Intelligence</div>', unsafe_allow_html=True)
        
        # 1. Combined Prime Window & 3-Year Odds
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
            <div style="font-size: 19px; font-weight: 800; color: #38bdf8; margin: 3px 0;">{prime_window}</div>
            <p style="font-size: 12px; color: #cbd5e1; margin-bottom: 12px;">{strategy_text}</p>
            <div style="border-top: 1px solid #1c2333; padding-top: 10px; margin-bottom: 8px;">
                <div style="color: #94a3b8; font-size: 11px; font-weight: 700;">🏆 3-YEAR CHAMPIONSHIP PROBABILITY</div>
            </div>
        """, unsafe_allow_html=True)

        selected_year = st.radio("Season", ["2026 (Current)", "2027 (Next)", "2028 (Year 3)"], horizontal=True, label_visibility="collapsed")
        year_col = "odds_2026" if "2026" in selected_year else ("odds_2027" if "2027" in selected_year else "odds_2028")
        sorted_odds = df_league[["team_name", year_col]].sort_values(by=year_col, ascending=False).reset_index(drop=True)

        for rank, row in enumerate(sorted_odds.itertuples(), 1):
            is_me = row.team_name == selected_team_name
            highlight_border = "border: 1px solid #38bdf8; background: #151f2e;" if is_me else "border: 1px solid #181e2b; background: #10141d;"
            accent_color = "#38bdf8" if is_me else "#f8fafc"
            
            row_html = (
                f'<div class="odds-row" style="{highlight_border}">'
                f'  <div style="font-size: 12px; font-weight: 600; color: {accent_color};">'
                f'      <span style="color: #64748b; margin-right: 6px;">#{rank}</span> {row.team_name}'
                f'  </div>'
                f'  <div style="font-size: 12px; font-weight: 800; color: #fbbf24;">{getattr(row, year_col):.1f}%</div>'
                f'</div>'
            )
            st.markdown(row_html, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

        # 2. 2026 Playoff Odds
        playoff_odds = 45 if my_row["wins"] == 0 else (98 if my_row["odds_2026"] >= 15 else 75)
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
            <div style="font-size: 11px; color: #64748b; margin-top: 5px;">Reflects 0-2 start, weekly points, and 8-team competition.</div>
        </div>
        """, unsafe_allow_html=True)

        # 3. Deduplicated Keepers & Sell Candidates
        superstars = list(dict.fromkeys([player_evals[p]["name"] for p in pids if player_evals.get(p) and player_evals[p]["value"] >= 750]))
        rising = list(dict.fromkeys([player_evals[p]["name"] for p in pids if player_evals.get(p) and player_evals[p]["stage"] == "Rising" and player_evals[p]["value"] >= 500]))
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

        # 4. Draft Capital
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

# ==================== TAB 2: OVERALL DYNASTY RANKINGS & FREE AGENT HUB ====================
with tab_rankings:
    st.markdown("### 📈 Overall Dynasty Player Rankings")
    st.caption("Caliber-weighted dynasty asset valuations across all NFL players, active rosters, and free agency pool.")

    f1, f2, f3, f4 = st.columns([1.5, 1.5, 2, 1.2])
    with f1:
        filter_pos = st.selectbox("Position", ["All Positions", "QB", "RB", "WR", "TE", "DL (Edge/Interior)", "IDP (LB/DB)"])
    with f2:
        filter_owner = st.selectbox("Player Pool", ["All Players", "Rostered Only", "Free Agents Only"])
    with f3:
        age_slider = st.slider("Age Filter", min_value=20, max_value=38, value=(20, 36))
    with f4:
        display_limit = st.selectbox("Show Top", [50, 25, 100], index=0)

    filtered_df = df_all_ranked.copy()

    if filter_pos == "QB":
        filtered_df = filtered_df[filtered_df["pos"] == "QB"]
    elif filter_pos == "RB":
        filtered_df = filtered_df[filtered_df["pos"] == "RB"]
    elif filter_pos == "WR":
        filtered_df = filtered_df[filtered_df["pos"] == "WR"]
    elif filter_pos == "TE":
        filtered_df = filtered_df[filtered_df["pos"] == "TE"]
    elif "DL" in filter_pos:
        filtered_df = filtered_df[filtered_df["pos"].isin(["DL", "DE", "DT"])]
    elif "IDP" in filter_pos:
        filtered_df = filtered_df[filtered_df["pos"].isin(["LB", "CB", "S", "DB"])]

    if filter_owner == "Rostered Only":
        filtered_df = filtered_df[filtered_df["owner"] != "Free Agent"]
    elif filter_owner == "Free Agents Only":
        filtered_df = filtered_df[filtered_df["owner"] == "Free Agent"]

    filtered_df = filtered_df[(filtered_df["age"] >= age_slider[0]) & (filtered_df["age"] <= age_slider[1])]
    sorted_df = filtered_df.sort_values(by="value", ascending=False).head(display_limit).reset_index(drop=True)

    if sorted_df.empty:
        st.info("No players found matching your criteria.")
    else:
        for rank, p in sorted_df.iterrows():
            rk_num = rank + 1
            rookie_html = '<span class="badge badge-rookie">ROOKIE</span>' if p["rookie"] else ''
            
            if p["owner"] == "Free Agent":
                owner_html = '<span class="badge badge-fa">FREE AGENT</span>'
            else:
                is_my_player = p["owner"] == selected_team_name
                owner_border = "border: 1px solid #38bdf8;" if is_my_player else ""
                owner_html = f'<span class="badge badge-owner" style="{owner_border}">{p["owner"]}</span>'

            row_html = (
                f'<div class="lineup-row">'
                f'  <div style="display: flex; align-items: center; min-width: 0;">'
                f'      <div class="rank-slot">#{rk_num}</div>'
                f'      <img src="{p["img"]}" class="player-avatar" onerror="this.onerror=null;this.src=\'https://sleepercdn.com/images/v2/icons/player_default.webp\';">'
                f'      <div style="white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">'
                f'          <div style="font-size: 14px; font-weight: 600; color: #f8fafc;">{p["name"]} '
                f'              <span style="font-size: 11px; color: #94a3b8; font-weight: 400;">{p["pos"]} - {p["team"]} • {p["age"]}yo</span>'
                f'          </div>'
                f'          <div style="margin-top: 2px;">'
                f'              <span class="badge {p["badge"]}">{p["stage"].upper()}</span>'
                f'              {rookie_html}'
                f'              {owner_html}'
                f'              <span class="badge {p["act_badge"]}">{p["action"]}</span>'
                f'          </div>'
                f'      </div>'
                f'  </div>'
                f'  <div style="text-align: right; flex-shrink: 0; margin-left: 10px;">'
                f'      <div style="font-size: 17px; font-weight: 800; color: #38bdf8;">{p["value"]:,}</div>'
                f'      <div style="font-size: 10px; color: #64748b;">Dynasty Index</div>'
                f'  </div>'
                f'</div>'
            )
            st.markdown(row_html, unsafe_allow_html=True)

    # ------------------ SUB-SECTION: BEST AVAILABLE FA BY POSITION ------------------
    st.markdown("---")
    st.markdown("### 💎 Best Available Free Agents (Waiver Wire Hub)")
    st.caption("Top unowned talent ready to claim, categorized by positional scarcity.")

    fa_pool_all = df_all_ranked[df_all_ranked["owner"] == "Free Agent"].copy()

    fa_qb_tab, fa_rb_tab, fa_wr_tab, fa_te_tab, fa_dl_tab, fa_idp_tab = st.tabs([
        "🏈 QB", "🏃 RB", "👐 WR", "🛡️ TE", "⚡ DL (Edge/DT)", "🎯 IDP (LB/DB)"
    ])

    def render_fa_grid(sub_df):
        if sub_df.empty:
            st.caption("No free agents found for this category.")
            return
        for rk, fa in sub_df.head(6).reset_index(drop=True).iterrows():
            rookie_tag = '<span class="badge badge-rookie">ROOKIE</span>' if fa["rookie"] else ''
            fa_row = (
                f'<div class="odds-row" style="padding: 8px 12px; margin-bottom: 6px;">'
                f'  <div style="display: flex; align-items: center; min-width: 0;">'
                f'      <span style="font-size: 12px; font-weight: 700; color: #64748b; margin-right: 8px;">#{rk + 1}</span>'
                f'      <img src="{fa["img"]}" class="player-avatar" style="width: 30px; height: 30px; margin-right: 8px;" onerror="this.onerror=null;this.src=\'https://sleepercdn.com/images/v2/icons/player_default.webp\';">'
                f'      <div style="white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">'
                f'          <div style="font-size: 13px; font-weight: 600; color: #f8fafc;">{fa["name"]} '
                f'              <span style="font-size: 11px; color: #94a3b8;">{fa["pos"]} - {fa["team"]} • {fa["age"]}yo</span>'
                f'          </div>'
                f'          <div style="margin-top: 1px;"><span class="badge {fa["badge"]}">{fa["stage"].upper()}</span>{rookie_tag}</div>'
                f'      </div>'
                f'  </div>'
                f'  <div style="font-size: 14px; font-weight: 800; color: #c084fc; margin-left: 10px;">{fa["value"]:,} pts</div>'
                f'</div>'
            )
            st.markdown(fa_row, unsafe_allow_html=True)

    with fa_qb_tab:
        render_fa_grid(fa_pool_all[fa_pool_all["pos"] == "QB"].sort_values(by="value", ascending=False))
    with fa_rb_tab:
        render_fa_grid(fa_pool_all[fa_pool_all["pos"] == "RB"].sort_values(by="value", ascending=False))
    with fa_wr_tab:
        render_fa_grid(fa_pool_all[fa_pool_all["pos"] == "WR"].sort_values(by="value", ascending=False))
    with fa_te_tab:
        render_fa_grid(fa_pool_all[fa_pool_all["pos"] == "TE"].sort_values(by="value", ascending=False))
    with fa_dl_tab:
        render_fa_grid(fa_pool_all[fa_pool_all["pos"].isin(["DL", "DE", "DT"])].sort_values(by="value", ascending=False))
    with fa_idp_tab:
        render_fa_grid(fa_pool_all[fa_pool_all["pos"].isin(["LB", "CB", "S", "DB"])].sort_values(by="value", ascending=False))

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
        df_league[["team_name", "wins", "losses", "points_for", "max_pf", "odds_2026"]].rename(columns={
            "team_name": "Team", "wins": "W", "losses": "L",
            "points_for": "Points For", "max_pf": "Max PF", "odds_2026": "2026 Title Odds %"
        }).sort_values(by=["W", "Points For"], ascending=[False, False]).style.format({
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
