# Setup intake

Collect every answer **before the first change in the org**, in one message to the user. The setup then runs without questions. Answers are stored in the engagement at `out/setup/intake.json` (template: `scaffold/setup_intake.template.json`).

```bash
python3 .claude/skills/mcnext-setup/scripts/intake.py init  <engagement dir>   # creates the file
python3 .claude/skills/mcnext-setup/scripts/intake.py check <engagement dir>   # lists what is missing
python3 .claude/skills/mcnext-setup/scripts/intake.py plan  <engagement dir>   # steps skipped by the answers
```

## Questions to ask (copy this list to the user)

**Org access**
1. My Domain of the target org (the part before `.my.salesforce.com` or `.lightning.force.com`).
2. Is it a sandbox, or a demo/trial org you want treated like a sandbox? Production orgs are not supported.
3. Edition: Growth or Advanced.
4. The Salesforce username that runs the setup. It receives the admin licences and permission sets.

**Data**
5. Data space: `default` unless you have a reason. The choice is permanent.
6. Marketing Cloud Engagement tenant EID to connect, or none.

**Email compliance** (Company Information cannot be saved without both)
7. Company physical address for the email footer: street, city, state, postcode, country.
8. Security contact: name, email, phone.

**Sending domain** (optional)
9. A root domain you control (DNS access needed), or skip. The agent creates a dedicated subdomain, default `e.<domain>`.
10. From display name and username (default `marketing`).
11. Activate the domain after you add the DNS records? (yes/no; validation up to 72 h)

**Testing and options**
12. Test recipient email for consent seeding and a first test send, or skip.
13. Install analytics apps? (default yes)
14. Einstein features to enable (default all four: Metrics Guard, Send Time Optimization, Engagement Frequency, Engagement Scoring).
15. Add Data 360 components to a new Contact record page? Activate it, or leave it for review? (default: build, do not activate)

## Before the first change, also get
- `sf org login web -a <alias> -r <login url>` done by the user.
- The user logged in to the org in Chrome, and not using that window during runs.
- For a demo/trial org: the user's trust grant, from their own terminal, in the engagement folder:
  `python3 scripts/approve.py "trust:org:<mydomain>" --reason "<why>" --ttl 720`
  It expires on its own (12 h here). Agents never create it.

## Rules
- Never invent an address, contact, domain or recipient. Missing answer = the step is skipped or handed back.
- Personal data from the intake stays in the engagement folder. Never copy it into the framework, skills or memory.
