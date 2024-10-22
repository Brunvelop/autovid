# AutoVid Project

https://drive.google.com/file/d/1f-ouxQCkqbmONIUNdAnq0MYBJTxG8Yh1/view?usp=sharing

pip3 install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121

## ArangoDB Integration

This project includes integration with ArangoDB, a multi-model database. Follow these instructions to set up and use ArangoDB within the project.

### Prerequisites

- Docker installed and configured to work with WSL2 (for Windows users)
- Python 3.x
- pip (Python package manager)

### Setting up ArangoDB

1. Install the required Python packages:
   ```
   pip install python-arango docker
   ```

2. Build the ArangoDB Docker image:
   ```
   cd arangodb
   docker build -t arangodb-custom .
   ```

3. Use the `arangodb_manager.py` script to manage the ArangoDB container:
   ```
   python arangodb/arangodb_manager.py
   ```
   This script provides options to:
   - Start the ArangoDB container
   - Stop the ArangoDB container
   - Ensure the ArangoDB container is running

   The script automatically handles data persistence by mounting a volume.

### Using the ArangoDB Manager

The `arangodb_manager.py` script simplifies the process of managing the ArangoDB container. Here's how to use it:

1. To start the container:
   ```
   python arangodb/arangodb_manager.py
   ```
   Then select option 1.

2. To stop the container:
   ```
   python arangodb/arangodb_manager.py
   ```
   Then select option 2.

3. To ensure the container is running (starts it if not already running):
   ```
   python arangodb/arangodb_manager.py
   ```
   Then select option 3.

### Interacting with ArangoDB

Use the `arangodb_client.py` script to interact with ArangoDB:

```
python arangodb/arangodb_client.py
```

This script demonstrates how to connect to ArangoDB, create a database and collection, and insert a document.

### Accessing the ArangoDB Web Interface

You can access the ArangoDB web interface by navigating to `http://localhost:8529` in your web browser. Use the following credentials:
- Username: root
- Password: password123 (as set in the Dockerfile)

## Note

Remember to secure your ArangoDB instance properly in a production environment. The current setup is for development purposes only.
