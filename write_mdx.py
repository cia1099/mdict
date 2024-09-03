from __future__ import unicode_literals
import asyncio, os, time
from typing import Coroutine, AsyncGenerator
from pathlib import Path
from mdict_utils.base.writemdict import MDictWriter

from test_gtts import rpc_gtts


def parse2template(word: str, pos: str, definition: str) -> str:
    html = f"""
<link href="example.css" rel="stylesheet" type="text/css" />
<div class="ml-1em">
<span class="color-navy"><b>{word}</b></span>
<span class="color-purple">/<a href="sound://{word}.mp3"><img src="/playsound.png"></a> lɪmp/ </span>
<span class="color-darkslategray bold italic">{pos}</span>
</div>
<div class="ml-2em">
{definition}
</div>
"""
    return html.replace("\n", "")


async def run_together(coroutines: AsyncGenerator[None, Coroutine]):
    print("Start to fetch sound files...", end="")
    tic = time.time()
    await asyncio.gather(*coroutines)
    print(f" elapsed {(time.time()-tic)*1e3:.4f} ms")


if __name__ == "__main__":
    dict_name = "example"
    dict_dir = Path(dict_name)
    dictionary = {
        "doe": ("noun", "a deer, a female deer."),
        "ray": ("noun", "a drop of golden sun."),
        "limp": ("adjective", "not firm or strong"),
    }
    try:
        dict_dir.mkdir()
    except:
        print(f"'{str(dict_dir)}' directory already exists")
    asyncio.run(
        run_together(
            (
                rpc_gtts(word, dir=str(dict_dir))
                for word in dictionary.keys()
                if not (dict_dir / f"{word}.mp3").exists()
            )
        )
    )
    writer = MDictWriter(
        {word: parse2template(word, v[0], v[1]) for word, v in dictionary.items()},
        title="Example Dictionary",
        description="This is an example dictionary.",
    )
    with open(f"{dict_name}.mdx", "wb") as of:
        writer.write(of)
    cmd = f"mdict -a {str(dict_dir)} {dict_name}.mdd"
    os.system(cmd)
