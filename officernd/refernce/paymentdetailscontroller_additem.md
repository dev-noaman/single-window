# Add new payment details for user

Source: https://developer.officernd.com/reference/paymentdetailscontroller_additem

orgSlug

string

required

organization slug

type

string

enum

required

The integration type of the payment detail.

stripe

Allowed:

`stripe`

method

string

enum

required

The method of the payment details.

card

Allowed:

`card`

data

string

required

The token of the card that will be recorded. This can be procured by using Stripe's /tokens API.

isPersonal

boolean

required

Determines whether the card is recorded for the member themselves or for their company.

truefalse

member

string

The member for which the card is recorded.

company

string

The company for which the card is recorded.

# `` 201

object

\_id

string

The \_id of the payment details.

details

object

An object containing the details data

Has additional fields

type

string

enum

The type of the payment provider.

`stripe`

method

string

enum

The method of the payment details.

`card`

paymentCustomer

string

The \_id of the card in Stripe. Same as the \_id in the "card" object.

paymentSource

string

The \_id of the card in Stripe. Same as the \_id in the "card" object.

locations

string

An array containing the list of locations for which the payment details are valid.

createdAt

date-time

The time when the payment details were created

createdBy

string

The \_id user that created the payment details

Updated 5 months ago

* * *

Did this page help you?

Yes

No

ShellNodeRubyPHPPython

Bearer

```

xxxxxxxxxx

curl --request POST \

     --url https://app.officernd.com/api/v2/organizations/orgSlug/payment-details \

     --header 'accept: application/json' \

     --header 'content-type: application/json' \

     --data '

{

  "type": "stripe",

  "method": "card",

  "isPersonal": true

}

'
```

```

xxxxxxxxxx



{

  "_id": "6985f1604cc913fc5ac7bf58",

  "details": {

    "id": "card_12EXMPLE34",

    "name": "Example Name",

    "brand": "Visa",

    "funding": "credit",

    "expirationMonth": 11,

    "expirationYear": 2026,

    "country": "US",

    "cvcCheck": "pass",

    "last4": "4242",

    "authorization": {

      "authProvider": "seti_12EXMPLE34",

      "status": "not_required"

    }

  },

  "type": "stripe",

  "method": "card",

  "paymentCustomer": "cus_12EXMPLE34",

  "paymentSource": "card_12EXMPLE34",

  "locations": [\
\
    "6985f1604cc913fc5ac7bf59"\
\
  ],

  "createdAt": "2021-04-21T18:00:00.000Z",

  "createdBy": "6985f1604cc913fc5ac7bf5a"

}
```

Updated 5 months ago

* * *

Did this page help you?

Yes

No