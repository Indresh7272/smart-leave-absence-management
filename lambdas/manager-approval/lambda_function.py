import boto3
import uuid
from datetime import datetime, timezone, timedelta


dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table("leave_approvals")


def lambda_handler(event, context):

    approval_id = "APPR-" + str(uuid.uuid4())

    now = datetime.now(timezone.utc)
    expires_at = now + timedelta(hours=48)

    item = {
    "approval_id": approval_id,
    "request_id": event["request_id"],
    "employee_id": event["employee_id"],
    "manager_id": event["manager_id"],
    "status": "PENDING",
    "created_at": now.isoformat(),
    "expires_at": expires_at.isoformat(),
    "task_token": event["taskToken"]
    }

    table.put_item(Item=item)

    return {
        "approval_id": approval_id,
        "request_id": event["request_id"],
        "status": "PENDING_MANAGER_APPROVAL"
    }