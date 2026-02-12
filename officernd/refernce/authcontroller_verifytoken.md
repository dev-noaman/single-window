# Validate JWT token

Source: https://developer.officernd.com/reference/authcontroller_verifytoken

orgSlug

string

required

organization slug

token

string

required

The JWT token to verify.

# `` 200

object

isValid

boolean

A flag indicating whether the token is valid.

user

string

The user reference.

member

string

The \_id of the member associated with the user.

company

string

The \_id of the company associated with the user.

Updated 11 days ago

* * *

Did this page help you?

Yes

No

ShellNodeRubyPHPPython

Bearer

```

xxxxxxxxxx

curl --request POST \

     --url https://app.officernd.com/api/v2/organizations/orgSlug/auth/verify \

     --header 'accept: application/json' \

     --header 'content-type: application/json'
```

```

xxxxxxxxxx



{

  "isValid": true,

  "user": "6080186f490fcf6e0537ec62",

  "member": "6080186f490fcf6e0537ec67",

  "company": "6080186f490fcf6e0537ec68"

}
```

Updated 11 days ago

* * *

Did this page help you?

Yes

No