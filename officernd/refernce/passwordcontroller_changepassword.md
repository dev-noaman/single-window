# Change password

Source: https://developer.officernd.com/reference/passwordcontroller_changepassword

orgSlug

string

required

organization slug

email

string

required

The email of your user.

oldPassword

string

required

The old password that you'd like to change.

newPassword

string

required

The new password you'd like to set.

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

curl --request PUT \

     --url https://app.officernd.com/api/v2/organizations/orgSlug/password \

     --header 'content-type: application/json'
```

Click `Try It!` to start a request and see the response here!

Updated 5 months ago

* * *

Did this page help you?

Yes

No