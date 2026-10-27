# Canonical project workspace

This directory, `D:\Steelmaking\refining-process-lab\refining-process`, is the single maintained source of this refining workbench. Make future code changes here. The user uses GitHub Desktop and Cloudflare directly from the source folder. Do not generate ZIP archives by default. Existing files in `release/` are historical deliverables, not another maintained source tree.

## Boundaries

- `dist/bed-*.mjs` contains the continuous-bed application, conditional calculation model, planning and evidence. Preserve the connected EAF–bed–caster design and concurrent operations attached to zones.
- Numeric controls are sliders. Main zone lengths are 0.5–3 m in 0.5 m increments; those are UI design allocations, not actual equipment dimensions.
- Preserve source IDs, cases, original units and verification boundaries in `dist/evidence/`. Literature references are not calibration runs.
- Never turn unknown inputs into zero, manufacture confidence intervals, or call unsupported chemistry/CFD/CAD/AI tools implemented. No industrial certification follows from software tests.
- A future GPT integration must call deterministic calculators through validated interfaces. Keep API secrets on the server. CAD and licensed Fluent tasks belong to separate execution services; do not imply browser-side execution.

## Work and delivery

- Run `npm test` for model changes and `npm run build` for static completeness. UI changes require appropriate browser checks, including preservation of live slider dragging and existing saved plans.
- Deliver the uncompressed source directory. Generate archives only if the user explicitly asks for them; do not automatically run `package-release.py`. Keep credentials, solver results and user uploads outside committed source.
- This GitHub/Cloudflare repository intentionally does not contain the old Site identity. The historical preview manifest stays in the parent directory; do not copy its `.git` or `.openai` into this repository. Cloudflare uses `dist/` and `wrangler.jsonc` here.
- Update `REVIEW_COMPLETENESS.md`, `ARCHITECTURE.md` and the UI's capability labels when relevant implementation or validation boundaries change.

