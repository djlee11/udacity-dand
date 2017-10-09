import xml.etree.cElementTree as ET
import pprint
import re
from collections import defaultdict
import operator

# count_tag, count_attribute
tree = ET.parse("./input/sample.osm")

# unique_key, explore_path, count_county
trees = ET.iterparse("./input/sample.osm")

def count_tag(path):
	tags = {}
	for elem in tree.iter():
		if elem.tag not in tags:
			tags[elem.tag] = 1
		else:
			tags[elem.tag] += 1
	pprint.pprint(tags)

#count_tag(tree)

def count_attribute(path):
	tag_keys = ["node", "node/tag", "way", "way/nd", "way/tag"]

	for tag in tag_keys:
		attributes = {}
		for element in tree.findall(tag):
		    for attr in element.attrib.keys():
		    	if attr in attributes:
		        	attributes[attr] += 1
		        else:
		        	attributes[attr] = 1
		print tag
		pprint.pprint(attributes)

#count_attribute(tree)

def unique_key(path):
	uk = defaultdict(int)
	for _, element in trees:
		if element.tag == 'node' or element.tag == 'way':
			for child in element:
				if child.tag == 'tag':
					uk[child.attrib['k']] +=1
	sorted_uk = sorted(uk.items(), key=operator.itemgetter(1), reverse = True)[0:20]
	pprint.pprint(sorted_uk)

#unique_key(trees)

def explore_path(path):
	ep = defaultdict(int)
	for _, element in trees:
		if element.tag == 'node' or element.tag == 'way':
			for child in element:
				if child.tag == 'tag':
					if child.attrib['k'] == 'addr:county':
						ep[child.attrib['v']] += 1
	pprint.pprint(list(ep))

#explore_path(trees)

def count_county(path):
	uk = defaultdict(int)
	for _, element in trees:
		if element.tag == 'node' or element.tag == 'way':
			for child in element:
				if child.tag == 'tag':
					if child.attrib['k'] == 'tiger:county' or child.attrib['k'] == 'addr:county':
						uk[child.attrib['v']] +=1
	sorted_uk = sorted(uk.items(), key=operator.itemgetter(1), reverse = True)
	pprint.pprint(sorted_uk)

count_county(trees)