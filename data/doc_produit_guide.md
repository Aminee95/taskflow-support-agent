# TaskFlow — Documentation produit

## 1. Présentation générale

TaskFlow est un outil de gestion de projet en ligne pour les équipes. Il permet de créer des projets, organiser des tâches en tableaux Kanban, assigner des responsables, suivre les échéances et collaborer en temps réel.

## 2. Créer un compte et démarrer

1. Rendez-vous sur app.taskflow.io/signup
2. Renseignez votre email professionnel et créez un mot de passe
3. Créez votre premier espace de travail (workspace) — c'est le conteneur qui regroupe tous vos projets d'équipe
4. Invitez des collègues via leur adresse email depuis Paramètres > Membres

## 3. Gérer les projets

- Un **projet** contient un ou plusieurs tableaux (boards)
- Un **tableau** est organisé en colonnes (ex: À faire, En cours, Terminé) que vous pouvez personnaliser
- Une **tâche** peut être déplacée entre colonnes par glisser-déposer
- Chaque tâche peut avoir : un responsable, une date d'échéance, des étiquettes (labels), des pièces jointes, des commentaires

## 4. Rôles et permissions

- **Propriétaire (Owner)** : accès complet, gère la facturation, peut supprimer l'espace de travail
- **Administrateur (Admin)** : gère les membres et les projets, pas accès à la facturation
- **Membre** : peut créer/éditer des tâches sur les projets auxquels il a accès
- **Invité (Guest)** : accès en lecture seule ou limité à un projet spécifique

## 5. Intégrations disponibles

- **Slack** : recevez des notifications de tâches directement dans un canal Slack. Configuration depuis Paramètres > Intégrations > Slack, puis autoriser l'accès.
- **Google Calendar** : synchronisez les échéances de vos tâches avec votre calendrier. Configuration depuis Paramètres > Intégrations > Google Calendar.
- **Zapier** : disponible uniquement sur le plan Enterprise, permet de connecter TaskFlow à plus de 3000 autres applications.

## 6. Notifications

Les notifications peuvent être reçues par email, dans l'application, ou via Slack si l'intégration est activée. Configurables individuellement depuis Paramètres > Notifications : à chaque assignation de tâche, à chaque commentaire, 24h avant une échéance.

## 7. Problèmes fréquents et solutions

- **Une tâche n'apparaît pas dans le tableau** : vérifiez les filtres actifs (en haut du tableau), ils peuvent masquer certaines tâches
- **Impossible d'inviter un membre** : vérifiez que vous n'avez pas atteint la limite de membres de votre plan (voir section Facturation)
- **La synchronisation Google Calendar ne fonctionne pas** : reconnectez l'intégration depuis Paramètres > Intégrations, les tokens d'autorisation expirent après 90 jours
- **L'application est lente** : généralement lié à un tableau contenant plus de 500 tâches actives ; nous recommandons d'archiver les tâches terminées