# Get a single membership

Source: https://developer.officernd.com/reference/membershipscontroller_getitem

membershipId

string

required

membership id

orgSlug

string

required

organization slug

# `` 200

object

properties

object

An object that contains all custom properties that can be applied to the item.

Has additional fields

\_id

string

The \_id of the membership.

name

string

The name of the membership.

isPersonal

boolean

If true, the membership is billed to the assigned member and not to the company.

status

string

enum

The approval status of the membership. This is usually set to approved, but if a member purchases a membership that needs to be approved, the status will be "not\_approved".

`approved``not_approved`

calculatedStatus

string

enum

The actual membership status calculated by the platform.

`not_started``active``expired``not_approved`

type

string

enum

The type of the membership.

`month_to_month``fixed`

location

string

A reference to the location the membership is issued for.

plan

string

A reference to the price plan assigned to the membership. It is used to determine the sales account when generating an invoice.

company

string

The \_id of the company with which the membership is associated.

member

string

The \_id of the member with which the membership is associated.

startDate

string

The membership starting date.

endDate

string

The last date of membership. If not set, the membership is open-ended.

intervalLength

string

enum

The membership interval. It could be "once", "hour", "day", or "month".

`once``hour``day``month`

intervalCount

number

The length of the membership interval.

isLocked

boolean

If true, prevents editing the membership.

price

number

The monthly price of the membership.

deposit

number

The deposit of the membership.

discount

string

A reference to a discount definition.

discountAmount

number

Manually granted discount for the specific membership.

calculatedDiscountAmount

number

The actual discount amount coming from a discount defintion or from a manually granted discount.

discountedPrice

number

The final membership unit price after granting the discount.

contract

string

Reference to the contract associated with the membership

source

string

The source of the membership.

createdAt

date-time

The date when the membership has been created.

createdBy

string

The user that created the membership.

modifiedAt

date-time

The user that did the last modification to the membership. If no update is made this field will match the "createdBy" field.

modifiedBy

string

The user that last updated the membership.

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

     --url https://app.officernd.com/api/v2/organizations/orgSlug/memberships/membershipId \

     --header 'accept: application/json'
```

```

xxxxxxxxxx



{

  "properties": {

    "customProperty1": "value1",

    "customProperty2": "value2"

  },

  "_id": "603dfbc260f4054084125d30",

  "name": "Private Office",

  "isPersonal": false,

  "status": "approved",

  "calculatedStatus": "active",

  "type": "month_to_month",

  "location": "603dfbc260f4054084125d33",

  "plan": "603dfbc260f4054084125d33",

  "company": "603dfbc260f4054084125d33",

  "member": "603dfbc260f4054084125d33",

  "startDate": "2024-01-01T00:00:00Z",

  "endDate": "2024-01-01T00:00:00Z",

  "intervalLength": "month",

  "intervalCount": 6,

  "isLocked": false,

  "price": 20,

  "deposit": 5,

  "discount": "603dfbc260f4054084125d33",

  "discountAmount": 5,

  "calculatedDiscountAmount": 5,

  "discountedPrice": 5,

  "contract": "603dfbc260f4054084125d33",

  "source": "admin",

  "createdAt": "2024-04-12T00:00:00.000Z",

  "createdBy": "6080186f490fcf6e0537ec27",

  "modifiedAt": "2024-05-12T00:00:00.000Z",

  "modifiedBy": "6080186f490fcf6e0537ec54"

}
```

Updated 5 months ago

* * *

Did this page help you?

Yes

No