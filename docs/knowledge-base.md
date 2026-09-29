# Setup knowledge base

`mcnext-setup` loads its knowledge from `.claude/skills/mcnext-setup/references/`:

| Path | What |
|---|---|
| `kb/00_index.md` | index and a table mapping each setup check (S1-S23) to its answer and confidence |
| `kb/01_setup_order.md` | canonical end-to-end order, licences to first test send, with dependencies and timings |
| `kb/10_` to `kb/23_` | topic files: steps, limits, gotchas, automation route (CLI/API vs UI-only), verification, sources |
| `kb/91_contradictions.md` | conflicts between sources and how they were resolved |
| `chrome_playbook.md` | how to drive Lightning Setup with Claude in Chrome: session hygiene, guard rules, the interaction ladder, known controls |
| `sources/` | the original foundation-setup articles the skill was first written from |

Every fact carries a source tag: `[AB:<slug>]` for arthurbackouche.com articles, `[MCT:<n>]` for the Medium "SFMC Tips" series by Nobuyuki Watanabe (@marketingcloudtips), `[FIELD]` for behaviour observed in live implementations. `[FIELD]` wins unless the target org shows otherwise. Org-specific findings never go here; they go to the engagement's `out/setup/open_items.md`.

## How it was built

1. **Collect.** `tools/kb/fetch_arthurbackouche.py` (sitemap, 58 pages) and `tools/kb/fetch_medium.py` (index built in Chrome from the author's profile, then a reader proxy per article).
2. **Analyse.** Parallel `mcnext-setup` agents in local-files mode, one per topic batch, write notes per article: purpose, prerequisites, steps with UI paths, limits, gotchas, automation route, verification, checks affected. Notes live in `research/<source>/notes/`.
3. **Merge.** One agent merges the notes into the `kb/` files and logs contradictions.

## Research folder

`research/` keeps the article indexes and analysis notes. Raw article text and HTML are git-ignored: rebuild them with the tools above. Medium articles are third-party content; do not commit them.

## Status

- arthurbackouche.com: 58 articles analysed and merged.
- Medium @marketingcloudtips: index of 352 posts, 213 selected for setup relevance, 180 fetched. The 33 that Cloudflare blocked are listed in `research/medium/failed.json`. Analysis and merge with `[MCT]` tags are pending (see CHANGELOG roadmap).
