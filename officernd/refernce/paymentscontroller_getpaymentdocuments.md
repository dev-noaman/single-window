# Get all documents associated with the specific invoice

Source: https://developer.officernd.com/reference/paymentscontroller_getpaymentdocuments

paymentId

string

required

invoice/overpayment/credit note id

orgSlug

string

required

organization slug

# `` 200

object

\_id

string

The \_id of the document associated with the payment.

name

string

The name of the document associated with the payment.

url

string

The URL of the document associated with the payment.

type

string

The template type of the document associated with the payment.

templateName

string

The template name of the document associated with the payment.

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

     --url https://app.officernd.com/api/v2/organizations/orgSlug/payments/paymentId/documents \

     --header 'accept: application/json'
```

```

xxxxxxxxxx



{

  "_id": "6985f15e4cc913fc5ac7bf38",

  "name": "Membership fee",

  "url": "https://example.com/document.pdf",

  "type": "invoice",

  "templateName": "Invoice Template"

}
```

Updated 5 months ago

* * *

Did this page help you?

Yes

No