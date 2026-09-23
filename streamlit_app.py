import streamlit as st
import pandas as pd
import requests
from datetime import datetime

st.set_page_config(
    page_title="Dynasty Hub & Lineup Architect", 
    page_icon="⚡", 
    layout="wide", 
    initial_sidebar_state="expanded"
)

# ==================== IOS PWA & LIQUID GLASS CSS ====================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

    @media (display-mode: standalone) {
        body { background-color: #04060b; }
    }

    .stApp {
        background-color: #04060b;
        background-image: 
            radial-gradient(at 10% 10%, rgba(14, 30, 60, 0.4) 0px, transparent 50%),
            radial-gradient(at 90% 10%, rgba(40, 15, 60, 0.3) 0px, transparent 50%),
            radial-gradient(at 50% 50%, rgba(8, 15, 30, 0.6) 0px, transparent 100%);
        color: #f1f5f9;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, "SF Pro Text", "SF Pro Display", sans-serif;
    }
    
    button[kind="header"] { display: none !important; }
    
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

    section[data-testid="stSidebar"] {
        width: 280px !important;
        background: rgba(8, 12, 20, 0.85) !important;
        backdrop-filter: blur(30px);
        -webkit-backdrop-filter: blur(30px);
        border-right: 1px solid rgba(255, 255, 255, 0.08);
    }
    
    section[data-testid="stSidebar"] .block-container {
        padding-top: 2rem;
    }

    .glass-header {
        background: rgba(255, 255, 255, 0.025);
        backdrop-filter: blur(24px);
        -webkit-backdrop-filter: blur(24px);
        border: 1px solid rgba(255, 255, 255, 0.07);
        border-top: 1px solid rgba(255, 255, 255, 0.15);
        border-radius: 18px;
        padding: 16px 24px;
        margin-bottom: 20px;
        display: flex;
        align-items: center;
        justify-content: space-between;
        box-shadow: 0 12px 40px 0 rgba(0, 0, 0, 0.45);
    }

    .metric-card {
        background: rgba(255, 255, 255, 0.025);
        backdrop-filter: blur(24px);
        -webkit-backdrop-filter: blur(24px);
        border: 1px solid rgba(255, 255, 255, 0.07);
        border-top: 1px solid rgba(255, 255, 255, 0.15);
        border-radius: 16px;
        padding: 16px 20px;
        margin-bottom: 16px;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
        transition: transform 0.2s ease, border-color 0.2s ease;
    }
    .metric-card:hover {
        border-color: rgba(56, 189, 248, 0.3);
    }

    .lineup-row {
        display: flex;
        align-items: center;
        justify-content: space-between;
        background: rgba(255, 255, 255, 0.015);
        backdrop-filter: blur(16px);
        -webkit-backdrop-filter: blur(16px);
        border: 1px solid rgba(255, 255, 255, 0.05);
        border-top: 1px solid rgba(255, 255, 255, 0.09);
        border-radius: 12px;
        padding: 9px 14px;
        margin-bottom: 6px;
        transition: all 0.2s ease;
    }
    .lineup-row:hover {
        background: rgba(255, 255, 255, 0.035);
        border-color: rgba(56, 189, 248, 0.3);
    }

    .pos-slot {
        width: 38px;
        height: 25px;
        line-height: 25px;
        font-size: 10px;
        font-weight: 800;
        color: #94a3b8;
        text-align: center;
        background: rgba(255, 255, 255, 0.04);
        border-radius: 7px;
        margin-right: 10px;
        flex-shrink: 0;
        border: 1px solid rgba(255, 255, 255, 0.08);
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
        width: 36px;
        height: 36px;
        border-radius: 50%;
        object-fit: cover;
        background: #19202f;
        border: 1px solid rgba(255, 255, 255, 0.15);
        margin-right: 12px;
        flex-shrink: 0;
        box-shadow: 0 2px 8px rgba(0,0,0,0.3);
    }

    .badge {
        padding: 2px 7px;
        border-radius: 6px;
        font-size: 9px;
        font-weight: 700;
        display: inline-block;
        margin-right: 4px;
    }
    .badge-rookie { background: rgba(56, 189, 248, 0.12); color: #38bdf8; border: 1px solid rgba(56, 189, 248, 0.3); }
    .badge-rising { background: rgba(74, 222, 128, 0.12); color: #4ade80; border: 1px solid rgba(74, 222, 128, 0.3); }
    .badge-prime { background: rgba(129, 140, 248, 0.12); color: #818cf8; border: 1px solid rgba(129, 140, 248, 0.3); }
    .badge-descending { background: rgba(251, 146, 60, 0.12); color: #fb923c; border: 1px solid rgba(251, 146, 60, 0.3); }
    .badge-unc { background: rgba(244, 63, 94, 0.12); color: #f43f5e; border: 1px solid rgba(244, 63, 94, 0.3); }
    
    .badge-buy { background: rgba(34, 197, 94, 0.12); color: #86efac; border: 1px solid rgba(34, 197, 94, 0.3); }
    .badge-sell { background: rgba(239, 68, 68, 0.12); color: #fca5a5; border: 1px solid rgba(239, 68, 68, 0.3); }
    .badge-hold { background: rgba(148, 163, 184, 0.1); color: #cbd5e1; border: 1px solid rgba(148, 163, 184, 0.2); }
    .badge-owner { background: rgba(168, 85, 247, 0.12); color: #d8b4fe; border: 1px solid rgba(168, 85, 247, 0.3); }
    .badge-fa { background: rgba(100, 116, 139, 0.12); color: #94a3b8; border: 1px solid rgba(100, 116, 139, 0.3); }

    .insight-card {
        background: rgba(255, 255, 255, 0.02);
        backdrop-filter: blur(24px);
        -webkit-backdrop-filter: blur(24px);
        border: 1px solid rgba(255, 255, 255, 0.06);
        border-top: 1px solid rgba(255, 255, 255, 0.12);
        border-radius: 18px;
        padding: 18px 20px;
        margin-bottom: 14px;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.3);
    }

    .odds-row {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 8px 12px;
        background: rgba(255, 255, 255, 0.01);
        border: 1px solid rgba(255, 255, 255, 0.04);
        border-top: 1px solid rgba(255, 255, 255, 0.07);
        border-radius: 10px;
        margin-bottom: 6px;
    }

    .section-header {
        font-size: 15px;
        font-weight: 700;
        color: #f8fafc;
        margin-top: 18px;
        margin-bottom: 10px;
        letter-spacing: 0.3px;
    }

    .pos-rank-row {
        display: flex;
        align-items: center;
        justify-content: space-between;
        background: rgba(255, 255, 255, 0.018);
        border: 1px solid rgba(255, 255, 255, 0.05);
        border-top: 1px solid rgba(255, 255, 255, 0.09);
        border-radius: 12px;
        padding: 10px 14px;
        margin-bottom: 8px;
    }
    .pos-rank-pill {
        display: inline-block;
        width: 50px;
        text-align: center;
        padding: 4px 0;
        font-size: 12px;
        font-weight: 800;
        border-radius: 7px;
    }
    .rank-top { background: rgba(74, 222, 128, 0.15); color: #4ade80; border: 1px solid rgba(74, 222, 128, 0.35); }
    .rank-mid { background: rgba(148, 163, 184, 0.1); color: #cbd5e1; border: 1px solid rgba(148, 163, 184, 0.25); }
    .rank-low { background: rgba(244, 63, 94, 0.15); color: #f43f5e; border: 1px solid rgba(244, 63, 94, 0.35); }

    details.player-expand-card {
        background: rgba(255, 255, 255, 0.015);
        backdrop-filter: blur(16px);
        border: 1px solid rgba(255, 255, 255, 0.05);
        border-top: 1px solid rgba(255, 255, 255, 0.09);
        border-radius: 12px;
        margin-bottom: 6px;
        overflow: hidden;
        transition: all 0.2s ease;
    }
    details.player-expand-card[open] {
        border-color: rgba(56, 189, 248, 0.4);
        background: rgba(255, 255, 255, 0.035);
    }
    details.player-expand-card summary {
        list-style: none;
        cursor: pointer;
        padding: 9px 12px;
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
        padding: 12px 16px 14px 16px;
        border-top: 1px solid rgba(255, 255, 255, 0.06);
        background: rgba(0, 0, 0, 0.4);
    }
</style>
""", unsafe_allow_html=True)

st.markdown("""
    <meta name="apple-mobile-web-app-capable" content="yes">
    <meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
    <meta name="apple-mobile-web-app-title" content="Dynasty Hub">
""", unsafe_allow_html=True)

BASE_URL = "https://api.sleeper.app/v1"
PERMANENT_LEAGUE_ID = "1312141303219249152"
league_id = PERMANENT_LEAGUE_ID

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

@st.cache_data(ttl=120)
def get_live_matchups_and_stats(l_id: str, week_num: int):
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        league_info = requests.get(f"{BASE_URL}/league/{l_id}", headers=headers, timeout=10).json()
        users = requests.get(f"{BASE_URL}/league/{l_id}/users", headers=headers, timeout=10).json() or []
        rosters = requests.get(f"{BASE_URL}/league/{l_id}/rosters", headers=headers, timeout=10).json() or []
        traded_picks = requests.get(f"{BASE_URL}/league/{l_id}/traded_picks", headers=headers, timeout=10).json() or []
        
        matchups = requests.get(f"{BASE_URL}/league/{l_id}/matchups/{week_num}", headers=headers, timeout=10).json() or []
        
        stats_resp = requests.get(f"{BASE_URL}/stats/nfl/regular/2026/{week_num}", headers=headers, timeout=10)
        weekly_stats = stats_resp.json() if stats_resp.status_code == 200 else {}

        return league_info, users, rosters, traded_picks, matchups, weekly_stats
    except Exception:
        return None, [], [], [], [], {}

all_players = get_all_players()

# ==================== SLIDEOUT PANEL (SIDEBAR NAVIGATION) ====================
with st.sidebar:
    st.markdown("<h3 style='color: #f8fafc; font-size: 16px; font-weight: 800; margin-bottom: 12px;'>⚡ Dynasty Navigation</h3>", unsafe_allow_html=True)
    nav_selection = st.radio(
        "Navigation", 
        [
            "👤 Roster & Insights", 
            "📈 Overall Dynasty Rankings", 
            "🔍 Deep Dive", 
            "⚔️ Fantasy Matchups", 
            "🏈 NFL Schedule & Scores", 
            "🎲 Playoffs & Toilet Bowl", 
            "📜 Trades & Calculator"
        ],
        label_visibility="collapsed"
    )
    st.markdown("---")

league_info, users, rosters, traded_picks, matchups, weekly_stats = get_live_matchups_and_stats(league_id, 3)

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

    p_stat = weekly_stats.get(str(pid), {})
    pts = float(p_stat.get("pts_half_ppr", 0.0) or p_stat.get("pts_ppr", 0.0) or p_stat.get("fantasy_points", 0.0) or 0.0)

    dynasty_val = max(100, int(1000 - (search_rank if search_rank else 200) * 1.5))
    redraft_val = int(dynasty_val * 0.9)

    return {
        "pid": str(pid), "value": dynasty_val, "redraft_val": redraft_val,
        "stage": "Prime", "badge": "badge-prime", "action": "HOLD", "act_badge": "badge-hold",
        "rookie": is_rookie, "ppg": pts, "gp": 1, "age": age, "pos": pos, "team": team,
        "owner": owner, "name": p_info.get('full_name') or f"Player {pid}",
        "img": f"https://sleepercdn.com/content/nfl/players/{pid}.jpg",
        "college": p_info.get("college") or "N/A", "number": p_info.get("number") or "-",
        "stat_line": f"{pts:.1f} Fantasy Pts", "desc": f"Active starter for {team}."
    }

# ==================== DRAFT PICK INVENTORY (2027–2029 ONLY, SORTED) ====================
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
                    "sort_key": (yr, rd, 0),
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
    if yr >= 2027:
        rd = int(tp.get("round", 1))
        if new_owner in team_picks:
            team_picks[new_owner].append({
                "year": yr, "round": rd, "original_rid": orig_roster,
                "sort_key": (yr, rd, 1),
                "desc": f"{yr} Rd {rd} via {roster_owner_map.get(orig_roster, 'Team')}",
                "value": int(pick_value_base.get(rd, 200))
            })

for rid in team_picks:
    team_picks[rid] = sorted(team_picks[rid], key=lambda x: (x["year"], x["round"], x["sort_key"][2]))

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

    weeks_played = 3
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

df_curr_calc = df_league.sort_values(by=["wins", "points_for"], ascending=[False, False]).reset_index(drop=True)
curr_seed_dict = {row["roster_id"]: idx + 1 for idx, row in df_curr_calc.iterrows()}

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

# ==================== HEADER & FRANCHISE SELECTOR ====================
team_names = [roster_owner_map[r["roster_id"]] for r in rosters]

st.markdown(f"""
<div class="glass-header">
    <div>
        <h1 style="font-size: 24px; font-weight: 800; color: #f8fafc; margin: 0; letter-spacing: -0.5px;">⚡ {league_info.get('name', 'Dynasty Hub')}</h1>
        <p style="font-size: 12px; color: #94a3b8; margin: 3px 0 0 0;">8 Teams • 1QB • 2TE (+0.25 TEP) • 4 Flex • Big-Play IDP • 2027–2029 Draft Picks</p>
    </div>
</div>
""", unsafe_allow_html=True)

selected_team_name = st.selectbox("Active Franchise", team_names, index=0)

selected_roster = next(r for r in rosters if roster_owner_map[r["roster_id"]] == selected_team_name)
selected_rid = selected_roster["roster_id"]
my_row = df_league[df_league["roster_id"] == selected_rid].iloc[0]

# ==================== CONDITIONAL VIEW RENDERER ====================
if nav_selection == "👤 Roster & Insights":
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
            <div style="border-top: 1px solid rgba(255,255,255,0.06); padding-top: 10px; margin-bottom: 8px;">
                <div style="color: #94a3b8; font-size: 11px; font-weight: 700;">🏆 3-YEAR CHAMPIONSHIP PROBABILITY</div>
            </div>
        """, unsafe_allow_html=True)

        selected_year = st.radio("Season", ["2026 (Current)", "2027 (Next)", "2028 (Year 3)"], horizontal=True, label_visibility="collapsed")
        year_col = "odds_2026" if "2026" in selected_year else ("odds_2027" if "2027" in selected_year else "odds_2028")
        sorted_odds = df_league[["team_name", year_col]].sort_values(by=year_col, ascending=False).reset_index(drop=True)

        for rank, row in enumerate(sorted_odds.itertuples(), 1):
            is_me = row.team_name == selected_team_name
            highlight_border = "border: 1px solid rgba(56, 189, 248, 0.4); background: rgba(56, 189, 248, 0.05);" if is_me else ""
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

elif nav_selection == "📈 Overall Dynasty Rankings":
    st.markdown("### 📈 Overall Dynasty Player Rankings (1QB Format)")
    st.caption("True 1QB dynasty rankings where elite RBs, WRs, and 2TE premium tight ends rightfully dominate the board.")

    f1, f2, f3, f4 = st.columns([1.5, 1.5, 2, 1.2])
    with f1:
        filter_pos = st.selectbox("Position", ["All Positions", "QB", "RB", "WR", "TE", "DL (Edge/Interior)", "IDP (LB/DB)"], key="rk_pos")
    with f2:
        filter_owner = st.selectbox("Player Pool", ["All Players", "Rostered Only", "Free Agents Only"], key="rk_pool")
    with f3:
        age_slider = st.slider("Age Filter", min_value=20, max_value=38, value=(20, 36), key="rk_age")
    with f4:
        display_limit = st.selectbox("Show Top", [50, 25, 100], index=0, key="rk_limit")

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

    for rank, p in sorted_df.iterrows():
        rk_num = rank + 1
        rookie_html = '<span class="badge badge-rookie">ROOKIE</span>' if p["rookie"] else ''
        owner_html = '<span class="badge badge-fa">FREE AGENT</span>' if p["owner"] == "Free Agent" else f'<span class="badge badge-owner">{p["owner"]}</span>'
        row_html = (
            f'<div class="lineup-row">'
            f'  <div style="display: flex; align-items: center; min-width: 0;">'
            f'      <div class="rank-slot">#{rk_num}</div>'
            f'      <img src="{p["img"]}" class="player-avatar" onerror="this.onerror=null;this.src=\'https://sleepercdn.com/images/v2/icons/player_default.webp\';">'
            f'      <div style="white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">'
            f'          <div style="font-size: 14px; font-weight: 600; color: #f8fafc;">{p["name"]} '
            f'              <span style="font-size: 11px; color: #94a3b8; font-weight: 400;">{p["pos"]} - {p["team"]} • {p["age"]}yo</span>'
            f'          </div>'
            f'          <div style="margin-top: 2px;"><span class="badge {p["badge"]}">{p["stage"].upper()}</span>{rookie_html}{owner_html}<span class="badge {p["act_badge"]}">{p["action"]}</span></div>'
            f'      </div>'
            f'  </div>'
            f'  <div style="text-align: right; flex-shrink: 0; margin-left: 10px;">'
            f'      <div style="font-size: 17px; font-weight: 800; color: #38bdf8;">{p["value"]:,}</div>'
            f'      <div style="font-size: 10px; color: #64748b;">Dynasty Index</div>'
            f'  </div>'
            f'</div>'
        )
        st.markdown(row_html, unsafe_allow_html=True)

elif nav_selection == "🔍 Deep Dive":
    st.markdown(f"### 🔍 Deep Dive: {selected_team_name}")
    st.caption("Positional power matrix, real-time NFL performance stats, and championship window synchronizer.")

    luck_val = my_row["luck_score"]
    luck_color = "#4ade80" if luck_val > 0.4 else ("#f43f5e" if luck_val < -0.4 else "#94a3b8")
    d1, d2, d3 = st.columns(3)
    d1.markdown(f'<div class="metric-card"><div style="color: #94a3b8; font-size: 11px; font-weight: 700;">STRATEGIC POSTURE</div><div style="font-size: 22px; font-weight: 800; color: #f8fafc; margin: 2px 0;">{my_row["posture"]}</div><div style="font-size: 11px; color: #cbd5e1;">{my_row["posture_desc"]}</div></div>', unsafe_allow_html=True)
    d2.markdown(f'<div class="metric-card"><div style="color: #94a3b8; font-size: 11px; font-weight: 700;">SCHEDULE LUCK RATING</div><div style="font-size: 22px; font-weight: 800; color: {luck_color}; margin: 2px 0;">{luck_val:+.2f}</div></div>', unsafe_allow_html=True)
    d3.markdown(f'<div class="metric-card"><div style="color: #94a3b8; font-size: 11px; font-weight: 700;">FUTURE CAPITAL ASSETS</div><div style="font-size: 22px; font-weight: 800; color: #fbbf24; margin: 2px 0;">{len(team_picks.get(selected_rid, []))} Picks Owned</div></div>', unsafe_allow_html=True)

elif nav_selection == "⚔️ Fantasy Matchups":
    st.markdown("### ⚔️ Live Fantasy Matchups & Scoreboard (Week 3)")
    st.caption("Real-time head-to-head scores, individual player stats, and pre-game win probabilities.")

    cur_matchups = matchups
    if not cur_matchups:
        st.info("No matchup data currently recorded for Week 3.")
    else:
        matchup_pairs = {}
        for m in cur_matchups:
            mid = m.get("match_id")
            if mid is not None:
                if mid not in matchup_pairs:
                    matchup_pairs[mid] = []
                matchup_pairs[mid].append(m)

        for mid, pair in matchup_pairs.items():
            if len(pair) == 2:
                team1, team2 = pair[0], pair[1]
                t1_rid = team1.get("roster_id")
                t2_rid = team2.get("roster_id")
                t1_name = roster_owner_map.get(t1_rid, "Team")
                t2_name = roster_owner_map.get(t2_rid, "Team")
                t1_pts = float(team1.get("points", 0.0) or 0.0)
                t2_pts = float(team2.get("points", 0.0) or 0.0)

                t1_val = team_positional_values.get(t1_rid, {}).get("Overall", 10000)
                t2_val = team_positional_values.get(t2_rid, {}).get("Overall", 10000)
                total_val = max(t1_val + t2_val, 1)
                t1_win_prob = round((t1_val / total_val) * 100)
                t2_win_prob = 100 - t1_win_prob

                st.markdown(f"""
                <div class="insight-card" style="padding: 16px 20px; margin-bottom: 14px;">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <div style="flex: 1; text-align: left;">
                            <div style="font-size: 15px; font-weight: 700; color: #f8fafc;">{t1_name}</div>
                            <div style="font-size: 26px; font-weight: 800; color: #f1f5f9; margin-top: 2px;">{t1_pts:.2f} pts</div>
                            <div style="font-size: 11px; color: #4ade80; font-weight: 600;">Win Prob: {t1_win_prob}%</div>
                        </div>
                        <div style="padding: 0 16px; font-size: 13px; font-weight: 800; color: #64748b;">VS</div>
                        <div style="flex: 1; text-align: right;">
                            <div style="font-size: 15px; font-weight: 700; color: #f8fafc;">{t2_name}</div>
                            <div style="font-size: 26px; font-weight: 800; color: #f1f5f9; margin-top: 2px;">{t2_pts:.2f} pts</div>
                            <div style="font-size: 11px; color: #4ade80; font-weight: 600;">Win Prob: {t2_win_prob}%</div>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

elif nav_selection == "🏈 NFL Schedule & Scores":
    st.markdown("### 🏈 Real-Time NFL Game Center & Scores (Week 3)")
    st.caption("Live NFL scores, team logos, and prime-time prime game tags (TNF, SNF, MNF).")
    
    try:
        nfl_games_resp = requests.get("https://site.api.espn.com/apis/site/v2/sports/football/nfl/scoreboard", timeout=6)
        if nfl_games_resp.status_code == 200:
            events = nfl_games_resp.json().get("events", [])
            if events:
                for ev in events:
                    comp = ev.get("competitions", [{}])[0]
                    competitors = comp.get("competitors", [])
                    game_date_str = ev.get("date", "")
                    
                    prime_tag = ""
                    try:
                        g_dt = datetime.fromisoformat(game_date_str.replace("Z", "+00:00"))
                        weekday = g_dt.weekday()
                        hour = g_dt.hour
                        if weekday == 3:
                            prime_tag = '<span class="badge badge-rookie">TNF</span>'
                        elif weekday == 0:
                            prime_tag = '<span class="badge badge-buy">MNF</span>'
                        elif weekday == 6 and hour >= 20:
                            prime_tag = '<span class="badge badge-prime">SNF</span>'
                    except Exception:
                        pass

                    if len(competitors) == 2:
                        team_a, team_b = competitors[0], competitors[1]
                        
                        name_a = team_a.get("team", {}).get("shortDisplayName", "Team A")
                        logo_a = team_a.get("team", {}).get("logo", "")
                        score_a = team_a.get("score", "0")
                        
                        name_b = team_b.get("team", {}).get("shortDisplayName", "Team B")
                        logo_b = team_b.get("team", {}).get("logo", "")
                        score_b = team_b.get("score", "0")
                        
                        status = comp.get("status", {}).get("type", {}).get("description", "Scheduled")
                        
                        st.markdown(f"""
                        <div class="lineup-row" style="padding: 12px 18px; margin-bottom: 8px;">
                            <div style="display: flex; align-items: center; gap: 12px; flex: 1;">
                                <img src="{logo_a}" width="28" height="28" style="object-fit: contain;" onerror="this.style.display='none'">
                                <div style="font-size: 14px; font-weight: 700; color: #f8fafc;">{name_a} <span style="color: #38bdf8; font-size: 15px; margin-left: 4px;">{score_a}</span></div>
                            </div>
                            <div style="text-align: center; flex: 0 0 100px;">
                                {prime_tag}
                                <div style="font-size: 11px; font-weight: 600; color: #64748b; margin-top: 2px;">{status}</div>
                            </div>
                            <div style="display: flex; align-items: center; gap: 12px; justify-content: flex-end; flex: 1;">
                                <div style="font-size: 14px; font-weight: 700; color: #f8fafc;"><span style="color: #38bdf8; font-size: 15px; margin-right: 4px;">{score_b}</span> {name_b}</div>
                                <img src="{logo_b}" width="28" height="28" style="object-fit: contain;" onerror="this.style.display='none'">
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
            else:
                st.info("NFL games for this week are currently between slates.")
        else:
            st.info("NFL scoreboard API currently unavailable.")
    except Exception:
        st.info("Unable to fetch live NFL scores at the moment.")

elif nav_selection == "🎲 Playoffs & Toilet Bowl":
    st.markdown("### 🏆 Championship Playoffs & 🚽 Toilet Bowl Race")
    standings_mode = st.radio("Standings View", ["Current Week Standings", "Projected Final Season Standings"], horizontal=True, key="std_mode")
    is_proj_mode = "Projected" in standings_mode
    active_standings_list = df_proj_calc.to_dict('records') if is_proj_mode else df_curr_calc.to_dict('records')
    
    for idx in range(min(8, len(active_standings_list))):
        row = active_standings_list[idx]
        st.markdown(f"""
        <div class="odds-row" style="padding: 10px 14px; margin-bottom: 6px;">
            <div style="font-size: 13px; font-weight: 700; color: #f8fafc;"><span style="color: #38bdf8; margin-right: 8px;">#{idx+1}</span> {row.get('team_name')}</div>
            <div style="font-size: 12px; font-weight: 800; color: #fbbf24;">{row.get('wins', 0)}W - {row.get('losses', 0)}L ({row.get('points_for', 0):.1f} PF)</div>
        </div>
        """, unsafe_allow_html=True)

elif nav_selection == "📜 Trades & Calculator":
    st.markdown("### ⚖️ Dynasty Trade Architect & Positional Shift Simulator")
    st.caption("Construct multi-asset trade proposals. Select players and draft picks independently to evaluate equity.")

    c_pod_a, c_pod_b = st.columns(2, gap="medium")
    with c_pod_a:
        st.markdown('<div style="font-size: 11px; font-weight: 800; color: #38bdf8; margin-bottom: 8px;">YOU SEND (OUTGOING ASSETS)</div>', unsafe_allow_html=True)
        ta = st.selectbox("Select Your Franchise", team_names, index=team_names.index(selected_team_name) if selected_team_name in team_names else 0, key="t_a", label_visibility="collapsed")
        r_a = next(r for r in rosters if roster_owner_map[r["roster_id"]] == ta)
        p_a = r_a.get("players", []) or []
        
        evaluated_players_a = sorted([(evaluate_player(p, all_players.get(p, {}))['value'], p, evaluate_player(p, all_players.get(p, {}))) for p in p_a], key=lambda x: x[0], reverse=True)
        player_options_a = {f"{p_obj['name']} ({p_obj['pos']} - {p_obj['team']}) • {p_obj['value']:,} pts": (p, val, p_obj) for val, p, p_obj in evaluated_players_a}
        sel_players_a = st.multiselect("Players You Send", list(player_options_a.keys()), key="sel_pl_a", placeholder="Search players to send...", label_visibility="collapsed")
        val_a = sum(player_options_a[item][1] for item in sel_players_a)
        st.markdown(f"**Total Outgoing Value:** `{val_a:,} pts`", unsafe_allow_html=True)

    with c_pod_b:
        st.markdown('<div style="font-size: 11px; font-weight: 800; color: #c084fc; margin-bottom: 8px;">YOU RECEIVE (INCOMING ASSETS)</div>', unsafe_allow_html=True)
        tb = st.selectbox("Select Trade Partner", [t for t in team_names if t != ta], index=0, key="t_b", label_visibility="collapsed")
        r_b = next(r for r in rosters if roster_owner_map[r["roster_id"]] == tb)
        p_b = r_b.get("players", []) or []
        
        evaluated_players_b = sorted([(evaluate_player(p, all_players.get(p, {}))['value'], p, evaluate_player(p, all_players.get(p, {}))) for p in p_b], key=lambda x: x[0], reverse=True)
        player_options_b = {f"{p_obj['name']} ({p_obj['pos']} - {p_obj['team']}) • {p_obj['value']:,} pts": (p, val, p_obj) for val, p, p_obj in evaluated_players_b}
        sel_players_b = st.multiselect("Players You Receive", list(player_options_b.keys()), key="sel_pl_b", placeholder="Search players to receive...", label_visibility="collapsed")
        val_b = sum(player_options_b[item][1] for item in sel_players_b)
        st.markdown(f"**Total Incoming Value:** `{val_b:,} pts`", unsafe_allow_html=True)
