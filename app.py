import streamlit as st
import random

# --- DATA & ASSETS ---
TYPE_CHART = {
    "Fire": {"Grass": 2.0, "Water": 0.5, "Fire": 0.5},
    "Water": {"Fire": 2.0, "Grass": 0.5, "Water": 0.5},
    "Grass": {"Water": 2.0, "Fire": 0.5, "Grass": 0.5}
}

DATA = {
    "Kanto": {
        "Bulbasaur": {"id": 1, "type": "Grass", "hp": 100, "moves": {"Tackle": 15, "Vine Whip": 25}},
        "Charmander": {"id": 4, "type": "Fire", "hp": 100, "moves": {"Scratch": 15, "Ember": 25}},
        "Squirtle": {"id": 7, "type": "Water", "hp": 100, "moves": {"Tackle": 15, "Water Gun": 25}},
    },
    "Hoenn": {
        "Treecko": {"id": 252, "type": "Grass", "hp": 100, "moves": {"Pound": 15, "Absorb": 28}},
        "Torchic": {"id": 255, "type": "Fire", "hp": 100, "moves": {"Scratch": 15, "Ember": 28}},
        "Mudkip": {"id": 258, "type": "Water", "hp": 100, "moves": {"Tackle": 15, "Water Gun": 28}},
    }
}

# --- STYLING ---
st.set_page_config(page_title="PokeStream v2", page_icon="🎮")

st.markdown("""
    <style>
    .stApp { background: #121212; color: white; }
    .poke-card { background: #2d2d2d; padding: 20px; border-radius: 15px; border: 2px solid #555; text-align: center; }
    .battle-log { color: #00ff00; font-family: monospace; background: #000; padding: 10px; border-radius: 5px; }
    </style>
""", unsafe_allow_html=True)

# --- INITIALIZE MEMORY (SESSION STATE) ---
if 'phase' not in st.session_state:
    st.session_state.phase = "setup"
    st.session_state.logs = []
    st.session_state.player = None
    st.session_state.enemy = None

def get_img(poke_id):
    return f"https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/{poke_id}.png"

# --- GAME FUNCTIONS ---
def handle_attack(move_name, move_power):
    # 1. Player Attack Logic
    p_type = st.session_state.player['type']
    e_type = st.session_state.enemy['type']
    
    # Check multiplier
    mult = TYPE_CHART.get(p_type, {}).get(e_type, 1.0)
    dmg = int(move_power * mult) + random.randint(-2, 2)
    st.session_state.enemy['hp'] -= dmg
    
    msg = f"✨ {st.session_state.player['name']} used {move_name}!"
    if mult > 1: msg += " (SUPER EFFECTIVE!)"
    elif mult < 1: msg += " (Not very effective...)"
    st.session_state.logs.append(msg)

    # 2. Check if Enemy Fainted
    if st.session_state.enemy['hp'] <= 0:
        st.session_state.enemy['hp'] = 0
        st.session_state.phase = "end"
        return

    # 3. Enemy Turn Logic
    e_move = random.choice(list(st.session_state.enemy['moves'].keys()))
    e_power = st.session_state.enemy['moves'][e_move]
    
    # Enemy multiplier (Opposite)
    e_mult = TYPE_CHART.get(e_type, {}).get(p_type, 1.0)
    e_dmg = int(e_power * e_mult) + random.randint(-2, 2)
    st.session_state.player['hp'] -= e_dmg
    
    st.session_state.logs.append(f"💥 Enemy {st.session_state.enemy['name']} used {e_move}! Dealing {e_dmg} damage.")

    # 4. Check if Player Fainted
    if st.session_state.player['hp'] <= 0:
        st.session_state.player['hp'] = 0
        st.session_state.phase = "end"

# --- UI LOGIC ---
if st.session_state.phase == "setup":
    st.title("🛡️ Choose Your Region & Pokémon")
    region = st.selectbox("Region", list(DATA.keys()))
    
    cols = st.columns(3)
    starters = DATA[region]
    
    for i, (name, details) in enumerate(starters.items()):
        with cols[i]:
            st.image(get_img(details['id']))
            # Critical Fix: Using session_state inside the button logic
            if st.button(f"Pick {name}", key=f"btn_{name}"):
                st.session_state.player = {
                    "name": name, "hp": 100, "type": details['type'], 
                    "id": details['id'], "moves": details['moves']
                }
                # Pick a random opponent from the same region
                opp_name = random.choice(list(starters.keys()))
                opp_details = starters[opp_name]
                st.session_state.enemy = {
                    "name": opp_name, "hp": 100, "type": opp_details['type'], 
                    "id": opp_details['id'], "moves": opp_details['moves']
                }
                st.session_state.phase = "battle"
                st.rerun()

elif st.session_state.phase == "battle":
    st.title("⚔️ Battle Arena")
    
    # Display Health & Images
    c1, c2 = st.columns(2)
    with c1:
        st.markdown(f"### {st.session_state.player['name']}")
        st.image(get_img(st.session_state.player['id']), width=150)
        st.progress(st.session_state.player['hp'] / 100)
        st.write(f"HP: {st.session_state.player['hp']}/100")
        
    with c2:
        st.markdown(f"### Enemy {st.session_state.enemy['name']}")
        st.image(get_img(st.session_state.enemy['id']), width=150)
        st.progress(st.session_state.enemy['hp'] / 100)
        st.write(f"HP: {st.session_state.enemy['hp']}/100")

    st.divider()
    
    # Move Selection
    st.write("#### Your Moves:")
    move_cols = st.columns(2)
    moves = list(st.session_state.player['moves'].items())
    
    for i, (m_name, m_power) in enumerate(moves):
        # We pass the logic to a function to keep state clean
        if move_cols[i%2].button(f"{m_name} (Pwr: {m_power})", key=f"move_{i}"):
            handle_attack(m_name, m_power)
            st.rerun()

    # Logs
    with st.expander("Battle History", expanded=True):
        for log in reversed(st.session_state.logs):
            st.markdown(f"<div class='battle-log'>{log}</div>", unsafe_allow_html=True)

elif st.session_state.phase == "end":
    if st.session_state.player['hp'] > 0:
        st.balloons()
        st.success(f"VICTORY! {st.session_state.player['name']} won!")
    else:
        st.error("DEFEAT! You fainted.")
    
    if st.button("Play Again"):
        st.session_state.clear()
        st.rerun()