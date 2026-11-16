import os.path

from aiogram import Router, F
from aiogram.types import Message, FSInputFile
from aiogram.filters import CommandStart, Command
from aiogram.exceptions import TelegramNetworkError, TelegramBadRequest, TelegramForbiddenError
from aiogram.enums import ChatType
from sqlalchemy.ext.asyncio import AsyncSession

from YTdlp.installer import sync_download_video
from YTdlp.exceptions import *
from filter.pydantic_filter import StrictURLFilter

from database.requests import get_subscription_data
from database.models import User, Group

from loguru import logger
import aiofiles.os
import asyncio
import html

rt = Router()
download_semaphore = asyncio.Semaphore(6)


@rt.message(CommandStart(), F.chat.type.in_({ChatType.PRIVATE, ChatType.GROUP, ChatType.SUPERGROUP}))
async def start_handler(message: Message):
    if not message.from_user: return
    if message.chat.type in (ChatType.GROUP, ChatType.SUPERGROUP): return
    name = message.from_user.username if message.from_user.username else message.from_user.first_name
    safe_name = html.escape(name)
    await message.answer(
        f"Hello <b><i>{safe_name}</i></b>, this is a Telegram bot that allows you to download short YouTube videos! (including TikTok)\n\n"
        "Use /help to see all commands."
    )

@rt.message(Command("subscription"), F.chat.type.in_({ChatType.PRIVATE, ChatType.GROUP, ChatType.SUPERGROUP}))
async def subscription_info(message: Message, session: AsyncSession):
    if not message.from_user: return

    if message.chat.type == ChatType.PRIVATE:
        model_name = User.__name__
        user_id = message.from_user.id
        date = await get_subscription_data(id=user_id, session=session, model_type=User)
    else:
        model_name = Group.__name__
        group_id_ = message.chat.id
        date = await get_subscription_data(id=group_id_, session=session, model_type=Group)

    if date is None:
        await message.answer("Make sure your subscription is active")
        return

    await message.answer(f"{model_name},\n Subscription expires: {date}")


@rt.message(Command("help"), F.chat.type.in_({ChatType.PRIVATE, ChatType.GROUP, ChatType.SUPERGROUP}))
async def help_handler(message: Message):
    help_text = (
        "🤖 <b>Bot Commands:</b>\n\n"

        "🔗 <b>Downloading Videos:</b>\n"
        "Just send a link to a video from YouTube, TikTok, Instagram, or Facebook, and I will download it for you.\n\n"

        "💎 <b>Subscription & Limits:</b>\n"
        "• <code>/buy [days]</code> — Buy/extend a premium subscription (e.g., <code>/buy 30</code>).\n"
        "• <code>/subscription</code> — Check when your current subscription expires.\n\n"

        "ℹ️ <b>Other:</b>\n"
        "• <code>/group_id</code> — Get the ID of the current group (only works in groups).\n"
        "• <code>/help</code> — Show this help message.\n\n"

        "<i>Note: To download videos, you need an active subscription.</i>"
    )

    await message.answer(help_text)

@rt.message(StrictURLFilter())
async def download_video_handler(message: Message):
    path: str | None = None

    try:
        async with download_semaphore:
            video_inf = await asyncio.to_thread(sync_download_video, message.text)
            path = video_inf.get('file_path')

            if await aiofiles.os.path.exists(path):  # type: ignore
                download_video = FSInputFile(path, filename=video_inf.get('title') + ".mp4")  # type: ignore
                await message.answer_video(download_video, request_timeout=300)
            else:
                logger.error(f"Nothing found at path: {path}")
                await message.answer("❌ Failed to find the video on the server.")

    except FileTooLargeError:
        logger.error("FileTooLargeError: video exceeds 50 MB")
        await message.answer("⚠️ Video is too large! Telegram limit is 50 MB.")

    except UnsupportedURLError:
        logger.error("UnsupportedURLError: link not supported")
        await message.answer("⚠️ This link is not supported. Please send a valid YouTube, TikTok, or Instagram link.")

    except PrivateVideoError:
        logger.error("PrivateVideoError: video deleted or unavailable")
        await message.answer("❌ This video is deleted, hidden by the author, or unavailable.")

    except GeoRestrictedError:
        logger.error("GeoRestrictedError: video blocked in server region")
        await message.answer("🌍 This video is blocked by the copyright holder in the server's region.")

    except AgeRestrictedError:
        logger.error("AgeRestrictedError: video requires authorization")
        await message.answer("🔞 This video has an age restriction. Authorization required.")

    except FFmpegError:
        logger.error("FFmpegError: media processing failed")
        await message.answer("⚙️ Server error while processing the video (FFmpeg issue). Please try another link.")

    except NetworkTimeoutError:
        logger.error("NetworkTimeoutError: network or hosting access issue")
        await message.answer("🌐 Network timeout. Please try again later.")

    except VideoDownloadError as e:
        logger.error(f"VideoDownloadError: {e}")
        await message.answer(f"❌ Failed to download the video. Error: {e}", parse_mode=None)

    except TelegramNetworkError as e:
        logger.error(f"TelegramNetworkError while sending video: {e}")
        await message.answer("🌐 Network error occurred while sending the video.")

    except TelegramBadRequest as e:
        logger.error(f"TelegramBadRequest: {e}")
        await message.answer("❌ Telegram rejected the video format.")

    except TelegramForbiddenError as e:
        logger.error(f"TelegramForbiddenError: {e}")

    except Exception as e:
        logger.exception(f"Unexpected error: {e}")
        await message.answer("❌ An unexpected server error occurred. Please try again later.")

    finally:
        if path and await aiofiles.os.path.exists(path):
            await aiofiles.os.remove(path)

        if path:
            folder_path = os.path.dirname(path)

            if await aiofiles.os.path.exists(folder_path):
                try:
                    await aiofiles.os.rmdir(folder_path)
                except OSError:
                    pass