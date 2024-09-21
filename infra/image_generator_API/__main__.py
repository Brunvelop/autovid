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

# Define un nuevo grupo de seguridad que permite SSH
security_group = aws.ec2.SecurityGroup('web-secgrp',
    description='Enable SSH access',
    ingress=[
        aws.ec2.SecurityGroupIngressArgs(
            protocol='tcp',
            from_port=22,
            to_port=22,
            cidr_blocks=['0.0.0.0/0'],
        ),
    ],
    opts=pulumi.ResourceOptions(provider=aws_provider)
)

# Creamos la instancia EC2 con el par de claves especificado
server = aws.ec2.Instance('pulumi-test',
    instance_type='t2.micro',
    vpc_security_group_ids=[security_group.id],
    ami='ami-0e86e20dae9224db8',
    key_name='autovid',
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
    with open('../.ssh/config', 'w') as f:
        f.write(config_content)

# Llamamos a la función para generar el archivo de configuración SSH
pulumi.export('ssh_config', server.public_dns.apply(generate_ssh_config))
