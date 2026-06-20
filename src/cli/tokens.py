import json
import os

import boto3

_AWS_REGION = os.getenv("AWS_REGION", "us-east-1")


def get_config() -> dict:
    ssm = boto3.client("ssm", region_name=_AWS_REGION)
    value = ssm.get_parameter(Name="/agentcore-finance-helper/cli-config")["Parameter"][
        "Value"
    ]
    return json.loads(value)
