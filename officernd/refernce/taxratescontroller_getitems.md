# Retrieve all tax rates.

Source: https://developer.officernd.com/reference/taxratescontroller_getitems

orgSlug

string

required

organization slug

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

The \_id of the tax rate.

name

string

The name of the tax rate in hand.

code

string

A unique code to identify the tax rate.

type

string

The type of the tax rate.

rate

number

The rate of the tax rate. It will be automatically calculated based on the percentage rate of the components.

components

array of objects

A list of tax rate components. Each tax rate component needs to have a name and rate of its own.

components

object

\_id

string

The \_id of the tax rate component.

name

string

The name of the tax rate component.

rate

number

The rate of the tax rate component.

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

     --url https://app.officernd.com/api/v2/organizations/orgSlug/tax-rates \

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
      "_id": "6985f15e4cc913fc5ac7bf42",\
\
      "name": "",\
\
      "code": "",\
\
      "type": "",\
\
      "rate": "",\
\
      "components": []\
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