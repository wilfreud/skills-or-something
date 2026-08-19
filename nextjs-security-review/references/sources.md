# Sources de référence

Sources faisant autorité pour ce skill. Cite-les par nom + URL, jamais par citation verbatim longue de leur contenu.

## Next.js (officiel)

- **How to think about data security in Next.js** — https://nextjs.org/docs/app/guides/data-security
  Guide officiel actuel sur les trois modèles d'accès aux données, le Data Access Layer, le tainting, `server-only`, la sécurité des Server Actions (IDs sécurisés, validation, CSRF, closures/chiffrement), et une checklist d'audit. Base principale de `references/data-exposure-rsc.md` et `references/server-actions-security.md`.
- **How to Think About Security in Next.js (blog, 2023)** — https://nextjs.org/blog/security-nextjs-server-components-actions
  Version blog historique du même sujet, avec en plus le détail sur le middleware/Route Handlers comme "escape hatches" à fort pouvoir et la gestion des erreurs (hashing côté client en prod).
- **Production checklist** — https://nextjs.org/docs/app/building-your-application/deploying/production-checklist
  Checklist officielle avant mise en production, section "Security" : tainting, vérif auth/authz dans les Server Actions, variables d'environnement (`.gitignore`, préfixe `NEXT_PUBLIC_`), CSP.
- **CVE-2025-66478** — https://nextjs.org/blog/CVE-2025-66478
  Avis de sécurité officiel Next.js pour la RCE critique (CVSS 10.0) dans le protocole RSC "Flight", déc. 2025. Versions affectées/corrigées, action requise, recommandation de rotation des secrets. Base de `references/known-cves-and-middleware.md`.
- **July 2026 Security Release** — https://nextjs.org/blog/july-2026-security-release
  Avis officiel détaillant les 9 CVE corrigées en juillet 2026 (dont les deux premiers SSRF documentés sur ce framework, via `rewrites()`/`redirects()` et via relai de Server Action), et le passage à un modèle de release de sécurité préannoncée.
- **Renaming Middleware to Proxy** — https://nextjs.org/docs/messages/middleware-to-proxy
  Documentation officielle du renommage `middleware.ts` → `proxy.ts` dans Next.js 16, avec la justification (confusion avec le middleware Express, encouragement à ne pas y loger de logique de sécurité) et le codemod de migration.
- **File-system conventions: proxy.js** — https://nextjs.org/docs/app/api-reference/file-conventions/proxy
  Référence technique de la nouvelle convention `proxy.js`/`proxy.ts`, API et comportement (exécution avant le rendu, runtime Node.js par défaut).

## Snyk

- **Security Advisory: Critical RCE Vulnerabilities in React Server Components** — https://snyk.io/blog/security-advisory-critical-rce-vulnerabilities-react-server-components/
  Analyse technique complémentaire de CVE-2025-55182/CVE-2025-66478 : mécanisme de désérialisation non sécurisée, chronologie de la divulgation, recommandations de détection (scanners de dépendances, monitoring réseau/cloud).

## Autres vendeurs de sécurité (recherche complémentaire sur les CVE 2026)

- **Vercel — Next.js May 2026 security release** — https://vercel.com/changelog/next-js-may-2026-security-release
  Résumé des 13 advisories de mai 2026 (DoS RSC, contournements middleware/proxy, SSRF WebSocket, empoisonnement de cache, XSS via nonces CSP).
- **Netlify — Next.js & React DoS vulnerability** — https://www.netlify.com/changelog/2026-04-08-react-nextjs-dos-vulnerability/ et **Next.js & React security release (May 2026)** — https://www.netlify.com/changelog/2026-05-08-react-nextjs-security-vulnerabilities/
  Détail de CVE-2026-23869 (avril) et du lot de mai 2026, avec l'impact spécifique par plateforme de déploiement (utile pour évaluer le risque réel selon l'hébergeur du projet audité).
- **Fastly — What is CVE-2026-23869?** — https://www.fastly.com/blog/what-is-cve-2026-23869-react-server-components-security-alert
  Détail technique du DoS via structures de données cycliques dans le protocole Flight.
- **GitHub Security Advisories** — GHSA-h25m-26qc-wcjf (CVE-2026-23864), GHSA-q4gf-8mx6-v5v3 (CVE-2026-23869)
  Avis GitHub associés à la série de DoS RSC, utiles pour vérifier les plages de versions précises si besoin d'un niveau de détail supérieur à ce que couvre `known-cves-and-middleware.md`.
- **HeroDevs — Three Next.js Vulnerabilities Affecting EOL versions** — https://www.herodevs.com/blog-posts/cve-2026-44573-cve-2026-44577-cve-2026-44572-three-next-js-vulnerabilities-affecting-eol-versions
  Analyse du lot de CVE du 13 mai 2026 spécifique aux versions Next.js en fin de vie (EOL).

## Arcjet (reconnu dans l'écosystème Next.js)

- **Next.js security checklist** — https://blog.arcjet.com/next-js-security-checklist/
  Checklist pratique en 7 points : dépendances, validation/sanitization des données, variables d'environnement, exposition de code (`server-only`), en-têtes de sécurité (CSP, HSTS, Trusted Types — non supporté par Next.js à ce jour), centralisation des fonctions de sécurité (AuthN/AuthZ), outillage éditeur (linters de sécurité, détecteurs de secrets).
- **Next.js middleware bypasses: How to tell if you were affected?** — https://blog.arcjet.com/next-js-middleware-bypasses-how-to-tell-if-you-were-affected/
  Détail de CVE-2025-29927 (bypass via `x-middleware-subrequest`) et CVE-2024-51479 (bypass d'autorisation basé sur le pathname), avec les signatures à rechercher dans des logs d'incident. Base de la section middleware dans `references/known-cves-and-middleware.md`.

## OWASP

- **Nodejs Security Cheat Sheet** — https://cheatsheetseries.owasp.org/cheatsheets/Nodejs_Security_Cheat_Sheet.html
  Bonnes pratiques génériques Node.js applicables au runtime serveur de Next.js : en-têtes de sécurité (Helmet), flags de cookies, limitation de taille de requête, fonctions dangereuses (`eval`, `child_process.exec`), regex ReDoS, gestion des erreurs non catchées. Base de `references/nodejs-hardening.md`.
- **OWASP Top 10:2025** — https://owasp.org/Top10/2025/
  Grille de classification macro pour toute trouvaille — voir aussi le fichier `owasp-top10-2025-react.md` du skill react-security-review (le mapping y est déjà détaillé et s'applique tel quel à Next.js).
- **OWASP Cheat Sheet Series (index)** — https://cheatsheetseries.owasp.org/
- **OWASP Code Review Guide** — https://owasp.org/www-project-code-review-guide/assets/OWASP_Code_Review_Guide_v2.pdf
- **OWASP Developer Guide** — https://devguide.owasp.org/

## Sources partagées avec le skill react-security-review

Ce skill se concentre sur ce qui est spécifique à Next.js (RSC, Server Actions, middleware, runtime Node). Pour le XSS côté rendu React (`dangerouslySetInnerHTML`, URLs `javascript:`, sinks DOM dangereux), qui s'applique identiquement dans une app Next.js, référe-toi au skill **react-security-review** et à ses fichiers `xss-prevention.md` / `owasp-top10-2025-react.md` s'il est installé. Sinon, le résumé condensé dans le `SKILL.md` de ce skill suffit pour les cas courants.

- OWASP Cross Site Scripting Prevention Cheat Sheet — https://cheatsheetseries.owasp.org/cheatsheets/Cross_Site_Scripting_Prevention_Cheat_Sheet.html
- OWASP DOM based XSS Prevention Cheat Sheet — https://cheatsheetseries.owasp.org/cheatsheets/DOM_based_XSS_Prevention_Cheat_Sheet.html
- Snyk — 10 React security best practices — https://snyk.io/blog/10-react-security-best-practices/
- Jim Manico — Building Secure ReactJS Applications — https://handouts.secappdev.org/handouts/2024/jimmanico_building-secure-reactjs-applications.pdf
- OWASP Bullet-proof React — https://owasp.org/www-project-bullet-proof-react/ (projet incubateur, contenu encore limité au moment de la rédaction)

## Comment utiliser cette liste

- Pour classifier une trouvaille RSC/Server Actions/middleware → les fichiers de référence de ce skill suffisent.
- Pour une trouvaille XSS classique côté rendu → mentionne qu'elle relève du skill react-security-review si l'utilisateur veut le détail complet, mais tu peux déjà répondre avec le résumé du SKILL.md.
- Pour vérifier si une version installée est concernée par une CVE → toujours confirmer avec `references/known-cves-and-middleware.md`, ne jamais deviner une plage de versions de mémoire.
- Ne reproduis jamais un extrait long d'une de ces pages mot pour mot — reformule et donne le lien.
