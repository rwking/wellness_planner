# API Endpoint Patterns

## CRUD Resource — Full Example

### Route Definition (Node/Express style)

```typescript
router.get("/api/v1/posts",           listPosts);
router.post("/api/v1/posts",          createPost);
router.get("/api/v1/posts/:id",       getPost);
router.patch("/api/v1/posts/:id",     updatePost);
router.delete("/api/v1/posts/:id",    deletePost);
router.get("/api/v1/posts/:id/comments", listPostComments);
```

### Request/Response Shapes

**Create Post**
```
POST /api/v1/posts
Authorization: Bearer <token>
Content-Type: application/json

{
  "title": "My Post",
  "body": "Content here...",
  "tags": ["swift", "api"]
}

→ 201
{
  "data": {
    "id": "post_abc123",
    "title": "My Post",
    "body": "Content here...",
    "tags": ["swift", "api"],
    "author": { "id": "user_xyz", "displayName": "Rich" },
    "createdAt": "2026-02-16T10:00:00Z",
    "updatedAt": "2026-02-16T10:00:00Z"
  },
  "meta": { "requestId": "req_001", "timestamp": "2026-02-16T10:00:00Z" }
}
```

**List Posts (Cursor Pagination)**
```
GET /api/v1/posts?limit=20&cursor=eyJ...&sort=-createdAt

→ 200
{
  "data": [ { ... }, { ... } ],
  "pagination": {
    "nextCursor": "eyJ...",
    "hasNextPage": true,
    "limit": 20
  },
  "meta": { ... }
}
```

**Validation Error**
```
POST /api/v1/posts
{ "title": "", "body": null }

→ 400
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Request validation failed",
    "details": [
      { "field": "title", "message": "Title is required and cannot be empty" },
      { "field": "body", "message": "Body is required" }
    ]
  },
  "meta": { ... }
}
```

## Authentication Endpoints

```
POST /api/v1/auth/register       — Create account
POST /api/v1/auth/login          — Get access + refresh tokens
POST /api/v1/auth/refresh        — Exchange refresh token for new access token
POST /api/v1/auth/logout         — Revoke refresh token
POST /api/v1/auth/forgot-password — Send reset email
POST /api/v1/auth/reset-password  — Set new password with reset token
```

### Token Response Shape
```json
{
  "data": {
    "accessToken": "eyJ...",
    "refreshToken": "eyJ...",
    "expiresIn": 900,
    "tokenType": "Bearer"
  }
}
```

## File Upload Pattern

Use multipart for uploads. Return a resource reference, not the file contents.

```
POST /api/v1/uploads
Content-Type: multipart/form-data

→ 201
{
  "data": {
    "id": "upload_abc",
    "url": "https://cdn.example.com/uploads/abc.jpg",
    "mimeType": "image/jpeg",
    "size": 204800,
    "createdAt": "2026-02-16T10:00:00Z"
  }
}
```

Then reference the upload ID when creating a resource:
```json
POST /api/v1/posts
{ "title": "Photo Post", "imageId": "upload_abc" }
```

## Search Pattern

```
GET /api/v1/search?q=swift+concurrency&type=posts,users&limit=10

→ 200
{
  "data": {
    "posts": [ { ... } ],
    "users": [ { ... } ]
  },
  "pagination": { ... },
  "meta": { ... }
}
```

## Bulk Operations

For batch create/update, accept an array and return per-item results:

```
POST /api/v1/posts/bulk
{
  "operations": [
    { "action": "create", "data": { "title": "Post 1", "body": "..." } },
    { "action": "update", "id": "post_abc", "data": { "title": "Updated" } }
  ]
}

→ 200
{
  "data": {
    "results": [
      { "status": "created", "id": "post_def" },
      { "status": "updated", "id": "post_abc" }
    ],
    "succeeded": 2,
    "failed": 0
  }
}
```

## Webhook Pattern

For event-driven integrations:

```
POST /api/v1/webhooks
{
  "url": "https://example.com/hooks",
  "events": ["post.created", "post.deleted"],
  "secret": "whsec_..."
}
```

Webhook payloads follow the same envelope:
```json
{
  "event": "post.created",
  "data": { ... },
  "meta": {
    "webhookId": "wh_abc",
    "deliveryId": "del_xyz",
    "timestamp": "2026-02-16T10:00:00Z"
  }
}
```

Sign payloads with HMAC-SHA256 using the webhook secret. Include signature in `X-Webhook-Signature` header.

## OpenAPI Spec Skeleton

```yaml
openapi: "3.1.0"
info:
  title: "My App API"
  version: "1.0.0"
servers:
  - url: https://api.example.com/api/v1

paths:
  /posts:
    get:
      summary: List posts
      parameters:
        - name: cursor
          in: query
          schema: { type: string }
        - name: limit
          in: query
          schema: { type: integer, default: 20, maximum: 100 }
      responses:
        "200":
          description: Paginated list of posts
          content:
            application/json:
              schema:
                $ref: "#/components/schemas/PostListResponse"

components:
  schemas:
    Post:
      type: object
      required: [id, title, body, createdAt]
      properties:
        id: { type: string }
        title: { type: string }
        body: { type: string }
        createdAt: { type: string, format: date-time }
        updatedAt: { type: string, format: date-time }
```
