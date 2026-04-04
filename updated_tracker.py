import streamlit as st
import pandas as pd
import os

# -----------------------------
# Page Configuration
# -----------------------------
st.set_page_config(page_title="Gaming Tracker Pro", layout="wide")

# 🎨 Global & Combined Styling
st.markdown("""
<style>
    /* Base styling */
    .stApp { background: #121212; color: #e0e0e0; }
    
    /* Card component (Used in both Poker and Blackjack) */
    .card { 
        background-color: #1e1e1e; 
        padding: 15px; border-radius: 12px; margin-bottom: 10px; 
        border: 1px solid #333; box-shadow: 0 4px 6px rgba(0,0,0,0.3);
    }
    
    /* Blackjack specific card style modifier */
    .bj-card {
        padding: 20px; border-radius: 15px; margin-bottom: 15px; 
        border-left: 5px solid #d4af37; box-shadow: 0 4px 15px rgba(0,0,0,0.5);
    }
    
    .stMetric { background: #222; padding: 10px; border-radius: 8px; }
    .net-pos { color: #00ffcc; font-weight: bold; }
    .net-neg { color: #ff4b4b; font-weight: bold; }
    .side-bet { color: #bb86fc; font-size: 0.9em; font-style: italic; }
</style>
""", unsafe_allow_html=True)

# -----------------------------
# Session State Initialization
# -----------------------------
if "app_mode" not in st.session_state:
    st.session_state.app_mode = "🃏 Poker"

cb_keys = {
    "cb_players": {}, "cb_scores": {}, "cb_history": [], 
    "cb_matches": [], "cb_confirmed": False, "cb_reset_inputs": True,
    "cb_edit_target": None
}
pk_keys = {
    "pk_players": {}, "pk_total_buyin": {}, "pk_history": [], 
    "pk_matches": [], "pk_buyin_confirmed": False, "pk_reset_bets": True, 
    "pk_reset_winners": False, "pk_dealer_idx": 0, "pk_edit_target": None
}
bj_keys = {
    "bj_players": {}, "bj_total_buyin": {}, "bj_history": [],
    "bj_matches": [], "bj_confirmed": False, "bj_edit_target": None
}

for d in [cb_keys, pk_keys, bj_keys]:
    for key, default in d.items():
        if key not in st.session_state:
            st.session_state[key] = default

# -----------------------------
# Sidebar Navigation & History
# -----------------------------
with st.sidebar:
    st.title("🕹️ Game Selector")
    st.radio("Choose Game:", ["🃏 Poker", "🎯 Callbreak", "♠️ Blackjack"], key="app_mode_select")
    st.session_state.app_mode = st.session_state.app_mode_select
    st.markdown("---")
    
    if st.session_state.app_mode == "🎯 Callbreak":
        st.subheader("📊 Callbreak History")
        if st.session_state.cb_matches:
            st.write("**🏆 Past Matches**")
            for i, m in enumerate(st.session_state.cb_matches):
                with st.expander(f"Match {i+1}"):
                    st.table(pd.Series(m["scores"]))
        if st.session_state.cb_history:
            st.write("**🕒 Round History**")
            st.dataframe(pd.DataFrame(st.session_state.cb_history), use_container_width=True)
            
    elif st.session_state.app_mode == "🃏 Poker":
        st.subheader("📊 Poker History")
        if st.session_state.pk_matches:
            st.write("**🏆 Past Matches**")
            for i, m in enumerate(st.session_state.pk_matches):
                with st.expander(f"Match {i+1}"):
                    st.table(pd.Series(m["players"]))
        if st.session_state.pk_history:
            st.write("**🕒 Round History**")
            h_rows = []
            for i, h in enumerate(reversed(st.session_state.pk_history)):
                row = {
                    "R": len(st.session_state.pk_history)-i, 
                    "Win": ", ".join(h["winners"]), 
                    "Pot": h["pot"]
                }
                # Show sidepot flag if there were sidepots
                if h.get("side_pots", 0) > 0:
                    row["Info"] = f"{h['side_pots']} SP"
                else:
                    row["Info"] = ""
                h_rows.append(row)
            st.dataframe(pd.DataFrame(h_rows), use_container_width=True)
            
    else:
        st.subheader("📊 Blackjack History")
        if st.session_state.bj_matches:
            for i, m in enumerate(reversed(st.session_state.bj_matches)):
                with st.expander(f"Match {len(st.session_state.bj_matches)-i}"):
                    st.table(pd.Series(m["players"], name="Final Chips"))
        else:
            st.info("No matches stored.")

# =============================================================================
# 🎯 CALLBREAK APP LOGIC
# =============================================================================

if st.session_state.app_mode == "🎯 Callbreak":
    # Deep Blue Gradient for Callbreak
    st.markdown('<style>.stApp { background: radial-gradient(circle at center, #1e3a8a, #0f172a); }</style>', unsafe_allow_html=True)
    st.title("🎯 Callbreak Tracker")
    
    
    if not st.session_state.cb_confirmed:
        # --- PLAYER SETUP ---
        with st.form("cb_add_form", clear_on_submit=True):
            cb_n = st.text_input("Enter Player Name")
            if st.form_submit_button("Add Player"):
                if cb_n and cb_n not in st.session_state.cb_players:
                    st.session_state.cb_players[cb_n] = 0.0
                    st.rerun()

        if st.session_state.cb_players:
            st.write("Manage Players:")
            for p in list(st.session_state.cb_players.keys()):
                c1, c2, c3 = st.columns([3, 1, 1])
                if st.session_state.cb_edit_target == p:
                    new_n = c1.text_input("Edit Name", p, key=f"edit_cb_{p}")
                    if c2.button("Save", key=f"save_cb_{p}"):
                        st.session_state.cb_players[new_n] = st.session_state.cb_players.pop(p)
                        st.session_state.cb_edit_target = None
                        st.rerun()
                else:
                    c1.write(f"👤 {p}")
                    if c2.button("✏️", key=f"btn_edit_cb_{p}"):
                        st.session_state.cb_edit_target = p
                        st.rerun()
                    if c3.button("🗑️", key=f"del_cb_{p}"):
                        del st.session_state.cb_players[p]
                        st.rerun()

            if len(st.session_state.cb_players) >= 2:
                if st.button("✅ Start Match", type="primary"):
                    st.session_state.cb_confirmed = True
                    st.rerun()

    else:
        # --- GAMEPLAY UI ---
        t_col1, t_col2 = st.columns([3, 1])
        with t_col1:
            st.info(f"Round {len(st.session_state.cb_history) + 1} | Scoring: Call 10 & 3+ Penalty active.")
        with t_col2:
            if st.button("🏁 Finish Match", use_container_width=True):
                st.session_state.cb_matches.append({"scores": st.session_state.cb_players.copy()})
                st.session_state.cb_players = {}; st.session_state.cb_history = []; st.session_state.cb_confirmed = False
                st.rerun()

        # Score Metrics
        score_cols = st.columns(len(st.session_state.cb_players))
        for i, (p, score) in enumerate(st.session_state.cb_players.items()):
            score_cols[i].metric(p, f"{score:.1f}")

        st.subheader("🎲 Current Round Entry")
        if st.session_state.cb_reset_inputs:
            for p in st.session_state.cb_players:
                st.session_state[f"call_{p}"] = 1
                st.session_state[f"got_{p}"] = 0
            st.session_state.cb_reset_inputs = False

        calls, gots = {}, {}
        for p in st.session_state.cb_players:
            st.markdown(f"**{p}**")
            c1, c2 = st.columns(2)
            calls[p] = c1.number_input("Call", 1, 13, key=f"call_{p}")
            gots[p] = c2.number_input("Tricks Won", 0, 13, key=f"got_{p}")

        if st.button("▶ Submit Round", type="primary"):
            round_scores = {"Round": len(st.session_state.cb_history) + 1}
            
            # 🔥 Check if anyone called 10+
            call_10_players = [p for p in st.session_state.cb_players if calls[p] >= 10]

            for p in st.session_state.cb_players:
                call = calls[p]
                got = gots[p]

                # 🚨 CASE: Call 10 rule active (High-stakes round)
                if call_10_players:
                    if p in call_10_players:
                        if got < call:
                            score = -float(call)
                        else:
                            extra = got - call
                            score = float(call) + (0.1 * extra)
                    else:
                        # Others just get what they won (no penalty/no negative for missing call)
                        score = float(got)
                
                # 🧠 NORMAL RULE
                else:
                    if got < call:
                        score = -float(call)
                    else:
                        extra = got - call
                        # Apply penalty for 3+ extra tricks
                        if extra >= 3:
                            score = (float(call) + (0.1 * extra)) - 2.0
                        else:
                            score = float(call) + (0.1 * extra)

                # Update balance and round data
                st.session_state.cb_players[p] = round(st.session_state.cb_players[p] + score, 1)
                round_scores[p] = round(score, 1)

            # Save history and reset
            st.session_state.cb_history.append(round_scores)
            st.session_state.cb_reset_inputs = True
            st.rerun()
            
# =============================================================================
# 🃏 POKER APP LOGIC
# =============================================================================
elif st.session_state.app_mode == "🃏 Poker":
    st.markdown('<style>.stApp { background: radial-gradient(circle at center, #0f5132, #022c22); }</style>', unsafe_allow_html=True)
    pk_players = list(st.session_state.pk_players.keys())
    
    d_idx, sb_idx, bb_idx = -1, -1, -1
    if pk_players:
        n = len(pk_players)
        d_idx = st.session_state.pk_dealer_idx % n
        sb_idx = (d_idx + 1) % n
        bb_idx = (d_idx + 2) % n

    st.title("🃏 Poker Tracker")
    
    # --- POKER HAND RANKINGS TAB/EXPANDER ---
    with st.expander("🏆 Show Poker Hand Rankings (Highest to Lowest)"):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        
        img_path_jpeg = os.path.join(current_dir, "poker_order.jpeg")
        img_path_png = os.path.join(current_dir, "poker_order.png")
        
        if os.path.exists(img_path_jpeg):
            st.image(img_path_jpeg, use_column_width=True) 
        elif os.path.exists(img_path_png):
            st.image(img_path_png, use_column_width=True)
        else:
            st.error(f"⚠️ Image not found. We looked for: \n- {img_path_jpeg}\n- {img_path_png}\n\nPlease double-check the file name and make sure it is in that exact folder.")
            
    if not st.session_state.pk_buyin_confirmed:
        with st.form("pk_add", clear_on_submit=True):
            c1, c2 = st.columns(2)
            pn = c1.text_input("Name")
            pb = c2.number_input("Buy-in", min_value=0, value=5000, step=100)
            if st.form_submit_button("Add Player"):
                if pn:
                    st.session_state.pk_players[pn] = pb
                    st.session_state.pk_total_buyin[pn] = pb
                    st.rerun()

        if pk_players:
            st.write("Manage Players:")
            for p in pk_players:
                c1, c2, c3, c4 = st.columns([3, 2, 1, 1])
                if st.session_state.pk_edit_target == p:
                    new_n = c1.text_input("Edit Name", p, key=f"edit_pk_{p}")
                    if c3.button("Save", key=f"save_pk_{p}"):
                        st.session_state.pk_players[new_n] = st.session_state.pk_players.pop(p)
                        st.session_state.pk_total_buyin[new_n] = st.session_state.pk_total_buyin.pop(p)
                        st.session_state.pk_edit_target = None
                        st.rerun()
                else:
                    c1.write(f"👤 {p}")
                    c2.write(f"₹{st.session_state.pk_players[p]}")
                    if c3.button("✏️", key=f"btn_edit_pk_{p}"):
                        st.session_state.pk_edit_target = p
                        st.rerun()
                    if c4.button("🗑️", key=f"del_pk_{p}"):
                        del st.session_state.pk_players[p]
                        del st.session_state.pk_total_buyin[p]
                        st.rerun()

            st.session_state.pk_dealer_idx = st.selectbox("Initial Dealer", range(len(pk_players)), format_func=lambda x: list(st.session_state.pk_players.keys())[x])
            if st.button("✅ Lock & Start"):
                st.session_state.pk_buyin_confirmed = True
                st.rerun()

    if st.session_state.pk_buyin_confirmed and pk_players:
        t_col1, t_col2 = st.columns([3, 1])
        with t_col1:
            st.info(f"🔘 Dealer: {pk_players[d_idx]} | 🔴 SB: {pk_players[sb_idx]} (₹25) | ⚫ BB: {pk_players[bb_idx]} (₹50)")
        with t_col2:
            if st.button("🏁 Finish Match", use_container_width=True):
                st.session_state.pk_matches.append({"players": st.session_state.pk_players.copy()})
                st.session_state.pk_players = {}; st.session_state.pk_total_buyin = {}
                st.session_state.pk_history = []; st.session_state.pk_buyin_confirmed = False
                st.rerun()
        
        if st.session_state.pk_reset_bets:
            for i, p in enumerate(pk_players):
                if i == sb_idx: st.session_state[f"pk_bet_{p}"] = min(int(st.session_state.pk_players[p]), 25)
                elif i == bb_idx: st.session_state[f"pk_bet_{p}"] = min(int(st.session_state.pk_players[p]), 50)
                else: st.session_state[f"pk_bet_{p}"] = 0
            st.session_state.pk_reset_bets = False

        # --- CALLBACK FUNCTIONS ---
        def set_all_in(player_name):
            st.session_state[f"pk_bet_{player_name}"] = int(st.session_state.pk_players[player_name])

        def add_chips(player_name, amount_key):
            amt_to_add = st.session_state[amount_key]
            if amt_to_add > 0:
                st.session_state.pk_players[player_name] += amt_to_add
                st.session_state.pk_total_buyin[player_name] += amt_to_add
                st.session_state[amount_key] = 0 # Reset the input box back to 0 instantly

        # --- BALANCES & TOP-UP AREA (Between Hands) ---
        st.subheader("💰 Balances & Top-ups")
        st.caption("⚠️ Table Stakes Rule: Only add chips *before* a new hand starts.")
        for i, p in enumerate(pk_players):
            bal = st.session_state.pk_players[p]
            buyin = st.session_state.pk_total_buyin.get(p, 0)
            net = bal - buyin
            net_class = "net-pos" if net >= 0 else "net-neg"
            tag = "🔘 Dealer" if i == d_idx else "🔴 SB" if i == sb_idx else "⚫ BB" if i == bb_idx else ""
            
            b_col1, b_col2 = st.columns([4, 1])
            with b_col1:
                st.markdown(f"<div class='card' style='margin-bottom:0px;'> <span style='float:right; color:#888;'>{tag}</span><b>{p}</b>: ₹{bal} | <span class='{net_class}'>Net: {'+' if net > 0 else ''}{net}</span></div>", unsafe_allow_html=True)
            
            with b_col2:
                rb_key = f"rb_amt_{p}"
                if rb_key not in st.session_state:
                    st.session_state[rb_key] = 0
                st.number_input(
                    "➕ Top-up (Press Enter)", 
                    min_value=0, 
                    step=100, 
                    key=rb_key, 
                    on_change=add_chips, 
                    args=(p, rb_key)
                )

        # --- MULTI-POT AND BETTING LOGIC (Active Round) ---
        st.markdown("---")
        st.subheader("🎲 Current Round")
        
        if st.session_state.pk_reset_winners:
            for k in ["w1", "w2", "w3", "w4"]:
                if k in st.session_state: st.session_state[k] = []
            st.session_state.pk_reset_winners = False

        st.caption("🏆 Rank the best hands. (Use 2nd/3rd/4th place ONLY for distributing Side Pots)")
        w_col1, w_col2, w_col3, w_col4 = st.columns(4)
        tier1 = w_col1.multiselect("1st Place", pk_players, key="w1")
        tier2 = w_col2.multiselect("2nd Place", pk_players, key="w2")
        tier3 = w_col3.multiselect("3rd Place", pk_players, key="w3")
        tier4 = w_col4.multiselect("4th Place", pk_players, key="w4")

        st.markdown("<br>**💰 Enter Bets (Clockwise Order)**", unsafe_allow_html=True)

        conts, total_pot = {}, 0
        n_players = len(pk_players)
        
        # 🔄 SORT PLAYERS BY TABLE POSITION (Starting from Small Blind)
        ordered_players = [pk_players[(sb_idx + i) % n_players] for i in range(n_players)]

        for p in ordered_players:
            orig_idx = pk_players.index(p)
            tag = "🔘 D" if orig_idx == d_idx else "🔴 SB" if orig_idx == sb_idx else "⚫ BB" if orig_idx == bb_idx else "👤"

            c1, c2 = st.columns([4, 1])
            
            amt = c1.number_input(
                f"{tag} {p}'s Bet", 
                0, 
                int(st.session_state.pk_players[p]) + 50000, 
                key=f"pk_bet_{p}"
            )
            
            c2.markdown("<div style='margin-top: 28px;'></div>", unsafe_allow_html=True)
            c2.button("ALL-IN", key=f"ai_{p}", on_click=set_all_in, args=(p,))
            
            conts[p] = amt
            total_pot += amt

        if st.button("▶ Process Round", type="primary"):
            if not tier1: 
                st.error("Select at least a 1st Place winner!")
            else:
                for p in pk_players: 
                    st.session_state.pk_players[p] -= conts[p]
                
                active_bets = {p: amt for p, amt in conts.items() if amt > 0}
                levels = sorted(list(set(active_bets.values())))
                
                # Calculate side pots for the sidebar history!
                side_pots_count = max(0, len(levels) - 1)
                
                ranked_tiers = [t for t in [tier1, tier2, tier3, tier4] if t]
                unselected = list(set(active_bets.keys()) - set(tier1 + tier2 + tier3 + tier4))
                if unselected:
                    ranked_tiers.append(unselected)

                prev_level = 0
                for level in levels:
                    pot_amount = 0
                    eligible_players = []
                    
                    for p, amt in active_bets.items():
                        if amt >= level:
                            pot_amount += (level - prev_level)
                            eligible_players.append(p)
                    
                    if pot_amount > 0:
                        for tier in ranked_tiers:
                            winners_in_tier = [w for w in tier if w in eligible_players]
                            
                            if winners_in_tier:
                                split = pot_amount / len(winners_in_tier)
                                for w in winners_in_tier:
                                    st.session_state.pk_players[w] += split
                                break 
                    
                    prev_level = level

                st.session_state.pk_dealer_idx = (st.session_state.pk_dealer_idx + 1) % len(pk_players)
                st.session_state.pk_history.append({
                    "winners": tier1, 
                    "pot": total_pot,
                    "side_pots": side_pots_count # Saved for sidebar
                })
                st.session_state.pk_reset_bets = True
                st.session_state.pk_reset_winners = True
                st.rerun()
                
                
# ==============================
# ===============================================
# ♠️ BLACKJACK APP LOGIC
# =============================================================================
elif st.session_state.app_mode == "♠️ Blackjack":
    # Casino Red/Burgundy Gradient for Blackjack
    st.markdown('<style>.stApp { background: radial-gradient(circle at center, #7f1d1d, #450a0a); }</style>', unsafe_allow_html=True)
    st.title("♠️ Blackjack")


    # --- PHASE 1: SETUP ---
    if not st.session_state.bj_confirmed:
        st.subheader("👥 Table Setup")
        with st.form("bj_add", clear_on_submit=True):
            c1, c2 = st.columns([3, 2])
            bj_n = c1.text_input("Player Name")
            bj_b = c2.number_input("Starting Chips", 100, 100000, 1000, step=100)
            if st.form_submit_button("Add Player"):
                if bj_n and bj_n not in st.session_state.bj_players:
                    st.session_state.bj_players[bj_n] = bj_b
                    st.session_state.bj_total_buyin[bj_n] = bj_b
                    st.rerun()

        if st.session_state.bj_players:
            for p in list(st.session_state.bj_players.keys()):
                col1, col2, col3, col4 = st.columns([3, 2, 1, 1])
                if st.session_state.bj_edit_target == p:
                    new_n = col1.text_input("Edit Name", p, key=f"edit_{p}")
                    if col3.button("Save", key=f"save_{p}"):
                        st.session_state.bj_players[new_n] = st.session_state.bj_players.pop(p)
                        st.session_state.bj_total_buyin[new_n] = st.session_state.bj_total_buyin.pop(p)
                        st.session_state.bj_edit_target = None; st.rerun()
                else:
                    col1.write(f"👤 {p}"); col2.write(f"Chips: {st.session_state.bj_players[p]}")
                    if col3.button("✏️", key=f"ed_{p}"): st.session_state.bj_edit_target = p; st.rerun()
                    if col4.button("🗑️", key=f"del_{p}"): 
                        del st.session_state.bj_players[p]; del st.session_state.bj_total_buyin[p]; st.rerun()
            
            if st.button("✅ Start Game", type="primary", use_container_width=True):
                st.session_state.bj_confirmed = True; st.rerun()

    # --- PHASE 2: GAMEPLAY ---
    else:
        c_h, c_f = st.columns([4, 1])
        with c_f:
            if st.button("🏁 Finish Match", use_container_width=True):
                st.session_state.bj_matches.append({"players": st.session_state.bj_players.copy()})
                st.session_state.bj_players = {}; st.session_state.bj_confirmed = False; st.rerun()

        # Display Chips
        for p, bal in st.session_state.bj_players.items():
            net = bal - st.session_state.bj_total_buyin[p]
            style = "net-pos" if net >= 0 else "net-neg"
            st.markdown(f"<div class='card bj-card'><b>{p}</b>: {bal} chips <span style='float:right' class='{style}'>Net: {'+' if net > 0 else ''}{net}</span></div>", unsafe_allow_html=True)

        st.markdown("---")
        st.subheader("🎲 Resolve Round")
        
        round_data = {}
        for p in st.session_state.bj_players:
            with st.expander(f"Update Results for {p}", expanded=True):
                # Main Blackjack Bet
                col1, col2 = st.columns([1, 2])
                main_bet = col1.number_input(f"Main Bet ({p})", 0, 10000, 50, key=f"main_{p}")
                outcome = col2.radio(f"Result ({p})", ["Win (1x)", "Blackjack (1.5x)", "Push", "Lose"], horizontal=True, key=f"res_{p}")
                
                # High Card Side Bet
                col3, col4 = st.columns([1, 2])
                hc_bet = col3.number_input(f"High Card Bet ({p})", 0, 5000, 0, step=10, key=f"hc_bet_{p}")
                hc_res = col4.radio(f"High Card Result ({p})", ["HC Win", "HC Lose"], horizontal=True, key=f"hc_res_{p}")
                
                round_data[p] = {"bet": main_bet, "out": outcome, "hc_bet": hc_bet, "hc_out": hc_res}

        if st.button("▶ Update All Chips", type="primary", use_container_width=True):
            for p, d in round_data.items():
                # Process Main Bet
                if d["out"] == "Win (1x)": st.session_state.bj_players[p] += d["bet"]
                elif d["out"] == "Blackjack (1.5x)": st.session_state.bj_players[p] += int(d["bet"] * 1.5)
                elif d["out"] == "Lose": st.session_state.bj_players[p] -= d["bet"]
                
                # Process High Card Bet (Only if bet > 0)
                if d["hc_bet"] > 0:
                    if d["hc_out"] == "HC Win": st.session_state.bj_players[p] += d["hc_bet"]
                    else: st.session_state.bj_players[p] -= d["hc_bet"]
            
            st.success("Round chips adjusted!")
            st.rerun()
            
            
st.markdown("---")
st.caption("Card Games Tracker ~ Arka ♠️🟢")
