class AioDownloaderExeption(Exception):
    pass


class QualityError(AioDownloaderExeption):
    pass


class UnAvailableLinkError(AioDownloaderExeption):
    pass
