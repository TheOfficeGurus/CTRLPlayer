# CTRLPlayer API Client Documentation

This document describes how to interact with the CTRLPlayer API. The API uses JWT authentication and provides endpoints for authentication and user management

---

## Authentication

### 1. Login

**Endpoint:**  
`POST /auth/login`

**Description:**  
Obtain a JWT token for subsequent requests.

**Request Body:**

```json
{
  "service": "serviceName",
  "environment": "environmentType",
  "phrase": "your_secret_phrase"
}
```

**Response:**

- **Success:**  

  `200 OK`

  ```json
  {
    "token": "Bearer <JWT_TOKEN>"
  }
  ```

- **Error:**  
  `400/401/403/500`

  ```json
  {
    "success": false,
    "error": "Error message"
  }
  ```

---

## User Endpoints

**All user endpoints require the `Authorization` header:**

```
Authorization: Bearer <JWT_TOKEN>
```

---

### 2. Verify User by Username

**Endpoint:**  
`POST /users/verify`

**Description:**  
Verify if a user exists in Active Directory and if the provided full name matches.

**Request Body:**

```json
{
  "username": "jdoe",
  "fullname": "John Doe"
}
```

**Response:**

- **Success:**  
  `200 OK`

  ```json
  {
    "success": true,
    "message": "Success",
    "data": {
      "VerifyUserAD": {
        "fullname": "John Doe",
        "username": "jdoe",
        "EmployeeID": "12345"
      }
    }
  }

  ```

- **Error:**  
  `400/401/500`

  ```json
  {
    "success": false,
    "error": "the Entra name does not match with the provided ..."
  }
  ```

---

### 3. Verify User by Full Name

**Endpoint:**  
`POST /users/verify_fullname`

**Description:**  
Verify if a user exists in Active Directory by full name and username.

**Request Body:**

```json
{
  "fullname": "John Doe"
}
```

**Response:**

- **Success:**  
  `200 OK`

  ```json
  {
    "success": true,
    "message": "Success",
    "data": {
      "Employee": {
        "fullname": "John Doe",
        "username": "jdoe",
        "EmployeeID": "12345"
      }
    }
  }
  ```

- **Error:**  
  `400/401/500`

  ```json
  {
    "success": false,
    "error": "the Entra name does not match with the provided ..."
  }
  ```

---

### 4. Assign Employee ID

**Endpoint:**  
`POST /users/assignEmployeeId`

**Description:**  
Assign a new Employee ID to a user.

**Request Body:**

```json
{
  "username": "jdoe",
  "fullname": "John Doe",
  "employeeId": "67890",
  "updatedBy": "admin"
}
```

**Response:**

- **Success:**  
  `200 OK`

  ```json
  {
    "success": true,
    "message": "Success",
    "data": {
      "Assigned": true,
      "Employee": {
        "fullname": "John Doe",
        "username": "jdoe",
        "EmployeeID": "67890"
      }
    }
  }
  ```

- **Error:**  
  `400/401/500`

  ```json
  {
    "success": false,
    "error": "This EmployeeId 67890 is been used by other employee"
  }
  ```

---

### 5. Assign new Supervisot

**Endpoint:**  
`POST /users/assingSuppervisor`

**Description:**  
Assign a new supervisor to a user.

**Request Body:**

```json
{
    "guru_employeeID": "67890",
    "sup_employeeID": "123",
    "updatedBy":"admin"
}
```

**Response:**

- **Success:**  
  `200 OK`

  ```json
  {
    "success": true,
    "message": "Success",
    "data": {
      "Assigned": true,
      "Employee": {
        "fullname": "John Doe",
        "username": "jdoe",
        "EmployeeID": "67890",
        "Manager": "John Smith"
      }
    }
  }
  ```

- **Error:**  
  `400/401/500`

  ```json
  {
    "success": false,
    "error": "This supervisor badge number does not exists, is inactive or is out of context:  "
  }
  ```

---

## Error Handling

All endpoints return errors in the following format:

```json
{
  "success": false,
  "error": "Error message"
}
```

---

## Example Usage

### Python

<details>

```python
import requests

# 1. Login
login_resp = requests.post(
    "https://ctrlplayer.tog.solutions/auth/login",
    json={"service": "serviceName", "environment": "environmentType", "phrase": "your_secret_phrase"}
)
token = login_resp.json()["token"]

headers = {"Authorization": token}

# 2. Verify user
verify_resp = requests.post(
    "https://ctrlplayer.tog.solutions/users/verify",
    json={"username": "jdoe", "fullname": "John Doe"},
    headers=headers
)
print(verify_resp.json())
```

</details>

### C#

<details>

```csharp
try
  {
    // 1. Login
    var loginData = new
    {
        service = "serviceName",
        environment = "environmentType",
        phrase = "your_secret_phrase"
    };
    
    var loginJson = JsonConvert.SerializeObject(loginData);
    var loginContent = new StringContent(loginJson, Encoding.UTF8, "application/json");
    
    var loginResponse = await client.PostAsync(
        "https://ctrlplayer.tog.solutions/auth/login", 
        loginContent
    );
    
    var loginResult = await loginResponse.Content.ReadAsStringAsync();
    dynamic loginData = JsonConvert.DeserializeObject(loginResult);
    string token = loginData.token;
    
    client.DefaultRequestHeaders.Add("Authorization", token);
    
    // 2. Verify user
    var verifyData = new
    {
        username = "jdoe",
        fullname = "John Doe"
    };
    
    var verifyJson = JsonConvert.SerializeObject(verifyData);
    var verifyContent = new StringContent(verifyJson, Encoding.UTF8, "application/json");
    
    var verifyResponse = await client.PostAsync(
        "https://ctrlplayer.tog.solutions/users/verify",
        verifyContent
    );
    
    var verifyResult = await verifyResponse.Content.ReadAsStringAsync();
    Console.WriteLine(verifyResult);
  }
  catch (Exception ex)
  {
      Console.WriteLine($"Error: {ex.Message}");
  }
```

</details>
---

## Notes

- All endpoints require a valid JWT token except `/auth/login`.
- Always use the correct parameter names and types as shown above.
- Error messages and codes may vary depending on the cause.

---

For further questions, contact the API administrators or A51

`version2 - 3b7dff6`
