import os
from dotenv import load_dotenv

import pulumi
import pulumi_aws as aws
from pulumi_aws.ec2 import SecurityGroupIngressArgs, SecurityGroupEgressArgs

from infra_definitios import Instaces, Amis

load_dotenv()

def generate_ssh_config(public_dns: str, save_path: str = '../ssh_config') -> None:
    config_content = f"""Host PULUMI
    HostName {public_dns}
    User ubuntu
    IdentityFile /home/user/Desktop/autovid/.ssh/autovid.pem
"""
    with open(save_path, 'w') as f:
        f.write(config_content)

def get_aws_provider() -> aws.Provider:
    return aws.Provider('aws', 
        access_key=os.getenv('AWS_ACCESS_KEY_ID'),
        secret_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
        region=os.getenv('AWS_REGION')
    )

def create_security_group(
    resource_name: str,
    ingress_rules: list[SecurityGroupIngressArgs] | SecurityGroupIngressArgs | None = None,
    egress_rules: list[SecurityGroupEgressArgs] | SecurityGroupEgressArgs | None = None
) -> aws.ec2.SecurityGroup:
    if not isinstance(ingress_rules, list):
        ingress_rules = [ingress_rules] if ingress_rules else []
    if not isinstance(egress_rules, list):
        egress_rules = [egress_rules] if egress_rules else []

    return aws.ec2.SecurityGroup(
        resource_name=resource_name,
        description=f"Ingress: {', '.join([rule.description for rule in ingress_rules if rule and rule.description])}; Egress: {', '.join([rule.description for rule in egress_rules if rule and rule.description])}",
        ingress=ingress_rules,
        egress=egress_rules
    )

def create_instance(
    aws_provider: aws.Provider,
    security_group: aws.ec2.SecurityGroup,
    key_name: str,
    resource_name: str,
    instance: Instaces,
    ami: Amis,
    ebs_optimized: bool = True,
    root_block_device: dict = {'volume_size': 100, 'volume_type': 'gp3'},
    init_script: str = None
) -> aws.ec2.Instance:

    return aws.ec2.Instance(
        resource_name=resource_name,
        vpc_security_group_ids=[security_group.id],
        key_name=key_name,
        instance_type=str(instance.value),
        ami=ami.value,
        ebs_optimized=ebs_optimized,
        root_block_device=root_block_device,
        tags={'Name': resource_name},
        user_data=init_script,
        opts=pulumi.ResourceOptions(provider=aws_provider)
    )

class InitScript:
    @staticmethod
    def _install_cog() -> str:
        return """sudo curl -o /usr/local/bin/cog -L https://github.com/replicate/cog/releases/latest/download/cog_$(uname -s)_$(uname -m)
        sudo chmod +x /usr/local/bin/cog"""
    
    @staticmethod
    def _clone_repo(repo_url: str) -> str:
        name = repo_url.split('/')[-1].replace('.git', '')
        return f"""git clone {repo_url} /home/ubuntu/{name}
        cd /home/ubuntu/{name}"""
    
    @staticmethod
    def _deploy_cog(repo_url: str) -> str:
        name = repo_url.split('/')[-1].replace('.git', '')
        return f"""sudo cog build -t {name}
        sudo docker run -d -p 80:5000 --gpus all {name}"""

    @classmethod
    def create(cls, cog_repo_url: str) -> str:
        init_script = f"""#!/bin/bash
            set -euo pipefail
            echo "Starting user data script execution"
            sudo apt-get update -y
            sudo apt-get upgrade -y
            {cls._install_cog()}
            {cls._clone_repo(cog_repo_url)}
            {cls._deploy_cog(cog_repo_url)}
            echo "User data script execution completed"
        """
        # Remove spaces at the beginning and add a space at the end of each line
        lines = init_script.strip().split('\n')
        processed_lines = [line.strip() + ' ' for line in lines[:-1]] + [lines[-1].strip()]
        return '\n'.join(processed_lines)