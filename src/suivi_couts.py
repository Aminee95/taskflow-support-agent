"""
suivi_couts.py
Calcule le coût et la latence réels du traitement d'un ticket, en captant
les tokens consommés par chaque appel LLM via le callback LangChain
`get_openai_callback`. Utile pour estimer le coût à l'échelle
(ex: "combien coûterait 10 000 tickets/mois ?").

Pour l'exécuter : python src/suivi_couts.py
"""

import json
import time
from langchain_community.callbacks import get_openai_callback
from graphe import construire_graphe


def traiter_avec_suivi(app, message):
    """Traite un ticket en mesurant précisément le temps et le coût."""
    debut = time.time()

    with get_openai_callback() as cb:
        resultat = app.invoke({"message": message, "tentatives": 0})

    duree = time.time() - debut

    return resultat, {
        "duree_secondes": round(duree, 2),
        "tokens_entree": cb.prompt_tokens,
        "tokens_sortie": cb.completion_tokens,
        "tokens_total": cb.total_tokens,
        "cout_usd": round(cb.total_cost, 5),
    }


if __name__ == "__main__":
    app = construire_graphe()

    with open("data/tickets_test.json", "r", encoding="utf-8") as f:
        tickets = json.load(f)

    # On teste sur 8 tickets variés pour avoir un échantillon représentatif
    echantillon = tickets[:8]

    couts_totaux = []
    durees_totales = []

    print("\n" + "=" * 70)
    print("SUIVI DES COÛTS ET LATENCES")
    print("=" * 70)

    for ticket in echantillon:
        resultat, metriques = traiter_avec_suivi(app, ticket["message"])

        couts_totaux.append(metriques["cout_usd"])
        durees_totales.append(metriques["duree_secondes"])

        print(f"\n{ticket['id']} : {ticket['message'][:60]}...")
        print(f"  Statut       : {resultat['statut_final']}")
        print(f"  Durée        : {metriques['duree_secondes']}s")
        print(f"  Tokens       : {metriques['tokens_total']} "
              f"(entrée: {metriques['tokens_entree']}, sortie: {metriques['tokens_sortie']})")
        print(f"  Coût         : ${metriques['cout_usd']}")

    # --- Synthèse et projection à l'échelle ---
    cout_moyen = sum(couts_totaux) / len(couts_totaux)
    duree_moyenne = sum(durees_totales) / len(durees_totales)

    print("\n" + "=" * 70)
    print("SYNTHÈSE")
    print("=" * 70)
    print(f"Coût moyen par ticket   : ${cout_moyen:.5f}")
    print(f"Latence moyenne         : {duree_moyenne:.2f}s")
    print(f"\nProjection à l'échelle :")
    print(f"  1 000 tickets/mois    : ${cout_moyen * 1000:.2f}")
    print(f"  10 000 tickets/mois   : ${cout_moyen * 10000:.2f}")
    print(f"  100 000 tickets/mois  : ${cout_moyen * 100000:.2f}")