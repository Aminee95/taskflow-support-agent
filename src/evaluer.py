"""
evaluer.py
Fait tourner le système complet (graphe.py) sur TOUS les tickets de test,
et calcule des métriques précises pour savoir objectivement si le système
est fiable. C'est ce script qui produit les chiffres à montrer en entretien.

Pour l'exécuter : python src/evaluer.py
"""

import json
from graphe import construire_graphe


def evaluer():
    app = construire_graphe()

    with open("data/tickets_test.json", "r", encoding="utf-8") as f:
        tickets = json.load(f)

    resultats_detailles = []

    for ticket in tickets:
        sortie = app.invoke({"message": ticket["message"], "tentatives": 0})

        # Comparaison 1 : la catégorie trouvée correspond-elle à l'attendue ?
        categorie_correcte = (sortie["categorie"] == ticket["categorie"])

        # Comparaison 2 : la décision d'escalade correspond-elle à l'attendue ?
        a_escalade = (sortie["statut_final"] == "escalade")
        escalade_correcte = (a_escalade == ticket["doit_escalader"])

        resultats_detailles.append({
            "id": ticket["id"],
            "categorie_attendue": ticket["categorie"],
            "categorie_trouvee": sortie["categorie"],
            "categorie_correcte": categorie_correcte,
            "doit_escalader_attendu": ticket["doit_escalader"],
            "a_escalade": a_escalade,
            "escalade_correcte": escalade_correcte,
            "tentatives": sortie["tentatives"],
            "statut_final": sortie["statut_final"],
        })

    return resultats_detailles


def calculer_metriques(resultats):
    total = len(resultats)

    nb_categorie_correcte = sum(1 for r in resultats if r["categorie_correcte"])
    nb_escalade_correcte = sum(1 for r in resultats if r["escalade_correcte"])
    nb_plusieurs_tentatives = sum(1 for r in resultats if r["tentatives"] > 1)

    return {
        "total_tickets": total,
        "precision_categorisation": round(nb_categorie_correcte / total * 100, 1),
        "precision_escalade": round(nb_escalade_correcte / total * 100, 1),
        "taux_reponse_du_premier_coup": round(
            (total - nb_plusieurs_tentatives) / total * 100, 1
        ),
    }


def afficher_rapport(resultats, metriques):
    print("\n" + "=" * 60)
    print("RAPPORT D'ÉVALUATION")
    print("=" * 60)

    print(f"\nTickets évalués : {metriques['total_tickets']}")
    print(f"Précision catégorisation : {metriques['precision_categorisation']}%")
    print(f"Précision décision d'escalade : {metriques['precision_escalade']}%")
    print(f"Taux de réponse correcte du 1er coup : {metriques['taux_reponse_du_premier_coup']}%")

    print("\n--- Détail des erreurs de catégorisation ---")
    erreurs_categorie = [r for r in resultats if not r["categorie_correcte"]]
    if not erreurs_categorie:
        print("Aucune erreur de catégorisation.")
    for r in erreurs_categorie:
        print(f"  {r['id']} : attendu '{r['categorie_attendue']}', "
              f"trouvé '{r['categorie_trouvee']}'")

    print("\n--- Détail des erreurs d'escalade ---")
    erreurs_escalade = [r for r in resultats if not r["escalade_correcte"]]
    if not erreurs_escalade:
        print("Aucune erreur de décision d'escalade.")
    for r in erreurs_escalade:
        print(f"  {r['id']} : attendu escalade={r['doit_escalader_attendu']}, "
              f"obtenu escalade={r['a_escalade']}")


if __name__ == "__main__":
    resultats = evaluer()
    metriques = calculer_metriques(resultats)
    afficher_rapport(resultats, metriques)

    # On sauvegarde aussi les résultats détaillés dans un fichier,
    # utile pour comparer avant/après une itération plus tard
    with open("data/resultats_evaluation.json", "w", encoding="utf-8") as f:
        json.dump(
            {"metriques": metriques, "details": resultats},
            f, indent=2, ensure_ascii=False
        )
    print("\nRésultats détaillés sauvegardés dans data/resultats_evaluation.json")