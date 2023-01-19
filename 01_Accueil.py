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
st.title ("Accueil")
    
st.header("Description")          

st.markdown(
    "Il s'agit d'une chaine IoT pour acheminer des données à partir de **noeuds** (capteurs et microcontrôleurs Raspberry Pico) jusqu'à ce **tableau de bord**. Voir les [diagrammes de déploiement](#diagramme-de-d-ploiement) en bas de page."
)

st.markdown(
    "Les pages comportent de l'interaction afin de permettre à l'utilisateur de modifier l'information présentée."
)

st.subheader("Métriques")

st.markdown(
    "Les dernière données captées (les plus à jour)."
)

st.subheader("Séries et Analyses")

st.markdown(
    "Des séries chronologiques de données captées sur plusieurs périodes de temps et des analyses (statistiques descriptives)."
)

st.subheader("Asynchrone")

st.markdown(
    "Les données captées puis affichées de façon asynchrone (avec un délai)."
)

st.header("Diagramme de déploiement")

with st.expander("En première partie du *pipeline*..."):
    st.markdown(
        "En première partie de la chaine, les **capteurs** peut être n'importe quel composant qui prend des mesures pour alimenter le **tableau de bord**: données environnementales (température, humidité, vitesse du vent, pluviométrie, etc.), quantité de gaz ou de fumée, rayonnement à différentes longueurs d'onde, niveau sonore, distance par sonar ou lidar, ainsi de suite. Un microcontrôleur plus puissant permettrait de réalisé du ML à la pointe. Il serait possible, par exemple, de compter des objets avec une caméra, de faire le traitement localement pour n'envoyer que des décomptes (des données comme des entiers)."
    )

    st.markdown(
        "La voie du WiFi est une des possibilités; plus facile pour débuter et tester le projet. La voie du LoRa est plus pratique en IoT. Il existe d'autres voies qui ont chacune des forces et des faiblesses en lien avec le débit de données, la portée du réseau, la consommation énergétique, les coûts, etc."
    )

tab1, tab2, tab3 = st.tabs(["WiFi", "LoRa", "Autres"])

with tab1:
    st.image("img/diagramme_deploiement_wifi.png")

with tab2:
    st.image("img/diagramme_deploiement_lora.png")

with tab3:
    st.image("img/protocols.png")

st.header("Possibilités") 

st.markdown(
    "Il pourrait y avoir une page **Prédiction**, par exemple, pour présenter un modèle statistiques (*Machine Learning*): projection de la tendance par régression ou modèle de séries chronologiques, classification de valeurs normales-extrêmes (par régression logistique, arbre de décision ou modèle d'ensemble du genre Random Forests, Support Vector Machine), détection d'anomalies (par K-Means, Gaussian Mixture Model ou réseau de neurone quelconque)."
)

with st.expander("Possibilités..."):
    st.image("img/diagramme_deploiement_plus.png")
