from aws_cdk import (
    aws_ec2 as ec2,
    aws_iam as iam,
    aws_autoscaling as autoscaling,
    aws_ec2_assets as ec2_assets,
    aws_lambda as lambda_,
    aws_s3 as s3,
    aws_s3_deployment as s3_deployment,
    aws_cloudfront as cloudfront,
    core
)

class MyEC2Stack(core.Stack):

    def __init__(self, scope: core.Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # Create a VPC
        vpc = ec2.Vpc(self, "MyVpc",
            cidr="10.0.0.0/16",
            max_azs=2,
            subnet_configuration=[
                ec2.SubnetConfiguration(
                    subnet_type=ec2.SubnetType.PUBLIC,
                    name="Public",
                    cidr_mask=24
                ),
                ec2.SubnetConfiguration(
                    subnet_type=ec2.SubnetType.PRIVATE,
                    name="Private",
                    cidr_mask=24
                )
            ]
        )

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
        core.CfnOutput(self, "PublicIPAddress",
            value=instance.instance_public_ip,
            description="Public IP Address of the EC2 instance"
        )

app = core.App()

MyEC2Stack(app, "MyEC2Stack")

app.synth()
