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
WARNING = "Seul le noeud 001 est actif. Les autres valeurs sont fictives."
#WARNING = "Seuls les noeuds 001 à 001 sont actifs."
NO_LIGNES= 50

# Déterminer les états de départ
st.session_state['noeud001a'] = False
st.session_state['noeud002a'] = False
st.session_state['noeud003a'] = False
st.session_state['noeud004a'] = False
st.session_state['noeud005a'] = False
st.session_state['noeud006a'] = False
st.session_state['noeud007a'] = False
st.session_state['noeud008a'] = False
st.session_state['noeud009a'] = False

##################################################
# Construire la page
st.title("Métriques")

# ???
st.write("Todo: créer automatisation de lire_mongo.py et 02.tableau.py, le faire marcher sur cette page avant de le déployer sur les autres pages, revoir les callback de 7_sept.py, écrire les formats {:.2f} {:.1%}")
# Resampling des periodes: s à min à 10min à heure à 6h à 12h à 24h ou jour à semaine à mois...
st.write("https://docs.streamlit.io/knowledge-base/using-streamlit/hide-row-indices-displaying-dataframe")

# Établir la connexion à la base de données
# https://docs.streamlit.io/streamlit-cloud/get-started/deploy-an-app/connect-to-data-sources/secrets-management
# https://docs.streamlit.io/library/api-reference/performance/st.experimental_singleton
# https://docs.streamlit.io/library/api-reference/performance/st.experimental_singleton.clear
@st.experimental_singleton
def etablir_connexion():
    # Chercher les données dans le fichier secrets.toml
    URI = f"mongodb+srv://{st.secrets['db_username']}:{st.secrets['db_pw']}@{st.secrets['db_cluster']}.gzo0glz.mongodb.net/?retryWrites=true&writeConcern=majority"
    return pymongo.MongoClient(URI)

client = etablir_connexion()

# Importer les données de la collection
# https://docs.streamlit.io/library/api-reference/performance/st.experimental_memo
@st.experimental_memo
def extraire_documents_dataframe():
    # Sélectioner la base de données
    db = client.toucan
    # Extraire de la collection et filtrer les documents
    # -1 sort descending, newest to oldest
    items = list(db.format2.find().sort("datetime",
                                        -1).limit(NO_LIGNES)) 
    # Convertir en DataFrame
    dataframe = pd.DataFrame(items)
    return dataframe

df = extraire_documents_dataframe()

# Préparer le DataFrame
@st.experimental_memo
def preparer_dataframe(dataframe):
    # Enlever une colonne
    dataframe.drop(['_id'], axis=1, inplace=True)
    # Transformer une colonne en ts
    dataframe['datetime'] = pd.to_datetime(dataframe['datetime'], infer_datetime_format=True)
    # Envoyer la colonne dans l'index
    dataframe_ts = dataframe.set_index(dataframe['datetime'], drop=False)
    # ???
    # Convertir string en float (valeur)
    return dataframe_ts

df_ts = preparer_dataframe(df)

# ???
# {"datetime": "2023-01-13 16:15:39.401550",
#  "noeud": "pico001",  
#  "capteur": "temperature",
#  "metrique": "moy_10_min",
#  "valeur": "1min"}

# Filtrer le DataFrame
@st.experimental_memo
def filtrer_dataframe(dataframe, capteur):
    # Construire les filtres
    # ???noeud, metrique
    #filtre_noeud = dataframe['noeud'] == noeud
    filtre_capteur = dataframe['capteur'] == capteur
    #filtre_metrique = dataframe['capteur'] == metrique
    # Appliquer les filtre
    dataframe_f = dataframe.loc[filtre_capteur]
    return dataframe_f

df_f = filtrer_dataframe(df_ts, "linhome")

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
    valeur_metrique = round(dataframe_2['valeur'].iloc[0], 2)
    valeur_delta = round(dataframe_2['valeur_delta'].iloc[0], 2)
    return valeur_metrique, valeur_delta


st.header("Sélection")

# Confirmer les changements d'état
# du formulaire
def mettre_jour_avec_form001():
    for i in range(1, COMPTE_NOEUD + 1, 1):
        i = '{:03d}'.format(i)
        #st.write(i)
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
        st.checkbox('Noeud 001', key='noeud001b')
        st.checkbox('Noeud 002', key='noeud002b')
        st.checkbox('Noeud 003', key='noeud003b')
    with col2:
        st.checkbox('Noeud 004', key='noeud004b')
        st.checkbox('Noeud 005', key='noeud005b')
        st.checkbox('Noeud 006', key='noeud006b')   
    with col3:
        st.checkbox('Noeud 007', key='noeud007b')
        st.checkbox('Noeud 008', key='noeud008b')
        st.checkbox('Noeud 009', key='noeud009b')
    # Invoquer la fonction callback    
    submit_button = st.form_submit_button('Soumettre', on_click=mettre_jour_avec_form001)

# ???
# Construire un onglet de changement du delai
# st.select_slider(label, options=(), value=None, format_func=special_internal_function, key=None, help=None, on_change=None, args=None, kwargs=None, *, disabled=False, label_visibility="visible")
st.subheader("Sélectionner le délai de mise à jour")
st.info("De 10s à 60s entre chaque extraction de la base de données.")
delai = st.slider("Sélectionner", 10, 60, 20, 5)


st.header("Affichage")
        
# Construire les métriques
st.warning(WARNING)

col1, col2 = st.columns(2, gap="small")

with col1:
    st.subheader("Température")
    
    # st.metric(label, value, delta=None, delta_color="normal", help=None, label_visibility="visible")
    if st.session_state['noeud001b']:
        st.metric("Noeud 001",
                  f'{selectionner_observations(df_f)[0]}°C',
                  f'{selectionner_observations(df_f)[1]}°C')
    if st.session_state['noeud002b']:
        st.metric("Noeud 002", f'{18.3}°C', 1)
    if st.session_state['noeud003b']:
        st.metric("Noeud 003", f'{22.7}°C', -1)

with col2:
    st.subheader("Humidité")
    if st.session_state['noeud001b']:
        st.metric("Noeud 001", f'{35.1}%', 2)
    if st.session_state['noeud002b']:
        st.metric("Noeud 002", f'{36.7}%', 1)
    if st.session_state['noeud003b']:
        st.metric("Noeud 003", f'{33.3}%', -1)
