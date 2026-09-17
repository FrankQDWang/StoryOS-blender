# StoryOS Library experiment

- 每次最终回复使用中文。
- Before designing, implementing, or resuming after context compaction, read `PLAN.md`. It owns the accepted scope, decisions, permissions, acceptance criteria, and current handoff.
- This directory is an independent experience prototype. Keep work here. The sibling `../StoryOS` repository is a read-only reference until the user requests integration.
- Use the adopted recommendation from the referenced conversation. Optional roaming and direct Quick Access are both part of the experience.
- Use Chrome for browser interaction and verification. The user authorized Chrome control and installation of necessary tools and dependencies on 2026-09-13.
- Keep project assets, source files, downloads, and verification evidence in this directory. Use project-local dependencies or established package managers for shared programs. Ask before an installation needs another location or a material permission change.
- Ask for genuine product tradeoffs or permission gaps. Resolve routine choices autonomously and do not re-ask settled decisions.
- Update the Current handoff section of `PLAN.md` after meaningful work and before stopping. Distinguish concepts, implemented behavior, and verified behavior. Record asset provenance and selected-image paths when assets are created.

- Before room edits, read `design/iterations/05-a-hearth-study-selected.md` and the Current handoff in `PLAN.md`. The accepted visual target is `design/round-05/A-hearth-study/final.png`; the user approved the implemented 0.1.3-preview.3 on 2026-09-17. Earlier iteration documents are history.
- Implement the selected image on the restored baseline, preserving five independent display slots, optional roaming, Quick Access and existing project/book flows. Keep hands and their animations unchanged. Preserve the selected composition and clear walking space; do not reopen style exploration or increase display slots.
- The user authorized saving the approved state to synchronized local/remote `main` and deleting iteration branches on 2026-09-17. Preserve existing historical tags. Future iterations start from this approved state; room layout in `apps/web/src/room-layout.json` must drive Blender geometry, book anchors and roaming collision together.

- Preserve the approved front composition when addressing the right-hand stands from the side. Keep the writing desk in its current position by default; if a later adjustment needs movement, the user prefers a slight move to the right, assessed in both views. The user authorized the three side-view corrections on 2026-09-16; preview.3 implements uniform right-hand stand proportions and more even spacing, with the writing desk unchanged. See `evidence/v013-side-balance/` and `design-qa.md`; the user has approved this state. `c03e1b9` remains the prior checkpoint; see `PLAN.md` for the latest save status.
