# Chrome playbook for Salesforce Setup (sandbox)

How to drive Lightning Setup, the Data Cloud app and Marketing Setup through Claude in Chrome without a human. Every rule here comes from failures and fixes logged in `out/setup/actions.log` (2026-09-23/24) or from the guard hook.

## 1. Session hygiene
- **One Chrome agent at a time.** Two agents share one tab group and close each other's tabs within 2 to 4 calls. If your tab disappears, stop Chrome work and return `blocked: chrome concurrency`. Do not keep opening tabs.
- Start: `tabs_context_mcp`, then `tabs_create_mcp` with the full sandbox URL. Never reuse a tab id from an earlier run.
- Every tab must `navigate` to a full URL before any click. The guard tracks the host per tab and blocks actions on a tab with no known host.
- Sandbox hosts contain `.sandbox.` (e.g. `<mydomain>--<sandbox>.sandbox.my.salesforce-setup.com` for Setup, `<mydomain>--<sandbox>.sandbox.lightning.force.com` for apps). Confirm the host and the "Sandbox" banner on the first screenshot of each step.
- If a tab stops responding ("Cannot access chrome-extension URL"), close it, open a new one and navigate by URL. Do not click App Launcher on the Sales home page: it froze a tab once.
- Login page, MFA, or any `exacttarget.com` / `marketingcloudapps.com` window: stop and hand back. Never type credentials.

## 2. Guard rules that shape tool choice
- Reads always pass: `read_page`, `find`, `get_page_text`, `screenshot`, `read_console_messages`, `read_network_requests`.
- Clicks, typing and `form_input` pass on sandbox hosts. On production Salesforce or MCE hosts they need approval.
- Never use `browser_batch`: the guard checks it as a tab with no known host and always blocks it. Use single `navigate` / `computer` / `find` / `javascript_tool` calls.
- Transient "auto mode classifier gave no verdict" errors happen mid-run. Wait briefly and retry the same call once.
- `javascript_tool` passes **only on sandbox hosts** and only if the script text contains none of: `fetch`, `XMLHttpRequest`, `location`, `window.open`, `sendBeacon`, `.submit(`, `import(`. On any other host (medium.com included) it needs approval. Reading pages elsewhere: use `read_page` / `get_page_text`.

## 3. Interaction ladder (per control, stop at the first rung that works)
Take a fresh `read_page` of the smallest container (dialog, panel, table) before each rung. Refs go stale after any re-render.

1. **Ref click on the right role.** Click the element whose role is `button`, `checkbox`, `option`, `radio`, `switch` or `tab`, not an inner `generic`/text node. For comboboxes: click the combobox ref, then immediately `read_page` the listbox subtree and click the `option` ref. (This fixed the Relationship Cardinality N:1 picker after 10 failed coordinate and keyboard tries.)
2. **`form_input` on the ref** for native inputs, selects and checkboxes (sets value and fires change events).
3. **Keyboard.** Focus the ref, then `key` Space (checkbox, toggle) or Down/Enter (combobox), or type ahead then Enter. Verify the value after, since keyboard once picked the wrong option (1:1 instead of N:1).
4. **Scripted click through shadow DOM** (sandbox only). Lightning renders inside shadow roots, so plain selectors miss it. Use this helper, then act on one element and return a short string:
   ```js
   const all=[];(function walk(r){r.querySelectorAll('*').forEach(e=>{all.push(e);if(e.shadowRoot)walk(e.shadowRoot);});})(document);
   const hit=all.filter(e=>(e.getAttribute('aria-label')||e.textContent||'').trim()==='View Objects');
   if(hit[0]){hit[0].scrollIntoView({block:'center'});hit[0].click();}
   'found '+hit.length
   ```
   For a checkbox: find the `input[type=checkbox]` in the row, call `.click()`; if the state does not change, set `checked` and dispatch `new Event('change',{bubbles:true,composed:true})` and `new Event('input',{bubbles:true,composed:true})`. For buttons that ignore `.click()`, dispatch `pointerdown`, `mousedown`, `pointerup`, `mouseup`, `click` in order with `{bubbles:true,composed:true}`.
5. **Reset and retry once.** Reload the page (navigate to the same URL), reopen the wizard or editor, redo rung 1 to 4 on that control only.
6. **Alternative route.** Look for another way to reach the same end state: a different page (e.g. Data Stream record vs wizard), a related-list button, a "New" from a list view, a Setup Quick Find entry, or a CLI or metadata route (section 6).
7. **Hand back.** Only after rungs 1 to 6 fail. Record the control, the rungs tried and a screenshot. Write the exact manual clicks for the user in `out/setup/runbook.md`, then move to the next independent step.

Count one "attempt" per rung, not per click. Log each rung in `out/setup/actions.log`.

## 4. Verify, never assume
- After each change: reload, screenshot, and read the value back (`read_page` or `find`). A focus outline is not a change: the graph editor showed focus with no toggle.
- Then prove it with a Part 1 check (SOQL, d360 read or visible saved state). Only that marks a step `done`.
- Record a GIF for each step with `gif_creator` (e.g. `setup_S11_graph_fields.gif`), saved to `out/setup/`.

## 5. Known controls (generic Lightning behaviour seen in live orgs)
| Control | Where | Status | What worked or next rung |
|---|---|---|---|
| Unified Individual Object combobox | Basic Settings | solved | find + ref click on 3rd try; listbox options then clickable |
| Relationship Cardinality picker | DMO > Relationships > New | solved | read_page dialog subtree right after opening, click `option` ref |
| Configure Basic Personalization graph picker | Assistant Home > Customer Engagement | solved | listbox `option` ref click, auto-saves |
| Data kits | Basic Settings | solved | one "Update" button deploys all kits (up to 30 min) |
| Generate Ruleset button | Basic Settings | solved when one Chrome agent | tab closures were concurrency, not the UI |
| View Objects toggle | Data Streams > New > Salesforce CRM | open | failed on coordinate, ref, double click. Next: rung 4 dispatch sequence; then rung 6 (bundle view search box, or Data Cloud Setup > Salesforce CRM > object picker) |
| Data Graph field checkboxes | Data Graph editor, the `editor_view` page reached by clicking the graph name in the Data Graphs list | dead end | this page is READ-ONLY: no Save button exists at all. Checkbox toggles (any rung) update the live field count but are always discarded on navigation. Do not use this entry point to edit a graph. |
| Data Graph field checkboxes | Data Graph editor, the `editor_edit` page reached by Data Graphs list row > Show Actions (kebab) > Edit | solved | rung 4b: checkboxes are natively `disabled` (by design). Find `input[type=checkbox]` via a light+shadow-DOM walk matched by its `value` attribute (= field id), set `checked=false`, then `dispatchEvent(new Event('change',{bubbles:true,composed:true}))` and the same for `'input'`. Ref click (rung 1) only focuses the row, never toggles, on both editor_view and editor_edit. A field that is the join/foreign-key to a related object (e.g. `ssot__PartyId__c`/"Party" linking Individual to Unified Link Individual) always reverts when unchecked -- protected, not a bug. Must `Save Draft` or `Save and Build` on the editor_edit page; no autosave. |
| "Add related object" combobox next to a tree node | Data Graph editor (editor_edit page) | solved | coordinate clicks after scrolling the popup are unreliable and silently select the wrong option (virtualization bug); `find()` cannot locate the option elements either. Fix: `read_page(filter="all", depth>=30)` on the whole page locates the dialog's `option` elements with stable refs (search output for the target object's exact label); click that ref directly. Works on the first try once the correct ref is used. |
| Save and Build (Data Graph editor_edit page) | Data Graph editor | solved, async | clicking `Save and Build` opens a "Set Your Data Graph's Refresh Schedule" modal; click its own `Save and Build` button too. Confirm success via `read_network_requests` for `POST aura?r=..&aura.CdpDataGraph.editDataGraph=1` returning 200 -- do NOT rely on `d360_data_graph_get` or the editor_view page updating immediately: the built/active definition only reflects the change after the graph's own schedule (e.g. every 30 minutes) runs its next build. Treat as a long job: record `running`, poll on a later run. |
| Match rule radio (Custom Rule) | Identity Resolution > Add Match Rule | open | ref and label click failed. Next: rung 2 `form_input`, then rung 4 |
| Add Data Protection Details to Records | Basic Settings | open | heading is a status indicator only. Next: `find` a link or button in that section; Quick Find "Data Protection"; Setup > Data Protection and Privacy; record what the page offers |

Update this table after every run: move items to "solved" with the rung that worked.

## 6. Non-UI routes worth trying before a hand-back
- **Permission sets and licences**: `sf org assign permset|permsetlicense -o <sandbox>` (guard allows on sandbox).
- **Metadata retrieve** (read-only, allowed): `sf project retrieve start -o <sandbox> -m "DataGraph:*"` or other Data Cloud types to learn the shape. A deploy of a changed graph or stream to the sandbox is allowed by the guard, but only after a retrieve proves the type exists. Confirm with a dry run first. Needs the `sf` login for the sandbox.
- **Data 360 REST** `/services/data/vXX.X/ssot/connections` works for generic connectors [AB:rest-connector-d360]. Not confirmed for the CRM or MCE connectors: GET a UI-built object first and use it as the template.
- **Consent seeding**: Consent Imports CSV in the UI, or a record-triggered flow with the `MessagingConsent` action (1-minute scheduled path) deployed as Draft.
