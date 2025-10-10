from bs4 import BeautifulSoup
from .extract_images import extract_images
from .formatter import run_formatter
from .sectioner import run_sectioner
from .splitter import Splitter
from .endanswers import get_endanswers
from .parser import run_parser
from .convert_txt import convert_txt
from .fix_numbering import fix_numbering
import socket
from api.tasks import run_pandoc_task
from django.conf import settings
import logging
newlogger = logging.getLogger(__name__)
# from api.logging.contextfilter import QuestionlibraryFilenameFilter
# logger.addFilter(QuestionlibraryFilenameFilter())
from api.logging.logging_adapter import FilenameLoggingAdapter

from api.logging.ErrorTypes import *
import os

class Process:
    def __init__(self, questionlibrary) -> None:
        self.questionlibrary = questionlibrary
        self.images_extracted = 0
        self.subsection_count = 0
        self.questions_expected = 0
        self.questions_processed = 0
        self.endanswers_count = 0
        self.question_info_count = 0
        self.question_warning_count = 0
        self.question_error_count = 0

    def run_pandoc(self):
        logger = FilenameLoggingAdapter(newlogger, {
            'filename': self.questionlibrary.temp_file.name,
            'user_ip': self.questionlibrary.user_ip
            })
        try:
            result = run_pandoc_task.apply_async(kwargs={"questionlibrary_id":self.questionlibrary.id}, ignore_result=False)
            pandoc_task_result = result.get()
            # logger.debug(pandoc_task_result)
            self.questionlibrary.pandoc_output = pandoc_task_result
        except Exception as e:
            raise Exception(str(e))

        if self.questionlibrary.pandoc_output == None:
            raise MarkDownConversionError("Pandoc output string is empty")

    def convert_txt(self):
        convert_txt(self.questionlibrary)

    def fix_numbering(self):
        # logger = FilenameLoggingAdapter(newlogger, {
        #     'filename': self.questionlibrary.temp_file.name,
        #     'user_ip': self.questionlibrary.user_ip
        #     })
        # logger.debug("starting pandoc html to md")
        # try:
        #     result = convert_html_to_md.apply_async(kwargs={"questionlibrary_id":self.questionlibrary.id}, ignore_result=False)
        #     convert_html_to_md_task_result = result.get()
        #     logger.debug("pdf to md result")
        #     logger.debug(convert_html_to_md_task_result)
        #     self.questionlibrary.txt_output = convert_html_to_md_task_result
        #     self.questionlibrary.save()
        # except Exception as e:
        #     raise Exception(str(e))

        fix_numbering(self.questionlibrary)
        
    def extract_images(self):
        self.images_extracted = extract_images(self.questionlibrary)

    def run_formatter(self):
        logger = FilenameLoggingAdapter(newlogger, {
            'filename': self.questionlibrary.temp_file.name,
            'user_ip': self.questionlibrary.user_ip
            })
        logger.debug("starting formatter antlr process")
        run_formatter(self.questionlibrary)

    # This is to split sections into separate objects
    def run_sectioner(self):
        logger = FilenameLoggingAdapter(newlogger, {
            'filename': self.questionlibrary.temp_file.name,
            'user_ip': self.questionlibrary.user_ip
            })
        logger.debug("starting sectioner antlr process")
        self.subsection_count = run_sectioner(self.questionlibrary)

    def run_splitter(self):
        logger = FilenameLoggingAdapter(newlogger, {
            'filename': self.questionlibrary.temp_file.name,
            'user_ip': self.questionlibrary.user_ip
            })
        logger.debug("starting splitter antlr process")
        splitter = Splitter(self.questionlibrary)
        self.questions_expected = splitter.run_splitter()

    def get_endanswers(self):
        self.endanswers_count = get_endanswers(self.questionlibrary)

    def run_parser(self):
        logger = FilenameLoggingAdapter(newlogger, {
            'filename': self.questionlibrary.temp_file.name,
            'user_ip': self.questionlibrary.user_ip
            })
        logger.debug("starting questionparser antlr process")
        run_parser(self.questionlibrary)

    def sendformat(self, status, statustext, data):

        return {
                'hostname': socket.gethostname(),
                'version': settings.APP_VERSION,
                'status': status,
                'statustext': statustext,
                'images_count': str(self.images_extracted),
                'section_count': str(self.subsection_count),
                'questions_count': str(self.questions_expected),
                'endanswer_count': str(self.endanswers_count),
                'question_info_count': str(self.question_info_count),
                'question_warning_count': str(self.question_warning_count),
                'question_error_count': str(self.question_error_count),
                'data': data
            }
# ++++++++++++++++++++++++++++++++===================================
