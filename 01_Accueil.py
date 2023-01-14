import streamlit as st
import base64

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

st.sidebar.markdown('Tableau de bord, `version 2`')

##################################################
st.title ("Projet de tableau de bord")

st.markdown(
    "Projet intégrateur de l'équipe Toucan Fortuné."
)

st.header("Description du projet")

st.markdown(
    "Il s'agit d'un *pipeline* pour acheminer des données en à partir d'un ou des capteurs jusqu'à ce tableau de bord. Voir le [schéma de déploiement](#sch-ma-de-d-ploiement) en bas de page."
)
 
st.header("Description du tableau de bord")          

st.markdown(
    "Les pages comportent de l'interaction afin de permettre à l'utilisateur de modifier l'information présentée."
)

st.subheader("Métriques")

st.markdown(
    "La page présente les données les plus à jour. Les 2 données les plus récentes sont tirées de MongoDB Atlas. Seule les dernières données sont affichées. Les avant-dernières données comptent dans le calcul du changement."
)

st.subheader("Séries")

st.markdown(
    "La page présente des séries chronologiques des données tirées de MongoDB Atlas."
)

st.subheader("Analyses")

st.markdown(
    "La page comportent des analyses (statistiques descriptives) des données tirées de MongoDB Atlas."
)

st.header("Schéma de déploiement")

st.image("img/schema_wifi.png")

st.header("Possibilité du tableau de bord") 

st.markdown(
    "Il pourrait y avoir une page **Prédiction**, par exemple, pour présenter un modèle statistiques (*Machine Learning*): projection de la tendance par régression ou modèle de séries chronologiques, classification de valeurs normales-extrêmes (par régression logistique, arbre de décision ou modèle d'ensemble du genre Random Forests, Support Vector Machine), détection d'anomalie (par K-Means, Gaussian Mixture Model ou réseau de neurone quelconque."
)