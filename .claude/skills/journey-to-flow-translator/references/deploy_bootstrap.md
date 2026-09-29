# Deploy bootstrap and procedure

The MCE and Salesforce MCP connectors cannot create flows. `sobject-all` has no Tooling or Metadata API access (confirmed: `SELECT ... FROM Flow` returns INVALID_TYPE). Deployment goes through the Salesforce CLI (Metadata API). Run it from Claude Code, or from this container with an SFDX auth URL. Claude in Chrome is the fallback.

## 1. Bootstrap templates (once per org, repeat after major releases)

Do not hand-write marketing element XML. Capture it.

1. In the target org UI, build one throwaway flow named `J2F_Template` of each trigger type you will use (usually Segment-Triggered and Record-Triggered). Each must contain:
   - Wait for Amount of Time (e.g. 3 days)
   - Decision with two outcomes plus default. One condition on a Data Graph attribute, one boolean, one text compare.
   - Send Email Message (any email)
   - Send SMS Message (any SMS)
   Save as Draft. Never activate.
2. Retrieve it:
   ```bash
   sf project retrieve start -m "Flow:J2F_Template_Segment" -o <alias>
   ```
3. Slice the XML into the template files the builder expects (see header of `scripts/build_flow_xml.py`). Replace real values with tokens. Keep every other tag exactly as retrieved: `processType`, `environments`, `processMetadataValues`, `actionType`, `actionName`, input parameter names, trigger/segment config.
4. Record in `templates/<org>/<trigger>/SOURCE.md`: org, API version, date, flow name retrieved.
5. Note the exact left-side reference syntax the Decision uses for Data Graph attributes. That syntax is what the `attributes` values in the reference map must look like.

Synthetic templates in `evals/fixtures/test_templates_NOT_ORG_CAPTURED` exist only to test wiring. Their `processType` and `actionName` values are invented and will fail deploy.

## 2. Reference map (per journey batch)

`map.json` resolves every MCE reference to its MC Next target. Build it from:
- `emails`: MCE emailId → MC Next email content reference (from the content migration register).
- `sms`: MCE SMS assetId → MC Next SMS content reference.
- `attributes`: every `source.field` in the spec's "Decision attributes" list → Data Graph field path. Query the Data Graph definition to confirm each exists.
- `units`: wait unit tokens as the template spells them.

The builder refuses to generate a flow with unresolved references. `--allow-placeholders` exists for dry runs only.

## 3. Build, validate, deploy as Draft

```bash
python3 scripts/build_flow_xml.py --ir <out>/ir/<journey>.json --templates templates/<org>/segment --map map.json --project <sfdx>
cd <sfdx>
sf project deploy start -d force-app/main/default/flows/<Flow>.flow-meta.xml -o <alias> --dry-run
sf project deploy start -d force-app/main/default/flows/<Flow>.flow-meta.xml -o <alias>
```

Status stays `Draft`. The builder never emits Active.

## 4. Verify parity from the org, not the local file

```bash
sf project retrieve start -m "Flow:<Flow>" -o <alias> -r /tmp/verify
python3 scripts/verify_parity.py --ir <out>/ir/<journey>.json --flow /tmp/verify/**/<Flow>.flow-meta.xml
```

Also confirm through the MCP that the definition exists and is inactive:
```sql
SELECT ApiName, ProcessType, IsActive, LatestVersionId FROM FlowDefinitionView WHERE ApiName = '<Flow>'
```

## 5. Cutover

Follow `cutover/<journey>.md`. Every production step is human-confirmed. Never pause, stop or publish an MCE journey or automation without explicit instruction in the conversation.
