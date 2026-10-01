# Séance 4: Organisation du projet et mise en place de la CI/CD

## Objectifs de la séance

Cette séance avait pour objectif de structurer le développement du projet Épicer’INT, d’organiser les différentes fonctionnalités à réaliser et de mettre en place les premiers éléments techniques nécessaires au développement.

## Organisation du projet

Un **GitHub Project** a été mis en place afin de centraliser et de suivre les différentes tâches du projet.

Les principales fonctionnalités identifiées dans le cahier des charges ont été créées sous forme d’issues :

- Gestion des utilisateurs et authentification
- Gestion des produits et des stocks
- Gestion des commandes et des paiements
- Gestion des distributions et de la récupération des commandes
- Système de notifications
- Dashboard administrateur et statistiques

Les issues ont été organisées dans le backlog du projet. Nous avons également mis en place l’utilisation des différents statuts (`Backlog`, `Ready`, `In progress`, `In review`, `Done`) afin de suivre leur avancement.

Des **itérations** ont également été configurées afin de déterminer les tâches à réaliser au cours des différentes périodes de développement.

## Estimation et répartition du travail

Une première estimation du temps nécessaire à la réalisation de chaque issue a été effectuée afin d’évaluer la charge de travail et de mieux organiser les prochaines séances.

Les différentes issues ont ensuite été réparties entre les membres du groupe afin que chacun dispose de responsabilités clairement identifiées.

Cette répartition pourra évoluer au cours du projet en fonction de l’avancement, des dépendances entre les fonctionnalités et des difficultés rencontrées pendant le développement.

## Mise en place de la CI/CD

Une pipeline **CI/CD** a été mise en place afin d’automatiser les vérifications nécessaires au cours du développement.

Une issue spécifique a été créée dans le GitHub Project pour suivre cette tâche. Le développement a été réalisé sur une branche associée à cette issue.

La pipeline permet d’exécuter automatiquement les premières vérifications du projet et constitue une base sur laquelle pourront être ajoutés progressivement les tests et autres contrôles de qualité.

## Organisation du workflow Git

Une convention de travail a été définie afin de relier les différents éléments du développement.

Chaque tâche de développement peut être associée à une issue GitHub. Une branche dédiée est ensuite créée pour réaliser les modifications correspondantes. Les changements sont enregistrés à travers des commits puis intégrés dans `main` à l’aide d’une Pull Request liée à l’issue concernée.

Cette organisation permet de conserver une meilleure traçabilité entre les tâches prévues et les modifications apportées au code.

## Cahier de laboratoire

Un cahier de laboratoire a été ajouté directement au dépôt GitHub dans le dossier :

`docs/cahier-de-labo/`

Il permettra de conserver une trace du travail effectué à chaque séance, des décisions prises, des difficultés rencontrées et de l’évolution du projet.

## Prochaines étapes

Les prochaines séances seront consacrées au développement progressif des fonctionnalités définies dans le backlog.

Les issues seront intégrées aux différentes itérations en fonction de leur priorité, de leur estimation et de leur répartition entre les membres du groupe.
