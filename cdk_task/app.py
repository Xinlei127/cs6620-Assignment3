#!/usr/bin/env python3
import os

import aws_cdk as cdk

from cdk_task.first_stack import FirstStack
from cdk_task.second_stack import SecondStack

app = cdk.App()
first_stack = FirstStack(app, "FirstStack",
                         env=cdk.Environment(account=os.getenv('CDK_DEFAULT_ACCOUNT'),
                                             region=os.getenv('CDK_DEFAULT_REGION')))
SecondStack(app, "SecondStack",
            first_stack,
            env=cdk.Environment(account=os.getenv('CDK_DEFAULT_ACCOUNT'),
                                region=os.getenv('CDK_DEFAULT_REGION')))
app.synth()
