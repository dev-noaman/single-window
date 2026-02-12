# Get plans

Source: https://developer.officernd.com/reference/planscontroller_getitems

orgSlug

string

required

organization slug

name

string

Filter by the exact name of the plan.

code

string

Filter by the code of the plan.

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

The \_id of the plan.

name

string

The name of the plan.

description

string

Text describing the plan. It will appear when users need to choose among different plans.

code

string

External identified for the plan. Usually used for accounting purposes.

type

string

The type of the plan. It could be office, desk, hotdesk or service or any custom type.

price

number

The default unit price for the plan, depending if it is recurring plan or a one-off plan.

deposit

number

The deposit of the plan. This is a fixed price.

depositPercent

number

The deposit of the plan. This is a percent of the price.

useDepositPercent

boolean

This shows if the deposit is fixed or is a percent of the price.

locations

array of strings

An array with the ids of the locations associated with the plan.

locations

image

string

A link to the image of the plan.

link

string

Link to the product page. It is used on the signup and checkout pages, and the booking dialog.

intervalLength

string

enum

The plan interval. It could be month or once.

`once``month`

intervalCount

number

The length of the interval.

revenueAccount

string

The \_id of the revenue account associated with the plan.

setupFees

array of strings

An array with the ids of the setup fees associated with the plan.

setupFees

discounts

array of strings

An array with the ids of the discounts applied to the plan.

discounts

legalDocuments

array of strings

An array with the ids of the legal documents that members should be prompted to accept when purchasing this plan.

legalDocuments

shouldProrate

boolean

Shows if the plan has proration

credits

array of objects

An array of the credits in the plan.

credits

object

View Additional Properties

useCoins

boolean

Shows if coins can be used in the plan.

passesForLocations

array of numbers

An array with the count of passes in the plan by location.

passesForLocations

extras

array of objects

An array with all the extras in the plan.

extras

object

View Additional Properties

requiresApproval

boolean

Shows if admins must approve purchases of this plan.

allowsCancellation

boolean

Shows if members can request cancellation of this plan.

forMembers

boolean

Shows if the plan is available for purchase by members marked as contact person.

forTeamMembers

boolean

Shows if the plan is available for purchase by all active company members.

forNonMembers

boolean

Shows if the plan is available for purchase on the Signup page and accessible to everyone on the Member Portal.

markupPercent

number

The markup percent of the plan.

shouldPassesGrantActiveStatus

boolean

Shows if passes give active status to the members without active memberships.

amenities

array of strings

An array with the ids of all the amenities in the plan.

amenities

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

     --url https://app.officernd.com/api/v2/organizations/orgSlug/plans \

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
      "_id": "6985f1604cc913fc5ac7bf43",\
\
      "name": "Plan Name",\
\
      "description": "Example Description",\
\
      "code": "EXMPL",\
\
      "type": "Desk",\
\
      "price": 100,\
\
      "deposit": 50,\
\
      "depositPercent": 20,\
\
      "useDepositPercent": true,\
\
      "locations": [\
\
        "6985f1604cc913fc5ac7bf44",\
\
        "6985f1604cc913fc5ac7bf45"\
\
      ],\
\
      "image": "exampleImageLink.com",\
\
      "link": "exampleExternalLink.com",\
\
      "intervalLength": "month",\
\
      "intervalCount": 6,\
\
      "revenueAccount": "6985f1604cc913fc5ac7bf46",\
\
      "setupFees": [\
\
        "6985f1604cc913fc5ac7bf47",\
\
        "6985f1604cc913fc5ac7bf48"\
\
      ],\
\
      "discounts": [\
\
        "6985f1604cc913fc5ac7bf49",\
\
        "6985f1604cc913fc5ac7bf4a"\
\
      ],\
\
      "legalDocuments": [\
\
        "6985f1604cc913fc5ac7bf4b",\
\
        "6985f1604cc913fc5ac7bf4c"\
\
      ],\
\
      "shouldProrate": true,\
\
      "credits": [],\
\
      "useCoins": true,\
\
      "passesForLocations": 10,\
\
      "extras": [],\
\
      "requiresApproval": true,\
\
      "allowsCancellation": true,\
\
      "forMembers": true,\
\
      "forTeamMembers": true,\
\
      "forNonMembers": true,\
\
      "markupPercent": true,\
\
      "shouldPassesGrantActiveStatus": true,\
\
      "amenities": [\
\
        "6985f1604cc913fc5ac7bf4d",\
\
        "6985f1604cc913fc5ac7bf4e"\
\
      ]\
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