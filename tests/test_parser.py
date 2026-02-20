from gdalgviz.gdalgviz import split_pipeline, parse_step, parse_step_recursive


def test_split_pipeline():
    res = split_pipeline(
        "gdal vector pipeline ! read in.gpkg ! reproject --dst-crs=EPSG:32632 ! select --fields fid,geom"
    )
    assert len(res) == 3

    res = split_pipeline(
        "gdal vector pipeline read in.gpkg ! reproject --dst-crs=EPSG:32632 ! select --fields fid,geom"
    )
    assert len(res) == 3

    res = split_pipeline(
        "GDAL vector pipeline read in.gpkg ! reproject --dst-crs=EPSG:32632 ! select --fields fid,geom"
    )
    assert len(res) == 3

    res = split_pipeline(
        "GDAL pipeline read in.gpkg ! reproject --dst-crs=EPSG:32632 ! select --fields fid,geom"
    )
    assert len(res) == 3

    res = split_pipeline(
        "gdal raster pipeline read in.gpkg ! reproject --dst-crs=EPSG:32632 ! select --fields fid,geom"
    )
    assert len(res) == 3

    res = split_pipeline(
        "gdal raster pipeline ! read in.gpkg ! reproject --dst-crs=EPSG:32632 ! select --fields fid,geom"
    )
    assert len(res) == 3


def test_parse_step():
    res = parse_step("read in.gpkg")
    assert len(res) == 2
    assert res[0] == "read"
    assert len(res[1]) == 1 and res[1][0] == "in.gpkg"

    res = parse_step(
        "reproject -r mode -d EPSG:4326 --bbox=112,2,116,4.5 --bbox-crs=EPSG:4326 --size 3000,3000"
    )

    assert len(res) == 2
    assert len(res[1]) == 5


def test_parse_step_recursive():

    steps = split_pipeline("""gdal raster pipeline
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
        """)

    step_dicts = [parse_step_recursive(s) for s in steps]

    for d in step_dicts:
        for k, v in d.items():
            print(k, v)

    """
step read n43.tif
step color-map --color-map color_file.txt
step tee
nested [{'step': 'write colored.tif --overwrite'}]
step blend --operator=hsv-value --overlay
nested [{'step': 'read n43.tif'}, {'step': 'hillshade -z 30'}, {'step': 'tee', 'nested': [{'step': 'write hillshade.tif --overwrite'}]}]
step write colored-hillshade.tif --overwrite
    """

    assert len(step_dicts) == 5
    assert len(step_dicts[0]) == 1
    assert len(step_dicts[1]) == 1
    assert len(step_dicts[2]) == 2
    assert len(step_dicts[3]) == 2
    assert len(step_dicts[4]) == 1


if __name__ == "__main__":
    test_split_pipeline()
    test_parse_step()
    test_parse_step_recursive()
    print("Done!")
