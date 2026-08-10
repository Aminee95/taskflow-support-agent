# TaskFlow Support Agent

Système multi-agents (LangGraph) qui automatise le traitement des tickets de support client pour TaskFlow, un SaaS fictif de gestion de projet.

## Le problème

Automatiser la lecture, la catégorisation et la réponse aux tickets clients, tout en sachant reconnaître quand une réponse doit être escaladée à un humain plutôt que d'être générée à tort.

## Architecture

*(schéma et détails à venir au fur et à mesure de la construction des agents)*

- Agent Routeur : catégorise le ticket et évalue l'urgence
- Agent Chercheur (RAG) : recherche dans la documentation produit
- Agent Rédacteur : formule la réponse client
- Agent Vérificateur : vérifie que la réponse est fondée sur les sources
- Agent Escalade : prépare un résumé pour un humain si nécessaire

## Stack technique

- Python, LangChain, LangGraph
- ChromaDB (base vectorielle)
- OpenAI (embeddings + LLM)

## Installation

Cloner le dépôt et se placer dans le dossier du projet :

\`\`\`bash

git clone https://github.com/ton-utilisateur/taskflow-support-agent.git

cd taskflow-support-agent

\`\`\`

Créer et activer un environnement virtuel Python :

\`\`\`bash
python -m venv venv
venv\Scripts\activate
\`\`\`

> Sous macOS/Linux : `source venv/bin/activate`

Installer les dépendances :

\`\`\`bash
pip install -r requirements.txt
\`\`\`

Configurer les variables d'environnement :

\`\`\`bash
cp .env.example .env
\`\`\`

Puis renseigner votre clé API OpenAI dans le fichier `.env`.

## Utilisation

Construire la base de connaissances à partir de la documentation produit :

\`\`\`bash
python src/ingest.py
\`\`\`

Tester la recherche sémantique sur la base de connaissances :

\`\`\`bash
python src/test_search.py
\`\`\`
## État du projet

🚧 En cours de développement — Semaine 1/4 : pipeline RAG de base fonctionnel.

## Résultats et métriques

*(à venir en semaine 3-4, avec les scores d'évaluation avant/après itérations)*
