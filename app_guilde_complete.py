import altair as alt
import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="Suivi Guilde Pandora",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# -----------------------------------------------------------------------------
# 1. PARAMÈTRES ET ACCÈS AUX DONNÉES GOOGLE SHEETS
# -----------------------------------------------------------------------------
SPREADSHEET_ID = "1B2-apCuGxSqyVZNm9iSDIHuqt9wUJNu6kpyWyzkqe44"
GID_REPONSES = "331774787"
GID_MEMBRES = "1938648214"

URL_REPONSES = f"https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}/export?format=csv&gid={GID_REPONSES}"
URL_MEMBRES = f"https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}/export?format=csv&gid={GID_MEMBRES}"


@st.cache_data(ttl=300)
def charger_donnees():
    df_rep = pd.read_csv(URL_REPONSES)
    df_memb = pd.read_csv(URL_MEMBRES, skiprows=3)
    return df_rep, df_memb


# Palette de couleurs globale pour les bonus
PALETTE_BONUS = {
    "Att R": "#D32F2F",
    "Att B": "#FF5252",
    "Att CDB R": "#B71C1C",
    "Att CDB B": "#FF7961",
    "Att EG R": "#E64A19",
    "Att EG B": "#FF8A65",
    "Def R": "#1976D2",
    "Def B": "#448AFF",
    "Def CDB R": "#0D47A1",
    "Def CDB B": "#82B1FF",
    "Def EG R": "#00838F",
    "Def EG B": "#80DEEA",
}

# Palette de couleurs de fond par Âge de cité
COULEURS_AGES = {
    "21- HUB": "#8D6E63",
    "20- TITAN": "#D84315",
    "18- VENUS": "#C2185B",
    "15- FV": "#7B1FA2",
    "14- FO": "#512DA8",
    "09- POST": "#0097A7",
    "08- MOD": "#388E3C",
    "07- PROG": "#FBC02D",
}


def generer_chart_altair(df_long, series_visibles, hauteur=280):
    """Fonction générique pour créer un graphique Altair réactif."""
    df_sub = df_long[df_long["Bonus_Type"].isin(series_visibles)].copy()
    domain_c = [k for k in PALETTE_BONUS.keys() if k in series_visibles]
    range_c = [PALETTE_BONUS[k] for k in domain_c]

    chart = (
        alt.Chart(df_sub)
        .mark_line()
        .encode(
            x=alt.X("Date:T", title=None, axis=alt.Axis(format="%b %Y")),
            y=alt.Y("Valeur:Q", title="Bonus"),
            color=alt.Color(
                "Bonus_Type:N",
                scale=alt.Scale(domain=domain_c, range=range_c),
                legend=alt.Legend(
                    orient="bottom", direction="horizontal", title=None
                ),
            ),
            strokeDash=alt.StrokeDash(
                "Style_Ligne:N",
                scale=alt.Scale(
                    domain=["Plein", "Pointillé"], range=[[0], [6, 4]]
                ),
                legend=None,
            ),
            tooltip=[
                alt.Tooltip("Date:T", format="%d/%m/%Y"),
                "Bonus_Type",
                "Valeur",
            ],
        )
        .properties(height=hauteur)
        .interactive()
    )
    return chart


try:
    df_reponses, df_membres = charger_donnees()

    # Nettoyage de la liste des membres actifs
    df_membres.columns = [col.strip() for col in df_membres.columns]
    col_nom_membre = df_membres.columns[0]
    col_age_membre = df_membres.columns[1] if len(df_membres.columns) > 1 else ""
    col_presence = df_membres.columns[3]

    df_actifs = df_membres[df_membres[col_presence] != "HG"].copy()
    membres_actifs_liste = sorted(
        [str(nom).strip() for nom in df_actifs[col_nom_membre].dropna().unique()]
    )

    # Structuration par onglets
    tab_graph, tab_table = st.tabs(
        ["📈 Graphiques Membre (Grille 2x2)", "🏆 Tableau Comparatif Guilde"]
    )

    # -------------------------------------------------------------------------
    # ONGLET 1 : GRILLE DE 4 GRAPHIQUES (TOUS, BASIC, CDB, EG)
    # -------------------------------------------------------------------------
    with tab_graph:
        col_sel1, col_sel2 = st.columns([2, 4])
        with col_sel1:
            joueur_selectionne = st.selectbox(
                "Choisir un membre :", membres_actifs_liste
            )

        col_pseudo = df_reponses.columns[1]
        df_joueur = df_reponses[
            df_reponses[col_pseudo].astype(str).str.strip() == joueur_selectionne
        ].copy()

        if df_joueur.empty:
            st.warning(f"Aucune donnée enregistrée pour {joueur_selectionne}.")
        else:
            col_date = df_joueur.columns[0]
            df_joueur[col_date] = pd.to_datetime(
                df_joueur[col_date], dayfirst=True, format="mixed"
            )
            df_joueur = df_joueur.sort_values(by=col_date)

            noms_bonus = [
                "Att R", "Def R", "Att B", "Def B",
                "Att CDB R", "Def CDB R", "Att CDB B", "Def CDB B",
                "Att EG R", "Def EG R", "Att EG B", "Def EG B",
            ]

            cols_source = df_joueur.columns[3:9]
            df_graphique = pd.DataFrame()
            df_graphique["Date"] = df_joueur[col_date]

            idx = 0
            for col in cols_source:
                split_data = (
                    df_joueur[col]
                    .astype(str)
                    .str.split("-", expand=True)
                    .apply(pd.to_numeric, errors="coerce")
                )
                if split_data.shape[1] >= 2:
                    df_graphique[noms_bonus[idx]] = split_data[0]
                    df_graphique[noms_bonus[idx + 1]] = split_data[1]
                idx += 2

            df_long = df_graphique.melt(
                id_vars=["Date"], var_name="Bonus_Type", value_name="Valeur"
            ).dropna()
            df_long["Style_Ligne"] = df_long["Bonus_Type"].apply(
                lambda x: "Pointillé" if x.endswith(" B") else "Plein"
            )

            # --- GRILLE 2x2 ---
            row1_col1, row1_col2 = st.columns(2)
            row2_col1, row2_col2 = st.columns(2)

            with row1_col1:
                with st.container(border=True):
                    st.markdown("#### 🌐 TOUS LES BONUS")
                    c1 = generer_chart_altair(df_long, noms_bonus)
                    st.altair_chart(c1, use_container_width=True)

            with row1_col2:
                with st.container(border=True):
                    st.markdown("#### ⚔️ BONUS BASIC")
                    c2 = generer_chart_altair(
                        df_long, ["Att R", "Def R", "Att B", "Def B"]
                    )
                    st.altair_chart(c2, use_container_width=True)

            with row2_col1:
                with st.container(border=True):
                    st.markdown("#### 🏰 BONUS CDB (Champ de Bataille)")
                    c3 = generer_chart_altair(
                        df_long,
                        ["Att CDB R", "Def CDB R", "Att CDB B", "Def CDB B"],
                    )
                    st.altair_chart(c3, use_container_width=True)

            with row2_col2:
                with st.container(border=True):
                    st.markdown("#### 🏛️ BONUS EG (Expédition de Guilde)")
                    c4 = generer_chart_altair(
                        df_long,
                        ["Att EG R", "Def EG R", "Att EG B", "Def EG B"],
                    )
                    st.altair_chart(c4, use_container_width=True)

    # -------------------------------------------------------------------------
    # ONGLET 2 : TABLEAU COMPARATIF DERNIÈRE SAISIE (AVEC PICTOS ET COULEURS)
    # -------------------------------------------------------------------------
    with tab_table:
        st.markdown("### 🏆 Classement Guilde — Dernières Saisies")

        # Préparation du tableau comparatif
        df_rep_clean = df_reponses.copy()
        col_d = df_rep_clean.columns[0]
        col_p = df_rep_clean.columns[1]

        df_rep_clean[col_d] = pd.to_datetime(
            df_rep_clean[col_d], dayfirst=True, format="mixed"
        )
        df_rep_clean[col_p] = df_rep_clean[col_p].astype(str).str.strip()

        # Conserver uniquement la saisie la plus récente de chaque joueur
        df_latest = df_rep_clean.sort_values(col_d).groupby(col_p).last().reset_index()

        # Filtrer uniquement les membres actifs
        df_latest = df_latest[df_latest[col_p].isin(membres_actifs_liste)].copy()

        # Renommage des colonnes avec PICTOGRAMMES ⚔️ 🛡️
        df_display = pd.DataFrame()
        df_display["Dernière Maj"] = df_latest[col_d].dt.strftime("%d/%m/%Y")
        df_display["Pseudo"] = df_latest[col_p]

        # Traitement des valeurs Attaque/Défense
        idx_b = 0
        noms_colonnes_picto = [
            "🔴 Att", "🔴 Def", "🔵 Att", "🔵 Def",
            "🏰 🔴 Att", "🏰 🔴 Def", "🏰 🔵 Att", "🏰 🔵 Def",
            "🏛️ 🔴 Att", "🏛️ 🔴 Def", "🏛️ 🔵 Att", "🏛️ 🔵 Def",
        ]

        for col in df_latest.columns[3:9]:
            split_data = (
                df_latest[col]
                .astype(str)
                .str.split("-", expand=True)
                .apply(pd.to_numeric, errors="coerce")
            )
            if split_data.shape[1] >= 2:
                df_display[noms_colonnes_picto[idx_b]] = split_data[0]
                df_display[noms_colonnes_picto[idx_b + 1]] = split_data[1]
            idx_b += 2

        # Affichage du tableau interactif complet
        st.dataframe(
            df_display,
            use_container_width=True,
            hide_index=True,
            height=500,
        )

except Exception as e:
    st.error(f"Erreur de chargement : {e}")