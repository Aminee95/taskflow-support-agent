"""
debug_tickets.py
Script de diagnostic : affiche le détail complet (justification du Routeur,
réponse du Chercheur, verdict du Vérificateur) pour des tickets précis.
Sert à comprendre POURQUOI un ticket est mal traité, pas juste QUE c'est le cas.

Pour l'exécuter : python src/debug_tickets.py
"""

import json
from agent_routeur import router_ticket
from agent_chercheur import generer_reponse
from agent_verificateur import verifier_reponse

# Les tickets qui posent problème après la v2 du Routeur
IDS_A_DIAGNOSTIQUER = ["T004", "T010", "T015"]


def diagnostiquer(ticket):
    print(f"\n{'='*70}")
    print(f"TICKET {ticket['id']} : {ticket['message']}")
    print(f"{'='*70}")

    # Étape 1 : le Routeur
    routage = router_ticket(ticket["message"])
    print(f"\n[ROUTEUR]")
    print(f"  Catégorie      : {routage['categorie']} (attendu: {ticket['categorie']})")
    print(f"  Urgence        : {routage['urgence']}")
    print(f"  Escalade dir.  : {routage['necessite_escalade_directe']} (attendu doit_escalader: {ticket['doit_escalader']})")
    print(f"  Justification  : {routage['justification']}")

    if routage["necessite_escalade_directe"]:
        print("\n-> Le Routeur a escaladé directement, le Chercheur n'est jamais appelé.")
        return

    # Étape 2 : le Chercheur (uniquement si le Routeur ne l'a pas déjà escaladé)
    reponse, contexte = generer_reponse(ticket["message"])
    print(f"\n[CHERCHEUR]")
    print(f"  Réponse générée : {reponse}")

    if reponse == "INSUFFISANT":
        print("\n-> Le Chercheur juge lui-même ne pas avoir assez de contexte.")
        return

    # Étape 3 : le Vérificateur
    verification = verifier_reponse(reponse, contexte)
    print(f"\n[VÉRIFICATEUR]")
    print(f"  Fondée         : {verification['fondee']}")
    print(f"  Raison         : {verification['raison']}")
    if verification["affirmations_non_fondees"]:
        print(f"  Affirmations non fondées : {verification['affirmations_non_fondees']}")

    print(f"\n[CONTEXTE UTILISÉ PAR LE CHERCHEUR]")
    print(f"  {contexte[:400]}...")


if __name__ == "__main__":
    with open("data/tickets_test.json", "r", encoding="utf-8") as f:
        tickets = json.load(f)

    tickets_cibles = [t for t in tickets if t["id"] in IDS_A_DIAGNOSTIQUER]

    for ticket in tickets_cibles:
        diagnostiquer(ticket)