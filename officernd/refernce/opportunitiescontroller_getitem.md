# Get opportunity

Source: https://developer.officernd.com/reference/opportunitiescontroller_getitem

opportunityId

string

required

opportunity id

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

The \_id of the opportunity.

name

string

The full name of the opportunity.

company

string

The \_id of the contact company associated with the opportunity. Either a member or a company is necessary to create an opportunity.

member

string

The \_id of the contact member associated with the opportunity. Either a member or a company is necessary to create an opportunity.

status

string

The \_id of the status associated with the opportunity.

probability

number

The probability of the deal, it should match the percentage associated with the status of the opportunity.

startDate

date-time

The start date of the opportunity.

dealSize

number

The size of the deal in currency.

membersCount

number

The number of members that come with the opportunity.

resources

string

Array containing all the \_ids of resources associated with the opportunity.

requestedPlans

string

Array containing all the \_ids of plans that were requested for the opportunity.

createdAt

string

The date when the opportunity has been created.

createdBy

string

The id of the user that created the opportunity.

modifiedAt

string

The date of the last update of the opportunity.

modifiedBy

string

The id of user that did the last updated the opportunity.

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

     --url https://app.officernd.com/api/v2/organizations/orgSlug/opportunities/opportunityId \

     --header 'accept: application/json'
```

```

xxxxxxxxxx



{

  "properties": {

    "customProperty1": "value1",

    "customProperty2": "value2"

  },

  "_id": "6985f1644cc913fc5ac7bf62",

  "name": "John Doe",

  "company": "6985f1644cc913fc5ac7bf63",

  "member": "6985f1644cc913fc5ac7bf64",

  "status": "6985f1644cc913fc5ac7bf65",

  "probability": 10,

  "startDate": "2024-02-08T10:00:00.000Z",

  "dealSize": 500,

  "membersCount": 5,

  "resources": [\
\
    "6985f1644cc913fc5ac7bf66",\
\
    "6985f1644cc913fc5ac7bf67"\
\
  ],

  "requestedPlans": [\
\
    "6985f1644cc913fc5ac7bf68",\
\
    "6985f1644cc913fc5ac7bf69"\
\
  ],

  "createdAt": "2022-02-07T10:03:33.169Z",

  "createdBy": "6985f1644cc913fc5ac7bf6a",

  "modifiedAt": "2022-02-08T10:03:33.169Z",

  "modifiedBy": "6985f1644cc913fc5ac7bf6b"

}
```

Updated 5 months ago

* * *

Did this page help you?

Yes

No