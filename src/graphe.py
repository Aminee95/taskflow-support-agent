"""
graphe.py
Le coeur du système multi-agents : connecte l'Agent Routeur et l'Agent
Chercheur dans un graphe LangGraph. Le ticket passe automatiquement de
l'un à l'autre, avec une logique de décision au milieu.

Pour l'exécuter : python src/graphe.py
"""

import json
from typing import TypedDict, Optional
from langgraph.graph import StateGraph, END
from dotenv import load_dotenv

from agent_routeur import router_ticket
from agent_chercheur import generer_reponse

load_dotenv()


# ------------------------------------------------------------------
# L'ÉTAT DU GRAPHE
# ------------------------------------------------------------------
# C'est LA notion centrale de LangGraph à comprendre : un dictionnaire
# partagé entre tous les agents, qui s'enrichit au fur et à mesure que
# le ticket avance dans le graphe. Chaque agent lit ce dont il a besoin
# dedans, et y ajoute ses propres résultats.
class EtatTicket(TypedDict):
    message: str                          # le ticket client brut (donnée d'entrée)
    categorie: Optional[str]              # rempli par l'Agent Routeur
    urgence: Optional[str]                # rempli par l'Agent Routeur
    necessite_escalade: Optional[bool]    # rempli par l'Agent Routeur
    reponse: Optional[str]                # rempli par l'Agent Chercheur
    statut_final: Optional[str]           # "repondu" ou "escalade"


# ------------------------------------------------------------------
# LES NOEUDS DU GRAPHE
# ------------------------------------------------------------------
# Un "noeud" est une fonction qui prend l'état actuel, fait un traitement,
# et retourne les champs qu'elle a modifiés/ajoutés.

def noeud_routeur(etat: EtatTicket) -> dict:
    """Appelle l'Agent Routeur et met à jour l'état avec sa décision."""
    resultat = router_ticket(etat["message"])
    return {
        "categorie": resultat["categorie"],
        "urgence": resultat["urgence"],
        "necessite_escalade": resultat["necessite_escalade_directe"],
    }


def noeud_chercheur(etat: EtatTicket) -> dict:
    """Appelle l'Agent Chercheur pour générer une réponse basée sur la doc."""
    reponse, _ = generer_reponse(etat["message"])
    return {
        "reponse": reponse,
        "statut_final": "repondu" if reponse != "INSUFFISANT" else "escalade",
    }


def noeud_escalade(etat: EtatTicket) -> dict:
    """Prépare le ticket pour un humain, sans générer de réponse automatique."""
    return {
        "reponse": None,
        "statut_final": "escalade",
    }


# ------------------------------------------------------------------
# LA LOGIQUE DE DÉCISION (le routage conditionnel)
# ------------------------------------------------------------------
def decider_apres_routeur(etat: EtatTicket) -> str:
    """
    Décide, après le passage du Routeur, où envoyer le ticket ensuite.
    C'est le nom du PROCHAIN noeud à exécuter qui est retourné ici.
    """
    if etat["necessite_escalade"]:
        return "escalade"
    return "chercheur"


# ------------------------------------------------------------------
# CONSTRUCTION DU GRAPHE
# ------------------------------------------------------------------
def construire_graphe():
    graphe = StateGraph(EtatTicket)

    # On déclare les noeuds (les "étapes" possibles)
    graphe.add_node("routeur", noeud_routeur)
    graphe.add_node("chercheur", noeud_chercheur)
    graphe.add_node("escalade", noeud_escalade)

    # Le point d'entrée : tout ticket commence toujours par le Routeur
    graphe.set_entry_point("routeur")

    # Le routage conditionnel : après le Routeur, on choisit dynamiquement
    # la prochaine étape en fonction du résultat (chercheur OU escalade)
    graphe.add_conditional_edges(
        "routeur",
        decider_apres_routeur,
        {
            "chercheur": "chercheur",
            "escalade": "escalade",
        },
    )

    # Une fois le Chercheur ou l'Escalade terminés, le graphe s'arrête (END)
    graphe.add_edge("chercheur", END)
    graphe.add_edge("escalade", END)

    return graphe.compile()


if __name__ == "__main__":
    app = construire_graphe()

    with open("data/tickets_test.json", "r", encoding="utf-8") as f:
        tickets = json.load(f)

    # On teste sur 6 tickets variés (questions simples ET plaintes)
    tickets_a_tester = [t for t in tickets if t["id"] in
                         ["T001", "T011", "T016", "T017", "T003"]]

    for ticket in tickets_a_tester:
        resultat = app.invoke({"message": ticket["message"]})

        print(f"\n{'='*60}")
        print(f"TICKET ({ticket['id']}) : {ticket['message']}")
        print(f"{'-'*60}")
        print(f"Catégorie   : {resultat['categorie']} (urgence: {resultat['urgence']})")
        print(f"Statut      : {resultat['statut_final']}")
        if resultat["statut_final"] == "repondu":
            print(f"Réponse     : {resultat['reponse']}")
        else:
            print(f"Réponse     : [Escaladé à un humain, pas de réponse automatique]")