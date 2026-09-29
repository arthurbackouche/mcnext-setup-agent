# Customer 360 target cheat-sheet for MCE data

Standard DMO fields verified against a live Data 360 tenant. Standard fields carry the `ssot__` prefix.
Client-specific custom attributes appear without it. Always re-check against the client's `d360_metadata`
output before writing a mapping, because clients extend standard DMOs and the field list differs per tenant.

## Party and contact points

| Concept | DMO | Key fields |
|---|---|---|
| Person | `ssot__Individual__dlm` | `ssot__Id__c` (PK), `ssot__FirstName__c`, `ssot__LastName__c`, `ssot__Salutation__c`, `ssot__BirthDate__c`, `ssot__PartyId__c` |
| Email | `ssot__ContactPointEmail__dlm` | `ssot__Id__c`, `ssot__EmailAddress__c`, `ssot__PartyId__c`, `ssot__EmailLatestBounceDateTime__c`, `ssot__EmailLatestBounceReasonText__c` |
| Phone | `ssot__ContactPointPhone__dlm` | `ssot__Id__c`, `ssot__TelephoneNumber__c`, `ssot__FormattedE164PhoneNumber__c`, `ssot__PartyId__c` |
| Address | `ssot__ContactPointAddress__dlm` | `ssot__AddressLine1__c`, `ssot__CityName__c`, `ssot__StateProvinceName__c`, `ssot__PostalCodeText__c`, `ssot__CountryName__c`, `ssot__PartyId__c` |
| Business / location | `ssot__Account__dlm` | `ssot__Id__c`, `ssot__Name__c`, `ssot__AccountType__c`, `ssot__ParentAccountId__c` |
| Lead | `ssot__Lead__dlm` | `ssot__Id__c`, `ssot__PersonName__c`, `ssot__LeadSourceId__c`, `ssot__LeadStatusId__c`, `ssot__ContactPointEmailId__c`, `ssot__PartyId__c` |
| External ids | `ssot__PartyIdentification__dlm` | `ssot__IdentificationName__c`, `ssot__IdentificationNumber__c`, `ssot__PartyId__c`. Use for SubscriberKey when it is not the CRM id. |

## Consent

| Concept | DMO | Notes |
|---|---|---|
| Subscription-level consent | `ssot__CommunicationSubscriptionConsent__dlm` | `ssot__ConsentStatus__c` (OptIn / OptOut), `ssot__CommunicationSubscriptionChannelTypeId__c`, `ssot__ConsentCapturedDateTime__c`, `ssot__ContactPointValueText__c`, `ssot__PartyId__c` |
| Channel-level consent | `ssot__ContactPointConsent__dlm` | Often absent in a tenant until first mapped. Add from the standard model. |
| Party-level consent | `ssot__PartyConsent__dlm` | Same. |
| Publication list / channel type | `ssot__CommunicationSubscriptionChannelType__dlm`, `ssot__CommunicationSubscription__dlm` | One row per SFMC publication list. |

## Engagement (already handled by the MCE starter bundle)

`MessagingEventsEmailV2_*` and `MessagingEventsSmsV2_*` DLOs feed `ssot__EmailEngagement__dlm` and
`ssot__MessageEngagement__dlm`. `WebEngagementEventsV2_*` feeds `ssot__WebsiteEngagement__dlm`.
Do not add data-extension streams for tracking data; it duplicates the bundle.

## Personalization (Interaction Studio) catalog DEs

| SFMC DE | DMO |
|---|---|
| IGO_PROFILES | `ssot__Individual__dlm` via `ssot__PartyIdentification__dlm` |
| IGO_PRODUCTS | `ssot__GoodsProduct__dlm` |
| IGO_PRODUCTATTRIBS | `ssot__ProductAttribute__dlm` |
| IGO_PURCHASES | `ssot__SalesOrder__dlm` + `ssot__SalesOrderProduct__dlm` |
| IGO_VIEWS | `ssot__ProductBrowseEngagement__dlm` |
| PI_CONTENT / PI_CONTENTATTRIBS | `ssot__DigitalContent__dlm` |
| PI_CONTENTVIEWS / PI_SESSIONS / PI_SESSION_ENDS | `ssot__WebsiteEngagement__dlm` |
| PI_ABANDONED_CART_EVENT / _ITEMS | `ssot__ShoppingCartEngagement__dlm` / `ssot__ShoppingCartEngagementProduct__dlm` |

## Custom DMO conventions

Category drives behaviour: Profile (one row per party, joins to Unified Individual), Engagement (needs an
event time field, time-series), Other (reference data). Name `<Concept>__dlm`, fields `<snake_case>__c`,
PK first, event time field second. Keep a `source_de__c` column on consolidated DMOs so lineage survives.

## SFMC to Data 360 type map

| SFMC | Data 360 |
|---|---|
| Text | TEXT |
| EmailAddress | TEXT with business type EMAIL |
| Phone | TEXT with business type PHONE |
| Number / Decimal | NUMBER |
| Date | DATE_TIME |
| Boolean | BOOLEAN |
| Locale | TEXT |

Anything typed Text in SFMC that is really a date, email, phone or flag should be retyped in SFMC first.
Casting inside 100+ field mappings is slower to build and impossible to audit.
