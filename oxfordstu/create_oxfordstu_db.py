import os, re
from pathlib import Path
from mdict_utils import reader
import sqlalchemy as sql
from bs4 import BeautifulSoup
from tqdm import tqdm
from oxfordstu_schema import *
from log_config import log
from parse_oxfordstu import (
    get_asset_oxfordstu,
    get_cambridge_chinese,
    get_macmillan_tense,
)


def insert_word(cursor: sql.engine.Connection, word_idx: int, word: str) -> int:
    stmt = sql.insert(Word).values(word=word)
    try:
        cursor.execute(stmt)
        word_idx += 1
    except:
        raise ValueError(f"Cannot replicate word({word}) in database")
    return word_idx


def remove_word(cursor: sql.engine.Connection, word_idx: int) -> int:
    stmt = sql.delete(Word).where(Word.id == word_idx)
    try:
        cursor.execute(stmt)
        word_idx -= 1
    except:
        log.debug(f"Cannot delete word({word}, id={word_idx}) in database")
    return word_idx


def insert_definition(
    cursor: sql.engine.Connection, word_idx: int, definition_idx: int, **kwargs
) -> int:
    stmt = sql.insert(Definition).values(word_id=word_idx, **kwargs)
    try:
        cursor.execute(stmt)
        definition_idx += 1
    except:
        log.debug(
            f"Fail insert definition(id={definition_idx}) word(id={word_idx}), speech={kwargs['part_of_speech']}"
        )
    return definition_idx


def insert_explanation(
    cursor: sql.engine.Connection,
    word_idx: int,
    definition_idx: int,
    explanation_idx: int,
    **kwargs,
) -> int:
    stmt = sql.insert(Explanation).values(
        word_id=word_idx, definition_id=definition_idx, **kwargs
    )
    try:
        cursor.execute(stmt)
        explanation_idx += 1
    except:
        log.debug(
            f"Fail insert explanation(id={explanation_idx}) word(id={word_idx}), explain={kwargs['explain']}"
        )
    return explanation_idx


def insert_asset(cursor: sql.engine.Connection, word_idx: int, filename: str):
    stmt = sql.insert(Asset).values(word_id=word_idx, filename=filename)
    try:
        cursor.execute(stmt)
    except:
        log.debug(f"Fail asset of word(id={word_idx}), filename={filename}")


def insert_example(
    cursor: sql.engine.Connection,
    word_idx: int,
    explanation_idx: int,
    example_idx: int,
    **kwargs,
) -> int:
    stmt = sql.insert(Example).values(
        word_id=word_idx, explanation_id=explanation_idx, **kwargs
    )
    try:
        cursor.execute(stmt)
        example_idx += 1
    except:
        log.debug(
            f"Fail insert example(id={example_idx}) word(id={word_idx}), example={kwargs['example']}"
        )
    return example_idx


def create_oxfordstu_word(
    word: str,
    word_idx: int,
    definition_idx: int,
    explanation_idx: int,
    example_idx: int,
    cursor: sql.engine.Connection,
) -> tuple[int]:
    mdx_url = "/Users/otto/Downloads/dict/oxfordstu.mdx"
    html = reader.query(mdx_url, word)
    soup = BeautifulSoup(html, "lxml")
    try:
        cn_dict, alphabets = get_cambridge_chinese(word)
    except:
        raise ValueError(f"{word} failed getting from cambridge")
    try:
        tense = get_macmillan_tense(word)
    except:
        raise ValueError(f"{word} failed getting from macmillan")

    word_idx = insert_word(cursor, word_idx=word_idx, word=word)
    asset = get_asset_oxfordstu(soup)
    if asset is not None:
        insert_asset(cursor, word_idx=word_idx, filename=asset)
    for h_body in soup.find_all("h-g"):
        part_of_speech = h_body.find("z_p").get_text()
        # alphabet = h_body.find("i").get_text() #oxfordstu can't encode utf-8
        alphabet = alphabets.get(part_of_speech, None)
        chinese = cn_dict.get(part_of_speech, None)
        if alphabet is None or chinese is None:
            word_idx = remove_word(cursor, word_idx)
            raise ValueError(
                f'"{word}" mismatched [{part_of_speech}] in alphabets: {[k for k in alphabets.keys()]}, chinese: {[k for k in cn_dict.keys()]}'
            )
        inflection = tense.get(part_of_speech, "")
        try:
            i_body = h_body.find("i-g")
            hrefs = i_body.find_all("a", href=re.compile(r"sound://*"))
        except:
            word_idx = remove_word(cursor, word_idx)
            raise ValueError(f'"{word}" doesn\'t have <i-g> tag')
        audio_names = [Path(h["href"]).name for h in hrefs]
        # print(", ".join(["\x1b[32m%s\x1b[0m" % name for name in audio_names]))
        # insert one row definition below
        definition_idx = insert_definition(
            cursor,
            word_idx,
            definition_idx,
            part_of_speech=part_of_speech,
            inflection=inflection,
            alphabet_uk=alphabet[0],
            alphabet_us=alphabet[1],
            audio_uk=audio_names[0],
            audio_us=audio_names[1],
            chinese=chinese,
        )

        for n_body in h_body.find_all("n-g"):
            try:
                subscript = n_body.find(re.compile(r"z_(gr|pt)")).get_text()
            except:
                log.warning(f"{word} has no subscript in n-g tag")
                subscript = h_body.find(re.compile(r"z_(gr|pt)"))
                if subscript is not None:
                    subscript = subscript.get_text()

            explain = n_body.find("d").get_text()
            # insert one row explanation below
            explanation_idx = insert_explanation(
                cursor,
                word_idx,
                definition_idx,
                explanation_idx,
                subscript=subscript,
                explain=explain,
            )
            examples = [h5.get_text() for h5 in n_body.find_all("x")]
            # insert multiple rows example below
            for example in examples:
                example_idx = insert_example(
                    cursor, word_idx, explanation_idx, example_idx, example=example
                )

    return word_idx, definition_idx, explanation_idx, example_idx


if __name__ == "__main__":
    os.system("rm oxfordstu.db")
    DB_URL = "sqlite:///oxfordstu.db"
    MDX_URL = "/Users/otto/Downloads/dict/oxfordstu.mdx"

    engine = create_engine(DB_URL, echo=False)
    Base.metadata.create_all(engine)
    word_idx, definition_idx, explanation_idx, example_idx = 0, 0, 0, 0
    test_words = ["apple", "record", "watch"]
    with engine.connect() as cursor:
        for word in test_words:  # tqdm(reader.get_keys(MDX_URL), total=28895):
            try:
                word_idx, definition_idx, explanation_idx, example_idx = (
                    create_oxfordstu_word(
                        word,
                        word_idx,
                        definition_idx,
                        explanation_idx,
                        example_idx,
                        cursor,
                    )
                )
            except ValueError as e:
                log.debug(f"{e}")

        cursor.commit()
