---
version: alpha
name: Fitlab
description: Dark loyalty app for a gym — customer mobile app and admin command portal.
colors:
  primary: "#e30613"
  primary-soft: "rgba(227, 6, 19, 0.1)"
  background: "#131313"
  background-login: "#0a0a0a"
  background-admin: "#0a0a0a"
  surface: "#1c1b1b"
  surface-muted: "#201f1f"
  surface-elevated: "#18181b"
  surface-sidebar: "#09090b"
  input: "#2a2a2a"
  input-dark: "#0e0e0e"
  border: "#353534"
  border-muted: "#262626"
  border-soft: "#404040"
  border-admin: "#18181b"
  text: "#e5e2e1"
  text-muted: "#c6c6c7"
  text-dim: "#737373"
  text-nav: "#71717a"
  on-primary: "#ffffff"
  on-surface: "#e5e2e1"
  accent-red: "#dc2626"
  success: "#22c55e"
  warning: "#f59e0b"
typography:
  font-family-base:
    fontFamily: Lexend
    fontSize: 16px
    fontWeight: 400
    lineHeight: 1.5
  headline-display:
    fontFamily: Lexend
    fontSize: 48px
    fontWeight: 800
    lineHeight: 1.1
    letterSpacing: -0.04em
  headline-lg:
    fontFamily: Lexend
    fontSize: 40px
    fontWeight: 800
    lineHeight: 1.1
    letterSpacing: -0.02em
  headline-md:
    fontFamily: Lexend
    fontSize: 24px
    fontWeight: 900
    lineHeight: 1.2
    letterSpacing: -0.05em
  body-md:
    fontFamily: Lexend
    fontSize: 16px
    fontWeight: 400
    lineHeight: 1.5
  body-sm:
    fontFamily: Lexend
    fontSize: 14px
    fontWeight: 400
    lineHeight: 1.5
  label-caps:
    fontFamily: Lexend
    fontSize: 11px
    fontWeight: 700
    lineHeight: 1
    letterSpacing: 0.08em
  label-caps-sm:
    fontFamily: Lexend
    fontSize: 10px
    fontWeight: 700
    lineHeight: 1
    letterSpacing: 0.1em
  balance-value:
    fontFamily: Lexend
    fontSize: 56px
    fontWeight: 800
    lineHeight: 1
    letterSpacing: -0.02em
rounded:
  sm: 10px
  md: 12px
  lg: 32px
  pill: 9999px
spacing:
  xs: 4px
  sm: 8px
  md: 16px
  lg: 24px
  xl: 32px
  shell-padding: 20px
  card-padding: 24px
  sidebar-width: 260px
  mobile-max: 448px
components:
  button-primary:
    backgroundColor: "{colors.primary}"
    textColor: "{colors.on-primary}"
    rounded: "{rounded.pill}"
    padding: 15px 24px
    height: 56px
    typography: "{typography.label-caps}"
  button-secondary:
    backgroundColor: "{colors.surface}"
    textColor: "{colors.text}"
    rounded: "{rounded.pill}"
    padding: 15px 24px
    height: 56px
  card:
    backgroundColor: "{colors.surface}"
    rounded: "{rounded.lg}"
    padding: "{spacing.card-padding}"
  input-field:
    backgroundColor: "{colors.input}"
    textColor: "{colors.text}"
    rounded: "{rounded.md}"
    padding: 14px 16px
    height: 48px
  sidebar-nav-item:
    backgroundColor: transparent
    textColor: "{colors.text-nav}"
    rounded: "{rounded.md}"
    padding: 12px 16px
    typography: "{typography.label-caps}"
  sidebar-nav-item-active:
    backgroundColor: "rgba(227, 6, 19, 0.15)"
    textColor: "{colors.primary}"
    rounded: "{rounded.md}"
    padding: 12px 16px
  bottom-nav:
    backgroundColor: "rgba(24, 24, 27, 0.95)"
    rounded: "{rounded.lg}"
    padding: 13px 24px
  topbar:
    backgroundColor: "{colors.surface-sidebar}"
    height: 57px
    padding: 16px 20px
---

# Fitlab

## Overview

Fitlab is a **dark, athletic loyalty platform** for a gym brand. The visual language is bold, high-contrast, and mobile-first. Copy is short and uppercase for navigation and labels. The single accent color (Fitlab Red) signals energy, urgency, and primary actions — never use it decoratively on large surfaces.

**Product surfaces:**
- **Customer app** — mobile-first (max ~448px content), bottom navigation, slide-out sidebar on small screens, centered points balance, activity feed, rewards marketplace, referrals.
- **Auth** — login and register on near-black backgrounds with subtle red radial gradients and orb glow.
- **Admin portal** — desktop sidebar + mobile drawer, dense data tables, stat cards, approval queues.

**Emotional tone:** Premium gym tech — confident, dark, minimal, with red as the only vivid color.

**Live reference:** http://82.197.69.121:8083/

## Colors

The palette is almost entirely neutral dark grays with one accent.

- **Primary / Fitlab Red (#e30613):** Primary buttons, active nav, logo wordmark, badges, links on hover. Use sparingly — one primary action per view.
- **Background (#131313):** Main customer app canvas.
- **Background Login (#0a0a0a):** Auth pages — deeper black.
- **Surface (#1c1b1b):** Cards, form panels, elevated content.
- **Surface Sidebar (#09090b):** Top bar, sidebars, bottom nav shell.
- **Text (#e5e2e1):** Primary body and headings.
- **Text Muted (#c6c6c7):** Secondary copy.
- **Text Dim / Nav (#737373, #71717a):** Captions, inactive nav, metadata.
- **Border (#353534, #18181b):** Dividers, card edges, input outlines.
- **Success (#22c55e):** Positive deltas, approval states.

Never use pure white `#ffffff` for page backgrounds. White is reserved for text on red buttons and small highlights.

## Typography

**Lexend** is the only typeface (weights 300–900 via Google Fonts).

- **Display / Hero:** 36–48px, weight 800, uppercase, tight letter-spacing — register hero, admin page titles.
- **Logo / Brand:** 24px, weight 900, uppercase, red — "FITLAB" wordmark.
- **Balance:** 56px, weight 800 — TFL Points number on dashboard.
- **Body:** 16px regular — descriptions, form labels (sentence case on forms, uppercase on nav).
- **Labels / Nav:** 10–12px, weight 700, uppercase, wide letter-spacing (0.05–0.2em) — nav items, badges, section kickers.
- **Admin kickers:** 11px uppercase red — section labels above headings.

## Layout

**Customer mobile:** Single column, max-width 448px centered, 20px horizontal padding, 100px bottom padding for fixed bottom nav.

**Customer tablet/desktop (768px+):** Fixed left sidebar 220px, content offset, max content 720px.

**Admin:** Flex layout — 260px sticky left sidebar, main content max 1280px with 32px padding. Below 960px: sidebar becomes slide-out drawer with hamburger trigger.

**Spacing rhythm:** 8px base grid. Common gaps: 8px (nav items), 16px (sections), 24px (cards), 32px (admin panels).

## Elevation & Depth

Depth is achieved through **layered dark surfaces**, not heavy shadows.

- Page → `#131313` or `#0a0a0a`
- Sidebar / topbar → `#09090b` with `1px` border `#18181b`
- Cards → `#1c1b1b` or `#18181b` with `#27272a` border
- Bottom nav → `rgba(24, 24, 27, 0.95)` + blur, top border, rounded top corners (32px)
- Mobile sidebar drawer → `#09090b` + `box-shadow: 4px 0 32px rgba(0,0,0,0.5)`
- Accent glow on badges: `box-shadow: 0 0 15px rgba(227, 6, 19, 0.1)`

## Shapes

- **Cards & panels:** 32px radius (`--radius-lg`)
- **Nav items & inputs:** 12px radius
- **Buttons & pills:** Full pill (`9999px`)
- **Avatars:** Circle, 40px, 2px red border
- **Active bottom nav item:** 48px red circle behind icon

Avoid mixing sharp corners with the standard 12px/32px radii.

## Components

### Buttons
- **Primary:** Red fill, white uppercase text, pill shape, min-height 56px. Hover: slight brightness increase.
- **Secondary / Social:** Dark card background, muted border, pill shape, uppercase 12px label.

### Inputs
- Dark fill `#2a2a2a` or `#0e0e0e` on auth, 12px radius, placeholder `#525252`, focus ring uses accent border.

### Navigation
- **Sidebar links:** Uppercase 11–12px, gray default, red + tinted red background when active.
- **Bottom nav (mobile):** 4 items — Dash, Activity, Rewards, Referral. Active = red icon in red circle.
- **Mobile drawer:** Hamburger opens slide-out; overlay `rgba(0,0,0,0.65)`; close via X, overlay tap, or Escape.

### Cards & Stats
- **Dash balance:** Centered large points number, "TFL Points" label below, red badge above.
- **Admin stat card:** `#18181b` surface, 32px radius, icon in red, uppercase label, large value, green delta optional.

### Auth
- Fixed dark topbar with red logo.
- Centered form card on gradient/orb background.
- Divider with uppercase "OR" between email and social login.

### Tables (Admin)
- Dark rows on `#18181b` panels, horizontal scroll on mobile, uppercase column headers.

## Do's and Don'ts

- Do use **Fitlab Red** only for primary actions, active states, and brand marks.
- Do keep backgrounds **dark** — customer `#131313`, admin `#0a0a0a`, sidebars `#09090b`.
- Do use **uppercase + letter-spacing** for navigation and labels.
- Do design mobile-first for customer screens; admin can be wider.
- Don't introduce additional accent colors (no blue links, no green CTAs).
- Don't use light/white themes — Fitlab is always dark mode.
- Don't use serif or system-only fonts — always **Lexend**.
- Don't place more than one filled red button per screen.
- Maintain **WCAG AA** contrast: `#e5e2e1` on `#131313` for body text.
