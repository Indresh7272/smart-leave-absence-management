import boto3
from datetime import datetime


dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table("leave_requests")


def lambda_handler(event, context):

    employee_id = event["employee_id"]
    requested_start = datetime.strptime(
        event["start_date"], "%Y-%m-%d"
    )
    requested_end = datetime.strptime(
        event["end_date"], "%Y-%m-%d"
    )

    response = table.query(
        KeyConditionExpression=boto3.dynamodb.conditions.Key(
            "employee_id"
        ).eq(employee_id)
    )

    existing_requests = response.get("Items", [])

    for request in existing_requests:

        # Only approved leaves should block new requests
        if request.get("status") != "APPROVED":
            continue

        existing_start = datetime.strptime(
            request["start_date"], "%Y-%m-%d"
        )

        existing_end = datetime.strptime(
            request["end_date"], "%Y-%m-%d"
        )

        # Check date overlap
        if (
            existing_start <= requested_end
            and existing_end >= requested_start
        ):
            return {
                "overlap": True,
                "reason": "OVERLAPPING_APPROVED_LEAVE",
                "overlapping_request_id": request.get(
                    "request_id"
                )
            }

    return {
        "overlap": False,
        "reason": "NO_OVERLAPPING_APPROVED_LEAVE"
    }