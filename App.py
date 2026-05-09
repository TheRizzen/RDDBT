import streamlit as st

st.set_page_config(page_title="DiagBT - Aide à la recherche de défauts", layout="centered")

st.title("⚡ Assistant de Diagnostic Défaut BT")
st.write("Saisissez les relevés de mesure pour obtenir la stratégie de localisation.")

# --- SECTION 1 : CONTINUITÉ ---
st.header("1. Test de Continuité (Bouclage)")
col1, col2, col3 = st.columns(3)
with col1:
    l1n = st.number_input("L1/N (Ω)", min_value=0.0, format="%.2f")
    l1l2 = st.number_input("L1/L2 (Ω)", min_value=0.0, format="%.2f")
with col2:
    l2n = st.number_input("L2/N (Ω)", min_value=0.0, format="%.2f")
    l2l3 = st.number_input("L2/L3 (Ω)", min_value=0.0, format="%.2f")
with col3:
    l3n = st.number_input("L3/N (Ω)", min_value=0.0, format="%.2f")
    l3l1 = st.number_input("L3/L1 (Ω)", min_value=0.0, format="%.2f")

# --- SECTION 2 : ISOLEMENT ---
st.header("2. Mesure d'Isolement")
iso_val = st.number_input("Valeur du défaut relevée (Ω ou MΩ)", min_value=0.0)
unit = st.selectbox("Unité", ["Ω", "kΩ", "MΩ", "GΩ"])

# Conversion en Ohms pour la logique
rd = iso_val
if unit == "kΩ": rd *= 1000
elif unit == "MΩ": rd *= 1000000
elif unit == "GΩ": rd *= 1000000000

couple = st.selectbox("Couple en défaut", ["L1/N", "L2/N", "L3/N", "L1/L2", "L2/L3", "L3/L1", "N/Terre"])

# --- SECTION 3 : DIÉLECTRIQUE ---
st.header("3. Test Diélectrique")
dielec = st.radio("Résultat du test :", ["Pas d'amorçage", "Amorçage", "Pas de montée en tension"])

# --- LOGIQUE DE DIAGNOSTIC ---
st.divider()
if st.button("Générer le Diagnostic"):
    
    rupture_neutre = all(v > 1999 for v in [l1n, l2n, l3n])
    rupture_phase = any(v > 1999 for v in [l1l2, l2l3, l3l1])
    
    st.subheader("📋 Résultat du Diagnostic")

    # CAS 1 : RUPTURE DE NEUTRE (Test 3)
    if rupture_neutre:
        st.error("🚨 DÉFAUT : RUPTURE DE NEUTRE")
        st.warning("⚠️ MODE CHOC INTERDIT (Risque de surtension clients).")
        st.info("🛠️ MÉTHODE : Échométrie comparative + Suivi de tracé au RD8000.")

    # CAS 2 : RUPTURE DE PHASE (Test 4)
    elif rupture_phase:
        st.error(f"🚨 DÉFAUT : RUPTURE DE CONDUCTEUR ({couple})")
        if dielec == "Amorçage":
            st.success("✅ Amorçage détecté (Neutre périphérique) : Choc possible avec BOUCLAGE en extrémité.")
        st.info("🛠️ MÉTHODE : Échométrie directe (Localisation de la coupure).")

    # CAS 3 : DÉFAUT FRANC (Test 1 & 5)
    elif rd <= 10:
        st.error(f"🚨 DÉFAUT : COURT-CIRCUIT FRANC ({couple})")
        st.warning("⚠️ CHOC INEFFICACE (Pas d'assemblage).")
        st.info("🛠️ MÉTHODE : Échométrie directe + Fréquences audibles (RD8000).")

    # CAS 4 : DÉFAUT RÉSISTANT / ÉCLATEUR (Test 2 & 6)
    else:
        st.error(f"🚨 DÉFAUT : ISOLEMENT RÉSISTANT ({couple})")
        if dielec == "Amorçage":
            st.success("✅ MÉTHODE : Réflexion sur Arc (ARM) + Ondes de Choc.")
        else:
            st.info("🛠️ MÉTHODE : Échométrie directe (si Rd < 150Ω) ou Brûlage.")