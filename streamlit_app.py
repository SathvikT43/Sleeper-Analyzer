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

user_map = {u["user_id"]: u.get("metadata", {}).get("team_name") or u.get("display_name", f"User {u['user_id']}") for u in users}
roster_owner_map = {r["roster_id"]: user_map.get(r["owner_id"], f"Team {r['roster_id']}") for r in rosters}

player_owner_map = {}
all_rostered_players = set()
for r in rosters:
    owner_name = roster_owner_map.get(r["roster_id"], f"Team {r['roster_id']}")
    for pid in (r.get("players", []) or []):
        player_owner_map[pid] = owner_name
        all_rostered_players.add(pid)

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
    search_rank = p_info.get("search_rank")

    p_stat = weekly_stats.get(str(pid), {})
    pts = float(p_stat.get("pts_half_ppr", 0.0) or p_stat.get("pts_ppr", 0.0) or 0.0)

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

# ==================== DRAFT PICK INVENTORY ====================
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

# ==================== LEAGUE-WIDE AGGREGATION ====================
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

    fpts = r.get("settings", {}).get("fpts", 0) + (r.get("settings", {}).get("fpts_decimal", 0) / 100)
    ppts = r.get("settings", {}).get("ppts", 0) or fpts
    eff_pct = (fpts / ppts * 100) if ppts > 0 else 0.0
    wins = r.get("settings", {}).get("wins", 0)
    losses = r.get("settings", {}).get("losses", 0)
    fpts_against = r.get("settings", {}).get("fpts_against", 0) + (r.get("settings", {}).get("fpts_against_decimal", 0) / 100)

    league_stats.append({
        "roster_id": rid, "team_name": tname, "player_value": player_val, "pick_value": pick_val,
        "total_value": total_dynasty_val, "avg_age": t_age, "points_for": fpts, "points_against": fpts_against,
        "max_pf": ppts, "efficiency": eff_pct, "wins": wins, "losses": losses
    })

df_league = pd.DataFrame(league_stats)
df_curr_calc = df_league.sort_values(by=["wins", "points_for"], ascending=[False, False]).reset_index(drop=True)
curr_seed_dict = {row["roster_id"]: idx + 1 for idx, row in df_curr_calc.iterrows()}
df_league["seed"] = df_league["roster_id"].map(curr_seed_dict)

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

pool = []
for pid in all_rostered_players:
    pool.append(evaluate_player(pid, all_players.get(pid, {})))
df_all_ranked = pd.DataFrame(pool)

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

# ==================== NAVIGATION VIEWS ====================
if nav_selection == "👤 Roster & Insights":
    m1, m2, m3, m4 = st.columns(4)
    m1.markdown(f'<div class="metric-card"><div style="color: #94a3b8; font-size: 11px; font-weight: 700;">TOTAL FRANCHISE VALUE</div><div style="font-size: 24px; font-weight: 800; color: #38bdf8; margin: 2px 0;">{my_row["total_value"]:,} pts</div></div>', unsafe_allow_html=True)
    m2.markdown(f'<div class="metric-card"><div style="color: #94a3b8; font-size: 11px; font-weight: 700;">ROSTER AVG AGE</div><div style="font-size: 24px; font-weight: 800; color: #f8fafc; margin: 2px 0;">{my_row["avg_age"]:.1f} yrs</div></div>', unsafe_allow_html=True)
    m3.markdown(f'<div class="metric-card"><div style="color: #94a3b8; font-size: 11px; font-weight: 700;">START EFFICIENCY</div><div style="font-size: 24px; font-weight: 800; color: #fbbf24; margin: 2px 0;">{my_row["efficiency"]:.1f}%</div></div>', unsafe_allow_html=True)
    m4.markdown(f'<div class="metric-card"><div style="color: #94a3b8; font-size: 11px; font-weight: 700;">RECORD & STANDINGS</div><div style="font-size: 24px; font-weight: 800; color: #f43f5e; margin: 2px 0;">{my_row["wins"]}W - {my_row["losses"]}L</div></div>', unsafe_allow_html=True)

    st.markdown('<div class="section-header">⚡ Starters</div>', unsafe_allow_html=True)
    for pid in (selected_roster.get("starters", []) or []):
        p = evaluate_player(pid, all_players.get(pid, {}))
        st.markdown(f'<div class="lineup-row"><div><strong>{p["name"]}</strong> ({p["pos"]} - {p["team"]})</div><div style="color: #38bdf8; font-weight: 800;">{p["value"]:,} pts</div></div>', unsafe_allow_html=True)

elif nav_selection == "📈 Overall Dynasty Rankings":
    st.markdown("### 📈 Overall Dynasty Player Rankings (1QB Format)")
    for rank, p in df_all_ranked.sort_values(by="value", ascending=False).head(50).reset_index(drop=True).iterrows():
        st.markdown(f'<div class="lineup-row"><div><strong>#{rank+1}</strong> {p["name"]} ({p["pos"]} - {p["team"]})</div><div style="color: #38bdf8; font-weight: 800;">{p["value"]:,} pts</div></div>', unsafe_allow_html=True)

elif nav_selection == "🔍 Deep Dive":
    st.markdown(f"### 🔍 Deep Dive: {selected_team_name}")
    st.caption("Positional power matrix and franchise intelligence.")

elif nav_selection == "⚔️ Fantasy Matchups":
    st.markdown("### ⚔️ Live Fantasy Matchups & Scoreboard (Week 3)")
    for m in matchups:
        t_name = roster_owner_map.get(m.get("roster_id"), "Team")
        t_pts = float(m.get("points", 0.0) or 0.0)
        st.markdown(f'<div class="insight-card"><strong>{t_name}</strong> ➔ {t_pts:.2f} pts</div>', unsafe_allow_html=True)

elif nav_selection == "🏈 NFL Schedule & Scores":
    st.markdown("### 🏈 Real-Time NFL Game Center & Scores (Week 3)")
    st.caption("Official ESPN Week 3 Matchups, Away @ Home formats, Kickoff times, and Prime-Time Badges.")
    
    try:
        nfl_games_resp = requests.get("https://site.api.espn.com/apis/site/v2/sports/football/nfl/scoreboard?dates=2026&seasontype=2&week=3", timeout=6)
        if nfl_games_resp.status_code == 200:
            events = nfl_games_resp.json().get("events", [])
            if events:
                for ev in events:
                    comp = ev.get("competitions", [{}])[0]
                    competitors = comp.get("competitors", [])
                    game_date_str = ev.get("date", "")
                    notes = comp.get("notes", [])
                    
                    prime_tag = ""
                    note_text = notes[0].get("headline", "").lower() if notes else ""
                    
                    try:
                        g_dt = datetime.fromisoformat(game_date_str.replace("Z", "+00:00"))
                        time_formatted = g_dt.strftime("%a, %b %d • %I:%M %p")
                        
                        if "thursday" in note_text or g_dt.weekday() == 3:
                            prime_tag = '<span style="background: rgba(0, 168, 225, 0.2); color: #00a8e1; border: 1px solid rgba(0, 168, 225, 0.4); padding: 3px 8px; border-radius: 6px; font-size: 10px; font-weight: 800;">TNF • PRIME VIDEO</span>'
                        elif "monday" in note_text or g_dt.weekday() == 0:
                            prime_tag = '<span style="background: rgba(226, 24, 59, 0.2); color: #ff4d6d; border: 1px solid rgba(226, 24, 59, 0.4); padding: 3px 8px; border-radius: 6px; font-size: 10px; font-weight: 800;">MNF • ESPN</span>'
                        elif "sunday" in note_text or (g_dt.weekday() == 6 and g_dt.hour >= 20):
                            prime_tag = '<span style="background: rgba(251, 191, 36, 0.2); color: #fbbf24; border: 1px solid rgba(251, 191, 36, 0.4); padding: 3px 8px; border-radius: 6px; font-size: 10px; font-weight: 800;">SNF • NBC</span>'
                        else:
                            prime_tag = f'<span style="color: #64748b; font-size: 11px; font-weight: 600;">{time_formatted}</span>'
                    except Exception:
                        prime_tag = '<span style="color: #64748b; font-size: 11px;">Scheduled</span>'

                    if len(competitors) == 2:
                        home_team = next((c for c in competitors if c.get("homeAway") == "home"), competitors[0])
                        away_team = next((c for c in competitors if c.get("homeAway") == "away"), competitors[1])
                        
                        away_name = away_team.get("team", {}).get("shortDisplayName", "Away")
                        away_logo = away_team.get("team", {}).get("logo", "")
                        away_score = away_team.get("score", "0")
                        
                        home_name = home_team.get("team", {}).get("shortDisplayName", "Home")
                        home_logo = home_team.get("team", {}).get("logo", "")
                        home_score = home_team.get("score", "0")
                        
                        status = comp.get("status", {}).get("type", {}).get("description", "Scheduled")
                        matchup_string = f"{away_name} @ {home_name}"
                        
                        card_html = (
                            f'<div class="lineup-row" style="padding: 14px 18px; margin-bottom: 10px;">'
                            f'  <div style="display: flex; align-items: center; gap: 12px; flex: 1;">'
                            f'      <img src="{away_logo}" width="30" height="30" style="object-fit: contain;" onerror="this.style.display=\'none\'">'
                            f'      <div style="font-size: 14px; font-weight: 700; color: #f8fafc;">{away_name} <span style="color: #38bdf8; font-size: 16px; margin-left: 6px;">{away_score}</span></div>'
                            f'  </div>'
                            f'  <div style="text-align: center; flex: 0 0 180px;">'
                            f'      {prime_tag}'
                            f'      <div style="font-size: 10px; font-weight: 600; color: #94a3b8; margin-top: 3px;">{matchup_string}</div>'
                            f'      <div style="font-size: 10px; font-weight: 500; color: #64748b;">{status}</div>'
                            f'  </div>'
                            f'  <div style="display: flex; align-items: center; gap: 12px; justify-content: flex-end; flex: 1;">'
                            f'      <div style="font-size: 14px; font-weight: 700; color: #f8fafc;"><span style="color: #38bdf8; font-size: 16px; margin-right: 6px;">{home_score}</span> {home_name}</div>'
                            f'      <img src="{home_logo}" width="30" height="30" style="object-fit: contain;" onerror="this.style.display=\'none\'">'
                            f'  </div>'
                            f'</div>'
                        )
                        st.markdown(card_html, unsafe_allow_html=True)
            else:
                st.info("No NFL fixtures returned for Week 3.")
        else:
            st.info("NFL scoreboard API currently unavailable.")
    except Exception:
        st.info("Unable to fetch live NFL scores at the moment.")

elif nav_selection == "🎲 Playoffs & Toilet Bowl":
    st.markdown("### 🏆 Championship Playoffs & 🚽 Toilet Bowl Race")
    for idx, row in df_league.iterrows():
        st.markdown(f'<div class="odds-row"><strong>#{idx+1} {row["team_name"]}</strong> ({row["wins"]}W-{row["losses"]}L)</div>', unsafe_allow_html=True)

elif nav_selection == "📜 Trades & Calculator":
    st.markdown("### ⚖️ Dynasty Trade Architect")
    st.info("Select players and draft picks to simulate trade equity.")
