# Update a secondary currency

Source: https://developer.officernd.com/reference/secondarycurrenciescontroller_updateitem

secondaryCurrencyId

string

required

The id of the corresponding secondary currency

orgSlug

string

required

organization slug

exchangeRate

number

The exchange rate of the secondary currency.

# `` 200

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

curl --request PUT \

     --url https://app.officernd.com/api/v2/organizations/orgSlug/secondary-currencies/secondaryCurrencyId \

     --header 'accept: application/json' \

     --header 'content-type: application/json'
```

```

xxxxxxxxxx



{

  "_id": "6985f1684cc913fc5ac7bf8b",

  "code": "USD",

  "exchangeRate": 2.56

}
```

Updated 5 months ago

* * *

Did this page help you?

Yes

No