from enum import Enum

import pulumi_aws as aws

class Connections():
    class Ingress():
        SSH = aws.ec2.SecurityGroupIngressArgs(
                protocol='tcp',
                from_port=22,
                to_port=22,
                cidr_blocks=['0.0.0.0/0'],
                description='SSH'
        )
        HTTP = aws.ec2.SecurityGroupIngressArgs(
                protocol='tcp',
                from_port=80,
                to_port=80,
                cidr_blocks=['0.0.0.0/0'],
                description='HTTP'
        )
        HTTPS = aws.ec2.SecurityGroupIngressArgs(
                protocol='tcp',
                from_port=443,
                to_port=443,
                cidr_blocks=['0.0.0.0/0'],
                description='HTTPS'
        )
        GRADIO = aws.ec2.SecurityGroupIngressArgs(
                protocol='tcp',
                from_port=7860,
                to_port=7860,
                cidr_blocks=['0.0.0.0/0'],
                description='Gradio'
        )

    class Egress():
        ALL = aws.ec2.SecurityGroupEgressArgs(
                protocol='-1',
                from_port=0,
                to_port=0,
                cidr_blocks=['0.0.0.0/0'],
                description='Allow all outbound traffic'
        )

class Instaces(Enum):
    #https://aws.amazon.com/es/ec2/pricing/on-demand/

    #https://aws.amazon.com/es/ec2/instance-types/g6/
    G6_XLARGE = 'g6.xlarge' #24gb vram

    #https://aws.amazon.com/es/ec2/instance-types/g6e/
    G6E_XLARGE = 'g6e.xlarge' #48gb vram

class Amis(Enum):
    #Deep Learning OSS Nvidia Driver AMI GPU PyTorch 2.3 (Ubuntu 20.04)
    #https://docs.aws.amazon.com/dlami/latest/devguide/appendix-ami-release-notes.html
    UBUNTU_20_04_Nvidia_PyTorch_2_3 = 'ami-05c3e698bd0cffe7e'