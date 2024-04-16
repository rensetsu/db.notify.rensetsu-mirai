from typing import TypedDict

class MediaTitle(TypedDict):
    """Dictionary for titles"""
    canonical: str
    """Display/Canonical title"""
    romaji: str | None
    """Romaji title"""
    english: str | None
    """English title"""
    japanese: str | None
    """Japanese title"""
    hiragana: str | None
    """Hiragana title"""
    synonyms: list[str] | None
    """Synonyms"""

class AverageColor(TypedDict):
    """Dictionary for average color"""
    hue: float
    """Hue"""
    saturation: float
    """Saturation"""
    lightness: float
    """Lightness"""


class Image(TypedDict):
    """Dictionary for image spec"""
    extension: str
    """Extension"""
    width: int
    """Width"""
    height: int
    """Height"""
    averageColor: AverageColor
    """Average color"""
    lastModified: int
    """Last modified"""


class AnimeRating(TypedDict):
    """Dictionary for ratings"""
    overall: float
    """Overall rating"""
    story: float
    """Story rating"""
    visuals: float
    """Visuals rating"""
    soundtrack: float
    """Soundtrack rating"""
    count: dict[str, int]
    """Count"""

class AnimePopularity(TypedDict):
    """Dictionary for popularity"""
    watching: int
    """Watching"""
    completed: int
    """Completed"""
    planned: int
    """Planned"""
    hold: int
    """Hold"""
    dropped: int
    """Dropped"""

class BasicMapping(TypedDict):
    """Dictionary for basic mapping"""
    service: str
    """Service Name"""
    serviceId: str
    """Service ID"""

class Links(TypedDict):
    """Dictionary for links"""
    title: str
    """Title"""
    url: str


class Anime(TypedDict):
    """Notify.moe Anime Object struct"""
    id: str
    """Base64 ID of the entry"""
    type: str | None
    """Type of the entry"""
    title: MediaTitle
    """Title"""
    summary: str | None
    """Synopsis/summary of the show"""
    status: str | None
    """Release status"""
    genres: list[str] | None
    """Genres"""
    startDate: str | None
    """Start date"""
    endDate: str | None
    """End date"""
    episodeCount: int | None
    """Episode count"""
    episodeLength: int | None
    """Episode length"""
    source: str | None
    """Source"""
    image: Image | None
    """Image"""
    firstChannel: str | None
    """First channel"""
    rating: AnimeRating | None
    """Rating"""
    popularity: AnimePopularity | None
    """Popularity"""
    trailers: list[BasicMapping] | None
    """Trailers"""
    episodes: list[str] | None
    """Episodes"""
    mappings: list[BasicMapping] | None
    """Mappings"""
    posts: list[str] | None
    """Posts"""
    likes: list[str] | None
    """Likes"""
    created: str | None
    """Created"""
    createdBy: str | None
    """Created by"""
    edited: str | None
    """Edited"""
    editedBy: str | None
    """Edited by"""
    isDraft: bool | None
    """Draft status"""
    studios: list[str] | None
    """Studios"""
    producers: list[str] | None
    """Producers"""
    licensors: list[str] | None
    """Licensors"""
    links: list[Links] | None
