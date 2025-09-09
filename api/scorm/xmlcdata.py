# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

import six
import xml.etree.ElementTree as ET


def CDATA(text=None):
    element = ET.Element('![CDATA[')
    element.text = text
    return element

ET._original_serialize_xml = ET._serialize_xml


def _serialize_xml2(write, elem, encoding, qnames, namespaces, orig=ET._serialize_xml):
	if elem.tag == '![CDATA[':
	    write("\n<%s%s]]>\n" % \
	          (elem.tag, elem.text.encode(encoding, "xmlcharrefreplace")))
	    return
	return orig(write, elem, encoding, qnames, namespaces)

def _serialize_xml3(write, elem, qnames, namespaces,
                    short_empty_elements=None,
                    orig=ET._serialize_xml):
    if elem.tag == '![CDATA[':
        write("\n<{tag}{text}]]>\n".format(
            tag=elem.tag, text=elem.text))
        return
    if short_empty_elements:
        # python >=3.3
        return orig(write, elem, qnames, namespaces, short_empty_elements)
    else:
        # python <3.3
        return orig(write, elem, qnames, namespaces)

if six.PY3:
    ET._serialize_xml = \
        ET._serialize['xml'] = _serialize_xml3
elif six.PY2:
    ET._serialize_xml = \
        ET._serialize['xml'] = _serialize_xml2