# CVE critiques connues et pièges du middleware/proxy — référence détaillée

Mise à jour : recherche effectuée le 31 juillet 2026. Cette référence documente des vulnérabilités réelles avec CVE attribué sur l'écosystème React/Next.js, de la RCE critique de décembre 2025 jusqu'aux dernières releases de sécurité de juillet 2026. Ce n'est pas un contenu OWASP au sens strict — OWASP publie des cheat sheets et un Top 10 généraliste, pas de CVE spécifiques à un framework. Les CVE listées ici proviennent des avis officiels Vercel/Next.js, de GitHub Security Advisories (GHSA), du NVD/CVE.org, et de vendeurs de sécurité (Netlify, Cloudflare, Fastly, Snyk). La colonne "Catégorie OWASP" fait le pont avec le Top 10:2025 utilisé ailleurs dans ce skill et dans react-security-review — voir la note en fin de fichier sur les limites de ce mapping.

**Vérifie systématiquement si une CVE plus récente que celles listées ici a été publiée avant de conclure un audit** — ce framework a eu un rythme de publication très soutenu sur les 8 derniers mois, et rien ne garantit que cette liste reste exhaustive après la date de mise à jour indiquée ci-dessus.

## Changement architectural essentiel : `middleware.ts` → `proxy.ts` (Next.js 16)

Avant même de lister les CVE, il faut connaître ce changement car il redéfinit le vocabulaire du reste de ce fichier.

**Next.js 16 a renommé la convention de fichier `middleware.ts` en `proxy.ts`** (export nommé `proxy` plutôt que `middleware`). La convention `middleware.ts` est officiellement dépréciée ; un codemod officiel migre automatiquement le nom de fichier et de fonction.

- **Raison donnée par l'équipe Next.js** : le terme "middleware" prête à confusion avec le middleware Express.js (qui tourne dans la même confiance applicative), alors que ce composant Next.js se comporte en réalité comme un **proxy réseau** placé devant l'application — d'où le renommage pour clarifier ce qu'il est réellement capable de faire, et décourager d'y loger de la logique métier ou d'y faire confiance comme couche de sécurité à elle seule.
- Le lien avec CVE-2025-29927 est explicite dans plusieurs analyses techniques : la confusion conceptuelle ("c'est du middleware, donc une couche de confiance applicative") a directement contribué à la sévérité de cette CVE de contournement.
- **API globalement inchangée** : `NextRequest`, `NextResponse`, les matchers, restent identiques — seul le nom du fichier/export et son fonctionnement par défaut changent (le proxy tourne par défaut sur le runtime Node.js plutôt que sur l'Edge Runtime).
- **Ce qui compte pour une revue** : si tu vois `middleware.ts` dans un projet récent, vérifie si le projet est resté sur Next.js 15 (convention encore valide) ou s'il tourne sur Next.js 16 avec un fichier non migré (avertissement de build, risque de configuration silencieusement ignorée). Si tu vois `proxy.ts`, applique exactement les mêmes précautions d'audit que pour `middleware.ts` : ce n'est toujours pas une couche d'autorisation suffisante à elle seule, quel que soit le nom.

## La série de vulnérabilités du protocole RSC "Flight" (déc. 2025 → mai 2026)

Le protocole de désérialisation des React Server Components a fait l'objet de **quatre avis de sécurité distincts** en six mois, sur la même surface de code (`react-server-dom-webpack`/`-parcel`/`-turbopack`). C'est le signal le plus important à retenir de ce fichier : cette surface a un historique de fragilité répétée, pas un incident isolé.

| Date         | CVE                                             | Sévérité                 | Nature                                                                                         | Versions corrigées (React / Next.js)                       |
| ------------ | ----------------------------------------------- | ------------------------ | ---------------------------------------------------------------------------------------------- | ---------------------------------------------------------- |
| 3 déc. 2025  | CVE-2025-55182 / CVE-2025-66478 ("React2Shell") | **Critique — CVSS 10.0** | RCE non authentifiée par désérialisation non sécurisée du payload Flight                       | React 19.0.1/19.1.2/19.2.1 · Next.js 15.0.5–15.5.7, 16.0.7 |
| 28 jan. 2026 | CVE-2026-23864 (GHSA-h25m-26qc-wcjf)            | Élevée                   | DoS (CPU, out-of-memory, crash serveur) via désérialisation RSC                                | Voir avis GitHub associé                                   |
| 8 avr. 2026  | CVE-2026-23869 (GHSA-q4gf-8mx6-v5v3)            | Élevée — CVSS 7.5        | DoS via structures de données cycliques dans `ReactFlightReplyServer.js` (CWE-770 + CWE-502)   | React 19.0.5/19.1.6/19.2.5 · Next.js 15.5.15, 16.2.3       |
| 6-7 mai 2026 | CVE-2026-23870                                  | Élevée — CVSS 7.5        | DoS, 4ᵉ avis de cette série depuis déc. 2025 ; requête forgée vers un endpoint Server Function | React 19.0.6/19.1.7/19.2.6 · Next.js 15.5.18, 16.2.6       |

**Ce que ça veut dire en revue** : si tu vois du code qui expose un endpoint Server Function/Server Action (donc quasiment toute app App Router), ne te contente pas de vérifier une seule CVE — vérifie que la version installée est postérieure à la **dernière** ligne de ce tableau (15.5.18/16.2.6 au minimum, idéalement la version patchée la plus récente listée plus bas). Une app "juste patchée contre React2Shell" en décembre 2025 pouvait rester vulnérable aux trois vagues de DoS suivantes.

## Mai 2026 : la release coordonnée de 13 advisories

Le 6-7 mai 2026, Next.js a publié une release de sécurité groupant **13 advisories** (React + Next.js), au-delà du DoS RSC déjà listé ci-dessus :

**Contournements de middleware/proxy (4 avis distincts, tous "High")** — GHSA-267c-6grr-h53f, GHSA-26hh-7cqf-hhc6, GHSA-492v-c6pp-mqqv, GHSA-36qx-fr4f-26g5 :

- Contournement d'authentification via l'URL de segment-prefetch de l'App Router.
- Contournement du même mécanisme de segment-prefetch — un correctif de suivi pour un fix initial incomplet.
- Pages Router avec i18n : le chemin `/_next/data/<buildId>/<page>.json` sans préfixe de locale n'était pas intercepté par le middleware/proxy, permettant de récupérer le JSON SSR de pages protégées sans passer par l'autorisation prévue.
- Contournement via injection de paramètre de route dynamique.

Explicitement documenté comme affectant **"les applications qui s'appuient sur `middleware.js` ou `proxy.js` pour l'autorisation"** — la même leçon architecturale que CVE-2025-29927/CVE-2024-51479, mais quatre nouvelles variantes techniques.

**Autres avis de ce lot** :

- **DoS via épuisement de connexions dans les Cache Components** (CVE-2026-44579) — requêtes POST malveillantes créant un deadlock sur le corps de requête, épuisant les descripteurs de fichiers serveur. Affecte les apps utilisant les Cache Components pour le Partial Prerendering (fonctionnalité opt-in).
- **SSRF via la gestion des upgrades WebSocket** (High).
- **Empoisonnement de cache des réponses RSC** (Modéré) et **empoisonnement de cache via collisions de cache-busting RSC** (Faible) — affecte les apps avec une couche de cache/CDN devant les réponses Server Components.
- **XSS via les nonces CSP dans l'App Router** et **XSS via les scripts `beforeInteractive` consommant une entrée non fiable** (Modéré chacun) — pertinent si le projet utilise des nonces CSP comme défense en profondeur contre le XSS (voir `xss-prevention.md` du skill react-security-review) : un nonce mal généré ou réutilisé annule une partie de cette protection.

Versions corrigées : Next.js **15.5.18** / **16.2.6** ; React **19.0.6** / **19.1.7** / **19.2.6**.

## 13 mai 2026 : lot spécifique aux versions EOL

Une semaine après la release coordonnée, trois CVE supplémentaires ont été publiées, concernant spécifiquement l'impact sur les versions **déjà en fin de vie (EOL)**, c'est-à-dire antérieures à la ligne 15.5.x :

| CVE            | Sévérité                                      | Nature                                                                                                                                                                                                               |
| -------------- | --------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| CVE-2026-44573 | Élevée (CVSS 7.5)                             | Une requête externe peut atteindre une route de données interne normalement protégée par le middleware — abus de l'en-tête interne `x-nextjs-data` sur un chemin géré par un middleware qui renvoie une redirection. |
| CVE-2026-44572 | Faible à Modéré selon la source (GHSA vs NVD) | Injection d'un en-tête interne qui ne devrait être positionné que par Next.js lui-même.                                                                                                                              |
| CVE-2026-44577 | Modéré (CVSS 5.9)                             | Une requête externe peut atteindre le chemin de récupération d'image en auto-hébergement sans limite de ressource sur la réponse — DoS via l'optimisation d'image.                                                   |

Ces trois CVE étaient déjà corrigées en amont dans **15.5.16** / **16.2.5** (avant même la release du 7 mai) mais restent **non corrigées sur les versions EOL** (antérieures à 15.5.x) — Vercel ne rétroporte pas de correctif sur ces lignes. Une CVE liée, **CVE-2026-44575**, concerne un correctif de contournement middleware qui ne s'appliquait pas correctement à `middleware.ts` utilisé avec Turbopack.

**Ce que ça veut dire en revue** : si le projet audité tourne sur une version Next.js antérieure à 15.5.x et n'a pas de plan de mise à jour, ce n'est plus un simple retard technique — c'est une exposition permanente à ces CVE sans correctif possible sur cette ligne. La recommandation dans ce cas n'est pas "patcher" mais "planifier une migration vers une ligne supportée", et le signaler comme un risque à part entière dans le rapport plutôt que comme une simple ligne de checklist.

## Juillet 2026 : 9 CVE supplémentaires + nouveau modèle de release préannoncée

Next.js est passé à un **modèle de release de sécurité préannoncée** (annoncée à l'avance pour laisser le temps aux équipes de planifier), officialisé mi-juillet 2026. La première release sous ce modèle, le 20 juillet 2026, corrige 9 CVE dans **16.2.11** (Active LTS) et **15.5.21** (Maintenance LTS) :

| CVE                | Sévérité | Nature                                                                                                                                                                                                                                                                                         |
| ------------------ | -------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| CVE-2026-64641     | Élevée   | DoS dans l'App Router via les Server Actions — une requête forgée consomme du CPU en excès et bloque le traitement des requêtes suivantes sur le même process.                                                                                                                                 |
| CVE-2026-64642     | Élevée   | Contournement middleware/proxy — App Router avec Turbopack et une seule entrée dans `config.i18n.locales` ; toute vérification d'auth du middleware/proxy est contournée.                                                                                                                      |
| **CVE-2026-64645** | Élevée   | **SSRF/Open Redirect** — une règle `rewrites()`/`redirects()` qui construit son hostname de destination à partir d'une entrée contrôlée par la requête peut être détournée vers un hostname arbitraire, quel que soit le suffixe attendu. `rewrites()` → SSRF ; `redirects()` → Open Redirect. |
| **CVE-2026-64649** | Élevée   | **SSRF via Server Actions sur serveur auto-hébergé** — quand une Server Action relaie/redirige une requête, un attaquant peut faire pointer la requête sortante vers un hôte malveillant en maîtrisant les en-têtes liés au Host.                                                              |
| CVE-2026-64644     | Modérée  | DoS dans l'API d'optimisation d'image via des SVG malveillants (auto-hébergement, chargement d'images distantes configuré).                                                                                                                                                                    |
| CVE-2026-64646     | Modérée  | Payload de Server Action non borné sur l'Edge runtime → épuisement mémoire.                                                                                                                                                                                                                    |
| CVE-2026-64643     | Modérée  | Divulgation non authentifiée des identifiants internes d'endpoints Server Function/`use cache` — utilisable en reconnaissance dans une attaque plus large.                                                                                                                                     |
| CVE-2026-64648     | Modérée  | Confusion de cache : un `fetch` serveur avec corps de requête peut retourner la réponse mise en cache d'une _autre_ requête vers la même URL avec un corps différent (`fetch(new Request(init), aDifferentInit)`).                                                                             |
| CVE-2026-64647     | Modérée  | Même famille de confusion de cache, spécifique aux corps de requête contenant des séquences UTF-8 invalides.                                                                                                                                                                                   |

**Deux nouveautés notables pour la checklist du SKILL.md principal** : c'est la première fois que du **SSRF via `rewrites()`/`redirects()` avec hostname contrôlé par la requête** et du **SSRF via relai de Server Action** apparaissent comme classe de vulnérabilité documentée sur ce framework — à ajouter explicitement aux patterns recherchés en revue (voir mise à jour de la table dans `SKILL.md`).

## Tableau récapitulatif — versions à date (31 juillet 2026)

| Ligne                            | Dernière version connue comme patchée au 31/07/2026                                                     |
| -------------------------------- | ------------------------------------------------------------------------------------------------------- |
| Next.js 16.x (Active LTS)        | 16.2.11 (ou 16.3.0-canary.92 / 16.3.0-preview.7 pour les fonctionnalités les plus récentes)             |
| Next.js 15.5.x (Maintenance LTS) | 15.5.21                                                                                                 |
| Next.js < 15.5 (EOL)             | Pas de correctif garanti pour CVE-2026-44572/44573/44577/44575 — migration recommandée plutôt que patch |
| React                            | 19.0.6 / 19.1.7 / 19.2.6 minimum (vérifier une version plus récente si publiée après cette recherche)   |

Ne présente jamais ce tableau comme définitif dans une réponse à l'utilisateur sans le qualifier — les CVE se sont enchaînées à un rythme mensuel sur ce framework depuis décembre 2025, donc une vérification en direct (changelog officiel Next.js, `npm view next versions`) reste nécessaire pour toute revue à enjeu réel.

## Principe général mis à jour

Les CVE de mars 2025 à juillet 2026 pointent toutes vers la même leçon architecturale, renforcée par le renommage `middleware.ts` → `proxy.ts` lui-même : **le middleware/proxy est fait pour de la redirection UX et un premier filtre grossier, jamais pour être l'unique gardien d'une ressource sensible.** Plusieurs guides de migration vers `proxy.ts` recommandent désormais explicitement de déplacer la logique d'authentification vers des **"Server Layout Guards"** — des vérifications de session faites dans `layout.tsx` via les Server Components, donc plus proches de la couche de données que de la couche réseau. Si tu vois un projet Next.js 16+ qui a migré vers `proxy.ts` mais y a conservé toute sa logique d'authentification sans re-vérification dans les layouts/Server Actions/DAL, signale-le comme le même risque architectural que documenté pour `middleware.ts` — le renommage ne change rien à la mécanique de contournement si l'usage ne change pas aussi.

Pour le SSRF (nouveau en 2026 sur ce framework), le principe équivalent : **toute construction d'URL de destination (rewrite, redirect, relai de Server Action) doit être validée contre une liste explicite de hosts autorisés, jamais construite à partir d'une entrée requête sans validation** — voir aussi `references/xss-prevention.md` du skill react-security-review, section validation d'URL, dont le principe de whitelist de protocole s'applique de façon analogue ici à la whitelist de hostname.

## Note sur le mapping OWASP

Rien dans ce fichier n'est une publication OWASP — OWASP ne référence pas de CVE de framework spécifique dans ses cheat sheets ou son Top 10. Le rattachement à une catégorie OWASP Top 10:2025 reste néanmoins utile pour un rapport de revue : les contournements de middleware/proxy relèvent d'A01 (Broken Access Control), les CVE de désérialisation RSC (RCE et DoS) relèvent d'A05 (Injection, au sens large de la désérialisation de données non fiables) ou d'A08 (Software/Data Integrity Failures) selon l'angle retenu, et les SSRF de juillet 2026 n'ont pas de catégorie dédiée dans le Top 10:2025 (contrairement au Top 10:2021 qui avait une catégorie SSRF autonome) — classe-les sous A05 par défaut, mais vérifie la documentation OWASP à jour si ce point a de l'importance pour le rapport, plutôt que d'affirmer ce mapping avec une confiance excessive.
