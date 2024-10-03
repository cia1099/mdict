from mdict_utils import reader
from bs4 import BeautifulSoup
import re, json

MDX_URL = "/Users/otto/Downloads/dict/oxfordstu.mdx"
HELP_MDX = "/Users/otto/Downloads/dict/cambridge4.mdx"

if __name__ == "__main__":
    query = "record"
    result = reader.query(MDX_URL, query)
    help_res = reader.query(HELP_MDX, query)
    help_soup = BeautifulSoup(help_res, "lxml")
    pron = [h5.get_text() for h5 in help_soup.find_all("span", class_="pron")]
    print(pron)
    # print(result)
    soup = BeautifulSoup(result, "lxml", exclude_encodings="unicode")
    heads = soup.find_all("h-g")
    dict_head = dict()
    for h_body in soup.find_all("h-g"):
        part_of_speech = h_body.find("z_p").get_text()
        alphabet = h_body.find("i").get_text()
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

        dict_head[part_of_speech] = {"alphabet": alphabet, "definitions": dict_def}

    print(json.dumps(dict_head))
