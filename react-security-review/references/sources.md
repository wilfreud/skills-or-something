# Sources de référence

Liste des sources faisant autorité sur lesquelles s'appuie ce skill. Cite-les (par leur nom + URL, jamais par citation verbatim de leur contenu) quand tu justifies une recommandation dans un rapport de revue.

## OWASP (sources officielles)

- **OWASP Top 10:2025** — https://owasp.org/Top10/2025/
  La liste consensuelle des 10 risques de sécurité applicative les plus critiques. Sert de grille de classification macro pour n'importe quelle vulnérabilité trouvée.
- **OWASP Cheat Sheet Series — Cross Site Scripting Prevention** — https://cheatsheetseries.owasp.org/cheatsheets/Cross_Site_Scripting_Prevention_Cheat_Sheet.html
  Référence sur l'encodage de sortie contextuel (HTML, attribut, JS, CSS, URL) et la sanitization HTML. Base de `references/xss-prevention.md`.
- **OWASP Cheat Sheet Series — DOM based XSS Prevention** — https://cheatsheetseries.owasp.org/cheatsheets/DOM_based_XSS_Prevention_Cheat_Sheet.html
  Référence sur le XSS déclenché côté client (sans aller-retour serveur), les sinks dangereux du DOM, et les pièges d'encodage en contexte JS.
- **OWASP Cheat Sheet Series (index général)** — https://cheatsheetseries.owasp.org/
  Utile pour aller chercher une cheat sheet plus spécifique (CSP, CSRF, Authentication, Secrets Management, Third Party Javascript Management...) si la revue déborde du périmètre XSS.
- **OWASP Code Review Guide** — https://owasp.org/www-project-code-review-guide/assets/OWASP_Code_Review_Guide_v2.pdf
  Méthodologie générale de revue de code orientée sécurité (comment prioriser, comment documenter une trouvaille, checklist de review).
- **OWASP Developer Guide** — https://devguide.owasp.org/
  Guide plus large sur la conception d'applications sécurisées, utile pour du contexte architecture (au-delà du seul composant React revu).
- **OWASP Bullet-proof React** — https://owasp.org/www-project-bullet-proof-react/
  Projet OWASP (incubateur) dédié spécifiquement à la sécurité des apps React/Node. Encore jeune en contenu au moment de la rédaction de ce skill — vérifier s'il a été enrichi avant de s'y référer en détail.

## Autres sources reconnues

- **Snyk — 10 React security best practices** — https://snyk.io/blog/10-react-security-best-practices/
  Checklist orientée pratique : binding JSX par défaut, URLs `javascript:`, `dangerouslySetInnerHTML` + DOMPurify, accès DOM direct via refs, SSR (`renderToStaticMarkup`), dépendances vulnérables, injection JSON dans le state préchargé, versions de React, configuration ESLint sécurité, code de librairies tierces.
- **Jim Manico — Building Secure ReactJS Applications** (SecAppDev) — https://handouts.secappdev.org/handouts/2024/jimmanico_building-secure-reactjs-applications.pdf
  Support de formation d'un expert reconnu en sécurité applicative (co-auteur de plusieurs OWASP Cheat Sheets). PDF volumineux ; à consulter directement si l'utilisateur veut approfondir un point précis que ce skill ne couvre pas déjà.

## Comment utiliser cette liste

- Pour une explication technique courante (encodage, sinks dangereux, sanitization) → les fichiers de référence de ce skill suffisent déjà, pas besoin d'aller chercher les sources à chaque fois.
- Pour un sujet non couvert ici (CSRF, authentification, secrets management, sécurité GraphQL, etc.) → indique à l'utilisateur la cheat sheet OWASP pertinente plutôt que d'improviser.
- Ne reproduis jamais un extrait long d'une de ces pages mot pour mot — reformule l'idée avec tes propres mots et donne le lien pour que l'utilisateur aille lire l'original si besoin.
