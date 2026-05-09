import streamlit as st

st.set_page_config(page_title="DiagBT - Expert Terrain", layout="wide")

st.title("⚡ Diagnostic de Défaut Réseau BT")
st.write("Saisissez l'intégralité des relevés de la fiche de mesure.")

# --- SECTION 1 : CONTINUITÉ (BOUCLAGE) ---
st.header("1️⃣ Test de Continuité (Bouclage en extrémité)")
c1, c2, c3 = st.columns(3)
with c1:
    l1n_c = st.number_input("L1 / N (Ω)", key="l1nc", format="%.2f")
    l1l2_c = st.number_input("L1 / L2 (Ω)", key="l1l2c", format="%.2f")
with c2:
    l2n_c = st.number_input("L2 / N (Ω)", key="l2nc", format="%.2f")
    l2l3_c = st.number_input("L2 / L3 (Ω)", key="l2l3c", format="%.2f")
with c3:
    l3n_c = st.number_input("L3 / N (Ω)", key="l3nc", format="%.2f")
    l3l1_c = st.number_input("L3 / L1 (Ω)", key="l3l1c", format="%.2f")

# --- SECTION 2 : ISOLEMENT (MÉGOHMMÈTRE) ---
st.header("2️⃣ Mesures d'Isolement")
st.info("Saisissez les valeurs (ex: 4.8). L'unité par défaut est le MΩ.")

col_iso1, col_iso2, col_iso3 = st.columns(3)
with col_iso1:
    l1n_i = st.number_input("L1 / N", key="l1ni")
    l1t_i = st.number_input("L1 / Terre", key="l1ti")
    nt_i = st.number_input("N / Terre", key="nti", help="0 Ω est normal sur ce réseau")
with col_iso2:
    l2n_i = st.number_input("L2 / N", key="l2ni")
    l2t_i = st.number_input("L2 / Terre", key="l2ti")
    l1l2_i = st.number_input("L1 / L2", key="l1l2i")
with col_iso3:
    l3n_i = st.number_input("L3 / N", key="l3ni")
    l3t_i = st.number_input("L3 / Terre", key="l3ti")
    l2l3_i = st.number_input("L2 / L3", key="l2l3i")
    l3l1_i = st.number_input("L3 / L1", key="l3l1i")

unit_iso = st.radio("Unité des saisies d'isolement :", ["MΩ", "Ω", "kΩ", "GΩ"], horizontal=True)

# --- SECTION 3 : DIÉLECTRIQUE ---
st.header("3️⃣ Test Diélectrique (3Uo)")
st.write("Indiquez s'il y a eu un amorçage pour chaque couple (laisser vide si non testé).")
dielec_res = st.multiselect("Couples ayant amorcé :", 
                            ["L1/N", "L2/N", "L3/N", "L1/L2", "L2/L3", "L3/L1", "L1/T", "L2/T", "L3/T"])
pas_montee = st.checkbox("Pas de montée en tension (Défaut franc)")

# --- BOUTON DE DIAGNOSTIC ---
if st.button("🚀 LANCER LE DIAGNOSTIC"):
    
    # 1. Logique de Rupture (Basée sur tes Tests 3 et 4)
    rupture_neutre = all(v > 1999 for v in [l1n_c, l2n_c, l3n_c]) [cite: 51]
    ruptures = []
    if l1n_c > 1999: ruptures.append("L1") [cite: 35]
    if l2n_c > 1999: ruptures.append("L2")
    if l3n_c > 1999: ruptures.append("L3")
    
    # 2. Identification du couple en défaut (le plus bas en isolement, hors N/T)
    mesures = {
        "L1/N": l1n_i, "L2/N": l2n_i, "L3/N": l3n_i,
        "L1/L2": l1l2_i, "L2/L3": l2l3_i, "L3/L1": l3l1_i,
        "L1/T": l1t_i, "L2/T": l2t_i, "L3/T": l3t_i
    }
    couple_defaut = min(mesures, key=mesures.get)
    val_defaut = mesures[couple_defaut]

    st.divider()
    
    # AFFICHAGE DES RÉSULTATS
    if rupture_neutre:
        st.error("🚨 ALERTE : RUPTURE DE NEUTRE DÉTECTÉE") [cite: 51]
        st.warning("⚠️ MODE CHOC INTERDIT. Risque de surtension chez les abonnés.")
        st.info("🛠️ MÉTHODE : Échométrie comparative uniquement.")
    
    elif len(ruptures) > 0:
        st.error(f"🚨 RUPTURE DE CONDUCTEUR DÉTECTÉE : {', '.join(ruptures)}") [cite: 35]
        if any(couple_defaut.startswith(r) for r in ruptures) and len(dielec_res) > 0:
            st.success("✅ Amorçage sur conducteur rompu (Neutre périphérique) : Choc possible avec BOUCLAGE.") [cite: 35]
        st.info("🛠️ MÉTHODE : Échométrie directe.")

    elif val_defaut <= 10 and unit_iso == "Ω":
        st.error(f"🚨 COURT-CIRCUIT FRANC détecté sur {couple_defaut} ({val_defaut} Ω)") [cite: 15, 69]
        st.warning("⚠️ CHOC INEFFICACE (Pas d'assemblage).") [cite: 15]
        st.info("🛠️ MÉTHODE : Échométrie directe + Fréquences audibles (RD8000).") [cite: 17, 71]

    else:
        st.error(f"🚨 DÉFAUT D'ISOLEMENT RÉSISTANT sur {couple_defaut}")
        if couple_defaut in dielec_res or len(dielec_res) > 0:
            st.success("✅ MÉTHODE : Réflexion sur Arc (ARM) + Ondes de Choc.") [cite: 15, 17]
        else:
            st.info("🛠️ MÉTHODE : Échométrie directe (si < 150Ω) ou ARM.")
