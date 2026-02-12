# Update a set of day passes

Source: https://developer.officernd.com/reference/passescontroller_updateitem

passesId

string

required

passes id

orgSlug

string

required

organization slug

count

string

The updated number of passes granted.

# `` 200

object

\_id

string

The \_id of the set of passes.

count

number

The number of passes granted.

usedCount

number

The number of used passes.

intervalLength

number

Determines the recurrence of the passes. Can be either "month" or "once". If unspecified the credits issued will be set as "once".

startDate

date-time

The start date of the monthly recurring passes. Should be used only for credits with "intervalLength" set to "month".

endDate

date-time

The end date of the monthly recurring passes. Should be used only for credits with "intervalLength" set to "month".

renewDate

date-time

The renew date of the monthly recurring passes. Should be used only for credits with "intervalLength" set to "month".

validFrom

date-time

The start date from which the passes are valid.

validTo

date-time

The end date for which the passes are valid.

company

string

The \_id of the company with which the passes are associated.

member

string

The \_id of the member with which the passes are associated.

isPersonal

boolean

Shows if the set of passes is for a single member or if its shared for a company.

membership

string

The \_id of the membership with which the passes are associated.

fee

string

Shows if the set of fee is for a single member or if its shared for a company.

shouldGrantActiveStatus

boolean

Shows if the set of passes grants active status to members that do not have active memberships.

resourceType

string

The type of the resource associated to the set of passes.

status

string

enum

The status of the set of passes.

`used``valid``expired``pending`

createdAt

date-time

The date and time of the creation of the set of passes.

createdBy

string

The user that created the set of passes.

modifiedAt

date-time

The date and time of the last update the set of passes.

modifiedBy

string

The user that last updated the set of passes.

Updated 5 months ago

* * *

Did this page help you?

Yes

No

ShellNodeRubyPHPPython

Bearer

```

xxxxxxxxxx

curl --request PUT \

     --url https://app.officernd.com/api/v2/organizations/orgSlug/passes/passesId \

     --header 'accept: application/json' \

     --header 'content-type: application/json'
```

```

xxxxxxxxxx



{

  "_id": "6080186f490fcf6e0537ec52",

  "count": 15,

  "usedCount": 5,

  "intervalLength": "month",

  "startDate": "2024-04-12T00:00:00.000Z",

  "endDate": "2024-05-12T00:00:00.000Z",

  "renewDate": "2024-05-12T00:00:00.000Z",

  "validFrom": "2024-03-06T00:00:00.000Z",

  "validTo": "2024-04-06T00:00:00.000Z",

  "company": "6080186f490fcf6e0537ec62",

  "member": "6080186f490fcf6e0537ec67",

  "isPersonal": true,

  "membership": "6080186f490fcf6e0537ec33",

  "fee": "6080186f490fcf6e0537ec34",

  "shouldGrantActiveStatus": true,

  "resourceType": "hotdesk",

  "status": "pending",

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