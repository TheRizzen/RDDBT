import streamlit as st

st.set_page_config(page_title="DiagBT - Expert", layout="wide")

st.title("⚡ Diagnostic Expert Réseau BT")
st.write("Saisissez l'intégralité des mesures relevées sur le terrain.")

# Fonction utilitaire pour convertir les unités
def to_ohms(val, unit):
    if unit == "GΩ": return val * 1_000_000_000
    if unit == "MΩ": return val * 1_000_000
    if unit == "kΩ": return val * 1_000
    return val

# --- SECTION 1 : CONTINUITÉ ---
st.header("1️⃣ Test de Continuité (Bouclage)")
c1, c2, c3 = st.columns(3)
with c1:
    l1n_c = st.number_input("L1 / N (Ω)", value=0.0, step=0.1, key="l1nc")
    l1l2_c = st.number_input("L1 / L2 (Ω)", value=0.0, step=0.1, key="l1l2c")
with c2:
    l2n_c = st.number_input("L2 / N (Ω)", value=0.0, step=0.1, key="l2nc")
    l2l3_c = st.number_input("L2 / L3 (Ω)", value=0.0, step=0.1, key="l2l3c")
with c3:
    l3n_c = st.number_input("L3 / N (Ω)", value=0.0, step=0.1, key="l3nc")
    l3l1_c = st.number_input("L3 / L1 (Ω)", value=0.0, step=0.1, key="l3l1c")

st.divider()

# --- SECTION 2 : ISOLEMENT ET DIÉLECTRIQUE (TABLEAU) ---
st.header("2️⃣ Isolement & Test Diélectrique")

labels = ["L1/N", "L2/N", "L3/N", "L1/L2", "L2/L3", "L3/L1", "L1/T", "L2/T", "L3/T", "N/T"]
data = {}

# Création d'une ligne par mesure pour une précision totale
for label in labels:
    col1, col2, col3, col4 = st.columns([2, 1, 2, 2])
    with col1:
        val = st.number_input(f"Isolement {label}", value=0.0, key=f"val_{label}")
    with col2:
        unit = st.selectbox(f"Unité", ["MΩ", "GΩ", "kΩ", "Ω"], key=f"unit_{label}")
    with col3:
        dielec = st.selectbox(f"Diélectrique {label}", ["N.R", "Amorçage", "Pas d'amorçage", "Pas de montée en tension"], key=f"die_{label}")
    with col4:
        tension = st.text_input(f"Tension d'amorçage (V/kV)", key=f"tens_{label}", placeholder="Ex: 1.5 kV")
    
    data[label] = {
        "ohms": to_ohms(val, unit),
        "dielec": dielec,
        "label": label
    }

# --- LOGIQUE DE DIAGNOSTIC ---
if st.button("🚀 GÉNÉRER LE DIAGNOSTIC TECHNIQUE"):
    
    # 1. Analyse Rupture (Tests 3 & 4)
    # On identifie les conducteurs coupés (> 1999 Ohms)
    ruptures = []
    if l1n_c > 1999: ruptures.append("L1")
    if l2n_c > 1999: ruptures.append("L2")
    if l3n_c > 1999: ruptures.append("L3")
    rupture_neutre = all(v > 1999 for v in [l1n_c, l2n_c, l3n_c])

    # 2. Identification du défaut d'isolement (le plus bas, hors N/T)
    iso_mesures = {k: v for k, v in data.items() if k != "N/T"}
    pire_couple = min(iso_mesures, key=lambda k: iso_mesures[k]["ohms"])
    val_pire = iso_mesures[pire_couple]["ohms"]
    statut_dielec = data[pire_couple]["dielec"]

    st.divider()
    st.subheader("📋 Rapport de Préconisation")

    # CAS A : Rupture de Neutre (Sécurité absolue)
    if rupture_neutre:
        st.error("🚨 DÉFAUT : RUPTURE DE NEUTRE")
        st.warning("⚠️ MODE CHOC INTERDIT : Risque de destruction des équipements clients (survoltage).")
        st.info("🛠️ ACTION : Localisation par Échométrie comparative uniquement.")

    # CAS B : Rupture de Phase (Test 4)
    elif len(ruptures) > 0:
        st.error(f"🚨 DÉFAUT : RUPTURE DE CONDUCTEUR ({', '.join(ruptures)})")
        if statut_dielec == "Amorçage":
            st.success("✅ Amorçage détecté : Le conducteur rompu touche le neutre périphérique. CHOC POSSIBLE AVEC BOUCLAGE.")
        st.info("🛠️ ACTION : Échométrie directe pour trouver la cassure.")

    # CAS C : Défaut Franc (Test 1 & 5)
    elif val_pire <= 10:
        st.error(f"🚨 DÉFAUT : COURT-CIRCUIT FRANC sur {pire_couple} ({val_pire} Ω)")
        st.warning("⚠️ CHOC INEFFICACE : Pas d'arc électrique (défaut métallique).")
        st.info("🛠️ ACTION : Localisation au RD8000 (Fréquences audibles).")

    # CAS D : Défaut Résistant / Éclateur (Test 2 & 6)
    else:
        st.error(f"🚨 DÉFAUT : ISOLEMENT RÉSISTANT sur {pire_couple}")
        if statut_dielec == "Amorçage":
            st.success("✅ MÉTHODE : Réflexion sur Arc (ARM) + Ondes de Choc (Le défaut claque).")
        else:
            st.info("🛠️ MÉTHODE : Échométrie directe (si < 150Ω) ou recherche d'amorçage à plus haute tension.")
