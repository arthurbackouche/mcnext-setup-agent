# MC Next Flow: constraints that drive translation

Baseline: Sept 2026, Growth / Advanced editions. Refresh each release (SKILL.md Step 1).
Each line is tagged **[confirmed]** (seen in docs or practitioner write-ups) or **[verify]** (test in the org before relying on it).

## Engine

- Campaign automation runs on Salesforce Flow, not a separate journey engine. [confirmed]
- Eight trigger types: Segment, Engagement Event, Data Cloud, Record, Schedule, Platform Event, Autolaunched, Screen. Trigger choice sets entry timing, runtime context and error behaviour. [confirmed]
- Core marketing elements: Wait for Amount of Time, Wait Until Date, Wait Until Event, Decision, Create/Update Records, Action, Subflow, Send Email, Send SMS. [confirmed]
- Send To Journey (Flow hands off to an MCE journey) rolled out from Nov 2025. Useful for phased cutover of hard journeys. [confirmed, check org enablement]

## Entry and re-entry

- A segment-triggered flow runs on the last **published** segment, not the live definition. [confirmed]
- No native "No re-entry" setting. Use segment exclusions, a durable flag field, or Campaign Member status. [confirmed]
- Exit criteria: up to 10 conditions, evaluated at entry and after each wait completes. [confirmed]
- No goal object. Model goals as exit criteria plus Campaign Member status. [confirmed]

## Decisions

- Decision element needs a Data Graph built on Unified Individual, set under Setup > Marketing Cloud > Basic Personalization. [confirmed]
- Recent releases added numeric and date conditions on related attributes (e.g. average spend, days since last purchase) directly in Decision. Reduces pre-flattening. [confirmed, verify per org release]
- Journey Data (`Event.*` entry payload) has no direct equivalent. Every attribute must resolve from the Data Graph or the triggering record. [confirmed]
- Cross-object attribute comparison (JB `ValueIsReference`) needs a Data Graph related-object path or a pre-computed field. [verify]
- IN / list operators on text. [verify]

## Splits and tests

- Path Experiment replaces Random Split and Path Optimizer. **Advanced edition only.** [confirmed]
- Engagement split → Wait Until Event on click/open with timeout branch. Prefer clicks. [confirmed pattern]

## Channels

- SMS quiet hours / blackout equivalent. [verify]
- Einstein STO availability. [verify]
- Push and in-app availability by edition. [verify]

## Sources

- martechnotes.com, "The 8 Flow Types in Marketing Cloud Next" (Aug 2026)
- Nobuyuki Watanabe, SFMC Tips #88 and #89 on Medium (May, Jun 2026)
- "Marketing Cloud Next: Onto the Frontier, Session 4: Flow" deck (Oct 2025)
- arthurbackouche.com/docs (MC Next feature taxonomy)
