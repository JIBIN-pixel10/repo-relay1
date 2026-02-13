import streamlit as st
import random
import time

# --- POKEDEX DATA ---
DATA = {
    "Kanto": {
        "Bulbasaur": {"hp": 100, "moves": {"Tackle": 10, "Vine Whip": 20, "Razor Leaf": 25}},
        "Charmander": {"hp": 100, "moves": {"Scratch": 10, "Ember": 22, "Flamethrower": 30}},
        "Squirtle": {"hp": 100, "moves": {"Tackle": 10, "Water Gun": 18, "Bubble": 20}},
    },
    "Hoenn": {
        "Treecko": {"hp": 100, "moves": {"Pound": 12, "Absorb": 15, "Leaf Blade": 28}},
        "Torchic": {"hp": 100, "moves": {"Scratch": 10, "Ember": 22, "Peck": 18}},
        "Mudkip": {"hp": 100, "moves": {"Tackle": 10, "Water Gun": 20, "Mud-Slap": 15}},
    }
}

# --- STYLING ---
st.set_page_config(page_title="PokeStream Battle", page_icon="⚔️")
st.markdown("""
    <style>
    .main { background-color: #f0f2f6; }
    .stButton>button { width: 100%; border-radius: 20px; height: 3em; background-color: #ff4b4b; color: white; }
    .battle-log { background-color: #ffffff; padding: 15px; border-radius: 10px; border: 1px solid #ddd; height: 200px; overflow-y: auto; }
    </style>
    """, unsafe_allow_html=True)

# --- INITIALIZE SESSION STATE ---
if 'game_state' not in st.session_state:
    st.session_state.game_state = "setup"
    st.session_state.logs = ["Welcome to the Battle Arena!"]

# --- GAME LOGIC ---
def add_log(msg):
    st.session_state.logs.append(msg)

def process_turn(move_name, move_power):
    # Player Turn
    dmg = move_power + random.randint(-2, 4)
    st.session_state.opp_hp = max(0, st.session_state.opp_hp - dmg)
    add_log(f"🔥 {st.session_state.player_poke} used {move_name}! Dealt {dmg} damage.")
    
    if st.session_state.opp_hp <= 0:
        st.session_state.game_state = "won"
        return

    # Enemy Turn
    opp_move = random.choice(list(st.session_state.opp_moves.keys()))
    opp_dmg = st.session_state.opp_moves[opp_move] + random.randint(-2, 4)
    st.session_state.player_hp = max(0, st.session_state.player_hp - opp_dmg)
    add_log(f"💥 Wild {st.session_state.opp_name} used {opp_move}! Dealt {opp_dmg} damage.")
    
    if st.session_state.player_hp <= 0:
        st.session_state.game_state = "lost"

# --- UI SCREENS ---
if st.session_state.game_state == "setup":
    st.title("🎒 Choose Your Starter")
    region = st.selectbox("Select Region", list(DATA.keys()))
    
    cols = st.columns(3)
    starters = list(DATA[region].keys())
    
    for i, name in enumerate(starters):
        with cols[i]:
            st.subheader(name)
            if st.button(f"Choose {name}"):
                st.session_state.player_poke = name
                st.session_state.player_hp = DATA[region][name]["hp"]
                st.session_state.player_moves = DATA[region][name]["moves"]
                
                # Setup Enemy
                opp = random.choice(starters)
                st.session_state.opp_name = opp
                st.session_state.opp_hp = DATA[region][opp]["hp"]
                st.session_state.opp_moves = DATA[region][opp]["moves"]
                
                st.session_state.game_state = "battle"
                st.rerun()

elif st.session_state.game_state == "battle":
    st.title("⚔️ Battle Underway!")
    
    # Battle Display
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric("Your " + st.session_state.player_poke, f"{st.session_state.player_hp} HP")
        st.progress(st.session_state.player_hp / 100)
        
    with col2:
        st.metric("Wild " + st.session_state.opp_name, f"{st.session_state.opp_hp} HP")
        st.progress(st.session_state.opp_hp / 100)

    st.divider()

    # Moves
    st.write("### Choose a Move:")
    m_cols = st.columns(len(st.session_state.player_moves))
    for i, (m_name, m_power) in enumerate(st.session_state.player_moves.items()):
        if m_cols[i].button(m_name):
            process_turn(m_name, m_power)
            st.rerun()

    # Logs
    st.write("### Battle Log")
    log_text = "\n".join(st.session_state.logs[::-1]) # Show latest on top
    st.text_area("", log_text, height=150, disabled=True)

elif st.session_state.game_state in ["won", "lost"]:
    if st.session_state.game_state == "won":
        st.balloons()
        st.success(f"VICTORY! Your {st.session_state.player_poke} won!")
    else:
        st.error(f"DEFEAT! {st.session_state.player_poke} fainted...")
        
    if st.button("Play Again"):
        st.session_state.game_state = "setup"
        st.session_state.logs = ["New game started!"]
        st.rerun()