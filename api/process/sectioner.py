import os
import subprocess
import xml.etree.ElementTree as ET
# from .process_helper import markdown_to_plain, trim_text, markdown_to_html
from api.tasks import markdown_to_plain, trim_text, markdown_to_html
from ..models import Section

import logging
newlogger = logging.getLogger(__name__)
from api.logging.logging_adapter import FilenameLoggingAdapter

# This is to split sections into separate objects
def run_sectioner(questionlibrary):
    logger = FilenameLoggingAdapter(newlogger, {
        'filename': questionlibrary.temp_file.name,
        'user_ip': questionlibrary.user_ip
        })

    try:
        os.chdir('/antlr_build/sectioner')
        result = subprocess.run(
            'java -cp sectioner.jar:* sectioner',
            shell=True,
            input=questionlibrary.formatter_output.encode("utf-8"),
            capture_output=True)
        os.chdir('/code')
    except:
        raise SectionerError("error while reading sections")

    # print(result.stdout.decode("utf-8"))
    questionlibrary.sectioner_output = result.stdout.decode("utf-8")
    questionlibrary.save()

    logger.debug("starting sections extraction")

    root = None
    try:
        root = ET.fromstring(result.stdout.decode("utf-8"))
    except:
        raise SectionerError("Sectioner results empty")

    if len(root) == 0:
        raise SectionerError("No Sections found")

    subsection_count = 0
    try:
        for section in root:
            sectionobject = Section.objects.create(
                question_library=questionlibrary)
            sectionobject.save()
            sectionobject.order = int(section.attrib.get("id")) + 1
            sectiontitle = section.find('title')
            if sectiontitle is not None:
                section_title_text = markdown_to_plain(sectiontitle.text)
                section_title_text = section_title_text.replace('\n', ' ')
                sectionobject.title = trim_text(section_title_text)

            maincontent = section.find('maincontent')
            if maincontent is not None:
                sectionobject.raw_content = maincontent.text
                sectionobject.is_main_content = True
                sectionobject.title = questionlibrary.main_title

            sectiontext = section.find('sectiontext')
            if sectiontext is not None:
                section_text = trim_text(sectiontext.text)
                sectionobject.text = markdown_to_html(section_text)
                sectionobject.is_main_content = False

            sectioncontent = section.find('sectioncontent')
            if sectioncontent is not None:
                sectionobject.raw_content = sectioncontent.text
                sectionobject.is_main_content = False
                subsection_count += 1
            sectionobject.save()
    except:
        raise SectionerError("Error extracting section contents")
    return subsection_count

class SectionerError(Exception):
    def __init__(self, reason, message="Sectioner Error"):
        self.reason = reason
        self.message = message
    def __str__(self):
        return f'{self.message} -> {self.reason}'