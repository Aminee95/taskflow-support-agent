"""
test_search.py
Script simple pour vérifier que la base vectorielle fonctionne bien,
AVANT de construire les agents dessus. On pose une question, on regarde
si les morceaux de documents récupérés sont pertinents.

Pour l'exécuter : python test_search.py
"""

from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from dotenv import load_dotenv

load_dotenv()

CHROMA_DIR = "chroma_db"


def search(query, k=3):
    """Cherche les k morceaux de documents les plus pertinents pour une question."""
    embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
    vectorstore = Chroma(persist_directory=CHROMA_DIR, embedding_function=embeddings)

    results = vectorstore.similarity_search(query, k=k)

    print(f"\nQuestion : {query}")
    print("-" * 50)
    for i, doc in enumerate(results, 1):
        print(f"\nRésultat {i} :")
        print(doc.page_content[:300])
        print("...")


if __name__ == "__main__":
    # Quelques questions de test tirées de nos tickets
    test_questions = [
        "Comment inviter un collègue sur mon espace de travail ?",
        "Je n'ai pas reçu ma facture, que faire ?",
        "Puis-je être remboursé après mon paiement ?",
    ]

    for q in test_questions:
        search(q)