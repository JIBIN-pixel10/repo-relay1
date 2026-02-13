import streamlit as st
import random
import json
import os
import copy

# -------------------- PERSISTENCE --------------------
SAVE_FILE = "trainer_data.json"

def load_data():
    if os.path.exists(SAVE_FILE):
        try:
            with open(SAVE_FILE, "r") as f:
                return json.load(f)
        except:
            return {"total_wins": 0}
    return {"total_wins": 0}

def save_data(wins):
    with open(SAVE_FILE, "w") as f:
        json.dump({"total_wins": wins}, f)

# -------------------- TYPE SYSTEM --------------------
TYPE_CHART = {
    "Fire": {"Grass": 2.0, "Water": 0.5, "Fire": 0.5},
    "Water": {"Fire": 2.0, "Grass": 0.5, "Water": 0.5},
    "Grass": {"Water": 2.0, "Fire": 0.5, "Grass": 0.5}
}

BASE_HP = 100

# -------------------- ALL REGIONS --------------------
REGIONS = {
    "Kanto": {
        "Bulbasaur": {"id": 1, "type": "Grass", "moves": {"Tackle": 15, "Vine Whip": 25}},
        "Charmander": {"id": 4, "type": "Fire", "moves": {"Scratch": 15, "Ember": 25}},
        "Squirtle": {"id": 7, "type": "Water", "moves": {"Tackle": 15, "Water Gun": 25}},
    },
    "Johto": {
        "Chikorita": {"id": 152, "type": "Grass", "moves": {"Tackle": 15, "Razor Leaf": 25}},
        "Cyndaquil": {"id": 155, "type": "Fire", "moves": {"Tackle": 15, "Flame Wheel": 25}},
        "Totodile": {"id": 158, "type": "Water", "moves": {"Scratch": 15, "Water Gun": 25}},
    },
    "Hoenn": {
        "Treecko": {"id": 252, "type": "Grass", "moves": {"Pound": 15, "Absorb": 28}},
        "Torchic": {"id": 255, "type": "Fire", "moves": {"Scratch": 15, "Ember": 28}},
        "Mudkip": {"id": 258, "type": "Water", "moves": {"Tackle": 15, "Water Gun": 28}},
    },
    "Sinnoh": {
        "Turtwig": {"id": 387, "type": "Grass", "moves": {"Tackle": 15, "Razor Leaf": 25}},
        "Chimchar": {"id": 390, "type": "Fire", "moves": {"Scratch": 15, "Ember": 25}},
        "Piplup": {"id": 393, "type": "Water", "moves": {"Pound": 15, "Water Gun": 25}},
    },
    "Unova": {
        "Snivy": {"id": 495, "type": "Grass", "moves": {"Tackle": 15, "Leaf Tornado": 25}},
        "Tepig": {"id": 498, "type": "Fire", "moves": {"Tackle": 15, "Ember": 25}},
        "Oshawott": {"id": 501, "type": "Water", "moves": {"Tackle": 15, "Water Gun": 25}},
    },
    "Kalos": {
        "Chespin": {"id": 650, "type": "Grass", "moves": {"Vine Whip": 20, "Seed Bomb": 28}},
        "Fennekin": {"id": 653, "type": "Fire", "moves": {"Scratch": 15, "Psybeam": 25}},
        "Froakie": {"id": 656, "type": "Water", "moves": {"Pound": 15, "Water Pulse": 25}},
    },
    "Alola": {
        "Rowlet": {"id": 722, "type": "Grass", "moves": {"Leafage": 20, "Astonish": 25}},
        "Litten": {"id": 725, "type": "Fire", "moves": {"Scratch": 15, "Fire Fang": 28}},
        "Popplio": {"id": 728, "type": "Water", "moves": {"Pound": 15, "Bubble Beam": 28}},
    }
}

# -------------------- PAGE CONFIG --------------------
st.set_page_config(page_title="NEON POKESTREAM", layout="wide")

st.markdown("""
<style>
.stApp {
    background: linear-gradient(rgba(0,0,0,0.85), rgba(0,0,0,0.85)),
                url("https://images.unsplash.com/photo-1614850523296-d8c1af93d400?q=80&w=2070");
    background-size: cover;
    color: #0ff;
}

.stButton>button {
    background: transparent;
    color: #0ff;
    border: 2px solid #0ff;
    border-radius: 10px;
    box-shadow: 0 0 10px #0ff;
    font-weight: bold;
}

.stButton>button:hover {
    background: #0ff;
    color: black;
}

h1, h2, h3 {
    color: white !important;
    text-shadow: 0 0 10px #0ff;
}
</style>
""", unsafe_allow_html=True)

# -------------------- STATE INIT --------------------
if "phase" not in st.session_state:
    st.session_state.phase = "setup"
    st.session_state.total_wins = load_data()["total_wins"]
    st.session_state.player = None
    st.session_state.enemy = None

def get_img(pid):
    return f"https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/{pid}.png"

# ==================== SETUP ====================
if st.session_state.phase == "setup":

    st.title("⚡ NEON POKEMON SELECT")
    st.sidebar.metric("PERMANENT WINS", st.session_state.total_wins)

    region = st.selectbox("Choose Region", list(REGIONS.keys()))
    starters = REGIONS[region]

    cols = st.columns(3)

    for i, (name, data) in enumerate(starters.items()):
        with cols[i]:
            st.image(get_img(data["id"]), width=200)
            st.subheader(name)

            if st.button(f"SELECT {name}", key=name, use_container_width=True):

                player = copy.deepcopy(data)
                player["hp"] = BASE_HP
                player["name"] = name
                st.session_state.player = player

                all_starters = []
                for r in REGIONS.values():
                    all_starters.extend(list(r.items()))

                while True:
                    opp_name, opp_data = random.choice(all_starters)
                    if opp_name != name:
                        break

                enemy = copy.deepcopy(opp_data)
                enemy["hp"] = BASE_HP
                enemy["name"] = opp_name
                st.session_state.enemy = enemy

                st.session_state.phase = "battle"
                st.rerun()

# ==================== BATTLE ====================
elif st.session_state.phase == "battle":

    st.title("⚔️ CYBER BATTLE ARENA")

    col1, col2 = st.columns(2)

    with col1:
        st.image(get_img(st.session_state.player["id"]), width=220)
        st.subheader(st.session_state.player["name"])
        st.progress(max(st.session_state.player["hp"], 0) / BASE_HP)

    with col2:
        st.image(get_img(st.session_state.enemy["id"]), width=220)
        st.subheader(f"WILD {st.session_state.enemy['name']}")
        st.progress(max(st.session_state.enemy["hp"], 0) / BASE_HP)

    st.write("---")

    moves = list(st.session_state.player["moves"].items())
    move_cols = st.columns(2)

    for i, (move_name, power) in enumerate(moves):
        if move_cols[i % 2].button(move_name, use_container_width=True):

            multiplier = TYPE_CHART.get(
                st.session_state.player["type"], {}
            ).get(st.session_state.enemy["type"], 1.0)

            damage = int(power * multiplier)
            st.session_state.enemy["hp"] -= damage

            if st.session_state.enemy["hp"] > 0:
                st.session_state.player["hp"] -= random.randint(12, 18)

            if st.session_state.player["hp"] <= 0 or st.session_state.enemy["hp"] <= 0:
                st.session_state.phase = "result"

            st.rerun()

# ==================== RESULT ====================
elif st.session_state.phase == "result":

    if st.session_state.player["hp"] > 0:
        st.balloons()
        st.header("🏆 MISSION SUCCESSFUL")
        st.session_state.total_wins += 1
        save_data(st.session_state.total_wins)
    else:
        st.header("💀 SYSTEM FAILURE")

    if st.button("REBOOT ADVENTURE"):
        st.session_state.phase = "setup"
        st.session_state.player = None
        st.session_state.enemy = None
        st.rerun()
