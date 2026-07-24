import azure.functions as func
import json
import logging

from remediation import (
    validate_request,
    approval_required,
    remediate_mc01,
    remediate_mc02,
    remediate_mc11
)

app = func.FunctionApp(http_auth_level=func.AuthLevel.FUNCTION)


@app.route(route="AutoRemediation", methods=["POST"])
def AutoRemediation(req: func.HttpRequest) -> func.HttpResponse:

    logging.info("CloudGuardian Auto Remediation Triggered")

    try:
        body = req.get_json()
    except ValueError:
        return func.HttpResponse(
            json.dumps({"error": "Invalid JSON"}),
            mimetype="application/json",
            status_code=400
        )

    mc_id = body.get("mc_id")

    if not mc_id:
        return func.HttpResponse(
            json.dumps({"error": "mc_id is required"}),
            mimetype="application/json",
            status_code=400
        )

    # Guardrail
    if approval_required(mc_id):

        return func.HttpResponse(
            json.dumps({

                "status": "Pending Approval",

                "mc_id": mc_id,

                "approval_required": True,

                "approver": "Cloud Administrator",

                "reason": "High-risk remediation requires manual approval."

            }),

            mimetype="application/json",

            status_code=202
        )

    if not validate_request(mc_id):

        return func.HttpResponse(
            json.dumps({

                "status": "Rejected",

                "reason": "Unknown remediation request."

            }),

            mimetype="application/json",

            status_code=400
        )

    # Safe Auto Remediation
    if mc_id == "MC-01":
        result = remediate_mc01()

    elif mc_id == "MC-02":
        result = remediate_mc02()

    elif mc_id == "MC-11":
        result = remediate_mc11()

    else:
        result = "Unsupported remediation."

    return func.HttpResponse(
        json.dumps({
            "status": "Success",
            "mc_id": mc_id,
            "message": result
        }),
        mimetype="application/json",
        status_code=200
    )
