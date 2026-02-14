from unittest.mock import patch

from gdalgviz import cli  # assuming cli.py is inside gdalgviz/ folder


def test_main_with_pipeline_string(tmp_path):
    """
    Test passing a raw pipeline string via --pipeline
    """
    output_file = tmp_path / "output.svg"
    pipeline_str = "gdal_translate input.tif output.tif"

    with patch("gdalgviz.cli.generate_diagram") as mock_generate:
        mock_generate.return_value = 0

        argv = ["--pipeline", pipeline_str, str(output_file)]
        exit_code = cli.main(argv)

    # Check that the CLI returned the mocked exit code
    assert exit_code == 0

    # Check that generate_diagram was called with the correct args
    mock_generate.assert_called_once_with(
        pipeline=pipeline_str, output_fn=str(output_file)
    )


def test_main_with_missing_file(tmp_path):
    """
    Test that CLI returns an error code when a file does not exist
    """
    output_file = tmp_path / "output.svg"
    missing_file = tmp_path / "does_not_exist.txt"

    with patch("gdalgviz.cli.generate_diagram") as mock_generate:
        argv = [str(missing_file), str(output_file)]
        exit_code = cli.main(argv)

    # Should return 1 because the input file does not exist
    assert exit_code == 1
    # generate_diagram should not be called
    mock_generate.assert_not_called()


def test_main_with_file(tmp_path):
    """
    Test passing a real text file as input
    """
    input_file = tmp_path / "pipeline.txt"
    output_file = tmp_path / "output.svg"
    pipeline_content = "gdal_translate input.tif output.tif"

    input_file.write_text(pipeline_content)

    with patch("gdalgviz.cli.generate_diagram") as mock_generate:
        mock_generate.return_value = 0

        argv = [str(input_file), str(output_file)]
        exit_code = cli.main(argv)

    assert exit_code == 0
    mock_generate.assert_called_once_with(
        pipeline=pipeline_content, output_fn=str(output_file)
    )
