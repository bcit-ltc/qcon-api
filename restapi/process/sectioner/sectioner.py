import os
import subprocess
import xml.etree.ElementTree as ET
# from .process_helper import markdown_to_plain, trim_text, markdown_to_html
# from api.tasks import markdown_to_plain, trim_text, markdown_to_html
from ...models import Section

import logging
newlogger = logging.getLogger(__name__)
from api.logging.logging_adapter import FilenameLoggingAdapter

# This is to split sections into separate objects
def run_sectioner(sectionlist):
    logger = FilenameLoggingAdapter(newlogger, {
        'filename': ""
        })
    logger.info("sectioner starting")
    
    content = os.linesep + sectionlist.content
    
    try:
        os.chdir('/antlr_build/sectioner')
        result = subprocess.run(
            'java -cp sectioner.jar:* sectioner',
            shell=True,
            input=content.encode("utf-8"),
            capture_output=True)
        os.chdir('/code')
    except:
        raise SectionerError("error while reading sections")

    logger.debug("starting sections extraction")

    root = None
    try:
        root = ET.fromstring(result.stdout.decode("utf-8"))
    except:
        raise SectionerError("Sectioner results empty")

    # logger.info(ET.tostring(root, encoding='utf8'))

    if len(root) == 0:
        raise SectionerError("No Sections found")

    try:
        for section in root:
            sectionobj = Section()
            
            sectionobj.order = int(section.attrib.get("id")) + 1
            sectiontitle = section.find('title')
            if sectiontitle is not None:
                sectionobj.title = sectiontitle.text

            maincontent = section.find('maincontent')
            if maincontent is not None:
                sectionobj.title = content
                sectionobj.is_main_content = True
                sectionobj.sectioncontent = maincontent.text

            sectionheader = section.find('sectionheader')
            if sectionheader is not None:
                sectionobj.is_main_content = False
                sectionobj.sectionheader = sectionheader.text

            sectioncontent = section.find('sectioncontent')
            if sectioncontent is not None:
                sectionobj.is_main_content = False
                sectionobj.sectioncontent = sectioncontent.text

            sectionlist.sections_list.append(sectionobj)
    except:
        raise SectionerError("Error extracting section contents")    
    
    return sectionlist


class SectionerError(Exception):
    def __init__(self, reason, message="Sectioner Error"):
        self.reason = reason
        self.message = message
    def __str__(self):
        return f'{self.message} -> {self.reason}'