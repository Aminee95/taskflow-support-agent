"""
verifier_seuils.py
Lit les résultats de la dernière évaluation et vérifie qu'ils dépassent
des seuils minimums acceptables. Si un seuil n'est pas atteint, le script
se termine avec un code d'erreur -- ce qui fait échouer le pipeline CI
et alerte visuellement sur GitHub qu'une régression a été introduite.

Pour l'exécuter : python src/verifier_seuils.py
"""

import json
import sys

# Seuils minimums acceptables, basés sur les résultats obtenus en v4
# (voir tableau d'itérations dans le README). Si une modification future
# fait tomber les métriques sous ces seuils, le CI doit le signaler.
SEUILS_MINIMUMS = {
    "precision_categorisation": 85.0,
    "precision_escalade": 85.0,
    "taux_reponse_du_premier_coup": 65.0,
}


def verifier():
    with open("data/resultats_evaluation.json", "r", encoding="utf-8") as f:
        donnees = json.load(f)

    metriques = donnees["metriques"]
    echecs = []

    for cle, seuil in SEUILS_MINIMUMS.items():
        valeur = metriques.get(cle, 0)
        statut = "OK" if valeur >= seuil else "ÉCHEC"
        print(f"[{statut}] {cle} : {valeur}% (seuil minimum : {seuil}%)")

        if valeur < seuil:
            echecs.append(cle)

    if echecs:
        print(f"\n❌ {len(echecs)} métrique(s) sous le seuil minimum : {', '.join(echecs)}")
        sys.exit(1)  # code d'erreur -- fait échouer le pipeline CI
    else:
        print("\n✅ Toutes les métriques sont au-dessus des seuils minimums.")
        sys.exit(0)


if __name__ == "__main__":
    verifier()