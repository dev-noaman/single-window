# Update allocation accounting

Source: https://developer.officernd.com/reference/paymentscontroller_updateallocationaccounting

allocationId

string

required

Id of the allocated payment

paymentId

string

required

invoice/overpayment/credit note id

orgSlug

string

required

organization slug

provider

string

required

The name of the accounting provider.

providerId

string

The id of the payment in the accounting provider.

externalOrgId

string

required

The organization id in the accounting provider.

deepLink

string

A deep link to the payment in the accounting provider.

lastSync

string

The date of the last sync of the payment with the accounting integration.

error

string

An error message with more details about the reason of the failure.

# `` 200

object

properties

object

An object that contains all custom properties that can be applied to the item.

Has additional fields

\_id

string

The id of the payment.

number

string

The document number for the payment.

documentType

string

enum

The type of the document. It could be either invoice, creditNote, or overpayment. If omitted, invoice is assumed.

`creditNote``invoice``overpayment``paymentCharge`

date

string

The issue date of the payment.

dueDate

string

The due date of the payment.

company

string

A reference to the company the payment is issued for.

member

string

A reference to the member or individual the payment is issued for.

location

string

A reference to the location the payment is issued by.

reference

string

Additional data describing the payment. It could be any string value.

taxType

string

enum

The type of the tax calculation for the payment. It could be excluded, included or noTax.

`included``excluded``noTax`

allocations

array of objects

A list of credit allocations. Each allocation has amount and target.

allocations

object

\_id

string

The id of the credit allocation.

target

string

If payment is an invoice, a reference to the credit note, sourcing the credit.
If payment is a credit note, a reference to the invoice the credit is allocated to.

amount

number

The allocated amount.

documentType

string

enum

The type of document that was allocated to the payment.

`creditNote``invoice``overpayment``paymentCharge`

accounting

object

The accounting data for the allocation.

accounting object

lines

array of objects

A list of payment line items.

lines

object

taxPercent

number

The tax percent applied to the line item.

taxAmount

number

The tax amount applied to the line item.

price

number

The total price as described in the system.

discountAmount

number

The calculated discount amount based on the discount set in the payment.

unitPrice

number

Based on the quantity of the line item, this is the price of a single unit.

baseUnitPrice

number

Based on the quantity of the line item, this is the price of a single unit in the base currency.

subTotal

number

The subtotal of the line item (including tax).

baseTotal

number

The total price of the line item in the base currency (including discount).

total

number

The total for the line item (including tax).

convertedAmounts

object

If the invoice's currency is different than the base currency of the organization,
these are the converted stats for the line item.

convertedAmounts object

description

string

Description of the line item.

account

string

A reference to the account the line item is allocated to.

plan

string

A reference to the plan the line item is for.

fee

string

A reference to the fee the line item is for.

location

string

A reference to the location the line item is for.

membership

string

deprecated

A reference to the membership the line item is for. @deprecated Use memberships array instead.

taxRate

string

A reference to the taxRate the line item is for.

discount

number

Based on the quantity of the line item, this is the total discount that applied.

unitDiscount

number

Based on the quantity of the line item, this is the single discount of a unit.

quantity

number

The quantity of items described in the line item.

startDate

string

The start date of the billing period.

endDate

string

The end date of the billing period.

addOns

object

Any addons that are included in the membership will be added here.

addOns object

fees

array of strings

An array of fee references from the original lines that were merged into this invoice line.

fees

memberships

array of strings

An array of membership references from the original lines that were merged into this invoice line.

memberships

processingFeeLine

object

The processing fee of the payment.

taxPercent

number

The tax percent applied to the line item.

taxAmount

number

The tax amount applied to the line item.

price

number

The total price as described in the system.

discountAmount

number

The calculated discount amount based on the discount set in the payment.

unitPrice

number

Based on the quantity of the line item, this is the price of a single unit.

baseUnitPrice

number

Based on the quantity of the line item, this is the price of a single unit in the base currency.

subTotal

number

The subtotal of the line item (including tax).

baseTotal

number

The total price of the line item in the base currency (including discount).

total

number

The total for the line item (including tax).

convertedAmounts

object

If the invoice's currency is different than the base currency of the organization,
these are the converted stats for the line item.

convertedAmounts object

description

string

Description of the line item.

account

string

A reference to the account the line item is allocated to.

plan

string

A reference to the plan the line item is for.

fee

string

A reference to the fee the line item is for.

location

string

A reference to the location the line item is for.

membership

string

deprecated

A reference to the membership the line item is for. @deprecated Use memberships array instead.

taxRate

string

A reference to the taxRate the line item is for.

discount

number

Based on the quantity of the line item, this is the total discount that applied.

unitDiscount

number

Based on the quantity of the line item, this is the single discount of a unit.

quantity

number

The quantity of items described in the line item.

startDate

string

The start date of the billing period.

endDate

string

The end date of the billing period.

addOns

object

Any addons that are included in the membership will be added here.

addOns object

fees

array of strings

An array of fee references from the original lines that were merged into this invoice line.

fees

memberships

array of strings

An array of membership references from the original lines that were merged into this invoice line.

memberships

taxAmounts

array of arrays

A list of payment tax amounts.

taxAmounts

array

subTotal

number

The total of the payment before tax.

amount

number

The total of the payment after tax and discount.

payableAmount

number

Total amount due for this payment. Voided and paid payments have payableAmount of 0.

accounting

object

Data on the payment sync with an accounting integration.

provider

string

The name of the accounting provider.

providerId

string

The id of the payment in the accounting provider.

externalOrgId

string

The organization id in the accounting provider.

deepLink

string

A deep link to the payment in the accounting provider.

lastSync

string

The date of the last sync of the payment with the accounting integration.

error

string

An error message with more details about the reason of the failure.

baseTotal

number

The base total amount of the payment.

total

number

The total amount of the payment.

paidAmount

number

The total amount paid for the payment.

pendingAmount

number

The total amount pending for the payment.

allocatedAmount

number

The total amount allocated for the payment.

currency

string

The currency of the payment.

currencyConversionRate

number

The conversion rate for the currency of the payment.

isFailed

boolean

Determines whether the payment is considered as failed.

isPaid

boolean

Determines whether the payment is considered as paid.

isSent

boolean

Shows if the payment has been sent.

status

string

enum

The status of the payment.

`voided``failed``draft``pending``refunded``paid``awaiting_payment``partially_paid`

chargeMethod

string

The charge method of the payment.

createdAt

string

The date when the payment has been created at.

createdBy

string

The user that created the payment.

modifiedAt

string

The date when the payment has been modified for the last time. Note that adding/removing charges and credit allocations are considered modifications to both the invoice and the credit note/overpayment.

modifiedBy

string

The user that did the last modification to the payment. Before the first modification, this field equals to the createdBy field.

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

     --url https://app.officernd.com/api/v2/organizations/orgSlug/payments/paymentId/allocations/allocationId/accounting \

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

  "_id": "6780f1ba1a2b3c4d5e6f7a8b",

  "number": "INV-123",

  "documentType": "creditNote",

  "date": "2025-01-01T00:00:00.000Z",

  "dueDate": "2025-01-01T00:00:00.000Z",

  "company": "6780f1ba3c4d5e6f7a8b9c0d",

  "member": "6780f1ba2b3c4d5e6f7a8b9c",

  "location": "6780f1ba4d5e6f7a8b9c0d1e",

  "reference": "Payment for the membership fee.",

  "taxType": "included",

  "allocations": [],

  "lines": [\
\
    {\
\
      "description": "Membership fee",\
\
      "quantity": 2,\
\
      "account": "6780f1ba5e6f7a8b9c0d1e2f",\
\
      "plan": "6780f1ba6f7a8b9c0d1e2f3a",\
\
      "fee": "6780f1ba7a8b9c0d1e2f3a4b",\
\
      "membership": "6780f1ba9c0d1e2f3a4b5c6d",\
\
      "location": "6780f1ba4d5e6f7a8b9c0d1e",\
\
      "taxRate": "6780f1ba1e2f3a4b5c6d7e8f",\
\
      "taxPercent": 25,\
\
      "taxAmount": 25.7,\
\
      "discountAmount": 10,\
\
      "price": 60,\
\
      "unitPrice": 30,\
\
      "unitDiscount": 5,\
\
      "subTotal": 60,\
\
      "baseUnitPrice": 70,\
\
      "baseTotal": 60,\
\
      "total": 60,\
\
      "startDate": "2025-01-01T00:00:00.000Z",\
\
      "endDate": "2025-01-01T00:00:00.000Z",\
\
      "convertedAmounts": {\
\
        "price": 60,\
\
        "discountAmount": 10,\
\
        "baseUnitPrice": 70,\
\
        "subTotal": 60,\
\
        "unitPrice": 30,\
\
        "taxAmount": 12,\
\
        "taxPercent": 15,\
\
        "baseTotal": 60,\
\
        "total": 60\
\
      },\
\
      "addons": [\
\
        {\
\
          "name": "Addon 1",\
\
          "unitPrice": 10,\
\
          "description": "Addon description"\
\
        },\
\
        {\
\
          "name": "Addon 2",\
\
          "unitPrice": 20,\
\
          "description": "Addon description"\
\
        }\
\
      ],\
\
      "fees": [\
\
        "6780f1ba7a8b9c0d1e2f3a4b",\
\
        "6780f1ba8b9c0d1e2f3a4b5c"\
\
      ],\
\
      "memberships": [\
\
        "6780f1ba9c0d1e2f3a4b5c6d"\
\
      ]\
\
    }\
\
  ],

  "processingFeeLine": {

    "description": "3.11% Processing Fee",

    "account": "6780f1ba5e6f7a8b9c0d1e2f",

    "plan": "6780f1ba6f7a8b9c0d1e2f3a",

    "fee": "6780f1ba7a8b9c0d1e2f3a4b",

    "taxRate": "6780f1ba1e2f3a4b5c6d7e8f",

    "discount": 0,

    "quantity": 1

  },

  "taxAmounts": [\
\
    {\
\
      "percent": 25,\
\
      "total": 25.7,\
\
      "taxRate": "6780f1ba1e2f3a4b5c6d7e8f"\
\
    }\
\
  ],

  "subTotal": 60,

  "amount": 60,

  "payableAmount": 60,

  "accounting": {

    "provider": "xero",

    "providerId": "123456789",

    "externalOrgId": "987654321",

    "deepLink": "https://xero.com/123456789",

    "lastSync": "2025-01-01T00:00:00.000Z",

    "error": "An error occurred while syncing with Xero"

  },

  "baseTotal": 60,

  "total": 80,

  "paidAmount": 40,

  "pendingAmount": 40,

  "allocatedAmount": 40,

  "currency": "USD",

  "currencyConversionRate": 0.98567,

  "isFailed": false,

  "isPaid": true,

  "isSent": false,

  "status": "partially_paid",

  "chargeMethod": "Credit Card",

  "createdAt": "2025-01-01T00:00:00.000Z",

  "createdBy": "6780f1ba4b5c6d7e8f9a0b1c",

  "modifiedAt": "2025-01-01T00:00:00.000Z",

  "modifiedBy": "6780f1ba4b5c6d7e8f9a0b1c"

}
```

Updated 5 months ago

* * *

Did this page help you?

Yes

No