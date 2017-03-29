import os
import xml.etree.ElementTree as xml

xml_path = os.environ.get('XML_PATH', 'nosetests.xml')


def parse_xml():
    tree = xml.parse(xml_path)
    root = tree.getroot()

    tcases = {}

    for tc in root.iter('testcase'):
        tc_info = tc.attrib
        tcases[tc_info['name']] = tc_info['status']

    return tcases
