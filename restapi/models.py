# from django.db import models
from .tasks import run_pandoc_task
from .process.common.extract_images import extract_images
from .process.formatter.convert_txt import convert_txt
from .process.formatter.fix_numbering import fix_numbering
# from .process.formatter.formatter import run_formatter_parser
from .process.common.restore_images import restore_images

import xml.etree.ElementTree as ET

import logging
logger = logging.getLogger(__name__)
import os
import subprocess
import re

from .logging.ErrorTypes import (WRInlineStructureError, WREndStructureError, MSInlineStructureError, MSEndStructureError, ORDInlineStructureError, ORDEndStructureError, MCInlineStructureError, MCEndStructureError, TFInlineStructureError, TFEndStructureError, FIBInlineStructureError, FIBEndStructureError, MATInlineStructureError, MATEndStructureError, InlineNoTypeError, EndAnswerNoTypeError, NoTypeDeterminedError, MarkDownConversionError)
from .logging.WarningTypes import (RespondusTypeEWarning, RespondusTypeMRWarning, RespondusTypeFMBWarning, RespondusTypeMTWarning)

import pypandoc
from enum import Enum
from django.utils.translation import gettext_lazy as _

class Format:

    '''
    main variables(part of final result)
    '''
    filename = None
    maincontent_title = None
    body = None
    end_answers = None
    '''
    intermediary variables
    '''
    pandoc_result = None
    content_after_images_extracted = None
    content_converted_to_txt = None
    content_numbering_fixed = None
    images_list = []
    formatter_result = None

    def __init__(self, temp_file_path, temp_file_name, filename, maincontent_title = None):
        self.temp_file_path = temp_file_path
        self.temp_file_name = temp_file_name
        self.filename = filename
        self.maincontent_title = maincontent_title

    def convert_pandoc(self):
        try:
            result = run_pandoc_task.apply_async(kwargs={"temp_file_path": self.temp_file_path, 
                                                         "filename": self.temp_file_name }, 
                                                         ignore_result=False)
            self.pandoc_result = result.get()
        except Exception as e:
            raise Exception(str(e))
        return self
    
    def extract_images(self):
        self.content_after_images_extracted, self.images_list  = extract_images(self.pandoc_result)
        return self
    
    def convert_txt(self):
        self.content_converted_to_txt = convert_txt(self.temp_file_path, self.filename)
        return self
    
    def fix_numbering(self):
        self.content_numbering_fixed = fix_numbering(self.content_after_images_extracted, self.content_converted_to_txt)
        return self
    
    def run_formatter(self):
        try:
            self.formatter_result = self.run_formatter_parser(self.content_numbering_fixed) 
            
            
            
            
            
            
            if 'maincontent_title' in self.formatter_result.keys():  
                self.maincontent_title = self.formatter_result['maincontent_title']
            if 'body' in self.formatter_result.keys():
                self.body = self.formatter_result['body']
            if 'end_answers' in self.formatter_result.keys():
                self.end_answers = self.formatter_result['end_answers']
        except Exception as e:
            raise Exception(str(e))
        return self
    
    def restore_images(self):
        self.body = restore_images(self.body, self.images_list)


    def run_formatter_parser(self, content):
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


class FormatterError(Exception):
    def __init__(self, reason, message="Formatter Error"):
        self.reason = reason
        self.message = message
    def __str__(self):
        return f'{self.message} -> {self.reason}'


class BaseQuestion:
    def __init__(self, questioncontent=None):
        self.questioncontent = questioncontent
        self.basetextanswers.clear()
        self.answers.clear()
        self.question_header_type = None
        self.question_header_title = None
        self.question_header_points = None
        self.questiontype_by_user = None
        self.questiontype_processed = None


    index = None
    number_provided = None
    questioncontent = None #raw content
    
    question_header_type = None
    question_header_title = None
    question_header_points = None
    
    questiontype_by_user = None
    questiontype_processed = None
    wr_answer = None

    feedback = None
    hint = None

    endanswer = None

    warning_message = []
    info_message = []
    error_message = []

    '''
    These Vars are only used for processing and not part of final result
    '''
    line_elements = None
    question_body_part_list = None

    answers = []
    basetextanswers = []


    def get_line_elements(self):      
        self.questioncontent = os.linesep + self.questioncontent
        os.chdir('/antlr_build/questionparser')
        popen = subprocess.Popen(
            'java -cp questionparser.jar:* questionparser', 
            shell=True,
            stdout=subprocess.PIPE,
            stdin=subprocess.PIPE,
            stderr=subprocess.PIPE
            )
        result, errors = popen.communicate(input=self.questioncontent.encode("utf-8"))
        popen.stdout.close()
        return_code = popen.wait()
        os.chdir('/code')
        try:
            self.line_elements = ET.fromstring(result.decode("utf-8"))
        except Exception as e:
            raise Exception(str(e))


        return self
    
    def extract_question_header_elements(self):

        question_header_type = self.line_elements.find('type')
        if question_header_type is not None:
            self.question_header_type = self.trim_text(question_header_type.text)


        question_header_title = self.line_elements.find('title')
        if question_header_title is not None:
            self.question_header_title = self.trim_text(question_header_title.text) 

        question_header_points = self.line_elements.find('points')
        if question_header_points is not None:
            filterpoint = re.search("\d+((.|,)\d+)?", question_header_points.text)
            self.question_header_points = float(filterpoint.group())
        return self

    def get_question_body_parts_list (self):
        question_body = self.line_elements.find("question_body")
        if question_body is None:
            raise Exception("Question_body empty")

        self.question_body_part_list = question_body.findall("question_body_part")
        if self.question_body_part_list is None:
            raise Exception("Question_body empty")
        return self

    def get_number_provided(self):
        try:
            # save question number that was provided
            number_provided = self.question_body_part_list[0].find('prefix')
            if number_provided is not None:
                filter_question_number = re.search("\d+", number_provided.text)
                self.number_provided = filter_question_number.group()
                return self
            # logger.debug("Finished getting question number")
        except Exception as e:
            raise Exception(f"failed to extract number_provided : {str(e)}")
    
    def separate_question_and_answers(self):
        answer_list = []
        part_of_question_list = []
        try:
            # logger.debug( f"#{str(question.number_provided)} Starting splitting body_part into question_content and answers block")
            # only if there are multiple question_body parts then proceed to splitting
            if (len(self.question_body_part_list) == 1) and (self.question_body_part_list[0].get('prefix_type') == 'NUMLIST_PREFIX'):
                part_of_question_list.append(self.question_body_part_list[0])
            else:
                # Filter out the last letter enumerated list so that it can be set as the answerlist
                start_of_list_found = False
                # Start iterating from the last item going up untill the index "a" is found and continue adding the rest of the lists as question content
                for question_body_part in reversed(self.question_body_part_list):
                    if not start_of_list_found:
                        answer_list.append(question_body_part)
                    else:
                        part_of_question_list.append(question_body_part)
                    if question_body_part.get('prefix_type') == "LETTERLIST_PREFIX" or question_body_part.get('prefix_type') == "CORRECT_ANSWER":
                        check_index = ''.join(filter(str.isalpha, question_body_part.find('prefix').text.lower()))
                        if check_index == "a":
                            start_of_list_found = True
                # because we started from the last item we need to reverse the list to bring in correct order
                answer_list = answer_list[::-1]
                part_of_question_list = part_of_question_list[::-1]
            # logger.debug( f"#{str(question.number_provided)} Finished plitting body_part into question_content and answers block")
        except Exception as e:
            raise Exception(f"failed to split body_part into question_content and answers block : {e}")
        
        try:
            # Combine feedback and answers 
            # Check if first item is LETTERLIST_PREFIX or CORRECT_ANSWER
            if (answer_list[0].get('prefix_type') == "LETTERLIST_PREFIX" or answer_list[0].get('prefix_type') == "CORRECT_ANSWER"):
                # raise Exception("First item in Answer list is not a Letterlist item")
                for answer in answer_list:
                    if answer.get('prefix_type') == "LETTERLIST_PREFIX":
                        current_answer = {
                            "answer_prefix": answer.find('prefix').text,
                            "answer_content": answer.find('content').text,
                            "correct": False,
                            "feedback": None
                            }
                        self.answers.append(current_answer)
                    elif answer.get('prefix_type') == "CORRECT_ANSWER":
                        current_answer = {
                            "answer_prefix": answer.find('prefix').text,
                            "answer_content": answer.find('content').text,
                            "correct": True,
                            "feedback": None
                            }
                        self.answers.append(current_answer)
                    elif answer.get('prefix_type') == "NUMLIST_PREFIX":
                        current_answer = self.answers.pop()
                        current_answer.update({"content": current_answer.get("content") + answer.find('content').text})
                        self.answers.append(current_answer)
                    elif answer.get('prefix_type') == "FEEDBACK":
                        current_answer = self.answers.pop()
                        current_answer.update({"feedback": answer.find('content').text})
                        self.answers.append(current_answer)
                    elif answer.get('prefix_type') == "HINT":
                        continue
            # logger.debug( f"#{str(question.number_provided)} Finished combining answer block elements items into answers")
        except Exception as e:
            raise Exception(f"failed to combine answer block elements items into one answers block{e}")
        

        try:
            # Combine question content, any lists, feedback and hint in one dict 
            question_from_xml = {
                "question_content": "",
                "feedback": "",
                "hint": ""
                }        
            for index, question_content_item in enumerate(part_of_question_list):
                if question_content_item.get('prefix_type') == "FEEDBACK":
                    question_from_xml.update({"feedback": question_content_item.find('content').text})
                elif question_content_item.get('prefix_type') == "HINT":
                    question_from_xml.update({"hint": question_content_item.find('content').text})
                else:
                    question_content = question_from_xml.get("question_content")
                    question_content_to_append = ""
                    if index > 0:
                        question_content_to_append = question_content_item.find('prefix').text
                    question_content_to_append = question_content_to_append + question_content_item.find('content').text
                    question_from_xml.update({"question_content": question_content + question_content_to_append})

            if question_from_xml is not None:
                question_text = question_from_xml.get("question_content")
                self.questioncontent = question_text
            
            self.wr_answer = self.line_elements.find("wr_answer")
            question_feedback = question_from_xml.get("feedback")
            if question_feedback is not None:
                self.feedback = question_feedback
            question_hint = question_from_xml.get("hint")
            if question_hint is not None:
                self.hint = question_hint

        except Exception as e:
            raise Exception(f"failed to combine question content, any lists, feedback and hint in one dict")

        for answer in self.answers:
            self.basetextanswers.append(BaseTextAnswer(answer))

        return self
    
    def check_questiontype(self):
        if self.endanswer == None:   
            self.questiontype_processed = self.__check_inline_questiontype()
        else:
            self.questiontype_processed = self.__check_endanswer_questiontype()
        return self
        

    def compare_user_type_with_processed_type(self):
        match self.questiontype_by_user:
            case 'WR' | 'E':
                if self.questiontype_by_user == 'E':
                    self.__add_respondus_type_warning(type_found='E', type_recommended='WR')
                if self.endanswer == None:
                    if not (self.questiontype_processed == 'inline_WR_keyword' or 
                            self.questiontype_processed == 'inline_WR_list'):
                        self.__add_inline_type_error(type_found='WR')    
                else:
                    if not self.questiontype_processed == 'endanswer_WR':
                        self.__add_endanswer_type_error(type_found='WR')
            case 'MS' | 'MR':
                if self.questiontype_by_user == 'MR':
                    self.__add_respondus_type_warning(type_found='MR', type_recommended='MS')
                if self.endanswer == None:
                    if not (self.questiontype_processed == 'inline_MS'):
                        self.__add_inline_type_error(type_found='MS')    
                else:
                    if not self.questiontype_processed == 'endanswer_MS':
                        self.__add_endanswer_type_error(type_found='MS')
            case 'ORD':
                if self.endanswer == None:
                    if not (self.questiontype_processed == 'inline_ORD'):
                        self.__add_inline_type_error(type_found='ORD')    
                else:
                    if not self.questiontype_processed == 'endanswer_ORD':
                        self.__add_endanswer_type_error(type_found='ORD')
            case 'MC':
                if self.endanswer == None:
                    if not (self.questiontype_processed == 'inline_MC'):
                        self.__add_inline_type_error(type_found='MC')    
                else:
                    if not self.questiontype_processed == 'endanswer_MC':
                        self.__add_endanswer_type_error(type_found='MC')
            case 'TF':
                if self.endanswer == None:
                    if not (self.questiontype_processed == 'inline_TF'):
                        self.__add_inline_type_error(type_found='TF')    
                else:
                    if not self.questiontype_processed == 'endanswer_TF':
                        self.__add_endanswer_type_error(type_found='TF')
            case 'FIB' | 'FMB':
                if self.questiontype_by_user == 'FMB':
                    self.__add_respondus_type_warning(type_found='FMB', type_recommended='FIB')
                if self.endanswer == None:
                    if not (self.questiontype_processed == 'inline_FIB'):
                        self.__add_inline_type_error(type_found='FIB')    
                else:
                    if not self.questiontype_processed == 'endanswer_FIB':
                        self.__add_endanswer_type_error(type_found='FIB')
            case 'MAT' | 'MT':
                if self.questiontype_by_user == 'MT':
                    self.__add_respondus_type_warning(type_found='MT', type_recommended='MAT')
            case _:
                logger.debug("question type not given by user")
        return self


    def build_question(self):
        match self.questiontype_processed:
            case 'inline_MC':
                build_inline_MC(question, answers, is_random, enumeration)
            case 'endanswer_MC':
                build_endanswer_MC(question, answers, endanswer, is_random, enumeration)
            case 'inline_TF':
                build_inline_TF(question, answers, enumeration)
            case 'endanswer_TF':
                build_endanswer_TF(question, answers, endanswer, enumeration)
            case 'inline_MS':
                build_inline_MS(question, answers, is_random, enumeration)
            case 'endanswer_MS':
                build_endanswer_MS(question, answers, endanswer, is_random, enumeration)
            case 'inline_WR_keyword':
                build_inline_WR_with_keyword(question, wr_answer)
            case 'inline_WR_list':
                build_inline_WR_with_list(question, answers)
            case 'endanswer_WR':
                build_endanswer_WR_with_list(question, endanswer, wr_answer)
            case 'inline_FIB':
                build_inline_FIB(question)
            case 'endanswer_FIB':
                build_endanswer_FIB(question, endanswer)
            case 'inline_MAT':
                build_inline_MAT(question, answers)
            case 'endanswer_MAT':
                build_endanswer_MAT(question, endanswer)
            case 'inline_ORD':
                build_inline_ORD(question, answers)
            case 'endanswer_ORD':
                build_endanswer_ORD(question, endanswer)
            case 'inline_NO_TYPE':
                error_message = "Cannot determined the inline question type."
                add_error_message(question, error_message)
                raise InlineNoTypeError(error_message)
            case 'endanswer_NO_TYPE':
                error_message = "Cannot determined the end answer question type."
                add_error_message(question, error_message)
                raise EndAnswerNoTypeError(error_message)
        

    def __add_respondus_type_warning(self, type_found, type_recommended):
        self.warning_message.append(f'Respondus format "Type: {type_found}" was found on the file. Please use "Type: {type_recommended}" instead.')

    def __add_inline_type_error(self, type_found):
        self.error_message.append(f"Inline question structure doesn't conform to {type_found} type question format.")

    def __add_endanswer_type_error(self, type_found):
        self.error_message.append(f"End answer question structure doesn't conform to {type_found} type question format.")



    def __check_inline_questiontype(self):
        answers_length = len(self.answers)
        marked_answers_count = 0
        unmarked_answers_count = 0
        matching_answers_count = 0
        KeywordTrueFound = False
        KeywordFalseFound = False

        is_fib = re.search(r"\[(.*?)\]", self.questioncontent)

        if answers_length == 0:
            if is_fib:
                # ====================  FIB confirmed  ====================
                logger.debug("Question Type determined: inline_FIB")   
                return 'inline_FIB'
            
            if self.wr_answer != None:
                # ====================  WR confirmed  ====================
                logger.debug("Question Type determined: inline_WR_keyword")
                return 'inline_WR_keyword'

        for answer in self.answers:
            # answer_text = markdown_to_plain(answer.find('content').text.lower())
            answer_text = self.markdown_to_plain(answer.get("answer_content").lower())
            answer_text = self.trim_text(answer_text)
            is_correct = answer.get('correct')
            if is_correct:
                marked_answers_count += 1
            if not is_correct:
                unmarked_answers_count += 1

            if answer_text == 'true':
                KeywordTrueFound = True

            if answer_text == 'false':
                KeywordFalseFound = True
            matching_answers = re.search(r"(.*)=(.*)", answer_text)

            if matching_answers is not None:
                matching_answers_count += 1
            
        if answers_length == 2 and KeywordTrueFound == True and KeywordFalseFound == True:
            # ====================  TF confirmed  ====================
            logger.debug("Question Type determined: inline_TF")
            return 'inline_TF'

        if marked_answers_count == 1 and (self.questiontype_by_user != 'MS' and self.questiontype_by_user != 'MR'):
            # ====================  MC confirmed  ====================
            logger.debug("Question Type determined: inline_MC")   
            return 'inline_MC'

        if marked_answers_count > 1 or (self.questiontype_by_user == 'MS' or self.questiontype_by_user == 'MR'):
            # ====================  MS confirmed  ====================
            logger.debug("Question Type determined: inline_MS")   
            return 'inline_MS'

        if matching_answers_count == answers_length and matching_answers_count > 1 :
            # ====================  MAT confirmed  ====================
            logger.debug("Question Type determined: inline_MAT")   
            return 'inline_MAT'

        if (unmarked_answers_count == 1 and answers_length == 1) or (self.questiontype_by_user == 'WR' or self.questiontype_by_user == 'E'):
            # ====================  WR confirmed  ====================
            logger.debug("Question Type determined: inline_WR_list")   
            return 'inline_WR_list'

        if answers_length > 0 and unmarked_answers_count == answers_length:
            # ====================  ORD confirmed  ====================
            logger.debug("Question Type determined: inline_ORD")   
            return 'inline_ORD'
        logger.debug("Question Type determined: inline_NO_TYPE")   
        return 'inline_NO_TYPE'

        


    def __check_endanswer_questiontype(self):
        answers_length = len(self.answers)
        endanswer_text = self.markdown_to_plain(self.endanswer.answer.lower())
        endanswer_text = self.trim_text(endanswer_text)

        if answers_length > 0:
            # possible TF, MC, MS
            answer_list = list(map(str.strip, endanswer_text.split(',')))
            answer_key_length = len(answer_list)
            KeywordTrueFound = False
            KeywordFalseFound = False
        
            for answer in self.answers:
                answer_text = self.markdown_to_plain(answer.find('content').text.lower())
                answer_text = self.trim_text(answer_text)

                for choice_answer in answer_list:
                    correctanswer_index =  (ord(choice_answer)-97)
                    
                    if correctanswer_index <= (answers_length-1):
                        # answer index exist
                        pass
                    else:
                        return 'endanswer_NO_TYPE'


                if answer_text == 'true':
                    KeywordTrueFound = True

                if answer_text == 'false':
                    KeywordFalseFound = True
            
            if answers_length == 2 and KeywordTrueFound == True and KeywordFalseFound == True:
                # ====================  TF confirmed  ====================
                return 'endanswer_TF'
                
            if answer_key_length == 1 and (self.questiontype_by_user != 'MS' and self.questiontype_by_user != 'MR'):
                # ====================  MC confirmed  ====================
                return 'endanswer_MC'

            if (self.questiontype_by_user == 'MS' or self.questiontype_by_user == 'MR') or answer_key_length > 1:
                # ====================  MS confirmed  ====================
                return 'endanswer_MS'
        
        else:
            # possible FIB, MAT, ORD, WR
            matching_answers_count = 0
            is_fib = re.findall(r"\[(.*?)\]", self.questioncontent)
            answer_list = list(map(str.strip, endanswer_text.split(';')))
            answer_key_length = len(answer_list)
            for answer in answer_list:
                matching_answer = re.search(r"(.*)=(.*)", answer)

                if matching_answer is not None:
                    matching_answers_count += 1
            
            if matching_answers_count == answer_key_length and matching_answers_count > 1 :
                # =========================  MAT confirmed =======================
                return 'endanswer_MAT'
                
            if len(is_fib) == answer_key_length:
                # =========================  FIB confirmed =======================
                return 'endanswer_FIB'

            if answer_key_length > 1:
                # =========================  ORD confirmed =======================
                return 'endanswer_ORD'

            if answer_key_length == 1:
                # =========================  WR confirmed =======================
                return 'endanswer_WR'

        return 'endanswer_NO_TYPE'


    # def build_inline_MC(question, answers, is_random, enumeration):

    #     logger.debug("building inline mc")
    #     question.questiontype = 'MC'
    #     question.save()

    #     mc_object = MultipleChoice.objects.create(question=question)
    #     if is_random == True:
    #         mc_object.randomize = True

    #     if enumeration:
    #         mc_object.enumeration = enumeration
    #     mc_object.save()
    #     # grab all answers
    #     for answer_order, answer_item in enumerate(answers):
    #         mc_answerobject = MultipleChoiceAnswer.objects.create(multiple_choice=mc_object)
    #         answer_index = trim_text(answer_item.get('answer_prefix'))
    #         mc_answerobject.index = re.sub(r'[\W_]', '', answer_index)
    #         mc_answerobject.order = answer_order + 1
    #         mc_answerobject.answer = trim_md_to_html(answer_item.get('answer_content'))
    #         answer_feedback = answer_item.get('feedback')
    #         is_correct = answer_item.get('correct')
    #         if answer_feedback != None:
    #             mc_answerobject.answer_feedback = trim_md_to_html(answer_feedback)

    #         if is_correct:
    #             mc_answerobject.weight = 100

    #         mc_answerobject.save()


    @staticmethod
    def markdown_to_plain(text):
        plain_text = pypandoc.convert_text(text, format="markdown_github+fancy_lists+emoji", to="plain", extra_args=['--wrap=none'])
        return plain_text


    @staticmethod
    def trim_text(txt):
        text = txt.strip()
        text = re.sub('<!-- -->', '', text)
        text = re.sub('<!-- NewLine -->', '\n', text, flags=re.IGNORECASE)
        text = text.strip(" \n")
        return text


class Section:
    '''
    main sectioner variables
    '''
    title = None
    order = None
    is_main_content = None
    sectionheader = None
    sectioncontent = None

    def __init__(self, title=None,
                 order=None,
                 is_main_content=None, 
                 sectionheader=None,
                 sectioncontent=None):
        self.title = title
        self.order = order
        self.is_main_content = is_main_content
        self.sectionheader = sectionheader
        self.sectioncontent = sectioncontent

    '''
    section variables for processing
    '''
    content_from_formatter = None
    content_after_images_extracted = None


class SectionList:
    content = None
    sections_list = []
    def __init__(self, content=None):
        self.content = content
        self.sections_list.clear()

    def run_sectioner(self):
        logger.info("sectioner starting")
        
        content = os.linesep + self.content
        
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

                self.sections_list.append(sectionobj)
        except:
            raise SectionerError("Error extracting section contents")    
        
        return self
        

class QuestionList:
    content = None
    question_list = []

    def __init__(self, content=None):
        self.content = content
        self.question_list.clear()

class SectionerError(Exception):
    def __init__(self, reason, message="Sectioner Error"):
        self.reason = reason
        self.message = message
    def __str__(self):
        return f'{self.message} -> {self.reason}'
    


class BaseTextAnswer():
    def __init__(self, answer):
        self.answer_prefix = answer['answer_prefix']
        self.MarkedWithStar = answer['correct']
        self.answer_content = answer['answer_content']
        self.feedback = answer['feedback']

    class EnumeratorTypes(Enum):
        LOWERCASELETTERS = 'LOWERCASELETTERS', _('LOWERCASELETTERS')
        UPPERCASELETTERS = 'UPPERCASELETTERS', _('UPPERCASELETTERS')
        NUMBERS = 'NUMBERS', _('NUMBERS')
        ROMAN_NUMERALS = 'ROMAN_NUMERALS', _('ROMAN_NUMERALS')
        UPPERCASE_ROMAN_NUMERALS = 'UPPERCASE_ROMAN_NUMERALS', _('UPPERCASE_ROMAN_NUMERALS')
        NO_ENUMERATION = 'NO_ENUMERATION', _('NO_ENUMERATION')

    enumerator = EnumeratorTypes.LOWERCASELETTERS
    answer_prefix = None
    answer_content = None
    MarkedWithStar = False

    def __str__(self):
        return f"[{self.answer_prefix}][marked*:{ self.MarkedWithStar }][content:{self.answer_content[0:20]}]"

