'''pyKML Parser Module

The pykml.parser module provides functions that can be used to parse KML 
from a file or remote URL.
'''
import os
from lxml import etree, objectify

class Schema():
    "A class representing an XML Schema used to validate KML documents"
    def __init__(self, schema):
        module_dir = os.path.split(__file__)[0]   # get the module path
        schema_file = os.path.join(module_dir, "schemas", schema)
        with open(schema_file) as f:
            self.schema = etree.XMLSchema(file=f)
    
    def validate(self, doc):
        """Validates a KML document
        
        This method eturns a boolean value indicating whether the KML document 
        is valid when compared to the XML Schema."""
        return self.schema.validate(doc)
    
    def assertValid(self, doc):
        """Asserts that a KML document is valide
        
        The method generates a validation error if the document is not valid
        when compared to the XML Schema.
        """
        return self.schema.assertValid(doc)

def fromstring(text, schema=None):
    """Parses a KML text string
    
    This function parses a KML text string and optionally validates it against 
    a provided schema object"""
    if schema:
        parser = objectify.makeparser(schema = schema.schema)
        return objectify.fromstring(text, parser=parser)
    else:
        return objectify.fromstring(text)

def parse(fileobject, schema=None):
    """Parses a file object
    
    This functon parses a KML file object, and optionally validates it against 
    a provided schema.
    """
    if schema:
        # with validation
        parser = objectify.makeparser(schema = schema.schema, strip_cdata=False)
        return objectify.parse(fileobject, parser=parser)
    else:
        # without validation
        return objectify.parse(fileobject)
