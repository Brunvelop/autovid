import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pulumi

import pulumi_utils
from infra_definitios import Connections, Instaces, Amis

server = pulumi_utils.create_instance(
    resource_name='image_generator_api',
    aws_provider=pulumi_utils.get_aws_provider(),
    security_group=pulumi_utils.create_security_group(
        resource_name='web-secgrp',
        ingress_rules=[
            Connections.Ingress.SSH,
            Connections.Ingress.HTTP,
            Connections.Ingress.HTTPS,
        ],
        egress_rules=Connections.Egress.ALL
    ),
    key_name='autovid',
    instance=Instaces.G6E_XLARGE,
    ami=Amis.UBUNTU_20_04_Nvidia_PyTorch_2_3,
    root_block_device={'volume_size': 100, 'volume_type': 'gp3'},
    init_script=pulumi_utils.InitScript.create(
        cog_repo_url='https://github.com/replicate/cog-flux-schnell'
    )
)

pulumi.export('public_ip', server.public_ip)
pulumi.export('public_dns', server.public_dns)
pulumi.export('ssh_config', server.public_dns.apply(
    lambda dns: pulumi_utils.generate_ssh_config(
        public_dns=dns,
        save_path='/home/user/Desktop/autovid/infra/ssh_config'
    )
))