import streamlit as st
import pandas as pd
import plotly.express as px
from dotenv import load_dotenv
import os
from groq import Groq

load_dotenv()
api_key = os.getenv('GROQ_API_KEY')
if not api_key:
    try:
        api_key = st.secrets["GROQ_API_KEY"]
    except:
        pass
client = Groq(api_key=api_key)

st.set_page_config(page_title="Offres d'emploi au Sénégal", layout="wide")

@st.cache_data
def load_data():
    df = pd.read_csv('dataset_final_propre.csv', encoding='utf-8')
    df['mois'] = pd.to_datetime(df['mois'], errors='coerce')
    df = df.dropna(subset=['mois'])
    return df

df = load_data()

st.title("Analyse des offres d'emploi au Sénégal")
st.caption("Source : senjob.com & goafricaonline.com - Juillet 2024 à Avril 2026")

st.sidebar.header("Filtres")

secteurs = ['Tous'] + sorted([s for s in df['secteur'].dropna().unique() if s != 'Non spécifié'])
secteur_choisi = st.sidebar.selectbox("Secteur", secteurs)

annees = ['Toutes'] + sorted(df['mois'].dt.year.dropna().unique().astype(str).tolist())
annee_choisie = st.sidebar.selectbox("Année", annees)

villes = ['Toutes'] + sorted([v for v in df['ville'].dropna().unique() if v != 'Non spécifié'])
ville_choisie = st.sidebar.selectbox("Ville", villes)

contrats = ['Tous'] + sorted([c for c in df['contrat'].dropna().unique() if c != 'Non spécifié'])
contrat_choisi = st.sidebar.selectbox("Type de contrat", contrats)

dff = df.copy()
if secteur_choisi != 'Tous':
    dff = dff[dff['secteur'] == secteur_choisi]
if annee_choisie != 'Toutes':
    dff = dff[dff['mois'].dt.year == int(annee_choisie)]
if ville_choisie != 'Toutes':
    dff = dff[dff['ville'] == ville_choisie]
if contrat_choisi != 'Tous':
    dff = dff[dff['contrat'] == contrat_choisi]

col1, col2, col3, col4 = st.columns(4)
col1.metric("Total offres", len(dff))
col2.metric("Secteur dominant", dff['secteur'].value_counts().index[0] if len(dff) > 0 else "—")
col3.metric("Ville principale", dff['ville'].value_counts().index[0] if len(dff) > 0 else "—")
col4.metric("Contrat majoritaire", dff['contrat'].value_counts().index[0] if len(dff) > 0 else "—")

st.divider()

col_a, col_b = st.columns(2)

with col_a:
    st.subheader("Top secteurs")
    secteur_count = dff['secteur'].value_counts().dropna().head(10).reset_index()
    secteur_count.columns = ['secteur', 'count']
    fig1 = px.bar(secteur_count, x='count', y='secteur', orientation='h',
                  color_discrete_sequence=['#1D9E75'])
    fig1.update_layout(yaxis={'categoryorder': 'total ascending'},
                       xaxis_title="Nombre d'offres", yaxis_title="")
    st.plotly_chart(fig1, use_container_width=True)

with col_b:
    st.subheader("Répartition des contrats")
    contrat_count = dff['contrat'].value_counts().dropna().reset_index()
    contrat_count.columns = ['contrat', 'count']
    fig2 = px.bar(contrat_count, x='count', y='contrat', orientation='h',
                  color_discrete_sequence=['#1D9E75'])
    fig2.update_layout(yaxis={'categoryorder': 'total ascending'},
                       xaxis_title="Nombre d'offres", yaxis_title="")
    st.plotly_chart(fig2, use_container_width=True)

st.subheader("Évolution mensuelle des offres")
evolution = dff.groupby('mois').size().reset_index(name='nb_offres')
fig3 = px.line(evolution, x='mois', y='nb_offres',
               color_discrete_sequence=['#1D9E75'],
               markers=True)
fig3.update_layout(xaxis_title="Mois", yaxis_title="Nombre d'offres")
st.plotly_chart(fig3, use_container_width=True)

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(f"""
    <div style="background:#E8F7F2; padding:16px; border-radius:8px; border-left:4px solid #1D9E75;">
        <p style="margin:0; font-size:12px; color:#666;">Total offres</p>
        <p style="margin:0; font-size:24px; font-weight:bold; color:#1D9E75;">{len(dff)}</p>
    </div>
    """, unsafe_allow_html=True)

with col2:
    val = dff['secteur'].value_counts().index[0] if len(dff) > 0 else "—"
    st.markdown(f"""
    <div style="background:#E8F7F2; padding:16px; border-radius:8px; border-left:4px solid #1D9E75;">
        <p style="margin:0; font-size:12px; color:#666;">Secteur dominant</p>
        <p style="margin:0; font-size:13px; font-weight:bold; color:#1A1A1A;">{val}</p>
    </div>
    """, unsafe_allow_html=True)

with col3:
    val = dff['ville'].value_counts().index[0] if len(dff) > 0 else "—"
    st.markdown(f"""
    <div style="background:#E8F7F2; padding:16px; border-radius:8px; border-left:4px solid #1D9E75;">
        <p style="margin:0; font-size:12px; color:#666;">Ville principale</p>
        <p style="margin:0; font-size:13px; font-weight:bold; color:#1A1A1A;">{val}</p>
    </div>
    """, unsafe_allow_html=True)

with col4:
    val = dff['contrat'].value_counts().index[0] if len(dff) > 0 else "—"
    st.markdown(f"""
    <div style="background:#E8F7F2; padding:16px; border-radius:8px; border-left:4px solid #1D9E75;">
        <p style="margin:0; font-size:12px; color:#666;">Contrat majoritaire</p>
        <p style="margin:0; font-size:13px; font-weight:bold; color:#1A1A1A;">{val}</p>
    </div>
    """, unsafe_allow_html=True)

st.divider()
st.subheader("Assistant IA :  Posez vos questions sur les données")

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

question = st.chat_input("Ex: Quel secteur recrute le plus ? Quelles compétences sont demandées ?")

if question:
    st.session_state.messages.append({"role": "user", "content": question})
    with st.chat_message("user"):
        st.markdown(question)

    contexte = f"""Tu es un assistant spécialisé dans l'analyse du marché de l'emploi au Sénégal.
Voici les données disponibles :
- Total offres : {len(dff)}
- Secteur dominant : {dff['secteur'].value_counts().index[0] if len(dff) > 0 else '—'}
- Ville principale : {dff['ville'].value_counts().index[0] if len(dff) > 0 else '—'}
- Contrat majoritaire : {dff['contrat'].value_counts().index[0] if len(dff) > 0 else '—'}
- Top 5 secteurs : {dff['secteur'].value_counts().head(5).to_dict()}
- Top 5 compétences : {dff['competences'].dropna().str.split(',').explode().str.strip().value_counts().head(5).to_dict()}
- Top 5 villes : {dff['ville'].value_counts().head(5).to_dict()}
- Offres par année : {dff.groupby(dff['mois'].dt.year).size().to_dict()}
Réponds en français, de façon concise et professionnelle.
Question : {question}"""

    try:
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": "Tu es un assistant data analyst spécialisé dans le marché de l'emploi au Sénégal. Réponds toujours en français."},
                {"role": "user", "content": contexte}
            ],
            max_tokens=500
        )
        reponse = response.choices[0].message.content
    except Exception as e:
        reponse = f"Erreur : {str(e)}"

    st.session_state.messages.append({"role": "assistant", "content": reponse})
    with st.chat_message("assistant"):
        st.markdown(reponse)