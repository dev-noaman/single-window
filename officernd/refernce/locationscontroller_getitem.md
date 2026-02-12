# Retrieve single location.

Source: https://developer.officernd.com/reference/locationscontroller_getitem

locationId

string

required

location id

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

The \_id of the location.

name

string

The name of the location.

address

object

The address details of the location.

formattedAddress

string

The address of the physical address.

country

string

The country of the physical address.

state

string

The state of the physical address.

city

string

The city of the physical address.

street

string

The name of the street of the physical address.

zip

string

The zip of the physical address.

latitude

string

The latitude of the physical address.

longitude

string

The longitude of the physical address.

timezone

string

The timezone of the location.

isOpen

boolean

If true, the location is operational;
if false or omitted, the location is not working - either not open yet, or suspended for some other reason.

isPublic

boolean

If true, the location is shown in the members portal;
if false or omitted the location is not displayed in the members portal.

image

string

The URL pointing to an image assigned to this location.

code

string

A unique code of the location.

targetRevenuePerPeriod

array of objects

An array of target revenue amounts per period for this location. Used for tracking revenue goals over time.

targetRevenuePerPeriod

object

startDate

date-time

The start date of the revenue target period.

endDate

date-time

The end date of the revenue target period. If not specified, the target applies indefinitely from the start date.

target

number

The target revenue amount for this period.

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

     --url https://app.officernd.com/api/v2/organizations/orgSlug/locations/locationId \

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

  "name": "Location 1",

  "address": "",

  "timezone": "UTC",

  "isOpen": true,

  "isPublic": true,

  "image": "//example.com/image.jpg",

  "code": "LOC123",

  "targetRevenuePerPeriod": [\
\
    {\
\
      "startDate": "2024-01-01T00:00:00.000Z",\
\
      "endDate": "2024-12-31T23:59:59.999Z",\
\
      "target": 50000\
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