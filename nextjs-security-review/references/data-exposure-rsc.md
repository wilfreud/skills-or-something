# Exposition de données via React Server Components — référence détaillée

Basé sur la documentation officielle Next.js ("How to think about data security in Next.js" et "How to Think About Security in Next.js"). C'est le risque le plus spécifique et le plus fréquent dans une app Next.js App Router — pas un bug exotique, mais une conséquence directe du modèle RSC.

## Pourquoi ce risque existe

Les Server Components et les Client Components s'exécutent dans deux systèmes de modules isolés, mais au premier chargement ils tournent tous les deux sur le serveur pour produire le HTML. Cette isolation protège en théorie les données privées : un Server Component peut accéder à la base de données, aux secrets, aux API internes ; un Client Component doit être traité comme s'il tournait déjà dans le navigateur — parce qu'il finira par y tourner. Le problème apparaît quand un Server Component **passe** des données à un Client Component en props : tout ce qui transite dans ces props est sérialisé et envoyé au client, qu'il soit affiché ou non.

## Choisir un modèle d'accès aux données (et vérifier lequel est utilisé)

Avant d'auditer le détail, identifie quelle approche le projet utilise — Next.js recommande de ne pas les mélanger, donc un mélange des trois est en soi un signal à relever :

1. **API HTTP externes** — le Server Component appelle une API REST/GraphQL existante via `fetch`, exactement comme le ferait un Client Component. Adapté aux projets existants avec une équipe backend séparée. Le modèle de sécurité "Zero Trust" s'applique : aucune confiance accordée du seul fait que l'appel vient du serveur.
2. **Data Access Layer (DAL)** — recommandé pour les nouveaux projets. Une librairie interne, marquée `import 'server-only'`, qui centralise l'accès aux données, effectue les vérifications d'autorisation, et ne retourne que des **Data Transfer Objects (DTO)** minimaux — jamais l'enregistrement brut de la base de données.
3. **Accès direct dans le composant** — requêtes DB écrites directement dans un Server Component. Acceptable pour un prototype, dangereux à grande échelle car rien n'empêche de passer l'objet entier (mot de passe hashé, tokens, champs internes inclus) à un Client Component enfant.

## Le pattern dangereux à repérer en priorité

```tsx
// Server Component
const [rows] = await sql`SELECT * FROM user WHERE slug = ${slug}`;
const userData = rows[0];
// EXPOSÉ : tous les champs de userData partent au client, y compris
// ceux que le composant enfant n'affiche pas.
return <Profile user={userData} />;
```

Le composant `Profile` (`"use client"`) n'a peut-être besoin que du `name`, mais si sa signature de props accepte l'objet `User` complet, rien n'empêche le Server Component appelant de lui passer plus que nécessaire — et cette sur-exposition passe facilement inaperçue en revue de code parce que rien ne "casse" visuellement.

**Correctif** : ne retourner que les champs publics depuis la fonction de données, et donner au composant client une interface de props volontairement étroite plutôt que d'accepter un type large comme `User`.

## Ce qu'il faut vérifier dans les fichiers `"use client"`

- Les props acceptées sont-elles un objet large (`user: User`, `team: Team`) plutôt qu'une interface minimale avec seulement les champs affichés ?
- Y a-t-il des champs sensibles même indirectement présents — `token`, `passwordHash`, `email` si non affiché, `creditCard`, `internalNotes` ? Signale-les même s'ils ne sont pas rendus visuellement : une fois envoyés au client, ils sont visibles dans les DevTools/le payload RSC quel que soit l'usage qu'en fait le JSX.

## Ce qu'il faut vérifier dans le Data Access Layer / les fonctions de données

- Le module est-il marqué `import 'server-only'` ? Si non, rien n'empêche un import accidentel depuis un fichier client, ce qui casserait le build seulement si Next.js le détecte — ne pas compter dessus comme seule protection, le marquage explicite est la vraie garde-fou.
- `process.env` (accès aux secrets) est-il utilisé uniquement dans cette couche, ou dispersé dans des composants ?
- Les requêtes utilisent-elles des requêtes paramétrées (template literal `sql\`...\`` avec une librairie qui échappe, ou un ORM) plutôt que de la concaténation de chaînes ? Sinon, c'est une injection SQL classique (voir A05 dans le mapping OWASP Top 10 du skill react-security-review).

## Tainting (defense in depth, pas une solution à elle seule)

Next.js expose les Taint APIs de React (`experimental_taintObjectReference`, `experimental_taintUniqueValue`), activables via `experimental.taint` dans `next.config.js`. Elles empêchent un objet ou une valeur unique marquée d'être transmise telle quelle à un Client Component, et font planter le build si ça arrive.

Limites importantes à signaler si tu vois du code qui s'appuie uniquement sur le tainting :

- Ça ne bloque pas l'extraction de champs individuels d'un objet tainté (`const { name, phone } = taintedUser` puis passer `phone` séparément continue de fonctionner).
- Ça ne protège pas les valeurs dérivées.
- C'est une couche de sécurité supplémentaire contre les erreurs humaines, pas un substitut au Data Access Layer qui filtre les données à la source.

## Variables d'environnement

- Par défaut, les variables d'environnement ne sont disponibles que côté serveur.
- Toute variable préfixée `NEXT_PUBLIC_` est automatiquement exposée au bundle client — un secret accidentellement préfixé ainsi (`NEXT_PUBLIC_STRIPE_SECRET_KEY` par exemple) est immédiatement lisible par n'importe qui.
- Signale toute variable sensible (clé API, secret, credential DB) qui n'est PAS préfixée `NEXT_PUBLIC_` mais qui est quand même référencée dans un fichier `"use client"` — le build devrait échouer si elle passe par un module `server-only`, mais un accès direct à `process.env.MA_CLE` dans un composant client est une fuite immédiate même sans ce garde-fou.

## Lecture de données (searchParams, params, headers)

Les entrées de l'URL (`searchParams`, `params` dynamiques entre crochets, `headers()`) sont fournies par le client et donc non fiables — elles doivent être revérifiées à chaque lecture, jamais utilisées directement pour une décision d'autorisation.

```tsx
// MAUVAIS : fait confiance à searchParams pour une décision de sécurité
export default async function Page({ searchParams }) {
  const isAdmin = (await searchParams).isAdmin;
  if (isAdmin === 'true') {
    return <AdminPanel />; // Vulnérable : dépend d'une donnée non fiable
  }
}

// BON : revérifie systématiquement via une source de confiance (session/cookie signé)
import { cookies } from 'next/headers';
export default async function Page() {
  const cookieStore = await cookies();
  const isAdmin = await verifyAdmin(cookieStore.get('AUTH_TOKEN'));
  if (isAdmin) return <AdminPanel />;
}
```

Un rendu de Server Component ne doit par ailleurs jamais produire d'effet de bord (mutation, suppression de cookie) — Next.js empêche structurellement de poser un cookie ou de revalider un cache pendant le rendu, précisément pour éviter que des GET/navigations aient des effets de mutation exploitables.

## Checklist rapide pour l'audit "use client" / "use server"

Reprends systématiquement, comme le recommande la documentation officielle :

- **Data Access Layer** : pratique établie et isolée ? Les packages DB et `process.env` ne sont-ils importés que là ?
- **Fichiers `"use client"`** : les props attendent-elles des données privées ? Les signatures de types sont-elles trop larges ?
- **Dossiers `[param]`** : ce sont des entrées utilisateur — sont-elles validées avant usage ?
