# smart-leave-absence-management
Smart Leave &amp; Absence Management System using AWS Step Functions, Lambda, DynamoDB, API Gateway, SNS and SES.

# Smart Leave & Absence Management System

An AWS-based Smart Leave & Absence Management System that automates employee leave validation, balance checking, overlap detection, manager approval, and approval workflow orchestration.

## Project Overview

The system automates the leave approval process using AWS serverless services.

When an employee submits a leave request, the system:

1. Validates the leave request.
2. Checks the employee's available leave balance.
3. Detects overlapping approved leaves.
4. Sends valid requests for manager approval.
5. Waits for the manager's decision using AWS Step Functions `waitForTaskToken`.
6. Resumes the workflow through a task-token callback.
7. Routes the request to the APPROVED or REJECTED path.
8. Handles manager inaction using a 48-hour timeout.

## Architecture

```text
Employee
   |
   v
API Gateway
   |
   v
Backend / Lambda
   |
   +----> DynamoDB
   |
   +----> SNS / SES Notifications
   |
   v
AWS Step Functions
   |
   +--> Validate Leave
   |
   +--> Check Balance
   |
   +--> Check Overlap
   |
   +--> Manager Approval
           |
           | waitForTaskToken
           v
      Manager Approval
           |
           v
      Callback
           |
           v
      Manager Decision
        /          \
       /            \
 APPROVED          REJECTED
    |                  |
    v                  v
Leave Approved    Leave Rejected