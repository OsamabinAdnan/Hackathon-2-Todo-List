---
id: 013
title: Fix Settings and Logout button visibility in Dashboard Navigation
stage: general
date: 2026-01-06
surface: agent
model: claude-sonnet-4-5-20250929
feature: dashboard
branch: main
user: unknown
command: continue-session
labels: [ui, navigation, contrast, theme]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
 - frontend/app/dashboard/layout.tsx
tests:
 - npm --prefix frontend run lint
---

## Prompt

Settings and Logout buttons in the Navbar/Sidebar were nearly invisible in both light and dark themes. The user provided screenshots (`issue1.png`, `issue2.png`) showing that these buttons were missing visual presence when inactive.

## Response snapshot

- Identified that inactive buttons were using `text-secondary`, which had extremely low contrast against the background in both theme modes.
- Refactored `frontend/app/dashboard/layout.tsx` (both mobile sidebar and desktop header) to use `text-foreground` for inactive links instead of `text-secondary`.
- Replaced the broken `hover:bg-hover` class with a functional `hover:bg-primary/10 hover:text-primary` pattern to provide clear visual feedback.
- Added `shadow-lg` to the active state button (`bg-primary`) to improve depth and focus.
- Modified the desktop Logout button to use a ghost-bordered style (`text-primary border-primary/20`) which balances the UI better than the solid primary block.
- Verified with `npm run lint` (PASS).

## Outcome

- ✅ Impact: Navigation links (Settings, Dashboard, Logout) are now high-contrast and clearly visible in both light and dark themes.
- 🧪 Tests: Lint passed.
- 📁 Files: Updated `frontend/app/dashboard/layout.tsx`.
- 🔁 Next prompts: None.
- 🧠 Reflection: Using specific "foreground" variables for text instead of "secondary" colors (which are often meant for backgrounds or subtle accents) ensures accessibility standards are met. Hardcoding hover states with opacity variants (e.g., `primary/10`) is more reliable than custom theme classes that might not be defined.

## Evaluation notes (flywheel)

- Failure modes observed: `text-secondary` color values in `globals.css` were too close to the `background` color in both themes, making text invisible.
- Graders run and results (PASS/FAIL): Frontend lint PASS.
- Prompt variant (if applicable): null
- Next experiment (smallest change to try): None.
