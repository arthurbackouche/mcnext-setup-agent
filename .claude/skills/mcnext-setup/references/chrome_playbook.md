# Chrome playbook for Salesforce Setup

How to drive Lightning Setup, the Data Cloud app and Marketing Setup with Claude in Chrome without a human. Browser technique only; the per-step routes are in `setup_routes.md`. Everything here comes from failures and fixes on live orgs.

## 1. Session hygiene
- **One Chrome agent at a time.** Agents share one tab group and close each other's tabs. If `tabs_context_mcp` suddenly reports no tab group, or returns a different `tabGroupId` than before, stop Chrome work and return `blocked: chrome concurrency`. Do not keep opening tabs. Ask the user not to use that Chrome window during a run.
- Start with `tabs_context_mcp`, then `tabs_create_mcp` with a full URL. Never reuse a tab id from an earlier run.
- Every tab must `navigate` to a full URL before any action: the guard tracks the host per tab. Links with `target="_blank"` open a new tab with no registered host: `navigate` that tab to its own URL first, then act.
- Confirm the host on the first screenshot of each step: a `.sandbox.` host, or the My Domain of a demo/trial org the user has trusted.
- A tab that stops responding: close it, open a new one, navigate by URL. Avoid the App Launcher on the Sales home page.
- Screenshots sometimes show the page tiled 2x2 or 4x4. Harmless: act on the top-left tile, the next navigation renders normally.
- Login page, MFA, or any `exacttarget.com` / `marketingcloudapps.com` window: stop and hand back. Never type credentials.

## 2. Guard rules that shape tool choice
- Reads always pass: `read_page`, `find`, `get_page_text`, `screenshot`, `read_console_messages`, `read_network_requests`.
- Clicks, typing and `form_input` pass on sandbox hosts and on demo/trial orgs covered by an active `trust:org:<mydomain>` grant. Production Salesforce and MCE hosts need approval.
- Never use `browser_batch`: the guard sees no known host and blocks it.
- `javascript_tool` passes only on sandbox/trusted hosts, and only if the script contains none of `fetch`, `XMLHttpRequest`, `location`, `window.open`, `sendBeacon`, `.submit(`, `import(`. Scripts that return values containing `=` or base64 can be refused by the auto-mode classifier: read such values with `find`/`read_page` instead.
- "Auto mode classifier gave no verdict" is transient: wait, retry once.

## 3. Interaction ladder (per control, stop at the first rung that works)
Take a fresh `read_page` of the smallest container before each rung; refs go stale after any re-render. Count one attempt per rung and log it.

1. **Ref click on the right role**: `button`, `checkbox`, `option`, `radio`, `switch`, `tab`, never an inner text node. Comboboxes: click the combobox, then `read_page` the listbox (for virtualised pickers use `filter="all"` and depth 30+) and click the `option` ref. Coordinate clicks in scrolled pickers pick the wrong option.
2. **`form_input` on the ref** for inputs, selects, checkboxes. Search and Quick Find boxes often ignore plain `type`: `find` a fresh ref, then `form_input`, then one real keystroke (End, BackSpace, one character) to fire the live filter.
3. **Keyboard**: Space for checkboxes and toggles, Down/Enter for comboboxes. Verify: keyboard has picked the wrong option before.
4. **Script through shadow DOM** (sandbox/trusted only):
   ```js
   const all=[];(function walk(r){r.querySelectorAll('*').forEach(e=>{all.push(e);if(e.shadowRoot)walk(e.shadowRoot);});})(document);
   const hit=all.filter(e=>(e.getAttribute('aria-label')||e.textContent||'').trim()==='<label>');
   if(hit[0]){hit[0].scrollIntoView({block:'center'});hit[0].click();}
   'found '+hit.length
   ```
   Disabled-by-design checkboxes (Data Graph field lists): find `input[type=checkbox]` by its `value` (the field id), set `checked`, then dispatch `change` and `input` with `{bubbles:true,composed:true}`. Buttons that ignore `.click()`: dispatch `pointerdown`, `mousedown`, `pointerup`, `mouseup`, `click`.
5. **Reset**: navigate to the same URL, reopen the wizard, redo rungs 1 to 4 on that control only.
6. **Alternative route**: another page reaching the same state (record page vs wizard, related list, list view "New", Quick Find, CLI or metadata).
7. **Hand back** only after rungs 1 to 6: record control, rungs, screenshot, and the exact manual steps in `out/setup/runbook.md`. Move to the next independent step.

Do not climb the ladder on a control that is disabled because a dependency is still running (e.g. Generate Ruleset while kits deploy): poll the dependency.

## 4. Classic Setup pages inside iframes
Company Information, permission-set "Data Cloud Data Space Management", and other classic pages render inside a same-origin `vfFrameId_...` iframe, often nested in a shadow root. `read_page`/`find` see only the Lightning chrome around it. Use the shadow-DOM walk to find the `iframe`, then work on `iframe.contentDocument`: set inputs by name/id, click Save (`input[name=save]` or an id ending `saveButton`), dismiss confirm dialogs (e.g. id `simpleDialog0button0`). Verify by reloading and reading the values back, or with SOQL.

## 5. Verify, never assume
- After each change: reload, then read the value back. A focus outline is not a change.
- Prove it with SOQL or the saved page state before marking `done`. Wait about 10 seconds after a reload before trusting a "not done" status: status lists render stale placeholders first.
- Async feature installs: the product's own status tab (Template, Status=Success, Monitoring "Task Overview N/N") is the signal, not the checklist button.
- Toggles that look reverted after reload (Einstein features): click again; a "disable?" dialog means it is on, click Cancel.
- Long grids with truncated values (DNS records): read each cell with `find`/`read_page`; a second grid can sit below the first.
- Record a GIF per step with `gif_creator` in `out/setup/` when practical.

## 6. Known controls (generic)
| Control | Behaviour | What works |
|---|---|---|
| Basic Settings "Try Again" on a failed item | fixes transient failures | rung 1 |
| Select a Data Space (Basic Settings) | opens with 0 options | see setup_routes S9: provisioning still running, or data space not granted per permission set |
| Data kits "Deploy" | one button for all kits; rows flip one by one | rung 1, then poll rows |
| Generate Ruleset | natively disabled while kits deploy; can enable before the last kit finishes | poll its disabled state; after Generate, Run the ruleset from its record page |
| Data Graph edit | name link opens read-only view | row menu > Edit; Save Draft or Save and Build (plus the schedule modal's own button); build is async |
| Data Graph add related object | only offers relationships declared on nodes already in the graph | find the target DMO's relationships in Data Model, add it from that source node |
| Relationship cardinality picker | selections revert | click the `option` ref from `read_page` right after opening |
| Lightning App Builder components | drag and drop silently fails | select a component to reveal the "+" insertion point, click it, then click the component in the left panel |
| Classic Clone / Save buttons | invisible to `find` | iframe contentDocument (section 4) |
| Company Information Save | fails "Security Contact: name is required" | collect Security Contact name, email, phone in the intake |
| Flow Performance data space | resets on reload | re-select before each Install |
| Identity Resolution match rule radios | ignore ref and label clicks | rung 2, then rung 4 |
| "New DMO > From Existing" wizard | can hang on the DLO fetch | reload the whole page, else use the Data Stream's Data Mapping route |
| View Objects toggle (new CRM stream) | ignores clicks | rung 4 dispatch, then the bundle view's search box |

Add generic rows only (page, control, what worked). No org names, hosts, record names or counts.

## 7. Non-UI routes worth trying first
- Licences and permission sets: `sf org assign permsetlicense|permset -o <alias>`.
- Data 360 enablement: Metadata API `Settings:CustomerDataPlatform` (see setup_routes S3).
- Metadata retrieve (read-only) to learn shapes: `sf project retrieve start -o <alias> -m "<Type>:*"`. Deploy only after a dry run.
- Data 360 REST `/services/data/vXX.X/ssot/connections` for generic connectors; GET a UI-built object first as the template.
- Consent seeding: Consent Imports CSV, or a Draft record-triggered flow with the `MessagingConsent` action (1-minute scheduled path).
