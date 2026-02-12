# Delete a single webhook

Source: https://developer.officernd.com/reference/webhookscontroller_deleteitem

webhookId

string

required

webhook id

orgSlug

string

required

organization slug

# `` 200

object

\_id

string

The \_id of the webhook.

url

string

The URL of the endpoint of your server where POST requests will be made.

description

string

A description of the webhook.

eventTypes

array of strings

An array containg the type of events associated with the webhook.

eventTypes

secret

string

The secret key used to sign the webhook payload.

isEnabled

boolean

Determines whether the webhook is enabled. If left empty the webhook will be turned on by default.

Updated 5 months ago

* * *

Did this page help you?

Yes

No

ShellNodeRubyPHPPython

Bearer

```

xxxxxxxxxx

curl --request DELETE \

     --url https://app.officernd.com/api/v2/organizations/orgSlug/webhooks/webhookId \

     --header 'accept: application/json'
```

```

xxxxxxxxxx



{

  "_id": "6985f1684cc913fc5ac7bf87",

  "url": "https://webhook.site/1b1b1b1b-1b1b-1b1b-1b1b-1b1b1b1b1b1b",

  "description": "A webhook for testing purposes.",

  "eventTypes": [\
\
    "membership.created",\
\
    "membership.updated"\
\
  ],

  "secret": "1b1b1b1b-1b1b-1b1b-1b1b-1b1b1b1b1b1b",

  "isEnabled": true

}
```

Updated 5 months ago

* * *

Did this page help you?

Yes

No