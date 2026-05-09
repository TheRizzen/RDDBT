import streamlit as st

st.set_page_config(page_title="DiagBT - Expert Terrain", layout="wide")

st.title("⚡ Expert de Recherche de Défauts BT")
st.write("Diagnostic détaillé basé sur les procédures de recherche de défauts souterrains.")

# --- FONCTIONS ---
def to_ohms(val, unit):
    if val is None: return None
    if unit == "GΩ": return val * 1_000_000_000
    if unit == "MΩ": return val * 1_000_000
    if unit == "kΩ": return val * 1_000
    return val

# --- SECTION 1 : CONTINUITÉ ---
st.header("1️⃣ Test de Continuité")
c_labels = ["L1/N", "L2/N", "L3/N", "L1/L2", "L2/L3", "L3/L1"]
cont_data = {}
cols = st.columns(3)
for i, label in enumerate(c_labels):
    with cols[i % 3]:
        choice = st.radio(f"État {label}", ["Valeur (Ω)", "Infinie"], key=f"c_{label}", horizontal=True)
        if choice == "Valeur (Ω)":
            val = st.number_input(f"Ω {label}", value=None, key=f"v_c_{label}")
            cont_data[label] = val if val is not None else 0.0
        else:
            cont_data[label] = float('inf')

# --- SECTION 2 : ISOLEMENT ---
st.header("2️⃣ Mesures d'Isolement")
labels_iso = ["L1/N", "L2/N", "L3/N", "L1/L2", "L2/L3", "L3/L1", "L1/T", "L2/T", "L3/T", "N/T"]
iso_results = {}
for label in labels_iso:
    col1, col2 = st.columns([3, 1])
    with col1:
        v = st.number_input(f"Iso {label}", value=None, key=f"i_v_{label}")
    with col2:
        u = st.selectbox(f"Unité", ["MΩ", "GΩ", "kΩ", "Ω"], key=f"i_u_{label}")
    iso_results[label] = to_ohms(v, u) if v is not None else 1_000_000_000_000

# --- SECTION 3 : DIÉLECTRIQUE ---
st.header("3️⃣ Test Diélectrique (3Uo)")
labels_die = ["L1/N", "L2/N", "L3/N", "L1/L2", "L2/L3", "L3/L1"]
die_results = {}
for label in labels_die:
    col_d1, col_d2 = st.columns([2, 2])
    with col_d1:
        s = st.selectbox(f"Résultat {label}", ["N.R", "Pas d'amorçage", "Amorçage", "Pas de montée en tension"], key=f"d_s_{label}")
    with col_d2:
        t = st.text_input(f"U amorçage {label}", key=f"d_t_{label}")
    die_results[label] = s

# --- LOGIQUE DE DIAGNOSTIC DÉTAILLÉ ---
st.divider()
if st.button("🚀 GÉNÉRER LE DIAGNOSTIC DÉTAILLÉ"):
    
    # Détection Ruptures
    rupture_neutre = cont_data["L1/N"] == float('inf') and cont_data["L2/N"] == float('inf') and cont_data["L3/N"] == float('inf')
    phases_coupees = [p for p in ["L1", "L2", "L3"] if cont_data.get(f"{p}/N") == float('inf')]
    
    # Analyse Isolement
    iso_filtre = {k: v for k, v in iso_results.items() if k != "N/T"}
    pire_couple = min(iso_filtre, key=iso_filtre.get)
    val_pire = iso_filtre[pire_couple]
    statut_die = die_results.get(pire_couple, "N.R")

    # --- AFFICHAGE ---
    st.subheader("📋 RAPPORT D'INTERVENTION")

    # CAS 1 : RUPTURE DE NEUTRE
    if rupture_neutre:
        st.error("### 🚩 NATURE : RUPTURE TOTALE DU NEUTRE")
        st.warning("**⚠️ SÉCURITÉ :** Le choc électrique est **STRICTEMENT INTERDIT**. Risque de destruction des appareils clients par rupture du point milieu (surtension 400V).")
        
        st.markdown("""
        **🔍 PRÉLOCALISATION (Échométrie) :**
        * Utiliser le mode **Comparaison**. 
        * Comparer la trace d'une phase saine avec la trace du neutre.
        * Le défaut se situe au point de divergence des deux courbes (montée brutale du signal sur le neutre).
        
        **📍 LOCALISATION FINALE (Terrain) :**
        * **Suivi de tracé au RD8000 :** Injecter le signal sur le neutre. Le défaut se trouve là où le signal disparaît ou change radicalement de comportement.
        """)

    # CAS 2 : RUPTURE DE PHASE
    elif len(phases_coupees) > 0:
        st.error(f"### 🚩 NATURE : RUPTURE DE CONDUCTEUR ({', '.join(phases_coupees)})")
        
        detail_choc = ""
        if statut_die == "Amorçage":
            detail_choc = "✅ **Amorçage détecté :** Le conducteur rompu est proche du neutre périphérique. Le mode **CHOC** est possible mais nécessite un **BOUCLAGE** en extrémité pour assurer le retour du courant."
        else:
            detail_choc = "❌ **Pas d'amorçage :** Le choc sera probablement inaudible. Priorité à l'échométrie."

        st.markdown(f"""
        {detail_choc}
        
        **🔍 PRÉLOCALISATION (Échométrie) :**
        * Mode direct. La rupture provoque une réflexion positive (impédance infinie). 
        * Mesurer la distance du premier front montant.
        
        **📍 LOCALISATION FINALE (Terrain) :**
        * Si amorçage : Recherche acoustique (micro de sol) avec bouclage.
        * Si pas d'amorçage : Suivi de tracé au RD8000 (disparition du signal).
        """)

    # CAS 3 : COURT-CIRCUIT FRANC
    elif val_pire <= 10:
        st.error(f"### 🚩 NATURE : DÉFAUT FRANC ({pire_couple})")
        st.warning("**⚠️ NOTE :** La résistance est trop faible ({val_pire} Ω) pour créer un arc électrique. Le camion de choc sera silencieux (pas d'assemblage).")
        
        st.markdown("""
        **🔍 PRÉLOCALISATION (Échométrie) :**
        * Mode direct. Le court-circuit provoque une réflexion négative (front descendant).
        * La distance est facile à lire car le signal est très net.
        
        **📍 LOCALISATION FINALE (Terrain) :**
        * **Générateur BF + RD8000 :** C'est la méthode la plus fiable ici. Suivre le courant de défaut jusqu'au point de contact métallique.
        """)

    # CAS 4 : DÉFAUT RÉSISTANT / ÉCLATEUR
    else:
        st.error(f"### 🚩 NATURE : DÉFAUT D'ISOLEMENT RÉSISTANT ({pire_couple})")
        
        if statut_die == "Amorçage":
            st.success("**✅ ÉCLATEUR DÉTECTÉ :** Le défaut ne se voit qu'en tension. Méthode ARM recommandée.")
            st.markdown("""
            **🔍 PRÉLOCALISATION (Échométrie) :**
            * Utiliser le mode **ARM (Réflexion sur Arc)**. 
            * Envoyer un choc pour créer l'arc et stabiliser la trace.
            
            **📍 LOCALISATION FINALE (Terrain) :**
            * **Ondes de choc acoustiques :** Utiliser le micro de sol. Le défaut "claque" bien, le bruit devrait être facile à localiser.
            """)
        else:
            st.info("**ℹ️ INFO :** Le défaut ne claque pas à la tension actuelle.")
            st.markdown("""
            **🔍 PRÉLOCALISATION :** Échométrie directe si Rd < 150 Ω. Sinon, augmenter la tension du test diélectrique pour tenter de transformer le défaut en éclateur.
            """)
