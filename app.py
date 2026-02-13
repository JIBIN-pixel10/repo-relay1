import streamlit as st
import random
import json
import os

# --- PERSISTENCE  ---
SAVE_FILE = "trainer_data.json"

def load_data():
    if os.path.exists(SAVE_FILE):
        try:
            with open(SAVE_FILE, "r") as f: return json.load(f)
        except: return {"total_wins": 0}
    return {"total_wins": 0}

def save_data(wins):
    with open(SAVE_FILE, "w") as f: json.dump({"total_wins": wins}, f)

# --- DATASET ---
TYPE_CHART = {
    "Fire": {"Grass": 2.0, "Water": 0.5, "Fire": 0.5},
    "Water": {"Fire": 2.0, "Grass": 0.5, "Water": 0.5},
    "Grass": {"Water": 2.0, "Fire": 0.5, "Grass": 0.5}
}

REGIONS = {
    "Kanto": {
        "Bulbasaur": {"id": 1, "type": "Grass", "hp": 100, "moves": {"Tackle": 15, "Vine Whip": 25}},
        "Charmander": {"id": 4, "type": "Fire", "hp": 100, "moves": {"Scratch": 15, "Ember": 25}},
        "Squirtle": {"id": 7, "type": "Water", "hp": 100, "moves": {"Tackle": 15, "Water Gun": 25}},
    },
    "Johto": {
        "Chikorita": {"id": 152, "type": "Grass", "hp": 100, "moves": {"Tackle": 15, "Razor Leaf": 25}},
        "Cyndaquil": {"id": 155, "type": "Fire", "hp": 100, "moves": {"Tackle": 15, "Flame Wheel": 25}},
        "Totodile": {"id": 158, "type": "Water", "hp": 100, "moves": {"Scratch": 15, "Water Gun": 25}},
    },
    "Hoenn": {
        "Treecko": {"id": 252, "type": "Grass", "hp": 100, "moves": {"Pound": 15, "Absorb": 28}},
        "Torchic": {"id": 255, "type": "Fire", "hp": 100, "moves": {"Scratch": 15, "Ember": 28}},
        "Mudkip": {"id": 258, "type": "Water", "hp": 100, "moves": {"Tackle": 15, "Water Gun": 28}},
    },
    "Sinnoh": {
        "Turtwig": {"id": 387, "type": "Grass", "hp": 100, "moves": {"Tackle": 15, "Razor Leaf": 25}},
        "Chimchar": {"id": 390, "type": "Fire", "hp": 100, "moves": {"Scratch": 15, "Ember": 25}},
        "Piplup": {"id": 393, "type": "Water", "hp": 100, "moves": {"Pound": 15, "Water Gun": 25}},
    },
    "Unova": {
        "Snivy": {"id": 495, "type": "Grass", "hp": 100, "moves": {"Tackle": 15, "Leaf Tornado": 25}},
        "Tepig": {"id": 498, "type": "Fire", "hp": 100, "moves": {"Tackle": 15, "Ember": 25}},
        "Oshawott": {"id": 501, "type": "Water", "hp": 100, "moves": {"Tackle": 15, "Water Gun": 25}},
    },
    "Kalos": {
        "Chespin": {"id": 650, "type": "Grass", "hp": 100, "moves": {"Vine Whip": 20, "Seed Bomb": 28}},
        "Fennekin": {"id": 653, "type": "Fire", "hp": 100, "moves": {"Scratch": 15, "Psybeam": 23}},
        "Froakie": {"id": 656, "type": "Water", "hp": 100, "moves": {"Pound": 15, "Water Pulse": 25}},
    },
    "Alola": {
        "Rowlet": {"id": 722, "type": "Grass", "hp": 100, "moves": {"Leafage": 20, "Astonish": 25}},
        "Litten": {"id": 725, "type": "Fire", "hp": 100, "moves": {"Scratch": 15, "Fire Fang": 25}},
        "Popplio": {"id": 728, "type": "Water", "hp": 100, "moves": {"Pound": 19, "Bubble Beam": 28}},
    }
}

# --- UI SETTINGS ---
st.set_page_config(page_title="NEON POKESTREAM", layout="wide")

st.markdown("""
    <style>
    /* Background Image with Dark Overlay */
    .stApp {
        background: linear-gradient(rgba(0, 0, 0, 0.8), rgba(0, 0, 0, 0.8)), 
                    url("https://images.unsplash.com/photo-1614850523296-d8c1af93d400?q=80&w=2070");
        background-size: cover;
        color: #0ff;
    }

    /* Neon Cards */
    .poke-card {
        background: rgba(20, 20, 20, 0.8);
        border: 2px solid #0ff;
        border-radius: 15px;
        padding: 20px;
        text-align: center;
        box-shadow: 0 0 15px #0ff, inset 0 0 5px #0ff;
        transition: 0.3s;
    }
    .poke-card:hover {
        box-shadow: 0 0 30px #f0f, inset 0 0 10px #f0f;
        border-color: #f0f;
    }

    /* Neon Buttons */
    .stButton>button {
        background: transparent;
        color: #0ff;
        border: 2px solid #0ff;
        border-radius: 10px;
        box-shadow: 0 0 10px #0ff;
        font-weight: bold;
        transition: 0.3s;
    }
    .stButton>button:hover {
        background: #0ff;
        color: black;
        box-shadow: 0 0 20px #0ff;
    }

    /* Text Glow */
    h1, h2, h3 {
        text-shadow: 0 0 10px #0ff, 0 0 20px #0ff;
        color: white !important;
    }
    </style>
""", unsafe_allow_html=True)

# --- STATE ---
if 'phase' not in st.session_state:
    st.session_state.update({
        "phase": "setup", 
        "total_wins": load_data()["total_wins"], 
        "player": None, "enemy": None, "logs": []
    })

def get_img(pid): return f"https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/{pid}.png"

# --- SCREENS ---
if st.session_state.phase == "setup":
    st.title("⚡ NEON POKEMON SELECT")
    st.sidebar.metric("PERMANENT WINS", st.session_state.total_wins)
    
    reg_choice = st.selectbox("CHOOSE REGION", list(REGIONS.keys()))
    cols = st.columns(3)
    
    starters = REGIONS[reg_choice]
    for i, (name, data) in enumerate(starters.items()):
        with cols[i]:
            st.markdown(f"<div class='poke-card'>", unsafe_allow_html=True)
            st.image(get_img(data['id']))
            if st.button(f"SELECT {name}", key=name, use_container_width=True):
                st.session_state.player = data.copy()
                st.session_state.player['name'] = name
                # Pick random opponent
                all_starters = []
                for r in REGIONS.values(): all_starters.extend(list(r.items()))
                opp_name, opp_data = random.choice(all_starters)
                st.session_state.enemy = opp_data.copy()
                st.session_state.enemy['name'] = opp_name
                st.session_state.phase = "battle"
                st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)

elif st.session_state.phase == "battle":
    st.title("⚔️ CYBER BATTLE ARENA")
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("<div class='poke-card'>", unsafe_allow_html=True)
        st.image(get_img(st.session_state.player['id']), width=180)
        st.subheader(st.session_state.player['name'])
        st.progress(max(0, st.session_state.player['hp']) / 100)
        st.markdown("</div>", unsafe_allow_html=True)
    with c2:
        st.markdown("<div class='poke-card' style='border-color: #f0f; box-shadow: 0 0 15px #f0f;'>", unsafe_allow_html=True)
        st.image(get_img(st.session_state.enemy['id']), width=180)
        st.subheader(f"WILD {st.session_state.enemy['name']}")
        st.progress(max(0, st.session_state.enemy['hp']) / 100)
        st.markdown("</div>", unsafe_allow_html=True)

    st.write("---")
    m_cols = st.columns(2)
    moves = list(st.session_state.player['moves'].items())
    for i, (m_name, m_pwr) in enumerate(moves):
        if m_cols[i%2].button(m_name, use_container_width=True):
            mult = TYPE_CHART.get(st.session_state.player['type'], {}).get(st.session_state.enemy['type'], 1.0)
            st.session_state.enemy['hp'] -= int(m_pwr * mult)
            if st.session_state.enemy['hp'] > 0:
                st.session_state.player['hp'] -= random.randint(12, 18)
            if st.session_state.player['hp'] <= 0 or st.session_state.enemy['hp'] <= 0:
                st.session_state.phase = "result"
            st.rerun()

elif st.session_state.phase == "result":
    st.markdown("<div class='poke-card'>", unsafe_allow_html=True)
    if st.session_state.player['hp'] > 0:
        st.balloons()
        st.header("🏆 MISSION SUCCESSFUL")
        st.session_state.total_wins += 1
        save_data(st.session_state.total_wins)
    else:
        st.header("💀 HHAA YOU LOSE 😂")
    
    if st.button("REBOOT ADVENTURE"):
        st.session_state.update({"phase": "setup", "logs": []})
        st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)
