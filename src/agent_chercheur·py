"""
agent_chercheur.py
Le premier agent du système : il prend une question client, cherche les
passages pertinents dans la documentation TaskFlow, et génère une réponse
en langage naturel basée UNIQUEMENT sur ces passages.

Pour l'exécuter : python src/agent_chercheur.py
"""

from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_community.vectorstores import Chroma
from langchain.prompts import ChatPromptTemplate
from dotenv import load_dotenv

load_dotenv()

CHROMA_DIR = "chroma_db"

# Le prompt : les instructions données au LLM.
# Le point le plus important : on lui interdit explicitement d'inventer
# une réponse qui ne serait pas dans le contexte fourni.
PROMPT_TEMPLATE = """Tu es un assistant support client pour TaskFlow, un outil de gestion de projet.

Réponds à la question du client UNIQUEMENT à partir du contexte ci-dessous.
Si le contexte ne contient pas assez d'information pour répondre avec certitude,
réponds exactement : "INSUFFISANT" (rien d'autre).

Ne jamais inventer d'information qui n'est pas dans le contexte.

Contexte :
{contexte}

Question du client :
{question}

Réponse (claire, professionnelle, en français) :"""


def rechercher_contexte(question, k=3):
    """Récupère les k passages de documentation les plus pertinents."""
    embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
    vectorstore = Chroma(persist_directory=CHROMA_DIR, embedding_function=embeddings)
    resultats = vectorstore.similarity_search(question, k=k)
    # On concatène les passages trouvés en un seul bloc de texte
    contexte = "\n\n---\n\n".join([doc.page_content for doc in resultats])
    return contexte


def generer_reponse(question):
    """Pipeline complet : recherche + génération de la réponse."""
    contexte = rechercher_contexte(question)

    prompt = ChatPromptTemplate.from_template(PROMPT_TEMPLATE)
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

    chaine = prompt | llm

    resultat = chaine.invoke({"contexte": contexte, "question": question})

    return resultat.content, contexte


if __name__ == "__main__":
    questions_test = [
        "Comment inviter un collègue sur mon espace de travail ?",
        "Je n'ai pas reçu ma facture, que faire ?",
        "Puis-je être remboursé après mon paiement ?",
        "Quelle est la couleur du logo de TaskFlow ?",  # question piège, hors contexte
    ]

    for q in questions_test:
        reponse, contexte = generer_reponse(q)
        print(f"\n{'='*60}")
        print(f"QUESTION : {q}")
        print(f"{'-'*60}")
        print(f"RÉPONSE : {reponse}")