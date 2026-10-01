# Séance 3 : Organisation du projet et mise en place de la CI/CD

## Informations sur la séance

- **Date :** 16 septembre 2026
- **Horaire :** 14 h 30 – 17 h 45
- **Lieu :** E’0022
- **Présents :** Adel et Rabah

## Objectifs de la séance

Cette séance avait pour objectif de structurer le développement du projet Épicer’INT, d’organiser les fonctionnalités à réaliser et de mettre en place les premiers éléments techniques.

## Mise en place du projet

L’architecture initiale de l’application Django a été ajoutée au dépôt. Une première Pull Request a permis d’intégrer cette architecture dans la branche principale.

Cette base contient les premiers fichiers de configuration du projet ainsi que l’application consacrée aux utilisateurs.

## Organisation du GitHub Project

Adel et Rabah ont mis en place un GitHub Project afin de centraliser et de suivre les différentes tâches.

Les principales fonctionnalités du cahier des charges ont été créées sous forme d’issues :

- gestion des utilisateurs et authentification ;
- gestion des produits et des stocks ;
- gestion des commandes et des paiements ;
- gestion des distributions et de la récupération des commandes ;
- système de notifications ;
- tableau de bord administrateur et statistiques.

Les issues ont été organisées dans le backlog. Différents statuts ont été utilisés pour suivre leur avancement : `Backlog`, `Ready`, `In progress`, `In review` et `Done`.

Des itérations ont également été configurées afin de répartir les tâches sur les différentes périodes de développement.

## Estimation et répartition du travail

Une première estimation du temps nécessaire à chaque issue a été effectuée afin d’évaluer la charge de travail.

Les tâches ont ensuite été réparties entre Adel et Rabah. Cette répartition pourra évoluer en fonction de l’avancement, des dépendances entre les fonctionnalités et des difficultés rencontrées.

## Mise en place de la CI/CD

Une pipeline CI/CD a été mise en place avec GitHub Actions afin d’automatiser les premières vérifications du projet.

Une issue spécifique a été créée pour suivre ce travail. Les modifications ont été réalisées sur une branche dédiée puis intégrées dans la branche principale à l’aide d’une Pull Request.

Cette pipeline constitue une première base sur laquelle des tests et d’autres contrôles de qualité pourront être ajoutés.

## Organisation du workflow Git

Une méthode de travail a été définie pour relier les issues et les modifications apportées au projet.

Chaque tâche peut être associée à une issue GitHub. Une branche dédiée est ensuite créée pour réaliser les modifications. Le travail est enregistré à travers des commits puis intégré dans `main` à l’aide d’une Pull Request.

Cette organisation permet de conserver une trace claire du travail réalisé.

## Cahier de laboratoire

Un cahier de laboratoire a été ajouté dans le dossier :

`docs/cahiers-de-labo/`

Il permet de conserver une trace du travail effectué à chaque séance, des décisions prises, des difficultés rencontrées et de l’évolution du projet.

## Prochaines étapes

Les prochaines étapes seront consacrées à la prise en main de Git, à la préparation des environnements locaux et au développement des premières issues.
