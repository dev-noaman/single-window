# Get members count by filter

Source: https://developer.officernd.com/reference/memberscontroller_countby

orgSlug

string

required

organization slug

\_id

string

Filter by the member id.

name

string

Filter by the name of the member. This returns a result only if the name is an exact match.

email

string

Filter by the email of the member. This returns a result only if the email is an exact match.

location

string

Filter by the location id of the member.

company

string

Filter by the company id of the member.

status

string

enum

Filter by the status of the member.
Accepts either a single status value or an array operator filter for multiple values.

```undefined
        Single value: status=active
        Multiple values: status[$in]=active,pending

        Available status values: active, former, pending, contact, not_approved, drop-in, lead
```

status=activeactiveformerpendingcontactnot\_approveddrop-inlead

Allowed:

`active``former``pending``contact``not_approved``drop-in``lead`

createdAt

string

Support date comparison filters: $gt, $gte, $lt, $lte

modifiedAt

string

Support date comparison filters: $gt, $gte, $lt, $lte

properties

string

Filter by custom properties. Uses deepObject style in query. Only string values are supported.

$countBy

string

enum

The field to count by

statuscompanylocation

Allowed:

`status``company``location`

# `` 200

object

total

number

required

groups

array of objects

groups

object

key

string

required

count

number

required

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

     --url https://app.officernd.com/api/v2/organizations/orgSlug/members/count \

     --header 'accept: application/json'
```

```

xxxxxxxxxx



{

  "total": 0,

  "groups": [\
\
    {\
\
      "key": "string",\
\
      "count": 0\
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