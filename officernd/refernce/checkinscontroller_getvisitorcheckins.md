# Retrieve all visitor check-ins.

Source: https://developer.officernd.com/reference/checkinscontroller_getvisitorcheckins

orgSlug

string

required

organization slug

\_id

string

Filter by the \_id of the check-in.

company

string

Filter by the company associated with the check-in.

member

string

Filter by the company associated with the check-in.

location

string

Filter by the location associated with the check-in.

source

string

Filter by the source associated with the check-in.

start

string

Support date comparison filters: $gt, $gte, $lt, $lte

end

string

Support date comparison filters: $gt, $gte, $lt, $lte

createdAt

date-time

Support date comparison filters: $gt, $gte, $lt, $lte

visitor

string

Filter by the visitor associated with the check-in.

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

The \_id of the check-in.

start

date-time

Contains the start date of the check-in.

end

date-time

Contains the end date of the check-in.

location

string

The \_id of the location associated with the check-in.

company

string

The \_id of the company associated with the check-in.

member

string

The \_id of the member associated with the check-in.

booking

string

The \_id of the booking associated with the check-in.

pass

string

The \_id of the pass associated with the check-in.

resourceType

string

The resourceType of the booking associated with the check-in.

source

string

The source associated with the check-in.

visitor

string

The \_id of the location visitor associated with the check-in.

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

     --url https://app.officernd.com/api/v2/organizations/orgSlug/checkins/visitors \

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
      "start": "2024-10-31T13:15:00.000Z",\
\
      "end": "2024-10-31T15:30:00.000Z",\
\
      "location": "6080186f490fcf6e0547ec57",\
\
      "company": "6080186f490fcf6e0547ec57",\
\
      "member": "6080186f490fcf6e0547ec57",\
\
      "booking": "6080186f490fcf6e0547ec57",\
\
      "pass": "6080186f490fcf6e0547ec57",\
\
      "resourceType": "hotdesk",\
\
      "source": "admin",\
\
      "visitor": "6080186f490fcf6e0547ec57"\
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