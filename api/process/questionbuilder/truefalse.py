from ...models import TrueFalse
from ..process_helper import add_error_message, trim_text, trim_md_to_html, markdown_to_plain
from api.logging.ErrorTypes import TFNoAnswerError, TFSelectedAnswerError
from celery.utils.log import get_task_logger
from api.logging.logging_adapter import FilenameLoggingAdapter
loggercelery = get_task_logger(__name__)

def build_inline_TF(question, answers, enumeration):
    questionlibrary = question.section.question_library
    logger = FilenameLoggingAdapter(loggercelery, {
        'filename': questionlibrary.temp_file.name,
        'user_ip': questionlibrary.user_ip
        })
    logger.debug("building inline TF")

    question.questiontype = 'TF'
    question.save()

    tf_object = TrueFalse.objects.create(question=question)
    if enumeration:
        tf_object.enumeration = enumeration
    
    correctanswer_count = 0

    for answer in answers:
        answer_text = answer.get('answer_content').lower()
        answer_feedback = answer.get('feedback')
        is_correct = answer.get('correct')

        if "true" in answer_text:
            if answer_feedback != None:
                tf_object.true_feedback = trim_md_to_html(answer_feedback)

            if is_correct:
                tf_object.true_weight = 100
                correctanswer_count += 1
        
        if "false" in answer_text:
            if answer_feedback != None:
                tf_object.false_feedback = trim_md_to_html(answer_feedback)
            
            if is_correct:
                tf_object.false_weight = 100
                correctanswer_count += 1

        tf_object.save()

    if correctanswer_count == 0:
        error_message = "No answer selected in True/False question."
        add_error_message(question, error_message)
        raise TFNoAnswerError(error_message)
            
    elif correctanswer_count > 1:
        error_message = "More than one answer selected in True/False question."
        add_error_message(question, error_message)
        raise TFSelectedAnswerError(error_message)

    


def build_endanswer_TF(question, answers, endanswer, enumeration):
    questionlibrary = question.section.question_library
    logger = FilenameLoggingAdapter(loggercelery, {
        'filename': questionlibrary.temp_file.name,
        'user_ip': questionlibrary.user_ip
        })
    logger.debug("building endanswer TF")
    question.questiontype = 'TF'
    question.save()

    tf_object = TrueFalse.objects.create(question=question)
    if enumeration:
        tf_object.enumeration = enumeration
    
    correctanswer_count = 0

    endanswer_text = markdown_to_plain(endanswer.answer)
    endanswer_text = trim_text(endanswer_text).lower()

    for idx, answer in enumerate(answers):
        answer_text = answer.get('answer_content').lower()
        parsedanswer_index = ord(endanswer_text)-97
        answer_feedback = answer.get('feedback')

        if "true" in answer_text:
            if answer_feedback != None:
                tf_object.true_feedback = trim_md_to_html(answer_feedback)

            if idx == parsedanswer_index:
                tf_object.true_weight = 100
                correctanswer_count += 1

        if "false" in answer_text:
            if answer_feedback != None:
                tf_object.false_feedback = trim_md_to_html(answer_feedback)

            if idx == parsedanswer_index:
                tf_object.false_weight = 100
                correctanswer_count += 1

        tf_object.save()

    if correctanswer_count == 0:
        error_message = "No answer selected in True/False question."
        add_error_message(question, error_message)
        raise TFNoAnswerError(error_message)

    elif correctanswer_count > 1:
        error_message = "More than one answer selected in True/False question."
        add_error_message(question, error_message)
        raise TFSelectedAnswerError(error_message)
