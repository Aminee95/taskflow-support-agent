"""
ingest.py
Ce script lit les documents de TaskFlow (dans le dossier data/),
les découpe en petits morceaux (chunks), et les stocke dans une base
de données vectorielle Chroma pour pouvoir les rechercher plus tard.

Pour l'exécuter : python ingest.py
"""

import os
from langchain_community.document_loaders import TextLoader, DirectoryLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from dotenv import load_dotenv

# Charge la clé API depuis le fichier .env
load_dotenv()

DATA_DIR = "data"
CHROMA_DIR = "chroma_db"


def load_documents():
    """Charge tous les fichiers .md du dossier data/"""
    loader = DirectoryLoader(
    DATA_DIR, 
    glob="*.md", 
    loader_cls=TextLoader,
    loader_kwargs={"encoding": "utf-8"}
)
    documents = loader.load()
    print(f"{len(documents)} document(s) chargé(s).")
    return documents


def split_documents(documents):
    """Découpe les documents en morceaux plus petits (chunks).

    Pourquoi découper ? Un LLM ne peut pas lire un document entier de 15
    pages à chaque question. On découpe en morceaux de ~500 caractères,
    avec un léger chevauchement (overlap) pour ne pas couper une idée
    en plein milieu.
    """
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=80,
        separators=["\n## ", "\n### ", "\n\n", "\n", " "],
    )
    chunks = splitter.split_documents(documents)
    print(f"{len(chunks)} chunk(s) créé(s) à partir des documents.")
    return chunks


def build_vectorstore(chunks):
    """Transforme chaque chunk en vecteur (embedding) et le stocke dans Chroma."""
    embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
    vectorstore = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=CHROMA_DIR,
    )
    print(f"Base vectorielle créée et sauvegardée dans '{CHROMA_DIR}/'.")
    return vectorstore


if __name__ == "__main__":
    docs = load_documents()
    chunks = split_documents(docs)
    build_vectorstore(chunks)
    print("\nIngestion terminée. Tu peux maintenant tester une recherche avec test_search.py")