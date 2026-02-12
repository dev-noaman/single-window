# Terminate a contract

Source: https://developer.officernd.com/reference/contractscontroller_terminateitem

contractId

string

required

contract id

orgSlug

string

required

organization slug

date

date-time

The date of the termination.

reasonKey

string

The reason for the termination.

comments

string

Comments about the termination.

`` 202

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

     --url https://app.officernd.com/api/v2/organizations/orgSlug/contracts/contractId/terminate \

     --header 'content-type: application/json'
```

Click `Try It!` to start a request and see the response here!

Updated 5 months ago

* * *

Did this page help you?

Yes

No