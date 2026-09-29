# Permissions and users

Covers checks S2 (entitlement/licences), S5 (permission sets exist), S6 (running user has them).

## Steps

1. Assign **Data Cloud Architect** permission set to the implementer first. Setup > Permission Sets > Data Cloud Architect > Manage Assignments > add user > Assign. Refresh the browser afterward or Data Cloud Setup will not appear in the gear menu. [AB:setup-d360] [AB:setup-datacloud-mcn]
2. This permission set may be named **Data Cloud Admin** instead of **Data Cloud Architect**, depending on org age/release. Same permission set, renamed by Salesforce; Architect is the current name. Search PermissionSet by both labels. [AB:setup-datacloud-mcn]
3. Data Cloud Architect/Admin grants: Data Cloud Setup, data model mapping, data streams, identity resolution rulesets, insights. [AB:setup-datacloud-mcn]
4. Assign **Marketing Cloud Admin** to the implementer before touching Basic Settings. This is required for the Data Space picker in Basic Settings to be usable. Setup > Permission Sets > search "Marketing Cloud Admin" > Manage Assignment > select user > No expiration date (or set one) > Assign. [AB:setup-mcn] [AB:permsets-mcn]
5. Two out-of-the-box MC Next permission sets exist: **Marketing Cloud Admin** and **Marketing Cloud Manager**. Admin also grants Salesforce Setup and Admin Flow access (flows with CRM elements) — this worries CRM admins. Manager does not get Setup/Flow access but still gets Agentforce and Prompt Template access. [AB:permsets-mcn]
6. A custom permission set can be built instead, scoped across: CMS Content Roles, General Marketing Permissions, Consent Permissions in Marketing Cloud Next, Content and Publishing Permissions, Flow Permissions in Marketing Cloud Next. Recommended for marketers who should not touch Salesforce Flows. [AB:permsets-mcn]
7. Other permission sets named in the series, assign as needed per feature: **Personalization Intelligence User** (Salesforce Personalization), **Tableau Next Included App Business User** (view Marketing Performance dashboard). [AB:sf-personalization-mcn] [AB:setup-mcn]
8. A **Flow User** designation and Flow Sharing (separate from permission sets) is required on the specific flow for any user/integration calling it via the On-Demand Flow REST API. [AB:on-demand-flow-mcn]

## Limits

- Two standard MC Next permission sets only (Admin, Manager) unless a custom one is built. [AB:permsets-mcn]
- No numeric caps stated for permission set assignment itself.

## Gotchas

- **Greyed-out Data Space picker in Basic Settings is the single most-cited failure mode across the whole series.** Cause: user lacks Marketing Cloud Admin. [AB:setup-mcn] [AB:data-kits-mcn]
- Permission set naming is inconsistent across articles: "Data Cloud Admin" vs "Data Cloud Architect" for the Data 360 side, and no article confirms whether both the Data Cloud family and the Marketing Cloud family are needed simultaneously, or just one for a given task. Treat S5/S6 checks as needing to search both families. (inferred — batch A cross-cutting)
- Marketing Cloud Admin grants access CRM admins are often uncomfortable with (Setup, Admin Flows). Recommend Marketing Cloud Manager for day-to-day marketers.

## Automation route

- Permission set **assignment** is CLI-doable once the exact API name is known: `sf org assign permset -n <PermissionSet.Name> -o <alias>`. This matches skill Part 2 Step A.
- Permission set **licence** assignment (if required before the permset assignment succeeds): `sf org assign permsetlicense -n <PSL DeveloperName> -o <alias>`.
- Building a custom permission set (choosing specific permission categories) is UI-only; no metadata API route given in any article.
- Everything else (enabling Data Cloud, Basic Settings visibility) is UI-only.

## Verification

- `SELECT Id, Name, Label FROM PermissionSet WHERE Label LIKE '%Marketing Cloud%' OR Label LIKE '%Data Cloud%' OR Label LIKE '%Data 360%'` — search both naming families.
- `SELECT PermissionSet.Label FROM PermissionSetAssignment WHERE AssigneeId = '<user id>'` for the running user.
- UI: Permission Set detail page > Manage Assignment shows the assigned users list.

## Sources

[AB:setup-d360] How to set-up Data 360
[AB:setup-datacloud-mcn] How to set-up Data Cloud for Marketing Cloud Next
[AB:setup-mcn] How to set-up Marketing Cloud Next
[AB:data-kits-mcn] How to use Data Kits in Marketing Cloud Next
[AB:permsets-mcn] How to configure the Permission Sets in Marketing Cloud Next
[AB:sf-personalization-mcn] How to Setup Salesforce Personalization for Marketing Cloud Next
[AB:on-demand-flow-mcn] How to Trigger On-Demand Flows with REST API in Marketing Cloud Next
