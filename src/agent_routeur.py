"""
agent_routeur.py
Le premier agent du système, dans l'ordre du graphe : il lit un ticket
client brut et détermine sa catégorie + son niveau d'urgence, AVANT toute
recherche dans la documentation.

Pour l'exécuter : python src/agent_routeur.py
"""

import json
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from dotenv import load_dotenv

load_dotenv()

CATEGORIES = [
    "facturation",
    "bug_technique",
    "question_produit",
    "plainte",
    "demande_fonctionnalite",
]

# On demande une sortie strictement en JSON pour pouvoir l'utiliser
# facilement dans le code ensuite (au lieu de devoir "parser" du texte libre).
#
# Version 2 du prompt (itération après évaluation v1 à 85%) :
# - Précision ajoutée sur "facturation" pour inclure les changements de plan
# - "urgence" et "necessite_escalade_directe" sont maintenant clairement
#   DÉCOUPLÉS : un ticket peut être urgent ET avoir une réponse simple dans
#   la doc (ex: "l'appli est trop lente" -> urgence haute mais pas d'escalade,
#   car la doc a la solution).
PROMPT_TEMPLATE = """Tu es un agent qui catégorise les tickets de support client pour TaskFlow.

Catégories possibles : {categories}

Précisions sur les catégories :
- "facturation" couvre : les questions sur les plans/abonnements, les changements
  de plan (upgrade/downgrade), les remboursements, les factures, les paiements.
- "question_produit" couvre uniquement : comment utiliser une fonctionnalité
  existante de l'outil (pas les plans ou la facturation).

Analyse le ticket suivant et réponds UNIQUEMENT avec un objet JSON valide,
sans aucun texte avant ou après, au format exact suivant :
{{
  "categorie": "une des catégories listées ci-dessus",
  "urgence": "basse" | "moyenne" | "haute",
  "necessite_escalade_directe": true | false,
  "justification": "une phrase courte expliquant ce choix"
}}

IMPORTANT : "urgence" et "necessite_escalade_directe" sont deux choses
DIFFÉRENTES. Un ticket peut être urgent tout en ayant une réponse simple
dans la documentation (dans ce cas, urgence="haute" mais escalade=false).

Règles pour "necessite_escalade_directe" (uniquement ces cas) :
- true si c'est une plainte, une menace de résiliation, une demande de
  changement vers le plan Enterprise (nécessite un commercial), ou un
  problème dont la résolution nécessite clairement une action humaine
  (ex: erreur de facturation à corriger manuellement)
- false pour toute question standard, même urgente ou frustrée, dès lors
  qu'une réponse factuelle peut raisonnablement exister dans une
  documentation produit

Règles pour "urgence" :
- "haute" si le client exprime une forte frustration, un blocage total,
  ou un impact financier
- "moyenne" ou "basse" sinon

Ticket client :
{ticket}
"""


def router_ticket(texte_ticket):
    """Analyse un ticket et retourne sa catégorie, son urgence, et s'il faut l'escalader."""
    prompt = ChatPromptTemplate.from_template(PROMPT_TEMPLATE)
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

    chaine = prompt | llm

    resultat = chaine.invoke({
        "categories": ", ".join(CATEGORIES),
        "ticket": texte_ticket,
    })

    # Le LLM renvoie du texte -- on le transforme en objet Python (dict)
    try:
        donnees = json.loads(resultat.content)
    except json.JSONDecodeError:
        # Filet de sécurité : si jamais le LLM ne renvoie pas un JSON propre,
        # on ne plante pas le programme, on renvoie une erreur explicite.
        donnees = {
            "categorie": "inconnue",
            "urgence": "haute",
            "necessite_escalade_directe": True,
            "justification": "Erreur de parsing JSON, escalade par sécurité",
        }

    return donnees


if __name__ == "__main__":
    # On teste sur quelques tickets de notre jeu de données
    with open("data/tickets_test.json", "r", encoding="utf-8") as f:
        tickets = json.load(f)

    # On teste sur les 6 premiers pour l'instant
    for ticket in tickets[:6]:
        resultat = router_ticket(ticket["message"])
        print(f"\n{'='*60}")
        print(f"TICKET ({ticket['id']}) : {ticket['message']}")
        print(f"{'-'*60}")
        print(f"Catégorie attendue : {ticket['categorie']}")
        print(f"Catégorie trouvée  : {resultat['categorie']}")
        print(f"Urgence            : {resultat['urgence']}")
        print(f"Escalade directe   : {resultat['necessite_escalade_directe']}")
        print(f"Justification      : {resultat['justification']}")