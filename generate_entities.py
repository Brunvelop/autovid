# # Add the project root to the Python path
# sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from unidecode import unidecode

from generators.LLM import LLM, Models
from arangodb.arangodb_client import connect_to_arangodb, create_collection, insert_document, create_relationship
from arangodb.entities_relationships import RelationshipType, Being

def generate_beings_and_relationships(llm):
    prompt = """
    Genera una lista de 5 dioses griegos como entidades Being. Para cada dios, proporciona:
    1. Nombre
    2. Descripcion (breve descripcion)
    2. Raza (por ejemplo, "Dios", "Titán", etc.)
    3. Descripción física
    4. Poderes (lista de al menos 3 poderes)
    5. Género
    6. Símbolos (lista de al menos 2 símbolos asociados)
    7. Relaciones con otros dioses

    Las relaciones deben ser SOLO de los siguientes tipos:
    - FATHER_OF (padre de)
    - MOTHER_OF (madre de)
    - BROTHER_OF (hermano de)
    - CHILD_OF (hijo/a de)

    Formatea la salida como una lista de diccionarios en Python, así:
    [
        {
            "name": "Zeus",
            "description": "Zeus es el dios del cielo y del trueno, el más importante de los dioses olímpicos."
            "race": "Dios",
            "physical_description": "Hombre barbudo y musculoso con cabello largo y blanco",
            "powers": ["Control del rayo", "Metamorfosis", "Control del clima"],
            "gender": "Masculino",
            "symbols": ["Rayo", "Águila", "Roble"],
            "relationships": [
                {"type": "FATHER_OF", "target": "Atenea"},
                {"type": "FATHER_OF", "target": "Apolo"},
                {"type": "BROTHER_OF", "target": "Poseidón"}
            ]
        },
        # Más dioses...
    ]
    """
    
    system_prompt = "Eres un asistente con amplio conocimiento de la mitología griega."
    
    response = llm.generate_text(prompt, system_prompt)
    if response:
        # Limpiamos la respuesta
        cleaned_response = response['text'].strip('`').strip()
        if cleaned_response.startswith('python\n'):
            cleaned_response = cleaned_response[7:]
        # Evaluamos la respuesta limpia
        return eval(cleaned_response)

def validate_being(being):
    required_fields = ['name', 'race', 'physical_description', 'powers', 'gender', 'symbols', 'relationships']
    for field in required_fields:
        if field not in being:
            raise ValueError(f"Campo requerido '{field}' falta en el Being")
    
    if not isinstance(being['powers'], list) or len(being['powers']) < 3:
        raise ValueError("'powers' debe ser una lista con al menos 3 elementos")
    
    if not isinstance(being['symbols'], list) or len(being['symbols']) < 2:
        raise ValueError("'symbols' debe ser una lista con al menos 2 elementos")
    
    valid_relationship_types = [r.name for r in RelationshipType.Being]
    for relationship in being['relationships']:
        if relationship['type'] not in valid_relationship_types:
            raise ValueError(f"Tipo de relación inválido: {relationship['type']}")

def insert_beings_and_relationships(db, beings):
    being_collection = create_collection(db, 'Beings')
    relationship_collection = create_collection(db, 'Relationships', edge=True)
    
    # First, insert all beings
    for being_data in beings:
        # Create Being object
        being = Being(
            name=being_data['name'],
            description=being_data['description'],
            race=being_data['race'],
            physical_description=being_data['physical_description'],
            powers=being_data['powers'],
            gender=being_data['gender'],
            symbols=being_data['symbols']
        )
        
        # Insert the Being
        being_doc = {
            "_key": unidecode(being.name.lower().replace(" ", "_")),
            'description': being.description,
            "name": being.name,
            "race": being.race,
            "physical_description": being.physical_description,
            "powers": being.powers,
            "gender": being.gender,
            "symbols": being.symbols
        }
        insert_document(being_collection, being_doc)
    
    # Then, insert all relationships
    for being_data in beings:
        for relationship in being_data['relationships']:
            from_id = f"Beings/{unidecode(being_data['name'].lower().replace(' ', '_'))}"
            to_id = f"Beings/{unidecode(relationship['target'].lower().replace(' ', '_'))}"
            edge_doc = {
                "_from": from_id,
                "_to": to_id,
                "type": relationship['type']
            }
            insert_document(relationship_collection, edge_doc)

def main():
    llm = LLM(model=Models.OpenAI.GPT4o)
    db = connect_to_arangodb()
    
    beings = generate_beings_and_relationships(llm)
    if beings:
        try:
            insert_beings_and_relationships(db, beings)
            print("Seres y relaciones generados e insertados exitosamente en la base de datos.")
        except ValueError as e:
            print(f"Error de validación: {str(e)}")
    else:
        print("No se pudieron generar seres y relaciones.")

if __name__ == "__main__":
    main()
