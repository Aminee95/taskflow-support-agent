# TaskFlow Support Agent

[![Évaluation automatique](https://github.com/Aminee95/taskflow-support-agent/actions/workflows/evaluation.yml/badge.svg)](https://github.com/Aminee95/taskflow-support-agent/actions/workflows/evaluation.yml)

🔗 **[Voir la démo en ligne](https://taskflow-support-agent-gpqsr4zvpadheplzbvaavx.streamlit.app/)**

Système multi-agents (LangGraph) qui automatise le traitement des tickets de support client pour TaskFlow, un SaaS fictif de gestion de projet.

## Le problème

Automatiser la lecture, la catégorisation et la réponse aux tickets clients, tout en sachant reconnaître quand une réponse doit être escaladée à un humain plutôt que d'être générée à tort. La contrainte centrale du projet : **le système ne doit jamais inventer une réponse non fondée sur la documentation.**

## Architecture

```
Ticket client entrant
        │
        ▼
  [Agent Routeur] ── catégorise le ticket + évalue l'urgence
        │
        ├── Si plainte / cas sensible ──────────────► [Escalade humaine]
        │
        ▼
  [Agent Chercheur] ── recherche dans la doc (RAG) et rédige une réponse
        │
        ▼
  [Agent Vérificateur] ── vérifie que la réponse est fondée sur la doc
        │
        ├── Fondée ──────────────────────────────────► Réponse envoyée
        ├── Non fondée + tentatives restantes ────────► Retour au Chercheur (boucle)
        └── Non fondée + tentatives épuisées ─────────► [Escalade humaine]
```

Le mécanisme central : une **boucle de correction conditionnelle**. Si le Vérificateur juge une réponse non fondée, le système retente automatiquement (dans la limite de 2 tentatives) avant d'escalader à un humain plutôt que de risquer une hallucination.

## Stack technique

- Python, LangChain, LangGraph
- ChromaDB (base vectorielle, embeddings OpenAI `text-embedding-3-small`)
- OpenAI `gpt-4o-mini` (agents)
- Streamlit (interface, déployée sur Streamlit Community Cloud)
- LangSmith (observabilité)
- GitHub Actions (CI/CD)

## Installation

Cloner le dépôt et se placer dans le dossier du projet :

```bash
git clone https://github.com/Aminee95/taskflow-support-agent.git
cd taskflow-support-agent
```

Créer et activer un environnement virtuel Python :

```bash
python -m venv venv
venv\Scripts\activate
```

> Sous macOS/Linux : `source venv/bin/activate`

Installer les dépendances :

```bash
pip install -r requirements.txt
```

Configurer les variables d'environnement :

```bash
cp .env.example .env
```

Puis renseigner votre clé API OpenAI (et optionnellement LangSmith) dans le fichier `.env`.

## Utilisation

Construire la base de connaissances à partir de la documentation produit :

```bash
python src/ingest.py
```

Lancer le système complet sur quelques tickets d'exemple :

```bash
python src/graphe.py
```

Lancer l'évaluation chiffrée sur l'ensemble du jeu de test :

```bash
python src/evaluer.py
```

Diagnostiquer en détail le raisonnement de chaque agent sur des tickets précis :

```bash
python src/debug_tickets.py
```

Lancer les tests de robustesse contre les tentatives de manipulation :

```bash
python src/test_robustesse.py
```

Mesurer le coût et la latence réels :

```bash
python src/suivi_couts.py
```

Lancer l'interface web en local :

```bash
streamlit run src/app.py
```

## Résultats et itérations

Le système est évalué sur un jeu de 20 tickets annotés (catégorie et décision d'escalade attendues), couvrant 5 types de demandes : facturation, bug technique, question produit, plainte, demande de fonctionnalité.

| Itération | Changement apporté | Précision catégorisation | Précision escalade | Réponse dès le 1er coup |
|---|---|---|---|---|
| v1 | Prompt Routeur initial | 85% | 85% | 85% |
| v2 | Clarification catégorie facturation + découplage urgence/escalade | 95% | 85% | 75% |
| v3 | Routeur ne présume plus l'escalade sur simple remboursement ; Chercheur interdit d'extrapoler une cause à effet non écrite dans le contexte ; k=3→5 | 90% | 90% | 70% |
| v4 | Chunks élargis (500→800 caractères) ; correction d'une annotation de test elle-même incorrecte (T003) | 90% | 100% | 70% |
| v5 | Few-shot prompting sur l'Agent Routeur pour lever l'ambiguïté persistante entre "facturation" et "question_produit" | **100%** | **100%** | 75% |

**Ce que ces itérations montrent** :
- Une correction ciblée sur un cas précis peut faire reculer une autre métrique ailleurs (v1→v2) — un rappel qu'itérer sur un système multi-agents demande de mesurer l'ensemble des métriques, pas une seule isolément.
- Un bug de "hallucination" peut en réalité être un problème de retrieval (chunking trop agressif), pas un problème de prompt — diagnostiquer la bonne couche du système est essentiel avant de corriger.
- Une évaluation rigoureuse peut révéler une erreur dans les **données de test elles-mêmes** : le ticket T003 était annoté comme nécessitant une escalade humaine, alors que la documentation prévoit un remboursement automatique pour ce cas précis.
- Quand des règles en texte libre échouent de façon répétée sur un cas limite (T002/T005, 4 itérations sans succès), **changer de technique** plutôt que de continuer à ajuster les règles peut être plus efficace : le passage au few-shot prompting (donner des exemples concrets plutôt que des règles abstraites) a résolu le problème en une seule itération.

## Robustesse face aux tentatives de manipulation

Au-delà de l'évaluation fonctionnelle, le système est testé contre 5 scénarios de prompt injection (`src/test_robustesse.py`) : instructions cachées pour extorquer un faux remboursement, usurpation d'un rôle système, tentative d'extraction du prompt interne, contournement de l'escalade via une fausse consigne, et confirmation forcée d'une fonctionnalité inexistante.

**Résultat : 5/5 tentatives repoussées**, toutes escaladées à un humain plutôt que de céder à la manipulation. Ce résultat découle directement de la conception du Vérificateur : il ne juge jamais si une réponse "semble convaincante", uniquement si elle est prouvée par la documentation. Comme aucune attaque ne peut fabriquer une preuve documentaire inexistante, le garde-fou tient sans logique de détection d'attaque dédiée.

## Coût et latence

Mesurés sur un échantillon de 8 tickets (`src/suivi_couts.py`), via le callback de suivi de tokens de LangChain :

| Métrique | Valeur |
|---|---|
| Coût moyen par ticket | $0.00036 |
| Latence moyenne | 9.46s |
| Projection à 10 000 tickets/mois | **$3.65** |
| Projection à 100 000 tickets/mois | $36.50 |

**Le vrai facteur limitant n'est pas le coût, mais la latence.** Le coût est négligeable même à grande échelle. En revanche, la latence varie fortement selon le chemin emprunté dans le graphe : de 3s pour un ticket escaladé directement, jusqu'à 23s pour un ticket qui déclenche la boucle de correction. Pour une mise en production réelle, c'est ce paramètre qui dicterait les arbitrages produit.

## Intégration continue (CI/CD)

Un workflow GitHub Actions (`.github/workflows/evaluation.yml`) exécute automatiquement l'évaluation complète à chaque push sur `main` : reconstruction de la base de connaissances, exécution des 20 tickets de test, puis vérification que chaque métrique dépasse un seuil minimum défini (`src/verifier_seuils.py`). Si une modification fait chuter la fiabilité du système sous ces seuils, le pipeline échoue visiblement sur GitHub.

## Limites actuelles et pistes d'amélioration

- Jeu de test volontairement restreint (20 tickets) — un jeu plus large (40-50 tickets) rendrait les métriques statistiquement plus robustes
- Pas encore de gestion du contexte multi-tours (chaque ticket est traité indépendamment)
- Base de connaissance volontairement restreinte (documentation synthétique de ~2 pages)
- Sur le déploiement en ligne, la base vectorielle est reconstruite à chaque redémarrage du serveur (pas de persistance entre sessions sur l'hébergement gratuit)
- Retrieval purement vectoriel (pas de recherche hybride mots-clés + sémantique, ni de reranking)

## État du projet

✅ Projet complet — pipeline RAG, système multi-agents avec boucle de correction, évaluation chiffrée sur 5 itérations (100% de précision), tests de robustesse, suivi coût/latence, CI/CD, interface déployée en ligne.