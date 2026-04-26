# A Side Step 3 Frontend Delivery Spec

## Summary

This spec defines the full implementation target for step 3 in [`双人协作边界.md`](../../../双人协作边界.md): A completes the frontend consumption layer on top of the frozen contract so B can continue step 4 without reopening frontend-owned scope.

This is not a product-wide spec, not a V0 replacement, and not a backend contract definition. It only defines what A must finish in the frontend consumption layer before handoff to B.

## Source Of Truth

This spec consumes but does not redefine the following sources:

- [`双人协作边界.md`](../../../双人协作边界.md)
- [`A_开工清单.md`](../../../A_开工清单.md)
- [`B_首批交付清单.md`](../../../B_首批交付清单.md)
- [`智能旅行助手.md`](../../../智能旅行助手.md)
- [`docs/RookieVito/openapi.json`](../../RookieVito/openapi.json)
- [`docs/RookieVito/02-field-stability.md`](../../RookieVito/02-field-stability.md)
- [`docs/RookieVito/CONTRACT_CHANGELOG.md`](../../RookieVito/CONTRACT_CHANGELOG.md)
- `docs/RookieVito/examples/*`

External contract dependencies for this step remain:

- `TripPlanRequest`
- `TripPlan`
- `EditRequest`
- Minimal error response contract

If any field is still missing for step 3, it must be recorded as a contract gap for B. A must not extend backend schema in frontend-only docs or code.

## Goal

Step 3 is complete when A can deliver a stable frontend result experience that consumes the frozen contract end to end without depending on B's real service integration work.

The frontend delivery target includes:

- A stable result page information architecture
- Fixed sections and anchors for `overview`, `budget`, `map`, `days`, and `weather`
- Stable local editing interactions and page-level feedback
- Stable loading, empty, and error states
- Frontend type mirrors aligned to the current backend contract
- Map rendering driven by backend `map_points`

## In Scope

### 1. Result Page Information Architecture

The result page must be organized into five stable sections:

- `overview`
- `budget`
- `map`
- `days`
- `weather`

These sections are user-visible structure, not only internal layout containers. Each section must have a stable anchor target so a navigation control can scroll to it predictably.

`overview` must be treated as its own result block rather than being implied only by the page header.

### 2. Navigation And Anchors

A must provide side navigation or equivalent in-page navigation for the five fixed sections above.

Required behavior:

- The user can jump to each result section directly
- Anchor targets remain stable across normal result rendering
- Navigation labels follow the result page structure instead of backend field names

This step only fixes the frontend navigation behavior. It does not add new backend fields.

### 3. Page-Level States And Feedback

This step requires page-level state behavior, not only button-level loading.

The frontend must explicitly define:

- planning/loading state while a plan is being created
- editing/loading state while an edit request is in flight
- result empty state
- planning failure state
- edit failure feedback

Toast-only feedback is not sufficient as the only behavior definition. The spec must treat these as page or section level UI states with explicit user-facing meaning.

### 4. Local Edit Loop

The allowed step 3 editing scope remains the current minimal local loop:

- delete attraction
- move attraction up
- move attraction down

The frontend owns the interaction flow, disabled states, refresh behavior, and user feedback. The backend contract still owns request shape and semantic meaning.

This step does not introduce new edit operations.

### 5. Contract Consumption Rules

The frontend must mirror the current backend contract completely enough to avoid hidden drift when B starts real service integration.

For step 3, the spec must explicitly require frontend alignment for contract-sensitive areas already frozen by B, including:

- top-level plan metadata such as `created_at` and `plan_version`
- image-related read-only fields such as `cover_image_url` and `image_url`
- structured weather details via `daily_forecasts`
- structured budget breakdown consumption
- backend-owned `map_points`

This spec intentionally does not restate field tables. The exact field shape comes from `openapi.json`, field stability notes, and example JSONs.

### 6. Map Consumption Rule

`map_points` is the only source of truth for result map rendering in step 3.

The frontend must not keep deriving map markers from `days.attractions` as the primary behavior, because that can silently discard backend-supplied non-attraction or enriched map data once B continues step 4.

### 7. Weather Consumption Rule

The weather block must explicitly choose one of the following stable display contracts for step 3:

- `overview` only
- `overview` plus `daily_forecasts`

The implementation must follow one chosen rule consistently. The decision must be reflected in tests and handoff notes so B does not infer a different display contract later.

Default for this spec: `overview` plus `daily_forecasts` when available, with graceful rendering if forecast data is empty.

### 8. Export Boundary

Step 3 may reserve an export entry point or placeholder in the information architecture, but export does not count as complete functionality in this step.

Allowed:

- placeholder entry
- reserved layout slot
- explicit "not yet connected" copy

Not allowed as step 3 acceptance:

- real PDF export
- real image export
- backend-assisted export workflow

## Explicit Non-Goals

This spec does not include:

- B-side real service integration
- backend schema redesign
- OpenAPI redesign
- image completion write-back
- final PDF/image export capability
- frontend-owned fallbacks for unfrozen backend fields
- new edit operations

## Current Gaps To Lock Before Implementation

The following step 3 gaps are already visible from the current frontend state and must be handled as part of the implementation target:

- Result page sections are present as cards but not yet fixed as anchored information architecture
- Page-level progress and state feedback are still lighter than the step 3 target
- Frontend type mirrors are not yet fully aligned to the current backend contract metadata and structured nested fields
- Map behavior still needs to be locked to backend `map_points`
- Weather rendering scope must be made explicit and testable
- Export must remain only a placeholder in this step

## Acceptance

Step 3 is accepted when all of the following are true:

- A can render a full result page from frozen example JSONs without requiring B's real service integration
- The page contains fixed `overview / budget / map / days / weather` sections with working anchor navigation
- Planning, editing, empty, and failure states are explicitly represented
- The map consumes backend `map_points`
- The frontend mirrors the frozen contract closely enough that B can continue step 4 without reopening frontend-owned contract assumptions
- Any remaining contract need is listed under a B-facing gap list instead of being silently added in frontend code

## Handoff To B

B can begin step 4 once A has completed this step 3 delivery and the following conditions hold:

- A consumes only frozen contract inputs from `docs/RookieVito/*`
- Result page structure, anchors, state flow, and edit feedback are stable
- The frontend no longer depends on locally invented field meanings
- Any still-missing field or example is documented as a `contract gap for B`

B's next-step scope remains:

- real service integration
- image completion support
- export support capabilities
- contract updates through `openapi.json`, field stability notes, examples, and changelog before notifying A
