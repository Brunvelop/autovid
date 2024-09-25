import pulumi
from pulumi import automation as auto
import os

def run_pulumi(program_path):
    os.environ["PULUMI_CONFIG_PASSPHRASE"] = ""
    # Configura el stack de Pulumi
    stack = auto.create_or_select_stack(
        stack_name="autovid",
        work_dir="/home/user/Desktop/autovid/infra/image_generator_API",
        program=program_path
    )

    # Ejecuta el programa Pulumi
    # up_result = stack.destroy(on_output=print)
    up_result = stack.up(on_output=print)
    
    # Imprime los resultados
    print(f"Update summary: \n{up_result.summary.result}")
    print("Outputs:")
    for key, value in up_result.outputs.items():
        print(f"{key}: {value.value}")

if __name__ == "__main__":
    # Puedes cambiar esto a la ruta de tu archivo de infraestructura
    infrastructure_file = "home/user/Desktop/autovid/infra/image_generator_API/flux.py"
    run_pulumi(infrastructure_file)