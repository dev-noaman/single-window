# Retrieve single resource.

Source: https://developer.officernd.com/reference/resourcescontroller_getitem

resourceId

string

required

resource id

orgSlug

string

required

organization slug

# `` 200

object

properties

object

An object that contains all custom properties that can be applied to the item.

Has additional fields

\_id

string

The unique identifier of the resource.

name

string

The name of the resource.

description

string

A detailed description of the resource.

type

string

The type of the resource. Resource types can be extended and customized, but the default system types are: "meeting\_room" (bookable meeting rooms), "team\_room" (assignable private offices), "desk" (assignable dedicated desks), "desk\_tr" (assignable office desks within private offices), "hotdesk" (bookable hot desks), and "desk\_na" (not available desks).

rate

string

The resource rate used for pricing bookings for this resource. Contains pricing rules, amenities, and booking configuration.

location

string

The location the resource is assigned to.

floor

string

The floorplan where the resource is located within the location.

price

number

The monthly price for assigning this resource. Only applicable to assignable resources (resource types with "Can assign" enabled), such as dedicated desks, office desks, and private offices. Used for monthly billing.

deposit

number

The deposit amount required when assigning this resource. Only applicable to assignable resources.

size

number

The capacity of the resource, representing the number of people that can use or occupy the resource simultaneously.

area

number

The physical area of the resource measured in square millimeters.

childrenCount

number

The count of available child resources associated with this parent resource. For example, the number of office desks (desk\_tr) within a private office (team\_room). This value is dynamically calculated and updated to reflect available children only.

desksCount

number

The total number of desks within this resource. Typically used for tracking desk inventory in private offices or other parent resources.

parents

array of strings

An array of parent resource IDs for hierarchical resources. Used for resources that can have multiple parents, such as meeting rooms that belong to multiple zones. Newer resources use this property instead of the single "parent" field.

parents

availability

object

Defines the time period during which the resource is available for booking or assignment. Contains "startDate" (when availability begins) and "endDate" (when availability ends, or null for indefinite availability). Multiple availability periods can be configured.

Has additional fields

images

array of strings

An array of image URLs associated with this resource, used for displaying resource photos in listings and detail views.

images

amenities

array of strings

An array of amenity IDs associated with this resource. Amenities can be defined directly on the resource or inherited from its resource rate (e.g., WiFi, projector, whiteboard, coffee machine).

amenities

privacy

string

enum

The privacy level of the resource, which determines who can view or book it. Available only for bookable resources. Possible values: "limited" (restricted to specific members, teams, or plans; if empty, only admins have access), "full" (public access for members, non-members, guests, and visible on the public calendar), and "active\_members" (restricted to active members only).

`full``active_members``limited`

createdAt

date-time

The timestamp when the resource was created.

createdBy

string

The ID of the user who created the resource.

modifiedAt

date-time

The timestamp when the resource was last updated.

modifiedBy

string

The ID of the user who last updated the resource.

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

     --url https://app.officernd.com/api/v2/organizations/orgSlug/resources/resourceId \

     --header 'accept: application/json'
```

```

xxxxxxxxxx



{

  "properties": {

    "customProperty1": "value1",

    "customProperty2": "value2"

  },

  "_id": "603dfbc260f4054084125d39",

  "name": "Resource 1",

  "description": "Resource Description",

  "type": "team_room",

  "rate": "603dfbc260f4054084125d39",

  "location": "603dfbc260f4054084125d39",

  "floor": "603dfbc260f4054084125d39",

  "price": 50,

  "deposit": 30,

  "size": 7,

  "area": 39483789.47303743,

  "childrenCount": 7,

  "desksCount": 2,

  "parents": [],

  "availability": {

    "startDate": "2018-01-01T00:00:00.000Z",

    "endDate": null

  },

  "images": [],

  "amenities": [],

  "privacy": "limited",

  "createdAt": "2022-02-07T10:03:33.169Z",

  "createdBy": "603dfbc260f4054084125d39",

  "modifiedAt": "2022-02-08T10:03:33.169Z",

  "modifiedBy": "603dfbc260f4054084125d39"

}
```

Updated 5 months ago

* * *

Did this page help you?

Yes

No