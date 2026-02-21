from dataclasses import dataclass

@dataclass(frozen=True)
class DbInfo:
    name: str
    desc: str
    category: str

@dataclass(frozen=True)
class MetadataEntry:
    series_code: str
    name_of_time_series_j: str
    name_of_time_series: str
    unit_j: str
    unit: str
    frequency: str
    category_j: str
    category: str
    layer1: int
    layer2: int
    layer3: int
    layer4: int
    layer5: int
    start_of_the_time_series: str
    end_of_the_time_series: str
    last_update: str
    notes_j: str
    notes: str

@dataclass(frozen=True)
class MetadataResponse:
    status: int
    message_id: str
    message: str
    date: str
    db: str
    result_set: tuple[MetadataEntry, ...]


