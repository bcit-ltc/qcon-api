import os
import subprocess
import xml.etree.ElementTree as ET
from ..models import Section
from ..models import Question
# from .process_helper import trim_text
from api.tasks import trim_text
import logging
newlogger = logging.getLogger(__name__)
from api.logging.logging_adapter import FilenameLoggingAdapter

import re


class Splitter:
    def __init__(self, questionlibrary) -> None:
        self.questionlibrary = questionlibrary
        self.total_questions_found = 0
        self.current_section_starts_with_1 = False

    def run_splitter(self):
        logger = FilenameLoggingAdapter(newlogger, {
            'filename': self.questionlibrary.temp_file.name,
            'user_ip': self.questionlibrary.user_ip
            })

        sections = self.questionlibrary.get_sections()    
        for section in sections:

            # Fails on empty section need to try/except because empty sections are deleted after splitter
            try:
                self.__add_newlines_before_question(section)
            except Exception as e:
                logger.info(str(e))

            try:
                section.questions_expected = self.__split_questions(section)
                section.save()
            except SplitterError as e:
                logger.debug("No questions detected. Discarding empty section")
                section.delete()
            # remove empty sections
            if section.questions_expected == 0:        
                section.delete()
        # return questions_count
        return self.total_questions_found

    def __add_newlines_before_question(self, sectionobject):  
        logger = FilenameLoggingAdapter(newlogger, {
            'filename': self.questionlibrary.temp_file.name,
            'user_ip': self.questionlibrary.user_ip
            })      
       
        lines_altered = []
        lines_original = sectionobject.raw_content.splitlines()
        # logger.debug("raw_content")
        # logger.debug(section.raw_content)
        # logger.debug("lines original")
        # logger.debug(lines_original)

        # check if the first question was found already
        number_1_found = False
        for line in lines_original:
            number_prefix = re.search(r"^ *(\d+)[\\]{0,2}[.|)]", line)
            if number_prefix:
                numbered_line = int(number_prefix.group(1))
                if numbered_line != 1:
                    #this section doesn't start with 1 so we dont need to check for it further
                    number_1_found = True
                    self.current_section_starts_with_1 = False
                    break
                else:
                    number_1_found = False
                    self.current_section_starts_with_1 = True
                    break
        tracklist = 0
        newline_detected = False
        # letterlist_enumvalue = ''
        for line in lines_original:
            # check if newlines are detected.(newlines cancel lists)
            if '<!-- NewLine -->' in line:
                #means newline is in this line so it canceled the previous list tracking
                # reset list back to zero 
                newline_detected = True
                tracklist = 0
            if number_1_found:                    
                #check if the current line is a numbered line
                number_prefix = re.search(r"^ *(\d+)[\\]{0,2}[.|)]", line)
                if number_prefix:
                    numbered_line = int(number_prefix.group(1))
                    #it is a numbered line, so check if it is a #1
                    if numbered_line == 1:
                        # starting a new numbered list
                        tracklist = 1
                        newline_detected = False # reset to allow new list to be tracked
                    else:
                        # check if we were in a list on the previous numbered line
                        if tracklist == 0:
                            # we were not a list on the previous numbered line
                            lines_altered.append('<!-- NewLine -->\n')
                        else:
                            # we were in a list on the previous line
                            # check if we still are on a list on this line
                            if numbered_line == tracklist+1:
                                # this means we might still be inside a list.
                                # to make sure lets see if a newline was detected prior to this line
                                if newline_detected:
                                    # there was a newline detected so this means the list is cancelled
                                    # reset the list tracker to zero
                                    tracklist = 0
                                    # and because the list was cancelled we can assume this line to be a new question
                                    lines_altered.append('<!-- NewLine -->\n')
                                    # reset the newline_detected to False
                                    newline_detected = False
                                else:
                                    #update tracklist to track the current list further
                                    tracklist = numbered_line
                                    # TODO WARN USER ABOUT POTENTIAL NEWLINE NEEDED HERE?? But we don't know the criteria to detect this issue yet. more development needed here
                            else:
                                # this means we have exited the list, and is safe to assume this is a new question
                                lines_altered.append('<!-- NewLine -->\n')
                                tracklist = 0                                    
            else:
                # look for first question          
                if re.search(r"^ *1[\\]{0,2}[.|)]", line):
                    number_1_found = True
            lines_altered.append(line)
        result = '\n'.join(lines_altered)
        result = '\n' + result
        sectionobject.raw_content = result
        sectionobject.save()
        return

    def __split_questions(self, sectionobject):
        logger = FilenameLoggingAdapter(newlogger, {
            'filename': self.questionlibrary.temp_file.name,
            'user_ip': self.questionlibrary.user_ip
            })
        root = None
        try:
            os.chdir('/antlr_build/splitter')
            result = subprocess.run(
                'java -cp splitter.jar:* splitter',
                shell=True,
                input=sectionobject.raw_content.encode("utf-8"),
                capture_output=True)
            os.chdir('/code')
            root = ET.fromstring(result.stdout.decode("utf-8"))
        except:
            sectionobject.error = "ANTLR"
            raise SplitterError("ANTLR")

        # COPY contents of first element into the second element because this sections does not start with number 1. 
        # meaning that the contents of the first element belongs 
        # to the first question in this section
        if not self.current_section_starts_with_1:
            if len(root) > 1:
                root[1][0].text = str(root[0][0].text) + str(root[1][0].text)
                root.remove(root[0])
                #renumber the question id because the first element was removed after being copied to the second element
                id = 0
                for question in root:
                    question.attrib["id"] = str(id)
                    id += 1

        section_questions_found = 0
        try:    
            for question in root:
                questionobject = Question.objects.create(
                    section=sectionobject)
                questionobject.save()
                content = question.find('content')
                if content is not None:
                    # Filter out empty questions
                    if len(trim_text(content.text)) > 0:
                        self.total_questions_found += 1
                        questionobject.index = self.total_questions_found
                        section_questions_found += 1
                        questionobject.raw_content = content.text
                questionobject.save()
        except:
            sectionobject.error = "Failed to process questions in section"
            raise SplitterError("Failed to process questions in section")
        return section_questions_found

class SplitterError(Exception):
    def __init__(self, reason, message="Splitter Error"):
        self.reason = reason
        self.message = message
    def __str__(self):
        return f'{self.message} -> {self.reason}'