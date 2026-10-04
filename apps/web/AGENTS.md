# Prototype Instructions

Run the local server yourself and open the preview in the browser available to this environment. Do not give the user server-start instructions when you can run it.

Before making substantial visual changes, use the Product Design plugin's `get-context` skill when the visual source is unclear or no longer matches the current goal. When the user gives durable prototype-specific design feedback, preferences, or decisions, record them in `AGENTS.md`.

When implementing from a selected generated mock, treat that image as the source of truth for layout, component anatomy, density, spacing, color, typography, visible content, and hierarchy.

Build app UI in `src/`. Keep `.openai/hosting.json`, `worker/index.js`, `scripts/prepare-sites-build.mjs`, and `tests/sites-worker.test.mjs` intact so the same local prototype can be handed to Sites. Before a Sites handoff, run `npm run build` and `npm run test:sites`; the build must leave `dist/client/index.html`, `dist/server/index.js`, and `dist/.openai/hosting.json`.

For book appearance or lifecycle changes, use the approved five-book family in `../../design/round-10-five-book-materials/` and the current `../../PLAN.md` handoff. The user confirmed automatic ordered allocation on creation, stable appearance and placement, and an empty slot after deletion; five display slots are not a project-count limit. Fresh libraries start empty and existing local works are retained.

For book geometry or opening/turning changes, read `../../design/iterations/26-flexible-bound-book.md`. The confirmed target is a flexible leather-bound notebook: thin leather covers and paper bend during motion, with continuous binding and no open gutter gap. Retain preview.2's material improvement and cover-only title. Inspect actual normal/slow opening and contact before handoff.

For future book-page or opening changes, use the 2026-10-04 rollback clarification at the top of `../../PLAN.md`: preserve the approved reference image's manuscript content, fill its central blank area in that same style, and remove only the assistant-added Chinese title/description overlays. Preserve the sequential multi-page opening. A soft leather cover still has stiffness; the rejected limp drape is not the target. The user subsequently approved a limited new preview: correct only the upward bow between binding and gripped outer edge, preserve the currently accepted stiffness/material and all multi-page motion, and fill the manuscript center in the same style (image generation is authorized if needed). For this iteration read `../../design/iterations/28-cover-sag-and-manuscript-fill.md`. Ask the user when intent is uncertain rather than widening the scope.
