from aws_cdk import Stack
from aws_cdk import aws_lambda as lambda_
from aws_cdk import aws_logs as logs
from aws_cdk import aws_cloudwatch as cloudwatch
from aws_cdk import aws_cloudwatch_actions as actions
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
                                            log_group=first_stack.log_group,
                                            environment={
                                                'DEST_BUCKET_NAME': first_stack.destination_bucket.bucket_name
                                            }
                                            )
        # Grant Lambda permission to delete objects from the S3 bucket
        first_stack.destination_bucket.grant_read(cleaner_function)
        first_stack.destination_bucket.grant_delete(cleaner_function)

        # Define CloudWatch Metric based on the Metric Filter
        total_size_metric = cloudwatch.Metric(
            namespace="Custom/S3",
            metric_name="TotalSize",
            period=aws_cdk.Duration.seconds(30),
            statistic="Sum"
        )

        # Create a CloudWatch Metric Filter to monitor the log
        metric_filter = logs.MetricFilter(self, "TotalSizeMetricFilter",
                                          log_group=first_stack.log_group,
                                          metric_namespace=total_size_metric.namespace,
                                          metric_name=total_size_metric.metric_name,
                                          filter_pattern=logs.FilterPattern.exists("$.size"),
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

        # Add the cleaner as the action for the alarm
        alarm.add_alarm_action(actions.LambdaAction(cleaner_function))
