"""
app.py
Interface web simple (Streamlit) pour interagir avec le système
multi-agents sans passer par le terminal. Affiche aussi le raisonnement
de chaque agent, pour rendre le fonctionnement transparent.

Pour l'exécuter : streamlit run src/app.py
"""

import streamlit as st
from graphe import construire_graphe

st.set_page_config(page_title="TaskFlow Support Agent", page_icon="🤖")

st.title("🤖 TaskFlow Support Agent")
st.caption(
    "Système multi-agents (Routeur → Chercheur → Vérificateur) qui traite "
    "automatiquement les tickets de support client, avec escalade humaine "
    "si la réponse ne peut pas être garantie fiable."
)

# On ne reconstruit le graphe qu'une seule fois, pas à chaque interaction
@st.cache_resource
def get_app():
    return construire_graphe()

app = get_app()

# Quelques exemples cliquables pour tester rapidement sans taper de texte
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

        # --- Résumé du traitement ---
        col1, col2, col3 = st.columns(3)
        col1.metric("Catégorie", resultat["categorie"])
        col2.metric("Urgence", resultat["urgence"])
        col3.metric("Tentatives", resultat["tentatives"])

        st.divider()

        # --- Résultat final ---
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

        # --- Détail du raisonnement (pour la transparence, repliable) ---
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