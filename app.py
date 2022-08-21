#!/usr/bin/env python3
import os

import aws_cdk as cdk

from s3_sns_sqs_lambda.s3_sns_sqs_lambda_stack import S3SnsSqsLambdaStack


app = cdk.App()
S3SnsSqsLambdaStack(app, "S3SnsSqsLambdaStack")
app.synth()
