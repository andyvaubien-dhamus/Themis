import json
import os
from datetime import datetime, timedelta

import pandas as pd
import sqlite3
import streamlit as st
import streamlit.components.v1 as components
from PIL import Image

# Variables "de sécurité" pour contourner un bug d'affichage du HTML dans le chat
D, H1, H2, H3, P, TABLE, TR, TD, TH, STRONG, EM, UL, LI, STYLE = (
    "div",
    "h1",
    "h2",
    "h3",
    "p",
    "table",
    "tr",
    "td",
    "th",
    "strong",
    "em",
    "ul",
    "li",
    "style",
)

# ---------------------------------------------------------------------------
# Valeurs par défaut utilisées uniquement lors de la toute première
# initialisation de la base (table "entreprise"). Ensuite, ces informations
# sont modifiables directement dans l'appli via le menu "⚙️ Paramètres de
# l'entreprise", sans toucher au code.
# ---------------------------------------------------------------------------
# ---------------------------------------------------------------------------
# Identité visuelle "Themis" — palette pastel sobre, logo, typographie.
# Le logo doit se trouver à côté de ce script sous le nom "themis.png"
# (fourni séparément). L'icône "Themis.ico" sert à personnaliser un raccourci
# de bureau / barre des tâches (voir instructions fournies avec le logo).
# ---------------------------------------------------------------------------
APP_DIR = os.path.dirname(os.path.abspath(__file__))
LOGO_PATH = os.path.join(APP_DIR, "themis.png")

THEME = {
    "cream": "#FAF7F2",
    "cream_card": "#FFFFFF",
    "sage": "#6E8A85",
    "sage_dark": "#55706B",
    "sage_light": "#C4D2C2",
    "sage_pale": "#E7EEE6",
    "blush": "#EFC9C3",
    "blush_dark": "#D9A79F",
    "blush_pale": "#FBEDEA",
    "text": "#3D3D3D",
    "text_muted": "#7A7A7A",
}


def inject_theme_css():
    """Injecte le thème visuel Themis (police, palette pastel, navigation,
    cartes) par-dessus les styles par défaut de Streamlit."""
    st.markdown(
        f"""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Manrope:wght@400;500;600;700;800&display=swap');

        html, body, [class*="css"] {{
            font-family: 'Manrope', -apple-system, BlinkMacSystemFont, sans-serif;
        }}

        /* Fond général de l'application */
        .stApp {{
            background-color: {THEME['cream']};
        }}

        /* Cacher l'habillage Streamlit par défaut pour un rendu "appli" */
        footer {{ visibility: hidden; }}
        #MainMenu {{ visibility: hidden; }}
        header[data-testid="stHeader"] {{ background-color: transparent; }}

        /* Barre latérale */
        section[data-testid="stSidebar"] {{
            background-color: {THEME['sage_pale']};
            border-right: 1px solid {THEME['sage_light']};
        }}
        section[data-testid="stSidebar"] .block-container {{
            padding-top: 1.5rem;
        }}

        /* Titres */
        h1, h2, h3 {{
            font-family: 'Manrope', sans-serif;
            font-weight: 700;
            color: {THEME['text']};
            letter-spacing: -0.01em;
        }}

        /* Boutons de navigation (sidebar) : pleine largeur, style pilule */
        section[data-testid="stSidebar"] .stButton > button {{
            width: 100%;
            text-align: left;
            border-radius: 10px;
            border: 1px solid transparent;
            padding: 0.55rem 0.9rem;
            font-weight: 600;
            font-size: 0.92rem;
            margin-bottom: 0.25rem;
            transition: all 0.15s ease-in-out;
            box-shadow: none;
        }}
        section[data-testid="stSidebar"] .stButton > button[kind="secondary"] {{
            background-color: transparent;
            color: {THEME['text']};
        }}
        section[data-testid="stSidebar"] .stButton > button[kind="secondary"]:hover {{
            background-color: {THEME['sage_light']};
            color: {THEME['text']};
            border-color: {THEME['sage_light']};
        }}
        section[data-testid="stSidebar"] .stButton > button[kind="primary"] {{
            background-color: {THEME['sage']};
            color: white;
            border-color: {THEME['sage']};
        }}
        section[data-testid="stSidebar"] .stButton > button[kind="primary"]:hover {{
            background-color: {THEME['sage_dark']};
            border-color: {THEME['sage_dark']};
        }}

        /* Boutons génériques dans le corps de la page */
        .stButton > button[kind="primary"] {{
            background-color: {THEME['sage']};
            border-color: {THEME['sage']};
            border-radius: 8px;
        }}
        .stButton > button[kind="primary"]:hover {{
            background-color: {THEME['sage_dark']};
            border-color: {THEME['sage_dark']};
        }}
        .stButton > button[kind="secondary"] {{
            border-radius: 8px;
        }}

        /* Cartes (st.container(border=True)) */
        div[data-testid="stVerticalBlockBorderWrapper"] {{
            border-radius: 14px !important;
            border-color: {THEME['sage_light']} !important;
            background-color: {THEME['cream_card']};
        }}

        /* En-tête de page personnalisé */
        .themis-page-header {{
            display: flex;
            align-items: center;
            gap: 0.9rem;
            margin-bottom: 1.4rem;
        }}
        .themis-page-header .themis-icon {{
            font-size: 1.9rem;
            background-color: {THEME['blush_pale']};
            border-radius: 12px;
            width: 52px;
            height: 52px;
            display: flex;
            align-items: center;
            justify-content: center;
            flex-shrink: 0;
        }}
        .themis-page-header .themis-title {{
            font-size: 1.5rem;
            font-weight: 800;
            color: {THEME['text']};
            line-height: 1.2;
        }}
        .themis-page-header .themis-subtitle {{
            font-size: 0.88rem;
            color: {THEME['text_muted']};
            margin-top: 0.1rem;
        }}

        /* Cartes KPI (tableau de bord) */
        .themis-kpi {{
            background-color: {THEME['cream_card']};
            border: 1px solid {THEME['sage_light']};
            border-radius: 14px;
            padding: 1rem 1.1rem;
            height: 100%;
        }}
        .themis-kpi .themis-kpi-label {{
            font-size: 0.78rem;
            font-weight: 600;
            color: {THEME['text_muted']};
            text-transform: uppercase;
            letter-spacing: 0.03em;
        }}
        .themis-kpi .themis-kpi-value {{
            font-size: 1.6rem;
            font-weight: 800;
            color: {THEME['sage_dark']};
            margin-top: 0.15rem;
        }}

        /* Badges de statut */
        .themis-badge {{
            display: inline-block;
            padding: 0.15rem 0.6rem;
            border-radius: 999px;
            font-size: 0.78rem;
            font-weight: 700;
        }}
        .themis-badge-sage {{ background-color: {THEME['sage_pale']}; color: {THEME['sage_dark']}; }}
        .themis-badge-blush {{ background-color: {THEME['blush_pale']}; color: {THEME['blush_dark']}; }}

        /* Sidebar : nom de l'application */
        .themis-brand-title {{
            font-size: 1.35rem;
            font-weight: 800;
            letter-spacing: 0.04em;
            color: {THEME['sage_dark']};
            text-align: center;
            margin-top: 0.4rem;
        }}
        .themis-brand-subtitle {{
            font-size: 0.75rem;
            color: {THEME['text_muted']};
            text-align: center;
            margin-bottom: 1.2rem;
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_header(icon, title, subtitle=None):
    """Affiche un en-tête de page cohérent (icône + titre + sous-titre)."""
    subtitle_html = (
        f'<div class="themis-subtitle">{subtitle}</div>' if subtitle else ""
    )
    st.markdown(
        f"""
        <div class="themis-page-header">
            <div class="themis-icon">{icon}</div>
            <div>
                <div class="themis-title">{title}</div>
                {subtitle_html}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


DEFAULT_ENTREPRISE_NOM = "LYSIS - Atelier Textile"
DEFAULT_ENTREPRISE_ADRESSE = "Capesterre-Belle-Eau, Guadeloupe"
DEFAULT_ENTREPRISE_SIRET = ""
DEFAULT_ENTREPRISE_RCS_RM = ""
DEFAULT_ENTREPRISE_FORME_JURIDIQUE = ""

DB_NAME = "devis_suivi.db"


def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # Table des devis
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS devis (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            numero_devis TEXT UNIQUE NOT NULL,
            date_creation TEXT NOT NULL,
            date_validite TEXT NOT NULL,
            client_nom TEXT NOT NULL,
            client_prenom TEXT NOT NULL,
            client_societe TEXT,
            client_adresse TEXT NOT NULL,
            client_telephone TEXT,
            client_email TEXT,
            montant_setup REAL NOT NULL,
            montant_abo REAL NOT NULL,
            pourcentage_acompte INTEGER NOT NULL,
            statut TEXT NOT NULL,
            sections_json TEXT
        )
    """)

    # Table dédiée aux factures (établissement et correction)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS factures (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            numero_facture TEXT UNIQUE NOT NULL,
            numero_devis TEXT NOT NULL,
            type_facture TEXT NOT NULL,
            date_facture TEXT NOT NULL,
            date_echeance TEXT NOT NULL,
            montant_ht REAL NOT NULL,
            statut TEXT NOT NULL
        )
    """)

    # Table des informations légales de l'entreprise (une seule ligne, id=1),
    # éditable depuis l'appli plutôt qu'en dur dans le code.
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS entreprise (
            id INTEGER PRIMARY KEY CHECK (id = 1),
            nom TEXT NOT NULL,
            adresse TEXT NOT NULL,
            siret TEXT,
            rcs_rm TEXT,
            forme_juridique TEXT
        )
    """)
    cursor.execute(
        """
        INSERT OR IGNORE INTO entreprise (id, nom, adresse, siret, rcs_rm, forme_juridique)
        VALUES (1, ?, ?, ?, ?, ?)
        """,
        (
            DEFAULT_ENTREPRISE_NOM,
            DEFAULT_ENTREPRISE_ADRESSE,
            DEFAULT_ENTREPRISE_SIRET,
            DEFAULT_ENTREPRISE_RCS_RM,
            DEFAULT_ENTREPRISE_FORME_JURIDIQUE,
        ),
    )

    try:
        cursor.execute("ALTER TABLE devis ADD COLUMN sections_json TEXT")
    except sqlite3.OperationalError:
        pass

    # Colonnes nécessaires aux avoirs (notes de crédit) : la facture d'origine
    # à laquelle l'avoir se rapporte, et le motif de l'avoir.
    try:
        cursor.execute("ALTER TABLE factures ADD COLUMN numero_facture_liee TEXT")
    except sqlite3.OperationalError:
        pass
    try:
        cursor.execute("ALTER TABLE factures ADD COLUMN motif TEXT")
    except sqlite3.OperationalError:
        pass

    # Colonnes nécessaires à l'archivage (soft delete) des devis : un devis
    # archivé n'apparaît plus dans les listes actives, mais reste consultable
    # et n'est jamais supprimé physiquement s'il est déjà rattaché à une
    # facture (intégrité des données).
    try:
        cursor.execute("ALTER TABLE devis ADD COLUMN archive INTEGER DEFAULT 0")
    except sqlite3.OperationalError:
        pass
    try:
        cursor.execute("ALTER TABLE devis ADD COLUMN motif_archivage TEXT")
    except sqlite3.OperationalError:
        pass

    conn.commit()
    conn.close()


def get_next_devis(conn):
    """Calcule le prochain numéro de devis au format DEV-YYYYMM-XX."""
    cursor = conn.cursor()
    today_str = datetime.today().strftime("%Y%m")
    pattern = f"DEV-{today_str}-%"

    cursor.execute(
        "SELECT numero_devis FROM devis WHERE numero_devis LIKE ? "
        "ORDER BY id DESC LIMIT 1",
        (pattern,),
    )
    res = cursor.fetchone()

    if res:
        try:
            last_seq = int(res[0].split("-")[-1])
            return f"DEV-{today_str}-{str(last_seq + 1).zfill(2)}"
        except (ValueError, IndexError):
            pass
    return f"DEV-{today_str}-01"


def get_next_avoir(conn):
    """Calcule le prochain numéro d'avoir au format AV-YYYYMM-XX."""
    cursor = conn.cursor()
    today_str = datetime.today().strftime("%Y%m")
    pattern = f"AV-{today_str}-%"

    cursor.execute(
        "SELECT numero_facture FROM factures WHERE numero_facture LIKE ? "
        "ORDER BY id DESC LIMIT 1",
        (pattern,),
    )
    res = cursor.fetchone()

    if res:
        try:
            last_seq = int(res[0].split("-")[-1])
            return f"AV-{today_str}-{str(last_seq + 1).zfill(2)}"
        except (ValueError, IndexError):
            pass
    return f"AV-{today_str}-01"


def get_entreprise_info(conn):
    """Récupère les informations légales de l'entreprise stockées en base."""
    cursor = conn.cursor()
    cursor.execute(
        "SELECT nom, adresse, siret, rcs_rm, forme_juridique FROM entreprise WHERE id = 1"
    )
    row = cursor.fetchone()
    if row:
        return {
            "nom": row[0] or "",
            "adresse": row[1] or "",
            "siret": row[2] or "Non renseigné",
            "rcs_rm": row[3] or "Non renseigné",
            "forme_juridique": row[4] or "Non renseigné",
        }
    return {
        "nom": "",
        "adresse": "",
        "siret": "Non renseigné",
        "rcs_rm": "Non renseigné",
        "forme_juridique": "Non renseigné",
    }


def text_to_html_list(text):
    """Transforme un texte à puces (lignes commençant par '-') en <ul><li>...</li></ul>."""
    if not text:
        return ""
    lines = text.strip().split("\n")
    html = f"<{UL}>"
    for line in lines:
        line = line.strip()
        if line.startswith("-"):
            line = line[1:].strip()
        if line:
            html += f"<{LI}>{line}</{LI}>"
    html += f"</{UL}>"
    return html


init_db()

# --- Icône de page : le logo Themis s'il est présent à côté du script,
#     sinon repli sur un emoji pour ne jamais faire planter l'appli. --------
try:
    _page_icon = Image.open(LOGO_PATH)
except Exception:
    _page_icon = "⚖️"

st.set_page_config(
    page_title="Themis",
    page_icon=_page_icon,
    layout="wide",
    initial_sidebar_state="expanded",
)

inject_theme_css()

# ---------------------------------------------------------------------------
# Navigation — remplace le menu déroulant classique par une barre latérale
# de type "app" moderne : logo, nom, puis une pile de boutons pleine largeur
# qui font office d'onglets, avec état actif mis en évidence par le CSS
# injecté plus haut. `choix` conserve les mêmes libellés que l'ancien menu
# pour ne rien changer au reste de la logique (le bloc if/elif ci-dessous).
# ---------------------------------------------------------------------------
NAV_ITEMS = [
    ("🧭", "Tableau de bord & Suivi"),
    ("✒️", "Créer / Modifier un devis"),
    ("🗃️", "🗄️ Archiver / Supprimer un devis"),
    ("⚖️", "Générer le Dossier Contractuel"),
    ("🧾", "Établir / Corriger une Facture"),
    ("🖨️", "Générer une Facture (PDF)"),
    ("🛠️", "⚙️ Paramètres de l'entreprise"),
]

if "nav_choice" not in st.session_state:
    st.session_state.nav_choice = NAV_ITEMS[0][1]

with st.sidebar:
    if os.path.exists(LOGO_PATH):
        col_logo_l, col_logo_c, col_logo_r = st.columns([1, 1, 1])
        with col_logo_c:
            st.image(LOGO_PATH, width=64)
    st.markdown('<div class="themis-brand-title">THEMIS</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="themis-brand-subtitle">Gestion commerciale &amp; documents</div>',
        unsafe_allow_html=True,
    )

    for icon, label in NAV_ITEMS:
        is_active = st.session_state.nav_choice == label
        display_label = label.replace("🗄️ ", "").replace("⚙️ ", "")
        if st.button(
            f"{icon}  {display_label}",
            key=f"nav_{label}",
            type="primary" if is_active else "secondary",
            use_container_width=True,
        ):
            st.session_state.nav_choice = label
            st.rerun()

choix = st.session_state.nav_choice

conn = sqlite3.connect(DB_NAME)

# Initialisation des variables de session
if "form_sections" not in st.session_state:
    st.session_state.form_sections = [{"title": "", "content": ""}]
if "form_key" not in st.session_state:
    st.session_state.form_key = 0
if "loaded_devis_id" not in st.session_state:
    st.session_state.loaded_devis_id = None
if "loaded_facture_num" not in st.session_state:
    st.session_state.loaded_facture_num = None
if "facture_form_key" not in st.session_state:
    st.session_state.facture_form_key = 0


# ---------------------------------------------------------------------------
# Tableau de bord
# ---------------------------------------------------------------------------
if choix == "Tableau de bord & Suivi":
    render_header("🧭", "Tableau de bord", "Vue d'ensemble de votre activité")

    df_devis = pd.read_sql_query(
        "SELECT * FROM devis WHERE archive = 0 ORDER BY id DESC", conn
    )
    df_devis_archives = pd.read_sql_query(
        "SELECT * FROM devis WHERE archive = 1 ORDER BY id DESC", conn
    )
    df_fact = pd.read_sql_query("SELECT * FROM factures ORDER BY id DESC", conn)

    ca_facture = df_fact["montant_ht"].sum() if not df_fact.empty else 0.0

    kpi1, kpi2, kpi3, kpi4 = st.columns(4)
    kpi_data = [
        (kpi1, "Devis actifs", len(df_devis)),
        (kpi2, "Devis archivés", len(df_devis_archives)),
        (kpi3, "Factures émises", len(df_fact)),
        (kpi4, "Facturé (H.T.)", f"{ca_facture:.2f} €"),
    ]
    for col, label, value in kpi_data:
        with col:
            st.markdown(
                f"""
                <div class="themis-kpi">
                    <div class="themis-kpi-label">{label}</div>
                    <div class="themis-kpi-value">{value}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    st.markdown("<br>", unsafe_allow_html=True)

    st.markdown("#### 📋 Devis actifs")
    if not df_devis.empty:
        st.dataframe(
            df_devis[[
                "numero_devis",
                "date_creation",
                "client_societe",
                "client_nom",
                "montant_setup",
                "statut",
            ]],
            width="stretch",
        )
    else:
        st.info("Aucun devis actif enregistré pour le moment.")

    with st.expander(f"🗄️ Devis archivés ({len(df_devis_archives)})"):
        if not df_devis_archives.empty:
            st.dataframe(
                df_devis_archives[[
                    "numero_devis",
                    "date_creation",
                    "client_societe",
                    "client_nom",
                    "montant_setup",
                    "statut",
                    "motif_archivage",
                ]],
                width="stretch",
            )
            st.caption(
                "Gérez la restauration ou la suppression définitive de ces devis "
                "dans le menu \"🗄️ Archiver / Supprimer un devis\"."
            )
        else:
            st.info("Aucun devis archivé.")

    st.markdown("#### 🧾 Factures émises")
    if not df_fact.empty:
        st.dataframe(
            df_fact[[
                "numero_facture",
                "numero_devis",
                "type_facture",
                "date_facture",
                "montant_ht",
                "statut",
            ]],
            width="stretch",
        )
    else:
        st.info("Aucune facture enregistrée pour le moment.")
        
    # ---------------------------------------------------------
    # NOUVEAU BLOC : Mettre à jour le statut d'un devis actif
    # ---------------------------------------------------------
    st.markdown("---")
    st.markdown("#### ✅ Validation et suivi des devis")
    
    if not df_devis.empty:
        with st.form("form_valider_devis"):
            col_statut1, col_statut2 = st.columns(2)
            with col_statut1:
                devis_cible = st.selectbox(
                    "Sélectionner le devis à mettre à jour", 
                    df_devis["numero_devis"].tolist()
                )
            with col_statut2:
                nouveau_statut = st.selectbox(
                    "Nouveau statut", 
                    ["Brouillon", "Envoyé au client", "Validé & Signé", "En cours de réalisation"]
                )
            
            btn_valider_statut = st.form_submit_button("Enregistrer le nouveau statut", type="primary")
            
        if btn_valider_statut:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE devis SET statut = ? WHERE numero_devis = ?", 
                (nouveau_statut, devis_cible)
            )
            conn.commit()
            st.success(f"Le statut du devis {devis_cible} est maintenant : {nouveau_statut}")
            st.rerun()    


# ---------------------------------------------------------------------------
# Créer / Modifier un devis
# ---------------------------------------------------------------------------
elif choix == "Créer / Modifier un devis":
    render_header("✒️", "Devis", "Créez un nouveau devis ou corrigez un devis existant")

    if "success_msg" in st.session_state:
        st.success(st.session_state.success_msg)
        del st.session_state.success_msg

    mode = st.radio(
        "Que souhaitez-vous faire ?",
        ["Créer un nouveau devis", "Modifier un devis existant (Correction)"],
        horizontal=True,
    )
    loaded_devis = None

    if mode == "Modifier un devis existant (Correction)":
        liste_devis = pd.read_sql_query(
            "SELECT numero_devis, client_societe FROM devis "
            "WHERE archive = 0 ORDER BY id DESC",
            conn,
        )
        if not liste_devis.empty:
            choix_mod = st.selectbox(
                "Sélectionnez le devis à corriger :", liste_devis["numero_devis"]
            )
            loaded_devis = pd.read_sql_query(
                "SELECT * FROM devis WHERE numero_devis = ?",
                conn,
                params=(choix_mod,),
            ).iloc[0]

            if st.session_state.loaded_devis_id != choix_mod:
                try:
                    st.session_state.form_sections = json.loads(
                        loaded_devis["sections_json"]
                    )
                    if not st.session_state.form_sections:
                        st.session_state.form_sections = [{"title": "", "content": ""}]
                except (TypeError, json.JSONDecodeError):
                    st.session_state.form_sections = [{"title": "", "content": ""}]

                st.session_state.loaded_devis_id = choix_mod
                st.session_state.form_key += 1
                st.rerun()
        else:
            st.info("Aucun devis n'est enregistré.")
    else:
        if st.session_state.loaded_devis_id is not None:
            st.session_state.loaded_devis_id = None
            st.session_state.form_sections = [{"title": "", "content": ""}]
            st.session_state.form_key += 1
            st.rerun()

    next_devis_num = get_next_devis(conn)

    if loaded_devis is not None:
        val_numero = loaded_devis["numero_devis"]
        try:
            val_date_c = datetime.strptime(
                loaded_devis["date_creation"], "%Y-%m-%d"
            ).date()
        except ValueError:
            val_date_c = datetime.today()
        val_societe = loaded_devis["client_societe"]
        val_nom = loaded_devis["client_nom"]
        val_prenom = loaded_devis["client_prenom"]
        val_adresse = loaded_devis["client_adresse"]
        val_tel = loaded_devis["client_telephone"]
        val_email = loaded_devis["client_email"]
        val_setup = float(loaded_devis["montant_setup"])
        val_abo = float(loaded_devis["montant_abo"])
        val_acompte = int(loaded_devis["pourcentage_acompte"])
    else:
        val_numero = next_devis_num
        val_date_c = datetime.today()
        val_societe = val_nom = val_prenom = val_adresse = val_tel = val_email = ""
        val_setup = val_abo = 0.0
        val_acompte = 30

    with st.form(f"form_devis_{st.session_state.form_key}"):
        col1, col2 = st.columns(2)
        with col1:
            if loaded_devis is not None:
                st.text_input("Numéro de Devis", value=val_numero, disabled=True)
                numero_devis = val_numero
            else:
                numero_devis = st.text_input(
                    "Numéro de Devis (Auto-incrémenté)", value=val_numero
                )

            date_creation = st.date_input("Date de création", value=val_date_c)
            date_validite = date_creation + timedelta(days=30)
            st.info(
                "📅 Date de validité (30 jours) :"
                f" **{date_validite.strftime('%d/%m/%Y')}**"
            )

        with col2:
            client_societe = st.text_input(
                "Nom de l'Entreprise / Société", value=val_societe
            )
            client_nom = st.text_input("Nom du contact", value=val_nom)
            client_prenom = st.text_input("Prénom du contact", value=val_prenom)

        client_adresse = st.text_area("Adresse complète", value=val_adresse)

        col3, col4 = st.columns(2)
        with col3:
            client_telephone = st.text_input("Téléphone", value=val_tel)
            client_email = st.text_input("Email", value=val_email)
        with col4:
            montant_setup = st.number_input(
                "Montant Setup (H.T.) en €", value=val_setup, format="%.2f"
            )
            montant_abo = st.number_input(
                "Montant Abonnement (H.T.) en €", value=val_abo, format="%.2f"
            )
            pourcentage_acompte = st.slider(
                "Pourcentage d'acompte (%)", 0, 50, val_acompte
            )

        st.markdown("---")
        st.subheader(
            "📝 Édition des titres et contenus de l'Annexe 1 (Cahier des Charges)"
        )

        updated_sections = []
        for i, sec in enumerate(st.session_state.form_sections):
            st.markdown(f"**Bloc {i + 1}**")
            new_title = st.text_input(
                f"Titre de la section {i + 1}",
                value=sec["title"],
                key=f"sec_title_{st.session_state.form_key}_{i}",
            )
            new_content = st.text_area(
                f"Contenu de la section {i + 1} (points à puces avec des tirets -)",
                value=sec["content"],
                key=f"sec_content_{st.session_state.form_key}_{i}",
            )
            updated_sections.append({"title": new_title, "content": new_content})

        st.markdown("<br><br>", unsafe_allow_html=True)

        c_btn1, c_btn2, c_btn3 = st.columns([2, 1, 1])
        with c_btn1:
            btn_label = (
                "💾 Enregistrer la modification"
                if loaded_devis is not None
                else "💾 Enregistrer le nouveau devis"
            )
            submitted = st.form_submit_button(btn_label, type="primary")
        with c_btn2:
            add_sec = st.form_submit_button("➕ Ajouter une section")
        with c_btn3:
            del_sec = st.form_submit_button("🗑️ Retirer section")

    if add_sec:
        for i in range(len(st.session_state.form_sections)):
            st.session_state.form_sections[i]["title"] = st.session_state[
                f"sec_title_{st.session_state.form_key}_{i}"
            ]
            st.session_state.form_sections[i]["content"] = st.session_state[
                f"sec_content_{st.session_state.form_key}_{i}"
            ]
        st.session_state.form_sections.append({"title": "", "content": ""})
        st.rerun()

    if del_sec and len(st.session_state.form_sections) > 1:
        for i in range(len(st.session_state.form_sections)):
            st.session_state.form_sections[i]["title"] = st.session_state[
                f"sec_title_{st.session_state.form_key}_{i}"
            ]
            st.session_state.form_sections[i]["content"] = st.session_state[
                f"sec_content_{st.session_state.form_key}_{i}"
            ]
        st.session_state.form_sections.pop()
        st.rerun()

    if submitted:
        try:
            sections_str = json.dumps(updated_sections)
            cursor = conn.cursor()

            if loaded_devis is not None:
                cursor.execute(
                    """
                    UPDATE devis
                    SET date_creation=?, date_validite=?, client_nom=?, client_prenom=?, client_societe=?,
                        client_adresse=?, client_telephone=?, client_email=?, montant_setup=?, montant_abo=?,
                        pourcentage_acompte=?, sections_json=?
                    WHERE numero_devis=?
                    """,
                    (
                        str(date_creation),
                        str(date_validite),
                        client_nom,
                        client_prenom,
                        client_societe,
                        client_adresse,
                        client_telephone,
                        client_email,
                        montant_setup,
                        montant_abo,
                        pourcentage_acompte,
                        sections_str,
                        numero_devis,
                    ),
                )
                conn.commit()
                st.session_state.success_msg = (
                    f"✅ Le devis {numero_devis} a été modifié avec succès !"
                )
            else:
                cursor.execute(
                    """
                    INSERT INTO devis (numero_devis, date_creation, date_validite, client_nom, client_prenom,
                        client_societe, client_adresse, client_telephone, client_email, montant_setup,
                        montant_abo, pourcentage_acompte, statut, sections_json)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'Brouillon', ?)
                    """,
                    (
                        numero_devis,
                        str(date_creation),
                        str(date_validite),
                        client_nom,
                        client_prenom,
                        client_societe,
                        client_adresse,
                        client_telephone,
                        client_email,
                        montant_setup,
                        montant_abo,
                        pourcentage_acompte,
                        sections_str,
                    ),
                )
                conn.commit()
                st.session_state.success_msg = (
                    f"✅ Le devis {numero_devis} a été enregistré avec succès !"
                )

            st.session_state.loaded_devis_id = None
            st.session_state.form_sections = [{"title": "", "content": ""}]
            st.session_state.form_key += 1
            st.rerun()

        except Exception as e:
            st.error(f"Erreur SQL : {e}")


# ---------------------------------------------------------------------------
# Archiver / Supprimer un devis
# ---------------------------------------------------------------------------
elif choix == "🗄️ Archiver / Supprimer un devis":
    render_header("🗃️", "Archives", "Archivage et suppression définitive des devis")
    st.markdown(
        "Un devis refusé ou annulé n'a pas à être conservé indéfiniment dans vos "
        "listes actives, mais il vaut mieux l'**archiver** plutôt que le "
        "supprimer : cela évite de casser les factures déjà rattachées et garde "
        "une trace pour votre suivi commercial. La suppression définitive reste "
        "possible, mais seulement si aucune facture n'y est rattachée."
    )

    if "archive_success_msg" in st.session_state:
        st.success(st.session_state.archive_success_msg)
        del st.session_state.archive_success_msg

    # -----------------------------------------------------------------
    # Archiver un devis actif
    # -----------------------------------------------------------------
    st.markdown("### Archiver un devis actif")
    df_devis_actifs = pd.read_sql_query(
        "SELECT numero_devis, client_societe, client_nom, montant_setup FROM devis "
        "WHERE archive = 0 ORDER BY id DESC",
        conn,
    )
    if not df_devis_actifs.empty:
        choix_archive = st.selectbox(
            "Sélectionner le devis à archiver",
            df_devis_actifs["numero_devis"].tolist(),
            key="select_devis_a_archiver",
        )
        d_archive = df_devis_actifs[
            df_devis_actifs["numero_devis"] == choix_archive
        ].iloc[0]

        nb_factures_liees = pd.read_sql_query(
            "SELECT COUNT(*) as n FROM factures WHERE numero_devis = ?",
            conn,
            params=(choix_archive,),
        ).iloc[0]["n"]
        if nb_factures_liees > 0:
            st.info(
                f"ℹ️ {nb_factures_liees} facture(s) sont déjà rattachées à ce "
                "devis. L'archivage n'affecte pas ces factures ; seule la "
                "suppression définitive serait bloquée."
            )

        with st.form("form_archiver_devis"):
            nouveau_statut = st.selectbox(
                "Motif de l'archivage (statut appliqué au devis)",
                ["Refusé", "Annulé", "Sans suite", "Autre"],
            )
            motif_archivage = st.text_area(
                "Précisions (optionnel)",
                placeholder="ex. Le client a choisi un autre prestataire...",
            )
            submitted_archive = st.form_submit_button(
                "🗄️ Archiver ce devis", type="primary"
            )

        if submitted_archive:
            cursor = conn.cursor()
            cursor.execute(
                """
                UPDATE devis
                SET archive = 1, statut = ?, motif_archivage = ?
                WHERE numero_devis = ?
                """,
                (nouveau_statut, motif_archivage.strip(), choix_archive),
            )
            conn.commit()
            st.session_state.archive_success_msg = (
                f"✅ Le devis {choix_archive} a été archivé (statut : {nouveau_statut})."
            )
            st.rerun()
    else:
        st.info("Aucun devis actif à archiver.")

    st.markdown("---")

    # -----------------------------------------------------------------
    # Restaurer ou supprimer définitivement un devis archivé
    # -----------------------------------------------------------------
    st.markdown("### Devis archivés")
    df_devis_archives = pd.read_sql_query(
        "SELECT numero_devis, client_societe, client_nom, statut, motif_archivage "
        "FROM devis WHERE archive = 1 ORDER BY id DESC",
        conn,
    )
    if not df_devis_archives.empty:
        choix_restaure = st.selectbox(
            "Sélectionner un devis archivé",
            df_devis_archives["numero_devis"].tolist(),
            key="select_devis_archive",
        )
        d_restaure = df_devis_archives[
            df_devis_archives["numero_devis"] == choix_restaure
        ].iloc[0]
        st.write(
            f"**Client :** {d_restaure['client_societe']} — "
            f"**Statut :** {d_restaure['statut']} — "
            f"**Motif :** {d_restaure['motif_archivage'] or 'Non précisé'}"
        )

        col_restore, col_delete = st.columns(2)
        with col_restore:
            if st.button("♻️ Restaurer ce devis (le rendre actif)"):
                cursor = conn.cursor()
                cursor.execute(
                    "UPDATE devis SET archive = 0 WHERE numero_devis = ?",
                    (choix_restaure,),
                )
                conn.commit()
                st.session_state.archive_success_msg = (
                    f"✅ Le devis {choix_restaure} a été restauré parmi les devis actifs."
                )
                st.rerun()

        with col_delete:
            nb_factures_restaure = pd.read_sql_query(
                "SELECT COUNT(*) as n FROM factures WHERE numero_devis = ?",
                conn,
                params=(choix_restaure,),
            ).iloc[0]["n"]

            if nb_factures_restaure > 0:
                st.error(
                    f"🔒 Suppression impossible : {nb_factures_restaure} "
                    "facture(s) sont rattachées à ce devis."
                )
            else:
                confirme_suppression = st.checkbox(
                    "Je confirme vouloir supprimer définitivement ce devis "
                    "(action irréversible).",
                    key="confirme_suppr_devis",
                )
                if st.button("🗑️ Supprimer définitivement", disabled=not confirme_suppression):
                    cursor = conn.cursor()
                    cursor.execute(
                        "DELETE FROM devis WHERE numero_devis = ?", (choix_restaure,)
                    )
                    conn.commit()
                    st.session_state.archive_success_msg = (
                        f"🗑️ Le devis {choix_restaure} a été supprimé définitivement."
                    )
                    st.rerun()
    else:
        st.info("Aucun devis archivé pour le moment.")


# ---------------------------------------------------------------------------
# Générer le dossier contractuel
# ---------------------------------------------------------------------------
elif choix == "Générer le Dossier Contractuel":
    render_header("⚖️", "Dossier Contractuel", "Devis, bon de commande, CGV, cahier des charges et annexes")
    df = pd.read_sql_query(
        "SELECT numero_devis, client_societe, client_nom FROM devis WHERE archive = 0",
        conn,
    )

    if not df.empty:
        choix_devis = st.selectbox(
            "Sélectionner le devis client", df["numero_devis"].tolist()
        )

        if choix_devis:
            query_client = "SELECT * FROM devis WHERE numero_devis = ?"
            df_client = pd.read_sql_query(query_client, conn, params=(choix_devis,))

            if not df_client.empty:
                d = df_client.iloc[0]
                entreprise_info = get_entreprise_info(conn)
                montant_setup = d["montant_setup"]
                pourcentage = d["pourcentage_acompte"]
                acompte_val = montant_setup * (pourcentage / 100)
                solde_val = montant_setup - acompte_val

                try:
                    sections_list = json.loads(d["sections_json"])
                except (TypeError, json.JSONDecodeError):
                    sections_list = []

                html_sections_blocs = ""
                for sec in sections_list:
                    if sec.get("title", "").strip() or sec.get("content", "").strip():
                        html_sections_blocs += (
                            f"<{H2}>{sec.get('title', '')}</{H2}>"
                            f"{text_to_html_list(sec.get('content', ''))}"
                        )

                dossier_html = f"""
                <{D} style="font-family: Arial, sans-serif; color: #333333;">
                    <{STYLE}>
                        .page-doc {{ width: 100%; max-width: 210mm; min-height: 297mm; padding: 20mm; margin: 20px auto; box-sizing: border-box; border: 1px solid #cbd5e0; background: #ffffff; box-shadow: 0 4px 6px rgba(0,0,0,0.1); border-radius: 8px; margin-bottom: 30px; }}
                        .page-doc {H1} {{ font-size: 18px; color: #1a365d; border-bottom: 2px solid #3182ce; padding-bottom: 5px; }}
                        .page-doc {H2} {{ font-size: 14px; color: #2b6cb0; margin-top: 15px; }}
                        .page-doc {P}, .page-doc {LI} {{ font-size: 12px; line-height: 1.5; }}
                        .box-info {{ border: 1px solid #cbd5e0; padding: 12px; border-radius: 5px; background: #f8fafc; margin-bottom: 15px; width: 48%; display: inline-block; vertical-align: top; box-sizing: border-box; }}
                        .table-devis {{ width: 100%; border-collapse: collapse; margin: 15px 0; }}
                        .table-devis {TH}, .table-devis {TD} {{ border: 1px solid #cbd5e0; padding: 8px; text-align: left; font-size: 12px; }}
                        .table-devis {TH} {{ background-color: #edf2f7; color: #1a365d; }}
                        .signatures-container {{ margin-top: 30px; width: 100%; }}
                        .sig-box-left {{ width: 45%; height: 70px; border: 1px dashed #a0aec0; padding: 8px; font-size: 11px; color: #718096; display: inline-block; box-sizing: border-box; }}
                        .sig-box-right {{ width: 45%; height: 70px; border: 1px dashed #a0aec0; padding: 8px; font-size: 11px; color: #718096; display: inline-block; float: right; box-sizing: border-box; }}
                    </{STYLE}>

                    <{D} class="page-doc">
                        <{TABLE} style="width: 100%; border: none; margin-bottom: 20px;">
                            <{TR} style="background: transparent;">
                                <{TD} style="border: none; vertical-align: top;">
                                    <{H2} style="margin: 0; color: #1a365d;">{entreprise_info['nom']}</{H2}>
                                    <{P} style="margin: 5px 0 0 0;">{entreprise_info['adresse']}</{P}>
                                    <{P}>Solutions logicielles sur-mesure</{P}>
                                    <{P} style="font-size: 10px; color: #666;">{entreprise_info['forme_juridique']}<br>
                                    SIRET : {entreprise_info['siret']}<br>
                                    {entreprise_info['rcs_rm']}</{P}>
                                </{TD}>
                                <{TD} style="border: none; text-align: right; vertical-align: top;">
                                    <{H1} style="margin: 0; border: none; font-size: 20px; color: #1a365d;">DEVIS N° {d['numero_devis']}</{H1}>
                                    <{P} style="margin: 5px 0 0 0;">Date : {d['date_creation']}</{P}>
                                    <{P}>Validité : {d['date_validite']}</{P}>
                                </{TD}>
                            </{TR}>
                        </{TABLE}>

                        <{D} style="margin-top: 20px;">
                            <{D} class="box-info">
                                <{H3} style="margin-top: 0; color: #2b6cb0; font-size: 13px;">Client :</{H3}>
                                <{P} style="margin: 0;"><{STRONG}>{d['client_societe']}</{STRONG}></{P}>
                                <{P}>{d['client_prenom']} {d['client_nom']}</{P}>
                                <{P}>{d['client_adresse']}</{P}>
                                <{P}>Tél : {d['client_telephone']} | Email : {d['client_email']}</{P}>
                            </{D}>
                            <{D} class="box-info" style="float: right;">
                                <{H3} style="margin-top: 0; color: #2b6cb0; font-size: 13px;">Modalités de règlement :</{H3}>
                                <{P} style="margin: 0;"><{STRONG}>Acompte ({d['pourcentage_acompte']}%) : {acompte_val:.2f} €</{STRONG}></{P}>
                                <{P}><{STRONG}>Solde : {solde_val:.2f} €</{STRONG}></{P}>
                                <{P}>Abonnement : {d['montant_abo']:.2f} € / mois</{P}>
                            </{D}>
                            <{D} style="clear: both;"></{D}>
                        </{D}>

                        <{TABLE} class="table-devis">
                            <{TR}>
                                <{TH}>Description de la Prestation</{TH}>
                                <{TH}>Qté</{TH}>
                                <{TH} style="text-align: right;">Prix H.T.</{TH}>
                                <{TH} style="text-align: right;">Total H.T.</{TH}>
                            </{TR}>
                            <{TR}>
                                <{TD}><{STRONG}>Forfait Setup & Création Initiale :</{STRONG}> Application sur-mesure</{TD}>
                                <{TD}>1</{TD}>
                                <{TD} style="text-align: right;">{montant_setup:.2f} €</{TD}>
                                <{TD} style="text-align: right;">{montant_setup:.2f} €</{TD}>
                            </{TR}>
                        </{TABLE}>

                        <{D} style="text-align: right; margin-top: 15px;">
                            <{P} style="font-size: 14px;"><{STRONG}>Total Frais de Création : {montant_setup:.2f} € H.T.</{STRONG}></{P}>
                            <{P} style="font-size: 10px; color: #666;"><{EM}>TVA non applicable, art. 293 B du CGI.</{EM}></{P}>
                        </{D}>

                        <{D} class="signatures-container">
                            <{P}><{STRONG}>Bon pour accord et engagement :</{STRONG}></{P}>
                            <{D} class="sig-box-left">Signature du Prestataire :</{D}>
                            <{D} class="sig-box-right">Signature & Cachet du Client :</{D}>
                            <{D} style="clear: both;"></{D}>
                        </{D}>
                    </{D}>

                    <{D} class="page-doc">
                        <{TABLE} style="width: 100%; border: none; margin-bottom: 20px;">
                            <{TR} style="background: transparent;">
                                <{TD} style="border: none; vertical-align: top;">
                                    <{H2} style="margin: 0; color: #1a365d;">{entreprise_info['nom']}</{H2}>
                                    <{P} style="margin: 5px 0 0 0;">{entreprise_info['adresse']}</{P}>
                                </{TD}>
                                <{TD} style="border: none; text-align: right; vertical-align: top;">
                                    <{H1} style="margin: 0; border: none; font-size: 20px; color: #1a365d;">BON DE COMMANDE N° {d['numero_devis'].replace("DEV", "BC")}</{H1}>
                                    <{P} style="margin: 5px 0 0 0;">Devis de référence : {d['numero_devis']} du {d['date_creation']}</{P}>
                                </{TD}>
                            </{TR}>
                        </{TABLE}>

                        <{D} class="box-info">
                            <{H3} style="margin-top: 0; color: #2b6cb0; font-size: 13px;">Client :</{H3}>
                            <{P} style="margin: 0;"><{STRONG}>{d['client_societe']}</{STRONG}></{P}>
                            <{P}>{d['client_prenom']} {d['client_nom']}</{P}>
                            <{P}>{d['client_adresse']}</{P}>
                            <{P}>Tél : {d['client_telephone']} | Email : {d['client_email']}</{P}>
                        </{D}>
                        <{D} style="clear: both;"></{D}>

                        <{H2}>Objet de la commande</{H2}>
                        <{P}>Le Client confirme, par le présent bon de commande, la commande ferme et
                        définitive de la prestation décrite au devis n° {d['numero_devis']} et à son
                        Annexe 1 (Cahier des Charges Fonctionnel), pour un montant de
                        <{STRONG}> {montant_setup:.2f} € H.T.</{STRONG}> au titre du forfait Setup &
                        Création Initiale, et un abonnement mensuel de
                        <{STRONG}> {d['montant_abo']:.2f} € H.T.</{STRONG}> à compter de la mise en
                        service de l'application.</{P}>

                        <{TABLE} class="table-devis">
                            <{TR}>
                                <{TH}>Élément</{TH}>
                                <{TH} style="text-align: right;">Montant H.T.</{TH}>
                            </{TR}>
                            <{TR}><{TD}>Acompte à la commande ({d['pourcentage_acompte']}%)</{TD}><{TD} style="text-align: right;">{acompte_val:.2f} €</{TD}></{TR}>
                            <{TR}><{TD}>Solde à la livraison</{TD}><{TD} style="text-align: right;">{solde_val:.2f} €</{TD}></{TR}>
                            <{TR}><{TD}>Abonnement mensuel (à compter de la mise en service)</{TD}><{TD} style="text-align: right;">{d['montant_abo']:.2f} €</{TD}></{TR}>
                        </{TABLE}>

                        <{P}>La signature du présent bon de commande vaut acceptation sans réserve des
                        Conditions Générales de Vente (Annexe 2) et engage le Client au versement de
                        l'acompte prévu ci-dessus, préalable au démarrage de la prestation.</{P}>

                        <{D} class="signatures-container">
                            <{P}><{STRONG}>Bon pour commande, le _____________________</{STRONG}></{P}>
                            <{D} class="sig-box-left">Pour le Prestataire<br>Signature :</{D}>
                            <{D} class="sig-box-right">Pour le Client<br>Signature & Cachet :</{D}>
                            <{D} style="clear: both;"></{D}>
                        </{D}>
                    </{D}>

                    <{D} class="page-doc">
                        <{H1}>ANNEXE 1 : Cahier des Charges Fonctionnel</{H1}>
                        <{P}>Client : <{STRONG}>{d['client_societe']}</{STRONG}></{P}>
                        <{P}>Le présent document définit le périmètre strict de l'application livrée
                        dans le cadre du devis n° {d['numero_devis']}. Il constitue le référentiel
                        technique et fonctionnel sur la base duquel la prestation est réalisée, et sur
                        la base duquel la recette de l'application sera effectuée à l'issue du
                        développement.</{P}>
                        {html_sections_blocs if html_sections_blocs else f"<{P}><{EM}>Aucune section détaillée n'a encore été renseignée pour ce devis.</{EM}></{P}>"}
                    </{D}>

                    <{D} class="page-doc">
                        <{H1}>ANNEXE 2 : Conditions Générales de Vente (CGV)</{H1}>

                        <{H2}>Article 1 : Objet</{H2}>
                        <{P}>Les présentes conditions générales de vente régissent les relations
                        contractuelles entre {entreprise_info['nom']} (ci-après « le Prestataire ») et le
                        Client, dans le cadre de la conception, du développement et de la mise à
                        disposition d'une solution logicielle sur-mesure, telle que définie au devis
                        n° {d['numero_devis']} et à son Annexe 1 (Cahier des Charges Fonctionnel). Toute
                        commande implique l'acceptation sans réserve des présentes CGV par le Client.</{P}>

                        <{H2}>Article 2 : Devis, commande et durée de validité</{H2}>
                        <{P}>Le devis est établi pour une durée de validité de trente (30) jours à compter
                        de sa date d'émission. La commande est réputée ferme et définitive à compter de la
                        signature du devis par le Client et du versement de l'acompte prévu à l'article 3.
                        Toute prestation complémentaire non prévue au devis initial fera l'objet d'un devis
                        additionnel.</{P}>

                        <{H2}>Article 3 : Prix et modalités de paiement</{H2}>
                        <{P}>Les prix sont exprimés en euros. Conformément à l'article 293 B du Code
                        général des impôts, la TVA n'est pas applicable. Les frais de création (« Setup »)
                        sont facturés en deux temps : un acompte de {d['pourcentage_acompte']}% à la
                        commande, exigible avant le démarrage des travaux, et un solde facturé à la
                        livraison de l'application, avant sa mise en production définitive. L'abonnement
                        mensuel de {d['montant_abo']:.2f} € couvre l'hébergement, la maintenance technique
                        et les mises à jour de l'application ; il est facturé mensuellement à compter de la
                        mise en service et reconductible tacitement, sauf résiliation dans les conditions de
                        l'article 10. Tout retard de paiement pourra entraîner la suspension des
                        prestations après mise en demeure restée infructueuse pendant quinze (15) jours.</{P}>

                        <{H2}>Article 4 : Délais d'exécution</{H2}>
                        <{P}>Les délais de réalisation communiqués par le Prestataire sont donnés à titre
                        indicatif et courent à compter de la réception de l'acompte et de l'ensemble des
                        éléments nécessaires au démarrage du projet (contenus, accès, validations). Ils
                        pourront être prolongés en cas de retard imputable au Client dans la fourniture de
                        ces éléments ou dans la validation des livrables intermédiaires.</{P}>

                        <{H2}>Article 5 : Obligations du Client</{H2}>
                        <{P}>Le Client s'engage à fournir dans les meilleurs délais l'ensemble des
                        informations, contenus, identifiants et accès nécessaires à la bonne exécution de
                        la prestation, à désigner un interlocuteur habilité à valider les livrables, et à
                        formuler ses observations dans un délai raisonnable afin de ne pas retarder le
                        projet. Le Client demeure seul responsable de la licéité des contenus qu'il fournit
                        et de leur conformité à la réglementation en vigueur.</{P}>

                        <{H2}>Article 6 : Obligations du Prestataire</{H2}>
                        <{P}>Le Prestataire s'engage à mettre en œuvre les moyens raisonnables et les
                        compétences nécessaires à la réalisation de la prestation conformément au cahier
                        des charges (Annexe 1), dans le respect des règles de l'art. Le Prestataire tient le
                        Client informé de l'avancement du projet et l'alerte sans délai en cas de difficulté
                        susceptible d'affecter les délais ou le périmètre convenu.</{P}>

                        <{H2}>Article 7 : Recette et livraison</{H2}>
                        <{P}>À l'issue du développement, l'application est mise à disposition du Client à
                        des fins de vérification et de recette, dans les conditions décrites en Annexe 3
                        (Procès-Verbal de Recette). L'absence de retour du Client dans un délai de dix (10)
                        jours ouvrés à compter de la mise à disposition vaut acceptation tacite de la
                        livraison.</{P}>

                        <{H2}>Article 8 : Propriété intellectuelle</{H2}>
                        <{P}>Le Prestataire demeure titulaire de l'ensemble des droits de propriété
                        intellectuelle attachés aux codes sources, briques logicielles, méthodes et
                        savoir-faire développés, y compris ceux développés spécifiquement pour le Client,
                        sauf stipulation contraire expresse figurant au devis. Le Client bénéficie, à
                        compter du complet paiement des sommes dues, d'un droit d'usage de l'application
                        pour ses besoins propres, non exclusif et non cessible. Les contenus fournis par le
                        Client (textes, images, marques, logo) restent sa propriété exclusive.</{P}>

                        <{H2}>Article 9 : Garantie et maintenance</{H2}>
                        <{P}>Le Prestataire garantit la correction, sans frais supplémentaires, des
                        anomalies ou dysfonctionnements bloquants signalés par le Client dans un délai de
                        trente (30) jours à compter de la recette, dès lors que ceux-ci résultent d'un
                        défaut de conception ou de réalisation imputable au Prestataire. Cette garantie ne
                        couvre pas les évolutions fonctionnelles, les demandes de nouvelles fonctionnalités,
                        ni les dysfonctionnements résultant d'une utilisation non conforme, d'une
                        modification effectuée par un tiers, ou d'un environnement technique du Client non
                        maîtrisé par le Prestataire. Au-delà de cette période, la maintenance corrective et
                        évolutive est couverte par l'abonnement mensuel visé à l'article 3.</{P}>

                        <{H2}>Article 10 : Résiliation</{H2}>
                        <{P}>L'abonnement mensuel peut être résilié par chacune des parties moyennant un
                        préavis écrit de trente (30) jours. En cas de manquement grave de l'une des parties
                        à ses obligations, non régularisé dans un délai de quinze (15) jours après mise en
                        demeure, l'autre partie pourra résilier le contrat de plein droit, sans préjudice de
                        tout dommage et intérêt éventuel. Les sommes dues au titre des prestations déjà
                        réalisées restent exigibles.</{P}>

                        <{H2}>Article 11 : Responsabilité</{H2}>
                        <{P}>La responsabilité du Prestataire ne pourra être engagée qu'en cas de faute
                        prouvée, et est limitée aux dommages directs, à l'exclusion de tout préjudice
                        indirect (perte d'exploitation, perte de données, perte de chiffre d'affaires,
                        préjudice commercial). En tout état de cause, la responsabilité totale du
                        Prestataire est plafonnée au montant total effectivement versé par le Client au
                        titre du devis concerné.</{P}>

                        <{H2}>Article 12 : Confidentialité et protection des données</{H2}>
                        <{P}>Chaque partie s'engage à conserver strictement confidentielles les
                        informations de nature commerciale, technique ou financière dont elle aurait
                        connaissance à l'occasion de l'exécution du contrat, et à ne les divulguer à aucun
                        tiers sans accord préalable écrit de l'autre partie. Le traitement des données à
                        caractère personnel réalisé dans le cadre de la prestation est effectué
                        conformément au Règlement Général sur la Protection des Données (RGPD) et à la loi
                        Informatique et Libertés.</{P}>

                        <{H2}>Article 13 : Force majeure</{H2}>
                        <{P}>Aucune des parties ne pourra être tenue responsable de l'inexécution de ses
                        obligations si celle-ci résulte d'un cas de force majeure au sens de l'article
                        1218 du Code civil et de la jurisprudence des tribunaux français.</{P}>

                        <{H2}>Article 14 : Droit applicable et litiges</{H2}>
                        <{P}>Les présentes CGV sont soumises au droit français. En cas de différend relatif
                        à leur interprétation ou à leur exécution, les parties s'efforceront de trouver une
                        solution amiable avant toute action contentieuse. À défaut d'accord amiable, les
                        tribunaux compétents seront ceux du ressort du siège du Prestataire, sauf
                        disposition d'ordre public contraire.</{P}>
                    </{D}>

                    <{D} class="page-doc">
                        <{H1}>ANNEXE 3 : PROCÈS-VERBAL DE RECETTE</{H1}>

                        <{H2}>Objet</{H2}>
                        <{P}>Le présent procès-verbal a pour objet de constater la vérification, par le
                        Client <{STRONG}>{d['client_societe']}</{STRONG}>, de la conformité de l'application
                        livrée par le Prestataire au titre du devis n° {d['numero_devis']}, au regard des
                        spécifications décrites en Annexe 1 (Cahier des Charges Fonctionnel).</{P}>

                        <{H2}>Vérifications effectuées</{H2}>
                        <{P}>Le Client déclare avoir procédé, seul ou avec l'assistance du Prestataire, aux
                        vérifications suivantes :</{P}>
                        <{UL}>
                            <{LI}>Contrôle du bon fonctionnement des fonctionnalités décrites en Annexe 1</{LI}>
                            <{LI}>Vérification de l'accessibilité et de la prise en main de l'application</{LI}>
                            <{LI}>Contrôle de la cohérence des contenus et informations intégrées</{LI}>
                            <{LI}>Test des principaux parcours d'utilisation de l'application</{LI}>
                        </{UL}>

                        <{H2}>Résultat de la recette</{H2}>
                        <{P}>(Cocher la mention applicable lors de l'impression ou de la signature du
                        document)</{P}>
                        <{TABLE} class="table-devis">
                            <{TR}>
                                <{TH} style="width: 15%;">☐</{TH}>
                                <{TD}>Recette prononcée <{STRONG}>sans réserve</{STRONG}> : l'application est
                                conforme au cahier des charges et est acceptée en l'état.</{TD}>
                            </{TR}>
                            <{TR}>
                                <{TH}>☐</{TH}>
                                <{TD}>Recette prononcée <{STRONG}>avec réserves</{STRONG}> : l'application est
                                acceptée sous réserve de la correction des anomalies listées ci-dessous, dans
                                les conditions de garantie prévues à l'Article 9 des CGV.</{TD}>
                            </{TR}>
                        </{TABLE}>

                        <{H2}>Liste des réserves éventuelles</{H2}>
                        <{TABLE} class="table-devis">
                            <{TR}>
                                <{TH}>N°</{TH}>
                                <{TH}>Description de l'anomalie</{TH}>
                                <{TH}>Date de correction prévue</{TH}>
                            </{TR}>
                            <{TR}><{TD}>1</{TD}><{TD}>&nbsp;</{TD}><{TD}>&nbsp;</{TD}></{TR}>
                            <{TR}><{TD}>2</{TD}><{TD}>&nbsp;</{TD}><{TD}>&nbsp;</{TD}></{TR}>
                            <{TR}><{TD}>3</{TD}><{TD}>&nbsp;</{TD}><{TD}>&nbsp;</{TD}></{TR}>
                        </{TABLE}>

                        <{H2}>Effets de la signature</{H2}>
                        <{P}>La signature du présent procès-verbal, avec ou sans réserve, emporte
                        acceptation de la livraison au sens de l'Article 7 des CGV et déclenche le point de
                        départ du délai de garantie prévu à l'Article 9 des CGV. À défaut de retour signé
                        du Client dans un délai de dix (10) jours ouvrés à compter de la mise à disposition
                        de l'application, la recette sera réputée acquise sans réserve.</{P}>

                        <{D} class="signatures-container" style="margin-top: 40px;">
                            <{P}><{STRONG}>Fait en deux exemplaires, le _____________________</{STRONG}></{P}>
                            <{D} class="sig-box-left">Pour le Prestataire<br>Nom et qualité :<br>Signature :</{D}>
                            <{D} class="sig-box-right">Pour le Client<br>Nom et qualité :<br>Signature :</{D}>
                            <{D} style="clear: both;"></{D}>
                        </{D}>
                    </{D}>

                    <{D} class="page-doc">
                        <{H1}>ANNEXE 4 : Contrat de Prestation et d'Abonnement</{H1}>

                        <{P}><{STRONG}>ENTRE LES SOUSSIGNÉS :</{STRONG}></{P}>
                        <{P}>{entreprise_info['nom']}, {entreprise_info['forme_juridique']}, dont le
                        siège est situé {entreprise_info['adresse']}, SIRET {entreprise_info['siret']},
                        {entreprise_info['rcs_rm']}, ci-après désigné « le Prestataire »,</{P}>
                        <{P}>ET</{P}>
                        <{P}><{STRONG}>{d['client_societe']}</{STRONG}>, {d['client_prenom']}
                        {d['client_nom']}, dont l'adresse est {d['client_adresse']}, ci-après désigné
                        « le Client »,</{P}>
                        <{P}><{EM}>Ci-après désignés ensemble « les Parties ».</{EM}></{P}>

                        <{P}>Le présent contrat a pour objet de formaliser, en complément du devis
                        n° {d['numero_devis']}, de son Annexe 1 (Cahier des Charges Fonctionnel) et des
                        Conditions Générales de Vente (Annexe 2), les conditions de réalisation de la
                        prestation de développement et les modalités de l'abonnement mensuel de
                        maintenance et d'hébergement.</{P}>

                        <{H2}>Article 1 : Objet</{H2}>
                        <{P}>Le Prestataire s'engage à développer, livrer, héberger et maintenir, pour le
                        compte du Client, l'application décrite en Annexe 1, et à fournir les
                        prestations d'hébergement et de maintenance associées à l'abonnement mensuel
                        prévu à l'article 3 des CGV.</{P}>

                        <{H2}>Article 2 : Durée</{H2}>
                        <{P}>Le présent contrat prend effet à sa date de signature. La phase de
                        développement se déroule jusqu'à la recette de l'application (Annexe 3).
                        L'abonnement mensuel prend effet à la mise en service de l'application et est
                        conclu pour une durée initiale de douze (12) mois, renouvelable ensuite par
                        tacite reconduction pour des périodes successives d'un (1) mois, sauf
                        résiliation dans les conditions de l'Article 6.</{P}>

                        <{H2}>Article 3 : Niveau de service (SLA)</{H2}>
                        <{P}>Le Prestataire s'engage sur les objectifs de service suivants pour
                        l'application hébergée, sauf cas de force majeure ou maintenance programmée
                        annoncée au moins 48 heures à l'avance :</{P}>
                        <{TABLE} class="table-devis">
                            <{TR}>
                                <{TH}>Niveau d'incident</{TH}>
                                <{TH}>Définition</{TH}>
                                <{TH}>Délai de prise en charge</{TH}>
                            </{TR}>
                            <{TR}>
                                <{TD}><{STRONG}>Bloquant</{STRONG}></{TD}>
                                <{TD}>Application inaccessible ou fonctionnalité essentielle inopérante</{TD}>
                                <{TD}>1 jour ouvré</{TD}>
                            </{TR}>
                            <{TR}>
                                <{TD}><{STRONG}>Majeur</{STRONG}></{TD}>
                                <{TD}>Fonctionnalité dégradée sans blocage total de l'application</{TD}>
                                <{TD}>3 jours ouvrés</{TD}>
                            </{TR}>
                            <{TR}>
                                <{TD}><{STRONG}>Mineur</{STRONG}></{TD}>
                                <{TD}>Anomalie sans impact significatif sur l'usage de l'application</{TD}>
                                <{TD}>10 jours ouvrés</{TD}>
                            </{TR}>
                        </{TABLE}>
                        <{P}>Les délais ci-dessus courent à compter du signalement de l'anomalie par le
                        Client au Prestataire, et correspondent à un délai de prise en charge (début du
                        diagnostic), non à une garantie de résolution dans ce délai pour les anomalies
                        complexes.</{P}>

                        <{H2}>Article 4 : Modalités financières</{H2}>
                        <{P}>Les modalités de prix et de facturation applicables au présent contrat sont
                        celles définies au devis n° {d['numero_devis']} et à l'Article 3 des Conditions
                        Générales de Vente (Annexe 2).</{P}>

                        <{H2}>Article 5 : Suspension du service</{H2}>
                        <{P}>Le Prestataire peut suspendre temporairement l'accès à l'application en cas
                        de maintenance programmée (avec information préalable du Client), d'impayé
                        persistant après mise en demeure restée infructueuse pendant quinze (15) jours
                        (conformément à l'Article 3 des CGV), ou de nécessité impérieuse liée à la
                        sécurité des systèmes. Le Prestataire informe le Client dans les meilleurs délais
                        de toute suspension et de sa durée prévisible.</{P}>

                        <{H2}>Article 6 : Résiliation</{H2}>
                        <{P}>L'abonnement mensuel peut être résilié par chacune des Parties dans les
                        conditions prévues à l'Article 10 des CGV (Annexe 2), à savoir moyennant un
                        préavis écrit de trente (30) jours, ou de plein droit en cas de manquement grave
                        non régularisé après mise en demeure.</{P}>

                        <{H2}>Article 7 : Réversibilité</{H2}>
                        <{P}>En cas de résiliation ou de non-renouvellement de l'abonnement, le
                        Prestataire s'engage à restituer au Client, dans un délai de trente (30) jours à
                        compter de la date d'effet de la résiliation, une exportation des données propres
                        au Client hébergées dans l'application, dans un format structuré et exploitable.
                        Cette réversibilité porte sur les données du Client ; elle ne confère aucun droit
                        sur le code source de l'application, dont la propriété reste régie par l'Article 8
                        des CGV.</{P}>

                        <{H2}>Article 8 : Confidentialité</{H2}>
                        <{P}>Les Parties demeurent tenues aux obligations de confidentialité prévues à
                        l'Article 12 des CGV (Annexe 2) ainsi que, le cas échéant, à l'Accord de
                        Confidentialité signé préalablement entre les Parties (Annexe 5).</{P}>

                        <{H2}>Article 9 : Hiérarchie contractuelle et divers</{H2}>
                        <{P}>En cas de contradiction entre les documents contractuels, l'ordre de
                        priorité suivant s'applique : (1) le présent Contrat de Prestation et
                        d'Abonnement, (2) le Bon de Commande signé, (3) les Conditions Générales de Vente
                        (Annexe 2), (4) le devis et son Annexe 1. Pour tout ce qui n'est pas prévu au
                        présent contrat, les dispositions des CGV s'appliquent. Le présent contrat est
                        soumis au droit français, dans les conditions de compétence juridictionnelle
                        prévues à l'Article 14 des CGV.</{P}>

                        <{D} class="signatures-container">
                            <{P}><{STRONG}>Fait en deux exemplaires, le _____________________</{STRONG}></{P}>
                            <{D} class="sig-box-left">Pour le Prestataire<br>Signature :</{D}>
                            <{D} class="sig-box-right">Pour le Client<br>Signature :</{D}>
                            <{D} style="clear: both;"></{D}>
                        </{D}>
                    </{D}>

                    <{D} class="page-doc">
                        <{H1}>ANNEXE 5 : Accord de Confidentialité (NDA)</{H1}>

                        <{P}><{STRONG}>ENTRE LES SOUSSIGNÉS :</{STRONG}></{P}>
                        <{P}>{entreprise_info['nom']}, dont le siège est situé
                        {entreprise_info['adresse']}, SIRET {entreprise_info['siret']}, ci-après désigné
                        « le Prestataire »,</{P}>
                        <{P}>ET</{P}>
                        <{P}><{STRONG}>{d['client_societe']}</{STRONG}>, {d['client_prenom']}
                        {d['client_nom']}, dont l'adresse est {d['client_adresse']}, ci-après désigné
                        « le Client »,</{P}>
                        <{P}><{EM}>Ci-après désignés ensemble « les Parties ».</{EM}></{P}>

                        <{H2}>Article 1 : Objet</{H2}>
                        <{P}>Le présent accord a pour objet de définir les conditions dans lesquelles les
                        Parties s'engagent à préserver la confidentialité des informations échangées dans
                        le cadre du projet objet du devis n° {d['numero_devis']}, tant lors des échanges
                        précontractuels que pendant l'exécution de la prestation.</{P}>

                        <{H2}>Article 2 : Informations confidentielles</{H2}>
                        <{P}>Sont considérées comme confidentielles toutes les informations, quelle qu'en
                        soit la forme, communiquées par l'une des Parties à l'autre à l'occasion du
                        projet, notamment les informations commerciales, financières ou stratégiques, les
                        spécifications fonctionnelles et techniques, les données clients ou salariés, et
                        tout code source ou savoir-faire communiqué. Ne sont pas confidentielles les
                        informations déjà connues, publiques sans manquement au présent accord, reçues
                        licitement d'un tiers, ou dont la divulgation est requise par la loi.</{P}>

                        <{H2}>Article 3 : Obligations des Parties</{H2}>
                        <{P}>Chaque Partie s'engage à ne divulguer les informations confidentielles de
                        l'autre Partie à aucun tiers sans accord écrit préalable, à ne les utiliser que
                        dans le cadre du projet, à en limiter l'accès aux personnes ayant besoin d'en
                        connaître, et à mettre en œuvre des mesures de protection raisonnables
                        équivalentes à celles appliquées à ses propres informations sensibles.</{P}>

                        <{H2}>Article 4 : Durée</{H2}>
                        <{P}>L'obligation de confidentialité s'applique pendant toute la durée de la
                        relation contractuelle et perdure pendant trois (3) ans à compter du terme de
                        celle-ci, quelle qu'en soit la cause.</{P}>

                        <{H2}>Article 5 : Absence de transfert de droits</{H2}>
                        <{P}>La communication d'informations confidentielles au titre du présent accord
                        ne confère à la Partie réceptrice aucun droit, licence ou titre de propriété
                        intellectuelle sur ces informations.</{P}>

                        <{H2}>Article 6 : Droit applicable</{H2}>
                        <{P}>Le présent accord est soumis au droit français, dans les conditions de
                        compétence juridictionnelle prévues à l'Article 14 des CGV (Annexe 2).</{P}>

                        <{D} class="signatures-container">
                            <{P}><{STRONG}>Fait en deux exemplaires, le _____________________</{STRONG}></{P}>
                            <{D} class="sig-box-left">Pour le Prestataire<br>Signature :</{D}>
                            <{D} class="sig-box-right">Pour le Client<br>Signature :</{D}>
                            <{D} style="clear: both;"></{D}>
                        </{D}>
                    </{D}>
                </{D}>
                """
                components.html(dossier_html, height=1200, scrolling=True)
    else:
        st.info("Aucun devis disponible.")


# ---------------------------------------------------------------------------
# Établir / Corriger une facture
# ---------------------------------------------------------------------------
elif choix == "Établir / Corriger une Facture":
    render_header("🧾", "Facturation", "Établissement, correction et avoirs")

    mode_facture = st.radio(
        "Action sur les factures :",
        [
            "Établir une nouvelle facture",
            "Modifier / Corriger une facture existante",
            "Émettre un avoir (note de crédit)",
        ],
        horizontal=True,
    )

    if mode_facture == "Établir une nouvelle facture":
        df_devis = pd.read_sql_query(
            "SELECT numero_devis, client_societe FROM devis WHERE archive = 0", conn
        )
        if not df_devis.empty:
            with st.form("form_create_facture"):
                choix_devis_fact = st.selectbox(
                    "Sélectionner le devis rattaché", df_devis["numero_devis"].tolist()
                )
                type_fact = st.selectbox(
                    "Type de Facture", ["Facture d'Acompte", "Facture de Solde"]
                )

                date_fact = st.date_input("Date de facturation", value=datetime.today())
                date_ech = st.date_input(
                    "Date d'échéance", value=datetime.today() + timedelta(days=15)
                )

                submitted_fact = st.form_submit_button("💾 Établir la facture")

            if submitted_fact:
                d_info = pd.read_sql_query(
                    "SELECT * FROM devis WHERE numero_devis = ?",
                    conn,
                    params=(choix_devis_fact,),
                ).iloc[0]
                setup = d_info["montant_setup"]
                pct = d_info["pourcentage_acompte"]

                if type_fact == "Facture d'Acompte":
                    num_f = choix_devis_fact.replace("DEV", "FAC-A")
                    montant_ht = setup * (pct / 100)
                else:
                    num_f = choix_devis_fact.replace("DEV", "FAC-S")
                    montant_ht = setup * (1 - (pct / 100))

                try:
                    cursor = conn.cursor()
                    cursor.execute(
                        """
                        INSERT INTO factures (numero_facture, numero_devis, type_facture, date_facture,
                            date_echeance, montant_ht, statut)
                        VALUES (?, ?, ?, ?, ?, ?, 'Émise')
                        """,
                        (
                            num_f,
                            choix_devis_fact,
                            type_fact,
                            str(date_fact),
                            str(date_ech),
                            montant_ht,
                        ),
                    )
                    conn.commit()
                    st.success(f"Facture {num_f} établie avec succès !")
                    st.rerun()
                except Exception as e:
                    st.error(f"Erreur (la facture existe peut-être déjà) : {e}")
        else:
            st.info("Veuillez d'abord créer un devis.")

    elif mode_facture == "Modifier / Corriger une facture existante":
        df_fact = pd.read_sql_query(
            "SELECT numero_facture FROM factures WHERE type_facture != 'Avoir' ORDER BY id DESC",
            conn,
        )
        if not df_fact.empty:
            choix_fact_mod = st.selectbox(
                "Sélectionner la facture à corriger", df_fact["numero_facture"]
            )
            f_data = pd.read_sql_query(
                "SELECT * FROM factures WHERE numero_facture = ?",
                conn,
                params=(choix_fact_mod,),
            ).iloc[0]

            with st.form("form_edit_facture"):
                st.write(f"**Modification de la facture :** {f_data['numero_facture']}")
                new_date_f = st.date_input(
                    "Date de facturation",
                    value=datetime.strptime(f_data["date_facture"], "%Y-%m-%d"),
                )
                new_date_e = st.date_input(
                    "Date d'échéance",
                    value=datetime.strptime(f_data["date_echeance"], "%Y-%m-%d"),
                )
                new_montant = st.number_input(
                    "Montant H.T. en €", value=float(f_data["montant_ht"]), format="%.2f"
                )
                new_statut = st.selectbox(
                    "Statut", ["Émise", "Payée", "Annulée"], index=0
                )

                submitted_edit = st.form_submit_button("💾 Enregistrer la correction")

            if submitted_edit:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    UPDATE factures
                    SET date_facture=?, date_echeance=?, montant_ht=?, statut=?
                    WHERE numero_facture=?
                    """,
                    (
                        str(new_date_f),
                        str(new_date_e),
                        new_montant,
                        new_statut,
                        choix_fact_mod,
                    ),
                )
                conn.commit()
                st.success(f"Facture {choix_fact_mod} corrigée avec succès !")
                st.rerun()
        else:
            st.info("Aucune facture à corriger.")

    else:  # Émettre un avoir (note de crédit)
        df_fact_orig = pd.read_sql_query(
            "SELECT numero_facture, numero_devis, montant_ht, type_facture "
            "FROM factures WHERE type_facture != 'Avoir' ORDER BY id DESC",
            conn,
        )
        if not df_fact_orig.empty:
            choix_fact_avoir = st.selectbox(
                "Sélectionner la facture à créditer",
                df_fact_orig["numero_facture"].tolist(),
            )
            f_orig = df_fact_orig[
                df_fact_orig["numero_facture"] == choix_fact_avoir
            ].iloc[0]

            st.info(
                f"Montant H.T. de la facture d'origine : **{f_orig['montant_ht']:.2f} €**"
            )

            with st.form("form_create_avoir"):
                motif = st.text_area(
                    "Motif de l'avoir",
                    placeholder="ex. Erreur de facturation, annulation de prestation, "
                    "remboursement partiel...",
                )
                montant_avoir = st.number_input(
                    "Montant H.T. à créditer en €",
                    value=float(f_orig["montant_ht"]),
                    min_value=0.0,
                    max_value=float(f_orig["montant_ht"]),
                    format="%.2f",
                    help="Peut être inférieur au montant de la facture d'origine "
                    "pour un avoir partiel.",
                )
                date_avoir = st.date_input("Date de l'avoir", value=datetime.today())

                submitted_avoir = st.form_submit_button(
                    "💾 Émettre l'avoir", type="primary"
                )

            if submitted_avoir:
                if not motif.strip():
                    st.error("Le motif de l'avoir est obligatoire.")
                else:
                    num_avoir = get_next_avoir(conn)
                    try:
                        cursor = conn.cursor()
                        cursor.execute(
                            """
                            INSERT INTO factures (numero_facture, numero_devis, type_facture,
                                date_facture, date_echeance, montant_ht, statut,
                                numero_facture_liee, motif)
                            VALUES (?, ?, 'Avoir', ?, ?, ?, 'Émise', ?, ?)
                            """,
                            (
                                num_avoir,
                                f_orig["numero_devis"],
                                str(date_avoir),
                                str(date_avoir),
                                -abs(montant_avoir),
                                choix_fact_avoir,
                                motif.strip(),
                            ),
                        )
                        conn.commit()
                        st.success(
                            f"Avoir {num_avoir} émis avec succès sur la facture "
                            f"{choix_fact_avoir} !"
                        )
                        st.rerun()
                    except Exception as e:
                        st.error(f"Erreur SQL : {e}")
        else:
            st.info("Aucune facture disponible pour émettre un avoir.")


# ---------------------------------------------------------------------------
# Générer une facture (document imprimable, dans le même esprit que le
# Dossier Contractuel)
# ---------------------------------------------------------------------------
elif choix == "Générer une Facture (PDF)":
    render_header("🖨️", "Facture imprimable", "Facture ou avoir prêt à partager avec le client")

    df_fact_gen = pd.read_sql_query(
        """
        SELECT f.*, d.client_nom, d.client_prenom, d.client_societe, d.client_adresse,
               d.client_telephone, d.client_email, d.pourcentage_acompte, d.montant_setup
        FROM factures f
        JOIN devis d ON f.numero_devis = d.numero_devis
        ORDER BY f.id DESC
        """,
        conn,
    )

    if not df_fact_gen.empty:
        choix_fact_gen = st.selectbox(
            "Sélectionner la facture à éditer", df_fact_gen["numero_facture"].tolist()
        )

        f = df_fact_gen[df_fact_gen["numero_facture"] == choix_fact_gen].iloc[0]
        entreprise_info = get_entreprise_info(conn)

        # Description de la ligne facturée, selon le type de facture
        if f["type_facture"] == "Facture d'Acompte":
            designation = (
                f"Acompte ({f['pourcentage_acompte']}%) sur Forfait Setup & Création "
                f"Initiale — Devis n° {f['numero_devis']}"
            )
            titre_document = f"FACTURE N° {f['numero_facture']}"
        elif f["type_facture"] == "Facture de Solde":
            designation = (
                f"Solde sur Forfait Setup & Création Initiale — Devis n° {f['numero_devis']}"
            )
            titre_document = f"FACTURE N° {f['numero_facture']}"
        else:  # Avoir (note de crédit)
            motif_avoir = f["motif"] if pd.notna(f["motif"]) and f["motif"] else "Non précisé"
            designation = (
                f"Avoir sur facture n° {f['numero_facture_liee']} — Motif : {motif_avoir}"
            )
            titre_document = f"AVOIR N° {f['numero_facture']}"

        total_label = "MONTANT À CRÉDITER" if f["type_facture"] == "Avoir" else "NET À PAYER"

        # Cachet visuel selon le statut de la facture
        if f["statut"] == "Payée":
            stamp_color = "#2f855a"
            stamp_text = "RÉGLÉE"
        elif f["statut"] == "Annulée":
            stamp_color = "#c53030"
            stamp_text = "ANNULÉE"
        else:
            stamp_color = ""
            stamp_text = ""

        stamp_html = ""
        if stamp_text:
            stamp_html = (
                f'<{D} style="position: absolute; top: 140px; right: 60px; '
                f'transform: rotate(-15deg); border: 3px solid {stamp_color}; '
                f'color: {stamp_color}; font-size: 26px; font-weight: bold; '
                f'padding: 6px 18px; border-radius: 6px; opacity: 0.75;">{stamp_text}</{D}>'
            )

        facture_html = f"""
        <{D} style="font-family: Arial, sans-serif; color: #333333;">
            <{STYLE}>
                .page-doc {{ position: relative; width: 100%; max-width: 210mm; min-height: 200mm; padding: 20mm; margin: 20px auto; box-sizing: border-box; border: 1px solid #cbd5e0; background: #ffffff; box-shadow: 0 4px 6px rgba(0,0,0,0.1); border-radius: 8px; }}
                .page-doc {H1} {{ font-size: 18px; color: #1a365d; border-bottom: 2px solid #3182ce; padding-bottom: 5px; }}
                .page-doc {H2} {{ font-size: 14px; color: #2b6cb0; margin-top: 15px; }}
                .page-doc {P}, .page-doc {LI} {{ font-size: 12px; line-height: 1.5; }}
                .box-info {{ border: 1px solid #cbd5e0; padding: 12px; border-radius: 5px; background: #f8fafc; margin-bottom: 15px; width: 48%; display: inline-block; vertical-align: top; box-sizing: border-box; }}
                .table-fact {{ width: 100%; border-collapse: collapse; margin: 15px 0; }}
                .table-fact {TH}, .table-fact {TD} {{ border: 1px solid #cbd5e0; padding: 8px; text-align: left; font-size: 12px; }}
                .table-fact {TH} {{ background-color: #edf2f7; color: #1a365d; }}
                .mentions-legales {{ font-size: 9px; color: #666; border-top: 1px solid #cbd5e0; margin-top: 25px; padding-top: 10px; line-height: 1.5; }}
                .signatures-container {{ margin-top: 30px; width: 100%; }}
                .sig-box-right {{ width: 45%; height: 70px; border: 1px dashed #a0aec0; padding: 8px; font-size: 11px; color: #718096; display: inline-block; float: right; box-sizing: border-box; }}
            </{STYLE}>

            <{D} class="page-doc">
                {stamp_html}
                <{TABLE} style="width: 100%; border: none; margin-bottom: 20px;">
                    <{TR} style="background: transparent;">
                        <{TD} style="border: none; vertical-align: top;">
                            <{H2} style="margin: 0; color: #1a365d;">{entreprise_info['nom']}</{H2}>
                            <{P} style="margin: 5px 0 0 0;">{entreprise_info['adresse']}</{P}>
                            <{P}>Solutions logicielles sur-mesure</{P}>
                            <{P} style="font-size: 10px; color: #666;">{entreprise_info['forme_juridique']}<br>
                            SIRET : {entreprise_info['siret']}<br>
                            {entreprise_info['rcs_rm']}</{P}>
                        </{TD}>
                        <{TD} style="border: none; text-align: right; vertical-align: top;">
                            <{H1} style="margin: 0; border: none; font-size: 20px; color: #1a365d;">{titre_document}</{H1}>
                            <{P} style="margin: 5px 0 0 0;">Date de facture : {f['date_facture']}</{P}>
                            <{P}>Date d'échéance : {f['date_echeance']}</{P}>
                            <{P}>Devis de référence : {f['numero_devis']}</{P}>
                        </{TD}>
                    </{TR}>
                </{TABLE}>

                <{D} style="margin-top: 20px;">
                    <{D} class="box-info">
                        <{H3} style="margin-top: 0; color: #2b6cb0; font-size: 13px;">Facturé à :</{H3}>
                        <{P} style="margin: 0;"><{STRONG}>{f['client_societe']}</{STRONG}></{P}>
                        <{P}>{f['client_prenom']} {f['client_nom']}</{P}>
                        <{P}>{f['client_adresse']}</{P}>
                        <{P}>Tél : {f['client_telephone']} | Email : {f['client_email']}</{P}>
                    </{D}>
                    <{D} class="box-info" style="float: right;">
                        <{H3} style="margin-top: 0; color: #2b6cb0; font-size: 13px;">Statut & règlement :</{H3}>
                        <{P} style="margin: 0;"><{STRONG}>Statut : {f['statut']}</{STRONG}></{P}>
                        <{P}>Mode de règlement : virement bancaire</{P}>
                        <{P}>Escompte pour paiement anticipé : néant</{P}>
                    </{D}>
                    <{D} style="clear: both;"></{D}>
                </{D}>

                <{TABLE} class="table-fact">
                    <{TR}>
                        <{TH}>Désignation</{TH}>
                        <{TH}>Qté</{TH}>
                        <{TH} style="text-align: right;">Prix H.T.</{TH}>
                        <{TH} style="text-align: right;">Total H.T.</{TH}>
                    </{TR}>
                    <{TR}>
                        <{TD}>{designation}</{TD}>
                        <{TD}>1</{TD}>
                        <{TD} style="text-align: right;">{f['montant_ht']:.2f} €</{TD}>
                        <{TD} style="text-align: right;">{f['montant_ht']:.2f} €</{TD}>
                    </{TR}>
                </{TABLE}>

                <{D} style="text-align: right; margin-top: 15px;">
                    <{P} style="font-size: 14px;"><{STRONG}>Total H.T. : {f['montant_ht']:.2f} €</{STRONG}></{P}>
                    <{P} style="font-size: 10px; color: #666;"><{EM}>TVA non applicable, art. 293 B du CGI.</{EM}></{P}>
                    <{P} style="font-size: 16px; margin-top: 10px;"><{STRONG}>{total_label} : {f['montant_ht']:.2f} €</{STRONG}></{P}>
                </{D}>

                <{D} class="mentions-legales">
                    <{P}>En cas de retard de paiement, seront exigibles, conformément à l'article
                    L441-10 du Code de commerce, une indemnité forfaitaire pour frais de recouvrement de
                    40 € ainsi que des pénalités de retard calculées au taux d'intérêt légal en vigueur
                    majoré de 10 points, sans qu'un rappel soit nécessaire. Aucun escompte n'est accordé
                    pour paiement anticipé. TVA non applicable, article 293 B du Code général des
                    impôts — mention légale attestant du statut de franchise en base de TVA.</{P}>
                </{D}>

                <{D} class="signatures-container">
                    <{D} class="sig-box-right">Cachet et signature du Prestataire :</{D}>
                    <{D} style="clear: both;"></{D}>
                </{D}>
            </{D}>
        </{D}>
        """
        components.html(facture_html, height=950, scrolling=True)
    else:
        st.info("Aucune facture n'a encore été établie. Rendez-vous dans "
                "\"Établir / Corriger une Facture\" pour en créer une.")


# ---------------------------------------------------------------------------
# Paramètres de l'entreprise (SIRET, RCS/RM, forme juridique...) — éditables
# directement dans l'appli, stockés en base, et injectés automatiquement dans
# les devis, factures et CGV générés.
# ---------------------------------------------------------------------------
elif choix == "⚙️ Paramètres de l'entreprise":
    render_header("🛠️", "Paramètres", "Informations légales de l'entreprise")
    st.markdown(
        "Ces informations apparaissent automatiquement sur tous les devis et "
        "factures générés (mentions obligatoires : art. L441-9 et L123-22 du "
        "Code de commerce)."
    )

    if "entreprise_success_msg" in st.session_state:
        st.success(st.session_state.entreprise_success_msg)
        del st.session_state.entreprise_success_msg

    info = get_entreprise_info(conn)

    with st.form("form_entreprise"):
        nom = st.text_input(
            "Nom / Raison sociale",
            value=info["nom"],
        )
        adresse = st.text_input(
            "Adresse",
            value=info["adresse"],
        )
        forme_juridique = st.text_input(
            "Forme juridique",
            value="" if info["forme_juridique"] == "Non renseigné" else info["forme_juridique"],
            placeholder="ex. Entreprise Individuelle / Micro-entreprise",
        )
        siret = st.text_input(
            "Numéro SIRET (14 chiffres)",
            value="" if info["siret"] == "Non renseigné" else info["siret"],
            placeholder="ex. 123 456 789 00012",
        )
        rcs_rm = st.text_input(
            "RCS ou RM (registre du commerce / des métiers)",
            value="" if info["rcs_rm"] == "Non renseigné" else info["rcs_rm"],
            placeholder="ex. RCS Basse-Terre 123 456 789, ou RM 971 ...",
        )

        submitted_entreprise = st.form_submit_button(
            "💾 Enregistrer les informations", type="primary"
        )

    if submitted_entreprise:
        cursor = conn.cursor()
        cursor.execute(
            """
            UPDATE entreprise
            SET nom=?, adresse=?, siret=?, rcs_rm=?, forme_juridique=?
            WHERE id=1
            """,
            (nom, adresse, siret, rcs_rm, forme_juridique),
        )
        conn.commit()
        st.session_state.entreprise_success_msg = (
            "✅ Informations de l'entreprise mises à jour avec succès !"
        )
        st.rerun()


conn.close()