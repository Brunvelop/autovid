from arango import ArangoClient

def connect_to_arangodb():
    client = ArangoClient(hosts='http://localhost:8529')
    db = client.db('_system', username='root', password='password123')
    if not db.has_database('mydb'):
        db.create_database('mydb')
    mydb = client.db('mydb', username='root', password='password123')
    return mydb

def create_collection(db, collection_name, edge=False):
    if not db.has_collection(collection_name):
        if edge:
            collection = db.create_collection(collection_name, edge=True)
        else:
            collection = db.create_collection(collection_name)
    else:
        collection = db.collection(collection_name)
    return collection

def insert_document(collection, document):
    result = collection.insert(document)
    return result

def create_relationship(db, edge_collection_name, from_id, to_id):
    edge_collection = create_collection(db, edge_collection_name, edge=True)
    edge_document = {
        '_from': from_id,
        '_to': to_id
    }
    result = edge_collection.insert(edge_document)
    return result

if __name__ == "__main__":
    # Ejemplo de uso
    db = connect_to_arangodb()
    mycollection = create_collection(db, 'mycollection')
    
    document = {'_key': 'doc1', 'name': 'Test Document', 'value': 123}
    result = insert_document(mycollection, document)
    
    print("Documento insertado exitosamente.")
    print(f"Documento insertado: {result}")
