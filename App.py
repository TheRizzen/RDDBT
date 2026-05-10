import streamlit as st
import math

# ─────────────────────────────────────────────
#  CONFIG
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="DiagBT — Expert Terrain",
    page_icon="⚡",
    layout="wide",
)

# ─────────────────────────────────────────────
#  CSS PERSONNALISÉ
# ─────────────────────────────────────────────
st.markdown("""
<style>
/* ---- palette sombre ---- */
:root {
    --orange: #e05c28;
    --orange-bg: rgba(224,92,40,0.12);
    --orange-border: rgba(224,92,40,0.35);
    --red-bg: rgba(220,60,60,0.13);
    --red-border: rgba(220,60,60,0.35);
    --red-text: #f07070;
    --green-bg: rgba(50,180,100,0.13);
    --green-border: rgba(50,180,100,0.35);
    --green-text: #5fcc8a;
    --yellow-bg: rgba(220,170,40,0.13);
    --yellow-border: rgba(220,170,40,0.35);
    --yellow-text: #e0b840;
    --blue-bg: rgba(60,130,220,0.13);
    --blue-border: rgba(60,130,220,0.35);
    --blue-text: #70a8f0;
}

/* ---- bannières de nature ---- */
.banner {
    border-radius: 10px; padding: 14px 18px;
    margin-bottom: 12px; display: flex;
    align-items: flex-start; gap: 12px;
    border: 0.5px solid;
}
.banner-danger  { background: var(--red-bg);    border-color: var(--red-border);    color: var(--red-text);    }
.banner-warning { background: var(--yellow-bg); border-color: var(--yellow-border); color: var(--yellow-text); }
.banner-info    { background: var(--blue-bg);   border-color: var(--blue-border);   color: var(--blue-text);   }
.banner-success { background: var(--green-bg);  border-color: var(--green-border);  color: var(--green-text);  }

.banner-icon  { font-size: 22px; flex-shrink: 0; margin-top: 2px; }
.banner-title { font-size: 15px; font-weight: 600; margin-bottom: 3px; }
.banner-sub   { font-size: 13px; opacity: .85; }

/* ---- boîtes d'alerte ---- */
.alertbox {
    border-radius: 7px; padding: 11px 14px;
    margin-bottom: 10px; font-size: 13px;
    line-height: 1.6; display: flex;
    gap: 9px; align-items: flex-start; border: 0.5px solid;
}
.alertbox-danger  { background: var(--red-bg);    border-color: var(--red-border);    color: var(--red-text);    }
.alertbox-warning { background: var(--yellow-bg); border-color: var(--yellow-border); color: var(--yellow-text); }
.alertbox-info    { background: var(--blue-bg);   border-color: var(--blue-border);   color: var(--blue-text);   }
.alertbox-success { background: var(--green-bg);  border-color: var(--green-border);  color: var(--green-text);  }

/* ---- cartes méthode ---- */
.method-grid {
    display: grid; grid-template-columns: 1fr 1fr;
    gap: 12px; margin-bottom: 12px;
}
@media (max-width: 640px) { .method-grid { grid-template-columns: 1fr; } }

.mcard {
    background: rgba(255,255,255,0.03);
    border: 0.5px solid rgba(255,255,255,0.1);
    border-radius: 10px; padding: 14px;
}
.mcard-title {
    font-size: 13px; font-weight: 600;
    color: var(--orange); margin-bottom: 10px;
    padding-bottom: 8px;
    border-bottom: 0.5px solid rgba(255,255,255,0.08);
}
.mcard-step {
    font-size: 12px; color: rgba(255,255,255,0.65);
    padding: 4px 0; line-height: 1.6;
}
.mcard-step::before { content: "→ "; color: var(--orange); font-weight: 700; }

/* ---- header ---- */
.app-header {
    display: flex; align-items: center; gap: 14px;
    padding-bottom: 18px; margin-bottom: 20px;
    border-bottom: 0.5px solid rgba(255,255,255,0.1);
}
.app-title   { font-size: 22px; font-weight: 700; margin: 0; }
.app-sub     { font-size: 13px; color: rgba(255,255,255,0.5); margin: 0; }

/* masquer l'index des dataframes */
thead tr th:first-child { display: none; }
tbody tr td:first-child { display: none; }
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
#  UTILITAIRES
# ─────────────────────────────────────────────
def to_ohms(val, unit):
    """Convertit une valeur + unité en Ohms."""
    if val is None:
        return None
    if unit == "GΩ":
        return val * 1_000_000_000
    if unit == "MΩ":
        return val * 1_000_000
    if unit == "kΩ":
        return val * 1_000
    return val  # Ω


def format_ohms(val):
    """Affiche une résistance dans l'unité la plus lisible."""
    if val == math.inf:
        return "∞"
    if val >= 1e9:
        return f"{val/1e9:.2f} GΩ"
    if val >= 1e6:
        return f"{val/1e6:.2f} MΩ"
    if val >= 1e3:
        return f"{val/1e3:.2f} kΩ"
    return f"{val:.2f} Ω"


def banner_html(cls, icon, title, sub):
    return f"""
    <div class="banner banner-{cls}">
        <span class="banner-icon">{icon}</span>
        <div>
            <div class="banner-title">{title}</div>
            <div class="banner-sub">{sub}</div>
        </div>
    </div>"""


def alert_html(cls, icon, msg):
    return f"""
    <div class="alertbox alertbox-{cls}">
        <span>{icon}</span><span>{msg}</span>
    </div>"""


def method_card_html(icon, title, steps):
    steps_html = "".join(f'<div class="mcard-step">{s}</div>' for s in steps)
    return f"""
    <div class="mcard">
        <div class="mcard-title">{icon} {title}</div>
        {steps_html}
    </div>"""


def method_grid_html(card1, card2):
    return f'<div class="method-grid">{card1}{card2}</div>'


# ─────────────────────────────────────────────
#  LOGIQUE DE DIAGNOSTIC
# ─────────────────────────────────────────────
def generer_diagnostic(cont_data, iso_results, die_results):
    """
    Retourne un bloc HTML de rapport basé sur les mesures saisies.

    cont_data   : dict {couple: float|inf}   (ex. {"L1/N": inf, "L2/N": 0.5, ...})
    iso_results : dict {couple: float}       en Ohms
    die_results : dict {couple: str}         résultat diélectrique
    """

    # --- Analyse continuité ---
    rup_neutre = (
        cont_data.get("L1/N") == math.inf and
        cont_data.get("L2/N") == math.inf and
        cont_data.get("L3/N") == math.inf
    )
    phases_coupees = [p for p in ["L1", "L2", "L3"] if cont_data.get(f"{p}/N") == math.inf]

    # --- Analyse isolement (hors N/T) ---
    iso_filtre = {k: v for k, v in iso_results.items() if k != "N/T" and v is not None}
    if iso_filtre:
        pire_couple = min(iso_filtre, key=iso_filtre.get)
        val_pire = iso_filtre[pire_couple]
    else:
        pire_couple = "N/A"
        val_pire = math.inf

    stat_die = die_results.get(pire_couple, "N.R")

    html = ""

    # ── CAS 1 : RUPTURE TOTALE DU NEUTRE ──────────────────────────
    if rup_neutre:
        html += banner_html(
            "danger", "🔌",
            "Rupture totale du neutre",
            "Continuité infinie sur L1/N, L2/N et L3/N."
        )
        html += alert_html(
            "danger", "⚠️",
            "<strong>Sécurité :</strong> Choc électrique <strong>STRICTEMENT INTERDIT</strong>. "
            "Risque de surtension 400 V sur les appareils clients (destruction du point milieu)."
        )
        html += method_grid_html(
            method_card_html("〰️", "Prélocalisation — Échométrie", [
                "Utiliser le mode Comparaison.",
                "Comparer la trace d'une phase saine avec la trace du neutre.",
                "La divergence des deux courbes indique la distance au défaut (montée brutale du signal neutre).",
            ]),
            method_card_html("📡", "Localisation finale — RD8000", [
                "Injecter le signal sur le conducteur neutre.",
                "Suivre le tracé : le signal disparaît ou change radicalement à l'aplomb du défaut.",
                "Confirmer par fouille ou inspection de boîte de jonction.",
            ])
        )

    # ── CAS 2 : RUPTURE DE PHASE(S) ───────────────────────────────
    elif phases_coupees:
        phases_str = ", ".join(phases_coupees)
        couples_str = ", ".join(f"{p}/N" for p in phases_coupees)
        html += banner_html(
            "danger", "✂️",
            f"Rupture de conducteur — {phases_str}",
            f"Continuité infinie mesurée sur {couples_str}."
        )
        if stat_die == "Amorçage":
            html += alert_html(
                "success", "✅",
                "Amorçage détecté — le conducteur rompu est proche du neutre périphérique. "
                "<strong>Choc possible</strong> mais nécessite un bouclage en extrémité."
            )
            html += method_grid_html(
                method_card_html("〰️", "Prélocalisation — Échométrie directe", [
                    "Mode direct. La rupture provoque une réflexion positive (impédance infinie).",
                    "Mesurer la distance du premier front montant.",
                ]),
                method_card_html("👂", "Localisation finale — Choc acoustique", [
                    "Bouclage obligatoire en extrémité du câble.",
                    "Micro de sol sur la zone prélocolisée.",
                    "Rechercher le claquement acoustique à l'aplomb du défaut.",
                ])
            )
        else:
            html += alert_html(
                "warning", "ℹ️",
                "Pas d'amorçage — le choc sera probablement inaudible. "
                "Priorité à l'échométrie directe ou au suivi de tracé."
            )
            html += method_grid_html(
                method_card_html("〰️", "Prélocalisation — Échométrie directe", [
                    "Mode direct. La rupture provoque une réflexion positive (impédance infinie).",
                    "Mesurer la distance du premier front montant.",
                ]),
                method_card_html("📡", "Localisation finale — RD8000", [
                    "Injecter un signal sur la phase rompue.",
                    "Suivre le tracé : le signal disparaît ou change radicalement à l'aplomb de la rupture.",
                ])
            )

    # ── CAS 3 : COURT-CIRCUIT FRANC (Rd ≤ 10 Ω) ──────────────────
    elif val_pire <= 10:
        html += banner_html(
            "warning", "🔗",
            f"Court-circuit franc — {pire_couple}",
            f"Résistance mesurée : {format_ohms(val_pire)} — contact métallique direct."
        )
        html += alert_html(
            "info", "ℹ️",
            "La résistance est trop faible pour créer un arc électrique. "
            "Le camion de choc sera <strong>silencieux</strong> — ne pas utiliser le mode acoustique seul."
        )
        html += method_grid_html(
            method_card_html("〰️", "Prélocalisation — Échométrie directe", [
                "Mode direct. Le court-circuit provoque une réflexion négative (front descendant).",
                "La distance est facile à lire, le signal est très net et stable.",
            ]),
            method_card_html("📡", "Localisation — Générateur BF + RD8000", [
                "Méthode la plus fiable pour les défauts francs.",
                "Injecter un signal BF sur le câble défectueux.",
                "Suivre le courant de défaut jusqu'au point de contact métallique.",
            ])
        )

    # ── CAS 4 : DÉFAUT RÉSISTANT / ÉCLATEUR ──────────────────────
    else:
        if stat_die == "Amorçage":
            html += banner_html(
                "success", "⚡",
                f"Défaut éclateur — {pire_couple}",
                f"Résistance : {format_ohms(val_pire)} — amorçage détecté au test diélectrique."
            )
            html += alert_html(
                "success", "✅",
                "Éclateur confirmé : le défaut ne se voit qu'en tension. "
                "Méthode ARM recommandée pour la prélocalisation."
            )
            html += method_grid_html(
                method_card_html("〰️", "Prélocalisation — Méthode ARM", [
                    "Utiliser le mode ARM (Réflexion sur Arc).",
                    "Envoyer un choc pour créer l'arc et stabiliser la trace échométrique.",
                    "L'arc génère une réflexion caractéristique — lire la distance directement.",
                ]),
                method_card_html("👂", "Localisation — Choc acoustique", [
                    "Micro de sol sur la zone prélocolisée.",
                    "Le défaut produit un claquement bien audible.",
                    "Localisation précise par triangulation acoustique.",
                ])
            )
        else:
            html += banner_html(
                "info", "🔵",
                f"Défaut d'isolement résistant — {pire_couple}",
                f"Résistance : {format_ohms(val_pire)} — pas d'amorçage détecté."
            )
            html += alert_html(
                "info", "ℹ️",
                "Le défaut ne claque pas à la tension actuelle. "
                "Augmenter la tension du test diélectrique pour tenter de transformer le défaut en éclateur."
            )
            html += method_grid_html(
                method_card_html("〰️", "Prélocalisation — Échométrie directe", [
                    "Utilisable si Rd < 150 Ω.",
                    "Au-delà : la réflexion est trop atténuée, résultat non fiable.",
                ]),
                method_card_html("🔧", "Action recommandée", [
                    "Relancer un test diélectrique à tension plus élevée.",
                    "Si amorçage obtenu : basculer en mode ARM pour la prélocalisation.",
                    "Si aucun amorçage : envisager la méthode par pont de Wheatstone.",
                ])
            )

    return html


# ─────────────────────────────────────────────
#  CONSTANTES
# ─────────────────────────────────────────────
C_LABELS   = ["L1/N", "L2/N", "L3/N", "L1/L2", "L2/L3", "L3/L1"]
ISO_LABELS = ["L1/N", "L2/N", "L3/N", "L1/L2", "L2/L3", "L3/L1", "L1/T", "L2/T", "L3/T", "N/T"]
DIE_LABELS = ["L1/N", "L2/N", "L3/N", "L1/L2", "L2/L3", "L3/L1"]
DIE_OPTS   = ["N.R", "Pas d'amorçage", "Amorçage", "Pas de montée en tension"]
UNITS      = ["MΩ", "GΩ", "kΩ", "Ω"]


# ─────────────────────────────────────────────
#  INTERFACE STREAMLIT
# ─────────────────────────────────────────────

# --- En-tête ---
st.markdown("""
<div class="app-header">
    <div>⚡</div>
    <div>
        <p class="app-title">DiagBT — Expert Terrain</p>
        <p class="app-sub">Diagnostic de défauts souterrains Basse Tension</p>
    </div>
</div>
""", unsafe_allow_html=True)

tab1, tab2, tab3 = st.tabs(["〰️  Continuité", "🔌  Isolement", "⚡  Diélectrique"])


# ─────────────────────────────────────────────
#  ONGLET 1 — CONTINUITÉ
# ─────────────────────────────────────────────
cont_data = {}
with tab1:
    st.caption("Cocher **Infinie (∞)** si le circuit est ouvert (rupture). Sinon renseigner la résistance mesurée en Ω.")
    cols = st.columns(3)
    for i, label in enumerate(C_LABELS):
        with cols[i % 3]:
            st.markdown(f"**{label}**")
            infinie = st.checkbox("∞ Infinie", key=f"c_inf_{label}")
            if infinie:
                cont_data[label] = math.inf
            else:
                val = st.number_input(
                    f"Résistance (Ω)", min_value=0.0, value=0.0,
                    key=f"c_val_{label}", label_visibility="collapsed"
                )
                cont_data[label] = float(val)
            st.markdown("---")


# ─────────────────────────────────────────────
#  ONGLET 2 — ISOLEMENT
# ─────────────────────────────────────────────
iso_results = {}
with tab2:
    st.caption("Saisir la valeur et l'unité pour chaque couple. Laisser à 0 si non mesuré (sera ignoré dans le diagnostic).")
    cols = st.columns(2)
    for i, label in enumerate(ISO_LABELS):
        with cols[i % 2]:
            st.markdown(f"**{label}**")
            c1, c2 = st.columns([3, 1])
            with c1:
                val = st.number_input(
                    "Valeur", min_value=0.0, value=0.0,
                    key=f"iso_v_{label}", label_visibility="collapsed"
                )
            with c2:
                unit = st.selectbox(
                    "Unité", UNITS,
                    key=f"iso_u_{label}", label_visibility="collapsed"
                )
            iso_results[label] = to_ohms(val, unit) if val > 0 else 1e12
            st.markdown("---")


# ─────────────────────────────────────────────
#  ONGLET 3 — DIÉLECTRIQUE
# ─────────────────────────────────────────────
die_results = {}
with tab3:
    st.caption("Pour chaque couple, indiquer le résultat du test haute tension (3Uo) et la tension d'amorçage si applicable.")
    for label in DIE_LABELS:
        c1, c2, c3 = st.columns([1, 2, 2])
        with c1:
            st.markdown(f"**{label}**")
        with c2:
            result = st.selectbox(
                "Résultat", DIE_OPTS,
                key=f"die_s_{label}", label_visibility="collapsed"
            )
            die_results[label] = result
        with c3:
            st.text_input(
                "U amorçage (kV)", placeholder="ex: 3.2 kV",
                key=f"die_t_{label}", label_visibility="collapsed"
            )
        st.markdown("---")


# ─────────────────────────────────────────────
#  BOUTON DIAGNOSTIC
# ─────────────────────────────────────────────
st.divider()
col_btn, _ = st.columns([1, 3])
with col_btn:
    run = st.button("⚡ Générer le diagnostic", type="primary", use_container_width=True)

if run:
    st.divider()
    st.markdown("### 📋 Rapport d'intervention")
    rapport_html = generer_diagnostic(cont_data, iso_results, die_results)
    st.markdown(rapport_html, unsafe_allow_html=True)
