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
    
    div[data-baseweb="select"] input,
    .stSelectbox input,
    input[aria-autocomplete="list"] {
        pointer-events: none !important;
        caret-color: transparent !important;
        user-select: none !important;
        cursor: pointer !important;
    }
    div[data-baseweb="select"] {
        cursor: pointer !important;
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
    }

    .pos-slot {
        width: 36px;
        height: 24px;
        line-height: 24px;
        font-size: 10px;
        font-weight: 800;
        color: #94a3b8;
        text-align: center;
        background: #181f2e;
        border-radius: 5px;
        margin-right: 8px;
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
        margin-top: 14px;
        margin-bottom: 8px;
    }

    .pos-rank-row {
        display: flex;
        align-items: center;
        justify-content: space-between;
        background: #10141d;
        border: 1px solid #1a2233;
        border-radius: 8px;
        padding: 8px 14px;
        margin-bottom: 6px;
    }
    .pos-rank-pill {
        display: inline-block;
        width: 48px;
        text-align: center;
        padding: 3px 0;
        font-size: 12px;
        font-weight: 800;
        border-radius: 6px;
    }
    .rank-top { background: rgba(74, 222, 128, 0.15); color: #4ade80; border: 1px solid rgba(74, 222, 128, 0.4); }
    .rank-mid { background: rgba(148, 163, 184, 0.12); color: #cbd5e1; border: 1px solid rgba(148, 163, 184, 0.25); }
    .rank-low { background: rgba(244, 63, 94, 0.15); color: #f43f5e; border: 1px solid rgba(244, 63, 94, 0.4); }

    details.player-expand-card {
        background: #10141d;
        border: 1px solid #181e2b;
        border-radius: 8px;
        margin-bottom: 5px;
        overflow: hidden;
        transition: border-color 0.15s ease, background 0.15s ease;
    }
    details.player-expand-card[open] {
        border-color: #38bdf8;
        background: #121724;
    }
    details.player-expand-card summary {
        list-style: none;
        cursor: pointer;
        padding: 7px 10px;
        display: flex;
        align-items: center;
        justify-content: space-between;
        user-select: none;
    }
    details.player-expand-card summary::-webkit-details-marker {
        display: none;
    }

    .chevron-indicator {
        font-size: 14px;
        font-weight: 800;
        color: #64748b;
        margin-right: 8px;
        display: inline-block;
        transition: transform 0.18s ease, color 0.18s ease;
        line-height: 1;
    }
    details.player-expand-card[open] summary .chevron-indicator {
        transform: rotate(90deg);
        color: #38bdf8;
    }

    .player-expand-content {
        padding: 10px 14px 12px 14px;
        border-top: 1px solid #1a2233;
        background: #0d1017;
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

@st.cache_data(ttl=1800)
def get_season_nfl_stats(season_year=2026):
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        r = requests.get(f"{BASE_URL}/stats/nfl/regular/{season_year}", headers=headers, timeout=12)
        if r.status_code == 200:
            return r.json()
    except Exception:
        pass
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
nfl_stats_season = get_season_nfl_stats(2026)
league_info, users, rosters, traded_picks, matchups, current_week, all_trades = fetch_league(league_id)

if not league_info or not rosters:
    st.error(f"⚠️ Could not load Sleeper league for ID: `{league_id}`.")
    st.stop()

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

# ==================== TRUE 1QB UNIFIED DYNASTY VALUATION ENGINE ====================
def evaluate_player(pid, p_info):
    if not p_info:
        return {
            "pid": str(pid), "value": 100, "redraft_val": 80, "stage": "Prime", "badge": "badge-prime",
            "action": "HOLD", "act_badge": "badge-hold", "rookie": False, "ppg": 0.0, "gp": 0,
            "age": 25, "pos": "FLEX", "name": f"Player {pid}", "team": "FA",
            "owner": player_owner_map.get(str(pid), "Free Agent"),
            "img": f"https://sleepercdn.com/content/nfl/players/{pid}.jpg",
            "college": "-", "height": "-", "weight": "-", "number": "-",
            "stat_line": "No stats recorded yet this season.", "desc": "Information currently unavailable."
        }
    
    pos = p_info.get("position", "N/A")
    age = p_info.get("age") or 25
    exp = p_info.get("years_exp") or 0
    is_rookie = exp == 0
    team = p_info.get("team") or "FA"
    owner = player_owner_map.get(str(pid), "Free Agent")
    depth_order = p_info.get("depth_chart_order")
    search_rank = p_info.get("search_rank")

    p_stat = nfl_stats_season.get(str(pid), {})
    gp = int(p_stat.get("gp", 0) or 0)
    pts_half_ppr = float(p_stat.get("pts_half_ppr", 0.0) or p_stat.get("pts_ppr", 0.0) or 0.0)
    ppg = round(pts_half_ppr / gp, 1) if gp > 0 else 0.0

    stat_fragments = []
    scout_fragments = []
    
    if pos == "QB":
        pass_yd = int(p_stat.get("pass_yd", 0))
        pass_td = int(p_stat.get("pass_td", 0))
        pass_int = int(p_stat.get("pass_int", 0))
        rush_yd = int(p_stat.get("rush_yd", 0))
        rush_td = int(p_stat.get("rush_td", 0))
        if pass_yd > 0 or rush_yd > 0:
            stat_fragments.append(f"{pass_yd} Pass Yds • {pass_td} TD • {pass_int} INT")
            if rush_yd > 0:
                stat_fragments.append(f"{rush_yd} Rush Yds • {rush_td} TD")
            scout_fragments.append(f"Starting QB for {team} with {pass_td} TDs.")
    elif pos == "RB":
        rush_att = int(p_stat.get("rush_att", 0))
        rush_yd = int(p_stat.get("rush_yd", 0))
        rush_td = int(p_stat.get("rush_td", 0))
        rec = int(p_stat.get("rec", 0))
        rec_yd = int(p_stat.get("rec_yd", 0))
        if rush_att > 0 or rec > 0:
            stat_fragments.append(f"{rush_att} Car • {rush_yd} Yds • {rush_td} TD")
            if rec > 0:
                stat_fragments.append(f"{rec} Rec • {rec_yd} Yds")
            scout_fragments.append(f"Feature back for {team} logging {rush_att} carries and {rec} receptions.")
    elif pos in ["WR", "TE"]:
        rec = int(p_stat.get("rec", 0))
        rec_yd = int(p_stat.get("rec_yd", 0))
        rec_td = int(p_stat.get("rec_td", 0))
        rec_tgt = int(p_stat.get("rec_tgt", 0))
        if rec_tgt > 0 or rec > 0:
            stat_fragments.append(f"{rec}/{rec_tgt} Targets • {rec_yd} Yds • {rec_td} TD")
            scout_fragments.append(f"Pass-catcher in {team} with {rec_tgt} targets.")
    else:  # IDP
        tkl = int(p_stat.get("idp_tkl", 0) or p_stat.get("tkl", 0))
        sack = float(p_stat.get("idp_sack", 0) or p_stat.get("sack", 0))
        tfl = int(p_stat.get("idp_tkl_loss", 0) or p_stat.get("tkl_loss", 0))
        if tkl > 0 or sack > 0:
            stat_fragments.append(f"{tkl} Tackles • {sack:.1f} Sacks • {tfl} TFL")
            scout_fragments.append(f"Front-7 defender recording {sack:.1f} sacks.")

    stat_line = " | ".join(stat_fragments) if stat_fragments else "0 GP (Pending 2026 debut)"

    if search_rank and search_rank > 0:
        if search_rank <= 5:
            talent_score = 1150 - (search_rank * 12)
        elif search_rank <= 15:
            talent_score = 1040 - ((search_rank - 5) * 10)
        elif search_rank <= 35:
            talent_score = 900 - ((search_rank - 15) * 8)
        elif search_rank <= 80:
            talent_score = 720 - ((search_rank - 35) * 4)
        elif search_rank <= 200:
            talent_score = 520 - ((search_rank - 80) * 2)
        elif search_rank <= 450:
            talent_score = 280 - ((search_rank - 200) * 0.7)
        else:
            talent_score = max(35, 100 - ((search_rank - 450) * 0.08))
    else:
        if depth_order == 1:
            talent_score = 360
        elif depth_order == 2:
            talent_score = 130
        else:
            talent_score = 50

    if pos == "RB":
        pos_multiplier = 1.38
    elif pos == "WR":
        pos_multiplier = 1.32
    elif pos == "TE":
        pos_multiplier = 1.25
    elif pos == "QB":
        if search_rank and search_rank <= 20:
            pos_multiplier = 0.56
        elif search_rank and search_rank <= 60:
            pos_multiplier = 0.38
        elif depth_order and depth_order >= 2:
            pos_multiplier = 0.08
        else:
            pos_multiplier = 0.24
    elif pos in ["DL", "DE"]:
        pos_multiplier = 0.60
    else:
        pos_multiplier = 0.40

    if pos == "RB":
        if age <= 24:
            stage, badge, age_mult = "Rising", "badge-rising", 1.25
        elif age <= 26:
            stage, badge, age_mult = "Prime", "badge-prime", 1.12
        elif age <= 27:
            stage, badge, age_mult = "Prime", "badge-prime", 0.95
        elif age <= 29:
            stage, badge, age_mult = "Descending", "badge-descending", 0.65
        else:
            stage, badge, age_mult = "Unc", "badge-unc", 0.35
    elif pos in ["WR", "TE"]:
        if age <= 24:
            stage, badge, age_mult = "Rising", "badge-rising", 1.22
        elif age <= 27:
            stage, badge, age_mult = "Prime", "badge-prime", 1.10
        elif age <= 29:
            stage, badge, age_mult = "Descending", "badge-descending", 0.85
        else:
            stage, badge, age_mult = "Unc", "badge-unc", 0.50
    elif pos == "QB":
        if age <= 25:
            stage, badge, age_mult = "Rising", "badge-rising", 1.10
        elif age <= 31:
            stage, badge, age_mult = "Prime", "badge-prime", 1.00
        elif age <= 34:
            stage, badge, age_mult = "Descending", "badge-descending", 0.85
        else:
            stage, badge, age_mult = "Unc", "badge-unc", 0.60
    else:  # IDP
        if age <= 25:
            stage, badge, age_mult = "Rising", "badge-rising", 1.10
        elif age <= 28:
            stage, badge, age_mult = "Prime", "badge-prime", 1.00
        else:
            stage, badge, age_mult = "Descending", "badge-descending", 0.70

    dynasty_val = max(int(talent_score * pos_multiplier * age_mult), 25)
    redraft_val = max(int(talent_score * pos_multiplier * (1.1 if stage in ["Prime", "Descending"] else 0.95)), 20)

    if dynasty_val >= 950:
        action, act_badge = "CORNERSTONE", "badge-buy"
    elif stage in ["Descending", "Unc"] and pos in ["RB", "WR"]:
        action, act_badge = "SELL HIGH", "badge-sell"
    elif stage == "Rising" and dynasty_val >= 550:
        action, act_badge = "BUY / STRONG HOLD", "badge-buy"
    elif dynasty_val >= 550:
        action, act_badge = "CORE STARTER", "badge-hold"
    else:
        action, act_badge = "HOLD / DEPTH", "badge-hold"

    full_name = p_info.get('full_name') or f"Player {pid}"
    scout_core = " ".join(scout_fragments)
    if dynasty_val >= 950:
        dynasty_outlook = f"Franchise anchor for {team}. In 1QB 8-team leagues, this caliber of high-scoring starter provides an overwhelming weekly point advantage."
    elif stage == "Rising":
        dynasty_outlook = f"Ascending young stud with foundational multi-year runway. Prime building block for 2027–2029 championship contention."
    elif stage == "Prime":
        dynasty_outlook = f"Peak-producing asset. Generating elite starting lineup efficiency right now."
    elif stage == "Descending":
        dynasty_outlook = f"High immediate win-now scoring, but approaching positional age cliff. Cash in for future 1sts if rebuilding."
    else:
        dynasty_outlook = f"Depth asset in an 8-team format; best used as situational flex or trade sweetener."

    desc = f"{full_name} ({age}yo {pos}, {team}). {scout_core} {dynasty_outlook}"

    return {
        "pid": str(pid), "value": dynasty_val, "redraft_val": redraft_val,
        "stage": stage, "badge": badge, "action": action, "act_badge": act_badge,
        "rookie": is_rookie, "ppg": ppg, "gp": gp, "age": age, "pos": pos, "team": team,
        "owner": owner, "name": full_name,
        "img": f"https://sleepercdn.com/content/nfl/players/{pid}.jpg",
        "college": p_info.get("college") or "N/A",
        "height": p_info.get("height") or "-",
        "weight": p_info.get("weight") or "-",
        "number": p_info.get("number") or "-",
        "stat_line": stat_line, "desc": desc
    }

# ==================== DRAFT PICK INVENTORY & TRADE MAPPING ====================
pick_value_base = {1: 750, 2: 360, 3: 160}
team_picks = {r["roster_id"]: [] for r in rosters}

for r in rosters:
    rid = r["roster_id"]
    for yr in [2027, 2028, 2029]:
        for rd in [1, 2, 3]:
            traded = False
            for tp in traded_picks:
                if str(tp.get("season")) == str(yr) and tp.get("round") == rd and tp.get("roster_id") == rid:
                    traded = True
                    break
            if not traded:
                team_picks[rid].append({
                    "year": yr, "round": rd, "original_rid": rid,
                    "desc": f"{yr} Rd {rd} (Team Pick)",
                    "value": int(pick_value_base[rd])
                })

for tp in traded_picks:
    new_owner = tp.get("owner_id")
    orig_roster = tp.get("roster_id")
    try:
        yr = int(tp.get("season", 2027))
    except Exception:
        yr = 2027
    rd = int(tp.get("round", 1))
    if new_owner in team_picks:
        team_picks[new_owner].append({
            "year": yr, "round": rd, "original_rid": orig_roster,
            "desc": f"{yr} Rd {rd} via {roster_owner_map.get(orig_roster, 'Team')}",
            "value": int(pick_value_base.get(rd, 200))
        })

# Map: original_roster_id -> current_owner_roster_id for 2027 Round 1 picks
pick_2027_rd1_owner = {}
for r in rosters:
    pick_2027_rd1_owner[r["roster_id"]] = r["roster_id"]
for tp in traded_picks:
    if str(tp.get("season")) == "2027" and tp.get("round") == 1:
        orig = tp.get("roster_id")
        current_holder = tp.get("owner_id")
        pick_2027_rd1_owner[orig] = current_holder

# ==================== LEAGUE-WIDE AGGREGATION & STANDINGS ====================
league_stats = []
team_positional_values = {}

for r in rosters:
    rid = r["roster_id"]
    tname = roster_owner_map.get(rid, f"Team {rid}")
    p_ids = r.get("players", []) or []
    evals = [evaluate_player(p, all_players.get(p, {})) for p in p_ids]
    
    player_val = sum(x["value"] for x in evals)
    pick_val = sum(p["value"] for p in team_picks.get(rid, []))
    total_dynasty_val = player_val + pick_val
    t_age = sum(x["age"] for x in evals) / max(len(evals), 1)
    
    qb_val = sum(x["value"] for x in evals if x["pos"] == "QB")
    rb_val = sum(x["value"] for x in evals if x["pos"] == "RB")
    wr_val = sum(x["value"] for x in evals if x["pos"] == "WR")
    te_val = sum(x["value"] for x in evals if x["pos"] == "TE")
    dl_val = sum(x["value"] for x in evals if x["pos"] in ["DL", "DE", "DT"])
    idp_val = sum(x["value"] for x in evals if x["pos"] in ["LB", "CB", "S", "DB"])

    team_positional_values[rid] = {
        "QB": qb_val, "RB": rb_val, "WR": wr_val, "TE": te_val, 
        "DL": dl_val, "IDP": idp_val, "Picks": pick_val, "Overall": total_dynasty_val
    }

    fpts = r.get("settings", {}).get("fpts", 0) + (r.get("settings", {}).get("fpts_decimal", 0) / 100)
    ppts = r.get("settings", {}).get("ppts", 0) or fpts
    eff_pct = (fpts / ppts * 100) if ppts > 0 else 0.0
    wins = r.get("settings", {}).get("wins", 0)
    losses = r.get("settings", {}).get("losses", 0)
    fpts_against = r.get("settings", {}).get("fpts_against", 0) + (r.get("settings", {}).get("fpts_against_decimal", 0) / 100)

    # Simulation Logic
    weeks_played = max(current_week, 1)
    ppg_scoring = fpts / weeks_played
    max_ppg = ppts / weeks_played
    total_season_weeks = 14
    remaining_weeks = max(0, total_season_weeks - weeks_played)

    win_prob = max(0.10, min(0.92, 0.50 + ((ppg_scoring - 180.0) / 120.0)))
    sim_add_wins = round(win_prob * remaining_weeks, 1)
    sim_add_losses = round((1.0 - win_prob) * remaining_weeks, 1)

    proj_wins = round(wins + sim_add_wins, 1)
    proj_losses = round(losses + sim_add_losses, 1)
    proj_pf = round(fpts + (ppg_scoring * remaining_weeks), 1)
    proj_max_pf = round(ppts + (max_ppg * remaining_weeks), 1)

    future_picks_count = len(team_picks.get(rid, []))
    if wins >= 2 or (fpts >= 420 and t_age >= 25.0):
        posture = "🔥 Competing (Win-Now)"
        posture_badge = "badge-buy"
        posture_desc = "Prime scoring core. Buy elite starters to capture the championship."
    elif t_age < 25.2 or future_picks_count >= 10:
        posture = "🏗️ Rebuilding (Picks & Youth)"
        posture_badge = "badge-rookie"
        posture_desc = "Asset rich with high runway. Maximize draft capital and trade aging assets for 2027-2029 1sts."
    else:
        posture = "🚀 Retooling (Youth Shift)"
        posture_badge = "badge-prime"
        posture_desc = "In transition. Pivot away from declining veterans into rising 22-25yo cornerstones."

    league_stats.append({
        "roster_id": rid,
        "team_name": tname,
        "player_value": player_val,
        "pick_value": pick_val,
        "total_value": total_dynasty_val,
        "avg_age": t_age,
        "points_for": fpts,
        "points_against": fpts_against,
        "max_pf": ppts,
        "efficiency": eff_pct,
        "wins": wins,
        "losses": losses,
        "proj_wins": proj_wins,
        "proj_losses": proj_losses,
        "proj_pf": proj_pf,
        "proj_max_pf": proj_max_pf,
        "posture": posture,
        "posture_badge": posture_badge,
        "posture_desc": posture_desc
    })

df_league = pd.DataFrame(league_stats)

# Current Standings calculation
df_curr_calc = df_league.sort_values(by=["wins", "points_for"], ascending=[False, False]).reset_index(drop=True)
curr_seed_dict = {row["roster_id"]: idx + 1 for idx, row in df_curr_calc.iterrows()}

# Projected Standings calculation
df_proj_calc = df_league.sort_values(by=["proj_wins", "proj_pf"], ascending=[False, False]).reset_index(drop=True)
proj_seed_dict = {row["roster_id"]: idx + 1 for idx, row in df_proj_calc.iterrows()}

df_league["seed"] = df_league["roster_id"].map(curr_seed_dict)
df_league["proj_seed"] = df_league["roster_id"].map(proj_seed_dict)

def compute_championship_odds(row):
    w = row["wins"]
    pf = row["points_for"]
    s = row["seed"]
    if s > 6:
        return 1.5
    score = (w * 35.0) + (pf * 0.15) + (15.0 if s <= 2 else 5.0)
    return max(score, 1.0)

scores_raw = [compute_championship_odds(r) for _, r in df_league.iterrows()]
tot_raw = sum(scores_raw)
df_league["odds_2026"] = [round((s / tot_raw) * 100, 1) for s in scores_raw]
df_league["odds_2027"] = [round((r["total_value"] / df_league["total_value"].sum()) * 100, 1) for _, r in df_league.iterrows()]
df_league["odds_2028"] = df_league["odds_2027"]

df_league["rank_val"] = df_league["total_value"].rank(ascending=False, method="min").astype(int)
df_league["rank_age"] = df_league["avg_age"].rank(ascending=True, method="min").astype(int)
df_league["rank_eff"] = df_league["efficiency"].rank(ascending=False, method="min").astype(int)

mean_pf = df_league["points_for"].mean()
mean_pa = df_league["points_against"].mean()
df_league["luck_score"] = ((df_league["points_for"] - mean_pf) - (df_league["points_against"] - mean_pa)) / 50.0

pos_ranks = {}
for p_cat in ["Overall", "QB", "RB", "WR", "TE", "DL", "IDP", "Picks"]:
    sorted_rids = sorted(team_positional_values.keys(), key=lambda x: team_positional_values[x][p_cat], reverse=True)
    pos_ranks[p_cat] = {rid: idx + 1 for idx, rid in enumerate(sorted_rids)}

pool = []
for pid in all_rostered_players:
    p_info = all_players.get(pid, {})
    pool.append(evaluate_player(pid, p_info))

for pid, p_info in all_players.items():
    if pid not in all_rostered_players:
        pos = p_info.get("position")
        team = p_info.get("team")
        status = p_info.get("status")
        if team and status != "Inactive" and pos in ["QB", "RB", "WR", "TE", "DL", "DE", "DT", "LB", "CB", "S", "DB"]:
            pool.append(evaluate_player(pid, p_info))

df_all_ranked = pd.DataFrame(pool)

def get_ordinal(n):
    if 10 <= n % 100 <= 20:
        suffix = 'th'
    else:
        suffix = {1: 'st', 2: 'nd', 3: 'rd'}.get(n % 10, 'th')
    return f"{n}{suffix}"

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

tab_overview, tab_rankings, tab_deepdive, tab_playoffs, tab_trades = st.tabs([
    "👤 Roster & Insights",
    "📈 Overall Dynasty Rankings",
    "🔍 Deep Dive",
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

    total_games = my_row['wins'] + my_row['losses']
    win_pct_display = my_row['wins'] / total_games if total_games > 0 else 0.0
    m4.markdown(f"""
    <div class="metric-card">
        <div style="color: #94a3b8; font-size: 11px; font-weight: 700; letter-spacing: 0.5px;">RECORD & STANDINGS</div>
        <div style="font-size: 24px; font-weight: 800; color: #f43f5e; margin: 2px 0;">{my_row['wins']}W - {my_row['losses']}L</div>
        <div style="font-size: 11px; color: #94a3b8; font-weight: 600;">Current Seed #{my_row['seed']} • Proj Seed #{my_row['proj_seed']} ({my_row['proj_wins']}W-{my_row['proj_losses']}L)</div>
    </div>
    """, unsafe_allow_html=True)

    pids = selected_roster.get("players", []) or []
    starters = selected_roster.get("starters", []) or []
    taxi = selected_roster.get("taxi", []) or []
    reserve = selected_roster.get("reserve", []) or []
    bench = [p for p in pids if p not in starters and p not in taxi and p not in reserve]
    player_evals = {pid: evaluate_player(pid, all_players.get(pid, {})) for pid in pids}

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
                    f'              <span style="font-size: 11px; color: #94a3b8; font-weight: 400;">{p["pos"]} - {p["team"]} • {p["age"]}yo</span>'
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

        playoff_odds = 25 if my_row["wins"] == 0 else (98 if my_row["wins"] >= 2 else 70)
        st.markdown(f"""
        <div class="insight-card">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <div>
                    <div style="color: #94a3b8; font-size: 11px; font-weight: 700;">2026 PLAYOFF ODDS</div>
                    <div style="font-size: 22px; font-weight: 800; color: {'#4ade80' if playoff_odds >= 70 else '#f43f5e'};">{playoff_odds}%</div>
                </div>
                <div style="text-align: right;">
                    <div style="color: #94a3b8; font-size: 11px; font-weight: 700;">2026 TITLE CHANCE</div>
                    <div style="font-size: 22px; font-weight: 800; color: {'#38bdf8' if my_row['odds_2026'] >= 15 else '#f43f5e'};">{my_row['odds_2026']}%</div>
                </div>
            </div>
            <div style="font-size: 11px; color: #64748b; margin-top: 5px;">Based on record ({my_row['wins']}W-{my_row['losses']}L), PF, and playoff seed #{my_row['seed']}.</div>
        </div>
        """, unsafe_allow_html=True)

        superstars = list(dict.fromkeys([player_evals[p]["name"] for p in pids if player_evals.get(p) and player_evals[p]["value"] >= 950]))
        rising = list(dict.fromkeys([player_evals[p]["name"] for p in pids if player_evals.get(p) and player_evals[p]["stage"] == "Rising" and player_evals[p]["value"] >= 650]))
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
    st.markdown("### 📈 Overall Dynasty Player Rankings (1QB Format)")
    st.caption("True 1QB dynasty rankings where elite RBs, WRs, and 2TE premium tight ends rightfully dominate the board.")

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

    # SUB-SECTION: BEST AVAILABLE FA BY POSITION
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

# ==================== TAB 3: DEEP DIVE ====================
with tab_deepdive:
    st.markdown(f"### 🔍 Deep Dive: {selected_team_name}")
    st.caption("Positional power matrix, real-time NFL performance stats, and championship window synchronizer.")

    luck_val = my_row["luck_score"]
    luck_desc = "Unlucky Schedule (High PA)" if luck_val < -0.4 else ("Lucky Breaks (Low PA)" if luck_val > 0.4 else "Neutral Schedule Luck")
    luck_color = "#4ade80" if luck_val > 0.4 else ("#f43f5e" if luck_val < -0.4 else "#94a3b8")

    d1, d2, d3 = st.columns(3)
    d1.markdown(f"""
    <div class="metric-card" style="border-left: 4px solid #38bdf8;">
        <div style="color: #94a3b8; font-size: 11px; font-weight: 700;">STRATEGIC POSTURE</div>
        <div style="font-size: 22px; font-weight: 800; color: #f8fafc; margin: 2px 0;">{my_row['posture']}</div>
        <div style="font-size: 11px; color: #cbd5e1;">{my_row['posture_desc']}</div>
    </div>
    """, unsafe_allow_html=True)

    d2.markdown(f"""
    <div class="metric-card" style="border-left: 4px solid {luck_color};">
        <div style="color: #94a3b8; font-size: 11px; font-weight: 700;">SCHEDULE LUCK RATING</div>
        <div style="font-size: 22px; font-weight: 800; color: {luck_color}; margin: 2px 0;">{luck_val:+.2f}</div>
        <div style="font-size: 11px; color: #cbd5e1;">{luck_desc} (PF: {my_row['points_for']:.1f} • PA: {my_row['points_against']:.1f})</div>
    </div>
    """, unsafe_allow_html=True)

    picks_owned_count = len(team_picks.get(selected_rid, []))
    d3.markdown(f"""
    <div class="metric-card" style="border-left: 4px solid #fbbf24;">
        <div style="color: #94a3b8; font-size: 11px; font-weight: 700;">FUTURE CAPITAL ASSETS</div>
        <div style="font-size: 22px; font-weight: 800; color: #fbbf24; margin: 2px 0;">{picks_owned_count} Picks Owned</div>
        <div style="font-size: 11px; color: #cbd5e1;">Value: {my_row['pick_value']:,} pts across 2027–2029</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="section-header">📊 Franchise Positional Rank Matrix (Out of 8 Teams)</div>', unsafe_allow_html=True)
    
    def render_pos_rank_item(label, p_key):
        rk = pos_ranks[p_key].get(selected_rid, 4)
        pill_class = "rank-top" if rk <= 2 else ("rank-mid" if rk <= 5 else "rank-low")
        val_pts = team_positional_values[selected_rid][p_key]
        return f"""
        <div class="pos-rank-row">
            <span class="pos-rank-pill {pill_class}">{get_ordinal(rk)}</span>
            <span style="font-size: 13px; font-weight: 700; color: #f1f5f9;">{label}</span>
            <span style="font-size: 12px; font-weight: 700; color: #38bdf8;">{val_pts:,} pts</span>
        </div>
        """

    pr_c1, pr_c2 = st.columns(2)
    with pr_c1:
        st.markdown(render_pos_rank_item("Overall Dynasty Power", "Overall"), unsafe_allow_html=True)
        st.markdown(render_pos_rank_item("Quarterbacks (QB)", "QB"), unsafe_allow_html=True)
        st.markdown(render_pos_rank_item("Running Backs (RB)", "RB"), unsafe_allow_html=True)
        st.markdown(render_pos_rank_item("Wide Receivers (WR)", "WR"), unsafe_allow_html=True)
    with pr_c2:
        st.markdown(render_pos_rank_item("Tight Ends (TE)", "TE"), unsafe_allow_html=True)
        st.markdown(render_pos_rank_item("Defensive Line (DL)", "DL"), unsafe_allow_html=True)
        st.markdown(render_pos_rank_item("Secondary & LBs (IDP)", "IDP"), unsafe_allow_html=True)
        st.markdown(render_pos_rank_item("Draft Capital (2027-2029)", "Picks"), unsafe_allow_html=True)

    st.markdown("---")

    col_dd_roster, col_dd_insights = st.columns([1.2, 0.8], gap="medium")

    with col_dd_roster:
        def render_deepdive_player_group(section_title, player_id_list, slot_label="BN"):
            st.markdown(f'<div class="section-header">{section_title} <span style="font-size: 12px; color: #94a3b8; font-weight: 400;">({len(player_id_list)})</span></div>', unsafe_allow_html=True)
            if not player_id_list:
                st.caption("No players assigned.")
                return

            league_slots = league_info.get("roster_positions", [])

            for idx, pid in enumerate(player_id_list):
                p = player_evals.get(pid)
                if not p:
                    continue

                if slot_label == "START":
                    raw_slot = league_slots[idx] if idx < len(league_slots) else "FLEX"
                    pos_display = "IDP" if "IDP" in raw_slot else ("DL" if raw_slot in ["DL", "DE", "DT"] else raw_slot)
                else:
                    pos_display = slot_label

                rookie_html = '<span class="badge badge-rookie">ROOKIE</span>' if p["rookie"] else ''
                diff_val = p['value'] - p['redraft_val']
                diff_color = '#4ade80' if diff_val >= 0 else '#f43f5e'

                card_html = (
                    f'<details class="player-expand-card">'
                    f'  <summary>'
                    f'      <div style="display: flex; align-items: center; min-width: 0;">'
                    f'          <span class="chevron-indicator">›</span>'
                    f'          <div class="pos-slot">{pos_display}</div>'
                    f'          <img src="{p["img"]}" class="player-avatar" onerror="this.onerror=null;this.src=\'https://sleepercdn.com/images/v2/icons/player_default.webp\';">'
                    f'          <div style="white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">'
                    f'              <div style="font-size: 13px; font-weight: 600; color: #f8fafc;">{p["name"]} '
                    f'                  <span style="font-size: 11px; color: #94a3b8; font-weight: 400;">{p["pos"]} - {p["team"]} • {p["age"]}yo</span>'
                    f'              </div>'
                    f'              <div style="margin-top: 2px;">'
                    f'                  <span class="badge {p["badge"]}">{p["stage"].upper()}</span>'
                    f'              {rookie_html}'
                    f'                  <span class="badge {p["act_badge"]}">{p["action"]}</span>'
                    f'              </div>'
                    f'          </div>'
                    f'      </div>'
                    f'      <div style="text-align: right; flex-shrink: 0; margin-left: 8px;">'
                    f'          <div style="font-size: 15px; font-weight: 800; color: #38bdf8;">{p["value"]:,}</div>'
                    f'          <div style="font-size: 10px; color: #64748b;">Dynasty Index</div>'
                    f'      </div>'
                    f'  </summary>'
                    f'  <div class="player-expand-content">'
                    f'      <div style="display: flex; flex-wrap: wrap; justify-content: space-between; gap: 12px;">'
                    f'          <div style="min-width: 170px; font-size: 12px; line-height: 1.7;">'
                    f'              <strong>2026 PPG:</strong> <span style="color: #fbbf24; font-weight: 700;">{p["ppg"]} ppg</span> ({p["gp"]} GP)<br>'
                    f'              <strong>Dynasty Index:</strong> <span style="color: #38bdf8; font-weight: 700;">{p["value"]:,} pts</span><br>'
                    f'              <strong>Redraft Win-Now:</strong> <span style="color: #94a3b8; font-weight: 700;">{p["redraft_val"]:,} pts</span><br>'
                    f'              <strong>Dynasty Premium:</strong> <span style="color: {diff_color}; font-weight: 700;">{diff_val:+d} pts</span>'
                    f'          </div>'
                    f'          <div style="flex: 1; min-width: 210px; font-size: 12px; line-height: 1.6;">'
                    f'              <strong>Real 2026 NFL Stats:</strong><br>'
                    f'              <span style="color: #38bdf8; font-weight: 600;">{p["stat_line"]}</span><br>'
                    f'              <div style="margin-top: 3px; color: #94a3b8; font-size: 11px;">'
                    f'                  #{p["number"]} • {p["college"]} • {p["height"]}, {p["weight"]} lbs'
                    f'              </div>'
                    f'              <p style="color: #cbd5e1; font-size: 11px; margin-top: 4px; margin-bottom: 0;">{p["desc"]}</p>'
                    f'          </div>'
                    f'      </div>'
                    f'  </div>'
                    f'</details>'
                )
                st.markdown(card_html, unsafe_allow_html=True)

        render_deepdive_player_group("⚡ Starters", starters, slot_label="START")
        render_deepdive_player_group("🪑 Bench", bench, slot_label="BN")
        render_deepdive_player_group("🚑 Injured Reserve (IR)", reserve, slot_label="IR")
        render_deepdive_player_group("🚕 Taxi Squad", taxi, slot_label="TAXI")

    with col_dd_insights:
        st.markdown('<div class="section-header">🧠 Window-Maximizing Intelligence</div>', unsafe_allow_html=True)

        my_all_player_objs = [player_evals[p] for p in pids if p in player_evals]
        my_avg_age = my_row["avg_age"]
        is_rebuilding = "Rebuilding" in my_row["posture"] or my_avg_age < 25.2 or my_row["wins"] <= 1
        is_competing = "Competing" in my_row["posture"] and my_row["wins"] >= 2

        out_of_window_players = [
            x for x in my_all_player_objs 
            if x["age"] >= 27 and x["value"] >= 350 and is_rebuilding
        ]
        
        young_window_cornerstones = [
            x for x in my_all_player_objs 
            if x["age"] <= 24 and x["value"] >= 450
        ]

        win_now_veterans = [
            x for x in my_all_player_objs 
            if x["age"] >= 28 and x["redraft_val"] >= 400
        ]

        st.markdown(f"""
        <div class="insight-card" style="border-left: 3px solid #38bdf8;">
            <div style="color: #38bdf8; font-size: 12px; font-weight: 700;">🎯 CHAMPIONSHIP TIMELINE SYNC</div>
            <div style="font-size: 13px; font-weight: 700; color: #f8fafc; margin-top: 4px;">
                {'Target Window: 2027–2030 (Ascending Peak)' if is_rebuilding else 'Target Window: 2026–2028 (Apex Prime Contender)'}
            </div>
            <p style="font-size: 12px; color: #cbd5e1; margin-top: 4px; margin-bottom: 0;">
                {'Your core is built for the near future. Keeping players who will age past their prime before 2027 represents wasted value depreciation. Maximize market leverage by trading them today.' if is_rebuilding else 'Your roster is built to win right now. Do not hoard future draft capital at the expense of starting lineup studs.'}
            </p>
        </div>
        """, unsafe_allow_html=True)

        if is_rebuilding and out_of_window_players:
            out_of_window_names = [f"<strong>{p['name']}</strong> ({p['pos']}, {p['age']}yo • {p['value']:,} pts)" for p in out_of_window_players]
            st.markdown(f"""
            <div class="insight-card" style="border-left: 3px solid #f43f5e;">
                <div style="color: #f43f5e; font-size: 12px; font-weight: 700;">⚠️ URGENT WINDOW MISALIGNMENT (SELL NOW)</div>
                <div style="font-size: 12px; color: #f1f5f9; margin-top: 4px;">
                    These players are producing right now, but will cross the age cliff before your 2027–2029 championship window opens. Trade them immediately while their market value is peaked:
                </div>
                <ul style="font-size: 12px; color: #cbd5e1; margin-top: 6px; padding-left: 18px;">
                    {"".join([f"<li>{item}</li>" for item in out_of_window_names])}
                </ul>
            </div>
            """, unsafe_allow_html=True)
        elif is_competing and win_now_veterans:
            st.markdown(f"""
            <div class="insight-card" style="border-left: 3px solid #fbbf24;">
                <div style="color: #fbbf24; font-size: 12px; font-weight: 700;">🔥 WIN-NOW SCORING FOUNDATION</div>
                <div style="font-size: 12px; color: #cbd5e1; margin-top: 4px;">
                    Veterans fueling your weekly starter ceiling: {', '.join([p['name'] for p in win_now_veterans[:4]])}. Ride these assets through the playoffs rather than selling them for distant picks.
                </div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown(f"""
        <div class="insight-card" style="border-left: 3px solid #4ade80;">
            <div style="color: #4ade80; font-size: 12px; font-weight: 700;">🟢 IN-WINDOW CORNERSTONES (LOCKED ASSETS)</div>
            <div style="font-size: 12px; color: #f1f5f9; margin-top: 4px;">
                Players whose prime aligns with your team's championship runway:
            </div>
            <ul style="font-size: 12px; color: #cbd5e1; margin-top: 6px; padding-left: 18px;">
                <li><strong>Youth Pillars:</strong> {', '.join([p['name'] for p in young_window_cornerstones[:5]]) if young_window_cornerstones else 'Acquire top 2027 picks to inject young talent.'}</li>
                <li><strong>2TE Scarcity:</strong> With 16 required TE starters, hold starting TEs under age 27 tightly.</li>
                <li><strong>Capital Stash:</strong> You control <strong>{picks_owned_count} picks</strong> across 2027–2029.</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

        st.markdown(f"""
        <div class="insight-card" style="border-left: 3px solid #a855f7;">
            <div style="color: #c084fc; font-size: 12px; font-weight: 700;">🔄 TARGETED LEAGUE TRADE BLUEPRINT</div>
            <div style="font-size: 12px; color: #cbd5e1; margin-top: 4px;">
                {'Target contenders who need win-now scoring. Offer them your older pieces for 2027 1st-rounders to maximize your Toilet Bowl draft positioning (lowest Max PF wins pick 1.01).' if is_rebuilding else 'Target rebuilding teams in the league. Offer your 2027/2028 2nd-round picks to buy starting-lineup difference makers.'}
            </div>
        </div>
        """, unsafe_allow_html=True)

# ==================== TAB 4: PLAYOFFS & TOILET BOWL (FIXED SAFE DICTIONARY LOOKUPS) ====================
with tab_playoffs:
    st.markdown("### 🏆 Championship Playoffs & 🚽 Toilet Bowl Race")
    st.caption("Official standings sorted by Win-Loss record, then Points For (PF). Seeds 1–6 advance to the playoffs. Seeds 7 & 8 play in the Toilet Bowl for Pick 1.01.")

    standings_mode = st.radio("Standings View", ["Current Week Standings", "Projected Final Season Standings"], horizontal=True)
    is_proj_mode = "Projected" in standings_mode

    # Use pure list of dictionaries to completely avoid pandas Series KeyError
    active_standings_list = df_proj_calc.to_dict('records') if is_proj_mode else df_curr_calc.to_dict('records')

    c_playoff, c_toilet = st.columns([1.1, 0.9], gap="medium")

    with c_playoff:
        header_label = "🔮 Projected Final Playoff Bracket (Seeds 1 to 6)" if is_proj_mode else "🥇 Current Playoff Bracket (Seeds 1 to 6)"
        st.markdown(f'<div class="section-header">{header_label}</div>', unsafe_allow_html=True)
        
        for idx in range(min(6, len(active_standings_list))):
            row = active_standings_list[idx]
            s_num = idx + 1
            bye_tag = '<span class="badge badge-rising">FIRST ROUND BYE</span>' if s_num <= 2 else '<span class="badge badge-hold">QUARTERFINALS</span>'
            is_me = row['team_name'] == selected_team_name
            highlight_border = "border: 1px solid #38bdf8; background: #131a27;" if is_me else "border: 1px solid #1c2333; background: #11151f;"
            
            p_wins = row.get("proj_wins", row["wins"])
            p_loss = row.get("proj_losses", row["losses"])
            p_pf = row.get("proj_pf", row["points_for"])
            p_mpf = row.get("proj_max_pf", row["max_pf"])
            p_seed = row.get("proj_seed", s_num)

            if is_proj_mode:
                stat_display = f'<div style="font-size: 11px; color: #38bdf8; margin-top: 3px;"><strong>Projected Finish:</strong> {p_wins}W - {p_loss}L • <strong>Proj PF:</strong> {p_pf:.1f} • <strong>Proj Max PF:</strong> {p_mpf:.1f}</div><div style="font-size: 10px; color: #64748b;">(Current Record: {row["wins"]}W - {row["losses"]}L | {row["points_for"]:.1f} PF)</div>'
            else:
                stat_display = f'<div style="font-size: 11px; color: #94a3b8; margin-top: 3px;"><strong>Current Record:</strong> {row["wins"]}W - {row["losses"]}L • <strong>Total PF:</strong> {row["points_for"]:.1f} • <strong>Max PF:</strong> {row["max_pf"]:.1f}</div><div style="font-size: 10px; color: #64748b;">(Simulated Pace: Proj {p_wins}W - {p_loss}L | Proj Seed #{p_seed})</div>'

            card_row = (
                f'<div class="insight-card" style="{highlight_border}; margin-bottom: 8px; padding: 10px 14px;">'
                f'<div style="display: flex; justify-content: space-between; align-items: center;">'
                f'<div>'
                f'<span style="font-size: 14px; font-weight: 800; color: #38bdf8; margin-right: 6px;">#{s_num}</span>'
                f'<strong style="font-size: 14px; color: #f1f5f9;">{row["team_name"]}</strong> {bye_tag}'
                f'{stat_display}'
                f'</div>'
                f'<div style="text-align: right;">'
                f'<div style="font-size: 16px; font-weight: 800; color: #fbbf24;">{row["odds_2026"]}%</div>'
                f'<div style="font-size: 10px; color: #64748b;">Title Odds</div>'
                f'</div>'
                f'</div>'
                f'</div>'
            )
            st.markdown(card_row, unsafe_allow_html=True)

    with c_toilet:
        toilet_header = "🚽 Projected Toilet Bowl (Seeds 7 & 8 Finishers)" if is_proj_mode else "🚽 Current Toilet Bowl (Teams in Seeds 7 & 8)"
        st.markdown(f'<div class="section-header">{toilet_header}</div>', unsafe_allow_html=True)
        
        team_7 = active_standings_list[6]
        team_8 = active_standings_list[7]

        mpf_key = "proj_max_pf" if is_proj_mode else "max_pf"
        
        # Determine 1.01 winner by lower Max PF between 7 & 8
        if team_7[mpf_key] < team_8[mpf_key]:
            pick_101_orig_team = team_7
            pick_102_orig_team = team_8
        else:
            pick_101_orig_team = team_8
            pick_102_orig_team = team_7

        owner_101_rid = pick_2027_rd1_owner.get(pick_101_orig_team['roster_id'], pick_101_orig_team['roster_id'])
        owner_101_name = roster_owner_map.get(owner_101_rid, pick_101_orig_team['team_name'])
        is_101_traded = owner_101_rid != pick_101_orig_team['roster_id']
        display_101 = f"{owner_101_name} <span style='font-size:11px; color:#38bdf8;'>(via {pick_101_orig_team['team_name']})</span>" if is_101_traded else owner_101_name

        owner_102_rid = pick_2027_rd1_owner.get(pick_102_orig_team['roster_id'], pick_102_orig_team['roster_id'])
        owner_102_name = roster_owner_map.get(owner_102_rid, pick_102_orig_team['team_name'])
        is_102_traded = owner_102_rid != pick_102_orig_team['roster_id']
        display_102 = f"{owner_102_name} <span style='font-size:11px; color:#38bdf8;'>(via {pick_102_orig_team['team_name']})</span>" if is_102_traded else owner_102_name

        p1_rec = f"Proj Final: {pick_101_orig_team['proj_wins']}W-{pick_101_orig_team['proj_losses']}L" if is_proj_mode else f"Current: {pick_101_orig_team['wins']}W-{pick_101_orig_team['losses']}L"
        p2_rec = f"Proj Final: {pick_102_orig_team['proj_wins']}W-{pick_102_orig_team['proj_losses']}L" if is_proj_mode else f"Current: {pick_102_orig_team['wins']}W-{pick_102_orig_team['losses']}L"

        toilet_summary = (
            f'<div class="insight-card" style="border-left: 4px solid #facc15; margin-bottom: 12px;">'
            f'<div style="color: #facc15; font-size: 12px; font-weight: 700;">TOILET BOWL (PICK 1.01 DETERMINATION)</div>'
            f'<div style="font-size: 12px; color: #cbd5e1; margin-top: 4px;">'
            f'Combatants: <strong>{team_7["team_name"]}</strong> & <strong>{team_8["team_name"]}</strong>. '
            f'Per league rule: <strong>The lower Max PF between these 2 teams wins Pick 1.01</strong>:'
            f'</div>'
            f'<div style="margin-top: 10px; padding: 8px 12px; background: #0a0d14; border-radius: 8px; border: 1px solid #1a2233;">'
            f'<div style="display: flex; justify-content: space-between; align-items: center;">'
            f'<div>'
            f'<span class="badge badge-rising">WINNER ➔ PICK 1.01</span>'
            f'<strong style="color: #f8fafc; font-size: 13px;">{display_101}</strong>'
            f'<div style="font-size: 11px; color: #94a3b8;">{p1_rec}</div>'
            f'</div>'
            f'<span style="font-size: 13px; font-weight: 800; color: #4ade80;">{pick_101_orig_team[mpf_key]:.1f} Max PF</span>'
            f'</div>'
            f'</div>'
            f'<div style="margin-top: 6px; padding: 8px 12px; background: #0a0d14; border-radius: 8px; border: 1px solid #1a2233;">'
            f'<div style="display: flex; justify-content: space-between; align-items: center;">'
            f'<div>'
            f'<span class="badge badge-hold">RUNNER-UP ➔ PICK 1.02</span>'
            f'<strong style="color: #f8fafc; font-size: 13px;">{display_102}</strong>'
            f'<div style="font-size: 11px; color: #94a3b8;">{p2_rec}</div>'
            f'</div>'
            f'<span style="font-size: 13px; font-weight: 800; color: #94a3b8;">{pick_102_orig_team[mpf_key]:.1f} Max PF</span>'
            f'</div>'
            f'</div>'
            f'</div>'
        )
        st.markdown(toilet_summary, unsafe_allow_html=True)

        board_header = "🎯 Projected 2027 Round 1 Draft Order (End-of-Season Simulation)" if is_proj_mode else "🎯 Projected 2027 Round 1 Draft Order (Current Standings)"
        st.markdown(f'<div class="section-header">{board_header}</div>', unsafe_allow_html=True)
        
        # Sort playoff teams (seeds 1 to 6) in reverse Max PF order
        playoff_six_sorted = sorted(active_standings_list[:6], key=lambda x: x[mpf_key])
        
        full_proj_order = [
            (pick_101_orig_team['roster_id'], pick_101_orig_team['team_name'], pick_101_orig_team[mpf_key]),
            (pick_102_orig_team['roster_id'], pick_102_orig_team['team_name'], pick_102_orig_team[mpf_key])
        ]
        for p_row in playoff_six_sorted:
            full_proj_order.append((p_row['roster_id'], p_row['team_name'], p_row[mpf_key]))

        for slot_idx, (orig_rid, orig_tname, mpf_val) in enumerate(full_proj_order, 1):
            curr_holder_rid = pick_2027_rd1_owner.get(orig_rid, orig_rid)
            curr_holder_name = roster_owner_map.get(curr_holder_rid, orig_tname)
            is_traded = curr_holder_rid != orig_rid
            
            is_me = curr_holder_name == selected_team_name
            highlight_border = "border: 1px solid #38bdf8; background: #131a27;" if is_me else "border: 1px solid #181e2b; background: #10141d;"
            
            if is_traded:
                pick_owner_text = f"{curr_holder_name} <span style='font-size: 11px; color: #38bdf8; font-weight: normal;'>(via {orig_tname})</span>"
            else:
                pick_owner_text = curr_holder_name

            order_row = (
                f'<div class="odds-row" style="{highlight_border}; padding: 6px 12px;">'
                f'<div style="font-size: 12px; font-weight: 700; color: {"#38bdf8" if is_me else "#f8fafc"};">'
                f'<span style="color: #64748b; margin-right: 8px;">Pick 1.0{slot_idx}</span> {pick_owner_text}'
                f'</div>'
                f'<div style="font-size: 11px; font-weight: 600; color: #94a3b8;">{mpf_val:.1f} Max PF</div>'
                f'</div>'
            )
            st.markdown(order_row, unsafe_allow_html=True)

# ==================== TAB 5: TRADES & AI IMPACT ANALYZER ====================
with tab_trades:
    st.markdown("### 📜 Dynasty Trade Analyzer & Positional Shift Simulator")
    st.caption("Construct multi-asset trades with players and 2027–2029 draft picks. Run the simulator to calculate your trade grade and positional rank shifts.")

    ca, cb = st.columns(2, gap="medium")
    with ca:
        ta = st.selectbox("Franchise A (Your Team)", team_names, index=team_names.index(selected_team_name) if selected_team_name in team_names else 0, key="t_a")
        r_a = next(r for r in rosters if roster_owner_map[r["roster_id"]] == ta)
        p_a = r_a.get("players", []) or []
        opts_a = {f"{all_players.get(p, {}).get('full_name', p)} ({all_players.get(p, {}).get('position', '-')}) - {evaluate_player(p, all_players.get(p, {}))['value']:,} pts": p for p in p_a}
        sel_pa = st.multiselect(f"Players sent by {ta}", list(opts_a.keys()), key="spa")
        
        my_picks_a = team_picks.get(r_a["roster_id"], [])
        opts_pka = {f"{p['desc']} ({p['value']:,} pts)": p for p in my_picks_a}
        sel_pka = st.multiselect(f"Draft Picks sent by {ta}", list(opts_pka.keys()), key="spka")

    with cb:
        tb = st.selectbox("Franchise B (Trade Partner)", [t for t in team_names if t != ta], index=0, key="t_b")
        r_b = next(r for r in rosters if roster_owner_map[r["roster_id"]] == tb)
        p_b = r_b.get("players", []) or []
        opts_b = {f"{all_players.get(p, {}).get('full_name', p)} ({all_players.get(p, {}).get('position', '-')}) - {evaluate_player(p, all_players.get(p, {}))['value']:,} pts": p for p in p_b}
        sel_pb = st.multiselect(f"Players sent by {tb}", list(opts_b.keys()), key="spb")
        
        my_picks_b = team_picks.get(r_b["roster_id"], [])
        opts_pkb = {f"{p['desc']} ({p['value']:,} pts)": p for p in my_picks_b}
        sel_pkb = st.multiselect(f"Draft Picks sent by {tb}", list(opts_pkb.keys()), key="spkb")

    val_a = sum(evaluate_player(opts_a[p], all_players.get(opts_a[p], {}))["value"] for p in sel_pa) + sum(opts_pka[p]["value"] for p in sel_pka)
    val_b = sum(evaluate_player(opts_b[p], all_players.get(opts_b[p], {}))["value"] for p in sel_pb) + sum(opts_pkb[p]["value"] for p in sel_pkb)

    st.markdown("---")
    res1, res2, res3 = st.columns(3)
    res1.metric(f"{ta} Gives", f"{val_a:,} pts")
    res2.metric(f"{tb} Gives", f"{val_b:,} pts")
    delta = val_b - val_a
    res3.metric("Net Value For " + ta, f"{abs(delta):,} pts", f"{'Surplus (+)' if delta >= 0 else 'Deficit (-)'}")

    st.markdown("")
    analyze_btn = st.button("⚡ Analyze Trade Impact & Positional Shifts", use_container_width=True, type="primary")

    if analyze_btn:
        if val_a == 0 and val_b == 0:
            st.warning("Please select at least one player or draft pick on each side to analyze.")
        else:
            ratio = (val_b / max(val_a, 1))
            if ratio >= 1.25:
                grade, grade_color = "A+", "#4ade80"
                verdict = "Smash Accept / Overwhelming Value Win"
            elif ratio >= 1.08:
                grade, grade_color = "A", "#4ade80"
                verdict = "Strong Value Win for Your Franchise"
            elif ratio >= 0.94:
                grade, grade_color = "B+", "#38bdf8"
                verdict = "Fair & Balanced Deal"
            elif ratio >= 0.80:
                grade, grade_color = "C", "#fbbf24"
                verdict = "Slight Loss in Value / Overpay"
            elif ratio >= 0.65:
                grade, grade_color = "D", "#f97316"
                verdict = "Significant Value Loss"
            else:
                grade, grade_color = "F", "#f43f5e"
                verdict = "Horrendous Trade / Do Not Accept"

            st.markdown(f"""
            <div class="metric-card" style="border-left: 4px solid {grade_color}; margin-top: 14px;">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <div>
                        <div style="color: #94a3b8; font-size: 11px; font-weight: 700;">TRADE GRADE FOR {ta.upper()}</div>
                        <div style="font-size: 32px; font-weight: 800; color: {grade_color}; margin: 2px 0;">{grade}</div>
                        <div style="font-size: 13px; font-weight: 700; color: #f1f5f9;">{verdict}</div>
                    </div>
                    <div style="text-align: right; max-width: 450px;">
                        <div style="font-size: 12px; color: #cbd5e1;">
                            {'This trade gains net dynasty value and improves your asset equity.' if delta >= 0 else 'You are giving away more overall value than you are receiving in return.'}
                        </div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

            st.markdown("#### 🔄 Projected Positional Rank Shift for " + ta)
            
            sim_pos_val = team_positional_values[r_a["roster_id"]].copy()

            for p in sel_pa:
                p_obj = evaluate_player(opts_a[p], all_players.get(opts_a[p], {}))
                p_cat = "DL" if p_obj["pos"] in ["DL", "DE", "DT"] else ("IDP" if p_obj["pos"] in ["LB", "CB", "S", "DB"] else p_obj["pos"])
                if p_cat in sim_pos_val:
                    sim_pos_val[p_cat] -= p_obj["value"]
                sim_pos_val["Overall"] -= p_obj["value"]

            for pk in sel_pka:
                sim_pos_val["Picks"] -= opts_pka[pk]["value"]
                sim_pos_val["Overall"] -= opts_pka[pk]["value"]

            for p in sel_pb:
                p_obj = evaluate_player(opts_b[p], all_players.get(opts_b[p], {}))
                p_cat = "DL" if p_obj["pos"] in ["DL", "DE", "DT"] else ("IDP" if p_obj["pos"] in ["LB", "CB", "S", "DB"] else p_obj["pos"])
                if p_cat in sim_pos_val:
                    sim_pos_val[p_cat] -= p_obj["value"]
                sim_pos_val["Overall"] -= p_obj["value"]

            for pk in sel_pkb:
                sim_pos_val["Picks"] += opts_pkb[pk]["value"]
                sim_pos_val["Overall"] += opts_pkb[pk]["value"]

            shift_cols = st.columns(4)
            checked_cats = ["Overall", "QB", "RB", "WR", "TE", "DL", "IDP", "Picks"]
            
            for idx, c_name in enumerate(checked_cats):
                col_target = shift_cols[idx % 4]
                curr_rank = pos_ranks[c_name][r_a["roster_id"]]
                
                all_others = [team_positional_values[rid][c_name] for rid in team_positional_values if rid != r_a["roster_id"]]
                sim_rank = sum(1 for val in all_others if val > sim_pos_val[c_name]) + 1

                rank_diff = curr_rank - sim_rank
                if rank_diff > 0:
                    shift_str = f"▲ Improved by +{rank_diff}"
                    shift_color = "#4ade80"
                elif rank_diff < 0:
                    shift_str = f"▼ Dropped by {rank_diff}"
                    shift_color = "#f43f5e"
                else:
                    shift_str = "— Unchanged"
                    shift_color = "#94a3b8"

                col_target.markdown(f"""
                <div class="odds-row" style="padding: 10px; margin-bottom: 8px;">
                    <div>
                        <div style="color: #94a3b8; font-size: 11px; font-weight: 700;">{c_name} ROOM</div>
                        <div style="font-size: 14px; font-weight: 800; color: #f1f5f9;">
                            #{curr_rank} ➔ <span style="color: #38bdf8;">#{sim_rank}</span>
                        </div>
                    </div>
                    <div style="font-size: 11px; font-weight: 700; color: {shift_color}; text-align: right;">
                        {shift_str}
                    </div>
                </div>
                """, unsafe_allow_html=True)
