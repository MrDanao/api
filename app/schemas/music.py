from typing import Optional
from uuid import (
    UUID,
    uuid4
)

from pydantic import (
    BaseModel,
    Field
)


class MusicSha256(BaseModel):
    audio: str
    image: str


class Music(BaseModel):
    id: UUID = Field(alias='_id', default_factory=uuid4, readOnly=True)
    artist: str
    title: str
    album: str
    label: str
    year: int
    sha256: MusicSha256 = Field(alias='_sha256', default={'audio': '0', 'image': '0'}, readOnly=True)


class MusicPatch(BaseModel):
    artist: Optional[str]
    title: Optional[str]
    album: Optional[str]
    label: Optional[str]
    year: Optional[int]
