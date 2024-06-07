"""An app for downloading medias => photo, video, file, multi medias and files"""

import asyncio
import os
import re
from typing import (
    Tuple,
    NewType,
    Callable,
    NoReturn,
    BinaryIO,
    Iterable,
    Annotated,
)

import aiohttp
import aiofiles
from tqdm.asyncio import tqdm_asyncio
from sqlalchemy.orm import Session

from src.aiodownloader.logs import logger
from src.aiodownloader.constances import (
    BASE_DIR,
    CHUNK_SIZE,
    Qualities,
    VideoFormats,
    PhotoFormats,
)
from src.aiodownloader.exceptions import QualityError, UnAvailableLinkError
from models.app_model import UserModel, engine

HttpUrl = NewType("HttpUrl", str)
Session_ = Annotated[aiohttp.ClientSession, "an object of client-session type"]


class Download:
    """Intializer and provider of primary stages of downloading a media or music.

    NOTICE: Entered urls must have available formats of videos and photos\n
    videos => [.mp4, .AVI, .MKV, .MOV]\n
    musics => [.mp3]\n
    photos => [.png, .jpg]\n
    Availabl Qualities => {
        music =>[128, 320]\n
        video => [144, 240, 360, 480, 720, 1080]\n
        }

    UNLESS: raised an Exception
    * In order to download a video or music, quality must be entered.
    """

    __slots__ = ("url", "quality", "status_bar")

    def __init__(
        self, url: HttpUrl, quality: int | None = None, status_bar: bool = False
    ):
        self.url = url
        self.quality = quality
        self.status_bar = status_bar

    def __repr__(self) -> Tuple[str, int]:
        return f"{self.__class__.__name__}{self.url, self.quality}"

    async def recognizer(self) -> Callable[[HttpUrl, int], BinaryIO]:
        """
        function which recognizes the url Entered
        is a photo or video or music in order to download
        """

        if (
            any(map(lambda x: x.value == self.url[-3:], tuple(VideoFormats)))
            or self.url[-3:] == "mp3"
        ):
            await _Video_Music_Downloader(
                self.url, self.quality, self.status_bar
            ).download_video_or_music()

        elif any(map(lambda x: x.value == self.url[-3:], tuple(PhotoFormats))):
            await _PhotoDownloader(self.url).download_photo()

        else:
            logger.error("the link dosen not exist...")
            raise UnAvailableLinkError


class _Video_Music_Downloader:
    """Class that download a video.."""

    def __init__(self, url: HttpUrl, quality: int, status_bar: bool):
        self.url = url
        self.quality = quality
        self.status_bar = status_bar
        self.match_quality = re.findall(
            r"128|320|144|240|360|480|720|1080", self.url, flags=re.MULTILINE
        )

    async def download_video_or_music(self) -> NoReturn | BinaryIO:

        if (
            any(map(lambda x: x.value == self.quality, tuple(Qualities)))
            and str(self.quality) in self.match_quality
        ) or (not self.match_quality):
            async with aiohttp.ClientSession() as session:
                async with session.get(self.url) as res:
                    if res.status == 200 and res.content_length:
                        logger.info(
                            f"the media with size of {res.content_length} bytes is about to download..."
                        )

                        async with aiofiles.open(
                            os.path.join(BASE_DIR, str(res.url.name)), "wb"
                        ) as file:

                            if self.status_bar:
                                with tqdm_asyncio(
                                    range(res.content_length),
                                    ascii=True,
                                    colour="red",
                                    desc="Downloading...",
                                    total=res.content_length,
                                    unit="KB",
                                ) as tqdm:

                                    async for data in res.content.iter_chunked(
                                        CHUNK_SIZE
                                    ):
                                        await file.write(data)
                                        tqdm.update(len(data))

                                    if self.url[-3:] == "mp3":
                                        with Session(engine) as session:
                                            insert = UserModel(music=str(res.url))
                                            session.add(insert)
                                            session.commit()

                                    with Session(engine) as session:
                                        insert = UserModel(video=str(res.url))
                                        session.add(insert)
                                        session.commit()

                            async for data in res.content.iter_chunked(CHUNK_SIZE):
                                await file.write(data)

                            if self.url[-3:] == "mp3":
                                with Session(engine) as session:
                                    insert = UserModel(
                                        music=str(
                                            res.url
                                        )  # str because the field does not support url type
                                    )
                                    session.add(insert)
                                    session.commit()

                            with Session(engine) as session:
                                insert = UserModel(video=str(res.url))
                                session.add(insert)
                                session.commit()

                            logger.info("the media has been successfully downloaded...")

                    else:
                        logger.error("the link does not exist...")
                        raise UnAvailableLinkError
        else:
            logger.error(
                "The quality is not available or does not match with the quality of url link"
            )
            raise QualityError


class _PhotoDownloader:
    """Class that download a photo."""

    def __init__(self, url: HttpUrl):
        self.url = url

    async def download_photo(self) -> NoReturn | BinaryIO:
        async with aiohttp.ClientSession() as session:
            async with session.get(self.url) as res:
                if res.status == 200 and res.content_length:
                    logger.info(
                        f"the media with size of {res.content_length}b is about to download..."
                    )
                    async with aiofiles.open(
                        os.path.join(BASE_DIR, str(res.url.name)), "wb"
                    ) as file:
                        await file.write(await res.read())

                    logger.info("the media has been successfully downloaded...")
                    with Session(engine) as session:
                        insert = UserModel(photo=str(res.url))
                        session.add(insert)
                        session.commit()
                else:
                    logger.error("the link does not exist...")
                    raise UnAvailableLinkError


async def _send_requests(session: aiohttp.ClientSession, url: HttpUrl) -> BinaryIO:
    async with session.get(url) as res:
        async with aiofiles.open(
            os.path.join(BASE_DIR, str(res.url.name)), "wb"
        ) as file:
            logger.info(
                f"the file with the size {res.content_length}b is about to download..."
            )
            async for data in res.content.iter_chunked(CHUNK_SIZE):
                await file.write(data)

            with Session(engine) as session_:
                insert = UserModel(
                    file=str(res.url)  # str because the field does not support url type
                )
                session_.add(insert)
                session_.commit()

            logger.info("the media has been successfully downloaded...")


async def download_multi_media(
    *urls: Iterable[HttpUrl],
) -> Callable[[Session_, HttpUrl], BinaryIO]:
    """Function that\'s able to download multi medias such as photos and
    videos or files with any formats together such as word or excel or etc files.

    NOTICE: no need to enter the quality of the video or music in this case.\n
    * Donloading videos or musics in this function is not recommended due to lack of quality.\n
    * In spite of that any Exceptions occured, the program does not crash
    in this function but the files downloaded are not openable.
    """
    async with aiohttp.ClientSession() as session:
        responses = (_send_requests(session, url) for url in urls)

        await asyncio.gather(*responses, return_exceptions=True)
