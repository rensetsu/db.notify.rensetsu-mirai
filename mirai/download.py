import requests as req
from alive_progress import alive_bar as abr
from consts import Status, pprint
from fake_useragent import FakeUserAgent


def download_database() -> bool:
    """Download Anime database from Notify server"""
    url = "https://notify.moe/api/types/Anime/download"
    ua = str(FakeUserAgent().random)  # type: ignore
    headers = {"User-Agent": ua}
    try:
        with req.get(url, headers=headers, stream=True) as rsp:
            rsp.raise_for_status()
            pprint.print(Status.INFO, "Downloading database")
            total_size = int(rsp.headers.get("content-length", 0))
            with open("Anime.dat", "wb") as file, abr(total_size) as bar:  # type: ignore
                for chunk in rsp.iter_content(chunk_size=1):  # type: ignore
                    file.write(chunk)
                    bar()
        pprint.print(Status.PASS, "Download complete")
        return True
    except req.exceptions.RequestException as e:
        pprint.print(Status.ERR, f"Failed to download database: {e}")
        return False
