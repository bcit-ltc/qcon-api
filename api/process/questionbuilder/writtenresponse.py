from ...models import WrittenResponse
from ..process_helper import add_warning_message, trim_md_to_html
from api.logging.WarningTypes import WREndAnswerExistWarning

def build_inline_WR_with_keyword(question, wr_answer):
    question.questiontype = 'WR'
    question.save()

    wr_object = WrittenResponse.objects.create(question=question)
    answer_key = wr_answer.find('content')

    if answer_key != None:
        wr_object.answer_key = trim_md_to_html(answer_key.text)

    wr_object.save()


def build_inline_WR_with_list(question, answers):
    question.questiontype = 'WR'
    question.save()

    wr_object = WrittenResponse.objects.create(question=question)

    answer_texts = []
    for answer in answers:
        answer_key = answer.get('answer_content')
        answer_texts.append(answer_key)

        if answer_texts:
            wr_object.answer_key = trim_md_to_html(' '.join(answer_texts))

        wr_object.save()

def build_endanswer_WR_with_list(question, endanswer, wr_answer):
    question.questiontype = 'WR'
    question.save()

    wr_object = WrittenResponse.objects.create(question=question)

    wr_object.answer_key = trim_md_to_html(endanswer.answer)
    wr_object.save()
    
    if wr_answer != None:
        warning_message = "Correct answer in the question is ignored because of existing Answer Key."
        add_warning_message(question, warning_message)
        raise WREndAnswerExistWarning(warning_message)
        
