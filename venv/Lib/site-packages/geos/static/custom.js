//////////////// GLOBAL FUNCTION DEFINITIONS ////////////////////////////
/**
 * implement a String.format function similar to the one
 * known from python.
 */
if (!String.prototype.format) {
    String.prototype.format = function () {
        var args = arguments;
        return this.replace(/{(\d+)}/g, function (match, number) {
            return typeof args[number] != 'undefined'
                ? args[number]
                : match
                ;
        });
    };
}


/////////////// DRAWING-RELATED FUNCTIONS //////////////////////////////
/**
 * Format length output.
 * @param {ol.geom.LineString} line The line.
 * @return {string} The formatted length.
 */
var formatLength = function (line) {
    var length;
    var coordinates = line.getCoordinates();
    length = 0;
    var sourceProj = map.getView().getProjection();
    for (var i = 0, ii = coordinates.length - 1; i < ii; ++i) {
        var c1 = ol.proj.transform(coordinates[i], sourceProj, 'EPSG:4326');
        var c2 = ol.proj.transform(coordinates[i + 1], sourceProj, 'EPSG:4326');
        length += wgs84Sphere.haversineDistance(c1, c2);
    }
    var output;
    if (length > 100) {
        output = (Math.round(length / 1000 * 100) / 100) +
            ' ' + 'km';
    } else {
        output = (Math.round(length * 100) / 100) +
            ' ' + 'm';
    }
    return output;
};


/**
 * Format area output.
 * @param {ol.geom.Polygon} polygon The polygon.
 * @return {string} Formatted area.
 */
var formatArea = function (polygon) {
    var area;
    var sourceProj = map.getView().getProjection();
    var geom = /** @type {ol.geom.Polygon} */(polygon.clone().transform(
        sourceProj, 'EPSG:4326'));
    var coordinates = geom.getLinearRing(0).getCoordinates();
    area = Math.abs(wgs84Sphere.geodesicArea(coordinates));
    var output;
    if (area > 10000) {
        output = (Math.round(area / 1000000 * 100) / 100) +
            ' ' + 'km<sup>2</sup>';
    } else {
        output = (Math.round(area * 100) / 100) +
            ' ' + 'm<sup>2</sup>';
    }
    return output;
};


function addInteraction() {
    var type = (measureType == 'area' ? 'Polygon' : 'LineString');
    draw = new ol.interaction.Draw({
        source: source,
        type: /** @type {ol.geom.GeometryType} */ (type),
        style: new ol.style.Style({
            fill: new ol.style.Fill({
                color: 'rgba(255, 255, 255, 0.2)'
            }),
            stroke: new ol.style.Stroke({
                color: 'rgba(0, 0, 0, 0.5)',
                lineDash: [10, 10],
                width: 2
            }),
            image: new ol.style.Circle({
                radius: 5,
                stroke: new ol.style.Stroke({
                    color: 'rgba(0, 0, 0, 0.7)'
                }),
                fill: new ol.style.Fill({
                    color: 'rgba(255, 255, 255, 0.2)'
                })
            })
        })
    });
    map.addInteraction(draw);

    createMeasureTooltip();
    createHelpTooltip();

    var listener;
    draw.on('drawstart',
        function (evt) {
            // set sketch
            sketch = evt.feature;

            /** @type {ol.Coordinate|undefined} */
            var tooltipCoord = evt.coordinate;

            listener = sketch.getGeometry().on('change', function (evt) {
                var geom = evt.target;
                var output;
                if (geom instanceof ol.geom.Polygon) {
                    output = formatArea(geom);
                    tooltipCoord = geom.getInteriorPoint().getCoordinates();
                } else if (geom instanceof ol.geom.LineString) {
                    output = formatLength(geom);
                    tooltipCoord = geom.getLastCoordinate();
                }
                measureTooltipElement.innerHTML = output;
                measureTooltip.setPosition(tooltipCoord);
            });
        }, this);

    draw.on('drawend',
        function () {
            measureTooltipElement.className = 'tooltip tooltip-static';
            measureTooltip.setOffset([0, -7]);
            // unset sketch
            sketch = null;
            // unset tooltip so that a new one can be created
            measureTooltipElement = null;
            createMeasureTooltip();
            ol.Observable.unByKey(listener);
        }, this);
}


/**
 * Creates a new help tooltip
 */
function createHelpTooltip() {
    if (helpTooltipElement) {
        helpTooltipElement.parentNode.removeChild(helpTooltipElement);
    }
    helpTooltipElement = document.createElement('div');
    helpTooltipElement.className = 'tooltip hidden';
    helpTooltip = new ol.Overlay({
        element: helpTooltipElement,
        offset: [15, 0],
        positioning: 'center-left'
    });
    map.addOverlay(helpTooltip);
    mapOverlays.push(helpTooltip);
}


/**
 * Creates a new measure tooltip
 */
function createMeasureTooltip() {
    if (measureTooltipElement) {
        measureTooltipElement.parentNode.removeChild(measureTooltipElement);
    }
    measureTooltipElement = document.createElement('div');
    measureTooltipElement.className = 'tooltip tooltip-measure';
    measureTooltip = new ol.Overlay({
        element: measureTooltipElement,
        offset: [0, -15],
        positioning: 'bottom-center'
    });
    map.addOverlay(measureTooltip);
    mapOverlays.push(measureTooltip);
}

/**
 * Handle pointer move.
 * @param {ol.MapBrowserEvent} evt The event.
 */
var pointerMoveHandler = function (evt) {
    if (evt.dragging) {
        return;
    }
    /** @type {string} */
    var helpMsg = 'Click to start drawing';

    if (sketch) {
        var geom = (sketch.getGeometry());
        if (geom instanceof ol.geom.Polygon) {
            helpMsg = continuePolygonMsg;
        } else if (geom instanceof ol.geom.LineString) {
            helpMsg = continueLineMsg;
        }
    }

    helpTooltipElement.innerHTML = helpMsg;
    helpTooltip.setPosition(evt.coordinate);

    helpTooltipElement.classList.remove('hidden');
};


//////////////////// GLOBAL VARIABLE DECLARATIONS /////////////////
var wgs84Sphere = new ol.Sphere(6378137);

/**
 * vector source for drawing
 * @type {any}
 */
var source = new ol.source.Vector();

/**
 * vector layer for drawing
 * @type {any}
 */
var vector = new ol.layer.Vector({
    source: source,
    style: new ol.style.Style({
        fill: new ol.style.Fill({
            color: 'rgba(255, 255, 255, 0.2)'
        }),
        stroke: new ol.style.Stroke({
            color: '#ffcc33',
            width: 2
        }),
        image: new ol.style.Circle({
            radius: 7,
            fill: new ol.style.Fill({
                color: '#ffcc33'
            })
        })
    })
});

// layers that persist when a new map is added.
var persistentLayers = [vector]

/**
 * global map object
 * @type {ol.Map}
 */
var map = new ol.Map({
    layers: persistentLayers,
    target: 'map',
    view: new ol.View({
        center: ol.proj.fromLonLat([37.41, 8.82]),
        zoom: 4
    })
});

/**
 * Currently drawn feature.
 * @type {ol.Feature}
 */
var sketch;

/**
 * The help tooltip element.
 * @type {Element}
 */
var helpTooltipElement;

/**
 * Overlay to show the help messages.
 * @type {ol.Overlay}
 */
var helpTooltip;

/**
 * The measure tooltip element.
 * @type {Element}
 */
var measureTooltipElement;

/**
 * Overlay to show the measurement.
 * @type {ol.Overlay}
 */
var measureTooltip;

/** List of all measure overlays **/
var mapOverlays = [];

/**
 * Message to show when the user is drawing a polygon.
 * @type {string}
 */
var continuePolygonMsg = 'Click to continue drawing the polygon';

/**
 * Message to show when the user is drawing a line.
 * @type {string}
 */
var continueLineMsg = 'Click to continue drawing the line';

var measureType = 'line'

var draw; // global so we can remove it later


var mapSources = [];
var currentMap;



function activateMap(mapSource) {
    currentMap = mapSource;
    $('#maps li.active').removeClass('active');
    $('#' + mapSource.id).addClass('active');
    console.log(mapSource.name);
    layers = map.getLayers();
    layers.clear();
    $.each(mapSource.layers, function (i, tileLayer) {
        tmpLayer = new ol.layer.Tile({
            source: new ol.source.XYZ({
                url: tileLayer.tile_url,
                crossOrigin: 'anonymous',
                minZoom: tileLayer.min_zoom,
                maxZoom: tileLayer.max_zoom
            })
        });
        layers.push(tmpLayer)
    });
    layers.extend(persistentLayers);
    handleMinMaxZoom();
    updatePrintZoomLevels(mapSource);
}

function startDrawing() {
    // activate drawing functions
    stopDrawing();
    map.on('pointermove', pointerMoveHandler);
    map.getViewport().addEventListener('mouseout', function () {
        helpTooltipElement.classList.add('hidden');
    });
    addInteraction();
}

function stopDrawing() {
    map.un('pointermove', pointerMoveHandler);
    map.removeInteraction(draw);
}

function removeDrawing() {
    $.each(mapOverlays, function(i, overlay) {
       map.removeOverlay(overlay);
    });
    mapOverlays = [];
    helpTooltip = false;
    helpTooltipElement = false;
    tmpSource = vector.getSource();
    tmpSource.clear();
}

function handleMinMaxZoom() {
    layers = map.getLayers();
    layers.forEach(function(layer, i, a) {
        tmpSource = layer.getSource()
        // 'duck typing' for source object, vector layers don't have a zoom level.
        if(typeof tmpSource.getTileGrid === 'function') {
            if(map.getView().getZoom() > tmpSource.getTileGrid().maxZoom ||
                map.getView().getZoom() < tmpSource.getTileGrid().minZoom) {
                layer.setVisible(false);
            } else {
                layer.setVisible(true);
            }
        }

    });
}

function updatePrintZoomLevels(mapSource) {
    $('#print-zoom').empty();
    for(var i=Math.max(5, mapSource.min_zoom); i<=mapSource.max_zoom; i++) {
        is_active = (i == mapSource.max_zoom) ? 'class="active"' : '';
        $('#print-zoom').append('<li {0}><a href="#" data-zoom="{1}">{2}</a></li>'.format(is_active, i, i));
    }
}


$(document).ready(function () {
    map.getView().on('change:resolution', handleMinMaxZoom);

    $navMain = $('.navbar-collapse')
    $navMain.on("click", "a:not([data-toggle])", null, function () {
        $navMain.collapse('hide');
    });
    $('.btn-done').click(function () {
        $('.childMenu.in').collapse('hide');
        $navMain.collapse('hide');
    })
    $('.parentMenu').click(function() {
        $('.childMenu.in').collapse('hide');
    });
    $('.navbar-toggle').click(function() {
        $('.childMenu.in').collapse('hide');
    })

    //download and process map sources
    $.getJSON('/maps.json', function (tmpMapSources) {
        //data is the JSON string
        mapSources = tmpMapSources;
        $.each(mapSources, function (mapId, mapSource) {
            $li = $("<li>", {'id': mapSource.id});
            $a = $("<a>", {'href': "#"}).html(mapSource.name)
            $a.click(function() { activateMap(mapSource) });
            $li.append($a);
            $("#maps").append($li);
        });
        activateMap(tmpMapSources.default)
    });

    $("#measure").click(startDrawing);

    // listener to change measure-type
    $("#measure-type-switch button").click(function (e) {
        e.stopImmediatePropagation();
        $("#measure-type-switch button").removeClass("btn-active");
        $(this).addClass("btn-active");
        measureType = $(this).attr("data-value");
        map.removeInteraction(draw);
        addInteraction();
    });

    // listener to clear drawing area
    $("#measure-clear").click(function (e) {
        e.stopImmediatePropagation();
        stopDrawing();
        removeDrawing();
        startDrawing();
    });

    // listener to stop drawing
    $("#measure-done").click(function (e) {
        stopDrawing();
    });

    // listener for printing
    $("#print-print").click(function (e) {
        e.stopImmediatePropagation();
        pZoom = $("#print-zoom li.active a").attr('data-zoom');
        pWidth = $("#print-size li.active a").attr('data-width');
        pHeight = $('#print-size li.active a').attr('data-height');
        if(pZoom === undefined) {
            alert('Your have to choose a zoom level');
        } else if (pWidth === undefined || pHeight === undefined) {
            alert('You have to choose a page format');
        } else {
            center = map.getView().getCenter();
            window.open("/print/{0}/{1}/{2}/{3}/{4}/{5}/map.pdf".format(currentMap.id, pZoom, center[0], center[1], pWidth, pHeight));
        }
    });


    $("#print-size").on('click', 'li', function (e) {
        $("#print-size li.active").removeClass('active');
        $(this).addClass('active');
    });

    $("#print-zoom").on('click', 'li', function (e) {
        $("#print-zoom li.active").removeClass('active');
        $(this).addClass('active');
    });

});
