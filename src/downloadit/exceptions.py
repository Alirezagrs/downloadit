class DownloaditExeption(Exception):
    pass


class QualityError(DownloaditExeption):
    pass


class UnAvailableLinkError(DownloaditExeption):
    pass
