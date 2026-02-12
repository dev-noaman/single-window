# Gets a specific floor

Source: https://developer.officernd.com/reference/floorscontroller_getitem

floorId

string

required

The id of the corresponding floor

orgSlug

string

required

organization slug

# `` 200

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

     --url https://app.officernd.com/api/v2/organizations/orgSlug/floors/floorId \

     --header 'accept: application/json'
```

```

xxxxxxxxxx



{

  "_id": "",

  "floor": "1",

  "name": "Fl-01",

  "location": "",

  "area": 1500000,

  "isOpen": true,

  "createdAt": "2024-08-21T16:00:00.000Z",

  "modifiedAt": "2024-08-21T16:00:00.000Z"

}
```

Updated 5 months ago

* * *

Did this page help you?

Yes

No