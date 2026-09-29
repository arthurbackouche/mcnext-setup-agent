# Slim journey schema

Use when an `sfmc_get_journey` response comes back inline and is too large to save verbatim.
The parser needs only these fields. Copy values exactly; do not paraphrase criteria XML.

```json
{
  "id": "...", "key": "...", "name": "...", "version": 1, "status": "Published",
  "entryMode": "SingleEntryAcrossAllVersions",
  "defaults": {"email": ["{{Event.DEAudience-xxxx.\"Email\"}}"], "mobileNumber": ["..."]},
  "activity": {"lastContactProcessed": "2026-09-21T22:03:03"},
  "triggers": [{"type": "EmailAudience", "metaData": {"eventDefinitionKey": "DEAudience-xxxx"}}],
  "exits": [{"metaData": {"criteriaDescription": "..."}}],
  "goals": [],
  "activities": [
    {"key": "EMAILV2-1", "name": "...", "type": "EMAILV2",
     "outcomes": [{"key": "o1", "next": "WAITBYDURATION-1"}],
     "configurationArguments": {"triggeredSend": {"emailId": 22249, "emailSubject": "...", "publicationListId": 1145}}},
    {"key": "WAITBYDURATION-1", "name": "7 days", "type": "WAIT",
     "outcomes": [{"key": "o2", "next": "MULTICRITERIADECISIONV2-1"}],
     "configurationArguments": {"waitDuration": 7, "waitUnit": "DAYS", "specifiedTime": "00:00", "timeZone": "..."},
     "metaData": {"waitType": "duration"}},
    {"key": "MULTICRITERIADECISIONV2-1", "name": "", "type": "MULTICRITERIADECISION",
     "outcomes": [{"key": "default_path_1", "next": "...", "metaData": {"label": "..."}},
                  {"key": "remainder_path", "next": "...", "metaData": {"label": "Remainder"}}],
     "configurationArguments": {"criteria": {"default_path_1": "<FilterDefinition>...</FilterDefinition>"}}},
    {"key": "SMSSYNC-1", "name": "...", "type": "SMSSYNC",
     "outcomes": [{"key": "o3", "next": "..."}],
     "configurationArguments": {"assetId": 107341, "fromName": "614...", "honorBlackoutWindowEnum": 2,
                                "mobileBlackoutWindowStartTime": "17:00", "mobileBlackoutWindowEndTime": "11:00"},
     "metaData": {"store": {"selectedContentBuilderMessage": "<body incl. AMPscript>",
                            "messageConfiguration": {"selectedCode": {"countryCode": "AU"}}}}}
  ]
}
```

Rules:
- Keep every activity and every outcome, including trailing 1-minute waits with no `next`. The parser uses them to detect path ends.
- `next` absent = path ends there.
- Keep criteria XML verbatim, including `ValueIsReference` and `ValueParameterName` attributes. They drive the cross-object flag.
- For unknown activity types keep `type`, `name`, `outcomes` and the full `configurationArguments`.
