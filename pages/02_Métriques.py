import code
import streamlit as st
import base64
import pymongo
import pandas as pd

# Dans le requirements.txt,
# ne pas installer de modules standards à Python

# Exécuter localement
# streamlit run index.py

##################################################
# Configurer la page
# wide, centered
# auto or expanded
st.set_page_config(page_title="Projet intégrateur",
                   page_icon="img/favicon.ico",
                   layout="centered",
                   initial_sidebar_state="auto",
                   menu_items={
                       "About": "Projet intégrateur de l'équipe Toucan Fortuné"}
)

# Cacher le menu officiel (hamburger)
hide_menu_style = """
        <style>
        #MainMenu {visibility: hidden;}
        </style>
        """
# ???
#st.markdown(hide_menu_style, unsafe_allow_html=True)

# Ajouter au Sidebar
def ajouter_image_sidebar(image):
    with open(image, "rb") as image:
        encodage = base64.b64encode(image.read())
    st.markdown(
    f"""
    <style>
    [data-testid="stSidebar"]  {{
        background-image: url(data:image/{"png"};base64,{encodage.decode()});
        background-size: 75px;
        background-repeat: no-repeat;
        background-position: 15px 15px;
    }}
    </style>
    """,
    unsafe_allow_html=True
)

ajouter_image_sidebar("img/android-chrome-512x512b.png")

##################################################
# Déterminer les constantes
COMPTE_NOEUD = 9
WARNING = "Seul les noeuds 001 à 003 sont actifs. Les autres valeurs sont calquées sur les noeuds actifs."
#WARNING = "Seuls les noeuds 001 à 001 sont actifs."
NO_LIGNES = 50

##################################################
# Construire la page
st.title("Métriques")

# ???Todo
# automatisation sur toutes les pages
# changer le schémas page Accueil

# https://docs.streamlit.io/knowledge-base/using-streamlit/hide-row-indices-displaying-dataframe

# Établir la connexion à la base de données
# https://docs.streamlit.io/streamlit-cloud/get-started/deploy-an-app/connect-to-data-sources/secrets-management
# https://docs.streamlit.io/library/api-reference/performance/st.experimental_singleton
# https://docs.streamlit.io/library/api-reference/performance/st.experimental_singleton.clear
@st.experimental_singleton
def etablir_connexion():
    # Chercher les données dans le fichier secrets.toml
    URI = f"mongodb+srv://{st.secrets['db_username']}:{st.secrets['db_pw']}@{st.secrets['db_cluster']}.gzo0glz.mongodb.net/?retryWrites=true&writeConcern=majority"
    return pymongo.MongoClient(URI)

# Importer les données de la collection
# https://docs.streamlit.io/library/api-reference/performance/st.experimental_memo
@st.experimental_memo
def extraire_documents_dataframe():
    # Sélectioner la BASE DE DONNÉES
    db = client.toucan
    # Extraire de la COLLECTION et filtrer les documents
    # -1 sort descending, newest to oldest
    items = list(db.format3.find().sort("datetime",
                                        -1).limit(NO_LIGNES)) 
    # Convertir en DataFrame
    dataframe = pd.DataFrame(items)
    return dataframe

# Préparer le DataFrame
@st.experimental_memo
def preparer_dataframe(dataframe):
    # Enlever une colonne
    dataframe.drop(['_id'], axis=1, inplace=True)
    # Transformer une colonne en ts
    dataframe['datetime'] = pd.to_datetime(dataframe['datetime'], infer_datetime_format=True)
    # Envoyer la colonne dans l'index
    dataframe_ts = dataframe.set_index(dataframe['datetime'], drop=False)
    dataframe_ts.index.name = None
    # Convertir la colonne de string à float32
    dataframe_ts['valeur'] = dataframe_ts['valeur'].astype('float16')
    return dataframe_ts

# Filtrer le DataFrame
@st.experimental_memo
def filtrer_dataframe(dataframe, noeud, capteur, metrique):
    # Construire les filtres
    filtre_noeud = dataframe['noeud'] == noeud
    filtre_capteur = dataframe['capteur'] == capteur
    filtre_metrique = dataframe['metrique'] == metrique
    # Appliquer les filtre
    dataframe_f = dataframe.loc[filtre_noeud & filtre_capteur & filtre_metrique]
    return dataframe_f

# Sélectionner les 2 dernières observations
@st.experimental_memo
def selectionner_observations(dataframe):
    # Trier les observations
    # descending, newest to oldest ou ascending=False
    # ascending, oldest to newest ou ascending=True
    dataframe.sort_index(ascending=False, inplace=True)
    # Sélectionner les 2 premières observations
    dataframe_2 = dataframe.iloc[0:2]
    # Créer une colonne de retard
    dataframe_2.loc[:, 'valeur_precedente'] = dataframe_2['valeur'].shift(periods=-1, fill_value=float('nan'))
    # Calculer le delta
    dataframe_2.loc[:, 'valeur_delta'] = dataframe_2['valeur'] - dataframe_2['valeur_precedente']
    # Extraire 2 valeurs
    valeur_datetime = dataframe_2['datetime'].iloc[0]
    valeur_metrique = dataframe_2['valeur'].iloc[0]
    valeur_delta = dataframe_2['valeur_delta'].iloc[0]
    return valeur_metrique, valeur_delta, valeur_datetime

##################################################
# Établir la connexion à la base de données
client = etablir_connexion()

##################################################
st.header("Sélection")

# Confirmer les changements d'état
# du formulaire
def mettre_jour_001():
    for i in range(1, COMPTE_NOEUD + 1, 1):
        i = '{:03d}'.format(i)
        st.session_state[f'noeud{i}a'] = st.session_state[f'noeud{i}b']
        
# Construire un formulaire de changement des états
# st.form_submit_button(label="Submit", help=None, on_click=None, args=None, kwargs=None, *, type="secondary", disabled=False)
with st.form(key='form001', clear_on_submit=False):
    st.subheader("Sélectionner les noeuds à afficher")
    
    st.warning(WARNING)
    
    # st.columns(spec, *, gap="small")
    col1, col2, col3 = st.columns(3)
    with col1:
        # st.checkbox(label, value=False, key=None, help=None, on_change=None, args=None, kwargs=None, *, disabled=False, label_visibility="visible")
        st.checkbox('Noeud 001', key='noeud001b', value=True)
        st.checkbox('Noeud 002', key='noeud002b', value=False)
        st.checkbox('Noeud 003', key='noeud003b', value=False)
    with col2:
        st.checkbox('Noeud 004', key='noeud004b', value=False)
        st.checkbox('Noeud 005', key='noeud005b', value=False)
        st.checkbox('Noeud 006', key='noeud006b', value=False)   
    with col3:
        st.checkbox('Noeud 007', key='noeud007b', value=False)
        st.checkbox('Noeud 008', key='noeud008b', value=False)
        st.checkbox('Noeud 009', key='noeud009b', value=False)
    # Invoquer la fonction callback    
    submit_button = st.form_submit_button('Soumettre', on_click=mettre_jour_001)

# ???
# Construire un onglet de changement du delai
# st.select_slider(label, options=(), value=None, format_func=special_internal_function, key=None, help=None, on_change=None, args=None, kwargs=None, *, disabled=False, label_visibility="visible")
st.subheader("Sélectionner le délai de mise à jour")
st.info("De 10s à 60s entre chaque extraction de la base de données.")
delai = st.slider("Sélectionner", 10, 60, 20, 5)

##################################################
# ???automatiser ici

# Importer les données de la collection
df = extraire_documents_dataframe()
# Préparer le DataFrame
df_ts = preparer_dataframe(df)

##################################################
st.header("Affichage")

# Construire les métriques
st.warning(WARNING)

col1, col2 = st.columns(2, gap="small")

with col1:
    st.subheader("Température")

    # st.metric(label, value, delta=None, delta_color="normal", help=None, label_visibility="visible")
    if st.session_state['noeud001b']:
        # Filtrer le DataFrame
        df_f = filtrer_dataframe(df_ts, "noeud01", "temperature", "brute")
        # Sélectionner les 2 dernières observations
        st.metric("Noeud 001",
                  f"{selectionner_observations(df_f)[0]:.1f}°C",
                  f"{selectionner_observations(df_f,)[1]:.1f}°C")
        st.caption(f"{selectionner_observations(df_f)[2]: %d %b %Y, %Hh%M:%S}")
    if st.session_state['noeud002b']:
        df_f = filtrer_dataframe(df_ts, "noeud02", "temperature", "brute")
        st.metric("Noeud 002",
                  f"{selectionner_observations(df_f)[0]:.1f}°C",
                  f"{selectionner_observations(df_f)[1]:.1f}°C")
        st.caption(f"{selectionner_observations(df_f)[2]: %d %b %Y, %Hh%M:%S}")
    if st.session_state['noeud003b']:
        df_f = filtrer_dataframe(df_ts, "noeud03", "temperature", "brute")
        st.metric("Noeud 003",
                  f"{selectionner_observations(df_f)[0]:.1f}°C",
                  f"{selectionner_observations(df_f)[1]:.1f}°C")
        st.caption(f"{selectionner_observations(df_f)[2]: %d %b %Y, %Hh%M:%S}")
    if st.session_state['noeud004b']:
        df_f = filtrer_dataframe(df_ts, "noeud01", "temperature", "brute")
        st.metric("Noeud 004",
                  f"{selectionner_observations(df_f)[0]:.1f}°C",
                  f"{selectionner_observations(df_f)[1]:.1f}°C")
        st.caption(f"{selectionner_observations(df_f)[2]: %d %b %Y, %Hh%M:%S}")
    if st.session_state['noeud005b']:
        df_f = filtrer_dataframe(df_ts, "noeud02", "temperature", "brute")
        st.metric("Noeud 005",
                  f"{selectionner_observations(df_f)[0]:.1f}°C",
                  f"{selectionner_observations(df_f)[1]:.1f}°C")
        st.caption(f"{selectionner_observations(df_f)[2]: %d %b %Y, %Hh%M:%S}")
    if st.session_state['noeud006b']:
        df_f = filtrer_dataframe(df_ts, "noeud03", "temperature", "brute")
        st.metric("Noeud 006",
                  f"{selectionner_observations(df_f)[0]:.1f}°C",
                  f"{selectionner_observations(df_f)[1]:.1f}°C")
        st.caption(f"{selectionner_observations(df_f)[2]: %d %b %Y, %Hh%M:%S}")
    if st.session_state['noeud007b']:
        df_f = filtrer_dataframe(df_ts, "noeud01", "temperature", "brute")
        st.metric("Noeud 007",
                  f"{selectionner_observations(df_f)[0]:.1f}°C",
                  f"{selectionner_observations(df_f)[1]:.1f}°C")
        st.caption(f"{selectionner_observations(df_f)[2]: %d %b %Y, %Hh%M:%S}")
    if st.session_state['noeud008b']:
        df_f = filtrer_dataframe(df_ts, "noeud02", "temperature", "brute")
        st.metric("Noeud 008",
                  f"{selectionner_observations(df_f)[0]:.1f}°C",
                  f"{selectionner_observations(df_f)[1]:.1f}°C")
        st.caption(f"{selectionner_observations(df_f)[2]: %d %b %Y, %Hh%M:%S}")
    if st.session_state['noeud009b']:
        df_f = filtrer_dataframe(df_ts, "noeud03", "temperature", "brute")
        st.metric("Noeud 001",
                  f"{selectionner_observations(df_f)[0]:.1f}°C",
                  f"{selectionner_observations(df_f)[1]:.1f}°C")
        st.caption(f"{selectionner_observations(df_f)[2]: %d %b %Y, %Hh%M:%S}")

with col2:
    st.subheader("Humidité")
    if st.session_state['noeud001b']:
        df_f = filtrer_dataframe(df_ts, "noeud01", "humidité", "brute")
        st.metric("Noeud 001",
                  f"{selectionner_observations(df_f)[0]:.1f}%",
                  f"{selectionner_observations(df_f)[1]:.1f}%")
        st.caption(f"{selectionner_observations(df_f)[2]: %d %b %Y, %Hh%M:%S}")
    if st.session_state['noeud002b']:
        df_f = filtrer_dataframe(df_ts, "noeud02", "humidité", "brute")
        st.metric("Noeud 001",
                  f"{selectionner_observations(df_f)[0]:.1f}%",
                  f"{selectionner_observations(df_f)[1]:.1f}%")
        st.caption(f"{selectionner_observations(df_f)[2]: %d %b %Y, %Hh%M:%S}")
    if st.session_state['noeud003b']:
        df_f = filtrer_dataframe(df_ts, "noeud03", "humidité", "brute")
        st.metric("Noeud 001",
                  f"{selectionner_observations(df_f)[0]:.1f}%",
                  f"{selectionner_observations(df_f)[1]:.1f}%")
        st.caption(f"{selectionner_observations(df_f)[2]: %d %b %Y, %Hh%M:%S}")
    if st.session_state['noeud004b']:
        df_f = filtrer_dataframe(df_ts, "noeud01", "humidité", "brute")
        st.metric("Noeud 001",
                  f"{selectionner_observations(df_f)[0]:.1f}%",
                  f"{selectionner_observations(df_f)[1]:.1f}%")
        st.caption(f"{selectionner_observations(df_f)[2]: %d %b %Y, %Hh%M:%S}")
    if st.session_state['noeud005b']:
        df_f = filtrer_dataframe(df_ts, "noeud02", "humidité", "brute")
        st.metric("Noeud 001",
                  f"{selectionner_observations(df_f)[0]:.1f}%",
                  f"{selectionner_observations(df_f)[1]:.1f}%")
        st.caption(f"{selectionner_observations(df_f)[2]: %d %b %Y, %Hh%M:%S}")
    if st.session_state['noeud006b']:
        df_f = filtrer_dataframe(df_ts, "noeud03", "humidité", "brute")
        st.metric("Noeud 001",
                  f"{selectionner_observations(df_f)[0]:.1f}%",
                  f"{selectionner_observations(df_f)[1]:.1f}%")
        st.caption(f"{selectionner_observations(df_f)[2]: %d %b %Y, %Hh%M:%S}")
    if st.session_state['noeud007b']:
        df_f = filtrer_dataframe(df_ts, "noeud01", "humidité", "brute")
        st.metric("Noeud 001",
                  f"{selectionner_observations(df_f)[0]:.1f}%",
                  f"{selectionner_observations(df_f)[1]:.1f}%")
        st.caption(f"{selectionner_observations(df_f)[2]: %d %b %Y, %Hh%M:%S}")
    if st.session_state['noeud008b']:
        df_f = filtrer_dataframe(df_ts, "noeud02", "humidité", "brute")
        st.metric("Noeud 001",
                  f"{selectionner_observations(df_f)[0]:.1f}%",
                  f"{selectionner_observations(df_f)[1]:.1f}%")
        st.caption(f"{selectionner_observations(df_f)[2]: %d %b %Y, %Hh%M:%S}")
    if st.session_state['noeud009b']:
        df_f = filtrer_dataframe(df_ts, "noeud03", "humidité", "brute")
        st.metric("Noeud 001",
                  f"{selectionner_observations(df_f)[0]:.1f}%",
                  f"{selectionner_observations(df_f)[1]:.1f}%")
        st.caption(f"{selectionner_observations(df_f)[2]: %d %b %Y, %Hh%M:%S}")
