import re
from ...models import MultipleSelect, MultipleSelectAnswer
from ..process_helper import add_warning_message, trim_text, trim_md_to_html, trim_md_to_plain
from api.logging.WarningTypes import MSEndAnswerExistWarning

def build_inline_MS(question, answers, is_random, enumeration):
    question.questiontype = 'MS'
    question.save()
    
    ms_object = MultipleSelect.objects.create(question=question)
    if is_random == True:
        ms_object.randomize = True

    if enumeration:
        ms_object.enumeration = enumeration
    ms_object.save()

    # grab all answers
    for answer_order, answer_item in enumerate(answers):
        ms_answerobject = MultipleSelectAnswer.objects.create(multiple_select=ms_object)
        answer_index = trim_text(answer_item.get('answer_prefix'))
        ms_answerobject.index = re.sub(r'[\W_]', '', answer_index)
        ms_answerobject.order = answer_order + 1
        ms_answerobject.answer = trim_md_to_html(answer_item.get('answer_content'))
        answer_feedback = answer_item.get('feedback')
        is_correct = answer_item.get('correct')

        if answer_feedback != None:
            ms_answerobject.answer_feedback = trim_md_to_html(answer_feedback)
        
        if is_correct:
            ms_answerobject.is_correct = True
        if not is_correct:
            ms_answerobject.is_correct = False

        ms_answerobject.save()



def build_endanswer_MS(question, answers, endanswer, is_random, enumeration):
    question.questiontype = 'MS'
    question.save()

    ms_object = MultipleSelect.objects.create(question=question)
    if is_random == True:
        ms_object.randomize = True
    
    if enumeration:
        ms_object.enumeration = enumeration
    ms_object.save()

    endanswer_text = trim_md_to_plain(endanswer.answer)
    endanswer_text = trim_text(endanswer_text).lower()
    answer_list = list(map(str.strip, endanswer_text.split(',')))

    # grab all answers
    for idx, answer_item in enumerate(answers):
        ms_answerobject = MultipleSelectAnswer.objects.create(multiple_select=ms_object)
        answer_index = trim_text(answer_item.get('answer_prefix'))
        ms_answerobject.index = re.sub(r'[\W_]', '', answer_index)
        ms_answerobject.order = idx + 1
        ms_answerobject.answer = trim_md_to_html(answer_item.get('answer_content'))
        answer_feedback = answer_item.get('feedback')
        is_correct = answer_item.get('correct')

        if answer_feedback != None:
            ms_answerobject.answer_feedback = trim_md_to_html(answer_feedback)
        
        for endanswer_option in answer_list:
            if idx == (ord(endanswer_option)-97):
                ms_answerobject.is_correct = True

        ms_answerobject.save()

        try:
            if is_correct:
                warning_message = "Correct answer in the question is ignored because of existing Answer Key."
                add_warning_message(question, warning_message)
                raise MSEndAnswerExistWarning(warning_message)
        except Exception as e:
            pass        
