# Create a user

Source: https://developer.officernd.com/reference/authcontroller_signup

orgSlug

string

required

organization slug

email

string

required

The email of the new user.

password

string

required

Password must be at least 8 characters long and contain 3 out of the 4 elements: uppercase letter, lowercase letter, digit or symbol.

name

string

required

The name of the new user.

# `` 201

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

     --url https://app.officernd.com/api/v2/organizations/orgSlug/auth/signup \

     --header 'accept: application/json' \

     --header 'content-type: application/json'
```

```

xxxxxxxxxx



{

  "_id": "6985f1694cc913fc5ac7bf90",

  "email": "example@gmail.com",

  "name": "John Doe"

}
```

Updated 5 months ago

* * *

Did this page help you?

Yes

No