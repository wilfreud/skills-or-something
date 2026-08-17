---
name: react-security-review
description: Utilise ce skill pour auditer, relire ou écrire du code React/JavaScript/TypeScript en gardant la sécurité en tête — XSS classique et DOM-based, injection via URL, sanitization de HTML, mauvaise gestion du SSR/hydration, dépendances npm vulnérables, contrôle d'accès géré uniquement côté client, secrets exposés au client, CSP absente, etc. Basé sur l'OWASP Top 10:2025, les OWASP Cheat Sheets (Cross Site Scripting Prevention, DOM based XSS Prevention), le guide de revue de code OWASP, et des sources reconnues (Snyk, Jim Manico). Déclenche ce skill dès que l'utilisateur demande une revue de sécurité d'un composant/PR React, demande si du code est "safe"/"sûr", colle du code contenant dangerouslySetInnerHTML, innerHTML, eval, une URL dynamique dans href/src, ou mentionne XSS, sanitization, CSP, OWASP, audit de sécurité, vulnérabilité — même sans utiliser explicitement le mot "sécurité".
---
 
# Revue de sécurité React
 
## Pourquoi cette approche
 
React encode automatiquement le contenu texte inséré via `{}` en JSX, ce qui protège déjà contre une bonne partie du XSS classique. Le vrai travail de revue consiste donc à repérer les endroits où le code *sort* de ce mécanisme de protection par défaut : accès direct au DOM, insertion de HTML brut, construction dynamique d'URL ou d'attributs, désérialisation de données non fiables, ou logique de sécurité qui n'existe que côté client. C'est là que se concentrent quasiment toutes les vulnérabilités réelles trouvées dans des apps React.
 
## Quand utiliser ce skill
 
- L'utilisateur demande explicitement une revue de sécurité, un audit, ou "est-ce que ce code est safe ?"
- Du code React/JS/TS est collé ou fourni en fichier et contient un des signaux suivants, même sans mention explicite de sécurité : `dangerouslySetInnerHTML`, `innerHTML`, `outerHTML`, `document.write`, `eval(`, `new Function(`, un `href`/`src` construit dynamiquement, `localStorage`/`sessionStorage` avec un token ou une clé, une route "protégée" par un simple `if` React.
- L'utilisateur écrit un nouveau composant qui doit afficher du contenu utilisateur, du HTML riche, ou gérer de l'authentification/autorisation — applique alors ce skill de façon proactive, pas seulement en mode revue.
- L'utilisateur mentionne OWASP, CSP, sanitization, DOMPurify, ou une CVE touchant React/npm.
## Méthode de revue
 
### 1. Repérer les sinks dangereux
 
Scanne le code (mentalement ou avec un vrai `grep` si tu as accès au dépôt) à la recherche de ces patterns. Chacun est développé en détail dans `references/xss-prevention.md`.
 
| Pattern à repérer | Risque | Détail |
|---|---|---|
| `dangerouslySetInnerHTML` sans sanitization visible juste à côté | XSS (HTML) | xss-prevention.md §1 |
| `ref.current.innerHTML =`, `.outerHTML =`, `document.write(` | XSS (HTML, accès DOM direct) | xss-prevention.md §1, "Accès direct au DOM" |
| `href={...}`, `src={...}`, `window.location =` avec une valeur non validée | XSS (URL / `javascript:`) | xss-prevention.md §3 |
| `eval(`, `new Function(`, `setTimeout(`/`setInterval(` avec une chaîne comme 1er argument | Injection de code | xss-prevention.md §4 |
| `renderToStaticMarkup()`/`renderToString()` suivi d'une concaténation, `JSON.stringify` d'un state préchargé sans échapper `<` | XSS (SSR/hydration) | xss-prevention.md "Server-Side Rendering" |
| Route ou bouton protégé uniquement par un `if` React, sans revérification serveur | Broken Access Control (A01) | owasp-top10-2025-react.md §A01 |
| Clé API, secret, ou logique métier sensible en dur dans un composant client | Exposition de secrets (A01/A04) | owasp-top10-2025-react.md §A01, §A04 |
| Version de `react`/`react-dom`/dépendance tierce ancienne ou jamais auditée | Supply chain (A03) | owasp-top10-2025-react.md §A03 |
| Script tiers chargé depuis un CDN sans `integrity=` | Software Integrity (A08) | owasp-top10-2025-react.md §A08 |
| Absence totale de CSP sur une app qui affiche du contenu utilisateur | Défense en profondeur manquante | xss-prevention.md "Défense en profondeur" |
 
Cette table est un point de départ, pas une liste exhaustive — si tu repères un pattern dangereux qui n'y figure pas, signale-le quand même en expliquant le raisonnement.
 
### 2. Qualifier chaque trouvaille
 
Pour chaque sink repéré, détermine si la donnée qui l'alimente est réellement non fiable (venant d'un utilisateur, d'une API tierce, de l'URL, du stockage local) ou si elle est en fait entièrement contrôlée par le code (auquel cas ce n'est pas une vulnérabilité, juste un pattern à surveiller si le code évolue). Ne signale pas comme "vulnérabilité confirmée" un sink dangereux alimenté uniquement par une constante codée en dur — nuance plutôt en "pattern risqué si la donnée devient dynamique un jour".
 
### 3. Produire un rapport structuré
 
Pour une revue de code existant, utilise ce format par trouvaille :
 
```
### [Sévérité] Titre court de la vulnérabilité
 
**Où** : chemin du fichier / nom du composant / numéro de ligne si connu
**Catégorie OWASP** : ex. A05 — Injection (XSS)
**Le problème** : explique en 1-2 phrases pourquoi ce pattern est exploitable, avec le mécanisme concret (pas juste "c'est dangereux")
**Exploitation possible** : un exemple concret et bref de ce qu'un attaquant pourrait faire
**Correctif recommandé** : le pattern sûr à utiliser à la place, avec un court extrait de code si utile
**Référence** : lien vers la cheat sheet OWASP ou la source pertinente (voir references/sources.md)
```
 
Sévérités à utiliser : **Critique** (exécution de code / exfiltration de données arbitraire, exploitable facilement), **Élevée** (XSS confirmé mais nécessitant des conditions spécifiques), **Moyenne** (pattern risqué, exploitabilité incertaine ou limitée), **Faible** (mauvaise pratique, défense en profondeur manquante).
 
Termine le rapport par un résumé en une phrase du niveau de risque global, et rappelle explicitement que cette revue est un premier passage automatisé/assisté, pas un audit de sécurité formel — recommande un test de pénétration ou une revue humaine spécialisée si l'enjeu le justifie (application exposée publiquement, données sensibles, secteur réglementé).
 
### 4. Si l'utilisateur écrit du nouveau code plutôt que d'en faire relire
 
Pas besoin d'un rapport formel — applique directement les patterns sûrs de `references/xss-prevention.md` en écrivant le code, et mentionne brièvement en une phrase pourquoi tu as fait tel choix (ex. "je valide le protocole de l'URL avant de l'utiliser dans le `href`, pour éviter l'injection via `javascript:`"). Ne transforme pas une simple demande de code en cours de sécurité — reste concis, l'explication doit tenir en une ou deux lignes par choix notable.
 
## Références disponibles
 
- `references/xss-prevention.md` — détail complet des contextes XSS (HTML, attribut, URL, JS, CSS), des sinks dangereux et sûrs, du SSR/hydration, et de la défense en profondeur (CSP, Trusted Types). Consulte-le avant de rédiger l'explication technique d'une trouvaille liée au XSS.
- `references/owasp-top10-2025-react.md` — comment chacune des 10 catégories OWASP 2025 se manifeste concrètement dans une app React, pour classifier correctement une trouvaille qui ne relève pas du XSS (accès, dépendances, intégrité...).
- `references/sources.md` — liste des sources faisant autorité à citer dans un rapport (jamais de citation verbatim longue, toujours reformulée).
## Limites à garder en tête
 
Ce skill couvre le code frontend React et ses interactions immédiates avec le DOM/le navigateur. Il ne remplace pas une revue de la sécurité backend (validation serveur, injection SQL, gestion des secrets côté serveur) — si le code fourni touche à ces sujets, tu peux les signaler brièvement mais oriente vers les cheat sheets OWASP correspondantes (`Injection_Prevention_Cheat_Sheet`, `Authorization_Cheat_Sheet`, etc.) plutôt que d'improviser une expertise backend que ce skill ne couvre pas en détail.