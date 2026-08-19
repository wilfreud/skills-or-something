# Durcissement serveur (Node.js) pour Next.js — référence détaillée

Next.js s'exécute sur Node.js côté serveur (hors Edge Runtime). Cette référence condense l'OWASP Node.js Security Cheat Sheet et la checklist Arcjet, filtrées pour ce qui reste pertinent une fois qu'on a déjà couvert le modèle RSC/Server Actions dans les autres fichiers.

## En-têtes de sécurité HTTP

Next.js ne configure aucun en-tête de sécurité par défaut — c'est à l'application de les définir, généralement via `proxy.ts` ou la config `headers()` dans `next.config.js`.

- **Content-Security-Policy (CSP)** : l'en-tête le plus important contre XSS/injection de code, spécifie quelles sources de scripts/styles/images sont autorisées. Démarrer strict (`default-src 'self'`) et assouplir seulement si nécessaire, plutôt que l'inverse. Next.js documente une approche manuelle via middleware ; des librairies comme Nosecone (Arcjet) ou Helmet (pour du Node.js générique) simplifient la configuration type-safe.
- **Strict-Transport-Security (HSTS)** : force HTTPS, empêche les attaques de downgrade.
- **X-Content-Type-Options: nosniff** : empêche le navigateur de deviner un type MIME différent de celui déclaré.
- **Permissions-Policy** : restreint quelles APIs navigateur (caméra, géoloc, etc.) sont accessibles aux scripts.
- **Referrer-Policy** : limite les informations envoyées au clic sur un lien sortant.
- **`X-Frame-Options` / `frame-ancestors`** : anti-clickjacking. `frame-ancestors` dans la CSP est la version moderne, `X-Frame-Options` reste utile pour les navigateurs plus anciens qui ne supportent pas cette directive CSP.
- **`X-XSS-Protection`** : header hérité d'Internet Explorer/anciens Chrome/Safari, **déprécié** — s'il est présent avec une valeur autre que `0`, c'est un signal de configuration obsolète à corriger plutôt qu'un vrai contrôle de sécurité actif.
- **Trusted Types** : supporté par React, mais **pas encore par Next.js** au moment de la rédaction de cette référence — ne pas recommander cette protection comme disponible nativement sur ce framework sans vérifier l'état actuel du support.

Une fois les en-têtes configurés, un outil comme securityheaders.com ou le CSP Evaluator de Google permet de vérifier la configuration effective plutôt que de se fier uniquement à la lecture du code.

## Cookies

`httpOnly`, `Secure`, et `SameSite` sont les trois attributs à vérifier systématiquement sur tout cookie de session :

- `httpOnly` empêche l'accès en JavaScript côté client — protection contre l'exfiltration de session via XSS.
- `Secure` empêche l'envoi du cookie hors HTTPS.
- `SameSite` (Next.js utilise `Lax` par défaut sur ses propres cookies internes) réduit fortement le CSRF.

## Variables d'environnement et secrets

- Vérifier que `.env*` figure dans `.gitignore` — un secret commité dans l'historique Git reste récupérable même après suppression du fichier.
- Seules les variables destinées au client doivent porter le préfixe `NEXT_PUBLIC_` ; toute variable sensible sans ce préfixe reste côté serveur par défaut, mais vérifier qu'aucun code ne la réexpose manuellement (voir `references/data-exposure-rsc.md`).
- Pour des secrets à fort enjeu (clés de paiement, clés de chiffrement principales), un gestionnaire de secrets dédié (Vault, AWS Secrets Manager, 1Password, Doppler...) est préférable à une simple variable d'environnement — les variables d'environnement peuvent fuiter via des logs, crashs, ou erreurs de configuration.
- En auto-hébergement, un scan des artefacts de build (ex. Trufflehog) permet de vérifier qu'aucun secret ne s'est retrouvé embarqué par erreur dans le bundle déployé.

## Limitation de fréquence et brute force

Toute route d'authentification, tout Server Action coûteux, et plus généralement toute opération qui peut être appelée en boucle par un script devrait avoir une forme de rate limiting. Sans ça, un formulaire de login est vulnérable au bourrage d'identifiants (credential stuffing) même si les mots de passe sont correctement hashés côté stockage.

## Fonctions et patterns dangereux côté serveur

- `eval()` et `child_process.exec()` avec une entrée influencée par l'utilisateur sont les deux sinks d'exécution de code les plus directs côté Node.js — s'ils apparaissent avec une donnée qui remonte, même indirectement, d'une requête HTTP, c'est une trouvaille Critique.
- Le module `vm` de Node.js permet d'exécuter du code dans un contexte isolé, mais n'est pas un vrai sandbox de sécurité — ne pas le présenter comme une protection suffisante contre du code non fiable.
- Regex "évils" (motifs avec répétition/alternance imbriquée) peuvent causer un déni de service (ReDoS) si appliqués à une entrée utilisateur non bornée en taille — repérer les regex complexes appliquées à des champs de formulaire libres.
- Limiter la taille des requêtes acceptées (`express.json({ limit: ... })` ou équivalent côté Route Handler) pour éviter qu'une requête à corps massif épuise la mémoire serveur.

## Ne retourner que le nécessaire

Ce principe s'applique autant aux Route Handlers (`route.ts`) qu'aux Server Actions et au Data Access Layer : une fonction qui interroge la base de données pour un utilisateur ne doit renvoyer que les champs dont l'appelant a besoin, jamais l'enregistrement complet "parce que c'est plus simple". C'est la même logique que les DTO du Data Access Layer, appliquée aussi aux endpoints REST/route handlers classiques d'un projet Next.js hybride.

## Dépendances

- `npm audit` (et `npm audit fix` pour les corrections automatiques) doit tourner régulièrement, idéalement en CI.
- Committer le lockfile (`package-lock.json`/équivalent) pour figer les versions exactes plutôt que des ranges qui se resolvent différemment à chaque install — ça réduit aussi la surface d'un détournement de package (package hijacking) qui viserait une nouvelle version publiée entre deux builds.
- Un outil de scan de dépendances en continu (Dependabot, Socket, Snyk) réduit le délai entre la divulgation d'une CVE et sa correction — voir `references/known-cves-and-middleware.md` pour les CVE spécifiques à surveiller en priorité sur cet écosystème.

## Gestion des erreurs

En mode production, React/Next.js remplacent automatiquement les messages d'erreur détaillés par un hash générique côté client (utile pour corréler avec les logs serveur sans exposer de détail sensible) — mais cette protection ne s'applique qu'en véritable mode production. Vérifier que le déploiement tourne bien avec `NODE_ENV=production` (`next build` + `next start`, pas `next dev`) ; le mode développement envoie les erreurs en clair au client, ce qui est acceptable en local mais jamais en production.

Pour du code Node.js hors du cycle de vie standard des requêtes (handlers `uncaughtException`, EventEmitters custom), vérifier que les erreurs sont bien écoutées/gérées plutôt que silencieusement avalées ou laissées à faire planter le process sans nettoyage des ressources.
