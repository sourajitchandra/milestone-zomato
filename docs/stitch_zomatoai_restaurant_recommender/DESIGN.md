---
name: Lumina Crimson
colors:
  surface: '#111319'
  surface-dim: '#111319'
  surface-bright: '#373940'
  surface-container-lowest: '#0c0e14'
  surface-container-low: '#191b22'
  surface-container: '#1e1f26'
  surface-container-high: '#282a30'
  surface-container-highest: '#33343b'
  on-surface: '#e2e2eb'
  on-surface-variant: '#e4bebc'
  inverse-surface: '#e2e2eb'
  inverse-on-surface: '#2e3037'
  outline: '#ab8987'
  outline-variant: '#5b403f'
  surface-tint: '#ffb3b1'
  primary: '#ffb3b1'
  on-primary: '#680011'
  primary-container: '#ff535a'
  on-primary-container: '#5b000e'
  inverse-primary: '#bb162c'
  secondary: '#ffb3b0'
  on-secondary: '#68000f'
  secondary-container: '#901822'
  on-secondary-container: '#ff9e9b'
  tertiary: '#c3c6d7'
  on-tertiary: '#2c303d'
  tertiary-container: '#8d90a0'
  on-tertiary-container: '#252936'
  error: '#ffb4ab'
  on-error: '#690005'
  error-container: '#93000a'
  on-error-container: '#ffdad6'
  primary-fixed: '#ffdad8'
  primary-fixed-dim: '#ffb3b1'
  on-primary-fixed: '#410007'
  on-primary-fixed-variant: '#92001c'
  secondary-fixed: '#ffdad8'
  secondary-fixed-dim: '#ffb3b0'
  on-secondary-fixed: '#410006'
  on-secondary-fixed-variant: '#8c1520'
  tertiary-fixed: '#dfe2f3'
  tertiary-fixed-dim: '#c3c6d7'
  on-tertiary-fixed: '#171b27'
  on-tertiary-fixed-variant: '#424654'
  background: '#111319'
  on-background: '#e2e2eb'
  surface-variant: '#33343b'
typography:
  display-lg:
    fontFamily: Outfit
    fontSize: 48px
    fontWeight: '700'
    lineHeight: 56px
    letterSpacing: -0.02em
  display-lg-mobile:
    fontFamily: Outfit
    fontSize: 32px
    fontWeight: '700'
    lineHeight: 40px
    letterSpacing: -0.02em
  headline-md:
    fontFamily: Outfit
    fontSize: 24px
    fontWeight: '600'
    lineHeight: 32px
  body-lg:
    fontFamily: Outfit
    fontSize: 18px
    fontWeight: '400'
    lineHeight: 28px
  body-md:
    fontFamily: Outfit
    fontSize: 16px
    fontWeight: '400'
    lineHeight: 24px
  label-caps:
    fontFamily: Outfit
    fontSize: 12px
    fontWeight: '700'
    lineHeight: 16px
    letterSpacing: 0.05em
rounded:
  sm: 0.25rem
  DEFAULT: 0.5rem
  md: 0.75rem
  lg: 1rem
  xl: 1.5rem
  full: 9999px
spacing:
  base: 8px
  container-margin: 24px
  gutter: 16px
  section-gap: 48px
---

## Brand & Style
The design system is engineered for a premium, AI-driven culinary experience. It balances the urgency of food delivery with the sophisticated precision of artificial intelligence. 

The aesthetic is a fusion of **Glassmorphism** and **High-Contrast Dark Mode**. It utilizes deep, "infinite" backgrounds to allow vibrant primary accents and frosted glass components to recede and advance in 3D space. The emotional response is one of high-fidelity reliability—feeling both futuristic and appetizing.

## Colors
The palette is anchored by a "Deep Dark" foundation to ensure maximum contrast for the AI elements. 

- **Primary Gradient:** The signature Zomato Crimson to Coral Pink gradient is reserved for primary actions, AI status indicators, and critical path highlights.
- **Surface Colors:** Use semi-transparent white (10% opacity) for glass containers to create depth against the #0F1117 background.
- **Functional Colors:** Success and warning states should be slightly desaturated to maintain the premium feel, ensuring they do not compete with the primary crimson glow.

## Typography
This design system uses **Outfit** exclusively to provide a clean, geometric, and modern feel. 

- **Hierarchy:** Use heavy weights (700) for AI-generated insights and restaurant names. 
- **Readability:** Increase line-height for body text to ensure legibility against dark backgrounds.
- **Styling:** Use the `label-caps` style for category tags and metadata to provide a technical, structured appearance that complements the organic nature of food imagery.

## Layout & Spacing
The layout follows a **fluid grid** logic with generous negative space to emphasize the glassmorphic depth.

- **Grid:** Use a 12-column grid for desktop and a 4-column grid for mobile.
- **Rhythm:** Spacing should follow an 8px incremental scale. 
- **Content Flow:** AI chat interfaces and recommendation carousels should use "peek" behavior on mobile, showing a hint of the next item to encourage horizontal exploration.

## Elevation & Depth
Depth is the core differentiator of this design system. It is achieved through:

1.  **Backdrop Blur:** All floating panels must use a `20px` to `40px` backdrop blur with a `10%` white border-stroke to define edges.
2.  **Interaction Glows:** Active elements (hovered cards or focused inputs) emit a subtle `#E23744` outer glow (blur: 20px, spread: -5px) to simulate the "energy" of the AI.
3.  **Layering:** AI suggestions sit at the highest elevation, using the most transparent glass to appear closest to the user.

## Shapes
The shape language is consistently **Rounded (2xl)**. 

- **Outer Containers:** Use a `24px` radius for main content cards and AI dialogue boxes.
- **Inner Elements:** Buttons and interactive chips use a slightly tighter `16px` radius to create a nested "squircle" harmony.
- **Visual Continuity:** Avoid sharp corners entirely; even progress bars and dividers should have rounded caps.

## Components

### Buttons
- **Primary:** Filled with the Crimson-to-Coral gradient. White text. On hover, apply the red glow effect.
- **Secondary:** Glass container (20% white) with a 1px white border.

### AI Input Field
- Use a thick `24px` rounded glass container. 
- The cursor/accent color should be the primary crimson.
- When active, the border should transition from white to the primary gradient.

### Cards (Restaurant/Food)
- **Background:** Semi-transparent glass.
- **Image:** Top-aligned with a subtle inner-shadow to ensure text overlays are readable.
- **Glow:** Add a subtle red drop-shadow on hover to indicate selectability.

### Chips & Tags
- Pill-shaped with high-transparency backgrounds. Use `label-caps` typography for tag content.

### AI Progress/Loading
- Instead of standard spinners, use a pulsing gradient border that travels around the perimeter of the glass container.