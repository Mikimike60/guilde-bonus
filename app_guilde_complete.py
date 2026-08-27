import base64
import os
import re
import altair as alt
import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="Suivi Guilde Pandora",
    page_icon="⚔️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# -----------------------------------------------------------------------------
# 1. SÉCURITÉ MOT DE PASSE (.streamlit/secrets.toml)
# -----------------------------------------------------------------------------
def verifier_mot_de_passe():
    if "authentifie" not in st.session_state:
        st.session_state["authentifie"] = False

    if not st.session_state["authentifie"]:
        st.title("🔒 Connexion à Pandora")
        mot_de_passe_saisi = st.text_input("Mot de passe :", type="password")
        mot_de_passe_correct = st.secrets.get("PASSWORD", "Pandora2026")

        if st.button("Se connecter"):
            if mot_de_passe_saisi == mot_de_passe_correct:
                st.session_state["authentifie"] = True
                st.rerun()
            else:
                st.error("Mot de passe incorrect.")
        return False
    return True


if not verifier_mot_de_passe():
    st.stop()

# -----------------------------------------------------------------------------
# 2. DONNÉES GOOGLE SHEETS
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


# -----------------------------------------------------------------------------
# 3. CONFIGURATION DES ÂGES, COULEURS ET ASSETS
# -----------------------------------------------------------------------------
DOSSIER_ASSETS = "assets/"


def convertir_image_base64(chemin):
    if os.path.exists(chemin):
        with open(chemin, "rb") as f:
            return f"data:image/png;base64,{base64.b64encode(f.read()).decode()}"
    return ""


LOGOS_GRAPHIQUES = {
    "TOUS": f"{DOSSIER_ASSETS}TOUS.png",
    "BASIC": f"{DOSSIER_ASSETS}BASIC.png",
    "CDB": f"{DOSSIER_ASSETS}CDB.png",
    "EG": f"{DOSSIER_ASSETS}EG.png",
}

PICTOS = {
    "AR": f"{DOSSIER_ASSETS}AR.png",
    "DR": f"{DOSSIER_ASSETS}DR.png",
    "AB": f"{DOSSIER_ASSETS}AB.png",
    "DB": f"{DOSSIER_ASSETS}DB.png",
    "AR_CDB": f"{DOSSIER_ASSETS}AR_CDB.png",
    "DR_CDB": f"{DOSSIER_ASSETS}DR_CDB.png",
    "AB_CDB": f"{DOSSIER_ASSETS}AB_CDB.png",
    "DB_CDB": f"{DOSSIER_ASSETS}DB_CDB.png",
    "AR_EG": f"{DOSSIER_ASSETS}AR_EG.png",
    "DR_EG": f"{DOSSIER_ASSETS}DR_EG.png",
    "AB_EG": f"{DOSSIER_ASSETS}AB_EG.png",
    "DB_EG": f"{DOSSIER_ASSETS}DB_EG.png",
}

# Mapping (Couleur de fond, Couleur de texte)
PALETTE_AGES = {
    "01- ADF": ("#E2997A", "#000000"),
    "02- HMA": ("#A8F09A", "#000000"),
    "03- MAC": ("#6A9EEB", "#000000"),
    "04- REN": ("#9400D3", "#FFFFFF"),
    "05- COL": ("#F5C242", "#000000"),
    "06- INDUS": ("#CCCCCC", "#000000"),
    "07- PROG": ("#E8A7B8", "#000000"),
    "08- MOD": ("#CC5533", "#000000"),
    "09- POST": ("#A2E0C4", "#000000"),
    "10- CTP": ("#70C8E8", "#000000"),
    "11- DEM": ("#EAE643", "#000000"),
    "12- FUT": ("#1958DB", "#FFFFFF"),
    "13- FA": ("#BDD5EA", "#000000"),
    "14- FO": ("#88A9C3", "#000000"),
    "15- FV": ("#FF00FF", "#FFFFFF"),
    "16- MARS": ("#2BB24C", "#000000"),
    "17- ESCA": ("#D92338", "#FFFFFF"),
    "18- VENUS": ("#F4B8C5", "#000000"),
    "19- JUP": ("#F7D4CE", "#000000"),
    "20- TITAN": ("#964B00", "#FFFFFF"),
    "21- HUB": ("#525252", "#FFFFFF"),
    "22- DEC": ("#5B2C83", "#FFFFFF"),
}

# Correspondance pour nettoyer les intitulés bruts de Google Sheet (ex: "MOYEU" -> "21- HUB")
MAPPING_BRUT_VERS_STD = {
    "ADF": "01- ADF",
    "HMA": "02- HMA",
    "MAC": "03- MAC",
    "REN": "04- REN",
    "COL": "05- COL",
    "INDUS": "06- INDUS",
    "PROG": "07- PROG",
    "PROGRAMME": "07- PROG",
    "MOD": "08- MOD",
    "POST": "09- POST",
    "POSTE": "09- POST",
    "CTP": "10- CTP",
    "DEM": "11- DEM",
    "FUT": "12- FUT",
    "FA": "13- FA",
    "FO": "14- FO",
    "FV": "15- FV",
    "MARS": "16- MARS",
    "ESCA": "17- ESCA",
    "VENUS": "18- VENUS",
    "VÉNUS": "18- VENUS",
    "JUP": "19- JUP",
    "TITAN": "20- TITAN",
    "HUB": "21- HUB",
    "MOYEU": "21- HUB",
    "DEC": "22- DEC",
}


def normaliser_age(valeur_brute):
    val_str = str(valeur_brute).strip().upper()
    for code, _ in PALETTE_AGES.items():
        if code in val_str:
            return code
    for mot_cle, code_std in MAPPING_BRUT_VERS_STD.items():
        if mot_cle in val_str:
            return code_std
    return val_str


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

# -----------------------------------------------------------------------------
# 4. COMPOSANTS GRAPHIQUES & TABLEAU HTML
# -----------------------------------------------------------------------------
def generer_chart_altair(df_long, series_visibles, hauteur=280):
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


def afficher_tableau_html(df_latest):
    p = {k: convertir_image_base64(v) for k, v in PICTOS.items()}
    px = 22

    lignes = [
        "<style>",
        ".table-container { overflow-x: auto; width: 100%; margin-bottom: 20px; }",
        ".tableau-pandora { width: 100%; border-collapse: collapse; font-family: Arial, sans-serif; font-size: 13px; text-align: center; }",
        ".tableau-pandora th, .tableau-pandora td { border: 1px solid #333333; padding: 5px 3px; }",
        ".tableau-pandora th { font-weight: bold; }",
        ".bg-rouge-titre { background-color: #CC0000; color: #FFFFFF; }",
        ".bg-bleu-titre { background-color: #0055B8; color: #FFFFFF; }",
        ".bg-rouge-cdb { background-color: #CC0000; color: #FFFFFF; }",
        ".bg-bleu-cdb { background-color: #0055B8; color: #FFFFFF; }",
        ".bg-entete-sub { background-color: #1E1E1E; color: #FFFFFF; }",
        "</style>",
        '<div class="table-container">',
        '<table class="tableau-pandora">',
        "<thead>",
        '<tr style="background-color: #262730; color: #FFFFFF;">',
        '<th rowspan="2">Horodateur</th>',
        '<th rowspan="2">PSEUDO<br>(dans le jeu)</th>',
        '<th rowspan="2">AGE DE<br>VOTRE CITE</th>',
        '<th colspan="2" class="bg-rouge-titre">BONUS ROUGE</th>',
        '<th colspan="2" class="bg-bleu-titre">BONUS BLEU</th>',
        '<th colspan="2" class="bg-rouge-cdb">BONUS ROUGE CDB</th>',
        '<th colspan="2" class="bg-bleu-cdb">BONUS BLEU CDB</th>',
        '<th colspan="2" class="bg-rouge-titre">BONUS ROUGE EG</th>',
        '<th colspan="2" class="bg-bleu-titre">BONUS BLEU EG</th>',
        "</tr>",
        '<tr class="bg-entete-sub">',
        f'<th><img src="{p.get("AR","")}" width="{px}"><br>Attaque</th>',
        f'<th><img src="{p.get("DR","")}" width="{px}"><br>Defense</th>',
        f'<th><img src="{p.get("AB","")}" width="{px}"><br>Attaque</th>',
        f'<th><img src="{p.get("DB","")}" width="{px}"><br>Defense</th>',
        f'<th><img src="{p.get("AR_CDB","")}" width="{px}"><br>Attaque</th>',
        f'<th><img src="{p.get("DR_CDB","")}" width="{px}"><br>Defense</th>',
        f'<th><img src="{p.get("AB_CDB","")}" width="{px}"><br>Attaque</th>',
        f'<th><img src="{p.get("DB_CDB","")}" width="{px}"><br>Defense</th>',
        f'<th><img src="{p.get("AR_EG","")}" width="{px}"><br>Attaque</th>',
        f'<th><img src="{p.get("DR_EG","")}" width="{px}"><br>Defense</th>',
        f'<th><img src="{p.get("AB_EG","")}" width="{px}"><br>Attaque</th>',
        f'<th><img src="{p.get("DB_EG","")}" width="{px}"><br>Defense</th>',
        "</tr>",
        "</thead>",
        "<tbody>",
    ]

    col_h = df_latest.columns[0]
    col_p = df_latest.columns[1]
    col_age = df_latest.columns[2]

    for _, row in df_latest.iterrows():
        age_std = normaliser_age(row[col_age])
        bg_color, text_color = PALETTE_AGES.get(age_std, ("#333333", "#FFFFFF"))

        style_ligne = f"background-color: {bg_color}; color: {text_color}; font-weight: bold;"

        lignes.append(f'<tr style="{style_ligne}">')

        # Horodateur au format DD/MM/YYYY
        date_val = row[col_h]
        date_str = (
            date_val.strftime("%d/%m/%Y")
            if isinstance(date_val, pd.Timestamp)
            else str(date_val)
        )

        lignes.append(f"<td>{date_str}</td>")
        lignes.append(f"<td>{row[col_p]}</td>")
        lignes.append(f"<td>{age_std}</td>")

        for col in df_latest.columns[3:9]:
            vals = str(row[col]).split("-")
            att = vals[0].strip() if len(vals) > 0 else str(row[col])
            def_ = vals[1].strip() if len(vals) > 1 else ""
            lignes.append(f"<td>{att}</td><td>{def_}</td>")

        lignes.append("</tr>")

    lignes.extend(["</tbody>", "</table>", "</div>"])
    st.markdown("".join(lignes), unsafe_allow_html=True)


# -----------------------------------------------------------------------------
# 5. APPLICATION PRINCIPALE
# -----------------------------------------------------------------------------
try:
    df_reponses, df_membres = charger_donnees()

    df_membres.columns = [col.strip() for col in df_membres.columns]
    col_nom_membre = df_membres.columns[0]
    col_presence = df_membres.columns[3]

    df_actifs = df_membres[df_membres[col_presence] != "HG"].copy()
    membres_actifs_liste = sorted(
        [str(nom).strip() for nom in df_actifs[col_nom_membre].dropna().unique()]
    )

    tab_graph, tab_table = st.tabs(
        ["📈 Graphiques Membre (Grille 2x2)", "🏆 Tableau Comparatif Guilde"]
    )

    # -------------------------------------------------------------------------
    # ONGLET 1 : GRAPHIQUES CHRONOLOGIQUES
    # -------------------------------------------------------------------------
    with tab_graph:
        col_sel1, _ = st.columns([2, 4])
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
                df_joueur[col_date], dayfirst=True, errors="coerce"
            )
            df_joueur = df_joueur.dropna(subset=[col_date]).sort_values(
                by=col_date
            )

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

            logo_tous = convertir_image_base64(LOGOS_GRAPHIQUES["TOUS"])
            logo_basic = convertir_image_base64(LOGOS_GRAPHIQUES["BASIC"])
            logo_cdb = convertir_image_base64(LOGOS_GRAPHIQUES["CDB"])
            logo_eg = convertir_image_base64(LOGOS_GRAPHIQUES["EG"])

            titre_tous = (
                f"<img src='{logo_tous}' width='28'> TOUS LES BONUS"
                if logo_tous
                else "🌐 TOUS LES BONUS"
            )
            titre_basic = (
                f"<img src='{logo_basic}' width='28'> BONUS BASIC"
                if logo_basic
                else "⚔️ BONUS BASIC"
            )
            titre_cdb = (
                f"<img src='{logo_cdb}' width='28'> BONUS CDB"
                if logo_cdb
                else "🏰 BONUS CDB"
            )
            titre_eg = (
                f"<img src='{logo_eg}' width='28'> BONUS EG"
                if logo_eg
                else "🏛️ BONUS EG"
            )

            row1_col1, row1_col2 = st.columns(2)
            row2_col1, row2_col2 = st.columns(2)

            with row1_col1:
                with st.container(border=True):
                    st.markdown(f"#### {titre_tous}", unsafe_allow_html=True)
                    st.altair_chart(
                        generer_chart_altair(df_long, noms_bonus),
                        use_container_width=True,
                    )

            with row1_col2:
                with st.container(border=True):
                    st.markdown(f"#### {titre_basic}", unsafe_allow_html=True)
                    st.altair_chart(
                        generer_chart_altair(
                            df_long, ["Att R", "Def R", "Att B", "Def B"]
                        ),
                        use_container_width=True,
                    )

            with row2_col1:
                with st.container(border=True):
                    st.markdown(f"#### {titre_cdb}", unsafe_allow_html=True)
                    st.altair_chart(
                        generer_chart_altair(
                            df_long,
                            ["Att CDB R", "Def CDB R", "Att CDB B", "Def CDB B"],
                        ),
                        use_container_width=True,
                    )

            with row2_col2:
                with st.container(border=True):
                    st.markdown(f"#### {titre_eg}", unsafe_allow_html=True)
                    st.altair_chart(
                        generer_chart_altair(
                            df_long,
                            ["Att EG R", "Def EG R", "Att EG B", "Def EG B"],
                        ),
                        use_container_width=True,
                    )

    # -------------------------------------------------------------------------
    # ONGLET 2 : TABLEAU DU CLASSEMENT
    # -------------------------------------------------------------------------
    with tab_table:
        st.markdown("### 🏆 Classement Guilde — Dernières Saisies")

        df_rep_clean = df_reponses.copy()
        col_d = df_rep_clean.columns[0]
        col_p = df_rep_clean.columns[1]
        col_age = df_rep_clean.columns[2]

        df_rep_clean[col_d] = pd.to_datetime(
            df_rep_clean[col_d], dayfirst=True, errors="coerce"
        )
        df_rep_clean = df_rep_clean.dropna(subset=[col_d])
        df_rep_clean[col_p] = df_rep_clean[col_p].astype(str).str.strip()

        # Récupération de la dernière saisie par pseudo
        df_latest = (
            df_rep_clean.sort_values(col_d).groupby(col_p).last().reset_index()
        )
        df_latest = df_latest[df_latest[col_p].isin(membres_actifs_liste)].copy()

        # Reconstitution de l'ordre exact des colonnes : [Horodateur, Pseudo, Age, Bonus...]
        cols_ordonnees = [col_d, col_p, col_age] + list(df_rep_clean.columns[3:])
        df_latest = df_latest[cols_ordonnees]

        # Tri par âge décroissant (22- DEC -> 01- ADF) puis par Pseudo
        def extraire_num_age(age_val):
            std = normaliser_age(age_val)
            match = re.search(r"^\d+", std)
            return int(match.group()) if match else 0

        df_latest["NUM_AGE"] = df_latest[col_age].apply(extraire_num_age)
        df_latest = df_latest.sort_values(
            by=["NUM_AGE", col_p], ascending=[False, True]
        ).drop(columns=["NUM_AGE"])

        afficher_tableau_html(df_latest)

except Exception as e:
    st.error(f"Erreur de chargement : {e}")
