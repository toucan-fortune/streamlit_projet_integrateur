import streamlit as st
import base64
import pymongo
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

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
WARNING = "Seul les noeuds 001 à 003 sont actifs."
#WARNING = "Seuls les noeuds 001 à 001 sont actifs."
NO_LIGNES = 50

##################################################
# Construire la page
st.title("Séries")

# Établir la connexion à la base de données
@st.experimental_singleton
def etablir_connexion():
    # Chercher les données dans le fichier secrets.toml
    URI = f"mongodb+srv://{st.secrets['db_username']}:{st.secrets['db_pw']}@{st.secrets['db_cluster']}.gzo0glz.mongodb.net/?retryWrites=true&writeConcern=majority"
    return pymongo.MongoClient(URI)

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
def filtrer_dataframe(dataframe, capteur, metrique):
    # Construire les filtres
    filtre_capteur = dataframe['capteur'] == capteur
    filtre_metrique = dataframe['metrique'] == metrique
    # Appliquer les filtre
    dataframe_f = dataframe.loc[filtre_capteur & filtre_metrique]
    return dataframe_f

# Sélectionner les observations
@st.experimental_memo
def selectionner_observations(dataframe, nombre):
    # Trier les observations
    # descending, newest to oldest ou ascending=False
    # ascending, oldest to newest ou ascending=True
    dataframe.sort_index(ascending=False, inplace=True)
    # Sélectionner les n premières observations
    dataframe_2 = dataframe.iloc[0:nombre]
    # Créer une colonne de retard
    dataframe_2.loc[:, 'valeur_precedente'] = dataframe_2['valeur'].shift(periods=-1, fill_value=float('nan'))
    # Calculer le delta
    dataframe_2.loc[0:, 'valeur_delta'] = dataframe_2['valeur'] - dataframe_2['valeur_precedente']
    dataframe_2.loc[0:, 'valeur_pct_delta'] = dataframe_2['valeur'] / dataframe_2['valeur_precedente'] - 1
    return dataframe_2

##################################################
# Établir la connexion à la base de données
client = etablir_connexion()

##################################################
st.header("Sélections")

# Confirmer les changements d'état
# du formulaire
def mettre_jour_002():
    for i in range(1, COMPTE_NOEUD + 1, 1):
        i = '{:03d}'.format(i)
        st.session_state[f'noeud{i}a'] = st.session_state[f'noeud{i}b']
        
# Construire un formulaire de changement des états
with st.form(key='form002', clear_on_submit=False):
    st.subheader("Sélectionner les noeuds à afficher")
    
    st.warning(WARNING)
    
    # st.columns(spec, *, gap="small")
    col1, col2, col3 = st.columns(3)
    with col1:
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
    submit_button = st.form_submit_button('Soumettre', on_click=mettre_jour_002)

# Construire un onglet de changement de l'étendue
st.subheader("Sélectionner l'étendue")

st.markdown("n périodes chronologiques.")
st.info("De 5 à 20 périodes.")
st.slider("Sélectionner", 5, 20, 10, 5, key='periode')

# ???
# Construire un onglet de changement du delai
# st.select_slider(label, options=(), value=None, format_func=special_internal_function, key=None, help=None, on_change=None, args=None, kwargs=None, *, disabled=False, label_visibility="visible")
st.subheader("Sélectionner le délai de mise à jour")
st.info("De 10s à 60s entre chaque extraction de la base de données.")
st.slider("Sélectionner", 10, 60, 20, 5, key='delai')

##################################################
# ???automatiser ici

# Importer les données de la collection
df = extraire_documents_dataframe()
# Préparer le DataFrame
# Trier par noeud, puis datetime
df_ts = preparer_dataframe(df).sort_values(by=["noeud", "datetime"])

##################################################
st.header("Affichage")

# Construire les graphiques
st.warning(WARNING)

st.subheader("Tableau interactif de 10 observations")
st.caption("Le DataFrame est trié en ordre descendant; la première rangée montre l'observation la plus récent.")

# Afficher un tableau interactif
st.dataframe(df_ts.head(10))

st.subheader("Graphiques: température")

# Filtrer pour les prochaines graphiques
liste_noeud = []
if st.session_state['noeud001a']:
    liste_noeud.append('noeud01')
if st.session_state['noeud002a']:
    liste_noeud.append('noeud02')
if st.session_state['noeud003a']:
    liste_noeud.append('noeud03')
# ...

# Filtrer pour les prochaines graphiques
# Refiltrer les noeuds
df_f = filtrer_dataframe(df_ts, "temperature", "brute").loc[df_ts['noeud'].isin(liste_noeud)]

# Tracer la ligne
# st.plotly_chart(figure_or_data, use_container_width=False, sharing="streamlit", theme="streamlit", **kwargs)
fig = px.line(selectionner_observations(df_f,
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
fig = px.bar(selectionner_observations(df_f,
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
st.plotly_chart(fig)

# Tracer les barres
fig = px.bar(selectionner_observations(df_f,
                                       st.session_state['periode']),
             x="datetime",
             y="valeur_pct_delta",
             color='noeud',
             labels={
                     "datetime": "",
                     "valeur_pct_delta": "% différence en °C",
                     "noeud": "Noeud"
                 },
             title='Brute, % changement (période à période)')
st.plotly_chart(fig)

st.subheader("Graphique: humidité")

# Filtrer pour les prochaines graphiques
# Refiltrer les noeuds
df_f = filtrer_dataframe(df_ts, "humidité", "brute").loc[df_ts['noeud'].isin(liste_noeud)]

# Tracer la ligne
fig = px.line(selectionner_observations(df_f,
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
fig = px.bar(selectionner_observations(df_f,
                                       st.session_state['periode']),
             x="datetime",
             y="valeur_delta",
             color='noeud',
             labels={
                     "datetime": "",
                     "valeur_delta": "différence en %",
                     "noeud": "Noeud"
                 },
             title='Brute, changement (période à période)')
st.plotly_chart(fig)




# ???
# pas de boites de sélection de noeuds
# juste périodes
st.subheader("Pour la page Analyses")

# Filtrer pour les prochaines graphiques
df_f = filtrer_dataframe(df_ts, "temperature", "brute")

# Tracer les violons
fig = px.violin(selectionner_observations(df_f,
                                          st.session_state['periode']),
             x="capteur",
             y="valeur",
             labels={
                     "capteur": "Capteur",
                     "valeur": "°C"
                 },
             box=True,
             points="all",
             title='Distribution de la température brute')
st.plotly_chart(fig)

# Tracer les violons
fig = px.violin(selectionner_observations(df_f,
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
             title='Distribution de la température brute par noeud')
st.plotly_chart(fig)

# Filtrer pour les prochaines graphiques
df_f = filtrer_dataframe(df_ts, "humidité", "brute")

# Tracer les violons
fig = px.violin(selectionner_observations(df_f,
                                          st.session_state['periode']),
             x="capteur",
             y="valeur",
             labels={
                     "capteur": "Capteur",
                     "valeur": "%"
                 },
             box=True,
             points="all",
             title='Distribution de l\'humidité brute')
st.plotly_chart(fig)

# Tracer les violons
fig = px.violin(selectionner_observations(df_f,
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
             title='Distribution de l\'humidité brute par noeud')
st.plotly_chart(fig)