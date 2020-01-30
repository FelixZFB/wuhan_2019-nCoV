from flask import Response, render_template, send_file, jsonify
from geos.kml import *
from geos.print import print_map
from geos import app


def kml_response(kml_map):
    """
    Args:
        kml_map (KMLMap): KMLMap object

    Returns:
        Response: a Flask Response with proper MIME-type.

    """
    return Response(kml_map.get_kml(), mimetype=kml_map.MIME_TYPE)


@app.route('/')
def index():
    return render_template("index.html")


@app.route("/maps.json")
def maps_json():
    """
    Generates a json object which serves as bridge between
    the web interface and the map source collection.

    All attributes relevant for openlayers are converted into
    JSON and served through this route.

    Returns:
        Response: All map sources as JSON object.
    """
    map_sources = {
        id: {
                "id": map_source.id,
                "name": map_source.name,
                "folder": map_source.folder,
                "min_zoom": map_source.min_zoom,
                "max_zoom": map_source.max_zoom,
                "layers": [
                    {
                        "min_zoom": layer.min_zoom,
                        "max_zoom": layer.max_zoom,
                        "tile_url": layer.tile_url.replace("$", ""),
                    } for layer in map_source.layers
                    ]

            } for id, map_source in app.config["mapsources"].items()
        }
    return jsonify(map_sources)


@app.route('/print/<map_source>/<zoom>/<x>/<y>/<width>/<height>/map.pdf')
def map_to_pdf(map_source, zoom, x, y, width, height):
    """
    Generate a PDF at the given position.

    Args:
        map_source (str): id of the map source to print.
        zoom (int): zoom-level to print
        x (float): Center of the Map in mercator projection (EPSG:4326), x-coordinate
        y (float): Center of the Map in mercator projection (EPSG:4326), y-coordinate
        width (float): width of the pdf in mm
        height (float): height of the pdf in mm

    Returns:

    """
    map_source = app.config["mapsources"][map_source]
    pdf_file = print_map(map_source, x=float(x), y=float(y),
                         zoom=int(zoom), width=float(width), height=float(height), format='pdf')
    return send_file(pdf_file,
                     attachment_filename="map.pdf",
                     as_attachment=True)


@app.route("/kml-master.kml")
def kml_master():
    """KML master document for loading all maps in Google Earth"""
    kml_doc = KMLMaster(app.config["url_formatter"], app.config["mapsources"].values())
    return kml_response(kml_doc)


@app.route("/maps/<map_source>.kml")
def kml_map_root(map_source):
    """KML for a given map"""
    map = app.config["mapsources"][map_source]
    kml_doc = KMLMapRoot(app.config["url_formatter"], map, app.config["LOG_TILES_PER_ROW"])
    return kml_response(kml_doc)


@app.route("/maps/<map_source>/<int:z>/<int:x>/<int:y>.kml")
def kml_region(map_source, z, x, y):
    """KML region fetched by a Google Earth network link. """
    map = app.config["mapsources"][map_source]
    kml_doc = KMLRegion(app.config["url_formatter"], map, app.config["LOG_TILES_PER_ROW"],
                        z, x, y)
    return kml_response(kml_doc)
