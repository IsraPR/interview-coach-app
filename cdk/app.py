#!/usr/bin/env python3
import os
import aws_cdk as cdk
from stacks.api_stack import ApiStack

app = cdk.App()
ApiStack(
    app,
    "AiApiProductionStack",
    env=cdk.Environment(
        # Configure your AWS account and region here
        # It's best practice to get these from environment variables or CDK context
        account=os.environ["CDK_DEFAULT_ACCOUNT"],
        region=os.environ["CDK_DEFAULT_REGION"],
    ),
)
app.synth()
