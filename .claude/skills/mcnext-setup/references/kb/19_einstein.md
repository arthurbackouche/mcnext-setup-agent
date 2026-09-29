# Einstein AI features

Covers check S17 (Einstein toggles: Metrics Guard, Send Time Optimization, Engagement Frequency, Engagement Scoring).

## Steps

### Einstein Metrics Guard (no prerequisite)

1. Setup > Assistant Home > "Set up Email" > "Go to Email Feature Settings" > "Activate Einstein Metrics Guard" > turn on the toggle. [AB:einstein-metrics-guard-mcn]
2. Purpose: filter bot/scanner/auto-open traffic (e.g. Apple Mail Privacy Protection) out of Open/Click metrics. Confidence score scale 0-100 (0 = bot, 100 = human), built on time-series + predictive models. [AB:einstein-metrics-guard-mcn]
3. This is the only one of the 4 Einstein features with **no Data Graph or Identity Resolution prerequisite stated**.

### Einstein Engagement Frequency (needs an existing Data Graph)

4. Setup > Assistant Home > Set Up Email > Optional Setup > "Go to Einstein Settings" > "Enable Einstein Engagement Frequency" section > Enable on the "Einstein for Marketing" page. [AB:einstein-frequency-mcn]
5. Edit your Data Graph and add the "Email Engagement Frequency" DMO as a related object; select fields "Email Engagement Classification" and "Email Engagement Frequency". Enabling the toggle alone does not wire it into flows — the DMO must be manually added to the graph. [AB:einstein-frequency-mcn]
6. In a Marketing Flow, drag the Einstein Decision element, select "Frequency" — splits into 4 sub-paths: Saturated, AlmostSaturated, OnTarget, Undersaturated. [AB:einstein-frequency-mcn]

### Einstein Engagement Scoring (needs an existing Data Graph, can share the Frequency graph)

7. Same navigation path, "Enable Einstein Engagement Scoring" section. [AB:einstein-scoring-mcn]
8. Edit the existing Data Graph, add "Einstein Engagement Score" DMO, select fields: Email Click Likelihood, Email Click Score, Email Subscribe Likelihood, Email Subscribe Score, Email Open Score, Email Open Likelihood, Email Engagement Persona. [AB:einstein-scoring-mcn]
9. In a Marketing Flow, Einstein Decision element > "Scoring" > 4 split types: Open Likelihood, Click Likelihood, Subscribe Likelihood, Persona. Persona options: Loyalist, Selective Subscriber, Window Shopper, Winback/Dormant. Likelihood options (each type): Most Likely, More Likely, Less Likely, Least Likely. [AB:einstein-scoring-mcn]
10. Confirmed: the two Einstein features (Frequency and Scoring) can share the same Data Graph, built incrementally. [AB:einstein-scoring-mcn]

### Einstein Send Time Optimization (needs Identity Resolution + Data Graph)

11. Explicit prerequisites: (1) an Identity Resolution Ruleset created on the Individual DMO, (2) a Data Graph created. [AB:einstein-sto-mcn]
12. Setup > Assistant Home > "Email Channel Configuration" > "Go to Einstein Settings" > "Activate Einstein Send Time Optimization" > enable "with global model (Pooled data)". [AB:einstein-sto-mcn]
13. Org-specific model is a separate, later option once enough org email volume exists (needs 90 days of the org's own send history); the article does not walk through enabling it. [AB:einstein-sto-mcn]
14. Usage: in a Campaign Flow's Email element, toggle STO on, set "Send Emails Within" (e.g. next 24 hours). [AB:einstein-sto-mcn]
15. Monitoring: Report tab > "Data Cloud" > "Einstein Send Time Optimization" report, or "Contact Point Email with Email Send Time Optimization" report. Fields: Organization Id, Contact Point Email Id, Time of Week (0-167, Monday midnight = 0, Sunday 11pm = 167), Created Date. [AB:einstein-sto-mcn]

### Advanced Edition note

16. Einstein Engagement Scoring and Einstein Engagement Frequency are stated as **"available only in Marketing Cloud Next Advanced Edition"**. [AB:configure-mcn]
17. Einstein Send Time Optimization requires opting in to "Global Data Model for Einstein" in Growth Edition; in Advanced Edition you can enable or disable global models. [AB:configure-mcn]

## Limits

- Engagement Frequency: **minimum 10 subscribers** required to model; **minimum 5 frequency variants** required (audience must receive at least 5 distinct send-interval variants over a **28-day period**). [AB:einstein-frequency-mcn]
- STO global model activation: **up to 72 hours** after enabling before usable. Org-specific model uses trailing **90 days** of send data; org-specific insights refresh **weekly**. Time of Week is a 0-167 integer scale. [AB:einstein-sto-mcn]
- Engagement Scoring: no minimum volume stated (contrast with Frequency).
- Metrics Guard: no timing/volume thresholds stated.

## Gotchas

- Modeling for Engagement Frequency will not activate below the 10-subscriber / 5-variant/28-day thresholds (inferred consequence, not an explicit error message).
- Metrics Guard's model is trained on Salesforce's own aggregated (anonymized) customer data from MCE/Account Engagement history, not the org's own data alone — a data-provenance point to flag to the client, not a technical blocker. [AB:einstein-metrics-guard-mcn]
- STO's global model shares only anonymized data across orgs (no email address, company, etc.) — not a privacy risk to enable, but predictions are generic until enough org-specific volume exists. [AB:einstein-sto-mcn]
- S10 (identity resolution) and S11 (Data Graph) block STO specifically; Metrics Guard can be enabled independently of both.

## Automation route

- **UI-only** for every Einstein toggle, Data Graph edit, and Flow Decision element in this KB. No API given anywhere.

## Verification

- Einstein Settings page shows the feature enabled.
- Data Cloud Object Explorer shows the added DMO's fields populated (e.g. "Email Engagement Classification").
- Flow Einstein Decision element offers the relevant sub-paths (Frequency or Scoring).
- STO: after 72 hours, the toggle is available inside an Email flow element; the two named reports return Time of Week data per Contact Point Email Id.

## Sources

[AB:einstein-metrics-guard-mcn] What is Einstein Metrics Guard in Marketing Cloud Next
[AB:einstein-frequency-mcn] How to setup Einstein Engagement Frequency in Marketing Cloud Next
[AB:einstein-scoring-mcn] How to setup Einstein Engagement Scoring in Marketing Cloud Next
[AB:einstein-sto-mcn] How to setup Einstein Send Time Optimization in Marketing Cloud Next
[AB:configure-mcn] How to configure Marketing Cloud Next
