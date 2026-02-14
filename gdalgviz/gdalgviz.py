import shlex
from pathlib import Path
from typing import List, Dict, Optional
from graphviz import Digraph
from .commands import RASTER_COMMANDS

# supported by Graphviz
VALID_FORMATS = ["svg", "png", "pdf", "jpg"]
# URL to GDAL command documentation
GDAL_DOCS_URL_TEMPLATE = (
    "https://gdal.org/en/latest/programs/gdal_{cmd_type}_{command}.html"
)
# general commands that don't have dedicated docs pages
GDAL_OPERATORS = ("read", "write", "tee")


def get_output_format(filename: str, valid_formats: list[str]) -> str:
    """
    Infer output format from filename extension and validate it.
    Raises ValueError if the extension is invalid.
    """
    ext = Path(filename).suffix.lower().lstrip(".")  # e.g., ".svg" -> "svg"

    if ext not in valid_formats:
        raise ValueError(
            f"Invalid output format '{ext}'. Must be one of {valid_formats}"
        )

    return ext


def get_command_type(cmd: str):
    """
    Get the command type (raster, vector, etc.)
    Take the first match if different types use the same name
    e.g. "read" exists in both raster and vector pipelines

    TODO add other types
    """

    if cmd in RASTER_COMMANDS:
        return "raster"
    else:
        return "vector"


def add_step_node(
    g: Digraph,
    step_dict: Dict[str, any],
    parent_ids: List[Optional[str]],
    node_counter: List[int],
    pipeline_type: Optional[str] = None,
) -> List[str]:
    step_str = step_dict["step"]
    cmd, args = parse_step(step_str)
    label = step_label_html(cmd, args)

    node_id = str(node_counter[0])
    node_counter[0] += 1

    if pipeline_type:
        cmd_type = pipeline_type
    else:
        cmd_type = get_command_type(cmd)

    # create the node
    if cmd_type and cmd.lower() not in GDAL_OPERATORS:
        cmd_cleaned = cmd.replace("-", "_")
        url = GDAL_DOCS_URL_TEMPLATE.format(cmd_type=cmd_type, command=cmd_cleaned)
        g.node(node_id, label=label, URL=url, tooltip=url)
    else:
        g.node(node_id, label=label)

    # connect this node to all parents
    for pid in parent_ids:
        if pid is not None:
            g.edge(pid, node_id)

    nested_steps = step_dict.get("nested", [])

    if not nested_steps:
        return [node_id]

    # tee splits into two paths
    if cmd == "tee":
        # tee: nested steps are dead-end outputs
        for nested in nested_steps:
            add_step_node(
                g,
                nested,
                parent_ids=[node_id],
                node_counter=node_counter,
                pipeline_type=pipeline_type,
            )
        # tee itself continues to next step
        return [node_id]

    # normal nested pipeline: one independent sub-pipeline
    # start with no inflows
    nested_parent_ids = []

    for nested in nested_steps:
        nested_parent_ids = add_step_node(
            g,
            nested,
            parent_ids=nested_parent_ids,  # chain sequentially
            node_counter=node_counter,
            pipeline_type=pipeline_type,
        )

    # Final nested step(s) feed into this parent node
    for nid in nested_parent_ids:
        g.edge(nid, node_id)

    return [node_id]


def parse_step_recursive(step: str):
    if "[" in step and "]" in step:
        # extract the inner block
        before, inner = step.split("[", 1)
        inner, after = inner.rsplit("]", 1)
        # recurse
        nested_steps = split_pipeline(inner)
        return {
            "step": before.strip(),
            "nested": [parse_step_recursive(s) for s in nested_steps],
        }
    else:
        return {"step": step.strip()}


def parse_step(step: str):
    """
    Split a step into command and grouped arguments.
    Handles arguments in the following forms:

    - -r mode
    - --size 3000,3000
    - --bbox=112,2,116,4.5
    - --dst-crs=EPSG:32632
    """
    tokens = shlex.split(step)
    if not tokens:
        return "", []

    cmd = tokens[0]
    args = []
    i = 1

    while i < len(tokens):
        token = tokens[i]

        # Flag that already includes a value (--x=y)
        if token.startswith("-") and "=" in token:
            args.append(token)
            i += 1

        # Flag that may consume the next token
        elif token.startswith("-"):
            if i + 1 < len(tokens) and not tokens[i + 1].startswith("-"):
                args.append(f"{token} {tokens[i + 1]}")
                i += 2
            else:
                args.append(token)
                i += 1

        else:
            args.append(token)
            i += 1

    return cmd, args


def step_label_html(cmd, args):
    """
    Create an HTML-like Graphviz label for a node
    """

    # add the command as the title
    rows = [f'<TR><TD BGCOLOR="#cfe2ff" ALIGN="CENTER"><B>{cmd}</B></TD></TR>']

    # add the arguments in the table below
    for arg in args:
        rows.append(f'<TR><TD ALIGN="LEFT">{arg}</TD></TR>')

    # wrap everything in a <TABLE>
    # the outer < > are required for Graphviz HTML labels
    return f"""<
<TABLE BORDER="0" CELLBORDER="1" CELLSPACING="0" CELLPADDING="6">
    {''.join(rows)}
</TABLE>
>"""


def workflow_diagram(
    steps, output_format: str, pipeline_type=None, title: str = "GDALG Workflow"
):
    g = Digraph(
        name=title,
        format=output_format,
        graph_attr={"rankdir": "LR"},  # Left - Right "TB" Top - Bottom
    )

    g.attr(
        "node",
        shape="plain",  # required for HTML labels
        fontname="Helvetica",
    )

    node_counter = [0]
    # parse steps recursively first
    step_dicts = [parse_step_recursive(s) for s in steps]

    # add all nodes recursively
    last_ids = []  # keeps track of the last nodes at the top level

    for sd in step_dicts:
        last_ids = add_step_node(
            g,
            sd,
            parent_ids=last_ids or [None],
            node_counter=node_counter,
            pipeline_type=pipeline_type,
        )

    return g


def tokenize(text: str):
    tokens = text.lstrip().split()
    lowered = [t.lower() for t in tokens]
    return tokens, lowered


def strip_prefix(text: str) -> str:
    """
    Remove any leading GDAL pipeline prefix
    """
    tokens, lowered = tokenize(text)

    prefixes = [
        ["gdal", "vector", "pipeline"],
        ["gdal", "raster", "pipeline"],
        ["gdal", "pipeline"],
    ]

    for prefix in prefixes:
        if lowered[: len(prefix)] == prefix:
            return " ".join(tokens[len(prefix) :])

    return text


def detect_pipeline_type(text: str) -> Optional[str]:
    """
    Return 'raster' or 'vector' if the second word matches.
    Otherwise return None.
    """
    _, lowered = tokenize(text)

    if len(lowered) >= 2 and lowered[1] in ("raster", "vector"):
        return lowered[1]

    return None


def split_pipeline(command_line: str) -> List[str]:
    """
    Split a GDAL pipeline command_line into steps, handling nested brackets.
    Returns a list where nested pipelines are represented as sublists.
    """

    command_line = strip_prefix(command_line)

    steps = []
    current = ""
    stack = []  # track open brackets
    i = 0
    while i < len(command_line):
        c = command_line[i]

        if c == "[":
            stack.append("[")
            current += c
        elif c == "]":
            stack.pop()
            current += c
        elif c == "!" and not stack:
            # end of step at this level
            step = current.strip()
            if step:
                steps.append(step)
            current = ""
        else:
            current += c
        i += 1

    if current.strip():
        steps.append(current.strip())

    return steps


def generate_diagram(pipeline: str, output_fn: str):
    """
    Generate a workflow diagram from a GDAL pipeline command line and save
    it to the specified output file.
    """

    output_format = get_output_format(output_fn, VALID_FORMATS)
    pipeline_type = detect_pipeline_type(pipeline)
    steps = split_pipeline(pipeline)

    diagram = workflow_diagram(steps, output_format, pipeline_type)
    # remove extension or it gets added twice
    output_file = Path(output_fn)
    output_stem = output_file.with_suffix("")
    diagram.render(output_stem, cleanup=True)


if __name__ == "__main__":
    pipeline = "gdal vector pipeline ! read in.tif ! reproject --dst-crs=EPSG:32632 ! select --fields fid,geom"
    output_fn = "./examples/raster.svg"
    generate_diagram(pipeline, output_fn)
    print("Done!")
