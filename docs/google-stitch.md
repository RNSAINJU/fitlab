# Link Fitlab to Google Stitch

Google [Stitch](https://stitch.withgoogle.com/) is Google's AI design canvas. This repo includes a **DESIGN.md** file that captures Fitlab's visual identity so Stitch can generate screens that match your live app.

## Option 1 — Import DESIGN.md (recommended)

1. Open https://stitch.withgoogle.com/ and sign in with Google.
2. Create a new project (or open an existing Fitlab project).
3. Open **Design system** / **DESIGN.md** in the project settings (or use the import option in the canvas).
4. Import this file from GitHub:
   ```
   https://github.com/RNSAINJU/fitlab/blob/main/DESIGN.md
   ```
   Or upload `DESIGN.md` from your local clone.
5. Stitch will use the tokens (colors, typography, spacing, components) for all new screens in that project.

## Option 2 — Extract from live URL

Stitch can derive a design system from a running site:

1. In Stitch, use **Extract design system from URL** (or similar in Design system tools).
2. Enter the live Fitlab URL:
   ```
   http://82.197.69.121:8083/
   ```
3. Also extract the admin portal for sidebar/table patterns:
   ```
   http://82.197.69.121:8083/admin-portal/
   ```
4. Review extracted tokens against `DESIGN.md` and merge any gaps manually.

## Option 3 — Screenshot + prompt

Upload screenshots of key screens and paste this prompt in Stitch:

```
Design a mobile loyalty app called Fitlab using this design system:

- Dark theme only: backgrounds #131313 / #09090b, never white pages
- Accent: Fitlab Red #e30613 for CTAs, active nav, logo
- Font: Lexend, uppercase labels with letter-spacing
- Customer app: bottom nav (Dash, Activity, Rewards, Referral), slide-out sidebar, centered TFL Points balance
- Admin: dark sidebar, stat cards, approval tables
- Pill buttons (9999px radius), cards with 32px radius

Match the reference screenshots and DESIGN.md tokens exactly.
```

## Validate DESIGN.md locally

```bash
npx @google/design.md lint DESIGN.md
```

Export tokens to Tailwind (optional):

```bash
npx @google/design.md export --format tailwind DESIGN.md
```

## Key screens to prototype in Stitch

| Screen | Route | Notes |
|--------|-------|-------|
| Login | `/accounts/login/` | Dark auth, red CTA, social buttons |
| Register | `/accounts/register/` | Hero headline, form card |
| Dashboard | `/accounts/dashboard/` | Points balance, activity preview |
| Activity | `/activity/` | Feed list, TFL Points per row |
| Rewards | `/rewards/` | Marketplace cards, point costs |
| Referrals | `/referrals/` | Referral code, share CTA |
| Admin overview | `/admin-portal/` | Stat grid, sidebar nav |
| Admin rewards | `/admin-portal/rewards/` | Create reward form |

## Keeping design in sync

When you change `static/css/fitlab.css` or major UI patterns:

1. Update `DESIGN.md` tokens and component notes.
2. Re-import or sync in Stitch.
3. Commit and push — the file lives at the repo root for agents and Stitch alike.

**Spec:** https://github.com/google-labs-code/design.md
