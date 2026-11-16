from yt_dlp.utils import DownloadError
from loguru import logger
from mutagen.mp4 import MP4
from YTdlp.exceptions import (
    UnsupportedURLError,
    FileTooLargeError,
    VideoDownloadError,
    PrivateVideoError,
    GeoRestrictedError,
    AgeRestrictedError,
    FFmpegError,
    NetworkTimeoutError
)
import imageio_ffmpeg as im_ffmpeg
import uuid
import yt_dlp
import os


def sync_download_video(video_url):
    unique_id = uuid.uuid4().hex

    ydl_opts = {
        'js_runtimes': {'deno': {}},
        'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
        'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36',
        'merge_output_format': 'mp4',
        'outtmpl': f'downloads/{unique_id}/%(id)s.%(ext)s',
        'quiet': True,
        'ffmpeg_location': im_ffmpeg.get_ffmpeg_exe(),
        'cookies_from_browser': 'firefox',
        'max_filesize': 50 * 1024 * 1024,
        'socket_timeout': 30
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:  # type: ignore
        try:
            info = ydl.extract_info(video_url, download=True)

            file = ydl.prepare_filename(info)

            if os.path.exists(file):
                video = MP4(file)
                duration = round(video.info.length)
            else:
                logger.error(f"File not found on disk after download: {file} (Task ID: {unique_id})")
                return None

            return {
                'platform': info.get('extractor_key', None),  # type: ignore
                'title': info.get('title', "Missing"),
                'file_path': file,
                'duration': duration,
            }

        except DownloadError as E:
            err_msg = str(E)
            logger.error(f"DownloadError for {video_url} (Task ID: {unique_id}). Original error: {err_msg}")

            if "larger than max-filesize" in err_msg:
                raise FileTooLargeError("File exceeds the allowed size limit.") from E
            elif "Unsupported URL" in err_msg or "is not a valid URL" in err_msg:
                raise UnsupportedURLError("This URL is not supported.") from E
            elif "Private video" in err_msg or "This video is unavailable" in err_msg:
                raise PrivateVideoError("Video deleted, hidden by the author, or unavailable.") from E
            elif "Geo-restricted" in err_msg:
                raise GeoRestrictedError("Video is blocked by the copyright holder in the server's region.") from E
            elif "Sign in to confirm your age" in err_msg:
                raise AgeRestrictedError("Video has an age restriction. Authorization required.") from E
            elif "ffmpeg" in err_msg.lower():
                raise FFmpegError("Media processing error on the server (FFmpeg issue).") from E
            elif "Temporary failure in name resolution" in err_msg or "timed out" in err_msg:
                raise NetworkTimeoutError("Network or hosting access issue.") from E

            raise VideoDownloadError(f"Download error: {E}") from E

        except TimeoutError as E:
            logger.error(f"Timeout Error for {video_url} (Task ID: {unique_id}): {E}")
            raise NetworkTimeoutError("Connection timed out.") from E

        except Exception as E:
            logger.exception(f"Unknown error while downloading {video_url} (Task ID: {unique_id}): {E}")
            raise