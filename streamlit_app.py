import streamlit as st
import pandas as pd
import requests
import plotly.express as px

st.set_page_config(page_title="Dynasty League Hub & Analyzer", layout="wide", initial_sidebar_state="expanded")

BASE_URL = "https://api.sleeper.app/v1"

# ==================== CONFIGURATION ====================
# REPLACE THIS WITH YOUR 18-DIGIT SLEEPER LEAGUE ID:
DEFAULT_LEAGUE_ID = "1312141303219249152"
# =======================================================

@st.cache_data(ttl=3600)  # Cached for 1 hr (Sleeper player catalog is large)
def get_all_players():
    resp = requests.get(f"{BASE_URL}/players/nfl")
    return resp.json() if resp.status_code == 200 else {}

@st.cache_data(ttl=600)
def load_league_data(league_id: str):
    # 1. League Metadata
    league_info = requests.get(f"{BASE_URL}/league/{league_id}").json()
    if not league_info:
        return None, None, None, None, None, None

    users = requests.get(f"{BASE_URL}/league/{league_id}/users").json()
    rosters = requests.get(f"{BASE_URL}/league/{league_id}/rosters").json()
    traded_picks = requests.get(f"{BASE_URL}/league/{league_id}/traded_picks").json()

    user_map = {
        u["user_id"]: u.get("metadata", {}).get("team_name") or u.get("display_name", f"User {u['user_id']}")
        for u in users
    }
    roster_owner_map = {
        r["roster_id"]: user_map.get(r["owner_id"], f"Roster {r['roster_id']}")
        for r in rosters
    }

    # 2. Weekly Matchup History
    state = requests.get(f"{BASE_URL}/state/nfl").json()
    current_week = state.get("week", 1)
    
    matchup_records = []
    max_weeks = min(current_week, 18)
    for w in range(1, max_weeks + 1):
        resp = requests.get(f"{BASE_URL}/league/{league_id}/matchups/{w}")
        if resp.status_code == 200 and resp.json():
            for m in resp.json():
                matchup_records.append({
                    "week": w,
                    "roster_id": m["roster_id"],
                    "team_name": roster_owner_map.get(m["roster_id"], f"Team {m['roster_id']}"),
                    "matchup_id": m["matchup_id"],
                    "points": m["points"],
                    "starters": m.get("starters", []),
                    "players_points": m.get("players_points", {})
                })

    df_matchups = pd.DataFrame(matchup_records)
    return league_info, users, rosters, traded_picks, df_matchups, roster_owner_map

# Run Data Fetch
with st.spinner("Connecting to Sleeper & Crunching Dynasty Numbers..."):
    all_players_data = get_all_players()
    league_info, users, rosters, traded_picks, df_matchups, roster_owner_map = load_league_data(DEFAULT_LEAGUE_ID)

if not league_info:
    st.error("⚠️ Failed to load league. Please check that DEFAULT_LEAGUE_ID in streamlit_app.py matches your Sleeper League ID.")
    st.stop()

# Helper: Approximate Dynasty Asset Value for 8-Team 2TE + TEP + IDP
def calculate_asset_value(player_id, p_data):
    if not p_data:
        return 5
    pos = p_data.get("position", "N/A")
    age = p_data.get("age", 25)
    exp = p_data.get("years_exp", 3)

    # Base values reflecting 8-team format where studs dictate championships
    base_val = 30
    if pos == "QB":
        base_val = 45 if age < 28 else 30  # 1QB lowers baseline QB value
    elif pos == "WR":
        base_val = 60 if age < 27 else 40
    elif pos == "RB":
        base_val = 55 if age < 26 else 30
    elif pos == "TE":
        base_val = 65 if age < 28 else 45  # Boosted for 2TE + 0.25 TEP
    elif pos in ["DL", "DE", "DT"]:
        base_val = 35 if age < 27 else 20  # Boosted for high sack/TFL scoring
    elif pos in ["LB", "CB", "S", "DB"]:
        base_val = 25

    # Age Curve adjustment
    age_multiplier = 1.0
    if age:
        if age <= 23:
            age_multiplier = 1.3
        elif age <= 26:
            age_multiplier = 1.15
        elif age >= 29:
            age_multiplier = 0.75
        elif age >= 31:
            age_multiplier = 0.5

    return int(base_val * age_multiplier)

# ----------------- TABS NAVIGATION -----------------
st.title(f"🏆 {league_info.get('name', 'Dynasty Hub')}")
st.caption("Custom 8-Team Dynasty | 1QB • 2TE (+0.25 TEP) • 4 Flex • Big Play IDP")

tab1, tab2, tab3, tab4 = st.tabs([
    "📊 Standings & Luck", 
    "🧭 Contend vs Rebuild", 
    "⚖️ Dynasty Trade Machine", 
    "💡 Strategy Recommendations"
])

# ==================== TAB 1: STANDINGS & LUCK ====================
with tab1:
    if df_matchups.empty:
        st.info("No matchups completed yet this season. Check back after Week 1!")
    else:
        # H2H calculations
        h2h_results = []
        for (w, mid), group in df_matchups.groupby(["week", "matchup_id"]):
            if len(group) == 2:
                t1, t2 = group.iloc[0], group.iloc[1]
                h2h_results.append((w, t1["roster_id"], int(t1["points"] > t2["points"])))
                h2h_results.append((w, t2["roster_id"], int(t2["points"] > t1["points"])))

        h2h_df = pd.DataFrame(h2h_results, columns=["week", "roster_id", "h2h_win"])
        df_merged = df_matchups.merge(h2h_df, on=["week", "roster_id"], how="left").fillna({"h2h_win": 0})

        # All-Play Calculation
        def calc_all_play(w_df):
            pts = w_df["points"].values
            w_df["ap_wins"] = w_df["points"].apply(lambda p: (p > pts).sum())
            w_df["ap_losses"] = w_df["points"].apply(lambda p: (p < pts).sum())
            return w_df

        df_merged = df_merged.groupby("week", group_keys=False).apply(calc_all_play)

        summary = df_merged.groupby("team_name").agg(
            Points_For=("points", "sum"),
            H2H_Wins=("h2h_win", "sum"),
            AP_Wins=("ap_wins", "sum"),
            AP_Losses=("ap_losses", "sum")
        ).reset_index()

        total_ap = summary["AP_Wins"] + summary["AP_Losses"]
        summary["All_Play_Pct"] = (summary["AP_Wins"] / total_ap).fillna(0)
        summary["Expected_Wins"] = summary["All_Play_Pct"] * len(df_merged["week"].unique())
        summary["Luck_Factor"] = summary["H2H_Wins"] - summary["Expected_Wins"]
        summary = summary.sort_values(by="Points_For", ascending=False)

        col1, col2 = st.columns([3, 2])
        with col1:
            st.subheader("Performance & Luck Table")
            st.dataframe(
                summary.style.format({
                    "Points_For": "{:.1f}",
                    "H2H_Wins": "{:.0f}",
                    "AP_Wins": "{:.0f}",
                    "AP_Losses": "{:.0f}",
                    "All_Play_Pct": "{:.3f}",
                    "Expected_Wins": "{:.2f}",
                    "Luck_Factor": "{:+.2f}"
                }),
                use_container_width=True
            )

        with col2:
            st.subheader("Expected vs Actual Wins")
            fig = px.scatter(
                summary, x="Expected_Wins", y="H2H_Wins", text="team_name",
                color="Luck_Factor", color_continuous_scale="RdYlGn",
                labels={"Expected_Wins": "Expected Wins (All-Play)", "H2H_Wins": "Actual Wins"}
            )
            fig.update_traces(textposition="top center")
            st.plotly_chart(fig, use_container_width=True)

# ==================== TAB 2: CONTEND VS REBUILD ====================
with tab2:
    st.subheader("Roster Trajectory Index")
    st.write("Diagnoses whether your team should **Push All-In (Contend)**, **Retool (Youth Shift)**, or **Full Rebuild** based on starting strength and age curve.")

    team_diagnostics = []
    for r in rosters:
        rid = r["roster_id"]
        t_name = roster_owner_map.get(rid, f"Team {rid}")
        players = r.get("players", []) or []
        starters = set(r.get("starters", []) or [])
        taxi = set(r.get("taxi", []) or [])

        ages = []
        starter_points_potential = 0
        total_team_value = 0

        for pid in players:
            p_info = all_players_data.get(pid, {})
            age = p_info.get("age")
            if age:
                ages.append(age)
            val = calculate_asset_value(pid, p_info)
            total_team_value += val

        avg_age = sum(ages) / len(ages) if ages else 26.0

        # Points for
        pts = r.get("settings", {}).get("fpts", 0) + (r.get("settings", {}).get("fpts_decimal", 0) / 100)
        wins = r.get("settings", {}).get("wins", 0)

        # Pick count (baseline is 3 rounds x 3 years = 9 picks)
        team_picks_owned = 9
        for p in traded_picks:
            if p["owner_id"] == rid and p["roster_id"] != rid:
                team_picks_owned += 1
            elif p["roster_id"] == rid and p["owner_id"] != rid:
                team_picks_owned -= 1

        # Classification Logic
        # In 8-team leagues, high points + top tier value = strong contender
        if pts > 250 and avg_age >= 26.5:
            status = "🔥 Strong Contender (Win-Now)"
            badge_color = "red"
        elif pts > 220 and avg_age < 26.0:
            status = "🚀 Young Powerhouse (Dynasty Sweet Spot)"
            badge_color = "green"
        elif avg_age > 27.0 and pts < 220:
            status = "⚠️ Danger Zone: Ageing / Must Retool"
            badge_color = "orange"
        else:
            status = "🏗️ Productive Rebuild"
            badge_color = "blue"

        team_diagnostics.append({
            "Team": t_name,
            "Status": status,
            "Points For": pts,
            "Avg Player Age": round(avg_age, 1),
            "Roster Asset Score": total_team_value,
            "Est. Picks Owned (27-29)": team_picks_owned
        })

    diag_df = pd.DataFrame(team_diagnostics).sort_values(by="Points For", ascending=False)
    st.dataframe(diag_df, use_container_width=True)

# ==================== TAB 3: DYNASTY TRADE MACHINE ====================
with tab3:
    st.subheader("8-Team Dynasty Trade Evaluator")
    st.write("Balances your 2TE, TEP, and Big-Play IDP scoring premiums alongside draft capital across 2027–2029.")

    teams_list = list(roster_owner_map.values())
    c1, c2 = st.columns(2)

    with c1:
        team_a_name = st.selectbox("Select Team A", teams_list, index=0)
        team_a_id = [k for k, v in roster_owner_map.items() if v == team_a_name][0]
        team_a_roster = next(r for r in rosters if r["roster_id"] == team_a_id)
        team_a_player_ids = team_a_roster.get("players", []) or []

        player_options_a = {
            f"{all_players_data.get(pid, {}).get('full_name', pid)} ({all_players_data.get(pid, {}).get('position', 'N/A')})": pid
            for pid in team_a_player_ids
        }
        selected_players_a = st.multiselect(f"Players from {team_a_name}", list(player_options_a.keys()))
        selected_picks_a = st.multiselect(
            f"Draft Picks from {team_a_name}",
            [f"{yr} Round {rd}" for yr in [2027, 2028, 2029] for rd in [1, 2, 3]],
            key="picks_a"
        )

    with c2:
        team_b_name = st.selectbox("Select Team B", teams_list, index=1 if len(teams_list) > 1 else 0)
        team_b_id = [k for k, v in roster_owner_map.items() if v == team_b_name][0]
        team_b_roster = next(r for r in rosters if r["roster_id"] == team_b_id)
        team_b_player_ids = team_b_roster.get("players", []) or []

        player_options_b = {
            f"{all_players_data.get(pid, {}).get('full_name', pid)} ({all_players_data.get(pid, {}).get('position', 'N/A')})": pid
            for pid in team_b_player_ids
        }
        selected_players_b = st.multiselect(f"Players from {team_b_name}", list(player_options_b.keys()))
        selected_picks_b = st.multiselect(
            f"Draft Picks from {team_b_name}",
            [f"{yr} Round {rd}" for yr in [2027, 2028, 2029] for rd in [1, 2, 3]],
            key="picks_b"
        )

    # Pick Values in 8-team (Round 1 pick = top 8 player)
    pick_values = {"Round 1": 65, "Round 2": 35, "Round 3": 18}

    val_a = sum([calculate_asset_value(player_options_a[p], all_players_data.get(player_options_a[p], {})) for p in selected_players_a])
    for pk in selected_picks_a:
        rd = "Round " + pk.split("Round ")[1]
        val_a += pick_values.get(rd, 20)

    val_b = sum([calculate_asset_value(player_options_b[p], all_players_data.get(player_options_b[p], {})) for p in selected_players_b])
    for pk in selected_picks_b:
        rd = "Round " + pk.split("Round ")[1]
        val_b += pick_values.get(rd, 20)

    st.markdown("---")
    res1, res2, res3 = st.columns(3)
    res1.metric(f"{team_a_name} Gives Up", f"{val_a} pts")
    res2.metric(f"{team_b_name} Gives Up", f"{val_b} pts")
    diff = val_a - val_b
    res3.metric("Net Advantage", f"{abs(diff)} pts", f"{'Favors ' + team_a_name if diff < 0 else 'Favors ' + team_b_name}")

    if val_a > 0 or val_b > 0:
        total = max(val_a, val_b)
        margin = abs(diff) / (total if total > 0 else 1)
        if margin <= 0.12:
            st.success("✅ **Fair Trade:** Values are within a balanced margin for an 8-team dynasty setup.")
        elif margin <= 0.25:
            st.warning("⚖️ **Slightly Unbalanced:** Consider throwing in a 2027/2028 2nd or 3rd rounder to even it out.")
        else:
            st.error("🚨 **Heavily Lopsided:** One manager is giving up substantially more long-term/immediate value.")

# ==================== TAB 4: STRATEGY & TARGETS ====================
with tab4:
    st.subheader("Tactical Recommendations for Your Roster")
    my_team = st.selectbox("Select Your Team", teams_list)
    my_row = diag_df[diag_df["Team"] == my_team].iloc[0]

    st.write(f"### Current Roster Classification: **{my_row['Status']}**")

    rec1, rec2 = st.columns(2)

    with rec1:
        st.markdown("#### 🎯 Strategic Action Plan")
        if "Contender" in my_row["Status"]:
            st.write("""
            * **Consolidate Bench Depth into Elite Studs:** In an 8-team league with 4 flex spots, bench depth is plentiful across waivers. You win by having top-3 positional dominators.
            * **Exploit 2TE & TEP Scarcity:** Look for contending TE upgrades. With 16 required TE starters across the league and 0.25 TEP, high-target TEs score like top WR1s.
            * **Trade Future Picks for Impact IDPs:** Top edge rushers with high sack/TFL rates score massive weekly bursts. If a rebuilder owns an elite DL, cash in your 2028/2029 2nds for them.
            """)
        elif "Danger Zone" in my_row["Status"] or "Rebuild" in my_row["Status"]:
            st.write("""
            * **Strip Veteran RBs:** Running back value falls off rapidly past age 26. Trade veteran RBs now to contenders for 2027 and 2028 1st-round capital.
            * **Corner the 2027/2028 Draft Market:** In an 8-team league, a 1st round pick is guaranteed to be a top-8 incoming rookie. Stockpile multiple 1sts.
            * **Taxi Stash Exploitation:** Maximize your 4 taxi spots with upside WRs and developmental TEs. Because taxi spots lock, let them sit and accrue value tax-free.
            """)
        else:
            st.write("""
            * **Maintain Flexibility:** You have youth and scoring power. Avoid trading away top young starters unless you get a definitive top-5 overall asset.
            * **Target IDP Value Inefficiencies:** Leaguemates often undervalue IDP players compared to offensive players. Exploit this by packaging spare flex depth for elite sack producers.
            """)

    with rec2:
        st.markdown("#### 🔄 Recommended Trade Partners")
        st.write("Based on opposing team trajectories across the league:")
        for _, row in diag_df.iterrows():
            if row["Team"] != my_team:
                if "Contender" in my_row["Status"] and ("Rebuild" in row["Status"] or "Retool" in row["Status"]):
                    st.info(f"💡 **Target {row['Team']}**: They are retooling/rebuilding. Offer them your future 2027–2029 draft picks in exchange for their top win-now starters.")
                elif "Rebuild" in my_row["Status"] and "Contender" in row["Status"]:
                    st.success(f"💡 **Sell to {row['Team']}**: They are in win-now mode. Send them your veterans in exchange for their 2027, 2028, or 2029 1st-round picks.")
