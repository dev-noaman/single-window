# Reset password

Source: https://developer.officernd.com/reference/passwordcontroller_resetpassword

orgSlug

string

required

organization slug

email

string

required

The email of the user whose password needs to be reset.

`` 204

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

     --url https://app.officernd.com/api/v2/organizations/orgSlug/password/reset \

     --header 'content-type: application/json'
```

Click `Try It!` to start a request and see the response here!

Updated 5 months ago

* * *

Did this page help you?

Yes

No