from ast import Not
import os
import xml.etree.ElementTree as ET
import subprocess
import re

import logging
logger = logging.getLogger(__name__)

def run_formatter_parser(content, filename):
    root = None

    try:
        os.chdir('/antlr_build/formatter')
        result = subprocess.run('java -cp formatter.jar:* formatter',
                                shell=True,
                                input=content.encode("utf-8"),
                                capture_output=True)
        os.chdir('/code')
        root = ET.fromstring(result.stdout.decode("utf-8"))
    except:
        raise FormatterError("Internal error while converting file")
    
    logger.debug("starting formatter extraction")
    
    format = {}

# # ==================================== MAINCONTENT TITLE
    maincontenttitle = root.find('maincontent_title')
    logger.debug("checking maincontent title")
    if maincontenttitle is not None:
        main_title = (maincontenttitle.text).strip()
        if main_title:
            # format["maincontent_title"] = (trim_text(main_title)).lstrip('# ')
            format["maincontent_title"] = main_title
    else:
        format["maincontent_title"] = None
    
# # ==================================== BODY
    body = root.find('body')
    logger.debug("checking formatter body")
    if body is not None:
        # questionlibrary.formatter_output = body.text.rstrip() + "\n"
        # questionlibrary.save()
        format["body"] = body.text.rstrip() + "\n"
    else:
        raise FormatterError("document body not found")

# ==================================== END ANSWERS

    end_answers = root.find('end_answers')
    logger.debug("checking for endanswers block")
    if end_answers is not None:
        logger.debug("endanswers block found")
        # questionlibrary.end_answers_raw = end_answers.text
        # questionlibrary.save()
        format["end_answers"] = end_answers.text
    else:
        logger.info("No endanswers block found")
        format["end_answers"] = None

    return format






# def run_formatter_parser(content, filename):
#     logger = FilenameLoggingAdapter(newlogger, {'filename': filename})
#     root = None

#     try:
#         os.chdir('/antlr_build/formatter')
#         result = subprocess.run('java -cp formatter.jar:* formatter',
#                                 shell=True,
#                                 input=content.encode("utf-8"),
#                                 capture_output=True)
#         os.chdir('/code')
#         root = ET.fromstring(result.stdout.decode("utf-8"))
#     except:
#         raise FormatterError("Internal error while converting file")
    
#     logger.debug("starting formatter extraction")

#     # format = Format()
# # ==================================== SECTION INFO

#     maincontenttitle = root.find('maincontent_title')
#     logger.debug("checking maincontent title")
#     if maincontenttitle is not None:
#         main_title = (maincontenttitle.text).strip()
#         if main_title:
#             format.maincontent_title = (trim_text(main_title)).lstrip('# ')
#     else:
#         format.maincontent_title = None
# # ==================================== BODY

#     body = root.find('body')
#     if body is not None:
#         # questionlibrary.formatter_output = body.text.rstrip() + "\n"
#         # questionlibrary.save()
#         format.body = body.text.rstrip() + "\n"
#     else:
#         raise FormatterError("document body not found")

# # ==================================== END ANSWERS

#     end_answers = root.find('end_answers')
#     logger.debug("checking for endanswers block")
#     if end_answers is not None:
#         logger.debug("endanswers block found")
#         # questionlibrary.end_answers_raw = end_answers.text
#         # questionlibrary.save()
#         format.end_answers = end_answers.text
#     else:
#         logger.info("No endanswers block found")

#     return format

class FormatterError(Exception):
    def __init__(self, reason, message="Formatter Error"):
        self.reason = reason
        self.message = message
    def __str__(self):
        return f'{self.message} -> {self.reason}'
