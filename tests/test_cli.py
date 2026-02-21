from unittest.mock import patch
from gdalgviz import cli
from gdalgviz.main import DOCS_ROOT
import pytest

PIPELINE_STR = "gdal vector pipeline ! read in.gpkg ! reproject --dst-crs=EPSG:32632"


def test_main_with_pipeline_string(tmp_path):
    """Test passing a raw pipeline string via --pipeline."""
    output_file = tmp_path / "output.svg"
    with patch("gdalgviz.cli.generate_diagram") as mock_generate:
        mock_generate.return_value = 0
        exit_code = cli.main(["--pipeline", PIPELINE_STR, str(output_file)])
    assert exit_code == 0
    mock_generate.assert_called_once_with(
        pipeline=PIPELINE_STR,
        output_fn=str(output_file),
        vertical=False,
        fontname="Helvetica",
        header_color="#cfe2ff",
        docs_root=DOCS_ROOT,
    )


def test_main_with_file(tmp_path):
    """Test passing a real text file as input."""
    input_file = tmp_path / "pipeline.txt"
    output_file = tmp_path / "output.svg"
    input_file.write_text(PIPELINE_STR)
    with patch("gdalgviz.cli.generate_diagram") as mock_generate:
        mock_generate.return_value = 0
        exit_code = cli.main([str(input_file), str(output_file)])
    assert exit_code == 0
    mock_generate.assert_called_once_with(
        pipeline=PIPELINE_STR,
        output_fn=str(output_file),
        vertical=False,
        fontname="Helvetica",
        header_color="#cfe2ff",
        docs_root=DOCS_ROOT,
    )


def test_main_with_missing_file(tmp_path):
    """Test that CLI returns error code 1 when input file does not exist."""
    output_file = tmp_path / "output.svg"
    missing_file = tmp_path / "does_not_exist.txt"
    with patch("gdalgviz.cli.generate_diagram") as mock_generate:
        exit_code = cli.main([str(missing_file), str(output_file)])
    assert exit_code == 1
    mock_generate.assert_not_called()


def test_main_vertical_flag(tmp_path):
    """Test that --vertical is passed through to generate_diagram."""
    output_file = tmp_path / "output.svg"
    with patch("gdalgviz.cli.generate_diagram") as mock_generate:
        mock_generate.return_value = 0
        exit_code = cli.main(
            ["--pipeline", PIPELINE_STR, "--vertical", str(output_file)]
        )
    assert exit_code == 0
    mock_generate.assert_called_once_with(
        pipeline=PIPELINE_STR,
        output_fn=str(output_file),
        vertical=True,
        fontname="Helvetica",
        header_color="#cfe2ff",
        docs_root=DOCS_ROOT,
    )


def test_main_custom_font(tmp_path):
    """Test that --font is passed through to generate_diagram."""
    output_file = tmp_path / "output.svg"
    with patch("gdalgviz.cli.generate_diagram") as mock_generate:
        mock_generate.return_value = 0
        exit_code = cli.main(
            ["--pipeline", PIPELINE_STR, "--font", "Arial", str(output_file)]
        )
    assert exit_code == 0
    mock_generate.assert_called_once_with(
        pipeline=PIPELINE_STR,
        output_fn=str(output_file),
        vertical=False,
        fontname="Arial",
        header_color="#cfe2ff",
        docs_root=DOCS_ROOT,
    )


def test_main_custom_docs_root(tmp_path):
    """Test that --docs-root is passed through to generate_diagram."""
    output_file = tmp_path / "output.svg"
    custom_root = "https://my-mirror.example.com/gdal/programs"
    with patch("gdalgviz.cli.generate_diagram") as mock_generate:
        mock_generate.return_value = 0
        exit_code = cli.main(
            ["--pipeline", PIPELINE_STR, "--docs-root", custom_root, str(output_file)]
        )
    assert exit_code == 0
    mock_generate.assert_called_once_with(
        pipeline=PIPELINE_STR,
        output_fn=str(output_file),
        vertical=False,
        fontname="Helvetica",
        header_color="#cfe2ff",
        docs_root=custom_root,
    )


def test_main_all_options(tmp_path):
    """Test combining all optional flags together."""
    output_file = tmp_path / "output.svg"
    custom_root = "https://my-mirror.example.com/gdal/programs"
    with patch("gdalgviz.cli.generate_diagram") as mock_generate:
        mock_generate.return_value = 0
        exit_code = cli.main(
            [
                "--pipeline",
                PIPELINE_STR,
                "--vertical",
                "--font",
                "Courier",
                "--docs-root",
                custom_root,
                str(output_file),
            ]
        )
    assert exit_code == 0
    mock_generate.assert_called_once_with(
        pipeline=PIPELINE_STR,
        output_fn=str(output_file),
        vertical=True,
        fontname="Courier",
        header_color="#cfe2ff",
        docs_root=custom_root,
    )


def test_main_custom_header_color(tmp_path):
    """Test that --header-color is passed through to generate_diagram."""
    output_file = tmp_path / "output.svg"
    with patch("gdalgviz.cli.generate_diagram") as mock_generate:
        mock_generate.return_value = 0
        exit_code = cli.main(
            [
                "--pipeline",
                PIPELINE_STR,
                "--header-color",
                "#ff0000",
                str(output_file),
            ]
        )
    assert exit_code == 0
    mock_generate.assert_called_once_with(
        pipeline=PIPELINE_STR,
        output_fn=str(output_file),
        vertical=False,
        fontname="Helvetica",
        docs_root=DOCS_ROOT,
        header_color="#ff0000",
    )


def test_main_invalid_header_color(tmp_path):
    """Test that an invalid hex color returns an error."""
    output_file = tmp_path / "output.svg"
    with patch("gdalgviz.cli.generate_diagram") as mock_generate:
        with pytest.raises(SystemExit) as exc_info:
            cli.main(
                [
                    "--pipeline",
                    PIPELINE_STR,
                    "--header-color",
                    "notacolor",
                    str(output_file),
                ]
            )
    assert exc_info.value.code != 0
    mock_generate.assert_not_called()


def test_main_default_header_color(tmp_path):
    """Test that the default header color is used when not specified."""
    output_file = tmp_path / "output.svg"
    with patch("gdalgviz.cli.generate_diagram") as mock_generate:
        mock_generate.return_value = 0
        exit_code = cli.main(["--pipeline", PIPELINE_STR, str(output_file)])
    assert exit_code == 0
    mock_generate.assert_called_once_with(
        pipeline=PIPELINE_STR,
        output_fn=str(output_file),
        vertical=False,
        fontname="Helvetica",
        docs_root=DOCS_ROOT,
        header_color="#cfe2ff",
    )
