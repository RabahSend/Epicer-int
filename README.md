# Epicer'INT

Application web Django pour la gestion des distributions alimentaires d'Épicer'INT.

## Démarrage avec Docker

Prérequis : [Docker](https://docs.docker.com/get-docker/) et Docker Compose.

```bash
docker compose up --build
```

L'application est ensuite accessible sur [http://localhost:8000](http://localhost:8000).

Les migrations sont appliquées automatiquement au démarrage. Pour créer un compte administrateur :

```bash
docker compose exec web python manage.py createsuperuser
```

Pour générer le diagramme des modèles de données du projet :

```bash
docker compose exec web python manage.py graph_models users catalog orders notifications core -o models.png
```

Pour arrêter les services :

```bash
docker compose down
```

## Règles d'accès

- Les visiteurs peuvent consulter les produits actifs et leur disponibilité.
- La création d'un compte ne valide pas une cotisation et ne donne pas accès au panier.
- Après cotisation auprès de l'association, un administrateur active le champ « cotisation active » du compte dans l'administration Django. Seuls les membres actifs peuvent ajouter des produits au panier, dans la limite du stock.
- Le panier sert actuellement à préparer une sélection. Le paiement en ligne et la validation d'une commande ne sont pas encore disponibles.

---

# Cahier des charges - Epicer'INT

## 1. Présentation du projet

Le projet consiste à développer un site web pour **Epicer'INT** permettant de faciliter la gestion des produits, des cotisants, des commandes et des distributions.

Epicer'INT organise régulièrement des distributions alimentaires à destination des étudiants de **Télécom SudParis** et **IMT-BS**.

Ces distributions proposent différents types de produits, notamment :

* des féculents ;
* des fruits et légumes frais ;
* des conserves ;
* des produits sucrés.

Actuellement, certaines informations, notamment celles concernant les cotisants, sont gérées à l'aide d'une feuille Excel.

L'objectif du projet est de centraliser et de simplifier une partie de cette gestion au sein d'une application web.

---

## 2. Objectifs

Le site devra permettre :

* la gestion des produits et des stocks ;
* la création et la gestion des comptes des cotisants ;
* l'authentification des utilisateurs ;
* l'achat et le paiement des produits directement depuis le site ;
* la gestion de la récupération des commandes ;
* l'envoi de notifications aux utilisateurs ;
* éventuellement, la mise à disposition d'un tableau de bord pour les administrateurs.

---

## 3. Fonctionnalités

### 3.1. Gestion des utilisateurs

Actuellement, les cotisants sont gérés via une feuille Excel.

Le nouveau système devra permettre de stocker les informations des cotisants dans une base de données.

Les cotisants devront pouvoir :

* disposer d'un compte ;
* s'authentifier sur le site ;
* accéder aux fonctionnalités qui leur sont réservées.

### 3.2. Gestion des produits et des stocks

Les administrateurs devront pouvoir gérer les produits disponibles sur le site.

Le système devra notamment permettre de gérer les stocks afin que les utilisateurs puissent sélectionner les produits disponibles.

### 3.3. Commandes et paiement

Les utilisateurs devront pouvoir :

1. sélectionner les produits qu'ils souhaitent acheter ;
2. effectuer leur paiement directement depuis le site ;
3. récupérer ensuite leur commande lors de la distribution.

### 3.4. Système de notifications

Un système de notifications devra informer les utilisateurs de certains événements.

Exemples indiqués :

* ajout d'un nouvel article ;
* modification d'un article ;
* rappel avant une distribution, par exemple :

> La distribution va commencer dans X minutes.

### 3.5. Dashboard administrateur — Optionnel

Une interface d'administration pourra être développée afin de fournir des statistiques sur l'utilisation du service.

Elle pourrait notamment présenter :

* le nombre de personnes ayant acheté un panier ;
* des statistiques liées aux produits ;
* d'autres indicateurs d'utilisation à définir.

Cette fonctionnalité est considérée comme **optionnelle** et pourra être réalisée après les fonctionnalités principales.

---

## 4. Priorisation

| Priorité    | Fonctionnalité                           |
| ----------- | ---------------------------------------- |
| Haute       | Gestion des comptes des cotisants        |
| Haute       | Authentification                         |
| Haute       | Base de données utilisateurs             |
| Haute       | Gestion des produits                     |
| Haute       | Gestion des stocks                       |
| Haute       | Commandes                                |
| Haute       | Paiement en ligne                        |
| Moyenne     | Gestion de la récupération des commandes |
| Moyenne     | Notifications                            |
| Optionnelle | Dashboard administrateur et statistiques |

---

## 5. Points restant à définir

Les éléments suivants devront être précisés avant ou pendant la conception du projet :

* les rôles et permissions des différents utilisateurs ;
* les informations nécessaires pour créer un compte ;
* les règles exactes de gestion des stocks ;
* le fonctionnement d'une commande ;
* le prestataire ou moyen de paiement ;
* le fonctionnement de la récupération des commandes ;
* les événements déclenchant une notification ;
* le canal utilisé pour envoyer les notifications ;
* les statistiques attendues dans le dashboard administrateur ;
* les contraintes techniques, de sécurité et d'hébergement.
