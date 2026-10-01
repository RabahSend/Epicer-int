# Séance 5 : Développement des premières fonctionnalités

## Informations sur la séance

- **Date :** 23 septembre 2026
- **Horaire :** 10 h 00 - 13 h 15
- **Lieu :** C206
- **Présents :** Adel et Rabah

## Objectifs de la séance

Cette séance avait pour objectif de poursuivre le développement des premières issues, de commencer l’authentification sur le site et de préparer la partie consacrée aux commandes.

## Avancement des issues

Adel et Rabah ont poursuivi le travail sur les issues placées dans le statut `In progress`.

Les modifications ont été réalisées progressivement sur des branches dédiées afin de pouvoir les vérifier avant leur intégration dans la branche principale.

## Mise en place de l’authentification

Rabah a commencé à mettre en place l’authentification sur l’application web.

Une page de connexion ainsi que les routes permettant de se connecter et de se déconnecter ont été ajoutées. Le menu du site a également été adapté afin d’afficher les liens correspondant à l’état de connexion de l’utilisateur.

Cette fonctionnalité sera nécessaire pour associer les commandes et les notifications au bon utilisateur.

L’inscription et la page de profil devront ensuite compléter cette première version de l’authentification.

## Début de la page des commandes

Adel a commencé à préparer la page consacrée aux commandes.

Cette première version reste volontairement simple. Elle doit permettre d’afficher un titre, un premier contenu visuel et un lien accessible depuis le menu principal.

Les fonctionnalités permettant de consulter les anciennes commandes, de passer une nouvelle commande et de payer seront ajoutées progressivement dans de prochaines sous-issues.

## Travail sur le modèle de données

Adel a également préparé le MCD du projet afin de représenter les principales entités et leurs relations.

Ce modèle comprend notamment les utilisateurs, les produits, les commandes, les lignes de commande, les paiements, les distributions et les notifications.

Le MCD sera ajouté au dépôt afin de conserver une représentation claire de la base de données.

## Coordination du travail

Adel et Rabah ont échangé sur leurs modifications afin de vérifier la compatibilité entre l’authentification et la future gestion des commandes.

Cette coordination est nécessaire, car une commande doit être associée à l’utilisateur connecté.

## Prochaines étapes

Les prochaines étapes seront :

- terminer l’inscription et la page de profil ;
- poursuivre la création de la page des commandes ;
- ajouter le MCD au dépôt ;
- revoir la gestion des catégories de produits ;
- continuer à utiliser une branche et une Pull Request pour chaque issue.
