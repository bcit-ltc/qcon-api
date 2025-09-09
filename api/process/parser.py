import os
import xml.etree.ElementTree as ET
from ..models import EndAnswer, Section, Question
from django.conf import settings

import logging
newlogger = logging.getLogger(__name__)
from api.logging.logging_adapter import FilenameLoggingAdapter

from api.tasks import parse_question

from celery import group

def run_parser(questionlibrary):
    logger = FilenameLoggingAdapter(newlogger, {
        'filename': questionlibrary.temp_file.name,
        'user_ip': questionlibrary.user_ip
        })

    import time
    sections = questionlibrary.get_sections()
    if len(sections) == 0:
        raise ParserError("No sections found for the parser to work on")
    endanswers = EndAnswer.objects.filter(question_library=questionlibrary)    
    question_count = 0
    section_count = 0
    start_time = time.time()
    for section in sections:
        questions = Question.objects.filter(section=section)
        # if section.is_main_content:
        #     logger.debug("Root section:")
        # else:
        #     section_count += 1
        #     logger.debug("Section", str(section.order), ":", section.title )

        section_start_time = time.time()
        section_question_count = 0

        # ----------------------- DELETE empty questions before adding to thread
        for question in questions:
            # discard empty question
            if question.raw_content is None:
                question.delete()

        # TODO ----------------------- Clean endanswers


        # ----------------------- Run parser task in celery
        try:
            questions = Question.objects.filter(section=section)
            tasklist = []
            for idx, question in enumerate(questions):
                if len(endanswers) != 0:
                    tasklist.append(parse_question.s(question.id, endanswers[idx].id))
                else:
                    tasklist.append(parse_question.s(question.id))
                section_question_count += 1
            lazy_group = group(tasklist)
            logger.info("Starting group task ... ")
            promise = lazy_group()
            result = promise.get()
            logger.debug(result)
            for item in result:
                if not item == 'success':
                    logger.error(item)
        except Exception as e:
            logger.error(str(e))
            raise ParserError("uncaught error in Parser group task")

        question_count += section_question_count
        section_end_time = time.time()
        section.processing_time = section_end_time - section_start_time
        section.save()
        logger.debug(f"  Section total questions : {section_question_count}")
        logger.debug(f"  Section processing time : {section.processing_time}")
    logger.info(f'Total Processing time for Parser : {time.time() - start_time}')
    logger.debug(f"Processing Time Total :  {time.time() - start_time}")

class ParserError(Exception):
    def __init__(self, reason, message="Parser Error"):
        self.reason = reason
        self.message = message
    def __str__(self):
        return f'{self.message} -> {self.reason}'
