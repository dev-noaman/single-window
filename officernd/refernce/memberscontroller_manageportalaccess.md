# Manage member portal access

Source: https://developer.officernd.com/reference/memberscontroller_manageportalaccess

memberId

string

required

member id

orgSlug

string

required

organization slug

isPortalAccessEnabled

boolean

required

Determines whether the member has access to the members portal.

truefalse

shouldSendInvitation

boolean

Defaults to false

Determines if an invitation email should be sent to the user. If not provided, defaults to false.

truefalse

`` 204

Updated 7 days ago

* * *

Did this page help you?

Yes

No

ShellNodeRubyPHPPython

Bearer

```

xxxxxxxxxx

curl --request PUT \

     --url https://app.officernd.com/api/v2/organizations/orgSlug/members/memberId/portal-access \

     --header 'content-type: application/json' \

     --data '

{

  "isPortalAccessEnabled": true,

  "shouldSendInvitation": false

}

'
```

Click `Try It!` to start a request and see the response here!

Updated 7 days ago

* * *

Did this page help you?

Yes

No