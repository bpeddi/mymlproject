from aws_cdk import (
    aws_ec2 as ec2,
    App,
    Stack,
    Environment,
    CfnOutput
)
from constructs import Construct

class MyInfraStack(Stack):


    def __init__(self, scope: Construct, id: str, env:Environment, **kwargs ) -> None:
        super().__init__(scope, id, env=env, **kwargs)

        # Use the default VPC
        vpc = ec2.Vpc.from_lookup(self, 'DefaultVpc', is_default=True)

        # Use the default subnets
        subnets = ec2.SubnetSelection(subnet_type=ec2.SubnetType.PUBLIC)
    # Create a security group for EC2 instance
        sg = ec2.SecurityGroup(self, "MySecurityGroup",
            vpc=vpc,
            description="Allow inbound HTTP traffic",
            allow_all_outbound=True
        )
        sg.add_ingress_rule(ec2.Peer.any_ipv4(), ec2.Port.tcp(80), "Allow HTTP access")

        # Launch an EC2 instance
        instance = ec2.Instance(self, "MyInstance",
            instance_type=ec2.InstanceType.of(ec2.InstanceClass.BURSTABLE2, ec2.InstanceSize.MICRO),
            machine_image=ec2.AmazonLinuxImage(generation=ec2.AmazonLinuxGeneration.AMAZON_LINUX_2),
            vpc=vpc,
            security_group=sg,
            vpc_subnets=ec2.SubnetSelection(subnet_type=ec2.SubnetType.PUBLIC)
        )

        # Install Apache HTTP server and deploy website
        instance.user_data.add_commands("yum install -y httpd", "systemctl start httpd")
        instance.connections.allow_from_any_ipv4(ec2.Port.tcp(80), "Allow inbound HTTP traffic")

        # Output the public IP address of the instance
        CfnOutput(self, "PublicIPAddress",
            value=instance.instance_public_ip,
            description="Public IP Address of the EC2 instance"
        )



env_USA = Environment(
    account="594801937661",
    region="us-east-1"
)

app = App()
MyInfraStack(app, 'MyInfraStack', env=env_USA)
app.synth()
