from distutils.command.upload import upload
from aws_cdk import (
    Duration,
    Stack,
    aws_lambda as _lambda,
    aws_lambda_event_sources as lambda_event,
    aws_sqs as sqs,
    aws_sns as sns,
    aws_sns_subscriptions as sns_subs,
    aws_s3 as _s3,
    aws_s3_notifications as s3n
)
from constructs import Construct

class S3SnsSqsLambdaStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, lambda_dir: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        """
        SQS/DLQ
        """
        # dlq (queue for capturing failed events) 
        dlq = sqs.Queue(
            self,
            id="dead_letter_queue_id",
            retention_period=Duration.days(7)
        )
        dead_letter_queue = sqs.DeadLetterQueue(
            max_receive_count=1,
            queue=dlq
        )

        # sqs (upload queue)
        upload_queue = sqs.Queue(
            self,
            id="sample_queue_id",
            visibility_timeout=Duration.seconds(30),
            dead_letter_queue=dead_letter_queue
        )

        """
        SNS
        """
        # sns (subscribe sqs queue)
        sqs_subsription = sns_subs.SqsSubscription(
            queue=upload_queue,
            raw_message_delivery=True
        )

        # sns topic 
        upload_event_topic = sns.Topic(
            self, 
            id="sample_sns_topic_id"
        )

        # bind SNS topic to the SQS queue 
        upload_event_topic.add_subscription(sqs_subsription)

        """ 
        S3 bucket with lifecycle rules (cost optimization)
        """

        s3_bucket = _s3.Bucket(
            self,
            id="sample_bucket_id",
            block_public_access=_s3.BlockPublicAccess.BLOCK_ALL,
            versioned=True,
            lifecycle_rules=[
                _s3.LifecycleRule(
                    enabled=True,
                    expiration=Duration.days(365),
                    transitions=[
                        _s3.Transition(
                            storage_class=_s3.StorageClass.INFREQUENT_ACCESS,
                            transition_after=Duration.days(30)
                        ),
                        _s3.Transition(
                            storage_class=_s3.StorageClass.GLACIER,
                            transition_after=Duration.days(90)
                        )
                    ]
                )
            ]
        )

        # Note: if you do not specify a filter, all uploads will trigger an event.
        # also, modifying the event type will handle other object operations. 
        
        # Binds the s3 bucket to the sns topic 
        s3_bucket.add_event_notification(
            _s3.EventType.OBJECT_CREATED_PUT,
            s3n.SnsDestination(upload_event_topic),
            _s3.NotificationKeyFilter(prefix="uploads", suffix=".json")
        )

        function = _lambda.Function(
            self,
            id="lambda_function",
            runtime=_lambda.Runtime.PYTHON_3_8,
            handler="lambda.handler",
            code=_lambda.Code.from_asset(path=lambda_dir)
        )

        # bind lambda to the sqs queue (trigger lambda)
        invoke_event_source = lambda_event.SqsEventSource(upload_queue)
        function.add_event_source(invoke_event_source)

        