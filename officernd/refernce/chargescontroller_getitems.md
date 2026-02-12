# Retrieve all charges

Source: https://developer.officernd.com/reference/chargescontroller_getitems

orgSlug

string

required

organization slug

\_id

string

Filter by the \_id of the charge.
Supports both single id values (e.g., \_id=603dfbc260f4054084125d33) and array operations (e.g., \_id\[$in\]=603dfbc260f4054084125d33,603dfbc260f4054084125d34).
Note: Multiple values in simple string format (e.g., \_id=603dfbc260f4054084125d33,603dfbc260f4054084125d34) are not allowed - use \_id\[$in\] format instead.

status

string

Filter by status of the invoice, credit note, or overpayment.
Supports both single status values (e.g., status=success) and array operations (e.g., status\[$in\]=success,pending).
Note: Multiple values in simple string format (e.g., status=success,pending) are not allowed - use status\[$in\]=success,pending format instead.

payment

string

Filter by reference to the invoice, to which the charge belongs to.

source

string

Filter by the source of the charge. The source will be an accounting integration if the charge is synced from an integration.

date

string

Filter by the date of the charge. Supports date comparison filters: $gt, $gte, $lt, $lte

modifiedAt

string

Support date comparison filters: $gt, $gte, $lt, $lte

createdAt

string

Support date comparison filters: $gt, $gte, $lt, $lte

$select

string

Select fields to return

$cursorNext

string

$cursorPrev

string

$limit

number

$sort

json

Sort by modifiedAt,createdAt and direction (asc, desc)

# `` 200

object

rangeStart

number

rangeEnd

number

cursorNext

string

cursorPrev

string

results

array of objects

results

object

\_id

string

required

The \_id of the charge.

amount

number

required

The amount of the charge.

currency

string

The currency of the charge.

account

string

The account to which the charge is allocated.

reference

string

A short description of the charge

date

string

The date of the charge.

accounting

object

Data on the payment sync with an accounting integration.

accounting object

source

string

The source of the charge. The source will be an accounting integration if the charge is synced from an integration.

status

string

enum

The status of the charge.

`pending``fail``success``refund`

payment

string

Reference to the invoice, to which the charge belongs to.

providerChargeReference

string

The payment gateway reference for the charge (e.g., Stripe charge ID).

createdAt

date-time

The date when the charge has been created at.

createdBy

string

The user that created the charge.

modifiedAt

date-time

The date when the charge has been modified for the last time.

modifiedBy

string

The user that did the last modification to the charge. Before the first modification, this field equals to the createdBy field.

Updated 5 months ago

* * *

Did this page help you?

Yes

No

ShellNodeRubyPHPPython

Bearer

```

xxxxxxxxxx

curl --request GET \

     --url https://app.officernd.com/api/v2/organizations/orgSlug/charges \

     --header 'accept: application/json'
```

```

xxxxxxxxxx



{

  "rangeStart": 0,

  "rangeEnd": 0,

  "cursorNext": "string",

  "cursorPrev": "string",

  "results": [\
\
    {\
\
      "_id": "6080186f490fcf6e0547ec50",\
\
      "amount": 15,\
\
      "currency": "USD",\
\
      "account": "Cash",\
\
      "reference": "Charge Reference 1",\
\
      "date": "2025-01-01T00:00:00.000Z",\
\
      "accounting": {\
\
        "provider": "xero",\
\
        "providerId": "123456789",\
\
        "externalOrgId": "987654321",\
\
        "deepLink": "https://xero.com/123456789",\
\
        "lastSync": "2025-01-01T00:00:00.000Z",\
\
        "error": "An error occurred while syncing with Xero"\
\
      },\
\
      "source": "API",\
\
      "status": "success",\
\
      "payment": "6080186f490fcf6e0547ec50",\
\
      "providerChargeReference": "ch_3ABC123DEF456",\
\
      "createdAt": "2025-01-01T00:00:00.000Z",\
\
      "createdBy": "6080186f490fcf6e0547ec50",\
\
      "modifiedAt": "2025-01-01T00:00:00.000Z",\
\
      "modifiedBy": "6080186f490fcf6e0547ec50"\
\
    }\
\
  ]

}
```

Updated 5 months ago

* * *

Did this page help you?

Yes

No