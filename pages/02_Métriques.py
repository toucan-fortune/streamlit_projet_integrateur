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
                       "About": "Projet intégrateur de l'équipe Toucan Fortuné."}
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

##################################################
# Construire la page
st.title("Métriques")

# ???Todo
# changer le schémas page Accueil

# Établir la connexion à la base de données
@st.experimental_singleton
def etablir_connexion():
    # Chercher les données dans le fichier secrets.toml
    URI = f"mongodb+srv://{st.secrets['db_username']}:{st.secrets['db_pw']}@{st.secrets['db_cluster']}.gzo0glz.mongodb.net/?retryWrites=true&writeConcern=majority"
    return pymongo.MongoClient(URI)

# Importer les données de la collection
@st.experimental_memo
def extraire_documents_dataframe(_client, _base, _collection, _nolignes):
    # Sélectioner la BASE DE DONNÉES
    base = _client.get_database(_base)
    # Sélectionner la COLLECTION
    collection = base.get_collection(_collection)
    # Extraire de la COLLECTION et filtrer les documents
    # -1 sort descending, newest to oldest
    items = list(collection.find().sort("datetime",
                                        -1).limit(_nolignes))
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
    # Convertir la colonne de string à float
    dataframe_ts['valeur'] = dataframe_ts['valeur'].astype('float16')
    return dataframe_ts

# Filtrer le DataFrame
@st.experimental_memo
def filtrer_dataframe_metriques(dataframe, noeud, capteur, metrique):
    # Construire les filtres
    filtre_noeud = dataframe['noeud'] == noeud
    filtre_capteur = dataframe['capteur'] == capteur
    filtre_metrique = dataframe['metrique'] == metrique
    # Appliquer les filtre
    dataframe_f = dataframe.loc[filtre_noeud & filtre_capteur & filtre_metrique]
    return dataframe_f

# Sélectionner les 2 dernières observations
@st.experimental_memo
def selectionner_obs_metrique(dataframe):
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
try:
    _un_client = etablir_connexion()
except Exception:
    print("Incapable de se connecter au serveur.")

##################################################
st.header("Sélection")

st.subheader("Sélectionner les données")

col1, col2, col3 = st.columns(3)

with col1:
    # Sélectionner la bd et la collection
    st.radio("Base de données",
    ('toucan',), key='base')
with col2:
    st.radio("Collection",
    ('format3',), key='collection')
with col3:
    st.radio("Documents",
    (850,), key='nolignes')

# Construire un contenant
with st.container():
    st.subheader("Sélectionner les noeuds à afficher")
    
    st.warning(WARNING)
    
    # st.columns(spec, *, gap="small")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.checkbox('Noeud 001', key='st_noeud001', value=False)
        st.checkbox('Noeud 002', key='st_noeud002', value=False)
        st.checkbox('Noeud 003', key='st_noeud003', value=False)
        st.empty()
    with col2:
        st.checkbox('Noeud 004', key='st_noeud004', value=False)
        st.checkbox('Noeud 005', key='st_noeud005', value=False)
        st.checkbox('Noeud 006', key='st_noeud006', value=False)   
    with col3:
        st.checkbox('Noeud 007', key='st_noeud007', value=False)
        st.checkbox('Noeud 008', key='st_noeud008', value=False)
        st.checkbox('Noeud 009', key='st_noeud009', value=False)

# Confirmer les changements d'état
# du formulaire
def mettre_jour_groupe():
    # a
    st.session_state['st_noeud001'] = st.session_state['st_groupe00a']
    st.session_state['st_noeud002'] = st.session_state['st_groupe00a']
    st.session_state['st_noeud003'] = st.session_state['st_groupe00a']
    # b
    st.session_state['st_noeud004'] = st.session_state['st_groupe00b']
    st.session_state['st_noeud005'] = st.session_state['st_groupe00b']
    st.session_state['st_noeud006'] = st.session_state['st_groupe00b']
    # c
    st.session_state['st_noeud007'] = st.session_state['st_groupe00c']
    st.session_state['st_noeud008'] = st.session_state['st_groupe00c']
    st.session_state['st_noeud009'] = st.session_state['st_groupe00c']

# Construire un formulaire de changement des états
with st.form(key="form", clear_on_submit=True):
    col1, col2, col3 = st.columns(3)
    with col1:
        st.checkbox('Groupe 00A', key='st_groupe00a', value=False)
    with col2:
        st.checkbox('Groupe 00B', key='st_groupe00b', value=False)
    with col3:
        st.checkbox('Groupe 00C', key='st_groupe00c', value=False)
    # Invoquer la fonction 
    bouton_soumettre = st.form_submit_button('Soumettre', on_click=mettre_jour_groupe)

##################################################
# Importer les données de la collection
df = extraire_documents_dataframe(_un_client,
                                  st.session_state["base"],
                                  st.session_state["collection"],
                                  st.session_state["nolignes"])
# Préparer le DataFrame
df_ts = preparer_dataframe(df)

##################################################
st.header("Affichage")

# Construire les métriques
st.warning(WARNING)

col1, col2 = st.columns(2, gap="small")

with col1:
    st.subheader("Température")
    if st.session_state['st_noeud001']:
        # Filtrer le DataFrame
        df_f = filtrer_dataframe_metriques(df_ts, "noeud01", "temperature", "brute")
        # Sélectionner les 2 dernières observations
        st.metric("Noeud 001",
                  f"{selectionner_obs_metrique(df_f)[0]:.1f}°C",
                  f"{selectionner_obs_metrique(df_f,)[1]:.1f}°C")
        st.caption(f"{selectionner_obs_metrique(df_f)[2]: %d %b %Y, %Hh%M:%S}")
    if st.session_state['st_noeud002']:
        df_f = filtrer_dataframe_metriques(df_ts, "noeud02", "temperature", "brute")
        st.metric("Noeud 002",
                  f"{selectionner_obs_metrique(df_f)[0]:.1f}°C",
                  f"{selectionner_obs_metrique(df_f)[1]:.1f}°C")
        st.caption(f"{selectionner_obs_metrique(df_f)[2]: %d %b %Y, %Hh%M:%S}")
    if st.session_state['st_noeud003']:
        df_f = filtrer_dataframe_metriques(df_ts, "noeud03", "temperature", "brute")
        st.metric("Noeud 003",
                  f"{selectionner_obs_metrique(df_f)[0]:.1f}°C",
                  f"{selectionner_obs_metrique(df_f)[1]:.1f}°C")
        st.caption(f"{selectionner_obs_metrique(df_f)[2]: %d %b %Y, %Hh%M:%S}")
    if st.session_state['st_noeud004']:
        df_f = filtrer_dataframe_metriques(df_ts, "noeud01", "temperature", "brute")
        st.metric("Noeud 004",
                  f"{selectionner_obs_metrique(df_f)[0]:.1f}°C",
                  f"{selectionner_obs_metrique(df_f)[1]:.1f}°C")
        st.caption(f"{selectionner_obs_metrique(df_f)[2]: %d %b %Y, %Hh%M:%S}")
    if st.session_state['st_noeud005']:
        df_f = filtrer_dataframe_metriques(df_ts, "noeud02", "temperature", "brute")
        st.metric("Noeud 005",
                  f"{selectionner_obs_metrique(df_f)[0]:.1f}°C",
                  f"{selectionner_obs_metrique(df_f)[1]:.1f}°C")
        st.caption(f"{selectionner_obs_metrique(df_f)[2]: %d %b %Y, %Hh%M:%S}")
    if st.session_state['st_noeud006']:
        df_f = filtrer_dataframe_metriques(df_ts, "noeud03", "temperature", "brute")
        st.metric("Noeud 006",
                  f"{selectionner_obs_metrique(df_f)[0]:.1f}°C",
                  f"{selectionner_obs_metrique(df_f)[1]:.1f}°C")
        st.caption(f"{selectionner_obs_metrique(df_f)[2]: %d %b %Y, %Hh%M:%S}")
    if st.session_state['st_noeud007']:
        df_f = filtrer_dataframe_metriques(df_ts, "noeud01", "temperature", "brute")
        st.metric("Noeud 007",
                  f"{selectionner_obs_metrique(df_f)[0]:.1f}°C",
                  f"{selectionner_obs_metrique(df_f)[1]:.1f}°C")
        st.caption(f"{selectionner_obs_metrique(df_f)[2]: %d %b %Y, %Hh%M:%S}")
    if st.session_state['st_noeud008']:
        df_f = filtrer_dataframe_metriques(df_ts, "noeud02", "temperature", "brute")
        st.metric("Noeud 008",
                  f"{selectionner_obs_metrique(df_f)[0]:.1f}°C",
                  f"{selectionner_obs_metrique(df_f)[1]:.1f}°C")
        st.caption(f"{selectionner_obs_metrique(df_f)[2]: %d %b %Y, %Hh%M:%S}")
    if st.session_state['st_noeud009']:
        df_f = filtrer_dataframe_metriques(df_ts, "noeud03", "temperature", "brute")
        st.metric("Noeud 001",
                  f"{selectionner_obs_metrique(df_f)[0]:.1f}°C",
                  f"{selectionner_obs_metrique(df_f)[1]:.1f}°C")
        st.caption(f"{selectionner_obs_metrique(df_f)[2]: %d %b %Y, %Hh%M:%S}")

with col2:
    st.subheader("Humidité")
    if st.session_state['st_noeud001']:
        df_f = filtrer_dataframe_metriques(df_ts, "noeud01", "humidité", "brute")
        st.metric("Noeud 001",
                  f"{selectionner_obs_metrique(df_f)[0]:.1f}%",
                  f"{selectionner_obs_metrique(df_f)[1]:.1f}%")
        st.caption(f"{selectionner_obs_metrique(df_f)[2]: %d %b %Y, %Hh%M:%S}")
    if st.session_state['st_noeud002']:
        df_f = filtrer_dataframe_metriques(df_ts, "noeud02", "humidité", "brute")
        st.metric("Noeud 001",
                  f"{selectionner_obs_metrique(df_f)[0]:.1f}%",
                  f"{selectionner_obs_metrique(df_f)[1]:.1f}%")
        st.caption(f"{selectionner_obs_metrique(df_f)[2]: %d %b %Y, %Hh%M:%S}")
    if st.session_state['st_noeud003']:
        df_f = filtrer_dataframe_metriques(df_ts, "noeud03", "humidité", "brute")
        st.metric("Noeud 001",
                  f"{selectionner_obs_metrique(df_f)[0]:.1f}%",
                  f"{selectionner_obs_metrique(df_f)[1]:.1f}%")
        st.caption(f"{selectionner_obs_metrique(df_f)[2]: %d %b %Y, %Hh%M:%S}")
    if st.session_state['st_noeud004']:
        df_f = filtrer_dataframe_metriques(df_ts, "noeud01", "humidité", "brute")
        st.metric("Noeud 001",
                  f"{selectionner_obs_metrique(df_f)[0]:.1f}%",
                  f"{selectionner_obs_metrique(df_f)[1]:.1f}%")
        st.caption(f"{selectionner_obs_metrique(df_f)[2]: %d %b %Y, %Hh%M:%S}")
    if st.session_state['st_noeud005']:
        df_f = filtrer_dataframe_metriques(df_ts, "noeud02", "humidité", "brute")
        st.metric("Noeud 001",
                  f"{selectionner_obs_metrique(df_f)[0]:.1f}%",
                  f"{selectionner_obs_metrique(df_f)[1]:.1f}%")
        st.caption(f"{selectionner_obs_metrique(df_f)[2]: %d %b %Y, %Hh%M:%S}")
    if st.session_state['st_noeud006']:
        df_f = filtrer_dataframe_metriques(df_ts, "noeud03", "humidité", "brute")
        st.metric("Noeud 001",
                  f"{selectionner_obs_metrique(df_f)[0]:.1f}%",
                  f"{selectionner_obs_metrique(df_f)[1]:.1f}%")
        st.caption(f"{selectionner_obs_metrique(df_f)[2]: %d %b %Y, %Hh%M:%S}")
    if st.session_state['st_noeud007']:
        df_f = filtrer_dataframe_metriques(df_ts, "noeud01", "humidité", "brute")
        st.metric("Noeud 001",
                  f"{selectionner_obs_metrique(df_f)[0]:.1f}%",
                  f"{selectionner_obs_metrique(df_f)[1]:.1f}%")
        st.caption(f"{selectionner_obs_metrique(df_f)[2]: %d %b %Y, %Hh%M:%S}")
    if st.session_state['st_noeud008']:
        df_f = filtrer_dataframe_metriques(df_ts, "noeud02", "humidité", "brute")
        st.metric("Noeud 001",
                  f"{selectionner_obs_metrique(df_f)[0]:.1f}%",
                  f"{selectionner_obs_metrique(df_f)[1]:.1f}%")
        st.caption(f"{selectionner_obs_metrique(df_f)[2]: %d %b %Y, %Hh%M:%S}")
    if st.session_state['st_noeud009']:
        df_f = filtrer_dataframe_metriques(df_ts, "noeud03", "humidité", "brute")
        st.metric("Noeud 001",
                  f"{selectionner_obs_metrique(df_f)[0]:.1f}%",
                  f"{selectionner_obs_metrique(df_f)[1]:.1f}%")
        st.caption(f"{selectionner_obs_metrique(df_f)[2]: %d %b %Y, %Hh%M:%S}")
