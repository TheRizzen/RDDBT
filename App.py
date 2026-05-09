import streamlit as st

st.set_page_config(page_title="DiagBT - Expert Réseau", layout="wide")

st.title("⚡ Diagnostic Expert Réseau BT")
st.write("Saisissez l'intégralité des mesures relevées sur le terrain étape par étape.")

# Fonction de conversion
def to_ohms(val, unit):
    if unit == "GΩ": return val * 1_000_000_000
    if unit == "MΩ": return val * 1_000_000
    if unit == "kΩ": return val * 1_000
    return val

# --- SECTION 1 : CONTINUITÉ ---
st.header("1️⃣ Test de Continuité (Bouclage)")
st.info("Relevez les valeurs de bouclage en extrémité de câble.")
c1, c2, c3 = st.columns(3)
with c1:
    l1n_c = st.number_input("L1 / N (Ω)", value=0.0, format="%.2f", key="l1nc")
    l1l2_c = st.number_input("L1 / L2 (Ω)", value=0.0, format="%.2f", key="l1l2c")
with c2:
    l2n_c = st.number_input("L2 / N (Ω)", value=0.0, format="%.2f", key="l2nc")
    l2l3_c = st.number_input("L2 / L3 (Ω)", value=0.0, format="%.2f", key="l2l3c")
with c3:
    l3n_c = st.number_input("L3 / N (Ω)", value=0.0, format="%.2f", key="l3nc")
    l3l1_c = st.number_input("L3 / L1 (Ω)", value=0.0, format="%.2f", key="l3l1c")

st.divider()

# --- SECTION 2 : ISOLEMENT ---
st.header("2️⃣ Mesures d'Isolement (Mégohmmètre)")
st.write("Saisissez les valeurs et choisissez l'unité pour chaque couple.")

labels = ["L1/N", "L2/N", "L3/N", "L1/L2", "L2/L3", "L3/L1", "L1/T", "L2/T", "L3/T", "N/T"]
iso_data = {}

# Création du tableau d'isolement
for label in labels:
    col1, col2 = st.columns([3, 1])
    with col1:
        val = st.number_input(f"Valeur Isolement {label}", value=0.0, key=f"iso_val_{label}")
    with col2:
        unit = st.selectbox(f"Unité {label}", ["MΩ", "GΩ", "kΩ", "Ω"], key=f"iso_unit_{label}")
    iso_data[label] = to_ohms(val, unit)

st.divider()

# --- SECTION 3 : TEST DIÉLECTRIQUE ---
st.header("3️⃣ Test Diélectrique (3Uo)")
st.write("Précisez le comportement sous tension pour chaque couple.")

dielec_data = {}
for label in labels:
    col_d1, col_d2 = st.columns([2, 2])
    with col_d1:
        statut = st.selectbox(f"Résultat Diélectrique {label}", 
                              ["N.R", "Pas d'amorçage", "Amorçage", "Pas de montée en tension"], 
                              key=f"die_stat_{label}")
    with col_d2:
        tension = st.text_input(f"Tension relevée pour {label} (V ou kV)", key=f"die_tens_{label}")
    dielec_data[label] = statut

# --- LOGIQUE DE DIAGNOSTIC ---
if st.button("🚀 LANCER L'ANALYSE TECHNIQUE"):
    
    # 1. Analyse des Ruptures (Logiciel basé sur Test 3 & 4)
    ruptures = []
    if l1n_c > 1999: ruptures.append("L1")
    if l2n_c > 1999: ruptures.append("L2")
    if l3n_c > 1999: ruptures.append("L3")
    rupture_neutre = all(v > 1999 for v in [l1n_c, l2n_c, l3n_c])

    # 2. Identification du défaut d'isolement principal (hors N/T)
    # On cherche la valeur la plus basse
    iso_filtre = {k: v for k, v in iso_data.items() if k != "N/T"}
    pire_couple = min(iso_filtre, key=iso_filtre.get)
    val_pire = iso_filtre[pire_couple]
    statut_dielec_pire = dielec_data[pire_couple]

    st.divider()
    st.subheader("📋 Rapport de Diagnostic Final")

    # CAS 1 : Rupture de Neutre (Sécurité)
    if rupture_neutre:
        st.error("🚨 DÉFAUT CRITIQUE : RUPTURE DE NEUTRE")
        st.warning("⚠️ MODE CHOC INTERDIT : Risque de surtension grave pour les abonnés.")
        st.info("🛠️ STRATÉGIE : Échométrie comparative (Tracé Phase vs Tracé Neutre).")

    # CAS 2 : Rupture de Phase (Test 4)
    elif len(ruptures) > 0:
        st.error(f"🚨 DÉFAUT : CONDUCTEUR(S) ROMPU(S) : {', '.join(ruptures)}")
        if statut_dielec_pire == "Amorçage":
            st.success("✅ Amorçage détecté (Neutre périphérique) : CHOC ACOUSTIQUE POSSIBLE AVEC BOUCLAGE.")
        st.info("🛠️ STRATÉGIE : Échométrie directe pour localiser l'interruption.")

    # CAS 3 : Court-Circuit Franc (Test 1 & 5)
    elif val_pire <= 10:
        st.error(f"🚨 DÉFAUT : COURT-CIRCUIT FRANC sur {pire_couple} ({val_pire} Ω)")
        st.warning("⚠️ CHOC INEFFICACE : Pas d'arc au point de défaut (contact métallique).")
        st.info("🛠️ STRATÉGIE : Localisation par Fréquences Audibles (RD8000).")

    # CAS 4 : Défaut Résistant / Éclateur (Test 2 & 6)
    else:
        st.error(f"🚨 DÉFAUT : ISOLEMENT RÉSISTANT sur {pire_couple}")
        if statut_dielec_pire == "Amorçage":
            st.success("✅ STRATÉGIE : Réflexion sur Arc (ARM) + Ondes de Choc.")
        else:
            st.info("🛠️ STRATÉGIE : Échométrie directe (si < 150Ω) ou augmenter la tension d'essai.")
