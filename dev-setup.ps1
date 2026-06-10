cd D:\GitHub\gdalgviz

# project creation
# C:\python314\python -m venv .venv
# python -m pip install --upgrade pip

.venv\Scripts\activate.ps1
$GVIZ_PATH = "C:\Program Files\Graphviz\bin"
$env:PATH = "$GVIZ_PATH;$env:PATH"

pip install -e .[dev]
black .
ruff check . --fix
ruff check .
mypy .
pytest tests
gdalgviz ./examples/tee.json ./examples/tee.svg
gdalgviz --pipeline "gdal vector pipeline ! read in.gpkg ! reproject --dst-crs=EPSG:32632 ! select --fields fid,geom" ./examples/pipeline.svg

# tests
pytest

# to update reference images for examples
python tests/test_examples.py --update-references


# test build and deploy
python -m build
python -m twine upload --repository testpypi dist/*

# automatic deployments from GitHub
git tag v0.2.2
git push origin v0.2.2
