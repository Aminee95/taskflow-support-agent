"""
app.py
Interface web simple (Streamlit) pour interagir avec le système
multi-agents sans passer par le terminal. Affiche aussi le raisonnement
de chaque agent, pour rendre le fonctionnement transparent.

Pour l'exécuter en local : streamlit run src/app.py
"""

import os
import streamlit as st
from graphe import construire_graphe

st.set_page_config(page_title="TaskFlow Support Agent", page_icon="🤖")

# Sur un déploiement en ligne (Streamlit Cloud), le dossier chroma_db/
# n'existe pas encore puisqu'il est exclu du dépôt Git (voir .gitignore).
# On le reconstruit automatiquement au premier démarrage si besoin.
if not os.path.exists("chroma_db"):
    with st.spinner("Premier démarrage : construction de la base de connaissances..."):
        from ingest import load_documents, split_documents, build_vectorstore
        docs = load_documents()
        chunks = split_documents(docs)
        build_vectorstore(chunks)

st.title("🤖 TaskFlow Support Agent")
st.caption(
    "Système multi-agents (Routeur → Chercheur → Vérificateur) qui traite "
    "automatiquement les tickets de support client, avec escalade humaine "
    "si la réponse ne peut pas être garantie fiable."
)


@st.cache_resource
def get_app():
    return construire_graphe()


app = get_app()

exemples = {
    "Facturation simple": "Je n'ai pas reçu ma facture du mois dernier, pouvez-vous me la renvoyer ?",
    "Question produit": "Comment inviter un collègue sur mon espace de travail ?",
    "Plainte (doit escalader)": "Ça fait 3 fois que je contacte le support sans solution, je suis très déçu.",
    "Bug non documenté (doit escalader)": "L'application plante à chaque fois que je clique sur une tâche.",
}

st.subheader("Tester un ticket")

exemple_choisi = st.selectbox(
    "Choisir un exemple, ou écrire votre propre ticket ci-dessous :",
    ["-- Écrire mon propre ticket --"] + list(exemples.keys()),
)

valeur_defaut = "" if exemple_choisi == "-- Écrire mon propre ticket --" else exemples[exemple_choisi]

message = st.text_area("Message du ticket client", value=valeur_defaut, height=100)

if st.button("Traiter le ticket", type="primary"):
    if not message.strip():
        st.warning("Merci d'écrire un message de ticket.")
    else:
        with st.spinner("Les agents traitent le ticket..."):
            resultat = app.invoke({"message": message, "tentatives": 0})

        col1, col2, col3 = st.columns(3)
        col1.metric("Catégorie", resultat["categorie"])
        col2.metric("Urgence", resultat["urgence"])
        col3.metric("Tentatives", resultat["tentatives"])

        st.divider()

        if resultat["statut_final"] == "repondu":
            st.success("✅ Réponse automatique validée")
            st.write(resultat["reponse"])
        else:
            st.error("🚨 Escaladé à un humain")
            st.write(
                "Le système n'a pas pu garantir une réponse fiable pour ce "
                "ticket. Il a été transmis à un agent humain plutôt que de "
                "risquer une réponse incorrecte."
            )

        with st.expander("Voir le détail du raisonnement des agents"):
            st.json({
                "categorie": resultat["categorie"],
                "urgence": resultat["urgence"],
                "necessite_escalade_directe_par_routeur": resultat["necessite_escalade"],
                "nombre_de_tentatives_chercheur": resultat["tentatives"],
                "statut_final": resultat["statut_final"],
            })

st.divider()
st.caption(
    "Projet démo — TaskFlow est un produit fictif. "
    "Code source : github.com/Aminee95/taskflow-support-agent"
)