# Epicer'INT

Application Django pour centraliser la gestion des produits, des membres et des distributions alimentaires d'Épicer'INT.

## Lancer le projet

Prérequis : Git, Docker Compose et Bash (Git Bash ou WSL sous Windows).

```bash
git clone https://github.com/RabahSend/Epicer-int.git
cd Epicer-int
sh ./run.sh
```

L'application est accessible sur [http://localhost:8000](http://localhost:8000).

## Comptes par défaut

Un compte administrateur est créé automatiquement au démarrage de Docker :

- **E-mail :** `admin@epicerint.local`
- **Mot de passe :** `projetinfo1A`

L'administration est accessible sur [http://localhost:8000/admin/](http://localhost:8000/admin/). Ces identifiants sont réservés au développement local : change le mot de passe avant tout déploiement. Les identifiants peuvent être personnalisés avec les variables `DJANGO_SUPERUSER_EMAIL` et `DJANGO_SUPERUSER_PASSWORD`.

## Roadmap

- [x] Gestion des comptes des cotisants et authentification
- [x] Gestion des produits et des stocks
- [x] Consultation du catalogue et préparation du panier
- [ ] Passage et validation des commandes
- [ ] Paiement en ligne
- [ ] Organisation du retrait des commandes lors des distributions
- [ ] Notifications aux utilisateurs
- [ ] Tableau de bord administrateur (optionnel)

## Modèle de données

![Graphe des modèles](docs/models.png)

Pour régénérer le graphe :

```bash
docker compose exec web python manage.py graph_models users catalog orders notifications core --disable-abstract-fields --exclude-models AbstractUser,AbstractBaseUser,PermissionsMixin,Group,Permission -o /tmp/models.png
docker compose cp web:/tmp/models.png docs/models.png
```
