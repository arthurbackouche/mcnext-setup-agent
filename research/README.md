# Research

Inputs behind the `mcnext-setup` knowledge base. See [docs/knowledge-base.md](../docs/knowledge-base.md).

| Path | Committed | What |
|---|---|---|
| `arthurbackouche/notes/batch_A.md` to `batch_E.md` | yes | per-article analysis of 58 arthurbackouche.com docs, grouped by topic |
| `arthurbackouche/raw/` | no | extracted article text. Rebuild: `python3 tools/kb/fetch_arthurbackouche.py --out research/arthurbackouche` |
| `medium/medium_index.json` | yes | index of all 352 @marketingcloudtips posts (url, title, date) |
| `medium/selection.json` | yes | the 213 posts selected as setup-relevant |
| `medium/failed.json` | yes | posts the reader proxy could not fetch (Cloudflare). Fetch these through Chrome `get_page_text`. |
| `medium/raw/` | no | third-party article text. Rebuild: `python3 tools/kb/fetch_medium.py --index research/medium/medium_index.json --out research/medium --extra 28,143,194,302,327,348` |

Raw folders are git-ignored on purpose: the articles belong to their authors. Commit analysis, not copies.
