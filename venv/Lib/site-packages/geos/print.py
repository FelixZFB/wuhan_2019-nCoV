"""
Module for printing maps / exporting them as pdf
"""

from geos.geometry import *
import urllib.request
from urllib.error import URLError
from PIL import Image, ImageDraw
from geos import app
from tempfile import NamedTemporaryFile
from multiprocessing import Pool
import pkg_resources

TILE_SIZE = 256  # px
# some tile servers block requests noch coming from a Browser
USER_AGENT = 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, ' \
             'like Gecko) Chrome/35.0.1916.153 Safari/537.36 SE 2.X MetaSr 1.0'
N_DOWNLOAD_WORKERS = 16

# set default user agent
opener = urllib.request.build_opener()
opener.addheaders = [('User-agent', USER_AGENT)]
urllib.request.install_opener(opener)


class MapPrintError(Exception):
    pass


def dpi_to_dpmm(dpi):
    """
    Convert dpi (dots per inch) to dpmm (dots per millimeter)

    Args:
        dpi (int):

    Returns:
        float: dots per millimeter
    """
    return dpi / 25.4


def print_map(map_source, x, y, zoom=14, width=297, height=210, dpi=300, format="pdf"):
    """
    Download map tiles and stitch them together in a single image, ready for printing.

    Args:
        map_source (MapSource): Map to download
        x (float): map center x-coordinate in Mercator projection (EPSG:4326)
        y (float): map center y-coordinate in Mercator projection (EPSG:4326)
        zoom (int): tile zoom level to use for printing
        width (float): page width in mm
        height (float): page height in mm
        dpi (int): resolution in dots per inch
        format (str): output format. Anything supported by ``Pillow.Image.save``. E.g. "pdf", "jpeg", "png".

    Returns:
        str: path of temporary output file.

    """
    bbox = get_print_bbox(x, y, zoom, width, height, dpi)
    tiles = [
        get_tiles(tile_layer, bbox) for tile_layer in map_source.layers if
        tile_layer.min_zoom <= zoom <= tile_layer.max_zoom
        ]
    img = stitch_map(tiles, width, height, bbox, dpi)
    outfile = NamedTemporaryFile(delete=False)
    img.save(outfile, format, quality=100, dpi=(dpi, dpi))
    outfile.close()
    return outfile.name


def get_print_bbox(x, y, zoom, width, height, dpi):
    """
    Calculate the tile bounding box based on position, map size and resolution.

    The function returns the next larger tile-box, that covers the specified
    page size in mm.

    Args:
        x (float): map center x-coordinate in Mercator projection (EPSG:4326)
        y (float): map center y-coordinate in Mercator projection (EPSG:4326)
        zoom (int): tile zoom level to use for printing
        width (float): page width in mm
        height (float): page height in mm
        dpi (int): resolution in dots per inch

    Returns:
        GridBB: Bounding box of the map in TileCoordinates.

    >>> str(get_print_bbox(4164462.1505763642, 985738.7965919945, 14, 297, 150, 120))
    '<tile min: <zoom: 14, x: 9891, y: 7786>, max: <zoom: 14, x: 9897, y: 7790>>'
    """
    tiles_h = width * dpi_to_dpmm(dpi) / TILE_SIZE
    tiles_v = height * dpi_to_dpmm(dpi) / TILE_SIZE
    mercator_coords = MercatorCoordinate(x, y)
    tile_coords = mercator_coords.to_tile(zoom)
    tile_bb = GridBB(zoom,
                     min_x=tile_coords.x - math.ceil(tiles_h / 2),
                     max_x=tile_coords.x + math.ceil(tiles_h / 2),
                     min_y=tile_coords.y - math.ceil(tiles_v / 2),
                     max_y=tile_coords.y + math.ceil(tiles_v / 2))
    return tile_bb


def download_tile(map_layer, zoom, x, y):
    """
    Download a given tile from the tile server.

    Args:
        map_layer (MapLayer): MapLayer object which provides the tile-url.
        zoom (int): zoom level
        x (int): Tile-x-coordinate
        y (int): Tile-y-coordinate

    Returns:
        file: temporary file containing the downloaded image.

    """
    try:
        tile_url = map_layer.get_tile_url(zoom, x, y)
        tmp_file, headers = urllib.request.urlretrieve(tile_url)
        return (x, y), tmp_file
    except URLError as e:
        app.logger.info("Error downloading tile x={}, y={}, z={} for layer {}: {}".format(
            x, y, zoom, map_layer, e.reason))
        return (x, y), pkg_resources.resource_filename("geos", "static/empty_tile.png")


def _download_tile_wrapper(args):
    """wrapper function for using the multiprocessing module with multiple arguments"""
    return download_tile(*args)


def get_tiles(map_layer, bbox, n_workers=N_DOWNLOAD_WORKERS):
    """
    Download tiles.

    Args:
        map_source (MapSource):
        bbox (TileBB): Bounding box delimiting the map
        n_workers (int): number of threads to used for downloading.

    Returns:
        dict of file: Dictionary mapping coordinates to temporary files.

        Example::

            {
                (x, y) : <FileHandle>
            }

    """
    p = Pool(n_workers)
    tiles = {}
    for (x, y), tmp_file in p.imap_unordered(_download_tile_wrapper, zip(itertools.repeat(map_layer),
                                                                         itertools.repeat(bbox.zoom),
                                                                         *zip(*bboxiter(bbox)))):
        app.logger.info("Downloaded tile x={}, y={}, z={}".format(x, y, bbox.zoom))
        tiles[(x, y)] = tmp_file

    return tiles


def stitch_map(tiles, width, height, bbox, dpi):
    """
    Merge tiles together into one image.

    Args:
        tiles (list of dict of file): tiles for each layer
        width (float): page width in mm
        height (height): page height in mm
        dpi (dpi): resolution in dots per inch

    Returns:
        PIL.Image: merged map.

    """
    size = (int(width * dpi_to_dpmm(dpi)), int(height * dpi_to_dpmm(dpi)))
    background = Image.new('RGBA', size, (255, 255, 255))
    for layer in tiles:
        layer_img = Image.new("RGBA", size)
        for (x, y), tile_path in layer.items():
            tile = Image.open(tile_path)
            layer_img.paste(tile, ((x - bbox.min.x) * TILE_SIZE, (y - bbox.min.y) * TILE_SIZE))
        background = Image.alpha_composite(background, layer_img)
    add_scales_bar(background, bbox)
    return background.convert("RGB")


def add_scales_bar(img, bbox):
    """
    Add a scales bar to the  map.

    Calculates the resolution at the current latitude and
    inserts the corresponding scales bar on the map.

    Args:
        img (Image): Image object to which the scales bar will be added.
        bbox (TileBB): boundaries of the map

    """
    tc = TileCoordinate(bbox.min.zoom, bbox.min.x, bbox.min.y)
    meters_per_pixel = tc.resolution()
    one_km_bar = int(1000 * (1 / meters_per_pixel))
    col_black = (0, 0, 0)

    line_start = (100, img.size[1] - 100)  # px
    line_end = (line_start[0] + one_km_bar, line_start[1])
    whiskers_left = [line_start[0], line_start[1] - 15, line_start[0], line_start[1] + 15]
    whiskers_right = [line_end[0], line_end[1] - 15, line_end[0], line_end[1] + 15]

    draw = ImageDraw.Draw(img)
    draw.line([line_start, line_end], fill=col_black, width=5)
    draw.line(whiskers_left, fill=col_black, width=2)
    draw.line(whiskers_right, fill=col_black, width=2)
    draw.text((line_start[0] + 10, line_start[1] + 10), fill=col_black, text="1 km")
    del draw
