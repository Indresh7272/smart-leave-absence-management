# DynamoDB Schema

The Smart Leave & Absence Management System uses DynamoDB for storing leave requests, leave balances, leave configuration, and manager approval workflow information.

## 1. leave_requests

Stores employee leave requests and their approval status.

### Primary Key

| Key | Attribute |
|---|---|
| Partition Key | `employee_id` |
| Sort Key | `request_id` |

### Attributes

- `employee_id`
- `request_id`
- `manager_id`
- `leave_type`
- `start_date`
- `end_date`
- `total_days`
- `reason`
- `status`

### Status Values

- `PENDING`
- `APPROVED`
- `REJECTED`

---

## 2. leave_balances

Stores the available leave balance for each employee and leave type/year.

### Primary Key

| Key | Attribute |
|---|---|
| Partition Key | `employee_id` |
| Sort Key | `leave_type#year` |

### Attributes

- `employee_id`
- `leave_type#year`
- `available_balance`
- `used_balance`

The sort key follows the format:

`<leave_type>#<year>`

Example:

`CASUAL#2026`

---

## 3. leave_config

Stores configuration associated with each leave type.

### Primary Key

| Key | Attribute |
|---|---|
| Partition Key | `leave_type` |
| Sort Key | None |

The table can contain leave-type-specific quota and configuration values.

---

## 4. leave_approvals

Stores manager approval information and the Step Functions task token.

### Primary Key

| Key | Attribute |
|---|---|
| Partition Key | `approval_id` |
| Sort Key | None |

### Attributes

- `approval_id`
- `request_id`
- `employee_id`
- `manager_id`
- `status`
- `created_at`
- `expires_at`
- `updated_at`
- `task_token`

### Status Values

- `PENDING`
- `APPROVED`
- `REJECTED`

### Global Secondary Index

**Index name:** `request_id-index`

| Key | Attribute |
|---|---|
| Partition Key | `request_id` |
| Sort Key | None |

This index allows the callback Lambda to locate an approval record using the leave `request_id` and retrieve the associated server-side Step Functions task token.

### Security Note

The Step Functions task token is stored server-side in DynamoDB. Actual task-token values must never be committed to the GitHub repository or exposed through approval URLs.

---

## Relationship Overview

```text
leave_requests
      |
      | request_id
      ↓
leave_approvals
      |
      | task_token
      ↓
Step Functions execution

employee_id
      |
      ├── leave_requests
      └── leave_balances

leave_type
      |
      ├── leave_balances
      └── leave_config