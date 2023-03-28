import streamlit as st
import base64
import pymongo
import pandas as pd
import plotly.express as px
import datetime
import time

# Dans le requirements.txt,
# ne pas installer de modules standards à Python



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
BASE = ('toucan',)
#!!!
COLLECTION = ('format10', 'format11', 'format12', 'format13')
DESCRIPTION = """
**format10**: rien - 
**format11**: simulation de pico01 au 15min - 
**format12**: simulation de pico01 à pico09 au 60min - 
**format13**: capteur pico01
"""
NOLIGNES = (50, 100, 200, 400, 800, 1600)
COMPTE_NOEUD = 9
WARNING = "Seuls certains noeuds peuvent être actifs."

##################################################
# Établir la connexion à la base de données
@st.cache_resource(ttl=3600)
def etablir_connexion():
    # Chercher les données dans le fichier secrets.toml
    URI = f"mongodb+srv://{st.secrets['db_username']}:{st.secrets['db_pw']}@{st.secrets['db_cluster']}.gzo0glz.mongodb.net/?retryWrites=true&writeConcern=majority"
    return pymongo.MongoClient(URI)


# Importer les données de la collection
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
def filtrer_dataframe_metriques(dataframe, noeud, capteur, metrique):
    # Construire les filtres
    filtre_noeud = dataframe['noeud'] == noeud
    filtre_capteur = dataframe['capteur'] == capteur
    filtre_metrique = dataframe['metrique'] == metrique
    # Appliquer les filtre
    dataframe_f = dataframe.loc[filtre_noeud & filtre_capteur & filtre_metrique]
    return dataframe_f


# Filtrer le DataFrame
def filtrer_dataframe_series(dataframe, capteur, metrique):
    # Construire les filtres
    filtre_capteur = dataframe['capteur'] == capteur
    filtre_metrique = dataframe['metrique'] == metrique
    # Appliquer les filtre
    dataframe_f = dataframe.loc[filtre_capteur & filtre_metrique]
    return dataframe_f


# Sélectionner les 2 dernières observations
def selectionner_obs_metriques(dataframe):
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
    st.error("Ne peut se connecter au serveur.")

##################################################
# Construire la page
# avec title, header, subheader, markdown, write
# columns, containerm form
# warning, info
# les widgets
# caption, metric

st.title("Asynchrone")

st.header("Sélection")

st.subheader("Sélectionner les données")

col1, col2, col3 = st.columns(3)

with col1:
    # Sélectionner la bd
    st.radio("Base de données",
             BASE, key='base')
with col2:
    # Sélectionner la collection
    st.radio("Collection",
             COLLECTION, key='collection')
with col3:
    # Sélectionner le nombre de documents
    st.radio("Documents",
             NOLIGNES, key='nolignes')

st.caption(DESCRIPTION, unsafe_allow_html=True)

# Construire un contenant
with st.container():
    st.subheader("Sélectionner les noeuds à afficher")

    st.warning(WARNING)

    col1, col2, col3 = st.columns(3)
    with col1:
        # Construire des placeholders
        p_checkbox = st.empty()

st.subheader("Sélectionner l'étendue")

# Construire des placeholders
p_periode_info = st.empty()
p_periode_slider = st.empty()

st.subheader("Sélectionner l'intervalle de temps")

# Construire des placeholders
p_delai_info = st.empty()
p_delai_slider = st.empty()
p_delai_info_2 = st.empty()
p_delai_radio = st.empty()
p_delai_resultat = st.empty()
separateur = st.empty()

# Construire des placeholders
p_demarrer_button = st.empty()
p_arreter_button = st.empty()
p_reactiver_button = st.empty()
p_caption_button = st.empty()
delta_temps_caption = st.empty()

st.header("Affichage")

st.warning(WARNING)
st.warning("Si aucune données n'apparait, il peut y avoir une mauvaise connexion au serveur ou la base de données, la collection ou les données n'existent pas.")

col1, col2 = st.columns(2)

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

st.subheader("Température")

p_chart_a = st.empty()

st.subheader("Humidité")

p_chart_b = st.empty()

##################################################
# Utiliser les placeholders
p_checkbox.checkbox('Noeud 001', key='st_noeud001', value=True)

p_periode_info.info(f"De 5 à {st.session_state['nolignes']} périodes chronologiques.")
p_periode_slider.slider("Sélectionner le nombre de périodes", 5, st.session_state["nolignes"], 10, 5, key='periode')

p_delai_info.info("Intervalles (seconde) entre chaque extraction de la base de données.")
p_delai_slider.slider("Sélectionner l'intervalle", 0.05, 10.0, 1.0, 0.05, key='delai')

p_delai_info_2.info("Multiplicateur de l'intervalle.")
p_delai_radio.radio("Multiplier l'intervalle par", ["1 (garder en seconde)", "60 (convertir en minute)", "3600 (convertir en heure)"], horizontal=True, key="multiplicateur")

# Récupérer le chiffre
mult = int(st.session_state["multiplicateur"].split(" ")[0])

p_delai_resultat.markdown(f"<br>Intervalle résultant: :red[{st.session_state['delai'] * mult:0.0f}s]; environ  :red[{st.session_state['delai'] * mult/60:0.0f}min]; environ  :red[{st.session_state['delai'] * mult/3600:0.0f}h]", unsafe_allow_html=True)

separateur.write("---")

p_caption_button.caption("... les extractions à intervalles de temps.")

##################################################
# Construire ce qui est mis à jour avec la boucle
def boucle():
    # Importer les données de la collection
    try:
        df = extraire_documents_dataframe(_un_client,
                                          st.session_state["base"],
                                          st.session_state["collection"],
                                          st.session_state["nolignes"])
    except:
        p_metric_t001.error("Ne peut se connecter au serveur ou la base de données, la collection ou les données n'existent pas.")
        
    # Préparer le DataFrame
    try:
        df_ts = preparer_dataframe(df)
    except:
        p_metric_t001.error("La base de données, la collection ou les données n'existent pas.")
    
    # Filtrer le DataFrame
    try:
        df_f = filtrer_dataframe_metriques(df_ts, "pico01", "temperature", "brute")
    except:
        p_metric_t001.error("Ne peut filtrer le Noeud 001.")
    
    # Activer les placeholders
    try:
        p_metric_t001.metric("Noeud 001",
                             f"{selectionner_obs_metriques(df_f)[0]:.1f}°C",
                             f"{selectionner_obs_metriques(df_f)[1]:.1f}°C")
        p_caption_t001.caption(f"{selectionner_obs_metriques(df_f)[2]: %d %b %Y, %Hh%M:%S}")
    except:
        p_metric_t001.error("Ne peut afficher le Noeud 001.")
    
    # Filtrer le DataFrame
    try:
        df_f = filtrer_dataframe_metriques(df_ts, "pico01", "humidite", "brute")
    except:
        p_metric_h001.error("Ne peut filtrer le Noeud 001.")
        
    # Activer les placeholders
    try:
        p_metric_h001.metric("Noeud 001",
                              f"{selectionner_obs_metriques(df_f)[0]:.1f}%",
                              f"{selectionner_obs_metriques(df_f)[1]:.1f}%")
        p_caption_h001.caption(f"{selectionner_obs_metriques(df_f)[2]: %d %b %Y, %Hh%M:%S}")
    except:
        p_metric_h001.error("Ne peut afficher le Noeud 001.")
    
    # Déterminer les noeuds
    liste_noeud = ['pico01', 'pico02', 'pico03',
                   'pico04', 'pico05', 'pico06',
                   'pico07', 'pico08', 'pico09']
    
    # Filtrer pour les prochaines graphiques
    try:
        df_f = filtrer_dataframe_series(df_ts, "temperature", "brute").loc[df_ts['noeud'].isin(liste_noeud)]
    except:
        df_f = pd.DataFrame({'datetime': [0],
                             'noeud': [0],
                             'capteur': [0],
                             'metrique': [0],
                             'valeur': [0]})
        pass
    
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
    
    # Filtrer pour les prochaines graphiques
    try:
        df_f = filtrer_dataframe_series(df_ts, "humidite", "brute").loc[df_ts['noeud'].isin(liste_noeud)]
    except:
        pass
        
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
    
    # Activer les placeholders
    p_chart_b.plotly_chart(fig)

##################################################
# Déterminer l'état de la boucle
etat = True

# Si objet est True (bouton appuyé)
if p_demarrer_button.button('Démarrer', key='start'):
    # Enlever ces placeholders
    p_demarrer_button.empty()
    #p_checkbox.empty()
    #p_periode_info.empty()
    #p_periode_slider.empty()
    p_delai_info.empty()
    p_delai_slider.empty()
    p_delai_info_2.empty()
    p_delai_radio.empty()
    # Démarrer le temps
    debut = datetime.datetime.now()
    
    # Si objet est True (bouton appuyé)
    if p_arreter_button.button('Arrêter', key='stop'):
        # Enlever ces placeholders
        p_delai_resultat.empty()
        p_arreter_button.empty()
        p_caption_button.empty()
        delta_temps_caption.empty()
        # Activer les placeholders
        p_reactiver_button.button("Réactiver la sélection de l'intervalle de temps", key='restart')
        # Changer l'état de la boucle
        etat = False
    
    # Boucle
    while etat:
        # Invoquer la fonction de mise à jour
        boucle()
        # Mesurer le temps depuis de démarrage
        delta = datetime.datetime.now() - debut
        delta = str(delta).split(".")[0]
        # Afficher le temps depuis de démarrage
        delta_temps_caption.write(f"Temps depuis le démarrage: :red[{delta}]")
        # Délai entre intérations, les mises à jour
        time.sleep(st.session_state["delai"] * mult)