# Retrieve single resource rate.

Source: https://developer.officernd.com/reference/resourceratescontroller_getitem

resourceRateId

string

required

resource rate id

orgSlug

string

required

organization slug

# `` 200

object

\_id

string

The \_id of the rate.

name

string

The name of the rate in hand.

code

string

A unique code to identify the rate.

description

string

A short description of the rate.

type

string

The type of the rate.

intervalLength

string

enum

The type of interval of the rate.

`once``hour``day``month`

intervalCount

number

The amount of intervals of the rate.

price

number

The price of the main component - i.e. either price per hour or price per day.

shouldProrate

boolean

Shows if the rate has proration

useCoins

boolean

Shows if coins can be used in the rate.

rates

array of objects

An array containing the secondary components of the rate.

rates

object

\_id

string

The \_id of the rate component.

price

number

The price of the secondary component.

intervalLength

string

enum

Depending on the type of the component can be either hour, day, week or month.

`hour``day``week``month`

intervalCount

number

Can be either 1 or 4 depending on the type of rate. 1 is used for most rates, 4 is used only for half-day rates. This is used for internal calculations mainly.

isOffRate

boolean

Determines if the rate is a non-business hours rate. If the parameter is missing then it's considered false.

isWeekendRate

boolean

Determines if the rate is a weekend rate. If the parameter is missing then it's considered false.

isHalfDayRate

boolean

Determines if the rate is a half-day rate. If the parameter is missing then it's considered false.

extras

array of strings

An array with all the extras in the rate.

extras

revenueAccount

string

The \_id of the revenue account with which the rate is associated. If missing, the default "Booking fees" account rate will be used.

locations

array of strings

An array of location \_ids, that determine for which location the plan is valid. If empty, the rate can be used for all locations.

locations

amenities

array of strings

An array of amenity \_ids, that determine which amenities are available for this rate.

amenities

createdAt

date-time

The time at which the rate was created.

createdBy

string

The \_id of the user that created the rate.

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

     --url https://app.officernd.com/api/v2/organizations/orgSlug/resource-rates/resourceRateId \

     --header 'accept: application/json'
```

```

xxxxxxxxxx



{

  "_id": "6080186f490fcf6e0537ec52",

  "name": "Rate 1",

  "code": "EXMPL",

  "description": "Example description",

  "type": "meeting_room",

  "intervalLength": "day",

  "intervalCount": 3,

  "price": 45,

  "shouldProrate": true,

  "useCoins": true,

  "rates": [\
\
    {\
\
      "_id": "67a2048010bab41f9aed3512",\
\
      "price": 150,\
\
      "intervalLength": "hour",\
\
      "intervalCount": 4,\
\
      "isWeekendRate": true,\
\
      "isHalfDayRate": true\
\
    },\
\
    {\
\
      "_id": "67a2048010bab41f9aed35df",\
\
      "price": 14,\
\
      "intervalLength": "week",\
\
      "intervalCount": 1\
\
    }\
\
  ],

  "extras": [\
\
    "6080186f490fcf6e0537eb20",\
\
    "6080186f490fcf6e0537eb25"\
\
  ],

  "revenueAccount": "6080186f490fcf6e0537ed15",

  "locations": [\
\
    "6080186f490fcf6e0537eb22",\
\
    "6080186f490fcf6e0537eb29"\
\
  ],

  "amenities": [\
\
    "6080186f490fcf6e0537eb21",\
\
    "6080186f490fcf6e0537eb23"\
\
  ],

  "createdAt": "2021-04-21T18:00:00.000Z",

  "createdBy": "5bbb155174321f100085eac1"

}
```

Updated 5 months ago

* * *

Did this page help you?

Yes

No