from ast import Not
import os
import xml.etree.ElementTree as ET
import subprocess
import re
# from ...models import Question

import logging
logger = logging.getLogger(__name__)

from enum import Enum
from django.utils.translation import gettext_lazy as _

def run_questionparser(question):

    question.get_line_elements()
    question.extract_question_header_elements()
    question.get_question_body_parts_list()
    question.get_number_provided()
    question.separate_question_and_answers()

    # question.check_questiontype()
    # question.compare_user_type_with_processed_type()

    # question.build_question()
    # logger.info(dir(question))

    # q = Question()
    # m = MultipleChoice()
    # m.enumeration = "letters"
    # m.answers = [MultipleChoiceAnswer(1,1,"answer1"),
    #              MultipleChoiceAnswer(2,2,"answer two")]
    # q.processedquestion = m

    # b = BaseTextAnswer()
    # b.answer_content = "hallo ik ben base van base van g;kwjefn;ewlrkfm;owemkl"

    # manswer = MultipleChoiceAnswer(basetextanswer=b)
    # print(manswer)
    # print(question.basetextanswers)
    print(help(question))


    return question



# class MultipleChoice():
#     randomize = None
#     enumeration = None
#     answers = []



# class BaseTextAnswer():
#     def __init__(self, answerlistitem):
#         self.answer_prefix = answerlistitem['answer_prefix']
#         self.MarkedWithStar = MarkedWithStar
#         self.answer_content = answer_content
#         self.feedback = feedback

#     class EnumeratorTypes(Enum):
#         LOWERCASELETTERS = 'LOWERCASELETTERS', _('LOWERCASELETTERS')
#         UPPERCASELETTERS = 'UPPERCASELETTERS', _('UPPERCASELETTERS')
#         NUMBERS = 'NUMBERS', _('NUMBERS')
#         ROMAN_NUMERALS = 'ROMAN_NUMERALS', _('ROMAN_NUMERALS')
#         UPPERCASE_ROMAN_NUMERALS = 'UPPERCASE_ROMAN_NUMERALS', _('UPPERCASE_ROMAN_NUMERALS')
#         NO_ENUMERATION = 'NO_ENUMERATION', _('NO_ENUMERATION')

#     enumerator = EnumeratorTypes.LOWERCASELETTERS
#     enumindex = None
#     answer_content = None
#     MarkedWithStar = False

#     def __str__(self):
#         return f"[{self.enumindex}][marked*:{ self.MarkedWithStar }][content:{self.answer_content[0:20]}]"

# class MultipleChoiceAnswer(BaseTextAnswer):
#     def __init__(self, basetextanswer=None, index=None, order=None):
#         self.index = index
#         self.order=order
#         # super(MultipleChoiceAnswer, self).__init__()
#         if type(basetextanswer) is BaseTextAnswer:
#             super().__init__(basetextanswer)
#         # self.answer=answer
#     index = None
#     order = None
#     # answer = None
#     answer_feedback = None
#     weight = None
#     def __str__(self):
#         return f"[{self.index}][marked*:{ self.MarkedWithStar }][content:]"


# class TrueFalse():
#     true_weight = None
#     true_feedback = None
#     false_weight = None
#     false_feedback = None
#     enumeration = None

# class Fib():
#     type = None
#     text = None
#     order = None
#     size = None
#     weight = None

# class MultipleSelect():
#     randomize = None
#     enumeration = None
#     style = None
#     grading_type = None

# class MultipleSelectAnswer():
#     index = None
#     order = None
#     answer = None
#     answer_feedback = None
#     is_correct = None

# class Matching():
#     grading_type = None


# class MatchingChoice():
#     choice_text = None

# class MatchingAnswer():
#     answer_text = None

# class Ordering():
#     text = None
#     order = None
#     ord_feedback = None

# class WrittenResponse():
#     enable_student_editor = None
#     initial_text = None
#     answer_key = None
#     enable_attachments = None