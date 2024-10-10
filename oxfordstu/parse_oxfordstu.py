from mdict_utils import reader
from bs4 import BeautifulSoup
import re, json
from pathlib import Path
from logging import Logger


def get_alphabet(soup: BeautifulSoup) -> dict:
    pron_dict = dict()
    for pos_header in soup.find_all("div", class_="pos-header"):
        pos = pos_header.find("span", class_="pos").get_text()
        # American phonetic at last
        # pron = pos_header.find_all("span", class_="pron")[-1]
        # pron_dict[pos] = pron.get_text()

        prons = [h5.get_text() for h5 in pos_header.find_all("span", class_="pron")]
        if len(prons) > 0:
            pron_dict[pos] = prons
    # print(get_cambridge_chinese(word))
    return pron_dict


def get_cambridge_chinese(word: str) -> tuple[dict]:
    mdx_url = "/Users/otto/Downloads/dict/cambridge4.mdx"
    res = reader.query(mdx_url, word)
    soup = BeautifulSoup(res, "lxml")
    cn_dict = dict()
    for entry in soup.find_all("div", class_="entry-body__el"):
        try:
            pos = entry.find("span", class_="pos").get_text()
        except:
            # print("No subscript in entry-body__el")
            pos = soup.find("span", class_="pos")
            if pos is not None:
                pos = pos.get_text()
        cn_def = "、".join(
            [h5.get_text() for h5 in entry.find_all("span", class_="cn_def")]
        )
        cn_dict[pos] = cn_def

    return cn_dict, get_alphabet(soup)


def get_macmillan_tense(word: str) -> tuple[dict]:
    mdx_url = "/Users/otto/Downloads/dict/MacmillanEnEn.mdx"
    res = reader.query(mdx_url, word)
    soup = BeautifulSoup(res, "lxml")
    dict_tense = dict()
    dict_pron = dict()
    for body in soup.find_all("div", class_="dict-american"):
        try:
            pos = body.find("span", class_="part-of-speech-ctx").get_text()
        except:
            continue
        tenses = ", ".join(
            [h5.get_text() for h5 in body.find_all("span", class_="inflection-entry")]
        )
        prons = [h5.get_text() for h5 in body.find_all("span", class_="pron")]
        dict_tense[pos] = tenses if len(tenses) > 0 else None
        dict_pron[pos] = list(map(lambda s: s.replace(" ", ""), prons))
    # print(json.dumps(dict_tense))
    return dict_tense, dict_pron


def get_asset_oxfordstu(soup: BeautifulSoup):
    path = None
    try:
        img = soup.find("div", class_="pic").find("img")
        path = img["src"].replace("file", "oxfordstu")
    except:
        pass
        # print("No asset in this word")
    return path


def create_oxfordstu_word(soup: BeautifulSoup, word: str, log: Logger = None) -> dict:
    dict_word = dict()
    for h_body in soup.find_all("h-g"):
        try:
            part_of_speech = h_body.find("z_p").get_text()
        except:
            msg = f"'{word}' doesn't speech in <z_p> tag"
            if log:
                log.debug(msg)
            else:
                print(msg)
            continue
        # alphabet = h_body.find("i").get_text() #oxfordstu can't encode utf-8
        word_defs = []
        for n_body in h_body.find_all("n-g"):
            try:
                subscript = n_body.find(re.compile(r"z_(gr|pt)")).get_text()
            except:
                msg = f"'{word}' No subscript in n-g tag"
                if log:
                    log.debug(msg)
                else:
                    print(msg)
                subscript = h_body.find(re.compile(r"(z_(gr|pt)|gram-g)"))
                if subscript:
                    subscript = (
                        "".join([f"({n5.get_text()})" for n5 in n_body.find_all("z_s")])
                        + subscript.get_text()
                    )

            # explain = n_body.find(re.compile(r"(d|xr-g)"))
            explain = n_body.find("d")
            if explain:
                explain = explain.get_text()
            else:
                msg = f"'{word}'({part_of_speech}, subscript={subscript}) doesn't have <d> tag in <n-g>"
                if log:
                    log.warning(msg)
                else:
                    print(f"\x1b[43m{msg}\x1b[0m")
                continue
            examples = [h5.get_text() for h5 in n_body.find_all("x")]
            word_defs.append(
                {"explanation": explain, "subscript": subscript, "examples": examples}
            )

        try:
            i_body = h_body.find("i-g")
            hrefs = i_body.find_all("a", href=re.compile(r"sound://*"))
            audio_names = [h["href"].replace("sound", "oxfordstu") for h in hrefs]
        except:
            # raise ValueError(f"doesn't have <i-g> tag")
            audio_names = []
        # print(", ".join(["\x1b[32m%s\x1b[0m" % name for name in audio_names]))
        dict_word[part_of_speech] = {"def": word_defs, "audio": audio_names}
    # ===== dr-g
    for dr_body in soup.find_all("dr-g"):
        try:
            part_of_speech = dr_body.find("z_p").get_text()
        except:
            msg = f"'{word}' doesn't speech in <z_p> tag"
            if log:
                log.debug(msg)
            else:
                print(msg)
            continue
        subscript = dr_body.find(re.compile(r"(z_(gr|pt)|gram-g)"))
        if subscript:
            subscript = (
                "".join([f"({dr5.get_text()})" for dr5 in dr_body.find_all("z_s")])
                + subscript.get_text()
            )

        explain = dr_body.find(re.compile(r"\b(zd|dr)\b"))
        if explain:
            explain = explain.get_text()
        else:
            msg = f"'{word}'({part_of_speech}, subscript={subscript}) doesn't have <dr|zd> tag in <dr-g>"
            if log:
                log.warning(msg)
            else:
                print(f"\x1b[43m{msg}\x1b[0m")
            continue
        examples = [h5.get_text() for h5 in dr_body.find_all("x")]
        word_def = {
            "explanation": explain,
            "subscript": subscript,
            "examples": examples,
        }
        try:
            i_body = dr_body.find("i-g")
            hrefs = i_body.find_all("a", href=re.compile(r"sound://*"))
            audio_names = [h["href"].replace("sound", "oxfordstu") for h in hrefs]
        except:
            audio_names = []
        dict_word[part_of_speech] = {"def": [word_def], "audio": audio_names}

    # print(json.dumps(dict_word))
    return dict_word


if __name__ == "__main__":
    from time import time
    from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
    from multiprocessing.pool import ThreadPool

    query = "abdomen"
    mdx_url = "/Users/otto/Downloads/dict/oxfordstu.mdx"
    # print(result)

    tic = time()

    html = reader.query(mdx_url, query)
    soup = BeautifulSoup(html, "lxml")

    ## ---- Pool executor: 388 ms
    # with ThreadPoolExecutor(max_workers=4) as executor:
    #     future_oxfordstu = executor.submit(create_oxfordstu_word, soup)
    #     future_cambridge = executor.submit(get_cambridge_chinese, query)
    #     future_macmillan = executor.submit(get_macmillan_tense, query)
    # _, pron_dict = future_cambridge.result()
    # _, p2 = future_macmillan.result()
    # oxfordstu_word = future_oxfordstu.result()
    ## ---- Multiple Thread: 393 ms
    # def outer_query(query: str) -> tuple[dict]:
    #     cambridge = get_cambridge_chinese(query)
    #     macmillan = get_macmillan_tense(query)
    #     return cambridge + macmillan

    # futures = ThreadPool(processes=1).apply_async(outer_query, (query,))
    # oxfordstu_word = create_oxfordstu_word(soup)
    # _, pron_dict, _, p2 = futures.get()
    ## ---- Single core: 388 ms
    oxfordstu_word = create_oxfordstu_word(soup, query)
    _, pron_dict = get_cambridge_chinese(query)
    tense, p2 = get_macmillan_tense(query)
    print(json.dumps(oxfordstu_word))
    print(pron_dict)
    print(p2)
    print(f"Elapsed = \x1b[32m{(time()-tic)*1e3:.3f}\x1b[0m msec")
