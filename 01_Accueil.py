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

##################################################
st.title ("Tableau de bord")

st.markdown(
    "Projet intégrateur de l'équipe Toucan Fortuné."
)

# ???
st.write("Todo: changer le schéma, st.expander de 6_six.py avant Schéma, st.tabs de 6_six.py pour les schémas, ")

st.header("Description")          

st.markdown(
    "Il s'agit d'un *pipeline* pour acheminer des données en à partir des capteurs jusqu'à ce tableau de bord. Voir le [diagramme de déploiement](#diagramme-de-d-ploiement) en bas de page."
)

st.markdown(
    "Les pages comportent de l'interaction afin de permettre à l'utilisateur de modifier l'information présentée."
)

st.subheader("Métriques")

st.markdown(
    "La page présente les données ponctuelles les plus à jour."
)

st.subheader("Séries")

st.markdown(
    "La page présente des séries chronologiques sur plusieurs périodes de temps."
)

st.subheader("Analyses")

st.markdown(
    "La page comportent des analyses (statistiques descriptives) des données sur plusieurs périodes de temps."
)

st.header("Diagramme de déploiement")

with st.expander("Pour plus de précision..."):
    st.markdown(
        "En première partie du *pipeline*, les capteurs peut être n'importe quel composant qui mesure quelque chose pour alimenter le tableau de bord: données environnementales, quantités de gaz ou de fumée, rayonnements dans différentes longueurs d'onde, niveaux sonores, distances par sonar ou lidar, ainsi de suite."
    )

    st.markdown(
        "En première partie du *pipeline*, la voie du WiFi-serveur-service-MQTT est une des possibilités. Il existe d'autres voies comme celle du LoRa-passerelle-LoRaWAN-TTN; ou d'autres protocoles Low-Power WAN (LPWAN)."
    )

tab1, tab2, tab3 = st.tabs(["WiFi", "LoRa", "Plus"])

with tab1:
    st.image("img/diagramme_deploiement_wifi.png")

with tab2:
    st.image("img/diagramme_deploiement_lora.png")

with tab3:
    st.image("img/diagramme_deploiement_plus.png")

st.header("Possibilités") 

st.markdown(
    "Il pourrait y avoir une page **Prédiction**, par exemple, pour présenter un modèle statistiques (*Machine Learning*): projection de la tendance par régression ou modèle de séries chronologiques, classification de valeurs normales-extrêmes (par régression logistique, arbre de décision ou modèle d'ensemble du genre Random Forests, Support Vector Machine), détection d'anomalies (par K-Means, Gaussian Mixture Model ou réseau de neurone quelconque)."
)