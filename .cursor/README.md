# Cursor Configuration

This directory contains configuration files for Cursor AI assistance.

## Directory Structure

- `rules/` - Contains rule files (`.mdc` format) that provide persistent context to the AI agent

## Rules Directory

Rules are `.mdc` files with YAML frontmatter that help guide the AI agent's behavior:

- **Always-apply rules**: Apply to every conversation (set `alwaysApply: true`)
- **File-specific rules**: Apply when working with specific file patterns (use `globs` field)

### Example Rule Structure

```markdown
---
description: Brief description of what this rule does
globs: **/*.ts  # File pattern for file-specific rules
alwaysApply: false  # Set to true if rule should always apply
---

# Rule Title

Your rule content here...
```

### Creating Rules

You can create rules by:
1. Manually creating `.mdc` files in the `rules/` directory
2. Asking the AI agent to create rules for you
3. Using the create-rule skill

For more information, ask the AI agent about creating Cursor rules.

## Skills Directory

Skills are reusable agent capabilities stored as `SKILL.md` files in `skills/`:

| Skill | Purpose |
|-------|---------|
| `ui-design-expert` | Cross-platform UI/UX design, color systems, trending components |
| `api-design` | REST/GraphQL contract design for web + mobile clients |
| `web-frontend-architecture` | React/Next.js project structure, patterns, and best practices |

## Potential Enhancements

Skills that would further strengthen a web + mobile companion project:

### Auth Flows (`auth-flows`)
Cross-platform authentication: JWT lifecycle, refresh token rotation, OAuth/social login, secure storage per platform (httpOnly cookies for web, Keychain for iOS, EncryptedSharedPreferences for Android), and session management patterns.

### Project Scaffolding (`project-scaffolding`)
Monorepo or polyrepo structure decisions, shared TypeScript types between web and API, Xcode project setup, environment configuration (`.env` per target), and CI/CD pipeline templates. Best used once at project kickoff.

### Accessibility Audit (`accessibility-audit`)
Dedicated skill for auditing screens against WCAG 2.2 AA: semantic HTML, ARIA roles, VoiceOver/TalkBack labels, dynamic type, reduced motion, focus management, and color contrast verification.

### Responsive Layout (`responsive-layout`)
Deep patterns for layouts that adapt across phone, tablet, and desktop: adaptive navigation (tab bar to sidebar), responsive grids, container queries, and breakpoint-driven component variants.

### Real-Time Sync (`real-time-sync`)
For apps with live data needs (chat, notifications, collaborative editing): WebSocket/SSE patterns, optimistic updates, conflict resolution, offline queue, and reconnection strategies.
