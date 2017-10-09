#!/usr/bin/env python
# -*- coding: utf-8 -*-

import csv
import codecs
import pprint
import re
import xml.etree.cElementTree as ET
import cerberus
import schema

from collections import defaultdict
import operator

from audit import update_street, update_postal, update_county, update_phone

OSM_PATH = "./input/sample.osm"

NODES_PATH = "./output/nodes.csv"
NODE_TAGS_PATH = "./output/nodes_tags.csv"
WAYS_PATH = "./output/ways.csv"
WAY_NODES_PATH = "./output/ways_nodes.csv"
WAY_TAGS_PATH = "./output/ways_tags.csv"

LOWER_COLON = re.compile(r'^([a-z]|_)+:([a-z]|_)+')
PROBLEMCHARS = re.compile(r'[=\+/&<>;\'"\?%#$@\,\. \t\r\n]')

SCHEMA = schema.schema

# Make sure the fields order in the csvs matches the column order in the sql table schema
NODE_FIELDS = ['id', 'lat', 'lon', 'user', 'uid', 'version', 'changeset', 'timestamp']
NODE_TAGS_FIELDS = ['id', 'key', 'value', 'type']
WAY_FIELDS = ['id', 'user', 'uid', 'version', 'changeset', 'timestamp']
WAY_TAGS_FIELDS = ['id', 'key', 'value', 'type']
WAY_NODES_FIELDS = ['id', 'node_id', 'position']

# USING TO COUNT ISSUES
COUNTER_DICT = defaultdict(int)
STREET_ISSUE = defaultdict(int)

def shape_element(element, node_attr_fields=NODE_FIELDS, way_attr_fields=WAY_FIELDS,
                  problem_chars=PROBLEMCHARS, default_tag_type='regular'):

    node_attribs = {}
    way_attribs = {}
    way_nodes = []
    tags = []  # Handle secondary tags the same way for both node and way elements

    # CLEANING FIRST DESPITE NODE OR WAY !!!!!

    if element.tag == 'node' or element.tag == 'way':

      for child in element:
        
        if child.tag == 'tag':
          child_tag = {}
          
          #COUNTER_DICT[child.attrib['k']] +=1
          
          # CHECKING FOR PROBLEMATIC CHARACTERS
          if not PROBLEMCHARS.search(child.attrib['k']):
          
            # WORKING WITH "TYPES"
            if LOWER_COLON.search(child.attrib['k']):
              
              # CLEANING ATTRIBUTES WITH ":" SUCH AS ADDR:
              sub_attr = child.attrib['k'].split(':', 1)[1]

              # CLEANING STATES
              if sub_attr == 'state':
                child.attrib['v'] = 'GA'
              
              # CLEANING STREETS
              elif sub_attr == 'street':
                child.attrib['v'] = update_street(child.attrib['v'], STREET_ISSUE)
              
              # CLEANING POSTCODES
              elif sub_attr == 'postcode':
                child.attrib['v'] = update_postal(child.attrib['v'])

              # CLEANING COUNTIES
              elif sub_attr == 'county':
                child.attrib['v'] = update_county(child.attrib['v'])

            # CLEANING PHONE
            elif child.attrib['k'] == 'phone':
              child.attrib['v'] = update_phone(child.attrib['v'])


    # ADDING ENTRIES TO NODES AND WAYS DICTIONARY
    if element.tag == 'node':

      for item in element.attrib:
        if item in NODE_FIELDS:
          node_attribs[item] = element.attrib[item]

      for child in element:
        
        if child.tag == 'tag':
          child_tag = {}
          
          # CHECKING FOR PROBLEMATIC CHARACTERS
          if not PROBLEMCHARS.search(child.attrib['k']):
          
            # WORKING WITH "TYPES"
            if LOWER_COLON.search(child.attrib['k']):
              
              s = child.attrib['k']
              child_tag['type'] = s[0:s.find(':')]

            else:
              child_tag['type'] = 'regular'


            # ADDING TAGS TO NODE_TAGS
            child_tag['id'] = node_attribs['id']
            child_tag['key'] = child.attrib['k']
            child_tag['value'] = child.attrib['v']

            tags.append(child_tag)

      return {'node': node_attribs, 'node_tags': tags}


    elif element.tag == 'way':
      counter = 0

      for item in element.attrib:
        if item in WAY_FIELDS:
          way_attribs[item] = element.attrib[item]


      for child in element:
        nd_temp = {}
        tag_temp = {}

        # WORKING WITH WAY_NODES
        if child.tag == 'nd':

          nd_temp['id'] = way_attribs['id']
          nd_temp['node_id'] = child.attrib['ref']
          nd_temp['position'] = counter
          
          counter +=1

          way_nodes.append(nd_temp)

        if child.tag == 'tag':

          child_tag = {}
          
          # CHECKING FOR PROBLEMATIC CHARACTERS
          if not PROBLEMCHARS.search(child.attrib['k']):
          
          # WORKING WITH "TYPES"
            if LOWER_COLON.search(child.attrib['k']):
                s = child.attrib['k']
                child_tag['type'] = s[0:s.find(':')]
            else:
              child_tag['type'] = 'regular'

            # WORKING WITH TAGS
            child_tag['id'] = way_attribs['id']
            child_tag['key'] = child.attrib['k']
            child_tag['value'] = child.attrib['v']

            tags.append(child_tag)

      return {'way': way_attribs, 'way_nodes': way_nodes, 'way_tags': tags}


# ================================================== #
#               Helper Functions                     #
# ================================================== #
def get_element(osm_file, tags=('node', 'way', 'relation')):
    """Yield element if it is the right type of tag"""

    context = ET.iterparse(osm_file, events=('start', 'end'))
    _, root = next(context)
    for event, elem in context:
        if event == 'end' and elem.tag in tags:
            yield elem
            root.clear()


def validate_element(element, validator, schema=SCHEMA):
    """Raise ValidationError if element does not match schema"""
    if validator.validate(element, schema) is not True:
        field, errors = next(validator.errors.iteritems())
        message_string = "\nElement of type '{0}' has the following errors:\n{1}"
        error_string = pprint.pformat(errors)
        
        raise Exception(message_string.format(field, error_string))


class UnicodeDictWriter(csv.DictWriter, object):
    """Extend csv.DictWriter to handle Unicode input"""

    def writerow(self, row):
        super(UnicodeDictWriter, self).writerow({
            k: (v.encode('utf-8') if isinstance(v, unicode) else v) for k, v in row.iteritems()
        })

    def writerows(self, rows):
        for row in rows:
            self.writerow(row)


# ================================================== #
#               Main Function                        #
# ================================================== #
def process_map(file_in, validate):
    """Iteratively process each XML element and write to csv(s)"""

    with codecs.open(NODES_PATH, 'w') as nodes_file, \
         codecs.open(NODE_TAGS_PATH, 'w') as nodes_tags_file, \
         codecs.open(WAYS_PATH, 'w') as ways_file, \
         codecs.open(WAY_NODES_PATH, 'w') as way_nodes_file, \
         codecs.open(WAY_TAGS_PATH, 'w') as way_tags_file:

        nodes_writer = UnicodeDictWriter(nodes_file, NODE_FIELDS)
        node_tags_writer = UnicodeDictWriter(nodes_tags_file, NODE_TAGS_FIELDS)
        ways_writer = UnicodeDictWriter(ways_file, WAY_FIELDS)
        way_nodes_writer = UnicodeDictWriter(way_nodes_file, WAY_NODES_FIELDS)
        way_tags_writer = UnicodeDictWriter(way_tags_file, WAY_TAGS_FIELDS)

        nodes_writer.writeheader()
        node_tags_writer.writeheader()
        ways_writer.writeheader()
        way_nodes_writer.writeheader()
        way_tags_writer.writeheader()

        validator = cerberus.Validator()

        for element in get_element(file_in, tags=('node', 'way')):
            el = shape_element(element)

            if el:
                if validate is True:
                    validate_element(el, validator)

                if element.tag == 'node':
                    nodes_writer.writerow(el['node'])
                    node_tags_writer.writerows(el['node_tags'])
                elif element.tag == 'way':
                    ways_writer.writerow(el['way'])
                    way_nodes_writer.writerows(el['way_nodes'])
                    way_tags_writer.writerows(el['way_tags'])

        # CHECKING STRUCTURE, ISSUES, ETC.
        ##pprint.pprint(STREET_ISSUE)
        pprint.pprint(sorted(COUNTER_DICT.items(), key=operator.itemgetter(1), reverse = True))

if __name__ == '__main__':
    # Note: Validation is ~ 10X slower. For the project consider using a small
    # sample of the map when validating.
    process_map(OSM_PATH, validate=False)
