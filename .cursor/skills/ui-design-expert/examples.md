# Component Examples

## Bento Grid — Web (React + Tailwind)

```jsx
function BentoGrid({ items }) {
  return (
    <div className="grid grid-cols-4 gap-4 auto-rows-[180px]">
      {items.map((item, i) => (
        <div
          key={i}
          className={`
            rounded-xl bg-white border border-neutral-200 p-6
            shadow-sm hover:shadow-md transition-shadow duration-200
            ${item.span === "wide" ? "col-span-2" : ""}
            ${item.span === "tall" ? "row-span-2" : ""}
            ${item.span === "feature" ? "col-span-2 row-span-2" : ""}
          `}
        >
          <h3 className="text-sm font-semibold text-neutral-900">{item.title}</h3>
          <p className="mt-1 text-xs text-neutral-500">{item.subtitle}</p>
        </div>
      ))}
    </div>
  );
}
```

## Card with Hover — Web (CSS)

```css
.card {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 12px;
  padding: 24px;
  transition: transform 200ms cubic-bezier(0.4, 0, 0.2, 1),
              box-shadow 200ms cubic-bezier(0.4, 0, 0.2, 1);
}

.card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
}
```

## Glassmorphism Card — SwiftUI

```swift
struct GlassCard<Content: View>: View {
    let content: Content

    init(@ViewBuilder content: () -> Content) {
        self.content = content()
    }

    var body: some View {
        content
            .padding(16)
            .background(.ultraThinMaterial)
            .clipShape(RoundedRectangle(cornerRadius: 20, style: .continuous))
            .shadow(color: .black.opacity(0.08), radius: 12, y: 4)
    }
}
```

## Floating Action Bar — SwiftUI

```swift
struct FloatingActionBar: View {
    var body: some View {
        HStack(spacing: 24) {
            ActionButton(icon: "house.fill", label: "Home")
            ActionButton(icon: "magnifyingglass", label: "Search")
            ActionButton(icon: "plus.circle.fill", label: "Create", isPrimary: true)
            ActionButton(icon: "bell.fill", label: "Alerts")
            ActionButton(icon: "person.fill", label: "Profile")
        }
        .padding(.horizontal, 24)
        .padding(.vertical, 12)
        .background(.ultraThinMaterial)
        .clipShape(Capsule())
        .shadow(color: .black.opacity(0.12), radius: 16, y: 8)
        .padding(.bottom, 8)
    }
}

private struct ActionButton: View {
    let icon: String
    let label: String
    var isPrimary: Bool = false

    var body: some View {
        VStack(spacing: 4) {
            Image(systemName: icon)
                .font(.system(size: isPrimary ? 28 : 20, weight: .medium))
                .foregroundStyle(isPrimary ? Color.accentColor : .secondary)
            Text(label)
                .font(.caption2)
                .foregroundStyle(.secondary)
        }
    }
}
```

## Skeleton Loader — Jetpack Compose

```kotlin
@Composable
fun SkeletonCard(modifier: Modifier = Modifier) {
    val shimmer = rememberInfiniteTransition(label = "shimmer")
    val alpha by shimmer.animateFloat(
        initialValue = 0.3f,
        targetValue = 0.7f,
        animationSpec = infiniteRepeatable(
            animation = tween(800, easing = LinearEasing),
            repeatMode = RepeatMode.Reverse
        ),
        label = "alpha"
    )

    Column(
        modifier = modifier
            .fillMaxWidth()
            .clip(RoundedCornerShape(12.dp))
            .background(MaterialTheme.colorScheme.surface)
            .padding(16.dp),
        verticalArrangement = Arrangement.spacedBy(12.dp)
    ) {
        Box(
            Modifier
                .fillMaxWidth(0.6f)
                .height(16.dp)
                .clip(RoundedCornerShape(4.dp))
                .background(MaterialTheme.colorScheme.onSurface.copy(alpha = alpha))
        )
        Box(
            Modifier
                .fillMaxWidth()
                .height(12.dp)
                .clip(RoundedCornerShape(4.dp))
                .background(MaterialTheme.colorScheme.onSurface.copy(alpha = alpha))
        )
    }
}
```

## Pill Navigation — Web (React + Tailwind)

```jsx
function PillNav({ tabs, activeTab, onChange }) {
  return (
    <div className="relative flex gap-1 rounded-full bg-neutral-100 p-1">
      {tabs.map((tab) => (
        <button
          key={tab.id}
          onClick={() => onChange(tab.id)}
          className={`
            relative z-10 rounded-full px-4 py-2 text-sm font-medium
            transition-colors duration-200
            ${activeTab === tab.id
              ? "text-neutral-900"
              : "text-neutral-500 hover:text-neutral-700"}
          `}
        >
          {activeTab === tab.id && (
            <span
              className="absolute inset-0 rounded-full bg-white shadow-sm"
              style={{ zIndex: -1 }}
            />
          )}
          {tab.label}
        </button>
      ))}
    </div>
  );
}
```

## Empty State — SwiftUI

```swift
struct EmptyStateView: View {
    let icon: String
    let title: String
    let message: String
    let actionLabel: String
    let action: () -> Void

    var body: some View {
        VStack(spacing: 16) {
            Image(systemName: icon)
                .font(.system(size: 48, weight: .light))
                .foregroundStyle(.secondary)

            VStack(spacing: 8) {
                Text(title)
                    .font(.title3.weight(.semibold))
                Text(message)
                    .font(.subheadline)
                    .foregroundStyle(.secondary)
                    .multilineTextAlignment(.center)
                    .frame(maxWidth: 280)
            }

            Button(action: action) {
                Text(actionLabel)
                    .font(.subheadline.weight(.semibold))
                    .padding(.horizontal, 24)
                    .padding(.vertical, 10)
                    .background(Color.accentColor)
                    .foregroundStyle(.white)
                    .clipShape(Capsule())
            }
            .padding(.top, 8)
        }
        .frame(maxWidth: .infinity, maxHeight: .infinity)
    }
}
```

## Animated Counter — Jetpack Compose

```kotlin
@Composable
fun AnimatedCounter(targetValue: Int, label: String) {
    val animatedValue by animateIntAsState(
        targetValue = targetValue,
        animationSpec = tween(durationMillis = 600, easing = FastOutSlowInEasing),
        label = "counter"
    )

    Column(horizontalAlignment = Alignment.CenterHorizontally) {
        Text(
            text = "$animatedValue",
            style = MaterialTheme.typography.displaySmall,
            fontWeight = FontWeight.Bold
        )
        Text(
            text = label,
            style = MaterialTheme.typography.bodySmall,
            color = MaterialTheme.colorScheme.onSurfaceVariant
        )
    }
}
```
