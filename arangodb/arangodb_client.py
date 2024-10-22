from arango import ArangoClient

def connect_to_arangodb():
    # Conectarse al cliente ArangoDB
    client = ArangoClient(hosts='http://localhost:8529')

    # Iniciar sesión como root
    db = client.db('_system', username='root', password='password123')

    # Crear una base de datos si no existe
    if not db.has_database('mydb'):
        db.create_database('mydb')

    # Conectar a la base de datos creada
    mydb = client.db('mydb', username='root', password='password123')

    return mydb

def create_collection(db, collection_name):
    # Crear una colección
    if not db.has_collection(collection_name):
        collection = db.create_collection(collection_name)
    else:
        collection = db.collection(collection_name)
    
    return collection

def insert_document(collection, document):
    # Insertar un documento
    result = collection.insert(document)
    return result

if __name__ == "__main__":
    # Ejemplo de uso
    db = connect_to_arangodb()
    mycollection = create_collection(db, 'mycollection')
    
    document = {'_key': 'doc1', 'name': 'Test Document', 'value': 123}
    result = insert_document(mycollection, document)
    
    print("Documento insertado exitosamente.")
    print(f"Documento insertado: {result}")
