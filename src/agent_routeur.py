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
PROMPT_TEMPLATE = """Tu es un agent qui catégorise les tickets de support client pour TaskFlow.

Catégories possibles : {categories}

Analyse le ticket suivant et réponds UNIQUEMENT avec un objet JSON valide,
sans aucun texte avant ou après, au format exact suivant :
{{
  "categorie": "une des catégories listées ci-dessus",
  "urgence": "basse" | "moyenne" | "haute",
  "necessite_escalade_directe": true | false,
  "justification": "une phrase courte expliquant ce choix"
}}

Règles pour "necessite_escalade_directe" :
- true si c'est une plainte, une menace de résiliation, ou un problème visiblement complexe/sensible
- false si c'est une question standard qui peut être répondue via la documentation

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