# Get a single integration

Source: https://developer.officernd.com/reference/integrationscontroller_getitem

integrationId

string

required

integration id

orgSlug

string

required

organization slug

# `` 200

object

\_id

string

The \_id of the integration.

type

string

The type of the integration.

user

string

The id of the user that created the integration.

settings

object

The settings of the integration.

appClientId

string

The app client id of the integration.

secret

string

The secret of the integration.

isExternal

boolean

Boolean that indicates whether the integration is external or not.

locations

array of strings

The locations the integration is enabled for.

locations

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

     --url https://app.officernd.com/api/v2/organizations/orgSlug/integrations/integrationId \

     --header 'accept: application/json'
```

```

xxxxxxxxxx



{

  "_id": "6985f1694cc913fc5ac7bf8c",

  "type": "Custom Integration",

  "user": "6985f1694cc913fc5ac7bf8d",

  "settings": {

    "appClientId": "CMyEmnbBa4I4iTAy",

    "secret": "ISUWAVbiyoIaVUyLhr2Fs7byzaqhh1P9",

    "isExternal": true

  },

  "locations": [\
\
    "6985f1694cc913fc5ac7bf8e",\
\
    "6985f1694cc913fc5ac7bf8f"\
\
  ]

}
```

Updated 5 months ago

* * *

Did this page help you?

Yes

No