# MC Next AMPscript Function Baseline (Summer '26, API 67.0)

Source: community runtime testing (sfmarketing.cloud, July 2026) cross-checked against the
official Salesforce AMPscript function index for Marketing Cloud Next / Growth & Advanced.
Refresh each release — new functions ship regularly.

## Supported — runtime-confirmed (35)

Add, BuildRowsetFromJson, Concat, DateAdd, DateDiff, DateParse, Divide, Empty, Field,
Format, FormatCurrency, FormatDate, FormatNumber, Iif, IndexOf, IsNull, Length, Lowercase,
Mod, Multiply, Now, Output, OutputLine, ProperCase, Random, Replace, ReplaceList, Row,
RowCount, StringToDate, Subtract, Substring, Trim, Uppercase, v

## Supported per official index — NOT yet runtime-verified publicly (6)

ContentBlockById, ContentBlockByKey, ContentBlockByName, Lookup, RetrieveSalesforceObjects,
RaiseError

Notes: Next's Lookup targets **Marketing Objects** (not Data Extensions) and returns a
single value — first matching record only. These six typically carry the highest-volume
personalisation in an estate; they are the reason for verdict C and the validation spike.

## Verdict definitions

| Verdict | Meaning | Effort |
|---|---|---|
| A | No AMPscript at all | Content copy only |
| B | Only runtime-confirmed functions | Carries over as written |
| C | Only supported functions, but includes the untested six | One test email validates all |
| D | Unsupported functions with a native Next replacement | Mechanical rebuild, nothing lost |
| E | Multi-row lookup family (LookupRows / LookupOrderedRows / LookupRowsCS) | One upstream data-prep change unlocks the whole category |
| F | Send-time writes / API calls / other no-equivalent functions | Individual redesign |

Precedence when scoring an email: F > E > D > C > B > A (worst function wins).

## Native replacement map (verdict D)

| MCE function | Next replacement |
|---|---|
| AttributeValue | Merge field / personalization data binding |
| RedirectTo | Standard dynamic link handling |
| CloudPagesURL | Next preference pages / forms (CloudPages absent) |
| BeginImpressionRegion / EndImpressionRegion | Drop — analytics is native |
| RegExMatch | Pre-compute in the segment / Marketing Object attribute |
| SystemDateToLocalDate | FormatDate with locale |
| URLEncode | Pre-compute / static links |
| GetSocialPublishUrlByName | Static share links |
| TreatAsContent | Plain merge fields (check subject lines!) |
| BuildRowsetFromString | Pre-concatenate upstream |

## Redesign map (verdicts E and F)

| Function | Category | Fix pattern |
|---|---|---|
| LookupRows / LookupOrderedRows / LookupRowsCS | E | Pre-flatten related records (names, counts, attributes) onto the contact during audience build; email reads merge fields |
| InsertDE / UpsertDE / UpdateDE / DeleteDE | F | Move write to Flow / ingestion pre- or post-send |
| HTTPPost / HTTPPost2 / HTTPGet | F | Call the API pre-send (Flow/Apex), store result on the record, merge it |
| WAT / WATP / other tracking-write | F | Native Next analytics |

Anything not in any list above and not an artifact = treat as F and research it individually.
