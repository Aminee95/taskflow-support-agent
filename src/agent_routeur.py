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

# Version 5 du prompt : ajout de few-shot prompting pour corriger les cas
# limites persistants (T002, T005) qui résistaient depuis 4 itérations de
# règles en texte libre. Le principe : donner des exemples concrets plutôt
# que des règles abstraites, pour que le modèle raisonne par analogie sur
# le cas le plus proche.
PROMPT_TEMPLATE = """Tu es un agent qui catégorise les tickets de support client pour TaskFlow.

Catégories possibles : {categories}

Précisions sur les catégories :
- "facturation" couvre : les questions sur les plans/abonnements, les changements
  de plan (upgrade/downgrade), les remboursements, les factures, les paiements,
  ET les questions d'accès/permissions liées aux paramètres de facturation.
- "question_produit" couvre uniquement : comment utiliser une fonctionnalité
  existante de l'outil, hors plans et hors facturation.

Voici des exemples de tickets déjà correctement catégorisés, pour t'aider sur
les cas ambigus :

Exemple 1 :
Ticket : "Comment inviter un nouveau membre sur mon espace de travail ?"
Catégorie : question_produit (usage d'une fonctionnalité, aucun lien avec la facturation)

Exemple 2 :
Ticket : "Je suis Admin sur notre espace, pourquoi je ne vois pas les paramètres de facturation ?"
Catégorie : facturation (même si la question porte sur un rôle/permission, le
sujet concret est l'accès aux paramètres de FACTURATION -- pas l'usage général du produit)

Exemple 3 :
Ticket : "Je voudrais passer du plan Pro au plan Enterprise, comment faire ?"
Catégorie : facturation, necessite_escalade_directe=true (changement de plan vers
Enterprise, nécessite un commercial)

Exemple 4 :
Ticket : "Comment personnaliser les colonnes de mon tableau Kanban ?"
Catégorie : question_produit (usage d'une fonctionnalité, aucun lien avec la facturation)

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

Règles pour "necessite_escalade_directe" (uniquement ces cas précis) :
- true si c'est une plainte explicite, une menace de résiliation, ou une
  demande de passage au plan Enterprise (nécessite un commercial)
- false dans TOUS les autres cas, y compris les demandes de remboursement
  standard -- même si tu ne sais pas si la demande sera acceptée, la
  politique de remboursement est documentée et doit être vérifiée par
  recherche documentaire plutôt que d'être présupposée comme nécessitant
  un humain
- Ne présume jamais qu'une demande nécessite une action humaine simplement
  parce qu'elle implique de l'argent : laisse la vérification factuelle
  se faire via la documentation

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

    try:
        donnees = json.loads(resultat.content)
    except json.JSONDecodeError:
        donnees = {
            "categorie": "inconnue",
            "urgence": "haute",
            "necessite_escalade_directe": True,
            "justification": "Erreur de parsing JSON, escalade par sécurité",
        }

    return donnees


if __name__ == "__main__":
    with open("data/tickets_test.json", "r", encoding="utf-8") as f:
        tickets = json.load(f)

    # On teste spécifiquement sur les tickets qui posaient problème
    ids_cibles = ["T002", "T005", "T011", "T014"]
    tickets_cibles = [t for t in tickets if t["id"] in ids_cibles]

    for ticket in tickets_cibles:
        resultat = router_ticket(ticket["message"])
        print(f"\n{'='*60}")
        print(f"TICKET ({ticket['id']}) : {ticket['message']}")
        print(f"{'-'*60}")
        print(f"Catégorie attendue : {ticket['categorie']}")
        print(f"Catégorie trouvée  : {resultat['categorie']}")
        print(f"Urgence            : {resultat['urgence']}")
        print(f"Escalade directe   : {resultat['necessite_escalade_directe']}")
        print(f"Justification      : {resultat['justification']}")