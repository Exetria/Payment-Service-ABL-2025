# Payment Endpoints

### 1. Create Payment

**URL**: `/payment`

**Method**: `POST`

**Description**: Create new payment

**Request Header**
```json
{
  "Authorization": <token>
}
```

**Request Body**:

```json
{
  "customer_id": 12345423,
  "requester_type": 1,
  "requester_id": 12345,
  "secondary_requester_id": 67890,
  "payment_method": "bca_va",
  "payment_amount": 150000.0
}
```

**Response**:

- Status: `200 - OK`
- Body:

```json
{
    "id": 1
}
```

---

### 2. Get Payment List

**URL**: `/payment`

**Method**: `GET`

**Description**: Get all payment

**Request Header**
```json
{
  "Authorization": <token>
}
```

**Response**:

- Status: `200 - OK`
- Body:

```json
[
    {
        "id": 1,
        "payment_amount": 150000.0,
        "payment_method": "bca_va",
        "status": 1,
        "settle_date": null,
        "secondary_requester_id": 67890,
        "payment_info": "02487385974310231818750",
        "customer_id": 12345423,
        "requester_id": 12345,
        "requester_type": "Order"
    }
]
```

---

### 3. Get Payment by ID

**URL**: `/payment/:id`

**Method**: `GET`

**Description**: Get payment using ID

**Request Header**
```json
{
  "Authorization": <token>
}
```

**Response**:

- Status: `200 - OK`
- Body:

```json
{
    "id": 1,
    "payment_amount": 150000.0,
    "payment_method": "bca_va",
    "status": 1,
    "settle_date": null,
    "secondary_requester_id": 67890,
    "payment_info": "02487385974310231818750",
    "customer_id": 12345423,
    "requester_id": 12345,
    "requester_type": "Order"
}
```

---

### 4. Get Payments by Customer ID

**URL**: `/payment/customer/:customerId`

**Method**: `GET`

**Description**: Get payments with the same customer ID

**Request Header**
```json
{
  "Authorization": <token>
}
```

**Response**:

- Status: `200 - OK`
- Body:

```json
[
    {
        "id": 1,
        "payment_amount": 150000.0,
        "payment_method": "bca_va",
        "status": 1,
        "settle_date": null,
        "secondary_requester_id": 67890,
        "payment_info": "02487385974310231818750",
        "customer_id": 12345423,
        "requester_id": 12345,
        "requester_type": "Order"
    }
]
```

---

### 5. Get Payments by Requester ID

**URL**: `/payment/requeste/:requesterId`

**Method**: `GET`

**Description**: Get payments with the same requester ID

**Request Header**
```json
{
  "Authorization": <token>
}
```

**Response**:

- Status: `200 - OK`
- Body:

```json
[
    {
        "id": 1,
        "payment_amount": 150000.0,
        "payment_method": "bca_va",
        "status": 1,
        "settle_date": null,
        "secondary_requester_id": 67890,
        "payment_info": "02487385974310231818750",
        "customer_id": 12345423,
        "requester_id": 12345,
        "requester_type": "Order"
    }
]
```

---

### 6. Get Payment Status

**URL**: `/payment/:id/status`

**Method**: `GET`

**Description**: Get payment status

**Request Header**
```json
{
  "Authorization": <token>
}
```

**Response**:

- Status: `200 - OK`
- Body:

```json
{
    "status": 1
}
```

---

### 7. Get Payment Amount

**URL**: `/payment/:id/amount`

**Method**: `GET`

**Description**: Get payment status

**Request Header**
```json
{
  "Authorization": <token>
}
```

**Response**:

- Status: `200 - OK`
- Body:

```json
{
    "amount": 150000.0
}
```

---

### 8. Complete Payment

**URL**: `/payment/:id/complete`

**Method**: `PATCH`

**Description**: Complete payment (cash only)

**Request Header**
```json
{
  "Authorization": <token>
}
```

**Response**:

- Status: `200 - OK`
- Body:

```json
{
    "response": "Success"
}
```

---

### 9. Cancel Payment

**URL**: `/payment/:id/cancel`

**Method**: `PATCH`

**Description**: Cancel payment 

**Request Header**
```json
{
  "Authorization": <token>
}
```

**Response**:

- Status: `200 - OK`
- Body:

```json
{
    "response": "Success"
}
```

---