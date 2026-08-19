---
name: nextjs-security-review
description: Utilise ce skill pour auditer, relire ou écrire du code Next.js (App Router ou Pages Router) en gardant la sécurité en tête — exposition de données RSC, Server Actions non revalidées (auth/authz/IDOR), middleware/proxy comme seule barrière d'autorisation, SSRF via rewrites/redirects/Server Actions, versions vulnérables (RCE CVE-2025-55182/66478, série de DoS RSC CVE-2026-23864/23869/23870, bypass middleware/proxy CVE-2025-29927/2024-51479/2026-64642, SSRF CVE-2026-64645/64649), variables d'env exposées, en-têtes manquants. Basé sur la doc officielle Next.js (sécurité, Server Actions, releases 2026, proxy.ts), avis Vercel/Next.js/Snyk, checklist Arcjet, OWASP Node.js Cheat Sheet. Se déclenche pour toute revue Next.js, ou du code avec "use server"/"use client", middleware.ts, proxy.ts, route.ts, rewrites()/redirects(), requête DB dans un Server Component, ou mention de RSC/CVE/next.config — même sans le mot "sécurité". Complète react-security-review pour le XSS côté rendu React.
---

# Revue de sécurité Next.js

## Pourquoi cette approche

Next.js App Router introduit un modèle où le code serveur et le code client sont écrits côte à côte dans les mêmes fichiers, avec une frontière logique (`"use client"` / `"use server"`) plutôt qu'une séparation physique claire comme dans une architecture SPA + API classique. C'est puissant, mais ça déplace le risque principal : ce n'est plus tant "un attaquant injecte du code" que "le développeur expose par erreur des données ou une action qui n'auraient jamais dû franchir la frontière serveur → client". La majorité des vulnérabilités réelles trouvées dans des apps Next.js récentes suivent ce schéma — d'où l'accent mis dans ce skill sur l'exposition de données RSC et la revalidation systématique des Server Actions, en plus des CVE connues du framework lui-même.

## Quand utiliser ce skill

- L'utilisateur demande une revue de sécurité, un audit, ou "est-ce que ce code Next.js est safe ?"
- Du code est fourni et contient un des signaux suivants, même sans mention explicite de sécurité : `"use server"`, `"use client"` avec des props larges, un Server Component qui fait une requête DB puis passe l'objet résultat directement à un composant enfant, `middleware.ts`, `route.ts` avec une méthode mutative, `process.env` en dehors d'une couche d'accès aux données, une variable préfixée `NEXT_PUBLIC_` contenant potentiellement un secret.
- L'utilisateur écrit un nouveau Server Action, une nouvelle route protégée, ou un nouveau composant qui affiche des données utilisateur — applique le skill de façon proactive, pas seulement en mode revue.
- L'utilisateur mentionne une version de Next.js/React, demande si son projet est concerné par une CVE, ou colle un extrait de `package.json`.

## Méthode de revue

### 1. Identifier le modèle d'accès aux données du projet

Avant d'auditer le détail, détermine si le projet utilise des API HTTP externes, un Data Access Layer dédié, ou un accès direct aux données dans les composants (voir `references/data-exposure-rsc.md`). Le mélange des trois approches dans un même projet est déjà un signal à mentionner, même sans vulnérabilité concrète identifiée.

### 2. Repérer les sinks et patterns dangereux

| Pattern à repérer | Risque | Référence |
|---|---|---|
| Server Component qui passe un objet DB entier (`<Profile user={userData} />`) à un composant `"use client"` | Exposition de données privées | data-exposure-rsc.md |
| Fichier `"use client"` dont les props acceptent un type large (`User`, `Team`) plutôt qu'une interface minimale | Exposition de données privées | data-exposure-rsc.md |
| `process.env` référencé hors d'un module `server-only` / du Data Access Layer | Fuite de secret | data-exposure-rsc.md |
| Variable `NEXT_PUBLIC_*` contenant une clé/API secrète | Secret exposé au bundle client | data-exposure-rsc.md, nodejs-hardening.md |
| `searchParams`/`params` utilisés directement pour une décision d'autorisation (`?isAdmin=true`) | Contournement d'accès (A01) | data-exposure-rsc.md |
| `"use server"` sans re-vérification d'auth/autorisation à l'intérieur de la fonction | Action publique non protégée | server-actions-security.md |
| Server Action qui vérifie l'authentification mais pas la propriété de la ressource | IDOR | server-actions-security.md |
| Server Action qui retourne l'enregistrement DB complet plutôt qu'un objet minimal | Sur-exposition de données | server-actions-security.md |
| `route.ts` avec un GET/POST custom sans vérification CSRF manuelle | CSRF (protections automatiques absentes hors Server Actions) | server-actions-security.md |
| Middleware/`proxy.ts` comme unique vérification d'autorisation pour une route sensible | Contournement structurel + historique de CVE réelles (dont 4 avis rien qu'en mai 2026) | known-cves-and-middleware.md |
| `matcher` du middleware/proxy qui ne couvre pas explicitement la route racine ET ses sous-routes, ou config i18n avec une seule locale + Turbopack | Contournement d'accès (CVE-2024-51479, CVE-2026-64642) | known-cves-and-middleware.md |
| `rewrites()`/`redirects()` qui construit un hostname de destination à partir d'une entrée requête sans whitelist | SSRF (rewrites) / Open Redirect (redirects) — CVE-2026-64645 | known-cves-and-middleware.md |
| Server Action qui relaie/redirige une requête sortante en se basant sur un en-tête Host contrôlable | SSRF — CVE-2026-64649 | known-cves-and-middleware.md, server-actions-security.md |
| `middleware.ts` non migré vers `proxy.ts` sur un projet Next.js 16+ (avertissement de build silencieux) | Config d'auth potentiellement ignorée | known-cves-and-middleware.md |
| Version de `next`/`react`/`react-dom` dans une plage vulnérable connue (RCE de déc. 2025, série de DoS RSC de jan./avr./mai 2026, lot EOL de mai 2026, 9 CVE de juillet 2026) | RCE critique, DoS, bypass middleware/proxy, SSRF | known-cves-and-middleware.md |
| Absence de CSP/en-têtes de sécurité, cookies de session sans `httpOnly`/`Secure`/`SameSite` | Défense en profondeur manquante | nodejs-hardening.md |
| `dangerouslySetInnerHTML`, `innerHTML`, URL `javascript:` dans un `href` | XSS classique (hérité de React) | voir résumé ci-dessous, ou skill react-security-review |

Cette table est un point de départ, pas une liste exhaustive.

### 3. Vérifier les versions contre les CVE connues

Dès que tu as accès à un `package.json`/lockfile (ou que l'utilisateur mentionne une version), croise-la avec `references/known-cves-and-middleware.md` — en particulier CVE-2025-55182/CVE-2025-66478 (RCE critique RSC, déc. 2025) et CVE-2025-29927/CVE-2024-51479 (contournements de middleware). Si tu n'as pas cette information, demande-la ou recommande explicitement à l'utilisateur de vérifier plutôt que de supposer que le projet est à jour.

### 4. Résumé XSS (si le skill react-security-review n'est pas disponible)

Next.js hérite intégralement du modèle de sécurité XSS de React : le binding JSX (`{}`) encode automatiquement, mais `dangerouslySetInnerHTML` sans sanitization (DOMPurify), les URLs `javascript:` non validées dans `href`/`src`, et l'accès direct au DOM via des refs restent les trois sinks à surveiller en priorité. Si le skill react-security-review est installé, utilise ses références pour le détail complet (contextes d'encodage, SSR/hydration, défense en profondeur) plutôt que de réexpliquer depuis zéro.

### 5. Qualifier chaque trouvaille

Comme pour toute revue de sécurité : une donnée sensible dans un sink dangereux n'est une vulnérabilité confirmée que si elle est réellement atteignable avec une entrée non fiable. Un `dangerouslySetInnerHTML` alimenté par une constante codée en dur est un pattern à surveiller, pas une vulnérabilité active — nuance en conséquence.

### 6. Produire un rapport structuré

Même format que pour une revue React classique :

```
### [Sévérité] Titre court de la vulnérabilité

**Où** : chemin du fichier / nom du composant ou de l'action / numéro de ligne si connu
**Catégorie** : ex. "Exposition de données RSC" ou "A01 — Broken Access Control" (OWASP Top 10:2025)
**Le problème** : explique en 1-2 phrases le mécanisme concret d'exploitation
**Exploitation possible** : exemple bref et concret
**Correctif recommandé** : le pattern sûr à utiliser à la place, avec extrait de code si utile
**Référence** : lien vers la source pertinente (voir references/sources.md)
```

Sévérités : **Critique** (RCE, exécution de code, exposition massive de données ou de secrets, contournement d'authentification complet), **Élevée** (IDOR confirmé, exposition de données privées ciblée), **Moyenne** (pattern risqué à exploitabilité incertaine, absence de rate limiting), **Faible** (défense en profondeur manquante, en-tête de sécurité absent).

Termine par un résumé en une phrase du niveau de risque global, et rappelle que cette revue est un premier passage assisté, pas un audit de sécurité formel — recommande un test de pénétration pour toute application exposée publiquement avec des données sensibles.

### 7. Si l'utilisateur écrit du nouveau code plutôt que d'en faire relire

Applique directement les patterns sûrs des fichiers de référence en écrivant le code (Data Access Layer dès le départ pour un nouveau projet, validation + revalidation d'auth systématique dans chaque Server Action, matcher de middleware couvrant explicitement route racine et sous-routes). Explique brièvement en une phrase le choix fait, sans transformer la demande en cours de sécurité complet.

## Références disponibles

- `references/data-exposure-rsc.md` — les trois modèles d'accès aux données, le pattern d'exposition accidentelle via props, le Data Access Layer, le tainting, les variables d'environnement, la checklist d'audit `"use client"`/`"use server"` officielle.
- `references/server-actions-security.md` — ce qu'une Server Action doit vérifier (arguments, auth, autorisation/IDOR, valeur de retour), closures et chiffrement, CSRF natif vs `route.ts` manuel, rate limiting.
- `references/known-cves-and-middleware.md` — détail de CVE-2025-55182/CVE-2025-66478 (RCE critique RSC) et CVE-2025-29927/CVE-2024-51479 (bypass middleware), avec versions affectées/corrigées et la leçon architecturale à en tirer.
- `references/nodejs-hardening.md` — en-têtes de sécurité, cookies, secrets, rate limiting, fonctions dangereuses côté Node, gestion des erreurs en production.
- `references/sources.md` — sources à citer dans un rapport, jamais de citation verbatim longue.

## Limites à garder en tête

Ce skill couvre le code Next.js (App Router en priorité, avec quelques éléments Pages Router/middleware/Node.js applicables aux deux). Pour le détail complet du XSS côté rendu React et le mapping OWASP Top 10 généraliste, le skill react-security-review va plus loin — installe-le en complément si l'utilisateur fait des revues fréquentes. Ce skill ne remplace pas non plus une revue de l'infrastructure de déploiement (configuration du reverse proxy, du WAF, du provider cloud) — signale ces sujets s'ils apparaissent mais oriente vers une expertise dédiée plutôt que d'improviser.