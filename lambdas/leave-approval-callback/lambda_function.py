import boto3
import json
from datetime import datetime, timezone

dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table("leave_approvals")

sfn = boto3.client("stepfunctions")


def lambda_handler(event, context):

    request_id = event.get("request_id")
    manager_id = event.get("manager_id")
    action = event.get("action")

    # Basic validation
    if not request_id:
        return {
            "statusCode": 400,
            "body": json.dumps({
                "error": "request_id is required"
            })
        }

    if not manager_id:
        return {
            "statusCode": 400,
            "body": json.dumps({
                "error": "manager_id is required"
            })
        }

    if action not in ["APPROVE", "REJECT"]:
        return {
            "statusCode": 400,
            "body": json.dumps({
                "error": "action must be APPROVE or REJECT"
            })
        }

    # Find approval record using request_id GSI
    response = table.query(
        IndexName="request_id-index",
        KeyConditionExpression="request_id = :request_id",
        ExpressionAttributeValues={
            ":request_id": request_id
        }
    )

    items = response.get("Items", [])

    if not items:
        return {
            "statusCode": 404,
            "body": json.dumps({
                "error": "Approval request not found"
            })
        }

    approval = items[0]

    # Verify manager
    if approval.get("manager_id") != manager_id:
        return {
            "statusCode": 403,
            "body": json.dumps({
                "error": "Manager is not authorized for this request"
            })
        }

    # Prevent duplicate processing
    if approval.get("status") != "PENDING":
        return {
            "statusCode": 409,
            "body": json.dumps({
                "error": "Approval has already been processed",
                "current_status": approval.get("status")
            })
        }

    task_token = approval.get("task_token")

    if not task_token:
        return {
            "statusCode": 500,
            "body": json.dumps({
                "error": "Task token not found"
            })
        }

    # Convert action to agreed callback decision
    decision = (
        "APPROVED"
        if action == "APPROVE"
        else "REJECTED"
    )

    callback_output = {
        "decision": decision,
        "request_id": request_id,
        "employee_id": approval.get("employee_id"),
        "manager_id": manager_id
    }

    # Add rejection reason only for rejected requests
    if decision == "REJECTED":
        callback_output["reason"] = "Manager rejected the leave request"

    # Send callback to Step Functions
    try:
        sfn.send_task_success(
            taskToken=task_token,
            output=json.dumps(callback_output)
        )

    except sfn.exceptions.InvalidToken:
        return {
            "statusCode": 410,
            "body": json.dumps({
                "error": "Task token is expired or invalid"
            })
        }

    # Update approval record
    now = datetime.now(timezone.utc).isoformat()

    table.update_item(
        Key={
            "approval_id": approval["approval_id"]
        },
        UpdateExpression="SET #s = :status, updated_at = :updated_at",
        ExpressionAttributeNames={
            "#s": "status"
        },
        ExpressionAttributeValues={
            ":status": decision,
            ":updated_at": now
        }
    )

    return {
        "statusCode": 200,
        "body": json.dumps({
            "message": "Leave approval callback processed successfully",
            "request_id": request_id,
            "employee_id": approval.get("employee_id"),
            "manager_id": manager_id,
            "decision": decision
        })
    }