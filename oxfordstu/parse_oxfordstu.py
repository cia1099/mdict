from mdict_utils import reader
from bs4 import BeautifulSoup
import re, json
from pathlib import Path


def get_alphabet(soup: BeautifulSoup) -> dict:
    pron_dict = dict()
    for pos_header in soup.find_all("div", class_="pos-header"):
        pos = pos_header.find("span", class_="pos").get_text()
        # American phonetic at last
        # pron = pos_header.find_all("span", class_="pron")[-1]
        # pron_dict[pos] = pron.get_text()
        pron_dict[pos] = [
            h5.get_text() for h5 in pos_header.find_all("span", class_="pron")
        ]
    # print(pron_dict)
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
            print("No subscript in entry-body__el")
            pos = soup.find("span", class_="pos")
            if pos is not None:
                pos = pos.get_text()
        cn_def = "、".join(
            [h5.get_text() for h5 in entry.find_all("span", class_="cn_def")]
        )
        cn_dict[pos] = cn_def

    return cn_dict, get_alphabet(soup)


def get_macmillan_tense(word: str) -> dict:
    mdx_url = "/Users/otto/Downloads/dict/MacmillanEnEn.mdx"
    res = reader.query(mdx_url, word)
    soup = BeautifulSoup(res, "lxml")
    dict_tense = dict()
    for body in soup.find_all("div", class_="dict-american"):
        pos = body.find("span", class_="part-of-speech-ctx").get_text()
        tenses = ", ".join(
            [h5.get_text() for h5 in body.find_all("span", class_="inflection-entry")]
        )
        dict_tense[pos] = tenses
    # print(json.dumps(dict_tense))
    return dict_tense


def get_asset_oxfordstu(soup: BeautifulSoup):
    path = None
    try:
        img = soup.find("div", class_="pic").find("img")
        path = img["src"].replace("file", "oxfordstu")
    except:
        pass
        # print("No asset in this word")
    return path


def create_oxfordstu_word(word: str):
    mdx_url = "/Users/otto/Downloads/dict/oxfordstu.mdx"
    html = reader.query(mdx_url, word)
    soup = BeautifulSoup(html, "lxml")
    asset = get_asset_oxfordstu(soup)
    if asset is not None:
        # insert one asset below
        print("\x1b[32m%s\x1b[0m" % asset)
    cn_dict, alphabets = get_cambridge_chinese(word)
    tense = get_macmillan_tense(word)
    dict_head = dict()
    for h_body in soup.find_all("h-g"):
        part_of_speech = h_body.find("z_p").get_text()
        # alphabet = h_body.find("i").get_text() #oxfordstu can't encode utf-8
        alphabet = alphabets.get(part_of_speech, None)
        chinese = cn_dict.get(part_of_speech, None)
        inflection = tense.get(part_of_speech, "")
        i_body = h_body.find("i-g")
        hrefs = i_body.find_all("a", href=re.compile(r"sound://*"))
        audio_names = [Path(h["href"]).name for h in hrefs]
        # print(", ".join(["\x1b[32m%s\x1b[0m" % name for name in audio_names]))
        # insert one row definition below
        dict_def = []
        for n_body in h_body.find_all("n-g"):
            try:
                subscript = n_body.find(re.compile(r"z_(gr|pt)")).get_text()
            except:
                print("No subscript in n-g tag")
                subscript = h_body.find(re.compile(r"z_(gr|pt)"))
                if subscript is not None:
                    subscript = subscript.get_text()

            definition = n_body.find("d").get_text()
            # insert one row explanation below
            examples = [h5.get_text() for h5 in n_body.find_all("x")]
            # insert one row example below
            dict_def.append(
                {"subscript": subscript, "definition": definition, "examples": examples}
            )

        dict_head[part_of_speech] = {
            "alphabet": alphabet,
            "definitions": dict_def,
            "chinese": chinese,
            "inflection": inflection,
        }

    print(json.dumps(dict_head))


if __name__ == "__main__":
    query = "apple"
    # print(result)

    # _, pron_dict = get_cambridge_chinese(query)
    create_oxfordstu_word(query)
    # get_macmillan_tense(query)
