from dataclasses import dataclass, field
from typing import List, Dict, Optional
from enum import Enum


@dataclass
class Entity:
    name: str
    description: str

@dataclass
class Being(Entity):
    race: str
    physical_description: str
    powers: List[str]
    gender: Optional[str] = None
    symbols: List[str] = field(default_factory=list)

@dataclass
class Place(Entity):
    physical_description: str
    climate: Optional[str] = None
    symbols: List[str] = field(default_factory=list)

@dataclass
class Story(Entity):
    summary: str = ""
    full_story: str = ""
    time_period: Optional[str] = None
    lessons: List[str] = field(default_factory=list)

@dataclass
class Object(Entity):
    physical_description: str
    powers: str
    origin: Optional[str] = None

@dataclass
class Community(Entity):
    type: str  # Nation, mythological group, clan, etc.
    origin: Optional[str] = None
    beliefs: List[str] = field(default_factory=list)

@dataclass
class Theme(Entity):
    cultural_interpretations: Dict[str, str] = field(default_factory=dict)

class RelationshipType():
    class Being(Enum):
        FATHER_OF = "father_of"
        MOTHER_OF = "mother_of"
        BROTHER_OF = "brother_of"
        CHILD_OF = "child_of"

@dataclass
class Relationship:
    from_id: str
    to_id: str
    type: RelationshipType

    def to_document(self):
        return {
            '_from': self.from_id,
            '_to': self.to_id,
            'type': self.type
        }

if __name__ == '__main__':
    relationship = Relationship(from_id="beings/zeus", to_id="beings/heracles", type=RelationshipType.FATHER_OF)
    doc = relationship.to_document()
    print(doc)