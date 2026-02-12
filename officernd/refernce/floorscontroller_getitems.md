# Retrieve all floors

Source: https://developer.officernd.com/reference/floorscontroller_getitems

orgSlug

string

required

organization slug

\_id

string

The exact \_id of the item you are looking for.

name

string

The exact name of the item you are looking for.

location

string

Filter by location id.

createdAt

string

Support date comparison filters: $gt, $gte, $lt, $lte

modifiedAt

string

Support date comparison filters: $gt, $gte, $lt, $lte

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

The \_id of the floor.

floor

string

The number of the floor.

name

string

The name of the floor.

location

string

The \_id of the location to which the floor is associated.

area

number

The area of the floor in square milimeters (10^6 m^2).

isOpen

boolean

Shows if the floor is currently open.

createdAt

date-time

The time when the floor was created.

modifiedAt

date-time

The time when the floor was last modified.

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

     --url https://app.officernd.com/api/v2/organizations/orgSlug/floors \

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
      "_id": "",\
\
      "floor": "1",\
\
      "name": "Fl-01",\
\
      "location": "",\
\
      "area": 1500000,\
\
      "isOpen": true,\
\
      "createdAt": "2024-08-21T16:00:00.000Z",\
\
      "modifiedAt": "2024-08-21T16:00:00.000Z"\
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