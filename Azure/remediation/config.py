import os

# Azure Configuration
SUBSCRIPTION_ID = os.getenv("SUBSCRIPTION_ID")
RESOURCE_GROUP = os.getenv("RESOURCE_GROUP")
STORAGE_ACCOUNT = os.getenv("STORAGE_ACCOUNT")

# Safe remediation list
SAFE_REMEDIATIONS = [
    "MC-01",
    "MC-02",
    "MC-11"
]

HIGH_RISK_REMEDIATIONS = [
    "MC-03",
    "MC-04",
    "MC-05",
    "MC-06",
    "MC-07",
    "MC-08",
    "MC-09",
    "MC-10",
    "MC-12",
    "MC-13"
]
