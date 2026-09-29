"""Build slim, synthetic fixtures for a fictional client (Acme Retail, a loyalty-programme retailer)
mirroring two representative journey structures and a subset of an interaction list.
All ids, keys, names and phone numbers below are invented for testing; they do not correspond to
any real Marketing Cloud tenant."""
import json, os

HERE = os.path.dirname(os.path.abspath(__file__))
os.makedirs(os.path.join(HERE, "journeys"), exist_ok=True)


def W(k, n, d, u, nxt=None):
    o = {"key": k + "o"}
    if nxt:
        o["next"] = nxt
    return {"key": k, "name": n, "type": "WAIT", "outcomes": [o],
            "configurationArguments": {"waitDuration": d, "waitUnit": u, "specifiedTime": "00:00",
                                       "timeZone": "AUS Eastern Standard Time"},
            "metaData": {"waitType": "duration"}}

def E(k, n, eid, subj, nxt):
    return {"key": k, "name": n, "type": "EMAILV2", "outcomes": [{"key": k + "o", "next": nxt}],
            "configurationArguments": {"triggeredSend": {"emailId": eid, "emailSubject": subj, "publicationListId": 1145,
                                                         "sendClassificationId": "88d8", "senderProfileId": "d444"}}}

def S(k, n, aid, frm, cc, bs, be, body, nxt):
    return {"key": k, "name": n, "type": "SMSSYNC", "outcomes": [{"key": k + "o", "next": nxt}],
            "configurationArguments": {"assetId": aid, "fromName": frm, "isOptIn": False, "honorBlackoutWindowEnum": 2,
                                       "mobileBlackoutWindowStartTime": bs, "mobileBlackoutWindowEndTime": be},
            "metaData": {"store": {"selectedContentBuilderMessage": body,
                                   "messageConfiguration": {"selectedCode": {"countryCode": cc}}}}}

def D(k, n, branches):
    outs, crit = [], {}
    for key, label, nxt, xml in branches:
        outs.append({"key": key, "next": nxt, "metaData": {"label": label}})
        if xml:
            crit[key] = xml
    return {"key": k, "name": n, "type": "MULTICRITERIADECISION", "outcomes": outs,
            "configurationArguments": {"criteria": crit}}

def C(key, op, val, eph=True, ref=False):
    a = 'IsEphemeralAttribute="true" ' if eph else ""
    r = ' ValueIsReference="true"' if ref else ""
    return f'<Condition {a}Key="{key}" Operator="{op}"{r}><Value><![CDATA[{val}]]></Value></Condition>'

def FD(*c):
    return '<FilterDefinition><ConditionSet Operator="AND">' + "".join(c) + "</ConditionSet></FilterDefinition>"

LK = "%%[SET @StoreName = Lookup('Account_Salesforce','Name','Id',@StoreID)]%%"
EV = "Event.DEAudience-2f6e0a91-1c8d-49e0-8f2b-6a4c7d1e9b30"
EA = "Event.AutomationAud-7b3c9e02-4a1f-4d6e-8b90-2c5f1a3d6e77"
CM = "Store_Customer_Master_Deduped"
SYNTH_PHONE = "15550000000"

plan = {
    "id": "9f2e6b41-7ab0-45f0-8c2d-3ea1a2b3c4d5", "key": "42a19c01", "name": "Loyalty-Plan Renewal and Winback",
    "version": 1, "status": "Published", "entryMode": "SingleEntryAcrossAllVersions",
    "defaults": {"email": ['{{Event.DEAudience-2f6e0a91-1c8d-49e0-8f2b-6a4c7d1e9b30."Email"}}'],
                 "mobileNumber": ['{{Event.DEAudience-2f6e0a91."Phone"}}']},
    "activity": {"lastContactProcessed": "2026-05-13T20:03:12"},
    "triggers": [{"type": "EmailAudience", "metaData": {"eventDefinitionKey": "DEAudience-2f6e0a91-1c8d-49e0-8f2b-6a4c7d1e9b30"}}],
    "exits": [], "goals": [],
    "activities": [
        D("MULTICRITERIADECISIONV2-1", "", [("default_path_1", "Plan Member", "EMAILV2-1", FD(C(EV + ".Plan", "Is", "true"), C(EV + ".Loyalty_Member", "Is", "false"))),
                                             ("remainder_path", "Remainder", "WAITBYDURATION-4", None)]),
        E("EMAILV2-2", "Loyalty_Plan_RenewalTrigger_3", 40001, "%%=v(@FirstName)=%%'s Rewards Plan Has Ended", "SMSSYNC-2"),
        W("WAITBYDURATION-8", "1 minute", 1, "MINUTES"),
        E("EMAILV2-1", "Loyalty_Plan_RenewalTrigger_2", 40002, "Important: Your Rewards Plan is Changing", "SMSSYNC-1"),
        W("WAITBYDURATION-5", "3 days", 3, "DAYS", "MULTICRITERIADECISIONV2-4"),
        S("SMSSYNC-2", "Loyalty_Plan_RenewalTrigger3_SMS", 50001, SYNTH_PHONE, "AU", "17:00", "11:00", LK + "Hi...", "WAITBYDURATION-2"),
        W("WAITBYDURATION-6", "1 minute", 1, "MINUTES"),
        D("MULTICRITERIADECISIONV2-3", "", [("default_path_1", "Loyalty Non Member", "EMAILV2-2", FD(C(EV + ".Loyalty_Member", "Is", "false"))),
                                             ("remainder_path", "Remainder", "WAITBYDURATION-16", None)]),
        S("SMSSYNC-1", "Loyalty_Plan_RenewalTrigger2_SMS", 50002, SYNTH_PHONE, "AU", "17:00", "11:00", LK + "Hi...", "WAITBYDURATION-1"),
        S("SMSSYNC-5", "GroupB_Loyalty_Plan_Winback_SMS", 50003, SYNTH_PHONE, "AU", "17:00", "12:00", LK + "Hi...", "WAITBYDURATION-8"),
        D("MULTICRITERIADECISIONV2-2", "", [("default_path_1", "Loyalty Non Member", "EMAILV2-3", FD(C(EV + ".Loyalty_Member", "Is", "false"))),
                                             ("remainder_path", "Remainder", "WAITBYDURATION-15", None)]),
        W("WAITBYDURATION-3", "1 minute", 1, "MINUTES"),
        W("WAITBYDURATION-16", "1 minute", 1, "MINUTES"),
        W("WAITBYDURATION-2", "2 weeks", 2, "WEEKS", "MULTICRITERIADECISIONV2-2"),
        S("SMSSYNC-3", "GroupA_Loyalty_Plan_Winback_SMS", 50004, SYNTH_PHONE, "AU", "17:00", "12:00", LK + "Hi...", "WAITBYDURATION-3"),
        W("WAITBYDURATION-15", "1 minute", 1, "MINUTES"),
        D("MULTICRITERIADECISIONV2-4", "", [
            ("default_path_1", "GroupA Loyalty Non Member", "SMSSYNC-3", FD(C(EV + ".Loyalty_Member", "Is", "false"), C(CM + ".StoreKey", "ExistsInWholeWord", "3001, 3002, 3003, 3004", eph=False))),
            ("bd7685a5", "GroupB Loyalty Non Member", "SMSSYNC-5", FD(C(CM + ".Loyalty_Member", "Is", "false", eph=False),
                                                              C(CM + ".StoreKey", "ExistsInWholeWord", "3101, 3102, 3103, 3104, 3105, 3106, 3107, 3108, 3109, 3110, 3111, 3050, 3112, 3113, 3114, 3115", eph=False))),
            ("remainder_path", "Remainder", "WAITBYDURATION-6", None)]),
        E("EMAILV2-3", "Loyalty_Plan_Winback", 40003, "%%=ProperCase(@FirstName)=%%'s Exclusive Offer", "WAITBYDURATION-5"),
        W("WAITBYDURATION-4", "1 minute", 1, "MINUTES"),
        W("WAITBYDURATION-1", "7 days", 7, "DAYS", "MULTICRITERIADECISIONV2-3"),
    ]}

store = {
    "id": "3d8a5f12-6e94-4b71-9a2c-1f7d0c8e4b56", "key": "6c91d4a7", "name": "Store Welcome Journey",
    "version": 7, "status": "Published", "entryMode": "SingleEntryAcrossAllVersions",
    "defaults": {"email": ['{{Event.AutomationAud-7b3c9e02-4a1f-4d6e-8b90-2c5f1a3d6e77."Email"}}'], "mobileNumber": ["x"]},
    "activity": {"lastContactProcessed": "2026-09-21T22:03:03"},
    "triggers": [{"type": "AutomationAudience", "metaData": {"eventDefinitionKey": "AutomationAud-7b3c9e02-4a1f-4d6e-8b90-2c5f1a3d6e77"}}],
    "exits": [], "goals": [],
    "activities": [
        E("EMAILV2-2", "Store_Welcome_eDM4_20241122", 40004, "%%=ProperCase(@ClientName)=%%! Welcome to our store", "WAITBYDURATION-20"),
        W("WAITBYDURATION-23", "1 minute", 1, "MINUTES"),
        S("SMSSYNC-2", "Store_Welcome_NZ", 50005, "30000", "NZ", "18:00", "08:00", LK + "Kia Ora...", "WAITBYDURATION-22"),
        S("SMSSYNC-1", "Store_Welcome_AU", 50006, SYNTH_PHONE, "AU", "18:00", "11:00", LK + "Hey...", "WAITBYDURATION-21"),
        W("WAITBYDURATION-20", "1 minute", 1, "MINUTES", "MULTICRITERIADECISIONV2-6"),
        D("MULTICRITERIADECISIONV2-6", "Has phone?", [("default_path_1", "Yes", "MULTICRITERIADECISIONV2-8", FD(C(EA + ".Phone", "IsNotNull", ""))),
                                                       ("remainder_path", "No", "WAITBYDURATION-24", None)]),
        D("MULTICRITERIADECISIONV2-8", "Country", [
            ("default_path_1", "Australia", "SMSSYNC-1", FD(C(EA + ".Country", "Equal", "Australia"), C(EA + ".ItemID", "Equal", "Store_Customer_Master.ItemID", ref=True),
                                                           C("Store_Customer_Master.ItemInactive", "Is", "false", eph=False))),
            ("1e999ccb", "New Zealand", "SMSSYNC-2", FD(C(EA + ".Country", "Equal", "New Zealand"), C(EA + ".ItemID", "Equal", "Store_Customer_Master.ItemID", ref=True),
                                                       C("Store_Customer_Master.ItemInactive", "Is", "false", eph=False))),
            ("remainder_path", "Remainder", "WAITBYDURATION-23", None)]),
        W("WAITBYDURATION-24", "1 minute", 1, "MINUTES"),
        W("WAITBYDURATION-21", "1 minute", 1, "MINUTES"),
        W("WAITBYDURATION-22", "1 minute", 1, "MINUTES"),
    ]}

json.dump(plan, open(os.path.join(HERE, "journeys", "loyalty-plan-renewal-winback.json"), "w"), indent=1)
json.dump(store, open(os.path.join(HERE, "journeys", "store-welcome.json"), "w"), indent=1)

L = [
    ("6d2a1ac1", "Loyalty User Creation", "5a39", "OnceAndDone", '{{Event.SalesforceObj9a1c."User: Contact:Email"}}', "2026-09-22T16:24:22", []),
    ("c0021241", "Credit Created", "ff83", "MultipleEntries", '{{Event.SalesforceObjb2f4."Credit__c:Customer__r:Email"}}', "2026-08-23T20:05:05", []),
    ("43e01120", "Unsuspended Journey", "2cbb", "SingleEntryAcrossAllVersions", '{{Contact.SendableAttribute.Email."Contact_Salesforce.Email"}}', "2026-09-22T13:35:48", []),
    ("8e60c04a", "COMPLIANCE Store Notification of Subscription Catch Up", "90bd", "MultipleEntries", '{{Event.DEAudience-6a2d."Email__c"}}', "2024-08-22T22:55:54", []),
    ("87d0b1b5", "COMPLIANCE Store Notification of Subscription Renewal", "1fa9", "MultipleEntries", '{{Event.AutomationAud-3f71."Email__c"}}', "2026-06-08T17:01:33", []),
    ("a8b01ae0", "NewMember_July_Sprint1_2024", "1041", "OnceAndDone", '{{Event.AutomationAud-c4e2."Email"}}', "2025-04-16T17:03:22", []),
    ("2c8201f1", "Growth_July_Sprint1_2024", "5d72", "OnceAndDone", '{{Event.AutomationAud-8b1a."Email"}}', "2025-04-02T17:02:01", []),
    ("4afc7d70", "Growth_July_Sprint1_2024_V2", "d4af", "MultipleEntries", '{{Event.DEAudience-e502."Email"}}', "2026-09-21T18:00:40", ["Id equal ItemID AND Customer__c is not equal ContactID"]),
    ("006a91a0", "Active_July_Sprint1_2024_V2", "ce7f", "MultipleEntries", '{{Event.DEAudience-9f36."Email"}}', "2026-09-21T22:46:38", ["Id equal ItemID AND Customer__c is not equal ContactID"]),
    ("621e8a70", "Lapsed_March_Sprint3_2025", "e586", "MultipleEntries", '{{Event.DEAudience-1a77."Email"}}', "2026-09-22T01:06:20", ["Id equal ItemID AND Customer__c is not equal ContactID"]),
    ("ae1596e0", "Test_P_MC_Unsubscribed", "fcbc", "MultipleEntries", "", "2025-04-24T00:50:14", []),
    ("c1c6ba00", "Promotion Launched Emails Sent to Advocate (NEWCUST10): All Advocates", "PL_NEWCUST10_Aall", "MultipleEntries", '{{Event.PL_NEWCUST10_Aall."Email"}}', "2025-06-22T23:17:50", []),
    ("fc741170", "Friend Completes First Purchase Emails Sent to Advocate (NEWCUST10)", "FP_NEWCUST10_A", "MultipleEntries", '{{Event.FP_NEWCUST10_A."Referral:Referrer:Contact:Email"}}', None, []),
    ("3d8a5f12-6e94-4b71-9a2c-1f7d0c8e4b56", "Store Welcome Journey", "6c91", "SingleEntryAcrossAllVersions", '{{Event.AutomationAud-7b3c."Email"}}', "2026-09-21T22:03:03", []),
    ("9f2e6b41-7ab0-45f0-8c2d-3ea1a2b3c4d5", "Loyalty-Plan Renewal and Winback", "42a1", "SingleEntryAcrossAllVersions", '{{Event.DEAudience-2f6e."Email"}}', "2026-05-13T20:03:12", []),
    ("1d6604d0", "Loyalty Plan - Renewal Confirmation Journey", "b33b", "SingleEntryAcrossAllVersions", '{{Event.DEAudience-7c19."Email"}}', "2026-09-22T16:01:40", []),
]
items = []
for i, n, k, m, e, last, ex in L:
    it = {"id": i, "key": k, "name": n, "version": 1, "status": "Published", "entryMode": m,
          "defaults": {"email": [e] if e else []},
          "exits": [{"metaData": {"criteriaDescription": x}} for x in ex], "goals": []}
    if last:
        it["activity"] = {"lastContactProcessed": last}
    items.append(it)
json.dump({"count": len(items), "items": items}, open(os.path.join(HERE, "interactions_list.json"), "w"), indent=1)
print("fixtures written")
