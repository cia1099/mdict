from dataclasses import dataclass
from typing import List, Any, TypeVar, Callable, Type, cast


T = TypeVar("T")


def from_str(x: Any) -> str:
    assert isinstance(x, str)
    return x


def from_list(f: Callable[[Any], T], x: Any) -> List[T]:
    assert isinstance(x, list)
    return [f(y) for y in x]


def to_class(c: Type[T], x: Any) -> dict:
    assert isinstance(x, c)
    return cast(Any, x).to_dict()


@dataclass
class Def:
    explanation: str
    subscript: str | None
    examples: List[str]

    @staticmethod
    def from_dict(obj: Any) -> "Def":
        assert isinstance(obj, dict)
        explanation = from_str(obj.get("explanation"))
        subscript = obj.get("subscript")
        examples = from_list(from_str, obj.get("examples"))
        return Def(explanation, subscript, examples)

    def to_dict(self) -> dict:
        result: dict = {}
        result["explanation"] = from_str(self.explanation)
        result["subscript"] = self.subscript
        result["examples"] = from_list(from_str, self.examples)
        return result


@dataclass
class PartWord:
    part_word_def: List[Def]
    audio: List[str]

    @staticmethod
    def from_dict(obj: Any) -> "PartWord":
        assert isinstance(obj, dict)
        part_word_def = from_list(Def.from_dict, obj.get("def"))
        audio = from_list(from_str, obj.get("audio"))
        return PartWord(part_word_def, audio)

    def to_dict(self) -> dict:
        result: dict = {}
        result["def"] = from_list(lambda x: to_class(Def, x), self.part_word_def)
        result["audio"] = from_list(from_str, self.audio)
        return result


def part_word_from_dict(s: Any) -> PartWord:
    return PartWord.from_dict(s)


def part_word_to_dict(x: PartWord) -> Any:
    return to_class(PartWord, x)
