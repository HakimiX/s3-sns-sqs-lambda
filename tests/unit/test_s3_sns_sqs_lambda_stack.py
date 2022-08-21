import aws_cdk as core
import aws_cdk.assertions as assertions

from s3_sns_sqs_lambda.s3_sns_sqs_lambda_stack import S3SnsSqsLambdaStack

# example tests. To run these tests, uncomment this file along with the example
# resource in s3_sns_sqs_lambda/s3_sns_sqs_lambda_stack.py
def test_sqs_queue_created():
    app = core.App()
    stack = S3SnsSqsLambdaStack(app, "s3-sns-sqs-lambda")
    template = assertions.Template.from_stack(stack)

#     template.has_resource_properties("AWS::SQS::Queue", {
#         "VisibilityTimeout": 300
#     })
