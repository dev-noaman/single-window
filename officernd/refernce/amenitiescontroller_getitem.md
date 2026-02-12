# Get an amenity

Source: https://developer.officernd.com/reference/amenitiescontroller_getitem

amenityId

string

required

The id of the corresponding amenity

orgSlug

string

required

organization slug

# `` 200

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

     --url https://app.officernd.com/api/v2/organizations/orgSlug/amenities/amenityId \

     --header 'accept: application/json'
```

```

xxxxxxxxxx



{

  "_id": "6080186f490fcf6e0547ec57",

  "title": "Amenity 1",

  "icon": "fa-500px",

  "createdAt": "2021-04-21T18:00:00.000Z",

  "createdBy": "5bbb155174321f100085eac1"

}
```

Updated 5 months ago

* * *

Did this page help you?

Yes

No