# UI, visual, and motion guidance

Use this reference when discovering UI appearance or interaction preferences. Apply the core skill's rules for scope, interpretation, and authorization while making visual choices concrete.

## References and vocabulary

Search by `[UI object] + [context] + [specific characteristic]`, for example `dense survival game inventory`, `character select large portrait RPG`, `radial weapon selector game UI`, or `drag equip inventory interaction`. Prefer screenshots and shipped interfaces for static appearance, and video, GIFs, or interactive examples for motion and behavior. Search for useful properties rather than one perfect design.

Offer only the vocabulary that helps the current decision:

- **Composition and hierarchy:** centered, asymmetric, split-pane, anchored, full-bleed; dominant element, secondary information, visual weight.
- **Density and spacing:** compact, sparse, grouped, uniform; tight versus loose spacing.
- **Typography:** restrained, condensed, bold, muted, uppercase, numeric emphasis.
- **Geometry and containers:** sharp, soft, rounded, angular; borderless, divided, nested, framed, card-based.
- **Depth and color:** flat, layered, elevated, inset, translucent; muted, saturated, monochrome, accent-driven.
- **Interaction:** hover, selected, active, drag, snap, threshold, cancel, valid and invalid outcomes.

For a vague "mobile app" reaction, rounded cards, large controls, and generous spacing are possible explanations, not a mandate to change all three. Isolate the material uncertainty or show a useful contrast before adopting an interpretation.

## Motion and unusual interactions

Describe states over time:

**trigger → immediate response → transition → intermediate behavior → resting state**

```text
Pointer down
→ item lifts slightly
→ item follows the pointer with light inertia
→ compatible target reacts within attraction range
→ release on a valid target snaps the item into place
→ restrained overshoot
→ settle
```

This is an illustrative variant, not a default preference. When useful, compare direct tracking with trailing inertia, hard snap with magnetic attraction, fade/scale with shared-element morph, or no overshoot with restrained settle or elastic bounce. Capture only relevant trigger, origin, trajectory, timing, easing or spring behavior, thresholds, interruptibility, cancel behavior, and valid/invalid outcomes. Physical descriptions such as weight, resistance, attraction, elasticity, momentum, and settling may communicate better than technical terms.

## Representative tests and precedent

Prefer one screen or interaction over an entire UI and placeholders when polish would distract from the question. Do not build a design system around an unvalidated direction. Inspect the relevant hierarchy, proportions, alignment, spacing, density, typography, geometry, contrast, consistency, interaction states, and motion. Surface the rendered or running result when possible.

Ask simple reactions such as "too dense, too sparse, or close?" or "too light, too bouncy, or about right?" Use approved representative results as scoped visual precedent. Reuse stable spacing, radii, typography, separators, item treatment, hover/selected/disabled states, and animation characteristics where applicable, instead of rediscovering them every time.
