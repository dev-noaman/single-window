# Get a list of fees

Source: https://developer.officernd.com/reference/feescontroller_getitems

orgSlug

string

required

organization slug

company

string

Filter by company id.

member

string

Filter by member id.

location

string

Filter by location id.

plan

string

Filter by plan id.

issueDate

string

Filter by issue date of the fee.

modifiedAt

string

Filter by last modified date of the fee.

$select

string

Select fields to return

$cursorNext

string

$cursorPrev

string

$limit

number

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

properties

object

An object that contains all custom properties that can be applied to the item.

Has additional fields

\_id

string

The \_id of the fee.

name

string

The name of the fee.

price

number

The unit price of the item described by the fee.

quantity

number

The quantity described by the one-off charge.

company

string

The \_id of the company that the fee is associated with.

member

string

The \_id of the member that the fee is associated with.

location

string

A reference to the location the fee is issued for.

plan

string

A reference to the price plan assigned to the fee.
It is used to determine the sales account when generating an invoice.

planType

string

enum

The type of the plan assigned to the fee.

`Plan``ResourceRate`

issueDate

string

The date the fee was issued.

status

string

enum

The status of the fee.

`approved``awaiting_approval`

discount

string

A reference to a discount definition.

discountAmount

number

Manually granted discount for the specific fee.

calculatedDiscountAmount

number

The actual discount amount coming from a discount defintion or from a manually granted discount.

discountedPrice

number

The final fee unit price after granting the discount.

isRefundable

boolean

If true, the one-off charge is counted as deposit and can be refunded later on.

isPersonal

boolean

If true, the one-off charge is billed to the assigned member and not to the company.

shouldBillInAdvance

boolean

If true, the one-off charge is billed in advance (respecting its date).
By default one-off charges are not billed in advance.

shouldUseCoins

boolean

In order for a fee to use coins you need to set this to true.
By default it's set to false.

payment

object

The invoice associated with the fee.

payment object

source

string

The source of the fee.

createdAt

date-time

The date when the fee has been created.

createdBy

string

The user that created the fee.

modifiedAt

date-time

The user that did the last modification to the fee. If no update is made this field will match the "createdBy" field.

modifiedBy

string

The user that last updated the fee.

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

     --url https://app.officernd.com/api/v2/organizations/orgSlug/fees \

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
      "properties": {\
\
        "customProperty1": "value1",\
\
        "customProperty2": "value2"\
\
      },\
\
      "_id": "603dfbc260f4054084125d30",\
\
      "name": "Example Fee Name",\
\
      "price": 20,\
\
      "quantity": 2,\
\
      "company": "603dfbc260f4054084125d30",\
\
      "member": "603dfbc260f4054084125d30",\
\
      "location": "603dfbc260f4054084125d30",\
\
      "plan": "603dfbc260f4054084125d30",\
\
      "planType": "Plan",\
\
      "issueDate": "2025-03-03T00:00:00.000Z",\
\
      "status": "approved",\
\
      "discount": "603dfbc260f4054084125d33",\
\
      "discountAmount": 5,\
\
      "calculatedDiscountAmount": 5,\
\
      "discountedPrice": 5,\
\
      "isRefundable": true,\
\
      "isPersonal": true,\
\
      "shouldBillInAdvance": true,\
\
      "shouldUseCoins": true,\
\
      "payment": {\
\
        "_id": "603dfbc260f4054084125d30",\
\
        "status": "paid",\
\
        "creditNote": "603dfbc260f4054084125d30"\
\
      },\
\
      "source": "admin",\
\
      "createdAt": "2024-04-12T00:00:00.000Z",\
\
      "createdBy": "6080186f490fcf6e0537ec27",\
\
      "modifiedAt": "2024-05-12T00:00:00.000Z",\
\
      "modifiedBy": "6080186f490fcf6e0537ec54"\
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