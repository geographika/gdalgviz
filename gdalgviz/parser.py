import re
from lark import Lark, Transformer

_PIPELINE_PREFIX_RE = re.compile(
    r"(^\s*gdal\s+(?:raster\s+|vector\s+)?pipeline)(\s+)(?!\s*!)",
    re.IGNORECASE | re.DOTALL,
)


class PipelineTransformer(Transformer):

    def start(self, items):
        return items[0]

    def pipeline(self, items):
        return items  # list of step dicts

    def step(self, items):
        command = items[0]  # string from command rule
        rest = items[1:]  # mix of arg dicts and nested dicts

        args = [x for x in rest if x.get("type") != "nested"]
        nested = [x for x in rest if x.get("type") == "nested"]

        result = {"command": command, "args": args}
        if nested:
            # only one nested block per step? currently supports multiple
            result["nested"] = nested if len(nested) > 1 else nested[0]
        return result

    def command(self, items):
        return " ".join(str(t) for t in items)

    def arg(self, items):
        return items[0]  # unwrap

    def short_arg(self, items):
        flag = str(items[0]).lstrip("-")
        value = items[1] if len(items) > 1 else None
        return {"type": "short_arg", "flag": flag, "value": value}

    def long_arg(self, items):
        flag = str(items[0]).lstrip("-")
        value = items[1] if len(items) > 1 else None
        return {"type": "long_arg", "flag": flag, "value": value}

    def positional(self, items):
        return {"type": "positional", "value": items[0]}

    def value(self, items):
        return items[0]  # already processed by QUOTED_STRING or BARE_VALUE

    def nested(self, items):
        return {"type": "nested", "pipeline": items[0]}

    def NAME(self, token):
        return str(token)

    def SHORT_FLAG(self, token):
        return str(token)

    def LONG_FLAG(self, token):
        return str(token)

    def BARE_VALUE(self, token):
        return str(token)

    def QUOTED_STRING(self, token):
        s = str(token)
        if len(s) >= 2 and s[0] in ('"', "'") and s[-1] == s[0]:
            s = s[1:-1]
        return s


def normalize_pipeline(text: str) -> str:
    """
    Insert a '!' after the pipeline prefix if missing
    """
    return _PIPELINE_PREFIX_RE.sub(r"\1\2! ", text)


def parse_pipeline(command_line):
    command_line = normalize_pipeline(command_line)
    # load grammar from pipeline.lark in the same directory
    parser = Lark.open("pipeline.lark", rel_to=__file__, parser="lalr")
    tree = parser.parse(command_line)
    # print(tree.pretty())

    transformer = PipelineTransformer()
    result = transformer.transform(tree)

    # import pprint
    # pprint.pprint(result)

    return result
