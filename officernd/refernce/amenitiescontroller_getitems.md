# Retrieve all amenities

Source: https://developer.officernd.com/reference/amenitiescontroller_getitems

orgSlug

string

required

organization slug

\_id

string

Filter by the \_id of the amenity.

title

string

Filter by the title of the amenity.

createdAt

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

The \_id of the amenity.

title

string

The name of the amenity.

icon

string

The icon chosen for the amenity, it's best to take a look at the UI and see what icons are available.

createdAt

date-time

The \_id of the amenity.

createdBy

string

The \_id of the amenity.

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

     --url https://app.officernd.com/api/v2/organizations/orgSlug/amenities \

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
      "title": "Amenity 1",\
\
      "icon": "fa-500px",\
\
      "createdAt": "2021-04-21T18:00:00.000Z",\
\
      "createdBy": "5bbb155174321f100085eac1"\
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