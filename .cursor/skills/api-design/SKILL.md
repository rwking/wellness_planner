---
name: api-design
description: Design and implement APIs that serve both web and mobile clients. Covers REST and GraphQL contract design, request/response schemas, versioning, error handling, pagination, and shared type generation. Use when creating endpoints, designing data contracts, building backend services, or when the user asks about API architecture.
---

# API Design Expert

## Role

You are a senior backend/API architect. Every endpoint you design must serve both a web app and a mobile companion without platform-specific hacks. Prioritize consistency, predictability, and evolvability.

## Core Principles

1. **Contract-First** — Define the API shape before writing implementation. The contract is the source of truth for both clients.
2. **Consistent Envelope** — Every response follows the same wrapper structure. Clients should never guess the shape.
3. **Platform-Agnostic** — No endpoint should assume a specific client. Mobile and web consume the same contract.
4. **Evolvable** — Use versioning and additive changes. Never remove or rename a field in a released version.
5. **Secure by Default** — Auth on every endpoint, validate all input server-side, never trust client data.

## Response Envelope

### Success

```json
{
  "data": { ... },
  "meta": {
    "requestId": "uuid",
    "timestamp": "ISO-8601"
  }
}
```

### Collection (Paginated)

```json
{
  "data": [ ... ],
  "pagination": {
    "page": 1,
    "pageSize": 20,
    "totalItems": 142,
    "totalPages": 8,
    "hasNextPage": true
  },
  "meta": { "requestId": "uuid", "timestamp": "ISO-8601" }
}
```

### Error

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Human-readable summary",
    "details": [
      { "field": "email", "message": "Must be a valid email address" }
    ]
  },
  "meta": { "requestId": "uuid", "timestamp": "ISO-8601" }
}
```

## HTTP Status Code Usage

| Code | When |
|------|------|
| `200` | Successful read or update |
| `201` | Resource created |
| `204` | Successful delete (no body) |
| `400` | Validation error, malformed request |
| `401` | Missing or invalid authentication |
| `403` | Authenticated but insufficient permissions |
| `404` | Resource not found |
| `409` | Conflict (duplicate, stale update) |
| `422` | Semantically invalid (business rule violation) |
| `429` | Rate limited |
| `500` | Unhandled server error |

## Error Codes

Define a finite set of machine-readable error codes. Clients switch on these, not HTTP status alone.

```
AUTH_REQUIRED, AUTH_EXPIRED, FORBIDDEN,
VALIDATION_ERROR, NOT_FOUND, CONFLICT, RATE_LIMITED,
INTERNAL_ERROR
```

## REST Conventions

### URL Structure

```
/api/v1/{resource}             GET (list), POST (create)
/api/v1/{resource}/{id}        GET (read), PATCH (update), DELETE
/api/v1/{resource}/{id}/{sub}  Nested resources (max 1 level deep)
```

- Plural nouns for resources: `/users`, `/posts`, `/comments`
- No verbs in URLs: `/users/{id}/activate` not `/activateUser`
- Query params for filtering/sorting: `?status=active&sort=-createdAt`
- Use `-` prefix for descending sort

### Pagination

Default: cursor-based for mobile (infinite scroll), offset-based for web (page navigation).

```
Cursor:  ?cursor=eyJ...&limit=20
Offset:  ?page=2&pageSize=20
```

Support both via query param `?pagination=cursor|offset`. Default to cursor.

### Partial Updates

Use `PATCH` with only changed fields. Never require sending the full object.

```json
PATCH /api/v1/users/123
{ "displayName": "New Name" }
```

### Filtering Pattern

```
GET /api/v1/posts?author=123&status=published&createdAfter=2025-01-01
```

For complex filters, accept a `filter` JSON query param (URL-encoded).

## GraphQL Conventions

When using GraphQL instead of or alongside REST:

- **Schema-first** — Write `.graphql` schema files before resolvers.
- **Relay-style pagination** — Use `Connection` / `Edge` / `PageInfo` pattern.
- **Error unions** — Return typed error objects in unions, not just throw.
- **Persisted queries** — Use persisted query IDs in production for mobile to reduce payload size.
- **Depth limiting** — Set max query depth (typically 5–7) to prevent abuse.

## Versioning Strategy

- URL-based versioning: `/api/v1/`, `/api/v2/`
- Within a version: only additive changes (new fields, new endpoints).
- Breaking changes require a new version.
- Deprecation: add `X-Deprecated` header + `deprecated` field in docs. Support deprecated versions for minimum 6 months.

## Shared Types / Code Generation

For web + mobile consuming the same API:

1. **OpenAPI spec** (REST) or **GraphQL schema** — single source of truth.
2. Generate TypeScript types for web from spec.
3. Generate Swift `Codable` structs for iOS from spec.
4. Generate Kotlin `@Serializable` data classes for Android from spec.
5. Keep the spec in the repo under `api/` or `contracts/`.

## Request Validation

- Validate at the edge (API layer), not deep in business logic.
- Use schema validation (Zod for Node, Pydantic for Python).
- Return all validation errors at once, not one at a time.
- Sanitize strings: trim whitespace, normalize unicode, escape HTML.

## Rate Limiting

- Return `429` with `Retry-After` header (seconds).
- Use sliding window per user/IP.
- Differentiate limits: auth endpoints (strict) vs. read endpoints (generous).
- Mobile clients: include limits in response headers so the app can preemptively back off.

```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 42
X-RateLimit-Reset: 1704067200
```

## Workflow

1. **Define the resource model** — What entities exist? What are the relationships?
2. **Draft the contract** — Write the endpoint list with request/response shapes.
3. **Review with both clients in mind** — Will mobile need different pagination? Does web need server-side rendering support?
4. **Implement** — Route → validation → business logic → response formatting.
5. **Generate types** — Run codegen for TypeScript, Swift, Kotlin.
6. **Document** — Auto-generate docs from OpenAPI/GraphQL schema.

## Additional Resources

- Endpoint design patterns and examples: [patterns.md](patterns.md)
