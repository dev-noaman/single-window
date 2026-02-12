# Create a new set of credits.

Source: https://developer.officernd.com/reference/creditscontroller_additem

orgSlug

string

required

organization slug

Credits data to add.

count

number

required

The number of credits granted.

validFor

string

enum

The valid for of the credits.

allratesresourceTypesall

Allowed:

`rates``resourceTypes``all`

resourceTypes

array of strings

The resource types for which the credits are applied.

resourceTypes
ADD string

company

string

The \_id of the company with which the credits are associated.

member

string

The \_id of the member with which the credits are associated.

resourceRates

array of strings

An array that contains the \_ids of the resource rates for which the credits will be valid.
If left empty the credits will be valid for all rates.

resourceRates
ADD string

intervalLength

string

enum

Determines the recurrence of the credits.
Can be either "month" or "once". If unspecified the credits issued will be set as "once".

monthmonthonce

Allowed:

`month``once`

startDate

string

The start date of the monthly recurring credits. Should be used only for credits with "intervalLength" set to "month".

endDate

string

The end date of the monthly recurring credits. Should be used only for credits with "intervalLength" set to "month".

# `` 201

object

\_id

string

The \_id of the set of credits.

company

string

The \_id of the company with which the set of credits are associated.

member

string

The \_id of the member with which the set of credits are associated.

fee

string

The \_id of the one-off fee with which the set of credits are associated.

membership

string

The \_id of the membership with which the set of credits are associated.

intervalLength

string

enum

Determines the recurrence of the credits.
Can be either "month" or "once". If unspecified the set of credits issued will be set as "once".

`month``once`

startDate

string

The start date of the monthly recurring credits. Should be used only for the set of credits with "intervalLength" set to "month".

endDate

string

The end date of the monthly recurring credits.

validFrom

string

The start date from which the credits are valid.

validTo

string

The end date for which the credits are valid. Can be set for both monthly recurring are once credits.

validFor

string

enum

The type of the credits and what they're valid for.

`rates``resourceTypes``all`

resourceTypes

array of arrays

The resource types for which the credits is applied.

resourceTypes

array

bookings

array of arrays

An array of bookings for which the credits are used.

bookings

array

parent

string

The parent set of credits of the current set of credits.

resourceRates

array of arrays

An array that contains the \_ids of the resource rates for which the credits will be valid.
If left empty the credits will be valid for all rates.

resourceRates

array

count

number

The number of credits granted.

usedCount

number

The number of credits used.

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

     --url https://app.officernd.com/api/v2/organizations/orgSlug/credits \

     --header 'accept: application/json' \

     --header 'content-type: application/json'
```

```

xxxxxxxxxx



{

  "_id": "603dfbc260f4054084125d30",

  "company": "603dfbc260f4054084125d30",

  "member": "603dfbc260f4054084125d33",

  "fee": "603dfbc260f4054084125d33",

  "membership": "603dfbc260f4054084125d33",

  "intervalLength": "month",

  "startDate": "2024-01-01T00:00:00Z",

  "endDate": "2024-01-01T00:00:00Z",

  "validFrom": "2024-01-01T00:00:00Z",

  "validTo": "2024-01-01T00:00:00Z",

  "validFor": "all",

  "resourceTypes": [\
\
    "603dfbc260f4054084125d30"\
\
  ],

  "bookings": [\
\
    {\
\
      "count": 2,\
\
      "booking": "603dfbc260f4054084125d30",\
\
      "occurrenceDate": "2024-01-01T00:00:00Z"\
\
    }\
\
  ],

  "parent": "603dfbc260f4054084125d30",

  "resourceRates": [\
\
    "603dfbc260f4054084125d30"\
\
  ],

  "count": 2,

  "usedCount": 1

}
```

Updated 5 months ago

* * *

Did this page help you?

Yes

No