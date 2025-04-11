import re
from copy import deepcopy
from dataclasses import asdict
from json import dump, load, loads
from typing import Any
from uuid import uuid4

from alive_progress import alive_bar
from consts import Status, pprint, Platform
from librensetsu.formatter import remove_empty_keys
from librensetsu.humanclock import translate_season
from librensetsu.models import (
    ConventionalMapping,
    Date,
    IdSlugPair,
    MediaInfo,
    PictureUrls,
    RelationMaps,
    TraktSeason,
)
from models import Anime


def process_data(text: str, data_uuid: str | None = None) -> MediaInfo:
    """
    Process the data from the text and convert it to `MediaInfo`
    :param text: Text to process
    :type text: str
    :return: `MediaInfo` object
    :rtype: MediaInfo
    """
    json: Anime = loads(text)
    nid = json["id"]

    # proc. title
    english = json["title"]["english"]
    native = json["title"]["japanese"]
    display = json["title"]["canonical"]
    transliteration = json["title"]["romaji"]
    kana = json["title"]["hiragana"]
    syns: list[str] = []
    if json["title"]["synonyms"]:
        syns = json["title"]["synonyms"]
        if kana:
            syns.append(kana)

    rdcomp = re.compile(r"(\d{4})(?:-(\d{2})(?:-(\d{2}))?)?")
    start_date = json["startDate"]
    fsdate = Date(timezone="+0000")
    if start_date:
        msdate = rdcomp.match(start_date)
        if msdate:
            fsdate.year = int(msdate.group(1))
            if msdate.group(2):
                fsdate.month = int(msdate.group(2))
            if msdate.group(3):
                fsdate.day = int(msdate.group(3))
    end_date = json["endDate"]
    fedate = Date()
    if end_date:
        medate = rdcomp.match(end_date)
        if medate:
            fedate.year = int(medate.group(1))
            if medate.group(2):
                fedate.month = int(medate.group(2))
            if medate.group(3):
                fedate.day = int(medate.group(3))

    # proc. eps
    eps = json["episodeCount"] if json["episodeCount"] else 0
    mins = json["episodeLength"] if json["episodeLength"] else 0
    wasted = int(eps) * int(mins)

    # proc. image
    imgcdn = "https://media.notify.moe/images/anime/"
    finimg = None
    img = json["image"]
    if img:
        exts = img["extension"]
        modified = img["lastModified"]
        finimg = PictureUrls(
            original=f"{imgcdn}original/{nid}{exts}?{modified}",
            large=f"{imgcdn}large/{nid}{exts}?{modified}",
            medium=f"{imgcdn}medium/{nid}{exts}?{modified}",
            small=f"{imgcdn}small/{nid}{exts}?{modified}",
        )

    # proc. mappings
    fmaps = RelationMaps(notify=nid)
    mappings = json["mappings"]
    if mappings:
        media_type = json["type"] if json["type"] else None
        if media_type != "movie":
            media_type = "show"
        media_type = f"{media_type}s"
        for mapping in mappings:
            serv = mapping["service"]
            mid = mapping["serviceId"]
            match serv:
                case "anidb/anime":
                    fmaps.anidb = int(mid.replace("a", ""))
                case "":
                    pprint.print(Status.WARN, f"Found a stub service info, guessing as AniDB instead for {mid} on {nid}", platform=Platform.ANIDB)
                    fmaps.anidb = int(mid.replace("a", ""))
                case "shoboi/anime":
                    fmaps.syoboical = int(mid)
                case "anilist/anime":
                    fmaps.anilist = int(mid)
                case "myanimelist/anime":
                    fmaps.myanimelist = int(re.sub(r"\D", "", mid))
                case "kitsu/anime":
                    try:
                        fmaps.kitsu = IdSlugPair(id=int(mid))
                    except Exception as err:
                        pprint.print(Status.ERR, f"{mid} is not Kitsu ID on {nid}", platform=Platform.KITSU)
                case "trakt/anime":
                    fmaps.trakt = ConventionalMapping(
                        id=int(mid),
                        media_type=media_type,  # type: ignore
                    )
                case "trakt/season":
                    pprint.print(Status.INFO, f"This entry ({nid}) uses unique Trakt season ID ({mid}) instead!", platform=Platform.TRAKT)
                    fmaps.trakt = TraktSeason(
                        id=int(mid),
                        media_type="seasons"
                    )
                case "tvdb/anime":
                    fmaps.tvdb = ConventionalMapping(
                        id=int(mid),
                        media_type=media_type,  # type: ignore
                    )
                case "thetvdb/anime":
                    splitter = mid.split('/')
                    season = None
                    if len(splitter) == 2:
                        season = int(splitter[1])
                    fmaps.tvdb = ConventionalMapping(
                        id=int(splitter[0]),
                        season=season,
                        media_type=media_type,  # type: ignore
                    )
                case "imdb/anime":
                    fmaps.imdb = ConventionalMapping(
                        id=mid,
                        media_type=media_type,  # type: ignore
                    )
                case _:
                    pprint.print(Status.INFO, f"Entry from {serv} was skipped. Mapping info: {mapping}")

    try:
        season = translate_season(fsdate)
    except ValueError:
        season = None

    return MediaInfo(
        uuid=data_uuid or str(uuid4()),
        title_display=display,
        title_transliteration=transliteration,
        title_native=native,
        title_english=english,
        synonyms=syns,
        is_adult=None,
        media_type="anime",
        media_sub_type=json["type"],
        year=fsdate.year,
        start_date=fsdate,
        end_date=fedate,
        unit_order=None,
        unit_counts=eps,
        subunit_order=mins,
        subunit_counts=wasted,
        volume_order=None,
        volume_counts=None,
        season=season,
        picture_urls=[finimg] if finimg else [],
        country_of_origin=None,
        mappings=fmaps,
        source_data="notify",
    )


def do_loop() -> list[MediaInfo]:
    """
    Loops all the object to convert as a list of MediaInfo
    :return: List of `MediaInfo`
    :rtype: MediaInfo
    """
    # Grab JSON on even lines
    try:
        with open("notify.json", "r") as file:
            old_data: list[dict[str, Any]] = load(file)
    except FileNotFoundError:
        old_data = []
    loi = len(old_data)
    new_info: list[MediaInfo] = []
    pprint.print(Status.INFO, "Processing data...")
    with open("Anime.dat", "r") as file:
        lines = file.readlines()
        media_id = ""
        with alive_bar(len(lines)) as bar:  # type: ignore
            for i, line in enumerate(lines):
                bar()
                data_uuid: str | None = None  # type: ignore
                if i % 2 == 0:
                    media_id = line.strip()
                else:
                    if loi > 0:
                        for data in old_data:
                            if data["mappings"]["notify"] == media_id:
                                data_uuid = data["uuid"]
                                break
                    new_info.append(process_data(line, data_uuid))
    pprint.print(Status.PASS, "Data processed.")
    pprint.print(Status.INFO, "Completed loop, converting dataclasses to dict")
    new_info = [asdict(info) for info in new_info]  # type: ignore
    # sort by notify id
    pprint.print(Status.INFO, "Sorting by Notify ID")
    new_info.sort(key=lambda x: x["mappings"]["notify"])  # type: ignore
    pprint.print(Status.INFO, "Dumping to notify.json")
    with open("notify.json", "w") as f:
        dump(new_info, f, ensure_ascii=False)
    # remove all keys that the value is either None, empty list, or empty dict, recursively
    pprint.print(Status.INFO, "Creating notify_min.json")
    mininfo = deepcopy(new_info)
    mininfo = remove_empty_keys(mininfo)
    pprint.print(Status.INFO, "Dumping to notify_min.json")
    with open("notify_min.json", "w") as f:
        dump(mininfo, f, ensure_ascii=False)
    return new_info
