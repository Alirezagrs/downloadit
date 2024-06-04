import enum
from pathlib import Path
from typing import Final, final

BASE_DIR: Final = Path(__file__).parent.parent
CHUNK_SIZE: Final = 3065


@final
class Qualities(enum.IntEnum):
    # Quality of musics
    _128 = 128
    _320 = 320
    # Quality of videos
    _144 = 144
    _240 = 240
    _360 = 360
    _480 = 480
    _720 = 720
    _1080 = 1080


@final
class VideoFormats(enum.Enum):
    MP4 = "mp4"
    AVI = "AVI"
    MKV = "MKV"
    MOV = "MOV"


@final
class PhotoFormats(enum.Enum):
    JPG = "jpg"
    PNG = "png"
