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
        return {"value": 100, "name": f"Player {pid}", "team": "FA", "pos": "FLEX", "age": 25, "img": f"https://sleepercdn.com/content/nfl/players/{pid}.jpg"}
    pos = p_info.get("position", "N/A")
    age = p_info.get("age") or 25
    team = p_info.get("team") or "FA"
    search_rank = p_info.get("search_rank")
    dynasty_val = max(100, int(1000 - (search_rank if search_rank else 200) * 1.5))
    p_stat = weekly_stats.get(str(pid), {})
    pts = float(p_stat.get("pts_half_ppr", 0.0) or p_stat.get("pts_ppr", 0.0) or 0.0)
    return {
        "value": dynasty_val, "name": p_info.get('full_name') or f"Player {pid}",
        "team": team, "pos": pos, "age": age, "img": f"https://sleepercdn.com/content/nfl/players/{pid}.jpg"
    }

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

# ==================== NAVIGATION VIEWS ====================
if nav_selection == "👤 Roster & Insights":
    st.markdown("### 👤 Franchise Roster Overview")
    for pid in (selected_roster.get("players", []) or [])[:12]:
        p = evaluate_player(pid, all_players.get(pid, {}))
        st.markdown(f'<div class="lineup-row"><div><strong>{p["name"]}</strong> ({p["pos"]} - {p["team"]})</div><div style="color: #38bdf8;">{p["value"]:,} pts</div></div>', unsafe_allow_html=True)

elif nav_selection == "📈 Overall Dynasty Rankings":
    st.markdown("### 📈 Overall Dynasty Player Rankings (1QB Format)")
    pool = [evaluate_player(pid, info) for pid, info in list(all_players.items())[:50]]
    for rank, p in enumerate(sorted(pool, key=lambda x: x["value"], reverse=True), 1):
        st.markdown(f'<div class="lineup-row"><div><strong>#{rank}</strong> {p["name"]} ({p["pos"]} - {p["team"]})</div><div style="color: #38bdf8;">{p["value"]:,} pts</div></div>', unsafe_allow_html=True)

elif nav_selection == "🔍 Deep Dive":
    st.markdown("### 🔍 Franchise Deep Dive & Positional Matrix")
    st.info("Comprehensive positional breakdown and roster valuation metrics.")

elif nav_selection == "⚔️ Fantasy Matchups":
    st.markdown("### ⚔️ Live Fantasy Matchups (Week 3)")
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
    st.info("Playoff bracket and draft pick projections.")

elif nav_selection == "📜 Trades & Calculator":
    st.markdown("### ⚖️ Dynasty Trade Architect")
    st.info("Trade calculator tools.")
