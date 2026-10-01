# Séance 5 : Révision du projet et développement des premières fonctionnalités

## Informations sur la séance

- **Date :** 23 septembre 2026
- **Horaire :** 10 h 00 - 13 h 15
- **Lieu :** C206
- **Présents :** Adel, Rabah et Loïc Roque

## Objectifs de la séance

Cette séance avait pour objectif de présenter l’avancement du projet à Loïc Roque, de revoir certaines pratiques liées à Git et de poursuivre le développement des premières fonctionnalités.

## Cours sur Git

Au début de la séance, Loïc Roque a fait un cours sur Git afin de présenter les bonnes pratiques à utiliser dans un projet réalisé en groupe.

Il a notamment expliqué le fonctionnement des branches, des commits, des Pull Requests et de la fusion des modifications dans la branche principale.

## Validation du projet

Adel et Rabah ont présenté le projet Épicer’INT, le cahier des charges et les fonctionnalités présentes dans le GitHub Project.

Loïc Roque a confirmé la cohérence générale du projet et des fonctionnalités choisies. Il leur a également donné plusieurs conseils concernant l’organisation du modèle de données.

## Modification de la gestion des catégories

Au départ, la catégorie d’un produit était enregistrée comme un simple attribut de l’entité `Product`.

Après discussion avec Loïc Roque, il a été décidé de créer une entité `Category` séparée. Cette organisation permettra de gérer plus facilement les catégories et d’en ajouter de nouvelles sans modifier directement le code de l’entité `Product`.

Une catégorie pourra contenir plusieurs produits et chaque produit sera associé à une catégorie.

Le MCD et les modèles Django devront être adaptés pour prendre en compte cette nouvelle relation.

## Mise en place de l’authentification

Rabah a poursuivi le développement de l’authentification.

Une page de connexion ainsi que les routes permettant de se connecter et de se déconnecter ont été ajoutées. L’inscription et la page de profil viendront ensuite compléter cette première version.

L’authentification sera nécessaire pour associer les commandes et les notifications au bon utilisateur.

## Début de la page des commandes

Adel a commencé à travailler sur la page consacrée aux commandes.

La première étape consiste à créer une page simple, accessible depuis le menu du site. Les fonctionnalités permettant de consulter les anciennes commandes, de passer une nouvelle commande et de payer seront ajoutées progressivement dans différentes sous-issues.

Adel a également travaillé sur le MCD afin de représenter les utilisateurs, les produits, les catégories, les commandes, les paiements, les distributions et les notifications.

## Prochaines étapes

Les prochaines étapes seront :

- ajouter l’entité `Category` dans les modèles Django ;
- adapter l’entité `Product` ;
- poursuivre l’inscription et la page de profil ;
- continuer la création de la page des commandes ;
- ajouter le MCD au dépôt ;
- appliquer les conseils donnés sur l’utilisation de Git.
