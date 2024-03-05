from aws_cdk import (
  # Duration, 
  Duration,
  Stack,
  aws_ec2 as ec2,
  aws_iam as iam
)

from constructs import Construct

class Ec2ApacheStack(Stack):

  def __init__(self, scope: Construct, id: str, **kwargs) -> None:
    super().__init__(scope, id, **kwargs)

    # Create an IAM role for the EC2 instance
    instance_role = iam.Role(self, "InstanceRole", assumed_by=iam.ServicePrincipal("ec2.amazonaws.com"))

    # Create a security group
    sg = ec2.SecurityGroup(self, "SecurityGroup",
      vpc=vpc,
      allow_all_outbound=True
    )
    sg.add_ingress_rule(ec2.Peer.any_ipv4(), ec2.Port.tcp(80), "Allow HTTP")

    # Launch an EC2 instance
    instance = ec2.Instance(self, "Ec2Instance",
      instance_type=ec2.InstanceType("t2.micro"),
      machine_image=ec2.AmazonLinuxImage(),
      role=instance_role,
      security_group=sg
    )

    # User data script to install and configure Apache
    user_data = ec2.UserData.for_linux()
    user_data.add_commands("yum install -y httpd")
    user_data.add_commands("echo 'Hello, World!' > /var/www/html/index.html") 
    user_data.add_commands("systemctl start httpd")

    instance.user_data = user_data
