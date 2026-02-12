# Get reception flows

Source: https://developer.officernd.com/reference/receptionflowscontroller_getitems

orgSlug

string

required

organization slug

\_id

string

Filter by reception flow id. Supports both single id values (e.g., \_id=66623dc53090242657393910) and array operations (e.g., \_id\[$in\]=66623dc53090242657393910,66623dbf309024265739390a).
Note: Multiple values in simple string format (e.g., \_id=66623dc53090242657393910,66623dbf309024265739390a) are not allowed - use \_id\[$in\] format instead.

name

string

Filter by reception flow name.

type

string

Filter by reception flow type.

location

string

Filter by reception flow location.

enabled

boolean

Filter by reception flow enabled status.

truetruefalse

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

The \_id of the reception flow.

name

string

required

The name of the reception flow.

location

string

The location of the reception flow.

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

     --url https://app.officernd.com/api/v2/organizations/orgSlug/reception-flows \

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
      "_id": "6080186f490fcf6e0547ec57",\
\
      "name": "Visitor",\
\
      "location": "6080186f490fcf6e0547ec58"\
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