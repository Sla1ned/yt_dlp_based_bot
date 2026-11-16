from urllib.parse import urlparse
from aiogram.filters import Filter
from aiogram.types import Message
from pydantic import HttpUrl, TypeAdapter, ValidationError

url_adapter = TypeAdapter(HttpUrl)

ALLOWED_DOMAINS = {
    # YouTube
    "youtube.com",
    "www.youtube.com",
    "m.youtube.com",
    "youtu.be",
    # Instagram
    "instagram.com",
    "www.instagram.com",
    "m.instagram.com",
    # TikTok
    "tiktok.com",
    "www.tiktok.com",
    "m.tiktok.com",
    "vt.tiktok.com",
    "vm.tiktok.com",
    # Facebook
    "facebook.com",
    "www.facebook.com",
    "m.facebook.com",
    "vt.facebook.com",
}


class StrictURLFilter(Filter):
    async def __call__(self, message: Message, **kwargs) -> bool | dict[str, HttpUrl]:

        if not message.text:
            return False

        cleaned_text = message.text.strip()


        if any(char.isspace() for char in cleaned_text):
            return False

        try:

            validated_url: HttpUrl = url_adapter.validate_python(cleaned_text)


            domain = urlparse(str(validated_url)).netloc.lower()

            domain = domain.split(":")[0]


            if domain in ALLOWED_DOMAINS:
                return {"url": validated_url}

            return False

        except ValidationError:
            return False