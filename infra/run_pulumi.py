import os
from pathlib import Path
from pulumi import automation as auto

class Deployer:
    def __init__(self, verbose:bool = True, pulumi_config_passphrase:str = ''):
        self.verbose = verbose
        os.environ['PULUMI_CONFIG_PASSPHRASE'] = pulumi_config_passphrase
    
    def deploy(self, infra_path:Path):
        stack = auto.create_or_select_stack(
            stack_name=infra_path.stem,
            work_dir=str(infra_path),
        )
        up_result = stack.up(on_output=print)
        
        if self.verbose:
            print(f"Update summary: \n{up_result.summary.result}")
            print("Outputs:")
            for key, value in up_result.outputs.items():
                print(f"{key}: {value.value}")

        return up_result
    
    def destroy(self, infra_path:Path):
        stack = auto.create_or_select_stack(
            stack_name=infra_path.stem,
            work_dir=str(infra_path),
        )
        destroy_result = stack.destroy(on_output=print)

        if self.verbose:
            print(f"Destroy summary: \n{destroy_result.summary.result}")

if __name__ == '__main__':
    deployer = Deployer()
    infra_path = Path('/home/user/Desktop/autovid/infra/Flux_replicate_api')
    # deployer.deploy_path(infra_path)
    deployer.destroy(infra_path)