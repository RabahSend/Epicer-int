# Séance 4 : Installation de l’environnement et prise en main de Git

## Informations sur la séance

- **Date :** 22 septembre 2026
- **Format :** réunion en visioconférence en dehors des heures de cours (20 h 00 - 22 h 00)
- **Présents :** Adel et Rabah

## Objectifs de la séance

Cette réunion avait pour objectif d’aider Adel à préparer son environnement de développement, de lui expliquer le fonctionnement de Git et de commencer le travail sur les premières issues.

## Prise en main de Git

Rabah a expliqué à Adel les principales commandes et le fonctionnement général de Git.

Ils ont notamment vu comment :

- récupérer le projet sur l’ordinateur ;
- consulter les fichiers modifiés ;
- créer et utiliser une branche ;
- ajouter des fichiers à un commit ;
- enregistrer les modifications ;
- envoyer une branche sur GitHub ;
- récupérer les dernières modifications du dépôt ;
- créer et fusionner une Pull Request.

Ces explications ont permis à Adel de mieux comprendre le workflow défini pendant la séance précédente.

## Installation de l’environnement

Rabah a accompagné Adel pendant l’installation et la configuration de l’environnement local.

Ils ont préparé l’environnement virtuel Python, installé les dépendances du projet et vérifié le lancement de l’application Django.

La configuration de PostgreSQL et de sa connexion avec Django a également été examinée. Plusieurs erreurs de connexion ont nécessité de vérifier le pilote `psycopg`, le service PostgreSQL et le fichier de configuration utilisé par le projet.

## Présentation de l’architecture

Rabah a présenté à Adel l’organisation du projet par domaine métier.

Le projet est divisé en plusieurs applications :

- `users` pour les utilisateurs ;
- `catalog` pour les produits ;
- `orders` pour les commandes et les paiements ;
- `notifications` pour les notifications ;
- `core` pour les éléments communs du site.

Les premiers modèles de données concernant les utilisateurs, les produits, les commandes, les paiements, les distributions et les notifications avaient été ajoutés au projet.

## Travail sur les premières issues

Adel et Rabah ont commencé à travailler sur les issues qui leur avaient été attribuées.

Le layout général du site et une première page consacrée aux produits ont été ajoutés. Adel a également fusionné la Pull Request liée à la création du layout général.

Cette première interface comprend une page d’accueil, un menu de navigation et une mise en page commune aux différentes pages du site.

## Prochaines étapes

Les prochaines étapes seront de poursuivre l’authentification, de préparer la page des commandes et de continuer à développer chaque fonctionnalité sur une branche dédiée.
