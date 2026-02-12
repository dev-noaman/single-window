# Update company

Source: https://developer.officernd.com/reference/companiescontroller_updateitem

companyId

string

required

company id

orgSlug

string

required

organization slug

properties

object

An object that contains all custom properties that can be applied to the item.

properties object

startDate

date-time

The start date of the company.

location

string

The location of the company.

name

string

The name of the company.

description

string

The description of the company.

email

string

The email of the company.

image

string

The logo/image URL of the company.

url

string

The website URL of the company.

address

object

The address of the company.

address object

billingDetails

object

The billing details of the company.

billingDetails object

portalPrivacy

object

The portal privacy settings of the company.

portalPrivacy object

hasActiveMembersAllowance

boolean

Indicates whether the "Active members allowance" setting is enabled.

truetruefalse

activeMembersAllowanceLimit

number

The limit of active member seats that can be added to the company.

# `` 200

object

properties

object

An object that contains all custom properties that can be applied to the item.

Has additional fields

\_id

string

The id of the company.

startDate

date-time

The start date of the company.

location

string

The location of the company.

name

string

The name of the company.

description

string

The description of the company.

email

string

The email of the company.

image

string

The logo/image URL of the company.

url

string

The website URL of the company.

address

object

The address details of the company.

country

string

The country of the address.

state

string

The state of the address.

city

string

The city of the address.

street

string

The street of the address.

zip

string

The zip of the address.

status

string

enum

The status of the company.

`active``former``pending``inactive``not_approved``drop-in``lead`

billingDetails

object

The billing details of the company.

billingName

string

The billing name of the company that will appear on transactions and invoices.

vatNumber

string

The VAT number of the company.

registrationNumber

string

The registration number of the company.

paymentMethod

string

The payment method of the company.

billingAddress

object

The billing address of the company.

billingAddress object

portalPrivacy

object

The portal privacy settings of the company.

isVisible

boolean

Determines whether the member's profile is visible in the members portal.

showContactDetails

boolean

Determines whether the member's contact details are visible in the members portal.

showSocialProfiles

boolean

Determines whether the member's (Twitter, LinkedIn, Facebook, Instragram) socials are visible in the members portal.

hasActiveMembersAllowance

boolean

Indicates whether the "Active members allowance" setting is enabled.

activeMembersAllowanceLimit

number

The limit of active member seats that can be added to the company.

tags

array of strings

An array of tags associated with the company.

tags

createdAt

date-time

The date of creation of the company.

createdBy

string

The user that created the company.

modifiedAt

date-time

The date of the last update the company.

modifiedBy

string

The user that last updated the company.

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

     --url https://app.officernd.com/api/v2/organizations/orgSlug/companies/companyId \

     --header 'accept: application/json' \

     --header 'content-type: application/json'
```

```

xxxxxxxxxx



{

  "properties": {

    "customProperty1": "value1",

    "customProperty2": "value2"

  },

  "_id": "603dfbc260f4054084125d33",

  "startDate": "2025-02-25T00:00:00.000Z",

  "location": "603dfbc260f4054084125d33",

  "name": "My Company",

  "description": "This is the description of the company.",

  "email": "example@gmail.com",

  "image": "image-url.com",

  "url": "company-url.com",

  "address": {

    "country": "United States",

    "state": "California",

    "city": "San Francisco",

    "street": "123 Main St, San Francisco, CA 94105",

    "zip": "94105"

  },

  "status": "active",

  "billingDetails": {

    "billingName": "Example Billing Name",

    "vatNumber": "123456789",

    "registrationNumber": "987654321",

    "paymentMethod": "Cash",

    "billingAddress": {

      "country": "United States",

      "state": "California",

      "city": "San Francisco",

      "street": "123 Main St, San Francisco, CA 94105",

      "zip": "94105"

    }

  },

  "portalPrivacy": {

    "isVisible": true,

    "showContactDetails": false,

    "showSocialProfiles": true

  },

  "hasActiveMembersAllowance": true,

  "activeMembersAllowanceLimit": 10,

  "tags": [\
\
    "tag1",\
\
    "tag2",\
\
    "tag3"\
\
  ],

  "createdAt": "2025-02-25T00:00:00.000Z",

  "createdBy": "603dfbc260f4054084125d33",

  "modifiedAt": "2025-02-25T00:00:00.000Z",

  "modifiedBy": "603dfbc260f4054084125d33"

}
```

Updated 5 months ago

* * *

Did this page help you?

Yes

No