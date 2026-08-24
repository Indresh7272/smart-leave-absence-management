from datetime import datetime


def lambda_handler(event, context):

    required_fields = [
        "request_id",
        "employee_id",
        "leave_type",
        "start_date",
        "end_date",
        "total_days"
    ]

    # Check required fields
    for field in required_fields:
        if field not in event:
            return {
                "valid": False,
                "reason": f"Missing required field: {field}"
            }

    # Validate dates
    try:
        start_date = datetime.strptime(
            event["start_date"], "%Y-%m-%d"
        )

        end_date = datetime.strptime(
            event["end_date"], "%Y-%m-%d"
        )

    except ValueError:
        return {
            "valid": False,
            "reason": "Invalid date format. Use YYYY-MM-DD."
        }

    # Check date order
    if start_date > end_date:
        return {
            "valid": False,
            "reason": "Start date cannot be after end date."
        }

    # Validate leave days
    try:
        total_days = int(event["total_days"])
    except (ValueError, TypeError):
        return {
            "valid": False,
            "reason": "Total days must be a valid number."
        }

    if total_days <= 0:
        return {
            "valid": False,
            "reason": "Total days must be greater than zero."
        }

    return {
        "valid": True,
        "reason": "Leave request format is valid."
    }