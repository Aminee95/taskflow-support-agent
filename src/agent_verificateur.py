"""
agent_verificateur.py
L'agent le plus important du système : il relit une réponse générée par
l'Agent Chercheur et vérifie qu'elle est bien fondée sur le contexte
documentaire fourni, sans invention. C'est le garde-fou anti-hallucination.

Pour l'exécuter : python src/agent_verificateur.py
"""

import json
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from dotenv import load_dotenv

load_dotenv()

PROMPT_TEMPLATE = """Tu es un contrôleur qualité pour un service de support client.

On te donne un CONTEXTE (extrait de documentation) et une RÉPONSE générée
pour un client. Ton unique tâche : vérifier si CHAQUE affirmation de la
réponse est bien soutenue par le contexte, sans rien inventer d'ajouté.

Réponds UNIQUEMENT avec un objet JSON valide, sans texte avant ou après :
{{
  "fondee": true | false,
  "raison": "une phrase courte expliquant le verdict",
  "affirmations_non_fondees": ["liste des affirmations problématiques, vide si aucune"]
}}

CONTEXTE :
{contexte}

RÉPONSE À VÉRIFIER :
{reponse}
"""


def verifier_reponse(reponse, contexte):
    """Vérifie si une réponse est fondée sur le contexte fourni.

    Retourne un dict avec 'fondee' (bool), 'raison', et
    'affirmations_non_fondees' (liste).
    """
    prompt = ChatPromptTemplate.from_template(PROMPT_TEMPLATE)
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

    chaine = prompt | llm

    resultat = chaine.invoke({"contexte": contexte, "reponse": reponse})

    try:
        donnees = json.loads(resultat.content)
    except json.JSONDecodeError:
        # Filet de sécurité : en cas de doute, on considère la réponse
        # comme NON fondée -- mieux vaut re-vérifier que laisser passer
        # une hallucination potentielle.
        donnees = {
            "fondee": False,
            "raison": "Erreur de parsing JSON du vérificateur, rejet par précaution",
            "affirmations_non_fondees": [],
        }

    return donnees


if __name__ == "__main__":
    # Test 1 : une réponse correcte, bien fondée sur le contexte
    contexte_test = """## 4. Remboursements
- Les remboursements ne sont possibles que dans les 14 jours suivant un paiement, sur demande écrite.
- Passé ce délai, aucun remboursement n'est possible."""

    reponse_correcte = "Vous pouvez être remboursé si votre demande est faite dans les 14 jours suivant le paiement."

    reponse_hallucinee = "Vous pouvez être remboursé à tout moment, et nous offrons même un geste commercial de 10% en plus."

    print("=== TEST 1 : réponse correcte ===")
    resultat1 = verifier_reponse(reponse_correcte, contexte_test)
    print(json.dumps(resultat1, indent=2, ensure_ascii=False))

    print("\n=== TEST 2 : réponse avec hallucination (info inventée) ===")
    resultat2 = verifier_reponse(reponse_hallucinee, contexte_test)
    print(json.dumps(resultat2, indent=2, ensure_ascii=False))