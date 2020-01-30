""" pyKML Utility Module

The pykml.utility module provides utility functions that operate on KML 
documents
"""
import re

def count_elements(doc):
    "Counts the number of times each element is used in a document"
    summary = {}
    for el in doc.iter():
        try:
            namespace, element_name = re.search('^{(.+)}(.+)$', el.tag).groups()
        except:
            namespace = None
            element_name = el.tag
        if not summary.has_key(namespace):
            summary[namespace] = {}
        if not summary[namespace].has_key(element_name):
            summary[namespace][element_name] = 1
        else:
            summary[namespace][element_name] += 1
    return summary
