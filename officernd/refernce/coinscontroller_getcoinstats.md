# Get the coin credit balance for a company/member in a specific month.

Source: https://developer.officernd.com/reference/coinscontroller_getcoinstats

orgSlug

string

required

organization slug

month

string

required

Filter by month in the format YYYY-MM.

company

string

Filter by company id.

member

string

Filter by member id.

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

creditAccount

string

The \_id of the credit account.

resourceRates

array of arrays

An array containing the resource rates for which the set of coins are valid.

resourceRates

array

resourceTypes

array of arrays

An array containing the resource types for which the set of coins are valid.

resourceTypes

array

oneOffPlans

array of arrays

An array containing the one-off plans for which the set of coins are valid.

oneOffPlans

array

validFor

string

enum

Describes the arrays for which the coins are valid. If they are valid for everything the value here will be set to "all".

`rates``resourceTypes``oneOffPlans``all`

member

string

The \_id of the member to which the set of coins are associated.

company

string

The \_id of the company to which the set of coins are associated.

monthly

object

The total number of monthly coins granted for the credit account.

monthly object

once

object

The total number of non-recurring coins granted for the credit account.

once object

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

     --url https://app.officernd.com/api/v2/organizations/orgSlug/coins/stats \

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
      "creditAccount": "603dfbc260f4054084125d30",\
\
      "resourceRates": [\
\
        "603dfbc260f4054084125d30",\
\
        "603dfbc260f4054084125d31"\
\
      ],\
\
      "resourceTypes": [\
\
        "603dfbc260f4054084125d30",\
\
        "603dfbc260f4054084125d31"\
\
      ],\
\
      "oneOffPlans": [\
\
        "603dfbc260f4054084125d30",\
\
        "603dfbc260f4054084125d31"\
\
      ],\
\
      "validFor": "all",\
\
      "member": "603dfbc260f4054084125d33",\
\
      "company": "603dfbc260f4054084125d33",\
\
      "monthly": {\
\
        "total": 100,\
\
        "used": 50,\
\
        "remaining": 50\
\
      },\
\
      "once": {\
\
        "total": 100,\
\
        "used": 50,\
\
        "remaining": 50\
\
      }\
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