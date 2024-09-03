# How to create your own dictionary in mdx file format

### Preparation
You have to install these packages for creating mdx and mdd files
```sh
pip install pyglossary mdict-utils gTTS 
```
For visualization what is appearance of `.mdx` with `.mdd`, you should install [goldenDict](https://github.com/goldendict/goldendict).
### Introduction
A dictionary has `.mdx` and .mdd files, `.mdx` is used for the contents of dictionary, .mdd for assets of dictionary e.g. `.mp3`, images, `.css` format and cover image et cetera.\
For build `.mdx` file, you have to collect words, definitions and example sentences.\
`.mdd` file include sound files, you can use gTTS service to get them, that's why we install gTTS package. Moreover, we can embed images and css format files to relate every word in `.mdx` contents.
### Getting start
Before we start our code, we should create the project structure like:
```sh
./
├── example
│   ├── playsound.png
│   └── example.css #(optional)
├── example.json
├── example.css
└── write_mdx.py
```
* `example.json` contains your dictionary key-value contents, which meat key represent word and value is definition or any example, vowel etc.. Contains all of contents of the words in value json format, we will discuss it later. In additional you can use other data collection file(.csv, .db, .txt[...](https://github.com/ilius/pyglossary?tab=readme-ov-file)) to parse it. In this example we used json data format to create our `.mdx` file.
* `example.css` used to revise our contents become beautiful, you can put it outside the `/example` folder which we used to create our `.mdd` file. Put it outside `.mdd` can make us edit the layout or appearance of our contents conveniently, we can modify any aesthetics instantaneously when it display in goldenDict.
* `/example` directory collects all of any asset of word including images, sound files. we will use gTTs to collect our sound resources and put these into here. If you'd like to hide yor `.css` file, you could put it into this folder to pack together.

#### 1. Generate pronunciation by gTTS
Actually we can generate not only English pronunciation as long as [gTTs](https://gtts.readthedocs.io/en/latest/) has supported it. We wrote every word by:
```py
import asyncio
from gtts import gTTS
async def rpc_gtts(text: str, lang: str = "en", dir: str = ""):
    tts = gTTS(text, lang=lang)
    filename = text.split(" ")[0].lower() + ".mp3"
    tts.save(str(Path(dir) / filename))
```
The text is contents which you want to text to sound, lang is desired language, dir is target directory you want to save, `example` is our usage case in here. We used first word of text as our stem name, and we used async declaration because this function is heavy I/O operation. Using even loop is the most efficient way to handle tremendous requests concurrently, which save our life.
```py
import asyncio
import json, time
from pathlib import Path
from typing import Coroutine, AsyncGenerator

async def run_together(coroutines: AsyncGenerator[None, Coroutine]):
    print("Start to fetch sound files...", end="")
    tic = time.time()
    await asyncio.gather(*coroutines)
    print(f" elapsed {(time.time()-tic)*1e3:.4f} ms")

with open("example.json", 'r') as rf:
    dictionary = json.load(rf)

dict_dir = Path("example")
asyncio.run(
        run_together((
            rpc_gtts(word, dir=str(dict_dir)) for word in dictionary.keys() if not (dict_dir / f"{word}.mp3").exists()
        ))
    )
```
When you executed above code, you would get `.mp3` files in `example` folder. Now we have our pronunciation files, congratulation Dude!

#### 2. Example of dictionary content
Here is an example of our dictionary, you could modify your own dictionary as you can parse format. Our `example.json` look like:
```json
{
    "doe": ["noun", "a deer, a female deer."],
    "ray": ["noun", "a drop of golden sun."],
    "limp": ["adjective", "not firm or strong"]
}
```
We used this format to parse html format:
```py
def parse2html(word: str, pos: str, definition: str) -> str:
    html = f"""
<link href="example.css" rel="stylesheet" type="text/css" />
<div class="ml-1em">
<span class="color-navy"><b>{word}</b></span>
<span class="color-purple">/<a href="sound://{word}.mp3"><img src="/playsound.png"></a> lɪmp/ </span>
<span class="color-darkslategray bold italic">{pos}</span>
</div>
<div class="ml-2em">{definition}</div>
"""
    return html.replace("\n", "")
```
The html class tags are according to `example.css`, you can revise them belong your favors.\
We used this function to parse our `example.json` data and write to `.mdx` file:
```py
import json
from mdict_utils.base.writemdict import MDictWriter

with open("example.json", 'r') as rf:
    dictionary = json.load(rf)

writer = MDictWriter(
        {word: parse2html(word, v[0], v[1]) for word, v in dictionary.items()},
        title="Example Dictionary",
        description="This is an example dictionary.",
    )
with open(f"example.mdx", "wb") as wf:
    writer.write(wf)
``` 
#### 3. Pack our dictionary with sounds and images
This is easiest step to do it. We just type the command in terminal to our resource folder which we collected source from step 1 then pack to a `.mdd` file:
```sh
mdict -a example example.mdd
```

### Summary
Congratulation, we have the `.mdx` and `.mdd` files which can put together then the goldenDict can read. We can open it to check our example appear well.\
There are some good dictionary that you can refer to create how they builded it.\
[freedict](https://downloads.freemdict.com/%E5%B0%9A%E6%9C%AA%E6%95%B4%E7%90%86/%E9%9B%86%E5%90%88/)\
You can query a word to see what is their format:
```sh
mdict -q <word> <dict>.mdx
```
Or use [pyglossary](https://github.com/ilius/pyglossary?tab=readme-ov-file) to unpack `.mdx`
```sh
# txt format
pyglossary example.mdx example.txt
# json format
pyglossary example.mdx example.json
```
[mdict-utils](https://github.com/liuyug/mdict-utils) also can unpack:
```sh
mkdir -p mdx
mdict -x <dict>.mdx -d ./mdx
```

