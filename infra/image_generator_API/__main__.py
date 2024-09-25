import os
from dotenv import load_dotenv


load_dotenv()

import pulumi
import pulumi_aws as aws

# Configurar el proveedor de AWS utilizando las credenciales cargadas
aws_provider = aws.Provider('aws', 
    access_key=os.getenv('AWS_ACCESS_KEY_ID'),
    secret_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
    region=os.getenv('AWS_REGION')
)

# Define un nuevo grupo de seguridad que permite SSH, HTTP, HTTPS y Gradio
security_group = aws.ec2.SecurityGroup('web-secgrp',
    description='Enable SSH, HTTP, HTTPS, and Gradio access',
    ingress=[
        aws.ec2.SecurityGroupIngressArgs(
            protocol='tcp',
            from_port=22,
            to_port=22,
            cidr_blocks=['0.0.0.0/0'],
            description='SSH'
        ),
        aws.ec2.SecurityGroupIngressArgs(
            protocol='tcp',
            from_port=80,
            to_port=80,
            cidr_blocks=['0.0.0.0/0'],
            description='HTTP'
        ),
        aws.ec2.SecurityGroupIngressArgs(
            protocol='tcp',
            from_port=443,
            to_port=443,
            cidr_blocks=['0.0.0.0/0'],
            description='HTTPS'
        ),
        aws.ec2.SecurityGroupIngressArgs(
            protocol='tcp',
            from_port=7860,
            to_port=7860,
            cidr_blocks=['0.0.0.0/0'],
            description='Gradio'
        ),
    ],
    egress=[
        aws.ec2.SecurityGroupEgressArgs(
            protocol='-1',
            from_port=0,
            to_port=0,
            cidr_blocks=['0.0.0.0/0'],
            description='Allow all outbound traffic'
        ),
    ],
    opts=pulumi.ResourceOptions(provider=aws_provider)
)

# Define el script de user_data
user_data_script = """#!/bin/bash 
exec > >(tee /var/log/user-data.log|logger -t user-data -s 2>/dev/console) 2>&1 
echo "Starting user data script execution" 
sudo apt-get update -y 
sudo apt-get upgrade -y 
sudo curl -o /usr/local/bin/cog -L https://github.com/replicate/cog/releases/latest/download/cog_`uname -s`_`uname -m` 
sudo chmod +x /usr/local/bin/cog 
git clone https://github.com/replicate/cog-flux-schnell 
cd cog-flux-schnell 
sudo docker run -d -p 80:5000 --gpus all cog-flux-schnell 
echo "User data script execution completed" 
"""

# Creamos la instancia EC2 con el par de claves especificado
server = aws.ec2.Instance('image_generator_API',
    instance_type='g6e.xlarge',
    vpc_security_group_ids=[security_group.id],
    ami='ami-05c3e698bd0cffe7e',
    key_name='autovid',
    ebs_optimized=True,
    root_block_device={
        'volume_size': 100,  #GB
        'volume_type': 'gp3',
    },
    tags={
        "Name": "image_generator_API"
    },
    user_data=user_data_script,
    opts=pulumi.ResourceOptions(provider=aws_provider)
)

# Exportamos la dirección pública de la instancia
pulumi.export('public_ip', server.public_ip)
pulumi.export('public_dns', server.public_dns)

# Generamos el archivo de configuración SSH
def generate_ssh_config(public_dns):
    config_content = f"""Host PULUMI
    HostName {public_dns}
    User ubuntu
    IdentityFile /home/user/Desktop/autovid/.ssh/autovid.pem
"""
    with open('../ssh_config', 'w') as f:
        f.write(config_content)

# Llamamos a la función para generar el archivo de configuración SSH
pulumi.export('ssh_config', server.public_dns.apply(generate_ssh_config))
