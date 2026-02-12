# Impersonate a member

Source: https://developer.officernd.com/reference/authcontroller_impersonatemember

orgSlug

string

required

organization slug

email

string

required

The email of the member with which the member is registered.

# `` 200

object

token

string

The generated token which you can use as authentication for various requests.

Updated 5 months ago

* * *

Did this page help you?

Yes

No

ShellNodeRubyPHPPython

Bearer

```

xxxxxxxxxx

curl --request POST \

     --url https://app.officernd.com/api/v2/organizations/orgSlug/auth/impersonate \

     --header 'accept: application/json' \

     --header 'content-type: application/json'
```

```

xxxxxxxxxx



{

  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6IjU4NDZmMjhhZmY1ZDg4MTI2YWJjZmMzZiIsImlhdCI6MTQ4MTExNjQwOCwiZXhwIjoxNDgxMjg5MjA4fQ.ElceBwjTRBhu669SWkn_Za8VKk-cwomzmbEsNywPt5A"

}
```

Updated 5 months ago

* * *

Did this page help you?

Yes

No