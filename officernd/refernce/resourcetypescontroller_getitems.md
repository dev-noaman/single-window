# Get resource types

Source: https://developer.officernd.com/reference/resourcetypescontroller_getitems

orgSlug

string

required

organization slug

\_id

array of strings

Filter by the \_id of the resource type.

\_id
ADD string

type

array of strings

Filter by the type of the resource type(s).

type
ADD string

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

The \_id of the resource type.

title

string

The name of the resource type.

type

string

A unique key that links the resource type to a zone type.

bookingMode

string

enum

Booking mode of the resource type. One of types listed above.

`time``date`

checkinMode

string

enum

Booking mode of the resource type. One of types listed above.

`hour``half_day`

icon

string

An icon to represent the resource type on the portal.

canBook

boolean

If true, the resource type is available for booking on a calendar.

canAssign

boolean

If true, memberships is assignable to the resource type.

isPrimary

boolean

If true, the resource occupancy can be tracked in the Occupancy section of the Dashboard.

isHierarchical

boolean

If true, the resource type allows parent/child relationship (applicable to meeting\_room type only).

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

     --url https://app.officernd.com/api/v2/organizations/orgSlug/resource-types \

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
      "_id": "5e37ebbc5bc88201b7aa5145",\
\
      "title": "Private office",\
\
      "type": "team_room",\
\
      "bookingMode": "time",\
\
      "checkinMode": "day",\
\
      "icon": "fa-building",\
\
      "canBook": true,\
\
      "canAssign": true,\
\
      "isPrimary": true,\
\
      "isHierarchical": true\
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