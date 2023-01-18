import streamlit as st
import base64
import pymongo
import pandas as pd
import plotly.express as px
import datetime
import time

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
WARNING = "Seul le noeuds 001 est actif."

# Construire la page
st.title("Démo Asynchrone")

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

# Filtrer le DataFrame
@st.experimental_memo
def filtrer_dataframe_series(dataframe, capteur, metrique):
    # Construire les filtres
    filtre_capteur = dataframe['capteur'] == capteur
    filtre_metrique = dataframe['metrique'] == metrique
    # Appliquer les filtre
    dataframe_f = dataframe.loc[filtre_capteur & filtre_metrique]
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
    # Marquer un temps de référence
    maintenant = datetime.datetime.now()
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
        st.checkbox('Noeud 001', key='st_noeud001', value=True)

# Construire un onglet de changement de l'étendue
st.subheader("Sélectionner l'étendue")

st.info(f"De 5 à {st.session_state['nolignes']} périodes chronologiques.")
st.slider("Sélectionner", 5, st.session_state["nolignes"], 10, 5, key='periode')

# Construire un onglet de l'intervalle de temps
st.subheader("Sélectionner l'intervalle de temps")

# Construire un contenant
with st.container():
    # Construire des placeholders
    p_delai_info = st.empty()
    p_delai_slider = st.empty()
    
    # Construire des placeholders
    p_activer_button = st.empty()
    p_arreter_button = st.empty()
    st.caption("... les extractions à intervalles.")
    delta_temps_caption = st.empty()

st.header("Affichage")

# Utiliser les placeholder
st.warning(WARNING)

col1, col2 = st.columns(2, gap="small")

with col1:
    st.subheader("Température")

    # Construire des placeholders
    p_metric_t001 = st.empty()
    p_caption_t001 = st.empty()
    
with col2:
    st.subheader("Humidité")
    # Construire des placeholders
    p_metric_h001 = st.empty()
    p_caption_h001 = st.empty()
    
st.subheader("Graphique: température")
    
p_chart_a = st.empty()
p_chart_b = st.empty()

##################################################

# Construire les placeholders
p_delai_info.info("Intervalles de 3s à 60s entre chaque extraction de la base de données.")
p_delai_slider.slider("Sélectionner", 3, 60, 3, 3, key='delai')

##################################################
# Utiliser les placeholders
# Si objet est True (présent)
if p_activer_button.button('Activer', key='start'):
    # Enlever ces objets
    p_activer_button.empty()
    p_delai_info.empty()
    p_delai_slider.empty()
    # Si objet est True (présent)
    if p_arreter_button.button('Arrêter', key='stop'):
        # Aller à la boucle
        pass
    # Boucle infinie
    # (à moins d'un évènement sur le bouton)
    while True:
        # Calculer le delta entre
        # le temps présent et
        # le temps de référence établi plus haut
        delta_temps = datetime.datetime.now() - maintenant
        # Si le delta est un multiple
        # égal au délai choisi...
        if delta_temps.seconds % st.session_state['delai'] == 0:
            # do...
            delta_temps_caption.write(f"Multiple de l'intervalle: {delta_temps.seconds}")
            ##################################################
            # Importer les données de la collection
            df = extraire_documents_dataframe(_un_client,
                                              st.session_state["base"],
                                              st.session_state["collection"],
                                              st.session_state["nolignes"])
            # Préparer le DataFrame
            df_ts = preparer_dataframe(df)
            # Filtrer le DataFrame
            df_f = filtrer_dataframe_metriques(df_ts, "noeud01", "temperature", "brute")
            # Activer les placeholders
            p_metric_t001.metric("Noeud 001",
                                f"{selectionner_obs_metrique(df_f)[0]:.1f}°C",
                                f"{selectionner_obs_metrique(df_f,)[1]:.1f}°C")
            p_caption_t001.caption(f"{selectionner_obs_metrique(df_f)[2]: %d %b %Y, %Hh%M:%S}")
            # Filtrer le DataFrame
            df_f = filtrer_dataframe_metriques(df_ts, "noeud01", "humidité", "brute")
            # Activer les placeholders
            p_metric_h001.metric("Noeud 001",
                                 f"{selectionner_obs_metrique(df_f)[0]:.1f}%",
                                 f"{selectionner_obs_metrique(df_f,)[1]:.1f}%")
            p_caption_h001.caption(f"{selectionner_obs_metrique(df_f)[2]: %d %b %Y, %Hh%M:%S}")
            # Filtrer pour les prochaines graphiques
            # Refiltrer les noeuds
            liste_noeud = ['noeud01']
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
            # Activer les placeholders
            p_chart_a.plotly_chart(fig)
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
                         title='Brute, changement (période à période)')
            p_chart_b.plotly_chart(fig)
            ##################################################
        # Délai entre intérations
        time.sleep(1)
