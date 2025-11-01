# BlueFolder API Client (Python)

A modular Python client for interacting with the [BlueFolder API 2.0](https://support.bluefolder.com/hc/en-us/sections/200381849-API-2-0). This library provides organized classes for each major API domain, making it easy to integrate BlueFolder functionality into your applications.

## 📦 Features

- One class per API domain for clarity and separation of concerns.
- Uses `requests` under the hood for API interaction.
- Simple configuration using `.env` or direct instantiation.
- Easily extendable as BlueFolder adds more functionality.

## 🔧 Installation

```bash
git clone https://github.com/ARCofMe/bluefolder-api-client.git
cd bluefolder-api-client
pip install -r requirements.txt  # if requirements file exists
```

## 🚀 Usage

```python
from bluefolder_api.client import BlueFolderAPI

api = BlueFolderAPI(api_key="YOUR_API_KEY", account_name="YOUR_ACCOUNT_NAME")

# List appointments
appointments = api.appointments.list()

# Get a specific customer
customer = api.customers.get(customer_id=1234)
```

### 🔐 Error Handling and Input Validation

This library is built with resilience in mind:

  - All domain modules extend `BlueFolderBase`, which includes:
  - **Input validation** for filters and parameters.
  - **Safe wrappers** around HTTP GET requests with consistent return types.
  - **Clear error messaging** to assist in debugging.

Example:

```python
from bluefolder_api.users import BlueFolderUsers

users_api = BlueFolderUsers()

try:
    users = users_api.get(filters={"status": "Active"})
except RuntimeError as e:
    print(f"API Error: {e}")
```

## 📂 Modules

| Module            | Class Name                 | Description                                 |
|-------------------|----------------------------|---------------------------------------------|
| `base.py`         | `BlueFolderClient`         | Core request handling and auth              |
| `appointments.py` | `BlueFolderAppointments`   | List and retrieve appointments              |
| `customers.py`    | `BlueFolderCustomers`      | Customer-related endpoints                  |
| `work_orders.py`  | `BlueFolderWorkOrders`     | Manage and view work orders                 |
| `users.py`        | `BlueFolderUsers`          | Access users and technicians                |
| `equipment.py`    | `BlueFolderEquipment`      | Query and update equipment records          |
| `tasks.py`        | `BlueFolderTasks`          | List and manage tasks                       |

## 🔑 Environment Variables

Create a `.env` file in the root directory:

```env
BLUEFOLDER_API_KEY=your_api_key_here
BLUEFOLDER_ACCOUNT_NAME=your_account_subdomain_here
```

## 🧪 Testing

Example test files can be added under `tests/` directory using `pytest` or `unittest`.

## 📄 License

MIT License.
