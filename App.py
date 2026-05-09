import streamlit as st

st.set_page_config(page_title="DiagBT - Expert Réseau", layout="wide")

st.title("⚡ Diagnostic Expert Réseau BT")
st.write("Saisissez les mesures relevées. Les cases sont vides par défaut pour une saisie rapide.")

# Fonction de conversion pour l'isolement
def to_ohms(val, unit):
    if val is None: return None
    if unit == "GΩ": return val * 1_000_000_000
    if unit == "MΩ": return val * 1_000_000
    if unit == "kΩ": return val * 1_000
    return val

# --- SECTION 1 : CONTINUITÉ ---
st.header("1️⃣ Test de Continuité (Bouclage)")
st.info("Indiquez si la boucle est passante (Ω) ou coupée (Infinie).")

c_labels = ["L1/N", "L2/N", "L3/N", "L1/L2", "L2/L3", "L3/L1"]
cont_data = {}

cols = st.columns(3)
for i, label in enumerate(c_labels):
    with cols[i % 3]:
        choice = st.radio(f"État {label}", ["Valeur (Ω)", "Infinie"], key=f"choice_{label}", horizontal=True)
        if choice == "Valeur (Ω)":
            val_c = st.number_input(f"Résistance {label}", value=None, format="%.2f", key=f"val_c_{label}", placeholder="Tapez...")
            cont_data[label] = val_c if val_c is not None else 0.0
        else:
            cont_data[label] = float('inf')

st.divider()

# --- SECTION 2 : ISOLEMENT (Toutes mesures) ---
st.header("2️⃣ Mesures d'Isolement (Mégohmmètre)")
# On garde toutes les mesures pour l'isolement car il est important de savoir si une phase fuit à la terre
labels_iso = ["L1/N", "L2/N", "L3/N", "L1/L2", "L2/L3", "L3/L1", "L1/T", "L2/T", "L3/T", "N/T"]
iso_results = {}

for label in labels_iso:
    col1, col2 = st.columns([3, 1])
    with col1:
        v = st.number_input(f"Isolement {label}", value=None, key=f"iso_v_{label}", placeholder="Valeur...")
    with col2:
        u = st.selectbox(f"Unité {label}", ["MΩ", "GΩ", "kΩ", "Ω"], key=f"iso_u_{label}")
    iso_results[label] = to_ohms(v, u) if v is not None else 1_000_000_000_000

st.divider()

# --- SECTION 3 : TEST DIÉLECTRIQUE (Uniquement Ph/N et Ph/Ph) ---
st.header("3️⃣ Test Diélectrique (3Uo)")
st.info("Note : Les tests vers la terre sont exclus de cette section.")
labels_dielec = ["L1/N", "L2/N", "L3/N", "L1/L2", "L2/L3", "L3/L1"]
dielec_results = {}

for label in labels_dielec:
    col_d1, col_d2 = st.columns([2, 2])
    with col_d1:
        s = st.selectbox(f"Résultat Diélectrique {label}", 
                         ["N.R", "Pas d'amorçage", "Amorçage", "Pas de montée en tension"], 
                         key=f"die_s_{label}")
    with col_d2:
        t = st.text_input(f"Tension {label}", key=f"die_t_{label}", placeholder="Ex: 1.2 kV")
    dielec_results[label] = s

# --- LOGIQUE DE DIAGNOSTIC ---
st.divider()
if st.button("🚀 LANCER L'ANALYSE TECHNIQUE"):
    
    # Détection des ruptures
    rupture_neutre = cont_data["L1/N"] == float('inf') and cont_data["L2/N"] == float('inf') and cont_data["L3/N"] == float('inf')
    
    # Analyse isolement (hors N/T)
    iso_filtre = {k: v for k, v in iso_results.items() if k != "N/T"}
    pire_couple = min(iso_filtre, key=iso_filtre.get)
    val_pire = iso_filtre[pire_couple]
    # On vérifie si on a une info diélectrique pour ce couple (sinon N.R)
    statut_dielec = dielec_results.get(pire_couple, "N.R")

    st.subheader("📋 Rapport de Préconisation")

    if rupture_neutre:
        st.error("🚨 DÉFAUT : RUPTURE DE NEUTRE")
        st.warning("⚠️ MODE CHOC INTERDIT : Sécurité absolue des abonnés.")
    elif any(v == float('inf') for v in cont_data.values()):
        st.error("🚨 DÉFAUT : RUPTURE DE CONDUCTEUR")
        if statut_dielec == "Amorçage":
            st.success("✅ Amorçage détecté : CHOC POSSIBLE AVEC BOUCLAGE.")
    elif val_pire <= 10:
        st.error(f"🚨 DÉFAUT : COURT-CIRCUIT FRANC ({pire_couple})")
        st.warning("⚠️ CHOC INEFFICACE : Pas d'arc (contact métallique).")
        st.info("🛠️ MÉTHODE : RD8000 (Fréquences Audibles).")
    else:
        st.error(f"🚨 DÉFAUT : ISOLEMENT RÉSISTANT ({pire_couple})")
        if statut_dielec == "Amorçage":
            st.success("✅ STRATÉGIE : ARM + Ondes de Choc.")
        else:
            st.info("🛠️ STRATÉGIE : Échométrie directe (si < 150Ω) ou test diélectrique plus poussé.")
