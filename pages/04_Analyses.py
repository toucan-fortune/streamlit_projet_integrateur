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
st.title("Analyses")














# ???Todo
# transfert

import time
import random
import plotly.express as px
import datetime

# Établir la connexion à la base de données
@st.experimental_singleton
def etablir_connexion():
    # Chercher les données dans le fichier secrets.toml
    URI = f"mongodb+srv://{st.secrets['db_username']}:{st.secrets['db_pw']}@{st.secrets['db_cluster']}.gzo0glz.mongodb.net/?retryWrites=true&writeConcern=majority"
    return pymongo.MongoClient(URI)

client = etablir_connexion()

# Suivant la connexion
# marquer un temps de référence
maintenant = datetime.datetime.now()


NO_LIGNES = 5


# Importer les données de la collection
#@st.experimental_memo
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



st.subheader("Sélection")

with st.container():
    # st.empty, placeholder, réserver cet endroit ici
    delai_info = st.empty()
    delai_slider = st.empty()
    
    # st.empty, placeholder, réserver cet endroit ici
    activer_button = st.empty()
    st.caption("... les extractions à intervalles.")
    arreter_button = st.empty()   

st.subheader("Affichage")

# st.empty, placeholder, réserver cet endroit ici
delta_temps_caption = st.empty()
dataframe_write = st.empty()

# Invoquer les placeholders
delai_info.info("Intervalles de 3s à 60s entre chaque extraction de la base de données.")
delai_slider.slider("Sélectionner", 3, 60, 3, 3, key='delai')

# Si objet est True (présent)
if activer_button.button('Activer', key='start'):
    # Enlever ces objets
    activer_button.empty()
    delai_info.empty()
    delai_slider.empty()
    # Si objet est True (présent)
    if arreter_button.button('Arrêter', key='stop'):
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
            df = extraire_documents_dataframe()
            dataframe_write.write(df)
        # Délai entre intérations
        time.sleep(1)
