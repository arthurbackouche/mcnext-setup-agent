# Analytics packages and reports

Covers checks S18 (analytics package choice/install) and S19 (share access to analytics folders).

## Steps

1. Prerequisite: **Marketing Data Kits (S8) must be deployed first** — explicit "Pre-requisites" heading in the source article. [AB:analytics-packages-mcn]
2. Setup > Assistant Home > "Marketing Performance" card > "Set Up Marketing Performance" > "Go To Marketing Data" next to "Install Marketing Data Kits" > confirm all kits deployed. [AB:analytics-packages-mcn]
3. **Analytics packages are installed from a separate Setup menu item**, not the Marketing Performance page: Setup > **"Analytics"** (under "Reporting and Optimization"). Install: [AB:analytics-packages-mcn]
   - Marketing Engagement Analytics package (email interaction insights)
   - SMS Analytics package (SMS interaction insights)
   - Landing Pages and Forms Analytics Package
   - Flow Reports Analytics Package (flow action run counts/status)
4. For each package: click "Install for Admin only" and confirm. [AB:analytics-packages-mcn]
5. Also required, as a **separate step, not automatic after install**: **"Share Access to Analytics Folders"** so the team can see the reports (S19). [AB:analytics-packages-mcn]
6. Access reports: Marketing App > Analytics tab — Email, SMS, Landing Pages & Forms, Flow Engagement. [AB:analytics-packages-mcn] [AB:reports-types-mcn]
7. "Marketing Cloud Manager" permission (not Admin) is what's needed to edit/share reports and dashboards, per the article's "How to manage Analytics Access" section. [AB:analytics-packages-mcn]
8. Campaign-level reports live on the Campaign record itself, not the Analytics tab: Marketing Performance tab > campaign record > "Campaign Performance dashboard (Insights)" (CTR, Sends, Open Rate, Delivery Rate, Click Rate, Bounce Rate, Opt-Out Rate; filterable by date range, Campaign Flow, Segment) and "Campaign Performance dashboard (Deliverability)" (Delivery Rate, Sends, Bounce Rate, Deliveries, Failed to Send, Bounces, Hard/Soft Bounced, Opt-Out Rate). [AB:reports-types-mcn]
9. Flow Builder: on a Send Email Message element, an Analytics tab shows run counts by status (Completed, Error, Waiting, Retrying) and Average Duration. [AB:reports-types-mcn]
10. **All of these dashboards/reports rely on the D360 (Data Cloud) Report feature** — Marketing Cloud Next reporting is built on Data Cloud reports and can be customised like any Data Cloud report. [AB:reports-types-mcn]
11. Separate AppExchange package for MCE-specific reporting inside Data 360 (not the MC Next analytics packages above): Setup > search AppExchange > **"Data Cloud Report Package for Marketing Cloud Engagement"** (Salesforce Labs) > Get It Now > Install for Admins Only. Reports appear in Data 360 > Report tab > "Data Cloud Report Installed" folder: Email Send Report, Email Performance Report, Email Bounce Summary Report, Email Domain Performance Report, Email Spam Complaint Report. Requires the MCE connector and Email/Mobile Studio bundles already ingested for reports to have data. [AB:intelligence-reports-d360]
12. Calculated Insights are a related, separate reporting mechanism built via SQL — see `13_crm_connector_streams_mapping.md` and the Email Engagement scoring example in that file's source article, `12_data_kits.md`.

## Limits

- No count of packages beyond the 4 named for S18, no size/refresh numbers stated for any analytics package.
- Calculated Insight refresh example: every 24 hours (configurable, not a hard limit).

## Gotchas

- **Package naming ambiguity, not resolved by this KB:** the direct how-to article names exactly 4 packages (Marketing Engagement Analytics, SMS Analytics, Landing Pages and Forms Analytics, Flow Reports Analytics) and never uses the terms "CRM Analytics" or "Marketing Performance Intelligence" anywhere. Whether those two terms are alternate/legacy names for the same 4 packages, a superset, or a different product is **unknown** — needs a direct check in the a live org Setup > Analytics page or a Salesforce Help lookup, not an assumption. [AB:analytics-packages-mcn]
- Folder sharing (S19) is a distinct, required step — not automatic after package install.
- AppExchange package install requires the underlying MCE bundles already ingested or reports will have no data (inferred).

## Automation route

- **UI-only** for package install ("Install for Admin only"), folder sharing, and viewing reports/dashboards.
- AppExchange package install is UI-only per this KB (no CLI package-install command given in any article, though `sf package install` generally exists for this purpose outside this KB's scope — not confirmed here).
- SQL authoring for Calculated Insights happens through the Data 360 Calculated Insights UI; the SQL read mechanism matches the `d360_query_sql`-style tool used elsewhere in this project, but article does not confirm the Calculated Insight *object itself* can be created via API.

## Verification

- Marketing App > Analytics tab shows Email/SMS/Landing Pages & Forms/Flow Engagement reports.
- Each package shows an installed state in Setup > Analytics.
- Presence of the named dashboards/reports under the Analytics tab and on Campaign records is itself the verification that S18 packages installed correctly.
- Data 360 > Report tab > "Data Cloud Report Installed" folder populated confirms the AppExchange package installed.

## Sources

[AB:analytics-packages-mcn] How to install Analytics Packages in Marketing Cloud Next
[AB:reports-types-mcn] Understanding the different type of Reports in Marketing Cloud Next
[AB:intelligence-reports-d360] How to Set up the Intelligence Reports in Data360
