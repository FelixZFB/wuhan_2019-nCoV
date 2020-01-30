import xml.etree.ElementTree
import itertools
import os
from pprint import pprint
from geos.geometry import GeographicBB
import re

F_SEP = "/"  # folder separator in mapsources (not necessarily == os.sep)


def load_maps(maps_dir):
    """
    Load all xml map sources from a given directory.

    Args:
        maps_dir: path to directory to search for maps

    Returns:
        dict of MapSource:

    """
    maps_dir = os.path.abspath(maps_dir)
    maps = {}
    for root, dirnames, filenames in os.walk(maps_dir):
        for filename in filenames:
            if filename.endswith(".xml"):
                xml_file = os.path.join(root, filename)
                map = MapSource.from_xml(xml_file, maps_dir)
                if map.id in maps:
                    raise MapSourceException("duplicate map id: {} in file {}".format(map.id, xml_file))
                else:
                    maps[map.id] = map
    return maps


def walk_mapsources(mapsources, root=""):
    """
    recursively walk through foldernames of mapsources.

    Like os.walk, only for a list of mapsources.

    Args:
        mapsources (list of MapSource):

    Yields:
        (root, foldernames, maps)

    >>> mapsources = load_maps("test/mapsources")
    >>> pprint([x for x in walk_mapsources(mapsources.values())])
    [('',
      ['asia', 'europe'],
      [<MapSource: osm1 (root 1), n_layers: 1, min_zoom:5, max_zoom:18>,
       <MapSource: osm10 (root 2), n_layers: 1, min_zoom:5, max_zoom:18>]),
     ('/asia',
      [],
      [<MapSource: osm6 (asia), n_layers: 1, min_zoom:5, max_zoom:18>]),
     ('/europe',
      ['france', 'germany', 'switzerland'],
      [<MapSource: osm4 (eruope 1), n_layers: 1, min_zoom:1, max_zoom:18>]),
     ('/europe/france',
      [],
      [<MapSource: osm2 (europe/france 1), n_layers: 1, min_zoom:5, max_zoom:18>,
       <MapSource: osm3 (europe/france 2), n_layers: 1, min_zoom:1, max_zoom:18>,
       <MapSource: osm5 (europe/france 3), n_layers: 1, min_zoom:5, max_zoom:18>]),
     ('/europe/germany',
      [],
      [<MapSource: osm7 (europe/germany 1), n_layers: 1, min_zoom:5, max_zoom:18>,
       <MapSource: osm8 (europe/germany 2), n_layers: 1, min_zoom:5, max_zoom:18>]),
     ('/europe/switzerland',
      [],
      [<MapSource: osm9 (europe/switzerland), n_layers: 1, min_zoom:5, max_zoom:18>])]

    """
    def get_first_folder(path):
        """
        Get the first folder in a path
        > get_first_folder("europe/switzerland/bs")
        europe
        """
        path = path[len(root):]
        path = path.lstrip(F_SEP)
        return path.split(F_SEP)[0]

    path_tuples = sorted(((get_first_folder(m.folder), m) for m in mapsources), key=lambda x: x[0])
    groups = {k: [x for x in g] for k, g in itertools.groupby(path_tuples, lambda x: x[0])}
    folders = sorted([x for x in groups.keys() if x != ""])
    mapsources = sorted([t[1] for t in groups.get("", [])], key=lambda x: x.id)
    yield (root, folders, mapsources)
    for fd in folders:
        yield from walk_mapsources([t[1] for t in groups[fd]], F_SEP.join([root, fd]))


class MapSourceException(Exception):
    pass


class MapLayer(object):
    """
    The layer object contained in a MapSource.

    A MapSource can contain multiple layers.
    A layer contains all information on how to access the tiles.

    Args:
        tile_url: URL to the tiles which {$z}, {$x} and {$y} as placeholders.
        min_zoom (int): minimal zoom level at which the layer is active
        max_zoom (int): maximal zoom level at which the layer is active
    """
    def __init__(self, tile_url=None, min_zoom=1, max_zoom=17):
        self.tile_url = tile_url
        self.min_zoom = min_zoom
        self.max_zoom = max_zoom

    def get_tile_url(self, zoom, x, y):
        """
        Fill the placeholders of the tile url with zoom, x and y.

        >>> ms = MapSource.from_xml("mapsources/osm.xml")
        >>> ms.get_tile_url(42, 43, 44)
        'http://tile.openstreetmap.org/42/43/44.png'
        """
        return self.tile_url.format(**{"$z": zoom, "$x": x, "$y": y})

    def __repr__(self):
        return "<MapLayer: url:{}, min_zoom:{}, max_zoom:{}>".format(
            self.tile_url, self.min_zoom, self.max_zoom)


class MapSource(object):
    """
    A MapSource contains Meta-Information of the map.
    Additionally it can hold one or more MapLayers which contain the information
    on how to access the tiles.
    """

    def __init__(self, id, name, folder="", bbox=None):
        """
        Args:
            id (str): unique identifier (e.g. filename)
            name (str): display name
            folder (str): folder to organize the map in (e.g. /europe/germany)
            bbox (GeographicBB): bounding box, only load tiles within

        >>> ms = MapSource.from_xml("mapsources/osm.xml")
        >>> ms.name
        'OSM Mapnik'
        >>> ms.min_zoom
        0
        >>> ms.max_zoom
        18
        >>> ms.layers
        [<MapLayer: url:http://tile.openstreetmap.org/{$z}/{$x}/{$y}.png, min_zoom:0, max_zoom:18>]
        """
        self.id = id
        self.name = name
        self.layers = []
        self.folder = folder
        self.bbox = bbox

    @property
    def min_zoom(self):
        """
        Get the minimal zoom level of all layers.

        Returns:
            int: the minimum of all zoom levels of all layers

        Raises:
            ValueError: if no layers exist

        """
        zoom_levels = [map_layer.min_zoom for map_layer in self.layers]
        return min(zoom_levels)

    @property
    def max_zoom(self):
        """
        Get the maximal zoom level of all layers.

        Returns:
            int: the maximum of all zoom levels of all layers

        Raises:
            ValueError: if no layers exist

        """
        zoom_levels = [map_layer.max_zoom for map_layer in self.layers]
        return max(zoom_levels)

    @staticmethod
    def parse_xml_boundary(xml_region):
        """
        Get the geographic bounds from an XML element

        Args:
            xml_region (Element): The <region> tag as XML Element

        Returns:
            GeographicBB:
        """
        try:
            bounds = {}
            for boundary in xml_region.getchildren():
                bounds[boundary.tag] = float(boundary.text)
            bbox = GeographicBB(min_lon=bounds["west"], max_lon=bounds["east"],
                                min_lat=bounds["south"], max_lat=bounds["north"])
            return bbox
        except (KeyError, ValueError):
            raise MapSourceException("region boundaries are invalid. ")

    @staticmethod
    def parse_xml_layers(xml_layers):
        """
        Get the MapLayers from an XML element

        Args:
            xml_layers (Element): The <layers> tag as XML Element

        Returns:
            list of MapLayer:

        """
        layers = []
        for custom_map_source in xml_layers.getchildren():
            layers.append(MapSource.parse_xml_layer(custom_map_source))
        return layers

    @staticmethod
    def parse_xml_layer(xml_custom_map_source):
        """
        Get one MapLayer from an XML element

        Args:
            xml_custom_map_source (Element): The <customMapSource> element tag wrapped
               in a <layers> tag as XML Element

        Returns:
            MapLayer:

        """
        map_layer = MapLayer()
        try:
            for elem in xml_custom_map_source.getchildren():
                if elem.tag == 'url':
                    map_layer.tile_url = elem.text
                elif elem.tag == 'minZoom':
                    map_layer.min_zoom = int(elem.text)
                elif elem.tag == 'maxZoom':
                    map_layer.max_zoom = int(elem.text)
        except ValueError:
            raise MapSourceException("minZoom/maxZoom must be an integer. ")

        if map_layer.tile_url is None:
            raise MapSourceException("Layer requires a tile_url parameter. ")

        return map_layer

    @staticmethod
    def from_xml(xml_path, mapsource_prefix=""):
        """
        Create a MapSource object from a MOBAC
        mapsource xml.

        Args:
            xml_path: path to the MOBAC mapsource xml file.
            mapsource_prefix: root path of the mapsource folder.
              Used to determine relative path within the maps
              directory.

        Note:
            The Meta-Information is read from the xml
            <id>, <folder>, <name> tags. If <id> is not available it defaults
            to the xml file basename. If <folder> is not available if defaults to
            the folder of the xml file with the `mapsource_prefix` removed.

            The function first tries <url>, <minZoom>, <maxZoom> from <customMapSource>
            tags within the <layers> tag. If the <layers> tag is not available,
            the function tries to find <url>, <minZoom> and <maxZoom> on the top level.
            If none of thie information is found, a MapSourceException is raised. 

        Returns:
            MapSource:

        Raises:
            MapSourceException: when the xml file could not be parsed properly.

        """
        xmldoc = xml.etree.ElementTree.parse(xml_path).getroot()

        map_id = os.path.splitext(os.path.basename(xml_path))[0]
        map_name = map_id
        map_folder = re.sub("^" + re.escape(mapsource_prefix), "", os.path.dirname(xml_path))
        bbox = None
        layers = None

        for elem in xmldoc.getchildren():
            if elem.tag == 'id':
                map_id = elem.text
            elif elem.tag == 'name':
                map_name = elem.text
            elif elem.tag == 'folder':
                map_folder = elem.text
            elif elem.tag == 'region':
                bbox = MapSource.parse_xml_boundary(elem)
            elif elem.tag == 'layers':
                layers = MapSource.parse_xml_layers(elem)

        if map_folder is None:
            map_folder = "" # fallback if bad specification in xml
        if layers is None:  # layers tag not found, expect url etc. in main xmldoc
            layers = [MapSource.parse_xml_layer(xmldoc)]

        ms = MapSource(map_id, map_name, map_folder, bbox=bbox)
        ms.layers = layers
        return ms

    def __repr__(self):
        return "<MapSource: {} ({}), n_layers: {}, min_zoom:{}, max_zoom:{}>".format(
            self.id, self.name, len(self.layers), self.min_zoom, self.max_zoom)


