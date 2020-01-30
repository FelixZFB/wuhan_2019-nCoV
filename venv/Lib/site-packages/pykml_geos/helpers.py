"""pyKML Helpers Module

The pykml.helpers module contains 'helper' functions that operate on pyKML 
document objects for accomplishing common tasks.

"""

from pykml.factory import KML_ElementMaker as K
from pykml.factory import GX_ElementMaker as GX

def separate_namespace(qname):
    "Separates the namespace from the element"
    import re
    try:
        namespace, element_name = re.search('^{(.+)}(.+)$', qname).groups()
    except:
        namespace = None
        element_name = qname
    return namespace, element_name

def set_max_decimal_places(doc, max_decimals):
    """Sets the maximum number of decimal places used by KML elements
    
    This method facilitates reducing the file size of a KML document.
    """
    
    def replace_delimited_string_member(
            delimited_str,
            separator,
            index_no,
            decimal_places):
        "Modify the number of decimal places for a delimited string member"
        values = delimited_str.split(separator)
        values[index_no] = str(round(float(values[index_no]), decimal_places))
        return separator.join(values)
    
    if max_decimals.has_key('longitude'):
        data_type = 'longitude'
        index_no = 0 # longitude is in the first position
        # modify <longitude>
        for el in doc.findall(".//{http://www.opengis.net/kml/2.2}longitude"):
            new_val = round(float(el.text), max_decimals[data_type])
            el.getparent().longitude = K.longitude(new_val)
        # modify <coordinates> elements
        for el in doc.findall(".//{http://www.opengis.net/kml/2.2}coordinates"):
            vertex_str_list = []
            for vertex in el.text.strip().split(' '):
                vertex_str_list.append(
                    replace_delimited_string_member(
                        delimited_str=vertex,
                        separator=',',
                        index_no=index_no,
                        decimal_places=max_decimals[data_type]
                    )
                )
            el_new = K.coordinates(' '.join(vertex_str_list).strip())
            el.getparent().replace(el, el_new)
        # modify <gx:coords> elements
        for el in doc.findall(".//{http://www.google.com/kml/ext/2.2}coord"):
            el._setText(
                replace_delimited_string_member(
                    delimited_str=el.text,
                    separator=' ',
                    index_no=index_no,
                    decimal_places=max_decimals[data_type]
                )
            )
    
    if max_decimals.has_key('latitude'):
        data_type = 'latitude'
        index_no = 1 # latitude is in the second position
        # modify <latitude> elements
        for el in doc.findall(".//{http://www.opengis.net/kml/2.2}latitude"):
            new_val = round(float(el.text), max_decimals[data_type])
            el.getparent().latitude = K.latitude(new_val)
        # modify <coordinates> elements
        for el in doc.findall(".//{http://www.opengis.net/kml/2.2}coordinates"):
            vertex_str_list = []
            for vertex in el.text.strip().split(' '):
                vertex_str_list.append(
                    replace_delimited_string_member(
                        delimited_str=vertex,
                        separator=',',
                        index_no=index_no,
                        decimal_places=max_decimals[data_type]
                    )
                )
            el_new = K.coordinates(' '.join(vertex_str_list).strip())
            el.getparent().replace(el, el_new)
        # modify <gx:coords> elements
        for el in doc.findall(".//{http://www.google.com/kml/ext/2.2}coord"):
            el._setText(
                replace_delimited_string_member(
                    delimited_str=el.text,
                    separator=' ',
                    index_no=index_no,
                    decimal_places=max_decimals[data_type]
                )
            )

    if max_decimals.has_key('altitude'):
        data_type = 'altitude'
        index_no = 2 # altitude is in the third position
        # modify <altitude> elements
        for el in doc.findall(".//{http://www.opengis.net/kml/2.2}altitude"):
            new_val = round(float(el.text), max_decimals[data_type])
            el.getparent().altitude = K.altitude(new_val)
        # modify <coordinates> elements
        for el in doc.findall(".//{http://www.opengis.net/kml/2.2}coordinates"):
            vertex_str_list = []
            for vertex in el.text.strip().split(' '):
                vertex_str_list.append(
                    replace_delimited_string_member(
                        delimited_str=vertex,
                        separator=',',
                        index_no=index_no,
                        decimal_places=max_decimals[data_type]
                    )
                )
            el_new = K.coordinates(' '.join(vertex_str_list).strip())
            el.getparent().replace(el, el_new)
        # modify <gx:coords> elements
        for el in doc.findall(".//{http://www.google.com/kml/ext/2.2}coord"):
            el._setText(
                replace_delimited_string_member(
                    delimited_str=el.text,
                    separator=' ',
                    index_no=index_no,
                    decimal_places=max_decimals[data_type]
                )
            )
    
    if max_decimals.has_key('heading'):
        for el in doc.findall(".//{http://www.opengis.net/kml/2.2}heading"):
            new_val = round(float(el.text), max_decimals['heading'])
            el.getparent().heading = K.heading(new_val)
    if max_decimals.has_key('tilt'):
        for el in doc.findall(".//{http://www.opengis.net/kml/2.2}tilt"):
            new_val = round(float(el.text), max_decimals['tilt'])
            el.getparent().tilt = K.tilt(new_val)
    if max_decimals.has_key('range'):
        for el in doc.findall(".//{http://www.opengis.net/kml/2.2}range"):
            new_val = round(float(el.text), max_decimals['range'])
            el.getparent().range = K.range(new_val)
