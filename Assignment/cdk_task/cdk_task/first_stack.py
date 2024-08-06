from aws_cdk import Stack
from aws_cdk import aws_s3 as s3
from aws_cdk import aws_sns as sns
from aws_cdk import aws_lambda as lambda_
from aws_cdk import aws_logs as logs
from aws_cdk import aws_s3_notifications as s3_notifications
from aws_cdk import aws_sns_subscriptions as sns_subscriptions
import aws_cdk.aws_iam as iam
import aws_cdk
from constructs import Construct


class FirstStack(Stack):

    def __init__(self, scope: Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)
        # Define source bucket
        self.source_bucket = s3.Bucket(self, "source",
                                       removal_policy=aws_cdk.RemovalPolicy.DESTROY,
                                       auto_delete_objects=True)

        # Define destination bucket
        self.destination_bucket = s3.Bucket(self, "destination",
                                            removal_policy=aws_cdk.RemovalPolicy.DESTROY,
                                            auto_delete_objects=True)

        # Define a CloudWatch Log Group
        self.log_group = logs.LogGroup(self, "CopierLogs",
                                       removal_policy=aws_cdk.RemovalPolicy.DESTROY)

        # Create the SNS topic
        topic = sns.Topic(self, "BucketObject")
        topic.add_to_resource_policy(
            iam.PolicyStatement(
                actions=["sns:Publish"],
                resources=[topic.topic_arn],
                principals=[iam.ServicePrincipal("s3.amazonaws.com")],
                conditions={
                    "ArnLike": {
                        "aws:SourceArn": self.source_bucket.bucket_arn
                    }
                }
            )
        )

        # Configure the notifications
        self.source_bucket.add_event_notification(
            s3.EventType.OBJECT_CREATED,
            s3_notifications.SnsDestination(topic)
        )

        # copier
        copier_function = lambda_.Function(self, "copier",
                                           runtime=lambda_.Runtime.PYTHON_3_8,
                                           handler="lambda_function.lambda_handler",
                                           code=lambda_.Code.from_asset("../lambda_handler/copier"),
                                           environment={
                                               'DEST_BUCKET_NAME': self.destination_bucket.bucket_name
                                           }
                                           )

        # dumper
        dumper_function = lambda_.Function(self, "dumper",
                                           runtime=lambda_.Runtime.PYTHON_3_8,
                                           handler="lambda_function.lambda_handler",
                                           code=lambda_.Code.from_asset("../lambda_handler/dumper"),
                                           log_group=self.log_group
                                           )

        # Grant Lambda permission to read and write objects from the S3 bucket
        self.source_bucket.grant_read(copier_function)
        self.source_bucket.grant_read(dumper_function)
        self.destination_bucket.grant_write(copier_function)

        # Subscribe Lambda functions to the SNS topic
        topic.add_subscription(sns_subscriptions.LambdaSubscription(copier_function))
        topic.add_subscription(sns_subscriptions.LambdaSubscription(dumper_function))
