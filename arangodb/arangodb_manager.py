import docker
from pathlib import Path
#sudo systemctl start docker
#sudo systemctl status docker

class ArangoDBManager:
    def __init__(self):
        self.client = docker.from_env()
        self.container_name = "arango-autovid"
        self.image_name = "arangodb-custom"
        self.port = 8529
        self.password = "password123"
        self.data_dir = Path("arangodb/arangodb_data")
        self.dockerfile_path = Path("arangodb")

    def is_container_running(self):
        try:
            container = self.client.containers.get(self.container_name)
            return container.status == "running"
        except docker.errors.NotFound:
            return False

    def build_image(self):
        try:
            print("Building custom ArangoDB image...")
            self.client.images.build(
                path=self.dockerfile_path,
                tag=self.image_name,
                dockerfile="Dockerfile"
            )
            print("Custom ArangoDB image built successfully.")
        except docker.errors.BuildError as e:
            print(f"Error building custom ArangoDB image: {str(e)}")
            raise

    def start_container(self):
        if not self.is_container_running():
            if not self.data_dir.exists():
                self.data_dir.mkdir(parents=True, exist_ok=True)
            
            try:
                self.build_image()  # Build the custom image before running
                self.client.containers.run(
                    self.image_name,
                    name=self.container_name,
                    detach=True,
                    environment={"ARANGO_ROOT_PASSWORD": self.password},
                    ports={f"{self.port}/tcp": self.port},
                    volumes={self.data_dir: {"bind": "/var/lib/arangodb3", "mode": "rw"}},
                )
                print(f"ArangoDB container started. Data directory: {self.data_dir}")
            except docker.errors.APIError as e:
                print(f"Error starting ArangoDB container: {str(e)}")
        else:
            print("ArangoDB container is already running.")

    def stop_container(self):
        try:
            container = self.client.containers.get(self.container_name)
            container.stop()
            print("ArangoDB container stopped.")
        except docker.errors.NotFound:
            print("ArangoDB container is not running.")

    def ensure_container_running(self):
        if not self.is_container_running():
            self.start_container()
        else:
            print("ArangoDB container is already running.")

if __name__ == "__main__":
    manager = ArangoDBManager()
    
    print("1. Start ArangoDB container")
    print("2. Stop ArangoDB container")
    print("3. Ensure ArangoDB container is running")
    choice = input("Enter your choice (1/2/3): ")
    
    if choice == "1":
        manager.start_container()
    elif choice == "2":
        manager.stop_container()
    elif choice == "3":
        manager.ensure_container_running()
    else:
        print("Invalid choice.")
