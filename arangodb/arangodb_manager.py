import docker
import os

class ArangoDBManager:
    def __init__(self):
        self.client = docker.from_env()
        self.container_name = "arango-autovid"
        self.image_name = "arangodb-custom"
        self.port = 8529
        self.password = "password123"
        self.data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "arangodb_data")

    def is_container_running(self):
        try:
            container = self.client.containers.get(self.container_name)
            return container.status == "running"
        except docker.errors.NotFound:
            return False

    def start_container(self):
        if not self.is_container_running():
            if not os.path.exists(self.data_dir):
                os.makedirs(self.data_dir)
            
            self.client.containers.run(
                self.image_name,
                name=self.container_name,
                detach=True,
                environment={"ARANGO_ROOT_PASSWORD": self.password},
                ports={f"{self.port}/tcp": self.port},
                volumes={self.data_dir: {"bind": "/var/lib/arangodb3", "mode": "rw"}},
            )
            print(f"ArangoDB container started. Data directory: {self.data_dir}")
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
