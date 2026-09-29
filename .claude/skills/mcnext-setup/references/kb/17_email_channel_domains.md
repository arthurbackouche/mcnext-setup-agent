# Email channel: domains, from addresses, reply mail, tracking

Covers check S13 (default email channel / sending domain). Consent and physical address content lives in `18_consent.md`.

## Steps

### Domain authentication (first step of the chain)

1. Salesforce Setup > "Set-up Email" > Go to Authenticated Domains > **+ Add a Domain**. Enter a **dedicated subdomain** (convention: `e.` or `email.` prefix, e.g. `e.example.com`) — deliberately not the root domain, so web-traffic reputation does not affect email domain reputation. [AB:domain-auth-mcn] [AB:configure-mcn]
2. Create an email address for that domain (e.g. `marketing@e.example.com`). Click "Manual DNS Record Information" under "Update the DNS Records", copy the listed records into the domain registrar's DNS tab (e.g. GoDaddy). Click "Apply Change" to validate. [AB:domain-auth-mcn]
3. **DNS validation is asynchronous and can take up to 72 hours** — do not expect immediate success after Apply Change. [AB:domain-auth-mcn]

### From Addresses (depends on step 1-3)

4. On the Authenticated Domain, "show details" > **From Addresses** > "+ Add From Addresses" > Display Name + Username (app builds full address from domain + username). Repeat for each sender identity needed. [AB:from-addresses-mcn]
5. Avoid free webmail domains (Gmail/Hotmail) as From Address — flagged as spammy. Avoid no-reply addresses. Use per-purpose addresses (sales@, marketing@, support@, events@). [AB:from-addresses-mcn]

### Reply Mail Management (depends on step 1-3, sits alongside From Addresses)

6. Authenticated Domain > "show details" > **Reply Mail Management** tab. Reply Filters: set "Delete Auto replies and Out-of-Office message" to Yes (recommended, avoids inbox flooding). Responses: auto-response text sent on reply. Routing: configure routing rules for incoming replies. Save. [AB:rmm-mcn]

### Tracking Domain (independent branch, own DNS + external CA flow)

7. Salesforce Setup > Certificate and Key Management > "Create CA-Signed Certificate" (Key Size 2048). Download the CSR. Submit it to **ZeroSSL** (external, free) for a 90-day SSL certificate; validate domain ownership via DNS at the registrar; download the resulting cert/key and upload it back into Salesforce Certificate and Key Management. [AB:tracking-domain-mcn]
8. Salesforce Setup > "Links" > "Create New" > select the custom tracking domain > Activate. [AB:tracking-domain-mcn]

### Email-related personalisation and test sends (dependency, cross-ref `16_data_graph.md` and `18_consent.md`)

9. Test-sending a personalised email requires the test recipient to already be an **opted-in** contact — see `18_consent.md`. Sender/domain authentication must be complete for delivery. [AB:merge-fields-mcn]

## Limits

- DNS validation: up to 72 hours. [AB:domain-auth-mcn]
- ZeroSSL certificate validity: 90 days (recurring renewal implied but not confirmed by the article — inferred no auto-renewal). [AB:tracking-domain-mcn]
- No cap stated on the number of From Addresses.

## Gotchas

- Using the root domain instead of a dedicated subdomain for email sending is explicitly discouraged. [AB:configure-mcn]
- A 90-day cert expiry implies a recurring renewal task; the article does not mention auto-renewal (inferred, needs a reminder).
- Shared sending domains carry over during a migration, but IPs and reputation do not — plan a **4 to 8 week warm-up**. [AB:worth-migrating-mcn]
- Test email personalisation failures: check (1) recipient is opted-in, (2) sender profile/domain is authenticated, (3) email not filtered to spam/junk. [AB:merge-fields-mcn]

## Automation route

- **UI-only** across every step in this file. DNS record creation happens outside Salesforce at the domain registrar — not automatable via any Salesforce tool. ZeroSSL steps are external web UI, not API-driven per this KB.

## Verification

- Authenticated Domains page shows the domain as validated once DNS propagates.
- From Addresses list under the domain's detail page shows the configured addresses.
- Reply Mail Management tab shows saved filter/response/routing config.
- Links page shows the custom tracking domain as Active.

## Sources

[AB:domain-auth-mcn] How to setup the Domain Authentication in Marketing Cloud Next
[AB:configure-mcn] How to configure Marketing Cloud Next
[AB:from-addresses-mcn] How to configure From Addresses in Marketing Cloud Next
[AB:rmm-mcn] How to Configure Reply Mail Management In Marketing Cloud Next
[AB:tracking-domain-mcn] How to configure the Tracking Domain in Marketing Cloud Next
[AB:merge-fields-mcn] How to Personalise Emails with Merge Fields in Marketing Cloud Next
[AB:worth-migrating-mcn] Is it worth migrating to Marketing Cloud Next now
