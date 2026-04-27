# A Side Step 3 Frontend Delivery Plan

## Summary

This plan executes step 3 from [`双人协作边界.md`](../../../双人协作边界.md) as an A-side frontend delivery slice. It assumes B has already frozen the initial contract and delivered `OpenAPI`, examples, field stability notes, and changelog material in `docs/RookieVito/`.

This plan does not redefine backend schema or add new public APIs. It turns the current frontend foundation into a stable handoff-ready delivery for B step 4.

## Current Baseline

Already implemented in the current frontend baseline:

- planning form submission
- request validation, loading, and failure toast
- result page rendering for basic itinerary, map, budget, and weather
- minimal edit loop for delete and move

Still required to complete step 3:

- fixed result page information architecture
- side navigation and anchors
- stronger page-level progress and state handling
- full contract mirroring on the frontend side
- `map_points` as the map source of truth
- explicit weather display rule
- export placeholder only

## Execution Order

1. Align frontend type mirrors to the current contract truth in `docs/RookieVito/*`.
   The implementation must consume the frozen contract shape rather than the current reduced frontend subset.

2. Restructure the result page into fixed `overview / budget / map / days / weather` sections.
   Each section must have a stable anchor target and user-facing label.

3. Add page-level state and progress behavior.
   Distinguish planning, editing, empty, and failure states instead of relying only on button loading and toasts.

4. Switch map rendering to backend `map_points`.
   Remove the implicit assumption that all map data can be reconstructed from `days.attractions`.

5. Lock weather and budget presentation rules.
   Weather follows `overview + daily_forecasts when available`; budget consumes the backend structured breakdown shape instead of a loose record assumption.

6. Reserve but do not complete export.
   Add only a placeholder entry point or layout slot. Do not connect real export behavior in this step.

7. Finalize tests and handoff notes.
   Record any missing contract need under `B contract follow-up` rather than solving it with frontend-owned schema drift.

## Implementation Rules

- Treat `docs/RookieVito/openapi.json`, `02-field-stability.md`, `CONTRACT_CHANGELOG.md`, and `examples/*` as the contract truth.
- Do not add or redefine backend field tables in frontend docs or code.
- If a field is unclear or missing, record it as a B-side contract gap.
- Do not pull step 4 or step 5 responsibilities into this plan.

## B Contract Follow-Up Format

If step 3 surfaces contract issues, record them in a short list with this shape:

- missing or unclear field
- why step 3 needs it
- which section or state it blocks
- whether a stable example JSON is enough or `openapi.json` also needs an update

This list is for handoff only. It is not a place to define new schema locally.

## Validation

### Docs Self-Check

- New files are limited to:
  - `docs/superpowers/specs/2026-04-25-a-step-3-frontend-delivery.md`
  - `docs/superpowers/plans/2026-04-25-a-step-3-frontend-delivery.md`
  - `docs/AGENTS.md`
  - `docs/CLAUDE.md`
- All referenced files under `docs/RookieVito/` and root collaboration docs resolve correctly
- `docs/CLAUDE.md` contains exactly `@AGENTS.md`
- `docs/superpowers/*` references contract truth but does not restate full `TripPlan*` or `EditRequest` field tables

### Implementation Verification Surface

The implementation driven by this plan must validate at least:

- `frontend/tests/services/api.test.ts`
  - request wrappers remain aligned to the current contract
  - map, weather, and budget data are consumed with the intended shape
- `frontend/tests/views/PlanningView.test.ts`
  - planning submission
  - loading and failure handling
  - empty or transitional state behavior as applicable
- `frontend/tests/views/ResultView.test.ts`
  - fixed section rendering
  - side navigation and anchor jumps
  - page-level progress and state feedback
  - edit refresh behavior
  - map rendering from `map_points`

### Manual Acceptance

The manual acceptance checklist for step 3 is fixed to five scenarios:

1. A stable example JSON renders a complete result page.
2. The page exposes `overview / budget / map / days / weather` sections with working navigation targets.
3. Planning, editing, empty, and failure states all show clear feedback.
4. One edit operation refreshes the result and restores the stable state.
5. Step 3 remains fully verifiable without a real backend; real service integration is deferred to B step 4.

## Step 4 Boundary

After this plan is implemented, B continues step 4 with:

- real service integration
- image completion support
- export support capabilities

If B changes shared fields after step 3, B must first update:

- `docs/RookieVito/openapi.json`
- `docs/RookieVito/02-field-stability.md`
- `docs/RookieVito/CONTRACT_CHANGELOG.md`
- any affected example JSON

Only then should A sync the frontend consumption layer.
