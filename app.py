import streamlit as st
import random
import requests

TYPE_CHART = {
    "Fire": {"Grass": 2.0, "Water": 0.5, "Fire": 0.5},
    "Water": {"Fire": 2.0, "Grass": 0.5, "Water": 0.5},
    "Grass": {"Water": 2.0, "Fire": 0.5, "Grass": 0.5},
    "Normal": {"Fire": 1.0, "Water": 1.0, "Grass": 1.0}
}

DATA = {
    "Kanto": {
        "Bulbasaur": {"id": 1, "type": "Grass", "hp": 100, "moves": {"Tackle": 15, "Vine Whip": 25}},
        "Charmander": {"id": 4, "type": "Fire", "hp": 100, "moves": {"Scratch": 15, "Ember": 25}},
        "Squirtle": {"id": 7, "type": "Water", "hp": 100, "moves": {"Tackle": 15, "Water Gun": 25}},
    },
    "Hoenn": {
        "Treecko": {"id": 252, "type": "Grass", "hp": 100, "moves": {"Pound": 15, "Absorb": 25}},
        "Torchic": {"id": 255, "type": "Fire", "hp": 100, "moves": {"Scratch": 15, "Ember": 25}},
        "Mudkip": {"id": 258, "type": "Water", "hp": 100, "moves": {"Tackle": 15, "Water Gun": 25}},
    }
}

st.set_page_config(page_title="PokeStream Battle Pro", layout="centered")

def apply_styles():
    st.markdown("""
        <style>
        .stApp {
            background: linear-gradient(rgba(0,0,0,0.6), rgba(0,0,0,0.6)), 
                        url("https://images.unsplash.com/photo-1613771404721-1f92d799e49f?q=80&w=2069");
            background-size: cover;
        }
        .poke-card {
            background-color: rgba(255, 255, 255, 0.9);
            padding: 20px;
            border-radius: 15px;
            border: 4px solid #3b4cca;
            text-align: center;
        }
        .log-box {
            background-color: #222;
            color: #00FF00;
            font-family: 'Courier New', monospace;
            padding: 10px;
            border-radius: 5px;
        }
        </style>
    """, unsafe_allow_html=True)

apply_styles()

def get_img(poke_id):
    return f"https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/{poke_id}.png"

# --- GAME ENGINE ---
if 'state' not in st.session_state:
    st.session_state.update({"phase": "setup", "logs": []})

def add_log(msg): st.session_state.logs.append(msg)

def calculate_damage(move_type, defender_type, base_power):
    multiplier = TYPE_CHART.get(move_type, {}).get(defender_type, 1.0)
    variance = random.randint(-3, 3)
    total = int(base_power * multiplier) + variance
    return total, multiplier

if st.session_state.phase == "setup":
    st.title("🔴 Pokémon Battle Arena")
    region = st.radio("Choose Region", list(DATA.keys()), horizontal=True)
    
    cols = st.columns(3)
    for i, (name, d) in enumerate(DATA[region].items()):
        with cols[i]:
            st.image(get_img(d['id']))
            if st.button(f"Go, {name}!", key=name):
                st.session_state.player = {"name": name, "hp": 100, "type": d['type'], "id": d['id'], "moves": d['moves']}
                opp_name, opp_d = random.choice(list(DATA[region].items()))
                st.session_state.enemy = {"name": opp_name, "hp": 100, "type": opp_d['type'], "id": opp_d['id'], "moves": opp_d['moves']}
                st.session_state.phase = "battle"
                st.rerun()

elif st.session_state.phase == "battle":
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown(f"<div class='poke-card'><h3>{st.session_state.player['name']}</h3>", unsafe_allow_html=True)
        st.image(get_img(st.session_state.player['id']), width=200)
        st.progress(st.session_state.player['hp']/100)
        st.write(f"HP: {st.session_state.player['hp']}/100")
        st.markdown("</div>", unsafe_allow_html=True)

    with col2:
        st.markdown(f"<div class='poke-card'><h3>Wild {st.session_state.enemy['name']}</h3>", unsafe_allow_html=True)
        st.image(get_img(st.session_state.enemy['id']), width=200)
        st.progress(st.session_state.enemy['hp']/100)
        st.write(f"HP: {st.session_state.enemy['hp']}/100")
        st.markdown("</div>", unsafe_allow_html=True)

    st.subheader("Select Move")
    m_cols = st.columns(2)
    moves = list(st.session_state.player['moves'].items())
    for i, (m_name, m_power) in enumerate(moves):
        if m_cols[i % 2].button(m_name, use_container_width=True):
            dmg, mult = calculate_damage(st.session_state.player['type'], st.session_state.enemy['type'], m_power)
            st.session_state.enemy['hp'] = max(0, st.session_state.enemy['hp'] - dmg)
            effect_msg = "It's super effective!" if mult > 1 else ("It's not very effective..." if mult < 1 else "")
            add_log(f"⭐ {st.session_state.player['name']} used {m_name}! {effect_msg} (-{dmg} HP)")

            if st.session_state.enemy['hp'] > 0:
                e_move = random.choice(list(st.session_state.enemy['moves'].keys()))
                e_power = st.session_state.enemy['moves'][e_move]
                e_dmg, e_mult = calculate_damage(st.session_state.enemy['type'], st.session_state.player['type'], e_power)
                st.session_state.player['hp'] = max(0, st.session_state.player['hp'] - e_dmg)
                add_log(f"👺 Enemy {st.session_state.enemy['name']} used {e_move}! (-{e_dmg} HP)")
            
            if st.session_state.player['hp'] <= 0 or st.session_state.enemy['hp'] <= 0:
                st.session_state.phase = "end"
            st.rerun()

    with st.expander("Battle Logs", expanded=True):
        for log in reversed(st.session_state.logs):
            st.markdown(f"<div class='log-box'>{log}</div>", unsafe_allow_html=True)

elif st.session_state.phase == "end":
    if st.session_state.player['hp'] > 0:
        st.balloons()
        st.success("YOU WON!")
    else:
        st.error("YOU FAINTED!")
    if st.button("Rematch?"):
        st.session_state.clear()
        st.session_state.update({"phase": "setup", "logs": []})
        st.rerun()