# Sécurité des Server Actions — référence détaillée

Basé sur la documentation officielle Next.js. Les Server Actions (`"use server"`) sont le mécanisme idiomatique pour les mutations en App Router, mais leur nature même — un point d'entrée public invocable indépendamment de l'UI — en fait une surface d'attaque qu'il faut auditer systématiquement.

## Le principe qui change tout

Dès qu'une fonction est exportée avec `"use server"`, elle devient joignable par une requête POST directe, **même si elle n'est appelée nulle part ailleurs dans le code visible**. Une Server Action doit être traitée exactement comme un endpoint d'API public — parce que c'en est un.

## Protections intégrées par Next.js (défense en profondeur, pas une autorisation)

- **IDs d'action sécurisés** : Next.js génère des identifiants chiffrés et non déterministes pour référencer chaque action, recalculés périodiquement entre les builds.
- **Élimination de code mort** : une Server Action jamais référencée dans le code est retirée du bundle client au build — elle ne devient donc pas un endpoint public accessible.

**Ce que ça ne fait PAS** : ces deux mécanismes réduisent le risque quand une couche d'authentification manque par erreur, mais ils ne remplacent jamais une vérification explicite. Toute Server Action doit être traitée comme atteignable directement, et vérifier elle-même qui l'appelle.

## Ce qu'une Server Action doit systématiquement faire, dans l'ordre

1. **Valider l'intégrité des arguments** — les annotations TypeScript ne sont pas appliquées à l'exécution ; un attaquant peut envoyer n'importe quel type. Utiliser une validation explicite (manuelle ou via `zod`/`valibot`) sur chaque argument avant de l'utiliser.
2. **Re-vérifier l'authentification** — une vérification faite au niveau de la page (`await auth()` dans le composant parent) ne s'étend PAS automatiquement à la Server Action définie dans cette page. C'est un point d'entrée séparé.
3. **Vérifier l'autorisation, pas seulement l'authentification** — être connecté ne suffit pas ; il faut vérifier que l'utilisateur a le droit d'agir sur _cette ressource précise_ (propriété de l'enregistrement, rôle adéquat). Sans ça, c'est une IDOR (Insecure Direct Object Reference) classique.

```tsx
// MAUVAIS : le composant parent vérifie l'admin, mais l'action ne revérifie rien
export default async function AdminPage() {
  const session = await auth();
  if (!session?.user?.isAdmin) redirect('/login');

  return (
    <form
      action={async () => {
        'use server';
        await db.record.deleteMany(); // Aucune vérification ici !
      }}
    >
      <button>Supprimer</button>
    </form>
  );
}

// BON : l'action revérifie indépendamment de la page qui l'entoure
async function deleteRecords() {
  'use server';
  const session = await auth();
  if (!session?.user?.isAdmin) throw new Error('Unauthorized');
  await db.record.deleteMany();
}
```

4. **Vérifier la propriété de la ressource (IDOR)** — pas seulement "est admin" mais "possède cet enregistrement précis" :

```tsx
export async function deletePost(postId: string) {
  'use server';
  const session = await auth();
  if (!session?.user) throw new Error('Unauthorized');

  const post = await db.post.findUnique({ where: { id: postId } });
  if (post.authorId !== session.user.id) throw new Error('Forbidden'); // vérif de propriété

  await db.post.delete({ where: { id: postId } });
}
```

5. **Ne retourner que ce dont le client a besoin** — une valeur de retour de Server Action est sérialisée et envoyée au client. Retourner l'enregistrement complet de la base (`return db.user.update(...)`) expose potentiellement des champs internes ; retourner un objet minimal (`return { success: true }`) évite le problème.

## Où mettre cette logique : action fine + DAL

Le pattern recommandé consiste à garder la logique d'auth/autorisation/DB dans le Data Access Layer (`server-only`), et à ne laisser dans la fonction `"use server"` que l'appel à cette couche plus la revalidation du cache. Ça garde les fichiers `"use server"` "fins" et centralise ce qui doit être audité en un seul endroit — voir `references/data-exposure-rsc.md` pour le détail du DAL.

## Fermetures (closures) et chiffrement

Une Server Action définie à l'intérieur d'un composant peut capturer des variables de la portée englobante (closure) — utile pour figer un instantané de données au moment du rendu. Ces variables capturées transitent vers le client puis reviennent au serveur lors de l'invocation ; Next.js les chiffre automatiquement avec une clé privée régénérée à chaque build.

- Ne compte pas sur ce chiffrement comme unique protection contre l'exposition de données sensibles dans une closure — c'est une couche supplémentaire, pas une garantie absolue documentée comme telle par Next.js lui-même.
- Alternative : `.bind(...)` pour lier un argument à une action — **ces valeurs ne sont PAS chiffrées**. Si tu vois un `.bind()` avec une donnée sensible (id interne suffisant à lui seul pour une action destructive sans revérification), signale-le.
- En auto-hébergement multi-serveurs, la clé de chiffrement doit être fixée via `NEXT_SERVER_ACTIONS_ENCRYPTION_KEY` pour rester cohérente entre instances — une clé qui varie entre serveurs peut casser silencieusement des actions en vol lors d'un déploiement.

## CSRF : ce qui est protégé nativement, ce qui ne l'est pas

- Les Server Actions n'utilisent que la méthode POST, ce qui élimine la plupart des CSRF classiques sur navigateur moderne, renforcé par les cookies `SameSite` par défaut.
- Protection additionnelle : Next.js compare l'en-tête `Origin` à l'en-tête `Host` (ou `X-Forwarded-Host`) et rejette la requête en cas de désaccord — une Server Action n'est donc invocable que depuis le même host que la page qui l'héberge.
- **Cas à vérifier en revue** : une architecture avec reverse proxy ou domaine API différent du domaine de production nécessite de configurer explicitement `experimental.serverActions.allowedOrigins` dans `next.config.js`. Une configuration trop permissive ici (wildcard large, origine de test laissée en prod) réintroduit un risque CSRF.
- Les Server Actions n'utilisent pas de token CSRF traditionnel — la sanitization HTML reste donc essentielle en complément (voir XSS dans le SKILL.md principal).
- **Les Route Handlers custom (`route.ts`) n'ont AUCUNE de ces protections automatiques.** S'ils implémentent un GET ou POST personnalisé, le CSRF doit être géré manuellement selon les techniques traditionnelles (token, vérification d'origine). Traite tout `route.ts` qui accepte une méthode mutative comme nécessitant un audit CSRF classique.

## Effets de bord pendant le rendu

Une mutation (déconnexion, écriture DB, invalidation de cache) ne doit jamais être déclenchée comme effet de bord du rendu d'une page — ni côté Server Component ni côté Client Component. Next.js empêche structurellement de poser un cookie ou de déclencher une revalidation de cache pendant le rendu ; si tu vois du code qui contourne ça (mutation basée sur la simple présence d'un `searchParams`), c'est un anti-pattern à signaler même si le contournement technique réussit — parce que ça réintroduit le risque qu'une simple requête GET (facilement forgeable, préchargée par le navigateur, indexée par un crawler) déclenche une action sensible.

## Rate limiting

Pour toute Server Action coûteuse (envoi d'email, écriture DB, appel à une API tierce payante), vérifie qu'une forme de limitation de fréquence existe. Son absence n'est pas une vulnérabilité au sens strict mais ouvre la porte à l'abus/déni de service applicatif — à signaler en sévérité Faible/Moyenne selon le contexte.
