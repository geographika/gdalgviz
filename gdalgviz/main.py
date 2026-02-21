from pathlib import Path
from typing import List, Dict, Optional
from graphviz import Digraph
from gdalgviz.commands import RASTER_COMMANDS
from gdalgviz.parser import parse_pipeline

# supported by Graphviz
VALID_FORMATS = ["svg", "png", "pdf", "jpg"]
# URL to GDAL command documentation
GDAL_DOCS_URL_TEMPLATE = (
    "https://gdal.org/en/latest/programs/gdal_{cmd_type}_{command}.html"
)
# general commands that don't have dedicated docs pages
GDAL_OPERATORS = ("read", "write", "tee")


def _is_pipeline_header(step: Dict) -> bool:
    """
    Return True if this step is just a pipeline declaration with no real args
    """
    cmd = step.get("command", "").strip().lower()
    return bool(cmd == "gdal")


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


def _run_nested_pipeline(
    g: Digraph,
    steps: List[Dict],
    parent_ids: List[Optional[str]],
    node_counter: List[int],
    pipeline_type: Optional[str],
) -> List[str]:
    """Chain a list of steps sequentially, returning the final node ids."""
    current_parents = parent_ids
    for step in steps:
        current_parents = add_step_node(
            g,
            step,
            parent_ids=current_parents,
            node_counter=node_counter,
            pipeline_type=pipeline_type,
        )
    return current_parents


def add_step_node(
    g: Digraph,
    step_dict: Dict,
    parent_ids: List[Optional[str]],
    node_counter: List[int],
    pipeline_type: Optional[str] = None,
) -> List[str]:
    cmd = _extract_cmd(step_dict)
    args = step_dict.get("args", [])
    label = step_label_html(cmd, args)

    node_id = str(node_counter[0])
    node_counter[0] += 1

    cmd_type = pipeline_type or get_command_type(cmd)

    # create the node
    if cmd_type and cmd.lower() not in GDAL_OPERATORS:
        cmd_cleaned = cmd.replace("-", "_")
        url = GDAL_DOCS_URL_TEMPLATE.format(cmd_type=cmd_type, command=cmd_cleaned)
        g.node(node_id, label=label, URL=url, tooltip=url, target="_blank")
    else:
        g.node(node_id, label=label)

    # connect to all parents
    for pid in parent_ids:
        if pid is not None:
            g.edge(pid, node_id)

    # handle nested block
    nested = step_dict.get("nested")
    if not nested:
        return [node_id]

    nested_pipeline = nested["pipeline"]
    nested_steps = (
        nested_pipeline if isinstance(nested_pipeline, list) else [nested_pipeline]
    )

    if cmd == "tee":
        # tee: nested steps are dead-end side outputs, main flow continues
        _run_nested_pipeline(
            g,
            nested_steps,
            parent_ids=[node_id],
            node_counter=node_counter,
            pipeline_type=pipeline_type,
        )
        return [node_id]

    # blend/overlay style: nested pipeline feeds INTO this node
    final_ids = _run_nested_pipeline(
        g,
        nested_steps,
        parent_ids=[],
        node_counter=node_counter,
        pipeline_type=pipeline_type,
    )
    for nid in final_ids:
        g.edge(nid, node_id)

    return [node_id]


def _html_escape(text: str) -> str:
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def step_label_html(cmd: str, args: List[Dict]) -> str:
    """
    Create an HTML-like Graphviz label for a node
    """
    rows = [f'<TR><TD BGCOLOR="#cfe2ff" ALIGN="CENTER"><B>{cmd}</B></TD></TR>']

    for arg in args:
        t = arg["type"]
        if t == "positional":
            text = _html_escape(arg["value"])
        elif t == "short_arg":
            val = f" {arg['value']}" if arg["value"] else ""
            text = _html_escape(f"-{arg['flag']}{val}")
        elif t == "long_arg":
            val = arg["value"] or ""
            if val.startswith("="):
                text = _html_escape(f"--{arg['flag']}{val}")
            elif val:
                text = _html_escape(f"--{arg['flag']} {val}")
            else:
                text = _html_escape(f"--{arg['flag']}")
        else:
            continue
        rows.append(f'<TR><TD ALIGN="LEFT">{text}</TD></TR>')

    return f"""<
<TABLE BORDER="0" CELLBORDER="1" CELLSPACING="0" CELLPADDING="6">
    {''.join(rows)}
</TABLE>
>"""


def _extract_cmd(step_dict: Dict) -> str:
    """Get the operative command word from a step dict (last word of command field)."""
    return step_dict["command"].split()[-1]


def workflow_diagram(
    steps: List[Dict],
    output_format: str,
    pipeline_type: Optional[str] = None,
    title: str = "GDALG Workflow",
) -> Digraph:
    """Build a Graphviz diagram from a structured pipeline dict list."""

    display_steps = steps
    if steps and _is_pipeline_header(steps[0]):
        display_steps = steps[1:]

    g = Digraph(
        name=title,
        format=output_format,
        graph_attr={"rankdir": "LR"},
    )
    g.attr("node", shape="plain", fontname="Helvetica")

    node_counter = [0]
    last_ids: List[str] = []

    for step in display_steps:
        last_ids = add_step_node(
            g,
            step,
            parent_ids=last_ids or [None],
            node_counter=node_counter,
            pipeline_type=pipeline_type,
        )

    return g


def detect_pipeline_type(steps: List[Dict]) -> Optional[str]:
    """
    Infer pipeline type (raster/vector) from the first step's command.
    e.g. 'gdal raster pipeline' -> 'raster'
    """
    if not steps:
        return None
    first_cmd = steps[0].get("command", "").lower()
    for word in first_cmd.split():
        if word in ("raster", "vector"):
            return word
    return None


def generate_diagram(pipeline: str, output_fn: str):
    """
    Parse a GDAL pipeline string and generate a workflow diagram.
    """
    output_format = get_output_format(output_fn, VALID_FORMATS)

    # parse into structured dict using lark
    steps = parse_pipeline(pipeline)

    pipeline_type = detect_pipeline_type(steps)
    diagram = workflow_diagram(steps, output_format, pipeline_type)

    output_stem = Path(output_fn).with_suffix("")
    diagram.render(output_stem, cleanup=True)


if __name__ == "__main__":
    pipeline = "gdal vector pipeline ! read in.tif ! reproject --dst-crs=EPSG:32632 ! select --fields fid,geom"
    output_fn = "./examples/raster.svg"
    generate_diagram(pipeline, output_fn)
    print("Done!")
