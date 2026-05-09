import streamlit as st

st.set_page_config(page_title="DiagBT - Expert Réseau", layout="wide")

st.title("⚡ Diagnostic Expert Réseau BT")
st.write("Saisissez l'intégralité des mesures relevées sur le terrain.")

# Fonction de conversion pour l'isolement
def to_ohms(val, unit):
    if unit == "GΩ": return val * 1_000_000_000
    if unit == "MΩ": return val * 1_000_000
    if unit == "kΩ": return val * 1_000
    return val

# --- SECTION 1 : CONTINUITÉ ---
st.header("1️⃣ Test de Continuité (Bouclage)")
st.info("Indiquez si la boucle est passante (Valeur en Ω) ou coupée (Infinie).")

c_labels = ["L1/N", "L2/N", "L3/N", "L1/L2", "L2/L3", "L3/L1"]
cont_data = {}

cols = st.columns(3)
for i, label in enumerate(c_labels):
    with cols[i % 3]:
        choice = st.radio(f"État {label}", ["Valeur (Ω)", "Infinie"], key=f"choice_{label}", horizontal=True)
        if choice == "Valeur (Ω)":
            val = st.number_input(f"Résistance {label}", min_value=0.0, format="%.2f", key=f"val_c_{label}")
            cont_data[label] = val
        else:
            st.write(f"📈 {label} : **Coupé**")
            cont_data[label] = float('inf')

st.divider()

# --- SECTION 2 : ISOLEMENT ---
st.header("2️⃣ Mesures d'Isolement (Mégohmmètre)")
labels_iso = ["L1/N", "L2/N", "L3/N", "L1/L2", "L2/L3", "L3/L1", "L1/T", "L2/T", "L3/T", "N/T"]
iso_results = {}

for label in labels_iso:
    col1, col2 = st.columns([3, 1])
    with col1:
        v = st.number_input(f"Isolement {label}", value=0.0, key=f"iso_v_{label}")
    with col2:
        u = st.selectbox(f"Unité {label}", ["MΩ", "GΩ", "kΩ", "Ω"], key=f"iso_u_{label}")
    iso_results[label] = to_ohms(v, u)

st.divider()

# --- SECTION 3 : TEST DIÉLECTRIQUE ---
st.header("3️⃣ Test Diélectrique (3Uo)")
dielec_results = {}
for label in labels_iso:
    col_d1, col_d2 = st.columns([2, 2])
    with col_d1:
        s = st.selectbox(f"Résultat Diélectrique {label}", 
                         ["N.R", "Pas d'amorçage", "Amorçage", "Pas de montée en tension"], 
                         key=f"die_s_{label}")
    with col_d2:
        t = st.text_input(f"Tension {label}", key=f"die_t_{label}", placeholder="V ou kV")
    dielec_results[label] = s

# --- LOGIQUE DE DIAGNOSTIC ---
if st.button("🚀 LANCER L'ANALYSE TECHNIQUE"):
    
    # Détection des ruptures (Infinie)
    rupture_l1 = cont_data["L1/N"] == float('inf') and cont_data["L1/L2"] == float('inf') [cite: 15]
    rupture_l2 = cont_data["L2/N"] == float('inf') and cont_data["L2/L3"] == float('inf') [cite: 15]
    rupture_l3 = cont_data["L3/N"] == float('inf') and cont_data["L3/L1"] == float('inf') [cite: 15]
    rupture_neutre = cont_data["L1/N"] == float('inf') and cont_data["L2/N"] == float('inf') and cont_data["L3/N"] == float('inf') [cite: 31]
    
    # Identification du défaut d'isolement principal
    iso_filtre = {k: v for k, v in iso_results.items() if k != "N/T"}
    pire_couple = min(iso_filtre, key=iso_filtre.get)
    val_pire = iso_filtre[pire_couple]
    statut_dielec = dielec_results[pire_couple]

    st.divider()
    st.subheader("📋 Rapport de Préconisation")

    if rupture_neutre:
        st.error("🚨 DÉFAUT : RUPTURE DE NEUTRE")
        st.warning("⚠️ MODE CHOC INTERDIT : Risque de destruction des appareils clients.") [cite: 31]
        st.info("🛠️ STRATÉGIE : Échométrie comparative.") [cite: 31]

    elif rupture_l1 or rupture_l2 or rupture_l3:
        phases_coupees = []
        if rupture_l1: phases_coupees.append("L1")
        if rupture_l2: phases_coupees.append("L2")
        if rupture_l3: phases_coupees.append("L3")
        st.error(f"🚨 DÉFAUT : RUPTURE DE PHASE ({', '.join(phases_coupees)})") [cite: 15]
        if statut_dielec == "Amorçage":
            st.success("✅ Amorçage détecté : CHOC POSSIBLE AVEC BOUCLAGE (Neutre périphérique).") [cite: 15]
        st.info("🛠️ STRATÉGIE : Échométrie directe.") [cite: 15]

    elif val_pire <= 10:
        st.error(f"🚨 DÉFAUT : COURT-CIRCUIT FRANC sur {pire_couple} ({val_pire} Ω)") [cite: 49, 65]
        st.warning("⚠️ CHOC INEFFICACE : Pas d'arc électrique.") [cite: 49, 65]
        st.info("🛠️ STRATÉGIE : RD8000 (Fréquences Audibles).") [cite: 49, 65]

    else:
        st.error(f"🚨 DÉFAUT : ISOLEMENT RÉSISTANT sur {pire_couple}") [cite: 49, 65, 66]
        if statut_dielec == "Amorçage":
            st.success("✅ STRATÉGIE : Réflexion sur Arc (ARM) + Ondes de Choc.") [cite: 66]
        else:
            st.info("🛠️ STRATÉGIE : Échométrie directe (si < 150Ω) ou Diélectrique plus élevé.")
