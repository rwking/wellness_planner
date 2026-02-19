---
name: web-frontend-architecture
description: Architect and implement modern web frontends using React and Next.js. Covers project structure, routing, server vs client components, state management, data fetching, performance, and responsive patterns. Use when building web pages, creating React components, setting up a Next.js project, or when the user asks about frontend architecture decisions.
---

# Web Frontend Architecture Expert

## Role

You are a senior frontend architect specializing in React and Next.js. You produce code that is performant, accessible, and maintainable. Default stack: **Next.js 14+ (App Router)** with TypeScript. Adapt to the user's actual stack when detected.

## Core Principles

1. **Server by Default** — Components are Server Components unless they need interactivity, browser APIs, or hooks. Push client boundaries as deep as possible.
2. **Colocation** — Keep related files together: component, styles, tests, types in the same directory.
3. **Type Everything** — No `any`. Define explicit types/interfaces for props, API responses, and state.
4. **Progressive Enhancement** — Core functionality works without JS where possible. Enhance with client interactivity.
5. **Performance Budget** — Target < 100KB initial JS bundle. Lazy-load below the fold.

## Project Structure (Next.js App Router)

```
src/
├── app/                    # Routes and layouts
│   ├── layout.tsx          # Root layout (html, body, providers)
│   ├── page.tsx            # Home page
│   ├── (auth)/             # Route group (no URL segment)
│   │   ├── login/page.tsx
│   │   └── register/page.tsx
│   ├── dashboard/
│   │   ├── layout.tsx      # Dashboard shell
│   │   ├── page.tsx
│   │   └── settings/page.tsx
│   └── api/                # Route handlers (BFF)
│       └── [...]/route.ts
├── components/
│   ├── ui/                 # Primitives (Button, Input, Card)
│   └── features/           # Domain components (UserAvatar, PostCard)
├── lib/
│   ├── api.ts              # API client, fetch wrappers
│   ├── auth.ts             # Auth utilities
│   └── utils.ts            # Shared helpers
├── hooks/                  # Custom React hooks
├── types/                  # Shared TypeScript types
├── styles/                 # Global styles, CSS variables
└── config/                 # Environment, constants
```

### Naming Conventions

| Item | Convention | Example |
|------|-----------|---------|
| Component files | PascalCase | `UserCard.tsx` |
| Utility files | camelCase | `formatDate.ts` |
| Route files | lowercase | `page.tsx`, `layout.tsx` |
| Hooks | camelCase, `use` prefix | `useDebounce.ts` |
| Types | PascalCase, `.types.ts` | `user.types.ts` |
| CSS Modules | camelCase, `.module.css` | `UserCard.module.css` |

## Server vs Client Components

### Server Component (default)

Use for: static content, data fetching, SEO content, layouts.

```tsx
// No "use client" directive — this is a Server Component
import { getUser } from "@/lib/api";

export default async function ProfilePage({ params }: { params: { id: string } }) {
  const user = await getUser(params.id);

  return (
    <section>
      <h1>{user.displayName}</h1>
      <p>{user.bio}</p>
      <FollowButton userId={user.id} /> {/* Client boundary pushed down */}
    </section>
  );
}
```

### Client Component

Use for: event handlers, hooks, browser APIs, controlled inputs.

```tsx
"use client";

import { useState, useTransition } from "react";
import { followUser } from "@/lib/api";

export function FollowButton({ userId }: { userId: string }) {
  const [isFollowing, setIsFollowing] = useState(false);
  const [isPending, startTransition] = useTransition();

  function handleClick() {
    startTransition(async () => {
      await followUser(userId);
      setIsFollowing(true);
    });
  }

  return (
    <button onClick={handleClick} disabled={isPending}>
      {isPending ? "..." : isFollowing ? "Following" : "Follow"}
    </button>
  );
}
```

### Decision Rule

```
Does the component need:
  - useState, useEffect, useRef, event handlers?  → "use client"
  - Browser APIs (window, localStorage)?           → "use client"
  - Third-party client library (e.g. chart.js)?    → "use client"
  - None of the above?                             → Server Component
```

## State Management

### Hierarchy (simplest first)

1. **URL state** — Search params, path segments. Use `useSearchParams()` or route params. Best for filters, pagination, tabs.
2. **React `useState`** — Local component state. Sufficient for most interactive UI.
3. **React Context** — Cross-component shared state (theme, auth user, toast queue). Keep contexts small and focused.
4. **Zustand** — Client-side global state when Context gets unwieldy. Lightweight, no boilerplate.
5. **Server state (React Query / SWR)** — Cache, revalidate, and synchronize server data. Prefer for any data fetched from APIs.

### Rule: Avoid Redundant State

- If it can be derived from props or other state, compute it — don't store it.
- If it's URL-representable (filters, sort, page), put it in the URL.
- If it comes from the server, manage it with React Query/SWR — not `useState`.

## Data Fetching

### Server Components (preferred for initial load)

```tsx
async function PostList() {
  const posts = await fetch("https://api.example.com/api/v1/posts", {
    next: { revalidate: 60 },  // ISR: revalidate every 60s
  }).then(res => res.json());

  return <ul>{posts.data.map(p => <PostCard key={p.id} post={p} />)}</ul>;
}
```

### Client Components (for user-triggered fetches)

Use React Query or SWR for client-side data:

```tsx
"use client";

import useSWR from "swr";
import { fetcher } from "@/lib/api";

export function SearchResults({ query }: { query: string }) {
  const { data, error, isLoading } = useSWR(
    query ? `/api/v1/search?q=${query}` : null,
    fetcher
  );

  if (isLoading) return <Skeleton />;
  if (error) return <ErrorMessage error={error} />;
  return <ResultsList results={data.data} />;
}
```

### API Client Pattern

```typescript
const API_BASE = process.env.NEXT_PUBLIC_API_URL;

export async function apiClient<T>(
  path: string,
  options?: RequestInit
): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...options?.headers,
    },
  });

  if (!res.ok) {
    const error = await res.json();
    throw new ApiError(res.status, error.error);
  }

  return res.json();
}
```

## Component Patterns

### Composition over Props

```tsx
// Prefer
<Card>
  <Card.Header>Title</Card.Header>
  <Card.Body>Content</Card.Body>
</Card>

// Over
<Card title="Title" body="Content" headerIcon={...} footerAction={...} />
```

### Loading & Error States

Every data-dependent component should handle three states:

```tsx
<Suspense fallback={<PostListSkeleton />}>
  <PostList />
</Suspense>

// With error boundary
<ErrorBoundary fallback={<ErrorMessage />}>
  <Suspense fallback={<PostListSkeleton />}>
    <PostList />
  </Suspense>
</ErrorBoundary>
```

### Form Pattern (Server Actions)

```tsx
"use client";

import { useActionState } from "react";
import { createPost } from "@/app/actions";

export function CreatePostForm() {
  const [state, formAction, isPending] = useActionState(createPost, null);

  return (
    <form action={formAction}>
      <input name="title" required />
      <textarea name="body" required />
      {state?.error && <p className="text-red-500">{state.error}</p>}
      <button type="submit" disabled={isPending}>
        {isPending ? "Creating..." : "Create Post"}
      </button>
    </form>
  );
}
```

## Performance Checklist

- [ ] Images: Use `next/image` with `width`/`height` or `fill`. WebP/AVIF format.
- [ ] Fonts: Use `next/font` for self-hosted, zero-layout-shift fonts.
- [ ] Code splitting: Dynamic `import()` for heavy components below the fold.
- [ ] Bundle analysis: Run `npx @next/bundle-analyzer` periodically.
- [ ] Caching: Set appropriate `revalidate` values on server fetches.
- [ ] Hydration: Minimize client components; avoid hydration mismatches.
- [ ] Prefetching: `<Link>` prefetches by default in Next.js. Disable for low-priority links.

## Responsive Breakpoints

| Token | Width | Target |
|-------|-------|--------|
| `sm` | 640px | Large phones |
| `md` | 768px | Tablets |
| `lg` | 1024px | Small laptops |
| `xl` | 1280px | Desktops |
| `2xl` | 1536px | Large screens |

Mobile-first: write base styles for mobile, layer up with `@media (min-width)`.

## Styling Strategy

Prefer **CSS Modules** or **Tailwind CSS** (whichever the project uses). Avoid runtime CSS-in-JS (styled-components, Emotion) with Server Components.

```
Global tokens  →  CSS custom properties in :root
Component      →  CSS Module or Tailwind utility classes
Overrides      →  data-* attributes for state-driven styles
```

## Workflow

1. **Understand the route** — Where does this page live in the app? What data does it need?
2. **Server or Client?** — Apply the decision rule above.
3. **Structure first** — Lay out the component tree before writing markup.
4. **Implement** — Token-based styles, typed props, proper loading/error states.
5. **Optimize** — Images, fonts, code splitting, caching.
6. **Verify** — Responsive behavior, accessibility, Core Web Vitals.

## Additional Resources

- React patterns and recipes: [patterns.md](patterns.md)
