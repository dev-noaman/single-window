# Get visit

Source: https://developer.officernd.com/reference/visitscontroller_getitem

visitId

string

required

The \_id of the visit

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

The \_id of the visit.

member

string

The \_id of the member for which the visit is being recorded.

visitor

string

The \_id of the visitor for which the visit is being recorded.

location

string

The \_id of the location for which the visit is being recorded.

start

date-time

The start date and time of the visit.

end

date-time

The end date and time of the visit.

receptionFlow

string

The \_id of the reception flow for which the visit is being recorded.

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

     --url https://app.officernd.com/api/v2/organizations/orgSlug/visits/visitId \

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

  "member": "603dfbc260f4054084125d38",

  "visitor": "603dfbc260f4054084125d34",

  "location": "603dfbc260f4054084125d36",

  "start": "2022-02-07T10:03:33.169Z",

  "end": "2022-02-07T10:03:33.169Z",

  "receptionFlow": "603dfbc260f4054084125d34"

}
```

Updated 5 months ago

* * *

Did this page help you?

Yes

No