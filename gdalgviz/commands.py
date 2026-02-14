# Raster commands
RASTER_COMMANDS = {
    "raster": "Entry point for raster commands",
    "info": "Get information on a raster dataset",
    "as-features": "Create features representing raster pixels",
    "aspect": "Generate an aspect map",
    "blend": "Blend/compose two raster datasets",
    "calc": "Perform raster algebra",
    "clean-collar": "Clean the collar of a raster dataset, removing noise",
    "clip": "Clip a raster dataset",
    "color-map": "Use a grayscale raster to replace the intensity of a RGB/RGBA dataset",
    "compare": "Compare two raster datasets",
    "convert": "Convert a raster dataset",
    "contour": "Builds vector contour lines from a raster elevation model",
    "create": "Create a new raster dataset",
    "edit": "Edit in place a raster dataset",
    "footprint": "Compute the footprint of a raster dataset",
    "fill-nodata": "Fill raster regions by interpolation from edges",
    "hillshade": "Generate a shaded relief map",
    "index": "Create a vector index of raster datasets",
    "materialize": "Materialize a piped dataset on disk to increase efficiency",
    "mosaic": "Build a mosaic, either virtual (VRT) or materialized",
    "neighbors": "Compute the value of each pixel from its neighbors (focal statistics)",
    "nodata-to-alpha": "Replace nodata value(s) with an alpha band",
    "overview": "Manage overviews of a raster dataset",
    "overview add": "Add overviews to a raster dataset",
    "overview delete": "Remove overviews of a raster dataset",
    "overview refresh": "Refresh overviews",
    "pansharpen": "Perform a pansharpen operation",
    "polygonize": "Create a polygon feature dataset from a raster band",
    "pixel-info": "Return information on a pixel of a raster dataset",
    "rgb-to-palette": "Convert a RGB image into a pseudo-color / paletted image",
    "reclassify": "Reclassify a raster dataset",
    "reproject": "Reproject a raster dataset",
    "resize": "Resize a raster dataset without changing the georeferenced extents",
    "roughness": "Generate a roughness map",
    "scale": "Scale the values of the bands of a raster dataset",
    "select": "Select a subset of bands from a raster dataset",
    "set-type": "Modify the data type of bands of a raster dataset",
    "sieve": "Remove small raster polygons",
    "slope": "Generate a slope map",
    "stack": "Combine input bands into a multi-band output, either virtual (VRT) or materialized",
    "tile": "Generate tiles in separate files from a raster dataset",
    "tpi": "Generate a Topographic Position Index (TPI) map",
    "tri": "Generate a Terrain Ruggedness Index (TRI) map",
    "unscale": "Convert scaled values of a raster dataset into unscaled values",
    "update": "Update the destination raster with the content of the input one",
    "viewshed": "Compute the viewshed of a raster dataset",
    "zonal-stats": "Compute raster zonal statistics",
}

# Vector commands
VECTOR_COMMANDS = {
    "vector": "Entry point for vector commands",
    "buffer": "Compute a buffer around geometries of a vector dataset",
    "check-coverage": "Check a polygon coverage for validity",
    "check-geometry": "Check a dataset for invalid or non-simple geometries",
    "clean-coverage": "Remove gaps and overlaps in a polygon dataset",
    "clip": "Clip a vector dataset",
    "concat": "Concatenate vector datasets",
    "convert": "Convert a vector dataset",
    "edit": "Edit metadata of a vector dataset",
    "explode-collections": "Explode geometries of type collection of a vector dataset",
    "filter": "Filter a vector dataset",
    "grid": "Create a regular grid from scattered points",
    "info": "Get information on a vector dataset",
    "index": "Create a vector index of vector datasets",
    "layer-algebra": "Perform algebraic operation between 2 layers",
    "make-point": "Create point geometries from coordinate fields",
    "make-valid": "Fix validity of geometries of a vector dataset",
    "materialize": "Materialize a piped dataset on disk to increase efficiency",
    "partition": "Partition a vector dataset into multiple files",
    "rasterize": "Burn vector geometries into a raster",
    "reproject": "Reproject a vector dataset",
    "segmentize": "Segmentize geometries of a vector dataset",
    "select": "Select a subset of fields from a vector dataset",
    "set-field-type": "Modify the type of a field of a vector dataset",
    "set-geom-type": "Modify the geometry type of a vector dataset",
    "simplify": "Simplify geometries of a vector dataset",
    "simplify-coverage": "Simplify shared boundaries of a polygonal vector dataset",
    "sort": "Spatially sort a vector dataset",
    "sql": "Apply SQL statement(s) to a dataset",
    "swap-xy": "Swap X and Y coordinates of geometries of a vector dataset",
    "update": "Update an existing vector dataset with an input vector dataset",
}

MDIM_COMMANDS = {
    "mdim": "Entry point for multidimensional commands",
    "mdim info": "Get information on a multidimensional dataset",
    "mdim convert": "Convert a multidimensional dataset",
    "mdim mosaic": "Build a mosaic, either virtual (VRT) or materialized, from multidimensional datasets",
}


DATASET_COMMANDS = {
    "dataset": "Entry point for dataset management commands",
    "dataset identify": "Identify driver opening dataset(s)",
    "dataset check": "Check whether there are errors when reading the content of a dataset",
    "dataset copy": "Copy files of a dataset",
    "dataset rename": "Rename files of a dataset",
    "dataset delete": "Delete dataset(s)",
}


VSI_COMMANDS = {
    "vsi": "Entry point for GDAL Virtual System Interface (VSI) commands",
    "vsi copy": "Copy files located on GDAL Virtual System Interface (VSI)",
    "vsi delete": "Delete files located on GDAL Virtual System Interface (VSI)",
    "vsi list": "List files of one of the GDAL Virtual System Interface (VSI)",
    "vsi move": "Move/rename a file/directory located on GDAL Virtual System Interface (VSI)",
    "vsi sync": "Synchronize source and target file/directory located on GDAL Virtual System Interface (VSI)",
    "vsi sozip": "SOZIP (Seek-Optimized ZIP) related commands",
}

DRIVER_COMMANDS = {
    "driver gpkg repack": "Repack/vacuum in-place a GeoPackage dataset",
    "driver gti create": "Create an index of raster datasets compatible with the GDAL Tile Index (GTI) driver",
    "driver openfilegdb repack": "Repack in-place a FileGeodatabase dataset",
    "driver parquet create-metadata-file": "Create the _metadata file for a partitioned Parquet dataset",
    "driver pdf list-layer": "Return the list of layers of a PDF file",
}


COMMANDS = {}
COMMANDS.update(RASTER_COMMANDS)
COMMANDS.update(MDIM_COMMANDS)
COMMANDS.update(DATASET_COMMANDS)
COMMANDS.update(VSI_COMMANDS)
COMMANDS.update(DRIVER_COMMANDS)
