class FileTooLargeError(Exception):
    pass

class UnsupportedURLError(Exception):
    pass

class PrivateVideoError(Exception):
    pass

class GeoRestrictedError(Exception):
    pass

class AgeRestrictedError(Exception):
    pass

class FFmpegError(Exception):
    pass

class NetworkTimeoutError(Exception):
    pass

class VideoDownloadError(Exception):
    pass