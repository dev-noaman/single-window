# Retrieve all opportunity statuses

Source: https://developer.officernd.com/reference/opportunitystatusescontroller_getitems

orgSlug

string

required

organization slug

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

The \_id of the opportunity status.

description

string

The description of the opportunity status.

probability

number

The probability of the opportunity status.

isSystem

string

Shows if the opportunity status is created by the system

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

     --url https://app.officernd.com/api/v2/organizations/orgSlug/opportunity-statuses \

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
      "_id": "6985f1644cc913fc5ac7bf74",\
\
      "description": "Open",\
\
      "probability": 50,\
\
      "isSystem": true\
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