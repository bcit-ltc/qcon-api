import re
from ...models import MultipleChoice, MultipleChoiceAnswer
from ..process_helper import add_warning_message, trim_text, trim_md_to_plain, trim_md_to_html
from api.logging.WarningTypes import MCEndAnswerExistWarning
from celery.utils.log import get_task_logger
from api.logging.logging_adapter import FilenameLoggingAdapter
loggercelery = get_task_logger(__name__)

def build_inline_MC(question, answers, is_random, enumeration):
    questionlibrary = question.section.question_library
    logger = FilenameLoggingAdapter(loggercelery, {
        'filename': questionlibrary.temp_file.name,
        'user_ip': questionlibrary.user_ip
        })
    logger.debug("building inline mc")
    question.questiontype = 'MC'
    question.save()

    mc_object = MultipleChoice.objects.create(question=question)
    if is_random == True:
        mc_object.randomize = True

    if enumeration:
        mc_object.enumeration = enumeration
    mc_object.save()
    # grab all answers
    for answer_order, answer_item in enumerate(answers):
        mc_answerobject = MultipleChoiceAnswer.objects.create(multiple_choice=mc_object)
        answer_index = trim_text(answer_item.get('answer_prefix'))
        mc_answerobject.index = re.sub(r'[\W_]', '', answer_index)
        mc_answerobject.order = answer_order + 1
        mc_answerobject.answer = trim_md_to_html(answer_item.get('answer_content'))
        answer_feedback = answer_item.get('feedback')
        is_correct = answer_item.get('correct')
        if answer_feedback != None:
            mc_answerobject.answer_feedback = trim_md_to_html(answer_feedback)

        if is_correct:
            mc_answerobject.weight = 100

        mc_answerobject.save()


def build_endanswer_MC(question, answers, endanswer, is_random, enumeration):
    questionlibrary = question.section.question_library
    logger = FilenameLoggingAdapter(loggercelery, {
        'filename': questionlibrary.temp_file.name,
        'user_ip': questionlibrary.user_ip
        })

    question.questiontype = 'MC'
    question.save()

    mc_object = MultipleChoice.objects.create(question=question)
    if is_random == True:
        mc_object.randomize = True
    
    if enumeration:
        mc_object.enumeration = enumeration
    mc_object.save()

    endanswer_text = trim_md_to_plain(endanswer.answer)
    endanswer_text = trim_text(endanswer_text).lower()

    # grab all answers
    for idx, answer_item in enumerate(answers):
        mc_answerobject = MultipleChoiceAnswer.objects.create(multiple_choice=mc_object)
        answer_index = trim_text(answer_item.get('answer_prefix'))
        mc_answerobject.index = re.sub(r'[\W_]', '', answer_index)
        mc_answerobject.order = idx + 1
        mc_answerobject.answer = trim_md_to_html(answer_item.get('answer_content'))
        answer_feedback = answer_item.get('feedback')
        is_correct = answer_item.get('correct')

        if answer_feedback != None:
            mc_answerobject.answer_feedback = trim_md_to_html(answer_feedback)

        if idx == (ord(endanswer_text)-97):
            mc_answerobject.weight = 100
        
        mc_answerobject.save()

        if is_correct:
            try:
                warning_message = "Correct answer in the question is ignored because of existing Answer Key."
                add_warning_message(question, warning_message)
                raise MCEndAnswerExistWarning(warning_message)
            except Exception as e:
                logger.debug(str(e))
