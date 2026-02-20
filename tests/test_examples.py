from gdalgviz.main import generate_diagram
from gdalgviz.parser import parse_pipeline
from pathlib import Path
import re
import sys
import json


UPDATE_REFERENCES = "--update-references" in sys.argv
OUTPUT_DIR = Path("./tests/output")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

REFERENCE_DIR = Path("./tests/reference")


def normalize_svg(svg_text: str) -> str:
    # collapse whitespace
    svg_text = re.sub(r"\s+", " ", svg_text)
    # remove XML comments
    svg_text = re.sub(r"<!--.*?-->", "", svg_text)
    # strip leading/trailing whitespace
    return svg_text.strip()


def assert_pipeline_equal(steps: list, name: str):
    output_path = OUTPUT_DIR / f"{name}.json"
    reference_path = REFERENCE_DIR / f"{name}.json"

    output_json = json.dumps(steps, indent=2, sort_keys=True)
    output_path.write_text(output_json, encoding="utf-8")

    if UPDATE_REFERENCES:
        reference_path.write_text(output_json, encoding="utf-8")
        print(f"  Updated reference: {reference_path.name}")
        return

    reference_json = reference_path.read_text(encoding="utf-8")
    assert output_json == reference_json, (
        f"Pipeline mismatch for {name}:\n"
        f"  output:    {output_path}\n"
        f"  reference: {reference_path}"
    )


def assert_svg_equal(output_path: Path, reference_path: Path):
    """
    graphviz produces different outputs depending on OS and Graphviz version
    """
    if UPDATE_REFERENCES:
        import shutil

        shutil.copy(output_path, reference_path)
        print(f"  Updated reference: {reference_path.name}")
        return

    # skip this test in CI because of variability in Graphviz output

    # output = normalize_svg(output_path.read_text(encoding="utf-8"))
    # reference = normalize_svg(reference_path.read_text(encoding="utf-8"))
    # assert (
    #     output == reference
    # ), f"SVG mismatch:\n  output:    {output_path}\n  reference: {reference_path}"


def test_vector_pipeline():
    output_path = OUTPUT_DIR / "test_vector_pipeline.svg"
    pipeline = "gdal vector pipeline ! read in.gpkg ! reproject --dst-crs=EPSG:32632 ! select --fields fid,geom"
    steps = parse_pipeline(pipeline)
    assert_pipeline_equal(steps, "test_vector_pipeline")
    generate_diagram(pipeline, str(output_path))
    assert_svg_equal(output_path, REFERENCE_DIR / "test_vector_pipeline.svg")


def test_vector_pipeline_with_bang():
    output_path = OUTPUT_DIR / "test_vector_pipeline_with_bang.svg"
    pipeline = "gdal vector pipeline ! read in.gpkg ! reproject --dst-crs=EPSG:32632 ! select --fields fid,geom"
    steps = parse_pipeline(pipeline)
    assert_pipeline_equal(steps, "test_vector_pipeline_with_bang")
    generate_diagram(pipeline, str(output_path))
    assert_svg_equal(output_path, REFERENCE_DIR / "test_vector_pipeline_with_bang.svg")


def test_vector_pipeline_without_bang():
    output_path = OUTPUT_DIR / "test_vector_pipeline_without_bang.svg"
    pipeline = "gdal vector pipeline read in.gpkg ! reproject --dst-crs=EPSG:32632 ! select --fields fid,geom"
    steps = parse_pipeline(pipeline)
    assert_pipeline_equal(steps, "test_vector_pipeline_without_bang")
    generate_diagram(pipeline, str(output_path))
    assert_svg_equal(
        output_path, REFERENCE_DIR / "test_vector_pipeline_without_bang.svg"
    )


def test_vector_pipeline_uppercase_gdal():
    output_path = OUTPUT_DIR / "test_vector_pipeline_uppercase_gdal.svg"
    pipeline = "GDAL vector pipeline read in.gpkg ! reproject --dst-crs=EPSG:32632 ! select --fields fid,geom"
    steps = parse_pipeline(pipeline)
    assert_pipeline_equal(steps, "test_vector_pipeline_uppercase_gdal")
    generate_diagram(pipeline, str(output_path))
    assert_svg_equal(
        output_path, REFERENCE_DIR / "test_vector_pipeline_uppercase_gdal.svg"
    )


def test_gdal_pipeline_no_type():
    output_path = OUTPUT_DIR / "test_gdal_pipeline_no_type.svg"
    pipeline = "GDAL pipeline read in.gpkg ! reproject --dst-crs=EPSG:32632 ! select --fields fid,geom"
    steps = parse_pipeline(pipeline)
    assert_pipeline_equal(steps, "test_gdal_pipeline_no_type")
    generate_diagram(pipeline, str(output_path))
    assert_svg_equal(output_path, REFERENCE_DIR / "test_gdal_pipeline_no_type.svg")


def test_raster_pipeline_without_bang():
    output_path = OUTPUT_DIR / "test_raster_pipeline_without_bang.svg"
    pipeline = "gdal raster pipeline read in.gpkg ! reproject --dst-crs=EPSG:32632 ! select --fields fid,geom"
    steps = parse_pipeline(pipeline)
    assert_pipeline_equal(steps, "test_raster_pipeline_without_bang")
    generate_diagram(pipeline, str(output_path))
    assert_svg_equal(
        output_path, REFERENCE_DIR / "test_raster_pipeline_without_bang.svg"
    )


def test_raster_pipeline_with_bang():
    output_path = OUTPUT_DIR / "test_raster_pipeline_with_bang.svg"
    pipeline = "gdal raster pipeline ! read in.gpkg ! reproject --dst-crs=EPSG:32632 ! select --fields fid,geom"
    steps = parse_pipeline(pipeline)
    assert_pipeline_equal(steps, "test_raster_pipeline_with_bang")
    generate_diagram(pipeline, str(output_path))
    assert_svg_equal(output_path, REFERENCE_DIR / "test_raster_pipeline_with_bang.svg")


def test_nested_input():
    output_path = OUTPUT_DIR / "test_nested_input.svg"
    pipeline = """gdal pipeline read n43.tif !
                color-map --color-map color_file.txt !
                blend --operator=hsv-value --overlay
                    [ read n43.tif ! hillshade -z 30 ] !
                write out.tif --overwrite
        """
    steps = parse_pipeline(pipeline)
    assert_pipeline_equal(steps, "test_nested_input")
    generate_diagram(pipeline, str(output_path))
    assert_svg_equal(output_path, REFERENCE_DIR / "test_nested_input.svg")


def test_nested_output():
    output_path = OUTPUT_DIR / "test_nested_output.svg"
    pipeline = """gdal raster pipeline
            ! read n43.tif
            ! color-map --color-map color_file.txt
            ! tee
                [ write colored.tif --overwrite ] 
            ! blend --operator=hsv-value --overlay
                [
                    read n43.tif
                    ! hillshade -z 30
                    ! tee
                        [
                            write hillshade.tif --overwrite
                        ]
                ]
            ! write colored-hillshade.tif --overwrite
        """
    steps = parse_pipeline(pipeline)
    assert_pipeline_equal(steps, "test_nested_output")
    generate_diagram(pipeline, str(output_path))
    assert_svg_equal(output_path, REFERENCE_DIR / "test_nested_output.svg")


def test_expressions():
    output_path = OUTPUT_DIR / "test_expressions.svg"
    pipeline = """gdal pipeline 
    ! read input.tif 
    ! slope --unit percent 
    ! reclassify -m "[0,15)=NO_DATA; [15,20)=1; [20,1000)=2; DEFAULT=NO_DATA" 
    ! polygonize -c ! write --format OpenFileGDB --update --output-layer slope2026_percent.gdb
    """
    steps = parse_pipeline(pipeline)
    assert_pipeline_equal(steps, "test_expressions")
    generate_diagram(pipeline, str(output_path))
    assert_svg_equal(output_path, REFERENCE_DIR / "test_expressions.svg")


if __name__ == "__main__":
    test_vector_pipeline()
    test_vector_pipeline_with_bang()
    test_vector_pipeline_without_bang()
    test_vector_pipeline_uppercase_gdal()
    test_gdal_pipeline_no_type()
    test_raster_pipeline_without_bang()
    test_raster_pipeline_with_bang()
    test_nested_input()
    test_nested_output()
    test_expressions()
    print("Done!")
