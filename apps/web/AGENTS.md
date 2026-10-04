# Prototype Instructions

Run the local server yourself and open the preview in the browser available to this environment. Do not give the user server-start instructions when you can run it.

Before making substantial visual changes, use the Product Design plugin's `get-context` skill when the visual source is unclear or no longer matches the current goal. When the user gives durable prototype-specific design feedback, preferences, or decisions, record them in `AGENTS.md`.

When implementing from a selected generated mock, treat that image as the source of truth for layout, component anatomy, density, spacing, color, typography, visible content, and hierarchy.

Build app UI in `src/`. Keep `.openai/hosting.json`, `worker/index.js`, `scripts/prepare-sites-build.mjs`, and `tests/sites-worker.test.mjs` intact so the same local prototype can be handed to Sites. Before a Sites handoff, run `npm run build` and `npm run test:sites`; the build must leave `dist/client/index.html`, `dist/server/index.js`, and `dist/.openai/hosting.json`.

For book appearance or lifecycle changes, use the approved five-book family in `../../design/round-10-five-book-materials/` and the current `../../PLAN.md` handoff. The user confirmed automatic ordered allocation on creation, stable appearance and placement, and an empty slot after deletion; five display slots are not a project-count limit. Fresh libraries start empty and existing local works are retained.

For book geometry, opening/turning or page-content changes, read `../../design/iterations/27-book-mechanics-and-blank-pages.md` and `../../design/iterations/26-flexible-bound-book.md`. The confirmed target is a flexible leather-bound notebook: thin leather covers and paper bend during motion, with continuous binding and no open gutter gap. Retain preview.2's material improvement and cover-only title. Inspect actual normal/slow opening and contact before handoff.

The user rejected preset-angle motion and decorative pseudo-writing. Opening must respect binding, the actual hand support, gravity and lectern contact; unsupported leather/paper must fall after release. Interior pages stay unprinted; only the outer cover carries the real title. A geometry or test pass does not establish natural movement.
