# Get contracts count by filter

Source: https://developer.officernd.com/reference/contractscontroller_count

orgSlug

string

required

organization slug

\_id

string

Filter by the exact id of the contract.

company

string

Filter by the id of the company associated with the contract

location

string

Filter by the id of the location associated with the contract.

status

string

enum

Filter by the status of the contract.

not\_signedsigneddraftterminatednot\_signedcanceled

Allowed:

`signed``draft``terminated``not_signed``canceled`

$countBy

string

enum

The field to count by

companycompanylocation

Allowed:

`company``location`

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

     --url https://app.officernd.com/api/v2/organizations/orgSlug/contracts/count \

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