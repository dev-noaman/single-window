# Retrieve all assignments for a specific resource

Source: https://developer.officernd.com/reference/assignmentscontroller_getitems

orgSlug

string

required

organization slug

resource

string

Filter by resource id.

membership

string

Filter by membership id.

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

\_id

string

The \_id of the assignment.

resource

string

The \_id of the resource with which the assignment is associated.

membership

string

The \_id of the membership with which the assignment is associated.

startDate

date-time

The start date of the assignment.

endDate

date-time

The end date of the assignment.

Updated 3 days ago

* * *

Did this page help you?

Yes

No

ShellNodeRubyPHPPython

Bearer

```

xxxxxxxxxx

curl --request GET \

     --url https://app.officernd.com/api/v2/organizations/orgSlug/assignments \

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
      "_id": "61f273a906afd1846de1fbb3",\
\
      "resource": "61f2736224071037dea8956c",\
\
      "membership": "6262b4de9d02c386771e3923",\
\
      "startDate": "2024-08-21T16:00:00.000Z",\
\
      "endDate": "2024-08-21T16:00:00.000Z"\
\
    }\
\
  ]

}
```

Updated 3 days ago

* * *

Did this page help you?

Yes

No