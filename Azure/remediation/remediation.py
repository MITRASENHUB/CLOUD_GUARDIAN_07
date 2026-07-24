import subprocess
import logging

from config import (
    RESOURCE_GROUP,
    STORAGE_ACCOUNT,
    SAFE_REMEDIATIONS,
    HIGH_RISK_REMEDIATIONS
)


def validate_request(mc_id):
    """
    Returns True if the remediation is safe for automatic execution.
    """
    return mc_id in SAFE_REMEDIATIONS


def approval_required(mc_id):
    """
    Returns True if manual approval is required.
    """
    return mc_id in HIGH_RISK_REMEDIATIONS


def execute_az_command(cmd):
    """
    Executes an Azure CLI command and returns the result.
    """
    logging.info("Executing: %s", " ".join(cmd))

    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True
    )

    if result.returncode == 0:
        logging.info("Remediation successful.")
        return True, result.stdout

    logging.error(result.stderr)
    return False, result.stderr


def remediate_mc01():
    """
    MC-01
    Disable Public Network Access
    """

    cmd = [
        r"C:\Program Files\Microsoft SDKs\Azure\CLI2\wbin\az.cmd",
        "storage",
        "account",
        "update",
        "--name", STORAGE_ACCOUNT,
        "--resource-group", RESOURCE_GROUP,
        "--public-network-access", "Disabled"
    ]

    success, message = execute_az_command(cmd)

    if success:
        return "Public Network Access successfully disabled."

    return f"MC-01 failed: {message}"


def remediate_mc02():
    """
    MC-02
    Disable Blob Public Access
    """

    cmd = [
        r"C:\Program Files\Microsoft SDKs\Azure\CLI2\wbin\az.cmd",
        "storage",
        "account",
        "update",
        "--name", STORAGE_ACCOUNT,
        "--resource-group", RESOURCE_GROUP,
        "--allow-blob-public-access", "false"
    ]

    success, message = execute_az_command(cmd)

    if success:
        return "Blob Public Access successfully disabled."

    return f"MC-02 failed: {message}"


def remediate_mc11():
    """
    MC-11
    Enforce TLS 1.2
    """

    cmd = [
        r"C:\Program Files\Microsoft SDKs\Azure\CLI2\wbin\az.cmd",
        "storage",
        "account",
        "update",
        "--name", STORAGE_ACCOUNT,
        "--resource-group", RESOURCE_GROUP,
        "--min-tls-version", "TLS1_2"
    ]

    success, message = execute_az_command(cmd)

    if success:
        return "Minimum TLS version successfully updated to TLS1_2."

    return f"MC-11 failed: {message}"
