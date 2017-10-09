import xml.etree.cElementTree as ET
from pprint import pformat
import pprint
import re
from collections import defaultdict

osmfile = './input/sample.osm'
street_type_re = re.compile(r'\b\S+\.?$', re.IGNORECASE)
num_type_re = re.compile(r'\b[0-9][0-9][0-9]$|\b[0-9][0-9]$')
lowercase_re = re.compile(r'\b[a-z]+\b')
capitalize_re = re.compile(r'\b[A-Z]+\b')
postal_re = re.compile(r'\D+')
county_re = re.compile(r'[\:]|[\;]')

expected = ["Street", "Avenue", "Boulevard", "Drive", "Court", "Place", "Lane", "Road", 
            "Trail", "Parkway", "Ridge", "Way", "Pass", "Creek", "Chase", "Crossing",
            "Terrace", "Point", "Path", "Loop", "Run", "Cove", 'Bend', 'Circle', 'Trace', 'Walk',
            "Southeast", "Southwest", "Square", "Northeast", "Northwest", "View", "Landing", "North","East",
            "South", "West"]

def audit_street_type(street_types, street_name):
	m = street_type_re.search(street_name)
	if m:
		street_type = m.group()
		if street_type not in expected:
			street_types[street_type].add(street_name)
			
def audit(osmfile):
	osm_file = open(osmfile, 'r')
	street_types = defaultdict(set)
	for event, elem in ET.iterparse('./input/sample.osm', events=("start",)):
			if elem.tag == 'node'  or elem.tag == 'way':
				for tag in elem.iter('tag'):
					if is_street_name(tag):
						audit_street_type(street_types, tag.attrib['v'])
	osm_file.close()


def update_street(name, street_issue):
	"""
	Takes in street suffix and determines if it is an expected suffix. 
	If not, function checks whether suffix is an abbreviation issue (from mapping) and corrects it if true.
	Also checks to make sure no lowercase issues.
	"""

	mapping = { "St": "Street",
                "St.": "Street",
                "Blvd": "Boulevard",
                "Blvd.": "Boulevard",
                "Ave": "Avenue",
                "Ave.": "Avenue",
                "Rd.": "Road",
                "Rd" : "Road,",
                "Dr" : "Drive",
                "Dr.": "Drive",
                "Trl": "Trail",
                "Rd" : "Road",
                "Ln" : "Lane",
                "Cir": "Circle",
                "Ct" : "Court",
                "Hwy": "Highway",
                "Trce": "Trace",
                "Pkwy": "Parkway",
                "Pl": "Place",
                "Xing": "Crossing",
                "Ter": "Terrace",
                "Mhp": "Mobile Home Park",
                "Crst": "Crest",
                "Lndg": "Landing",
                "Pt": "Point",
                "S": "South",
                "S.": "South",
                "W": "West",
                "W.": "West",
                "N": "North",
                "N.": "North",
                "E": "East",
                "E.": "East",
                "NE": "Northeast",
                "NW": "Northwest",
                "SE": "Southeast",
                "SW": "Southwest",
                "Hts": "Heights",
                "Rte": "Route"}

	nn = street_type_re.search(name)
	ll = lowercase_re.search(name)
	cc = capitalize_re.search(name)

	if nn:
		street_type = nn.group()
		if street_type not in expected:
			
			if street_type in mapping:

				name = re.sub(street_type_re, mapping[street_type], name)

			elif ll or cc:
				name = name.title()
				return name

			else:
				street_issue[street_type] += 1
				return name

	return name


def update_phone(n):
	""" Formatting phone numbers to ###-###-#### """

	match = re.match(re.compile(r'\d{3}\-\d{3}\-\d{4}'),n)
				
	if match is None:
		
		n = re.sub('\+1', '', n)
		n = re.sub(' ', '', n)
					
		if "(" in n or ")" in n:
			n = re.sub('[(]',"", n)
			n = re.sub('[)]','-',n)
			n = re.sub(' ', '', n)

		if "+1" in n:
			n = re.sub('\+1','',n)
		if re.match(re.compile(r'\-\d{3}\-\d{3}\-\d{4}'),n) is not None:
			n = n[1:]
		if re.match(re.compile(r'\d{1}\-\d{3}\-\d{3}\-\d{4}'),n) is not None:
			n = n[2:]
		if re.match(re.compile(r'\d{9}'),n):
			n = n[:3] + '-' + n[3:6] + '-' + n[6:] 
		if re.match(re.compile(r'\d{6}\-\d{4}'),n):
			n = n[:3] + '-' + n[3:]

	return n


def update_county(name):
	""" 
	Using regex to determine whether particular string has more than one county (separated by : or ;).
	If true, first county enlisted will be returned. If first county is from AL, we replace it with
	'Fulton, GA'.
	"""

	if county_re.search(name):
		if ":" in name:
			name = name.split(':')[0]
		elif ";" in name:
			name = name.split(';')[0]
	if "AL" in name:
		name = "Fulton, GA"
	print name
	return name


def update_postal(name):
	"""Return first five digits of postal code"""

	if postal_re.search(name):
		return name[:5]
	return name
