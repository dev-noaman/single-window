# Retrieve business hours.

Source: https://developer.officernd.com/reference/businesshourscontroller_getitems

orgSlug

string

required

organization slug

location

string

Filter by location id.

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

workDays

array of numbers

An array of work days represented as numbers (0-6, where 0 is Sunday).

workDays

openingTime

number

The opening hour of the business hours. Decimals represent specific times (e.g., 9.5 is 9:30, 9.75 is 9:45).

closingTime

number

The closing hour of the business hours. Decimals represent specific times (e.g., 17.5 is 17:30, 17.75 is 17:45).

closedDays

array of strings

The closed days of the business hours.

closedDays

location

string

Reference to the location the business hours are associated with.

Updated 3 months ago

* * *

Did this page help you?

Yes

No

ShellNodeRubyPHPPython

Bearer

```

xxxxxxxxxx

curl --request GET \

     --url https://app.officernd.com/api/v2/organizations/orgSlug/settings/business-hours \

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
      "workDays": [\
\
        1,\
\
        2,\
\
        3,\
\
        4,\
\
        5\
\
      ],\
\
      "openingTime": 9.5,\
\
      "closingTime": 17,\
\
      "closedDays": [\
\
        {\
\
          "from": "2025-01-01T00:00:00.000Z",\
\
          "to": "2025-01-01T00:00:00.000Z",\
\
          "description": "Holidays",\
\
          "occurrence": "once"\
\
        }\
\
      ],\
\
      "location": "507f1f77bcf86cd799439011"\
\
    }\
\
  ]

}
```

Updated 3 months ago

* * *

Did this page help you?

Yes

No