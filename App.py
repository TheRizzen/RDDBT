import streamlit as st

# Configuration pour que ça ressemble à une appli mobile
st.set_page_config(page_title="DiagBT Expert", layout="centered")

st.title("⚡ Assistant Diagnostic BT")
st.write("Saisissez vos relevés pour obtenir la marche à suivre.")

# --- 1. SAISIE DES MESURES (Vide par défaut) ---
st.header("1️⃣ Relevés Terrain")

col1, col2 = st.columns(2)
with col1:
    l1n_cont = st.number_input("Continuité L1/N (Ω)", value=None, placeholder="Ex: 0.7")
    l1l2_cont = st.number_input("Continuité L1/L2 (Ω)", value=None, placeholder="Ex: 1.2")
with col2:
    iso_min = st.number_input("Isolement mini (MΩ)", value=None, placeholder="Ex: 2.3")
    nt_iso = st.number_input("Isolement N/T (MΩ)", value=None, placeholder="Ex: 3.8")

dielec = st.selectbox("Résultat Diélectrique", ["N.R", "Pas d'amorçage", "Amorçage", "Pas de montée"])
tension = st.text_input("Tension d'amorçage", placeholder="Ex: 1.5 kV")

# --- 2. LOGIQUE ET TUTOS ---
if st.button("🚀 GÉNÉRER LE DIAGNOSTIC ET LE TUTO"):
    st.divider()
    
    # CAS : ÉCLATEUR (Basé sur ton doc Test 6)
    if dielec == "Amorçage":
        st.error("### RÉSULTAT : DÉFAUT ÉCLATEUR")
        st.info("📖 **TUTO DE BRANCHEMENT (EZ-THUMP)**")
        st.markdown(f"""
        **Analyse :** Le défaut est invisible à basse tension mais "claque" à {tension}.
        
        **Marche à suivre :**
        1. **Branchement :** Relier le câble HT (Rouge) sur la phase en défaut et le retour (Bleu) sur le Neutre.
        2. **Sécurité :** Vérifier la terre de sécurité (Contrôle F-ohm).
        3. **Prélocalisation :** Utiliser le mode **ARM** (Réflexion sur Arc).
        4. **Localisation :** Utiliser le micro de sol (Choc acoustique).
        """)
        # Ici on insère le schéma de branchement
        st.image("https://raw.githubusercontent.com/votre-compte/votre-app/main/tuto_ez.png", caption="Schéma de branchement pour localisation d'un éclat")

    # CAS : RUPTURE (Basé sur ton doc Test 3)
    elif l1n_cont is not None and l1n_cont > 100:
        st.error("### RÉSULTAT : CONDUCTEUR ROMPU")
        st.info("📖 **TUTO PRÉLOCALISATION**")
        st.markdown("""
        **Marche à suivre :**
        1. **Échométrie :** Utiliser le mode direct.
        2. **Signal :** Rechercher une réflexion positive (le trait monte).
        3. **Localisation :** Si pas d'amorçage, utiliser le RD8000 pour suivre le câble jusqu'à la perte du signal.
        """)

    # CAS : DÉFAUT FRANC (Basé sur ton doc Test 5)
    elif iso_min is not None and iso_min < 0.1:
        st.error("### RÉSULTAT : DÉFAUT FRANC")
        st.info("📖 **TUTO LOCALISATION**")
        st.markdown("""
        **Attention :** Le choc sera silencieux (pas d'arc possible).
        **Action :** Utiliser le générateur de signal et le **RD8000** en mode "Fréquences Audibles".
        """)
