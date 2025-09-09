from ...models import Fib
import re 
from ..process_helper import markdown_to_plain

def build_inline_FIB(question):
    question.questiontype = 'FIB'
    question.save()
    
    is_fib = re.search(r"\[(.*?)\]", question.text)
    answer_at_start = False

    if is_fib.start() == 0:
        answer_at_start = True
    
    list_of_answers = re.findall(r"\[(.*?)\]", question.text)
    replaced_answers = re.sub(r"\[(.*?)\]", "_______", question.text)
    list_of_text = replaced_answers.split("_______")

    if answer_at_start:
        list_of_text.pop(0)

    order = 1
    while len(list_of_text) + len(list_of_answers) > 0:

        if answer_at_start:
            try:
                answer_found = list_of_answers.pop(0)
                fib_object = Fib.objects.create(question=question)
                fib_object.order = order
                fib_object.text = markdown_to_plain(answer_found)
                fib_object.type = "fibanswer"
                fib_object.size = None
                fib_object.weight = None
                order += 1
                fib_object.save()
            except:
                pass
        
            try:
                text_found = list_of_text.pop(0)
                fib_object = Fib.objects.create(question=question)
                fib_object.order = order
                fib_object.text = text_found
                fib_object.type = "fibquestion"
                fib_object.size = None
                fib_object.weight = None
                order += 1
                fib_object.save()
            except:
                pass
        else:
            try:
                text_found = list_of_text.pop(0)
                fib_object = Fib.objects.create(question=question)
                fib_object.order = order
                fib_object.text = text_found
                fib_object.type = "fibquestion"
                fib_object.size = None
                fib_object.weight = None
                order += 1
                fib_object.save()
            except:
                pass

            try:
                answer_found = list_of_answers.pop(0)
                fib_object = Fib.objects.create(question=question)
                fib_object.order = order
                fib_object.text = markdown_to_plain(answer_found)
                fib_object.type = "fibanswer"
                fib_object.size = None
                fib_object.weight = None
                order += 1
                fib_object.save()
            except:
                pass


def build_endanswer_FIB(question, endanswer):
    question.questiontype = 'FIB'
    question.save()
    is_fib = re.search(r"\[(.*?)\]", question.text)
    answer_at_start = False

    if is_fib.start() == 0:
        answer_at_start = True
    
    list_of_answers = list(map(str.strip, endanswer.answer.split(";")))
    replaced_answers = re.sub(r"\[(.*?)\]", "_______", question.text)
    list_of_text = replaced_answers.split("_______")
    
    if answer_at_start:
        list_of_text.pop(0)

    order = 1
    while len(list_of_text) + len(list_of_answers) > 0:

        if answer_at_start:
            try:
                answer_found = list_of_answers.pop(0)
                fib_object = Fib.objects.create(question=question)
                fib_object.order = order
                fib_object.text = markdown_to_plain(answer_found)
                fib_object.type = "fibanswer"
                fib_object.size = None
                fib_object.weight = None
                order += 1
                fib_object.save()
            except:
                pass
        
            try:
                text_found = list_of_text.pop(0)
                fib_object = Fib.objects.create(question=question)
                fib_object.order = order
                fib_object.text = text_found
                fib_object.type = "fibquestion"
                fib_object.size = None
                fib_object.weight = None
                order += 1
                fib_object.save()
            except:
                pass
        else:
            try:
                text_found = list_of_text.pop(0)
                fib_object = Fib.objects.create(question=question)
                fib_object.order = order
                fib_object.text = text_found
                fib_object.type = "fibquestion"
                fib_object.size = None
                fib_object.weight = None
                order += 1
                fib_object.save()
            except:
                pass

            try:
                answer_found = list_of_answers.pop(0)
                fib_object = Fib.objects.create(question=question)
                fib_object.order = order
                fib_object.text = markdown_to_plain(answer_found)
                fib_object.type = "fibanswer"
                fib_object.size = None
                fib_object.weight = None
                order += 1
                fib_object.save()
            except:
                pass
