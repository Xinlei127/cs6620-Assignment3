from aws_cdk import Stack
from aws_cdk import aws_lambda as lambda_
from aws_cdk import aws_logs as logs
from aws_cdk import aws_sns as sns
from aws_cdk import aws_sqs as sqs
from aws_cdk import aws_sns_subscriptions as sns_subscriptions
from aws_cdk import aws_cloudwatch as cloudwatch
from aws_cdk import aws_cloudwatch_actions as actions
from aws_cdk import aws_lambda_event_sources as lambda_event_sources
import aws_cdk
from constructs import Construct


class SecondStack(Stack):

    def __init__(self, scope: Construct, id: str, first_stack, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)
        # cleaner
        cleaner_function = lambda_.Function(self, "cleaner",
                                            runtime=lambda_.Runtime.PYTHON_3_8,
                                            handler="lambda_function.lambda_handler",
                                            code=lambda_.Code.from_asset("../lambda_handler/cleaner"),
                                            environment={
                                                'DEST_BUCKET_NAME': first_stack.destination_bucket.bucket_name
                                            }
                                            )
        # Grant Lambda permission to delete objects from the S3 bucket
        first_stack.destination_bucket.grant_read(cleaner_function)
        first_stack.destination_bucket.grant_delete(cleaner_function)

        # Create an SNS topic
        topic = sns.Topic(self, "AlarmTopic")
        # Create an SQS queue
        queue = sqs.Queue(self, "AlarmQueue")
        # Subscribe the SQS queue to the SNS topic
        topic.add_subscription(sns_subscriptions.SqsSubscription(queue))

        # Grant the Lambda function permissions
        queue.grant_consume_messages(cleaner_function)
        # Set up the cleaner as a consumer of the SQS queue
        lambda_event_source = lambda_event_sources.SqsEventSource(queue)
        cleaner_function.add_event_source(lambda_event_source)

        # Define CloudWatch Metric based on the Metric Filter
        total_size_metric = cloudwatch.Metric(
            namespace="TheCustom/S3",
            metric_name="TotalSize",
            period=aws_cdk.Duration.seconds(30),
            statistic="Sum"
        )

        # Create a CloudWatch Metric Filter to monitor the log
        metric_filter = logs.MetricFilter(self, "TotalSizeMetricFilter",
                                          log_group=first_stack.log_group,
                                          metric_namespace=total_size_metric.namespace,
                                          metric_name=total_size_metric.metric_name,
                                          filter_pattern=logs.FilterPattern.string_value('$.type', '=', 'temp'),
                                          default_value=0,
                                          metric_value="$.size"
                                          )

        # Create a CloudWatch Alarm for the metric
        alarm = cloudwatch.Alarm(self, "CleanerAlarm",
                                 metric=total_size_metric,
                                 threshold=3072,
                                 evaluation_periods=1,
                                 comparison_operator=cloudwatch.ComparisonOperator.GREATER_THAN_THRESHOLD
                                 )

        # Add the topic as the action for the alarm
        alarm.add_alarm_action(actions.SnsAction(topic))
