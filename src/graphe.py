"""
graphe.py
Le coeur du système multi-agents, version 2 : Routeur -> Chercheur ->
Vérificateur, avec une boucle de correction si la réponse n'est pas
fondée sur la documentation. C'est le mécanisme le plus différenciant
du projet : le système se corrige tout seul avant de répondre au client.

Pour l'exécuter : python src/graphe.py
"""

import json
from typing import TypedDict, Optional
from langgraph.graph import StateGraph, END
from dotenv import load_dotenv

from agent_routeur import router_ticket
from agent_chercheur import generer_reponse
from agent_verificateur import verifier_reponse

load_dotenv()

NOMBRE_MAX_TENTATIVES = 2  # évite une boucle infinie si le Vérificateur
                            # rejette systématiquement


class EtatTicket(TypedDict):
    message: str
    categorie: Optional[str]
    urgence: Optional[str]
    necessite_escalade: Optional[bool]
    reponse: Optional[str]
    contexte: Optional[str]
    fondee: Optional[bool]
    tentatives: int                   # compteur de boucles Chercheur<->Vérificateur
    statut_final: Optional[str]


def noeud_routeur(etat: EtatTicket) -> dict:
    resultat = router_ticket(etat["message"])
    return {
        "categorie": resultat["categorie"],
        "urgence": resultat["urgence"],
        "necessite_escalade": resultat["necessite_escalade_directe"],
    }


def noeud_chercheur(etat: EtatTicket) -> dict:
    """Génère une réponse. On garde aussi le contexte utilisé, car le
    Vérificateur en a besoin juste après pour faire son contrôle."""
    reponse, contexte = generer_reponse(etat["message"])
    tentatives_actuelles = etat.get("tentatives", 0)
    return {
        "reponse": reponse,
        "contexte": contexte,
        "tentatives": tentatives_actuelles + 1,
    }


def noeud_verificateur(etat: EtatTicket) -> dict:
    """Vérifie que la réponse est fondée. Si le Chercheur a déjà répondu
    INSUFFISANT, pas besoin de vérifier -- on escalade direct."""
    if etat["reponse"] == "INSUFFISANT":
        return {"fondee": False}

    resultat = verifier_reponse(etat["reponse"], etat["contexte"])
    return {"fondee": resultat["fondee"]}


def noeud_escalade(etat: EtatTicket) -> dict:
    return {
        "reponse": None,
        "statut_final": "escalade",
    }


def noeud_validation_finale(etat: EtatTicket) -> dict:
    """La réponse a passé le contrôle du Vérificateur, elle est prête à partir."""
    return {"statut_final": "repondu"}


# ------------------------------------------------------------------
# LOGIQUE DE DÉCISION
# ------------------------------------------------------------------
def decider_apres_routeur(etat: EtatTicket) -> str:
    if etat["necessite_escalade"]:
        return "escalade"
    return "chercheur"


def decider_apres_verificateur(etat: EtatTicket) -> str:
    """
    Le coeur de la boucle de correction :
    - Si la réponse est fondée -> on valide et on termine
    - Si elle n'est PAS fondée ET qu'il reste des tentatives -> on relance le Chercheur
    - Si elle n'est PAS fondée ET qu'on a épuisé les tentatives -> on escalade à un humain
    """
    if etat["fondee"]:
        return "valide"
    if etat["tentatives"] < NOMBRE_MAX_TENTATIVES:
        return "reessayer"
    return "escalade"


def construire_graphe():
    graphe = StateGraph(EtatTicket)

    graphe.add_node("routeur", noeud_routeur)
    graphe.add_node("chercheur", noeud_chercheur)
    graphe.add_node("verificateur", noeud_verificateur)
    graphe.add_node("escalade", noeud_escalade)
    graphe.add_node("validation_finale", noeud_validation_finale)

    graphe.set_entry_point("routeur")

    graphe.add_conditional_edges(
        "routeur",
        decider_apres_routeur,
        {"chercheur": "chercheur", "escalade": "escalade"},
    )

    # Après le Chercheur, on passe TOUJOURS par le Vérificateur
    graphe.add_edge("chercheur", "verificateur")

    # Après le Vérificateur : 3 chemins possibles
    graphe.add_conditional_edges(
        "verificateur",
        decider_apres_verificateur,
        {
            "valide": "validation_finale",
            "reessayer": "chercheur",   # <-- LA BOUCLE : retour vers le Chercheur
            "escalade": "escalade",
        },
    )

    graphe.add_edge("validation_finale", END)
    graphe.add_edge("escalade", END)

    return graphe.compile()


if __name__ == "__main__":
    app = construire_graphe()

    with open("data/tickets_test.json", "r", encoding="utf-8") as f:
        tickets = json.load(f)

    tickets_a_tester = [t for t in tickets if t["id"] in
                         ["T001", "T011", "T016", "T017", "T003"]]

    for ticket in tickets_a_tester:
        resultat = app.invoke({"message": ticket["message"], "tentatives": 0})

        print(f"\n{'='*60}")
        print(f"TICKET ({ticket['id']}) : {ticket['message']}")
        print(f"{'-'*60}")
        print(f"Catégorie   : {resultat['categorie']} (urgence: {resultat['urgence']})")
        print(f"Tentatives  : {resultat['tentatives']}")
        print(f"Statut      : {resultat['statut_final']}")
        if resultat["statut_final"] == "repondu":
            print(f"Réponse     : {resultat['reponse']}")
        else:
            print(f"Réponse     : [Escaladé à un humain, pas de réponse automatique]")