from io import BytesIO
import asyncio
from pathlib import Path
from httpx import AsyncClient, HTTPStatusError
from gtts import gTTS
import pyglet


async def get_gtts(text: str, lang: str = "en"):
    async with AsyncClient(base_url="https://translate.google.com") as client:
        try:
            res = await client.get(
                "/translate_tts",
                params={
                    "ie": "UTF-8",
                    "q": text,
                    "tl": lang,
                    "client": "tw-ob",
                },
                headers={
                    "Referer": "http://translate.google.com/",
                    "User-Agent": "stagefright/1.2 (Linux;Android 9.0)",
                },
            )
            res.raise_for_status()
            filename = text.split(" ")[0].lower()
            with open(f"{filename}.mp3", "wb") as of:
                of.write(res.content)
        except HTTPStatusError as err:
            raise Exception(
                f"API request failed with status code {err.response.status_code}"
            ) from err


async def rpc_gtts(text: str, lang: str = "en", dir: str = ""):
    # ref. https://gtts.readthedocs.io/en/latest/
    tts = gTTS(text, lang=lang)
    filename = text.split(" ")[0].lower() + ".mp3"
    tts.save(str(Path(dir) / filename))


def direct_gtts(text: str, tld: str):
    tts = gTTS(text, lang="en", tld=tld)
    with BytesIO() as mp3_fp:
        tts.write_to_fp(mp3_fp)
        mp3_fp.seek(0)
        player = pyglet.media.load("_.mp3", file=mp3_fp).play()
        while player.playing:
            pyglet.app.platform_event_loop.dispatch_posted_events()
            pyglet.clock.tick()
    print("terminal gtts")


if __name__ == "__main__":
    # asyncio.run(get_gtts("Hi fuck your mother"))
    # asyncio.run(rpc_gtts("Hi fuck your mother", dir="mdd_dict"))
    direct_gtts("Hello, shit man!", tld="co.za")
