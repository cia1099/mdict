from mdict_utils import reader
from bs4 import BeautifulSoup
import re, json

MDX_URL = "/Users/otto/Downloads/dict/oxfordstu.mdx"


def get_alphabet(soup: BeautifulSoup) -> dict:
    pron_dict = dict()
    for pos_header in soup.find_all("div", class_="pos-header"):
        pos = pos_header.find("span", class_="pos").get_text()
        pron = pos_header.find_all("span", class_="pron")[-1]
        pron_dict[pos] = pron.get_text()
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


def create_oxfordstu_word(word: str):
    soup = BeautifulSoup(result, "lxml")
    dict_head = dict()
    cn_dict, alphabets = get_cambridge_chinese(word)
    for h_body in soup.find_all("h-g"):
        part_of_speech = h_body.find("z_p").get_text()
        # alphabet = h_body.find("i").get_text()
        alphabet = alphabets.get(part_of_speech, None)
        chinese = cn_dict.get(part_of_speech, None)
        # insert one row definition
        dict_def = []
        for n_body in h_body.find_all("n-g"):
            try:
                subscript = n_body.find(re.compile(r"z_(gr|pt)")).get_text()
            except:
                print("No subscript in n-g tag")
                subscript = h_body.find(re.compile(r"z_(gr|pt)"))
                if subscript is not None:
                    subscript = subscript.get_text()

            # insert one row explanation
            definition = n_body.find("d").get_text()
            # insert one row example
            examples = [h5.get_text() for h5 in n_body.find_all("x")]
            dict_def.append(
                {"subscript": subscript, "definition": definition, "examples": examples}
            )

        dict_head[part_of_speech] = {
            "alphabet": alphabet,
            "definitions": dict_def,
            "chinese": chinese,
        }

    print(json.dumps(dict_head))


if __name__ == "__main__":
    query = "record"
    result = reader.query(MDX_URL, query)
    # print(result)

    # _, pron_dict = get_cambridge_chinese(query)
    create_oxfordstu_word(query)
