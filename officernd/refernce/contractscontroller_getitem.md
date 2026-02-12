# Get contract

Source: https://developer.officernd.com/reference/contractscontroller_getitem

contractId

string

required

contract id

orgSlug

string

required

organization slug

# `` 200

object

notice

object

The number of months notice period for the contract.

months

number

The number of months notice period for the contract.

properties

object

An object that contains all custom properties that can be applied to the item.

Has additional fields

\_id

string

The \_id of the contract.

number

string

The number/name of the contract.

company

string

The \_id of the company associated with the contract.

member

string

The \_id of the member associated with the contract

location

string

The \_id of the location associated with the contract.

documentType

string

The type of the contract. Check "Settings"->"Platform"->"Contracts" to see what types are available.

startDate

string

The start date of the contract

endDate

string

The end date of the contract

plans

array of objects

An array containing all recurring plans that will be associated with the contract.

plans

object

id

string

The \_id of the plan used to create the membership.

steps

array of objects

The steps for the recurring plans in the contract. Each step will result in a separate membership once the contract is signed.

steps

object

price

number

The price of the step.

discount

string

The \_id of the discount associated to the step.

discountedAmount

number

The amount of the discount of the step.

startDate

date-time

The start date of the step.

endDate

date-time

The end date of the step.

count

number

The quantity of plans that will be purchased.

price

number

The price of the plan.

deposit

number

The deposit required for the plan.

increasePriceInRolling

boolean

Shows if the price is increased for this plan when the contract is rolling.

oneOffPlans

array of objects

An array containing all one-off plans that will be associated with the contract.

oneOffPlans

object

id

string

The \_id of the one-off plan used to create the fee.

steps

array of objects

This array contains the steps of the one-offs.

steps

object

price

number

The price of the step.

discount

string

The \_id of the discount associated to the step.

discountedAmount

number

The amount of the discount of the step.

startDate

date-time

The start date of the step.

endDate

date-time

The end date of the step.

count

number

The quantity of one-off plans that will be purchased.

price

number

The price of the one-off plan.

deposit

number

The deposit required for the one-off plan. If left empty the default deposit for the one-off plan will be used.

increasePriceInRolling

boolean

Shows if the price is increased for this one-off when the contract is rolling.

resources

array of objects

An array containing all resources that will be associated with the contract.

resources

object

id

string

The \_id of the resource.

steps

array of objects

The steps for the resource in the contract. Each step will result in a separate membership once the contract is signed.

steps

object

price

number

The price of the step.

discount

string

The \_id of the discount associated to the step.

discountedAmount

number

The amount of the discount of the step.

startDate

date-time

The start date of the step.

endDate

date-time

The end date of the step.

size

number

The number of people that can inhabit the resource. If left empty the default size of the office will be used.

price

number

The price of the resource.

deposit

number

The deposit required for the resource.

increasePriceInRolling

boolean

Shows if the price is increased for this resource when the contract is rolling.

legalDocuments

array of strings

An array with the ids of the legal documents attached to the contract.

legalDocuments

addendum

string

An addendum to the contract.

isRolling

boolean

A true/false value that decides if the contract is rolling or not

stage

string

enum

The stage of the contract.

`terminated``served_notice``active``up_for_renewal``not_renewed``expired``rolling`

status

string

enum

The status of the contract.

`signed``draft``terminated``not_signed``canceled`

signatureStatus

string

enum

The status of the signature of the contract.

`e_signed``manually_signed``out_for_signature``declined``requires_attention``canceled``signed_by_member`

signDate

string

The date and time when the contract was signed.

signedBy

object

Data of the user contract who signed the contract.

\_id

string

The \_id of the user who signed the contract.

displayName

string

The display name of the user who signed the contract.

activationErrors

array of objects

An array of activation errors

activationErrors

object

View Additional Properties

termination

object

An object with information about the termination of the contract.

date

string

The date of the termination.

reasonKey

string

The reason for the termination.

comments

string

Comments about the termination.

total

number

The total price of the contract (after taxes).

baseTotal

number

The total price of the contract (before taxes).

plansTotal

number

The total price of all the plans in the contract.

oneOffsTotal

number

The total price of all the one-offs in the contract.

resourcesTotal

number

The total price of all the resources in the contract.

percentagePriceIncrease

number

Percentage price increase of the contract.

previousDepositHeld

number

The previous deposit of the contract.

type

string

enum

The type of the contract.

`renewal``expansion``new`

renewedContract

string

The \_id of the renewed contract that this renewal contract continues.

renewalContract

string

The \_id of the renewal contract that continues this renewed contract.

createdAt

date-time

The date and time when the contract was created.

createdBy

string

The user that created the contract.

modifiedAt

date-time

The date and time when the contract was last modified.

modifiedBy

string

The user that last updated the contract.

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

     --url https://app.officernd.com/api/v2/organizations/orgSlug/contracts/contractId \

     --header 'accept: application/json'
```

```

xxxxxxxxxx



{

  "notice": {

    "months": 3

  },

  "properties": {

    "customProperty1": "value1",

    "customProperty2": "value2"

  },

  "_id": "6080186f490fcf6e0547ec57",

  "number": "CON-3",

  "company": "6080186f490fcf6e0547ec59",

  "member": "6080186f490fcf6e0547ec57",

  "location": "6080186f490fcf6e0547ec58",

  "documentType": "membershipagreement",

  "startDate": "2024-08-21T00:00:00.000Z",

  "endDate": "2025-08-20T00:00:00.000Z",

  "plans": [],

  "oneOffPlans": [],

  "resources": [],

  "legalDocuments": [\
\
    "6080186f490fcf6e0547ec85",\
\
    "6080186f490fcf6e0547ec59"\
\
  ],

  "addendum": "<p> This is an example addendum to the contract. </p>",

  "isRolling": true,

  "stage": "active",

  "status": "not_signed",

  "signatureStatus": "e_signed",

  "signDate": "2024-08-21T16:00:00.000Z",

  "signedBy": {

    "_id": "6080186f490fcf6e0547ec84",

    "displayName": "John Doe"

  },

  "activationErrors": [],

  "termination": {

    "date": "2025-10-03T00:00:00.000Z",

    "comments": "Example comment to the termination.",

    "reasonKey": "Example Reason Key"

  },

  "total": 150.5,

  "baseTotal": 145.62,

  "plansTotal": 120.81,

  "oneOffsTotal": 15.522,

  "resourcesTotal": 15.99,

  "percentagePriceIncrease": 10,

  "previousDepositHeld": 100,

  "type": "new",

  "renewedContract": "6080186f490fcf6e0547ec57",

  "renewalContract": "6080186f490fcf6e0547ec58",

  "createdAt": "2024-08-21T16:00:00.000Z",

  "createdBy": "6080186f490fcf6e0547ec50",

  "modifiedAt": "2024-08-21T16:00:00.000Z",

  "modifiedBy": "6080186f490fcf6e0547ec50"

}
```

Updated 5 months ago

* * *

Did this page help you?

Yes

No