import os
import subprocess
import xml.etree.ElementTree as ET
# from api.tasks import trim_text
import logging
logger = logging.getLogger(__name__)

from ...models import QuestionList
from ...models import BaseQuestion
# from ...models import Question


import re
import os

class Splitter(QuestionList):
    def __init__(self, content) -> None:
        super().__init__(content=content)
        self.total_questions_found = 0
        self.current_section_starts_with_1 = False

    def add_newlines_before_question(self):  
        lines_altered = []
        lines_original = self.content.splitlines()
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
        result = os.linesep.join(lines_altered)
        result = os.linesep + result
        self.content = result
        return self


    def split_questions(self):
        root = None
        try:
            os.chdir('/antlr_build/splitter')
            result = subprocess.run(
                'java -cp splitter.jar:* splitter',
                shell=True,
                input=self.content.encode("utf-8"),
                capture_output=True)
            os.chdir('/code')
            root = ET.fromstring(result.stdout.decode("utf-8"))
        except Exception as e:
            raise SplitterError("ANTLR: " + str(e))

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

        try:    
            for index, question in enumerate(root, start=1):
                questionobj = BaseQuestion()
                questionobj.index = index
                questioncontent = question.find('questioncontent')
                if questioncontent is not None:
                    questionobj.questioncontent = questioncontent.text
                self.question_list.append(questionobj)
        except:
            # sectionobject.error = "Failed to process questions in section"
            raise SplitterError("Failed to process questions in section")
        # return self.questionlist



class SplitterError(Exception):
    def __init__(self, reason, message="Splitter Error"):
        self.reason = reason
        self.message = message
    def __str__(self):
        return f'{self.message} -> {self.reason}'












