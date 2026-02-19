# Color Systems Reference

## Palette Generation Method

Given a single brand hex, generate a full system:

1. Convert to HSL.
2. **50–100**: Keep hue, reduce saturation 10–20%, push lightness to 95–98%.
3. **200–300**: Keep hue, saturation ±5%, lightness 75–85%.
4. **400–500**: Base color zone. 500 = the provided brand color.
5. **600–700**: Keep hue, increase saturation 5–10%, reduce lightness to 35–45%.
6. **800–900**: Keep hue, reduce saturation 10%, lightness 15–25%.
7. **Neutral track**: Take brand hue, drop saturation to 5–10%, generate 50–900 lightness ramp.

## Curated Color Stories

### 1. Warm Minimal (Default)

Mood: Calm, approachable, editorial.

```
bg:          #FAFAF9
surface:     #FFFFFF
border:      #E7E5E4
text:        #1C1917
text-muted:  #78716C
accent:      #3B82F6
accent-hover:#2563EB
```

### 2. Cool Slate

Mood: Professional, tech-forward, precise.

```
bg:          #F8FAFC
surface:     #FFFFFF
border:      #E2E8F0
text:        #0F172A
text-muted:  #64748B
accent:      #6366F1
accent-hover:#4F46E5
```

### 3. Forest & Earth

Mood: Organic, sustainable, grounded.

```
bg:          #FAFDF7
surface:     #FFFFFF
border:      #D9E8C8
text:        #1A2E05
text-muted:  #5C7A3A
accent:      #16A34A
accent-hover:#15803D
```

### 4. Midnight Luxe (Dark Theme)

Mood: Premium, immersive, sophisticated.

```
bg:          #09090B
surface:     #18181B
border:      #27272A
text:        #FAFAFA
text-muted:  #A1A1AA
accent:      #A78BFA
accent-hover:#8B5CF6
```

### 5. Soft Rose

Mood: Friendly, warm, personal.

```
bg:          #FFFBFB
surface:     #FFFFFF
border:      #FECDD3
text:        #1C1917
text-muted:  #9E7B7B
accent:      #E11D48
accent-hover:#BE123C
```

### 6. Ocean Depth

Mood: Trustworthy, calm, institutional.

```
bg:          #F0F9FF
surface:     #FFFFFF
border:      #BAE6FD
text:        #0C4A6E
text-muted:  #0369A1
accent:      #0284C7
accent-hover:#0369A1
```

## Dark Mode Derivation

For any light palette, derive dark mode:

| Light Token | Dark Mapping |
|------------|--------------|
| `bg` | neutral-900 or darker |
| `surface` | neutral-800 |
| `border` | neutral-700 with 50% opacity |
| `text` | neutral-50 |
| `text-muted` | neutral-400 |
| `accent` | Increase lightness +10–15% for contrast |

## Contrast Validation

Before finalizing any palette, verify:

- Body text on bg: ≥ 4.5:1
- Large text (≥18px bold or ≥24px) on bg: ≥ 3:1
- Interactive elements on bg: ≥ 3:1
- Accent on surface: ≥ 4.5:1 for text use, ≥ 3:1 for decorative

Tools: Use `contrast-ratio` formula `(L1 + 0.05) / (L2 + 0.05)` where L = relative luminance.

## Gradient Recipes

### Subtle Background Mesh
```css
background: radial-gradient(at 20% 80%, hsla(210, 40%, 95%, 0.8) 0%, transparent 50%),
            radial-gradient(at 80% 20%, hsla(260, 40%, 95%, 0.6) 0%, transparent 50%),
            hsl(0, 0%, 99%);
```

### Accent Gradient (Buttons/CTAs)
```css
background: linear-gradient(135deg, var(--primary-500) 0%, var(--primary-600) 100%);
```

### Glass Overlay
```css
background: hsla(0, 0%, 100%, 0.6);
backdrop-filter: blur(16px) saturate(180%);
border: 1px solid hsla(0, 0%, 100%, 0.3);
```
