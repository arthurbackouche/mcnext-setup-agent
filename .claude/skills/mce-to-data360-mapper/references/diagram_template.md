# Inline diagram template

Use the Visualizer (`show_widget`, SVG mode) after loading the `diagram` module. Produce one layered
map per estate and one for the mapping strategy. Never list every object; show layers with counts and
make each box clickable with `sendPrompt` so the user can drill in.

## Layer map (D360 or MCE)

viewBox 680 wide. Three tiers of boxes, 56px tall, widths 180 (three across) or 270 (two across) or
400 (one centred). Bus lines join tiers. Colour by role, not by sequence:

- gray: sources, landing, raw
- purple: canonical model (ssot__, unified, master data)
- teal: consumption (data graphs, segments, journeys, reporting)

Subtitle is `N objects, M fields` or a two-word descriptor. Sentence case everywhere.

## Mapping strategy map

Top: one gray box for the source estate with counts.
Middle row: purple "Standard dmos" | teal "N custom dmos" | gray "Not ingested", each with DE counts.
Below each: a 150px-tall box listing target DMO names or reasons (12px `ts` text, left aligned, 18px spacing).
Bottom: purple "Unified individual" box with the identity key statement, and a gray "Open gap" box.
Close with a one-line legend in `ts` text.

Template coordinates that are known to fit: rows at y=40, 140, 240 (150 tall), 434; columns at x=40, 250, 460 with width 180.
