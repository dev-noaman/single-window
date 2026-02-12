# Retrieve all payment methods

Source: https://developer.officernd.com/reference/paymentscontroller_getpaymentmethods

orgSlug

string

required

organization slug

locations

array of strings

Filter by location ids

locations
ADD string

# `` 200

object

paymentMethods

array of strings

required

An array of payment methods.

paymentMethods\*

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

     --url https://app.officernd.com/api/v2/organizations/orgSlug/payments/methods \

     --header 'accept: application/json'
```

```

xxxxxxxxxx



{

  "paymentMethods": [\
\
    "Cash",\
\
    "Credit Card",\
\
    "Bank Transfer"\
\
  ]

}
```

Updated 5 months ago

* * *

Did this page help you?

Yes

No