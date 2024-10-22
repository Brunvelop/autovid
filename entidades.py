from dataclasses import dataclass, field
from typing import List, Dict, Optional

@dataclass
class Entity:
    name: str
    description: str

@dataclass
class Being(Entity):
    race: str  # God, hero, monster, human, etc.
    physical_description: str
    powers: List[str]
    family: Dict[str, List[str]] = field(default_factory=dict)  # E.g. {"father": ["Zeus"]}
    related_stories: List[str] = field(default_factory=list)

@dataclass
class Place(Entity):
    location: str
    associated_beings: List[str] = field(default_factory=list)
    related_stories: List[str] = field(default_factory=list)

@dataclass
class Story(Entity):
    characters: List[str]
    places: List[str]
    themes: List[str]
    summary: Optional[str] = ""

@dataclass
class Object(Entity):
    owners: List[str]
    powers: List[str]
    related_stories: List[str] = field(default_factory=list)

@dataclass
class Community(Entity):
    type: str  # Nation, mythological group, clan, etc.
    member_beings: List[str] = field(default_factory=list)
    related_stories: List[str] = field(default_factory=list)

@dataclass
class Theme(Entity):
    related_stories: List[str] = field(default_factory=list)
