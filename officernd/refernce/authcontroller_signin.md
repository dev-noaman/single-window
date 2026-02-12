# Sign in a user

Source: https://developer.officernd.com/reference/authcontroller_signin

orgSlug

string

required

organization slug

email

string

required

The email which was registered during signup as a login credential.

password

string

required

The password which was registered during signup as a login credential.

# `` 200

object

\_id

string

The \_id of the user.

email

string

The email of the user.

name

string

The name of the user.

image

string

The image of the user.

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

     --url https://app.officernd.com/api/v2/organizations/orgSlug/auth/signin \

     --header 'accept: application/json' \

     --header 'content-type: application/json'
```

```

xxxxxxxxxx



{

  "_id": "6985f1694cc913fc5ac7bf91",

  "email": "example@gmail.com",

  "name": "John Doe",

  "image": "John Doe"

}
```

Updated 5 months ago

* * *

Did this page help you?

Yes

No