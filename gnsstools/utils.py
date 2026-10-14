import re


def camel2snake(string: str) -> str:
    compiled = re.compile("((?<=[a-z0-9])[A-Z]|(?!^)[A-Z](?=[a-z]))")
    # For case like "dX2" -> "dx2"
    if string[0] == "d" and string[1].isupper():
        return "d" + compiled.sub(r"_\1", string[1:]).lower()
    # For camel case
    return compiled.sub(r"_\1", string).lower()
