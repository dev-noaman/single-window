# Get single revenue account.

Source: https://developer.officernd.com/reference/revenueaccountscontroller_getitem

accountId

string

required

revenue account id

orgSlug

string

required

organization slug

# `` 200

object

\_id

string

The \_id of the revenue account.

name

string

The name of the revenue account.

description

string

The description of the revenue account.

code

string

A unique code to identify the revenue account.

defaultFor

string

This field will appear only for default accounts (by default, there are four pre-set accounts: Booking fees, Deposits, Membership fees, One-off Fees). In the field, you'll be able to see the item for which the account is created - bookings, fees etc.

taxRate

string

A reference to the tax rate that will be applied to the revenue account.

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

     --url https://app.officernd.com/api/v2/organizations/orgSlug/revenue-accounts/accountId \

     --header 'accept: application/json'
```

```

xxxxxxxxxx



{

  "_id": "",

  "name": "",

  "description": "",

  "code": "",

  "defaultFor": "",

  "taxRate": ""

}
```

Updated 5 months ago

* * *

Did this page help you?

Yes

No