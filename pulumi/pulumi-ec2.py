"""An AWS Python Pulumi program"""

import pulumi
from pulumi_aws import ec2

instnc = ec2.Instance(
    "carmel-test",
    ami="ami-0e86e20dae9224db8",
    instance_type=ec2.InstanceType.T2.MICRO,
    tags={
        "Name": "carmel-test"
    }
)