import boto3
from decimal import Decimal

dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table("leave_balances")


def lambda_handler(event, context):

    employee_id = event["employee_id"]
    leave_type = event["leave_type"]
    start_date = event["start_date"]
    requested_days = event["total_days"]

    # Derive year from leave start date
    year = start_date[:4]

    # DynamoDB sort key
    leave_key = f"{leave_type}#{year}"

    response = table.get_item(
        Key={
            "employee_id": employee_id,
            "leave_type#year": leave_key
        }
    )

    item = response.get("Item")

    if not item:
        return {
            "balance_valid": False,
            "available_balance": 0,
            "requested_days": requested_days,
            "reason": f"No leave balance found for {leave_type} for {year}."
        }

    available_balance = Decimal(
        str(item.get("available_balance", 0))
    )

    if available_balance < Decimal(str(requested_days)):
        return {
            "balance_valid": False,
            "available_balance": float(available_balance),
            "requested_days": requested_days,
            "reason": "Insufficient leave balance."
        }

    return {
        "balance_valid": True,
        "available_balance": float(available_balance),
        "requested_days": requested_days,
        "reason": "Leave balance is sufficient."
    }