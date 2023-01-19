import streamlit as st
import base64
import pymongo
import pandas as pd
import plotly.express as px


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
                   layout="wide",
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
BASE = 'toucan'
COLLECTION = 'format4b'
NOLIGNES = 2592
COMPTE_NOEUD = 9
WARNING = "Seul les noeuds 001 à 003 sont actifs."

##################################################
# Établir la connexion à la base de données
@st.experimental_singleton
def etablir_connexion():
    # Chercher les données dans le fichier secrets.toml
    URI = f"mongodb+srv://{st.secrets['db_username']}:{st.secrets['db_pw']}@{st.secrets['db_cluster']}.gzo0glz.mongodb.net/?retryWrites=true&writeConcern=majority"
    return pymongo.MongoClient(URI)


# Importer les données de la collection
@st.experimental_memo
def extraire_documents_dataframe(_client, _base, _collection, _nolignes):
    # Sélectioner la bd
    base = _client.get_database(_base)
    # Sélectionner la collection
    collection = base.get_collection(_collection)
    # Extraire de la collection et filtrer les documents
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
def filtrer_dataframe_series(dataframe, capteur, metrique):
    # Construire les filtres
    filtre_capteur = dataframe['capteur'] == capteur
    filtre_metrique = dataframe['metrique'] == metrique
    # Appliquer les filtre
    dataframe_f = dataframe.loc[filtre_capteur & filtre_metrique]
    return dataframe_f


# Sélectionner les observations
@st.experimental_memo
def selectionner_obser_series(dataframe, nombre):
    # Trier les observations
    # descending, newest to oldest ou ascending=False
    # ascending, oldest to newest ou ascending=True
    dataframe.sort_index(ascending=False, inplace=True)
    # Sélectionner les n premières observations
    dataframe_2 = dataframe.iloc[0:nombre]
    # Créer une colonne de retard
    dataframe_2.loc[:, 'valeur_precedente'] = dataframe_2['valeur'].shift(periods=-1, fill_value=float('nan'))
    # Calculer le delta
    dataframe_2.loc[:, 'valeur_delta'] = dataframe_2['valeur'] - dataframe_2['valeur_precedente']
    dataframe_2.loc[:, 'valeur_pct_delta'] = dataframe_2['valeur'] / dataframe_2['valeur_precedente'] - 1
    return dataframe_2


##################################################
# Établir la connexion à la base de données
try:
    _un_client = etablir_connexion()
except Exception:
    print("Incapable de se connecter au serveur.")

##################################################
# Construire la page
# avec title, header, subheader, markdown, write
# columns, containerm form
# warning, info
# les widgets
# caption, metric

st.title("Séries")

st.header("Sélection")

col1, col2, col3 = st.columns(3)

with col1:
    # Sélectionner la bd
    st.radio("Base de données",
             (BASE,), key='base')
with col2:
    # Sélectionner la collection
    st.radio("Collection",
             (COLLECTION,), key='collection')
with col3:
    # Sélectionner le nombre de documents
    st.radio("Documents",
             (NOLIGNES,), key='nolignes')

with st.container():
    st.subheader("Sélectionner les noeuds à afficher")

    st.warning(WARNING)

    col1, col2, col3 = st.columns(3)
    with col1:
        st.checkbox('Noeud 001', key='st_noeud001', value=False)
        st.checkbox('Noeud 002', key='st_noeud002', value=False)
        st.checkbox('Noeud 003', key='st_noeud003', value=False)
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
    # Groupe A
    st.session_state['st_noeud001'] = st.session_state['st_groupe00a']
    st.session_state['st_noeud002'] = st.session_state['st_groupe00a']
    st.session_state['st_noeud003'] = st.session_state['st_groupe00a']
    # Groupe B
    st.session_state['st_noeud004'] = st.session_state['st_groupe00b']
    st.session_state['st_noeud005'] = st.session_state['st_groupe00b']
    st.session_state['st_noeud006'] = st.session_state['st_groupe00b']
    # Groupe C
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

st.subheader("Sélectionner l'étendue")

st.info(f"De 5 à {st.session_state['nolignes']} périodes chronologiques.")

st.slider("Sélectionner", 5, st.session_state["nolignes"], 10, 5, key='periode')

##################################################
# Importer les données de la collection
df = extraire_documents_dataframe(_un_client,
                                  st.session_state["base"],
                                  st.session_state["collection"],
                                  st.session_state["nolignes"])

# Préparer le DataFrame
# Trier par noeud, puis datetime
df_ts = preparer_dataframe(df).sort_values(by=["noeud", "datetime"])

##################################################
st.header("Affichage")

st.warning(WARNING)

st.subheader("Tableau interactif de 10 observations")
st.caption("Le DataFrame est trié en ordre ascendant; la dernière rangée montre l'observation la plus récente.")

# Afficher un tableau interactif
st.dataframe(df_ts.head(10))

# Vérifier le nombre d'observations
st.write(f"Nombre total d'observations: {df_ts.shape[0]}")

st.subheader("Graphiques: température")

# Filtrer pour les prochaines graphiques
liste_noeud = []
if st.session_state['st_noeud001']:
    liste_noeud.append('pico01')
if st.session_state['st_noeud002']:
    liste_noeud.append('pico02')
if st.session_state['st_noeud003']:
    liste_noeud.append('pico03')
# ...

# Filtrer pour les prochaines graphiques
# Refiltrer les noeuds
df_f = filtrer_dataframe_series(df_ts, "temperature", "brute").loc[df_ts['noeud'].isin(liste_noeud)]

# Tracer la ligne
fig = px.line(selectionner_obser_series(df_f,
                                        st.session_state['periode']),
              x="datetime",
              y="valeur",
              color='noeud',
              labels={
                     "datetime": "",
                     "valeur": "°C",
                     "noeud": "Noeud"
                  },
              title='Brute')

st.plotly_chart(fig)

# Tracer les barres
fig = px.bar(selectionner_obser_series(df_f,
                                       st.session_state['periode']),
             x="datetime",
             y="valeur_delta",
             color='noeud',
             labels={
                     "datetime": "",
                     "valeur_delta": "différence en °C",
                     "noeud": "Noeud"
                 },
             title='Brute, changement, période à période')
st.plotly_chart(fig)

# Tracer les barres
fig = px.bar(selectionner_obser_series(df_f,
                                       st.session_state['periode']),
             x="datetime",
             y="valeur_pct_delta",
             color='noeud',
             labels={
                     "datetime": "",
                     "valeur_pct_delta": "% différence en °C",
                     "noeud": "Noeud"
                 },
             title='Brute, % changement, période à période')
st.plotly_chart(fig)

# Tracer les violons
fig = px.violin(selectionner_obser_series(df_f,
                                          st.session_state['periode']),
             x="capteur",
             y="valeur",
             labels={
                     "capteur": "Capteur",
                     "valeur": "°C"
                 },
             box=True,
             points="all",
             title='Distribution, brute')
st.plotly_chart(fig)

# Tracer les violons
fig = px.violin(selectionner_obser_series(df_f,
                                          st.session_state['periode']),
             x="capteur",
             y="valeur",
             color="noeud",
             labels={
                     "capteur": "Capteur",
                     "valeur": "°C",
                     "noeud": "Noeud"
                 },
             box=True,
             points="all",
             title='Distribution par noeud, brute')
st.plotly_chart(fig)

st.subheader("Graphiques: humidité")

# Filtrer pour les prochaines graphiques
# Refiltrer les noeuds
df_f = filtrer_dataframe_series(df_ts, "humidite", "brute").loc[df_ts['noeud'].isin(liste_noeud)]

# Tracer la ligne
fig = px.line(selectionner_obser_series(df_f,
                                        st.session_state['periode']),
              x="datetime",
              y="valeur",
              color='noeud',
              labels={
                     "datetime": "",
                     "valeur": "%",
                     "noeud": "Noeud"
                  },
              title='Brute')

st.plotly_chart(fig)


# Tracer les barres
fig = px.bar(selectionner_obser_series(df_f,
                                       st.session_state['periode']),
             x="datetime",
             y="valeur_delta",
             color='noeud',
             labels={
                     "datetime": "",
                     "valeur_delta": "différence en %",
                     "noeud": "Noeud"
                 },
             title='Brute, changement, période à période')
st.plotly_chart(fig)

# Filtrer pour les prochaines graphiques
# Refiltrer les noeuds
df_f = filtrer_dataframe_series(df_ts, "humidite", "brute").loc[df_ts['noeud'].isin(liste_noeud)]

# Tracer les violons
fig = px.violin(selectionner_obser_series(df_f,
                                          st.session_state['periode']),
             x="capteur",
             y="valeur",
             labels={
                     "capteur": "Capteur",
                     "valeur": "%"
                 },
             box=True,
             points="all",
             title='Distribution, brute')
st.plotly_chart(fig)

# Tracer les violons
fig = px.violin(selectionner_obser_series(df_f,
                                          st.session_state['periode']),
             x="capteur",
             y="valeur",
             color="noeud",
             labels={
                     "capteur": "Capteur",
                     "valeur": "%",
                     "noeud": "Noeud"
                 },
             box=True,
             points="all",
             title='Distribution, par noeud, brute')
st.plotly_chart(fig)
