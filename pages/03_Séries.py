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
st.title("Séries")

# ???
st.write("Todo: mettre T et H sur 2 colonnes comme 02_tableau.py, Resampling des periodes: s à min à 10min à heure à 6h à 12h à 24h ou jour à semaine à mois... ")
st.write("https://docs.streamlit.io/knowledge-base/using-streamlit/hide-row-indices-displaying-dataframe")

# Établir la connexion à la base de données
@st.experimental_singleton
def etablir_connexion():
    # Chercher les données dans le fichier secrets.toml
    URI = f"mongodb+srv://{st.secrets['db_username']}:{st.secrets['db_pw']}@{st.secrets['db_cluster']}.gzo0glz.mongodb.net/?retryWrites=true&writeConcern=majority"
    return pymongo.MongoClient(URI)

client = etablir_connexion()

# Importer les données de la collection
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

# Filtrer le DataFrame
@st.experimental_memo
def filtrer_dataframe(dataframe, capteur):
    # Construire les filtres
    # ???metrique
    filtre_capteur = dataframe['capteur'] == capteur
    #filtre_metrique = dataframe['capteur'] == metrique
    # Appliquer les filtre
    dataframe_f = dataframe.loc[filtre_capteur]
    return dataframe_f

df_f = filtrer_dataframe(df_ts, "linhome")

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
    dataframe_2.loc[:, 'valeur_delta'] = dataframe_2['valeur'] - dataframe_2['valeur_precedente']
    dataframe_2.loc[:, 'valeur_pct_delta'] = dataframe_2['valeur'] / dataframe_2['valeur_precedente'] - 1
    return dataframe_2

st.header("Sélections")

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
st.slider("Sélectionner", 10, 60, 20, 5, key='delai')

# Construire un onglet de changement de l'étendue
st.subheader("Sélectionner l'étendue")

st.markdown("n périodes chronologiques.")
st.info("De 5 à 20 périodes.")
st.slider("Sélectionner", 5, 20, 10, 5, key='periode')

st.write(st.session_state)

st.write()



st.header("Affichage")

# Construire les graphiques
st.warning(WARNING)

st.subheader("Température et ???")

# ???
# https://plotly.com/python/facet-plots/

# Tracer la ligne
# st.plotly_chart(figure_or_data, use_container_width=False, sharing="streamlit", theme="streamlit", **kwargs)
fig = px.line(selectionner_observations(df_f, st.session_state['periode']),
              x="datetime",
              y="valeur",
              color='capteur',
              labels={
                     "datetime": "",
                     "valeur": "°C",
                     "capteur": "Capteur"
                  },
              title='Température')
st.plotly_chart(fig)

# Tracer les barres
fig = px.bar(selectionner_observations(df_f, st.session_state['periode']),
             x="datetime",
             y="valeur_delta",
             color='capteur',
             labels={
                     "datetime": "",
                     "valeur_delta": "différence en °C",
                     "capteur": "Capteur"
                 },
             title='Delta de Température')
st.plotly_chart(fig)

# Tracer les barres
fig = px.bar(selectionner_observations(df_f, st.session_state['periode']),
             x="datetime",
             y="valeur_pct_delta",
             color='capteur',
             labels={
                     "datetime": "",
                     "valeur_pct_delta": "% différence en °C",
                     "capteur": "Capteur"
                 },
             title='Delta (%) de Température')
st.plotly_chart(fig)


st.write(selectionner_observations(df_f, st.session_state['periode']))

# Tracer les boites
fig = px.box(selectionner_observations(df_f, st.session_state['periode']),
             x="capteur",
             y="valeur",
             labels={
                     "capteur": "Capteur",
                     "valeur": "°C",
                 },
             points="all",
             title='Distribution de Température')
st.plotly_chart(fig)

# Tracer les violons
fig = px.violin(selectionner_observations(df_f, st.session_state['periode']),
             x="capteur",
             y="valeur",
             labels={
                     "capteur": "Capteur",
                     "valeur": "°C",
                 },
             box=True,
             points="all",
             title='Distribution de Température')
st.plotly_chart(fig)