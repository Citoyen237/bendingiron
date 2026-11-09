# Corrections de sécurité — novembre 2026

Ce fichier liste les changements apportés au projet après l'audit de sécurité
(voir `BendingIron_Audit_Securite.pdf`) et **ce qu'il faut faire pour les mettre en production**.

## À faire AVANT de déployer (obligatoire)

1. **Changer tous les secrets** qui étaient dans le code ou dans l'ancien `.env` :
   - nouvelle `SECRET_KEY` : `python -c "from django.core.management.utils import get_random_secret_key as g; print(g())"`
   - mot de passe de la boîte `contact@bending-iron.com` (chez Hostinger)
   - mot de passe MySQL (utilisateur `bendingiron` et root)
   - clés Orange Money (consumer key/secret, mot de passe API, PIN) et clé MTN MoMo
2. **Créer le `.env` sur le serveur** à partir de `.env.example` (il n'est plus dans le projet).
   Vérifier `DJANGO_SETTINGS_MODULE=SiteDFmac.production` et `DEBUG=False`.
3. **Migrations en attente** : les modèles `Projet` (champs `annee`, `sequence`) et `TraimentPro`
   ont changé sans migration dans l'archive reçue. Si ces migrations existent déjà sur ton serveur
   ou ta machine, ajoute-les au dépôt. Sinon, crée-les en local :
   `python manage.py makemigrations partenaires proforma` puis versionne-les.
   (La CI vérifie maintenant qu'aucune migration ne manque.)
4. **Nginx** : remplacer la configuration par `bending.conf` (MEDIA_URL est `/medias/`,
   les devis et archives ne sont plus servis directement), puis `sudo nginx -t && sudo systemctl reload nginx`.
5. **Droits des dossiers** (l'application ne tourne plus en root dans Docker) :
   `sudo chown -R 1000:1000 medias staticfiles` dans `/var/www/bendingiron`.
6. **Pare-feu** : `sudo ufw allow 22,80,443/tcp && sudo ufw enable`. MySQL et phpMyAdmin ne sont plus exposés.
7. **Déploiement GitHub Actions** : créer un utilisateur `deploy` sur le VPS (membre du groupe `docker`),
   puis ajouter les secrets `VPS_USER`, `VPS_IP`, `VPS_SSH_KEY` (clé privée ed25519) et
   `VPS_KNOWN_HOSTS` (sortie de `ssh-keyscan -H <IP>`). Le secret `VPS_SSH_PASS` n'est plus utilisé.
   Désactiver ensuite la connexion root par mot de passe (`PermitRootLogin no` dans sshd_config).
8. **Nettoyer l'historique Git** si `.env` ou `db.sqlite3` y ont été commités (`git filter-repo`).

Vérification après déploiement :
`docker compose exec web python manage.py check --deploy` ne doit rien signaler.

## Ce qui a changé

| Faille | Correction | Fichiers |
|---|---|---|
| S1 DEBUG en production | DEBUG lu dans le .env, `False` par défaut ; wsgi/asgi chargent `SiteDFmac.production` | `SiteDFmac/settings.py`, `production.py`, `wsgi.py`, `asgi.py` |
| S2 Secrets en dur | Toutes les clés lues via `config()` ; `.gitignore`, `.dockerignore`, `.env.example` ; mot de passe MySQL de docker-compose lu dans le .env | `settings.py`, `docker-compose.yml` |
| S3 Prix falsifiable | Prix recalculé par le serveur (cadre carré) ; contrôle minimal pour les autres produits | `produits/pricing.py`, `produits/views.py` |
| S4 Vues admin ouvertes | Module commun `auth_app/permissions.py` ; mixin admin sur les 8 vues oubliées | `admin_site/views.py` |
| S5 Factures d'autrui (IDOR) | Filtrage par propriétaire (`get_owned_or_404`) sur factures, bons, projets, commandes additionnelles ; proformas réservées aux admins | `usesOrders/views.py`, `partenaires/views.py`, `proforma/views.py`, `admin_site/views.py` |
| S6 Commande sur le projet d'un autre | Vérification du propriétaire, des articles du projet, des quantités restantes et de `peut_commander` | `partenaires/views.py` |
| S7 Commande sans paiement | `confirmer-la-commande/` et `information-personnel/` réservées aux admins (commande manuelle) | `usesOrders/views.py` |
| S8 Mot de passe oublié | Mécanisme Django (lien signé à usage unique) ; le mot de passe ne change plus à la demande | `auth_app/views.py`, `urls.py`, nouveaux gabarits |
| S9 GET + escalade | Changement de rôle, blocage, statuts, suppression en POST avec jeton CSRF ; rôles admin/superadmin donnés par un superadmin uniquement ; pas de modification de son propre compte | `admin_site/views.py`, 5 gabarits |
| S10 Code promo | Connexion + POST + CSRF obligatoires ; expiration vérifiée avant de compter une utilisation ; une seule utilisation comptée par panier ; codes générés avec `secrets` | `usesOrders/views.py`, `admin_site/views.py` |
| S11 Infra exposée | MySQL sans port public, phpMyAdmin à la demande en local, Gunicorn sans `--reload` et timeout 60 s, migrations non générées en production, image Docker sans root | `docker-compose.yml`, `run.sh`, `Dockerfile` |
| S12 CI root | Clé SSH + utilisateur dédié + vérification d'hôte ; rsync sans `.env` ni médias | `.github/workflows/django.yml`, `deploy.sh` |
| S13 Cookies/HTTPS | Cookies sécurisés, HSTS, redirection HTTPS, `SECURE_PROXY_SSL_HEADER` | `settings.py` |
| S14 Force brute | 5 essais par e-mail et IP, puis blocage 15 min | `auth_app/views.py` |
| S15 Paiement | Montant renvoyé par l'opérateur comparé au montant attendu ; `login_required` sur les pages de suivi | `paiements/models.py`, `paiements/views.py` |
| S16 Fichiers | Contrôle du contenu (PDF commençant par `%PDF-`, image vérifiée) ; devis et archives servis par des vues admin | `SiteDFmac/validators.py`, `contact/form.py`, `archives/` |
| S17 Lien e-mail | Construit avec `SITE_URL` (https), un seul e-mail envoyé | `auth_app/views.py` |
| S18 Dépendances | Django 5.2 LTS ; paquets inutilisés retirés | `requirements.txt` |
| S19 Requêtes lourdes | Compteurs du tableau de bord calculés pour les admins seulement, en une requête | `*/context_proc*.py` |

## Bogues corrigés

- **B1** Inscription : `username` = e-mail (deux clients peuvent avoir le même prénom).
- **B2** `Payment` devient une `ForeignKey` (`related_name="payments"`) : acompte puis solde possibles. Migration `usesOrders/0012`.
- **B3** Client MTN absent : plus de `NameError`, message d'erreur propre ; `paiements/services.py` (doublon mort) supprimé.
- **B4** Noms d'URL inexistants dans `paiements/views.py` corrigés.
- **B5** Gabarits `payments/paiement_en_cours.html` (avec suivi automatique) et `payments/payer_solde.html` créés.
- **B6** Panier vide / partenaire sans partenariat : redirection au lieu d'une erreur 500.
- **B7** Ajout au panier sans être connecté : redirection vers la connexion.
- **B8** La remise du code promo est maintenant copiée du panier vers la commande (avant, chaque commande prenait `remise=1` par défaut et la remise du code était perdue).
- **B9** `frais_ingenieurie` (texte) converti en nombre avant les calculs du projet.
- **B10** Langue et fuseau horaire : `fr-fr` et `Africa/Douala` (ils étaient écrasés par `en-us`/`UTC`).
- **B11** `change_password` exige la connexion et applique les règles de mot de passe de Django.
- **B14** `print()` de débogage retirés.
- **Nouveau** Deux URL portaient le même nom `change.status` (commandes et proformas) : la proforma utilise maintenant `change.status.pro`.
- **Nouveau** Le statut des commandes additionnelles modifiait une commande de projet portant le même numéro : vue dédiée `change_statut_order_add`.
- **Nouveau** `paiements/0001_initial` ne dépendait pas de `usesOrders` : une base neuve (ou la CI) ne pouvait pas être créée.
- **Nouveau** Liste des archives : variable `archive` inexistante (les vidéos ne s'affichaient pas).
- **Nouveau** `ReponseForm.clean_file` était placé dans `Meta` et n'était jamais exécuté.
- **Nouveau** Le processeur de contexte `constante_global` faisait planter toutes les pages si une ligne `FerPrice` manquait.

## Reste à faire

- **Prix côté serveur pour les autres produits** (S3). Seul le cadre carré est porté, car c'est le seul
  gabarit qui utilise déjà le nouveau modèle de calcul (PrixFer + Constante). Pour chaque autre produit,
  ajoute une fonction dans `produits/pricing.py` qui reproduit la formule de son gabarit, puis
  enregistre-la dans `CALCULATEURS`. Quand tous les produits sont portés, mets
  `PRIX_SERVEUR_OBLIGATOIRE = True` dans les réglages : un produit sans calcul serveur sera alors refusé.
  En attendant, les produits non portés acceptent encore le prix du navigateur (avec un contrôle
  minimal et un avertissement dans les journaux).
- Client MTN MoMo (`paiements/services/mtn_momo.py`) et tâche planifiée `expirer_demandes_perimees`.
- Remise : elle est calculée sur la somme des prix de revient **sans** tenir compte des quantités. À vérifier avec la règle commerciale.
- La limitation des tentatives de connexion utilise le cache mémoire (par worker Gunicorn).
  Pour une protection complète, installer `django-axes` ou ajouter `limit_req` dans Nginx.

## Tests

```
DB_ENGINE=sqlite SECRET_KEY=test DEBUG=True python manage.py test
```
`auth_app/tests.py` contient 23 tests qui vérifient les corrections (accès au cPanel, factures,
rôles, partenaires, prix serveur, mot de passe oublié, connexion, code promo).
