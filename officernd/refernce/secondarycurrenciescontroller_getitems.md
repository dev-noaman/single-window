# Retrieve all secondary currencies

Source: https://developer.officernd.com/reference/secondarycurrenciescontroller_getitems

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

The \_id of the secondary currency.

code

string

The code of the secondary currency.

exchangeRate

number

The exchange rate of the secondary currency.

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

     --url https://app.officernd.com/api/v2/organizations/orgSlug/secondary-currencies \

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
      "_id": "6985f1684cc913fc5ac7bf8b",\
\
      "code": "USD",\
\
      "exchangeRate": 2.56\
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