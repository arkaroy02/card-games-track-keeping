import streamlit as st
import copy

# -----------------------------
# Page Configuration
# -----------------------------
st.set_page_config(page_title="Bridge Pro Master", layout="wide")

# 🎨 THE GLASS-MODERN UI
st.markdown("""
<style>
    .stApp { background-color: #1a472a; color: white; }
    
    /* FAQ Table Styling */
    .faq-table { width: 100%; border-collapse: collapse; background: #0d2b1a; border: 1px solid #d4af37; border-radius: 8px; margin-bottom: 20px; }
    .faq-table th { background: #d4af37; color: #1a472a; padding: 10px; text-align: left; }
    .faq-table td { padding: 8px; border-bottom: 1px solid #245e3a; font-size: 0.9em; }
    .faq-cat { color: #ffcc00; font-weight: bold; width: 30%; }

    /* Scorer Card Styling */
    .score-card {
        background-color: #163e25;
        border: 2px solid #d4af37;
        border-radius: 12px;
        padding: 25px;
        box-shadow: 0px 10px 30px rgba(0,0,0,0.5);
        margin-bottom: 20px;
    }
    .score-table { width: 100%; border-collapse: collapse; text-align: center; font-size: 1.1em; }
    .score-table th { border-bottom: 2px solid #d4af37; padding: 12px; color: #d4af37; font-size: 1.3em; }
    .score-table td { padding: 10px; border-bottom: 1px solid #ffffff11; }
    .total-row { font-weight: bold; font-size: 1.5em; color: #00ffcc; border-top: 3px solid #d4af37 !important; }
    .vuln-badge { background-color: #ff4b4b; color: white; padding: 2px 6px; border-radius: 4px; font-size: 0.7em; margin-left: 5px; }

    /* 💎 NEW GLASS BIDDING PANEL UI 💎 */
    .glass-bidding-panel {
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 30px;
        padding: 30px;
        margin: 20px auto;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
    }

    .live-sequence {
        background: rgba(0, 0, 0, 0.2);
        padding: 15px;
        border-radius: 15px;
        font-family: 'Segoe UI', sans-serif;
        font-size: 1.2em;
        color: #00ffcc;
        border-left: 5px solid #00ffcc;
        margin-bottom: 20px;
        text-align: center;
    }

    /* Large, Modern Buttons */
    div.stButton > button {
        border-radius: 15px !important;
        height: 65px !important; 
        font-size: 1.6em !important;
        font-weight: 800 !important;
        border: 1px solid rgba(255,255,255,0.1) !important;
        transition: all 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275);
    }

    div.stButton > button:hover {
        transform: translateY(-3px);
        box-shadow: 0 10px 20px rgba(0,0,0,0.3);
    }

    /* Vibrant Gradients for Suit Buttons */
    .club-bid button { background: linear-gradient(145deg, #2c3e50, #34495e) !important; color: #fff !important; }
    .diamond-bid button { background: linear-gradient(145deg, #d35400, #e67e22) !important; color: #fff !important; }
    .heart-bid button { background: linear-gradient(145deg, #c0392b, #e74c3c) !important; color: #fff !important; }
    .spade-bid button { background: linear-gradient(145deg, #000000, #2c3e50) !important; color: #fff !important; }
    .nt-bid button { background: linear-gradient(145deg, #1e8449, #27ae60) !important; color: #00ffcc !important; }

    /* Active Selection Highlight */
    .highlight-bid button {
        border: 3px solid #00ffcc !important;
        box-shadow: 0 0 25px rgba(0, 255, 204, 0.6) !important;
    }

    /* Big Level Numbers */
    .lvl-label {
        font-size: 2em;
        font-weight: 900;
        color: #f1c40f;
        text-align: center;
        line-height: 65px;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.5);
    }

    .section-header { font-weight: bold; color: #d4af37; background: #0d2b1a; }
</style>
""", unsafe_allow_html=True)

# -----------------------------
# Session State
# -----------------------------
if "br_scores" not in st.session_state:
    st.session_state.br_scores = {
        "WE": {"above": 0, "below_g1": 0, "below_g2": 0, "below_g3": 0, "games": 0, "vuln": False},
        "THEY": {"above": 0, "below_g1": 0, "below_g2": 0, "below_g3": 0, "games": 0, "vuln": False}
    }
if "history" not in st.session_state: st.session_state.history = []
if "last_entry" not in st.session_state: st.session_state.last_entry = {"cp": 0, "ot": 0, "slam": 0, "insult": 0, "pen": 0, "team": ""}
if "bidding_active" not in st.session_state: st.session_state.bidding_active = True
if "bid_history" not in st.session_state: st.session_state.bid_history = []
if "current_bid" not in st.session_state: st.session_state.current_bid = {"lvl": 0, "suit": "", "team": ""}
if "pass_count" not in st.session_state: st.session_state.pass_count = 0
if "risk_multiplier" not in st.session_state: st.session_state.risk_multiplier = "Normal"
if "dealer" not in st.session_state: st.session_state.dealer = "WE"

# -----------------------------
# 📖 FAQ
# -----------------------------
with st.expander("🎯 BRIDGE SCORING – MASTER RULE TABLE", expanded=False):
    st.markdown("""
    <table class='faq-table'>
        <tr><th>Category</th><th>Details</th><th>Points</th></tr>
        <tr><td class='faq-cat'>Trick Points (Below)</td><td>No Trump (1st / Others)</td><td>40 / 30</td></tr>
        <tr><td class='faq-cat'>Trick Points (Below)</td><td>Majors (♥/♠) / Minors (♣/♦)</td><td>30 / 20</td></tr>
        <tr><td class='faq-cat'>Overtricks (Above)</td><td>Undoubled (NV / V)</td><td>Suit Val / 100 / 200</td></tr>
        <tr><td class='faq-cat'>Penalty (NV)</td><td>Doubled: 1st / 2nd-3rd / 4th+</td><td>100 / 200 / 300</td></tr>
        <tr><td class='faq-cat'>Penalty (V)</td><td>Doubled: 1st / Others</td><td>200 / 300</td></tr>
        <tr><td class='faq-cat'>Slams (Bid)</td><td>Small (12 Tricks) - NV / V</td><td>500 / 750</td></tr>
        <tr><td class='faq-cat'>Slams (Bid)</td><td>Grand (13 Tricks) - NV / V</td><td>1000 / 1500</td></tr>
    </table>
    """, unsafe_allow_html=True)

# -----------------------------
# 📢 BIDDING SECTION
# -----------------------------
st.title("🃏 Bridge Pro Master")

if st.session_state.bidding_active:
    st.markdown("<div class='glass-bidding-panel'>", unsafe_allow_html=True)
    
    # Dealer Selection
    if not st.session_state.bid_history:
        st.session_state.dealer = st.radio("Who is the Dealer?", ["WE", "THEY"], horizontal=True)
    
    seq_text = " ➔ ".join(st.session_state.bid_history) if st.session_state.bid_history else "Ready for opener..." 
    
    t_col1, t_col2 = st.columns([3, 1])
    with t_col1:
        st.markdown(f"<div class='live-sequence'><b>SEQUENCE:</b> {seq_text}</div>", unsafe_allow_html=True)
    with t_col2:
        if st.button("Reset Bids", use_container_width=True):
            st.session_state.bid_history, st.session_state.current_bid = [], {"lvl": 0, "suit": "", "team": ""}
            st.session_state.pass_count = 0
            st.rerun()

    turn_order = ["WE", "THEY"] if st.session_state.dealer == "WE" else ["THEY", "WE"]
    current_turn = turn_order[len(st.session_state.bid_history) % 2]
    st.markdown(f"<h2 style='text-align:center; color:#00ffcc; margin-top:0;'>{current_turn}'s Turn</h2>", unsafe_allow_html=True)

    suit_info = [("♣", "club-bid"), ("♦", "diamond-bid"), ("♥", "heart-bid"), ("♠", "spade-bid"), ("NT", "nt-bid")]
    suit_names = ["♣", "♦", "♥", "♠", "NT"]

    for lvl in range(1, 8):
        cols = st.columns([0.5, 1, 1, 1, 1, 1], gap="medium")
        cols[0].markdown(f"<div class='lvl-label'>{lvl}</div>", unsafe_allow_html=True)

        for i, (icon, style_class) in enumerate(suit_info):
            is_current = (lvl == st.session_state.current_bid["lvl"] and icon == st.session_state.current_bid["suit"])
            final_style = f"{style_class} highlight-bid" if is_current else style_class

            is_disabled = False
            if lvl < st.session_state.current_bid["lvl"]: is_disabled = True
            elif lvl == st.session_state.current_bid["lvl"]:
                cur_suit_rank = suit_names.index(st.session_state.current_bid["suit"]) if st.session_state.current_bid["suit"] else -1
                if i <= cur_suit_rank: is_disabled = True

            with cols[i+1]:
                st.markdown(f"<div class='{final_style}'>", unsafe_allow_html=True)
                if st.button(f"{lvl}{icon}", key=f"b_{lvl}_{icon}", disabled=is_disabled, use_container_width=True):
                    st.session_state.current_bid = {"lvl": lvl, "suit": icon, "team": current_turn}
                    st.session_state.bid_history.append(f"{current_turn}: {lvl}{icon}")
                    st.session_state.pass_count = 0
                    st.rerun()
                st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div style='margin-top:25px;'></div>", unsafe_allow_html=True)
    b_cols = st.columns(3, gap="large")
    if b_cols[0].button("PASS", use_container_width=True):
        st.session_state.bid_history.append(f"{current_turn}: PASS")
        st.session_state.pass_count += 1
        if st.session_state.pass_count >= 3 and st.session_state.current_bid["lvl"] > 0:
            st.session_state.bidding_active = False
        elif st.session_state.pass_count >= 4:
            st.session_state.bid_history, st.session_state.current_bid = [], {"lvl": 0, "suit": "", "team": ""}
            st.session_state.pass_count = 0
            st.info("Hand Passed Out.")
        st.rerun()
    if b_cols[1].button("DOUBLE (X)", use_container_width=True):
        st.session_state.risk_multiplier = "Doubled"
        st.session_state.bid_history.append(f"{current_turn}: X")
        st.rerun()
    if b_cols[2].button("REDOUBLE (XX)", use_container_width=True):
        st.session_state.risk_multiplier = "Redoubled"
        st.session_state.bid_history.append(f"{current_turn}: XX")
        st.rerun()
    
    st.markdown("</div>", unsafe_allow_html=True)

# -----------------------------
# 📊 LIVE SCOREBOARD TABLE
# -----------------------------
s = st.session_state.br_scores
le = st.session_state.last_entry

we_v = '<span class="vuln-badge">VUL</span>' if s['WE']['vuln'] else ''
they_v = '<span class="vuln-badge">VUL</span>' if s['THEY']['vuln'] else ''
we_total = s['WE']['above'] + s['WE']['below_g1'] + s['WE']['below_g2'] + s['WE']['below_g3']
they_total = s['THEY']['above'] + s['THEY']['below_g1'] + s['THEY']['below_g2'] + s['THEY']['below_g3']

st.markdown(f"""
<div class='score-card'>
    <table class='score-table'>
        <thead>
            <tr>
                <th style='text-align:left;'>LIVE SCOREBOARD</th>
                <th>WE {we_v}</th>
                <th>THEY {they_v}</th>
            </tr>
        </thead>
        <tbody>
            <tr><td>Contract Points (Below)</td><td>{le['cp'] if le['team']=='WE' else 0}</td><td>{le['cp'] if le['team']=='THEY' else 0}</td></tr>
            <tr><td>Overtrick Points</td><td>{le['ot'] if le['team']=='WE' else 0}</td><td>{le['ot'] if le['team']=='THEY' else 0}</td></tr>
            <tr><td>Slam Bonus</td><td>{le['slam'] if le['team']=='WE' else 0}</td><td>{le['slam'] if le['team']=='THEY' else 0}</td></tr>
            <tr><td>Made Doubled Bonus</td><td>{le['insult'] if le['team']=='WE' else 0}</td><td>{le['insult'] if le['team']=='THEY' else 0}</td></tr>
            <tr><td>Undertrick Penalty</td><td>{le['pen'] if le['team']=='WE' else 0}</td><td>{le['pen'] if le['team']=='THEY' else 0}</td></tr>
            <tr class='section-header'><td colspan='3'>Above the line</td></tr>
            <tr style='font-style: italic; color: #bb86fc;'>
                <td style='text-align:right;'>Total Above Line</td>
                <td>{s['WE']['above']}</td>
                <td>{s['THEY']['above']}</td>
            </tr>
            <tr class='section-header'><td colspan='3'>Below the line</td></tr>
            <tr><td style='text-align:right;'>Game 1</td><td>{s['WE']['below_g1']}</td><td>{s['THEY']['below_g1']}</td></tr>
            <tr><td style='text-align:right;'>Game 2</td><td>{s['WE']['below_g2']}</td><td>{s['THEY']['below_g2']}</td></tr>
            <tr><td style='text-align:right;'>Game 3</td><td>{s['WE']['below_g3']}</td><td>{s['THEY']['below_g3']}</td></tr>
            <tr class='total-row'>
                <td style='text-align:left;'>TOTAL POINTS</td>
                <td>{we_total}</td>
                <td>{they_total}</td>
            </tr>
        </tbody>
    </table>
</div>
""", unsafe_allow_html=True)

# -----------------------------
# 💰 SCORING LOGIC
# -----------------------------
if not st.session_state.bidding_active:
    cb = st.session_state.current_bid
    with st.expander(f"💰 CALCULATE SCORE: {cb['lvl']}{cb['suit']} by {cb['team']}", expanded=True):
        with st.form("result_form"):
            tricks = st.number_input("Total Tricks Won", 0, 13, 6 + cb['lvl'])
            honors = st.selectbox("Honors Held", [0, 100, 150])
            
            if st.form_submit_button("💰 COMMIT TO SCOREBOARD"):
                st.session_state.history.append(copy.deepcopy(st.session_state.br_scores))
                declarer, opp = cb['team'], ("THEY" if cb['team'] == "WE" else "WE")
                is_vuln = s[declarer]["vuln"]
                needed = 6 + cb['lvl']
                m = (1 if st.session_state.risk_multiplier == "Normal" else 2 if st.session_state.risk_multiplier == "Doubled" else 4)
                res = {"cp": 0, "ot": 0, "slam": 0, "insult": 0, "pen": 0, "team": declarer}

                if tricks >= needed:
                    if cb['suit'] == "NT": res["cp"] = (40 + (cb['lvl']-1)*30) * m
                    elif cb['suit'] in ["♥", "♠"]: res["cp"] = (cb['lvl'] * 30) * m
                    else: res["cp"] = (cb['lvl'] * 20) * m
                    
                    g_idx = min(s[declarer]["games"] + 1, 3)
                    s[declarer][f"below_g{g_idx}"] += res["cp"]
                    
                    over = tricks - needed
                    if over > 0:
                        if st.session_state.risk_multiplier == "Normal": 
                            res["ot"] = over * (20 if cb['suit'] in ["♣", "♦"] else 30)
                        else:
                            val = 100 if not is_vuln else 200
                            if st.session_state.risk_multiplier == "Redoubled": val *= 2 
                            res["ot"] = over * val
                    
                    if cb['lvl'] == 6: res["slam"] = 500 if not is_vuln else 750
                    elif cb['lvl'] == 7: res["slam"] = 1000 if not is_vuln else 1500
                    
                    if st.session_state.risk_multiplier == "Doubled": res["insult"] = 50
                    elif st.session_state.risk_multiplier == "Redoubled": res["insult"] = 100
                    
                    s[declarer]["above"] += (res["ot"] + res["slam"] + res["insult"] + honors)

                    if s[declarer][f"below_g{g_idx}"] >= 100:
                        s[declarer]["games"] += 1
                        s[declarer]["vuln"] = True
                        if s[declarer]["games"] >= 2:
                            s[declarer]["above"] += (700 if s[opp]["games"] == 0 else 500)
                            st.balloons()
                else:
                    under = needed - tricks
                    res["team"] = opp
                    if st.session_state.risk_multiplier == "Normal": 
                        res["pen"] = under * (100 if is_vuln else 50)
                    else:
                        if not is_vuln:
                            p_list = [100, 300, 500]
                            res["pen"] = p_list[min(under-1, 2)] + (max(0, under-3) * 300)
                        else: 
                            res["pen"] = 200 + (under-1)*300
                        if st.session_state.risk_multiplier == "Redoubled": res["pen"] *= 2
                    s[opp]["above"] += (res["pen"] + honors)

                st.session_state.last_entry = res
                st.session_state.bidding_active = True
                st.session_state.bid_history, st.session_state.current_bid = [], {"lvl": 0, "suit": "", "team": ""}
                st.rerun()

# -----------------------------
# 🛠️ SIDEBAR
# -----------------------------
st.sidebar.title("🛠️ Game Admin")
if st.sidebar.button("⏪ Undo Last Hand"):
    if st.session_state.history: 
        st.session_state.br_scores = st.session_state.history.pop()
        st.rerun()
if st.sidebar.button("🗑️ Reset Rubber"):
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.rerun()
