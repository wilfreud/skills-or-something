# OWASP Top 10:2025 appliqué à une application React

Le Top 10 OWASP est pensé pour des applications web dans leur ensemble (front + back + infra), pas spécifiquement pour un composant React. Ce fichier explique comment chaque catégorie se manifeste côté frontend, pour que tu puisses classifier une trouvaille de revue sous la bonne étiquette dans un rapport.

Point important pour 2025 : **le XSS n'est plus une catégorie à part — il est classé sous A05 Injection** (CWE-79, avec plus de 30 000 CVE rattachés). Garde ça en tête quand tu écris "A05" dans un rapport pour un problème de XSS plutôt que de chercher une catégorie "XSS" dédiée qui n'existe plus dans cette édition.

## A01 — Broken Access Control

Dans le Top 10:2025, c'est la catégorie n°1, présente dans 100% des applications testées lors de l'étude OWASP.

**Manifestation côté React** : tout contrôle d'accès qui n'existe _que_ dans le composant (un `if (user.role === 'admin')` qui cache un bouton ou bloque une route côté client) est par construction contournable — un attaquant appelle directement l'API avec `curl` sans jamais passer par l'UI. OWASP illustre littéralement ce scénario dans sa documentation 2025 : une page admin protégée uniquement par du JavaScript côté navigateur reste accessible en requêtant l'endpoint directement.

Ce que ça veut dire en pratique pour une revue : un `<ProtectedRoute>` ou un garde de navigation React est une bonne pratique UX, jamais une mesure de sécurité suffisante à elle seule. Vérifie systématiquement (ou demande confirmation) que l'API backend réapplique la même vérification. Vérifie aussi le stockage de tokens (attributs de cookies, `SameSite`), et les configurations CORS trop permissives côté client qui autorisent des origines non fiables à consommer l'API.

## A02 — Security Misconfiguration

Côté frontend, ça recouvre : configuration CSP absente ou trop permissive (`unsafe-inline`, `*` comme source), variables d'environnement de build exposées par erreur au bundle client (notamment en Next.js/Vite si un préfixe public est mal utilisé), source maps de production accessibles publiquement révélant la structure interne du code, headers de sécurité manquants (`X-Content-Type-Options`, `X-Frame-Options` / `frame-ancestors`).

## A03 — Software Supply Chain Failures

Catégorie élargie en 2025 : ce n'est plus seulement "dépendances avec CVE connu", mais toute la chaîne (packages non maintenus, compromission d'un package légitime, absence de SBOM, pipeline CI/CD faiblement sécurisé). Pour un projet React/npm concrètement :

- Dépendances `react`/`react-dom` ou librairies tierces avec des vulnérabilités connues → auditer avec `npm audit`, Snyk, ou un outil équivalent, pas seulement une fois mais en continu.
- Attention particulière aux attaques de type ver auto-propagateur sur l'écosystème npm (des campagnes réelles ont déjà touché des centaines de packages en exploitant des scripts post-install et des tokens npm volés sur les machines de développeurs) : vérifier que les scripts `postinstall` de tes dépendances sont légitimes, et que les tokens npm/CI ne traînent pas en clair sur les postes de dev.
- Préférer figer les versions (lockfile committé, versions exactes plutôt que ranges larges) et ne mettre à jour que consciemment plutôt qu'en confiance aveugle.

## A04 — Cryptographic Failures

Rarement le cœur d'un composant React, mais à signaler si tu vois : des secrets/clés API en dur dans le code client (tout ce qui est bundlé côté client est lisible par n'importe qui, quel que soit l'obfuscation), du chiffrement "maison" tenté côté navigateur pour protéger des données sensibles (le navigateur n'est pas un environnement de confiance pour ça), ou des données sensibles transmises sans HTTPS.

## A05 — Injection (inclut le XSS)

La catégorie centrale de ce skill. Voir `references/xss-prevention.md` pour le détail complet. Pour résumer le principe general OWASP : le problème apparaît chaque fois qu'une donnée non fiable atteint un interpréteur (ici : le moteur de rendu HTML/JS du navigateur) sans être séparée du code exécutable — que ce soit via `dangerouslySetInnerHTML`, une URL `javascript:`, ou un `eval`.

## A06 — Insecure Design

Concerne des choix d'architecture plutôt qu'un bug ponctuel : par exemple, une SPA qui fait reposer toute sa logique métier sensible côté client (calculs de prix, permissions fines, règles métier) sans jamais les revalider côté serveur. Un attaquant modifie simplement l'état local ou intercepte/rejoue une requête pour contourner la logique.

## A07 — Authentication Failures

Côté React : gestion de session fragile (token de longue durée stocké sans rotation, pas de déconnexion effective côté serveur), absence de protection contre le brute force sur les formulaires de login gérés côté client, réutilisation d'un même token entre plusieurs contextes de confiance.

## A08 — Software or Data Integrity Failures

Pertinent si l'app charge du code ou des données depuis des sources externes sans vérification d'intégrité : scripts tiers chargés sans Subresource Integrity (`integrity="sha384-..."`), CDN non épinglé à une version précise, désérialisation de données non fiables sans validation de schéma, mise à jour automatique (auto-update) de composants sans vérification de signature.

## A09 — Security Logging and Alerting Failures

Moins visible dans un simple composant, mais pertinent en revue plus large : absence de traçabilité des échecs d'autorisation côté client qui remonteraient au backend, logs client qui exposent par erreur des données sensibles (attention aux `console.log` de tokens/PII qui restent en prod).

## A10 — Mishandling of Exceptional Conditions

Gestion d'erreur qui expose des détails internes (stack traces, messages d'erreur bruts de l'API renvoyés tels quels à l'utilisateur), ou à l'inverse des erreurs silencieusement avalées qui masquent un échec de contrôle de sécurité (par exemple un `try/catch` qui neutralise une erreur de validation et laisse le flux continuer comme si tout allait bien).

## Comment utiliser ce mapping dans un rapport

Pour chaque trouvaille, indique la catégorie OWASP Top 10:2025 correspondante (ex. "A05 — Injection (XSS via dangerouslySetInnerHTML)") en plus de la description technique. Ça donne à l'utilisateur un langage commun avec le reste de son organisation si elle utilise déjà le Top 10 comme référentiel de priorisation.
