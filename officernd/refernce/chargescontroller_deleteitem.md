# Delete a charge for invoice

Source: https://developer.officernd.com/reference/chargescontroller_deleteitem

chargeId

string

required

Id of the charge.

orgSlug

string

required

organization slug

# `` 200

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

provider

string

The name of the accounting provider.

providerId

string

The id of the payment in the accounting provider.

externalOrgId

string

The organization id in the accounting provider.

deepLink

string

A deep link to the payment in the accounting provider.

lastSync

string

The date of the last sync of the payment with the accounting integration.

error

string

An error message with more details about the reason of the failure.

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

curl --request DELETE \

     --url https://app.officernd.com/api/v2/organizations/orgSlug/charges/chargeId \

     --header 'accept: application/json'
```

```

xxxxxxxxxx



{

  "_id": "6080186f490fcf6e0547ec50",

  "amount": 15,

  "currency": "USD",

  "account": "Cash",

  "reference": "Charge Reference 1",

  "date": "2025-01-01T00:00:00.000Z",

  "accounting": {

    "provider": "xero",

    "providerId": "123456789",

    "externalOrgId": "987654321",

    "deepLink": "https://xero.com/123456789",

    "lastSync": "2025-01-01T00:00:00.000Z",

    "error": "An error occurred while syncing with Xero"

  },

  "source": "API",

  "status": "success",

  "payment": "6080186f490fcf6e0547ec50",

  "providerChargeReference": "ch_3ABC123DEF456",

  "createdAt": "2025-01-01T00:00:00.000Z",

  "createdBy": "6080186f490fcf6e0547ec50",

  "modifiedAt": "2025-01-01T00:00:00.000Z",

  "modifiedBy": "6080186f490fcf6e0547ec50"

}
```

Updated 5 months ago

* * *

Did this page help you?

Yes

No