import re
from ...models import Matching, MatchingChoice, MatchingAnswer
from ..process_helper import add_error_message, trim_text, markdown_to_html
from api.logging.ErrorTypes import MATNoMatchError, MATMissingChoiceError, MATMissingAnswerError

def build_inline_MAT(question, answers):
    question.questiontype = 'MAT'
    question.save()

    mat_object = Matching.objects.create(question=question)
    mat_object.save()
        
    for answer in answers:
        answercontent = trim_text(answer.get('answer_content'))
        regpattern = r"(\\`(.+)\\`\s*=\s*\\`(.+)\\`)|((.+)==(.+))|((.+)=(.+))"
        choice_answer_groups_regex = re.search(regpattern, answercontent)
        
        if choice_answer_groups_regex is not None:
            group_num = []
            if choice_answer_groups_regex.group(1):
                group_num.extend([2, 3])
            elif choice_answer_groups_regex.group(4):
                group_num.extend([5, 6])
            elif choice_answer_groups_regex.group(7):
                group_num.extend([8, 9])
            else:
                # This should be impossible as we made sure the answer would have an `=`
                try:
                    error_message = "No match found in MAT answer."
                    add_error_message(question, error_message)
                    raise MATNoMatchError(error_message)
                except Exception as e:
                    pass

            mat_choice_text = choice_answer_groups_regex.group(group_num[0]).strip()
            mat_choice_text = re.sub(r"^\\\`|\\\`$", '', mat_choice_text)
            mat_choice_text = markdown_to_html(mat_choice_text)

            mat_answer_text = choice_answer_groups_regex.group(group_num[1]).strip()
            mat_answer_text = re.sub(r"^\\\`|\\\`$", '', mat_answer_text)
            mat_answer_text = markdown_to_html(mat_answer_text)

            mat_choice = None
            if mat_choice_text == "":
                try:
                    error_message = "One or more matching choice is missing."
                    add_error_message(question, error_message)
                    raise MATMissingChoiceError(error_message)
                except Exception as e:
                    pass

            else:
                if mat_object.get_matching_choice_by_text(mat_choice_text):
                    mat_choice = mat_object.get_matching_choice_by_text(mat_choice_text)
                    mat_choice.save()
                else:
                    mat_choice = MatchingChoice.objects.create(matching=mat_object)
                    mat_choice.choice_text = mat_choice_text
                    mat_choice.save()

            mat_answer = None
            if mat_choice.has_matching_answer(mat_answer_text):
                # duplicate matching_answer
                pass
            else:
                mat_answer = MatchingAnswer.objects.create(matching_choice=mat_choice)

            if mat_answer_text == "":
                try:
                    error_message = "One or more matching answer is missing."
                    add_error_message(question, error_message)
                    raise MATMissingAnswerError(error_message)
                except Exception as e:
                    pass
            else:
                mat_answer.answer_text = mat_answer_text
                mat_answer.save()

        else:
            try:
                error_message = "One or more matching choice/answer choices missing"
                add_error_message(question, error_message)
                raise MATMissingOptionError(error_message)
            except Exception as e:
                pass

        
    
    
def build_endanswer_MAT(question, endanswer):
    question.questiontype = 'MAT'
    question.save()

    mat_object = Matching.objects.create(question=question)
    mat_object.save()

    answer_list = list(map(str.strip, endanswer.answer.split(";")))

    for answer in answer_list:
        answercontent = trim_text(answer)
        regpattern = r"(\\`(.+)\\`\s*=\s*\\`(.+)\\`)|((.+)==(.+))|((.+)=(.+))"
        choice_answer_groups_regex = re.search(regpattern, answercontent)

        if choice_answer_groups_regex is not None:
            group_num = []
            if choice_answer_groups_regex.group(1):
                group_num.extend([2, 3])
            elif choice_answer_groups_regex.group(4):
                group_num.extend([5, 6])
            elif choice_answer_groups_regex.group(7):
                group_num.extend([8, 9])
            else:
                # This should be impossible as we made sure the answer would have an `=`
                try:
                    error_message = "No match found in MAT answer."
                    add_error_message(question, error_message)
                    raise MATNoMatchError(error_message)
                except Exception as e:
                    pass

            mat_choice_text = choice_answer_groups_regex.group(group_num[0]).strip()
            mat_choice_text = re.sub(r"^\\\`|\\\`$", '', mat_choice_text)
            mat_choice_text = markdown_to_html(mat_choice_text)

            mat_answer_text = choice_answer_groups_regex.group(group_num[1]).strip()
            mat_answer_text = re.sub(r"^\\\`|\\\`$", '', mat_answer_text)
            mat_answer_text = markdown_to_html(mat_answer_text)

            mat_choice = None
            if mat_choice_text == "":
                try:
                    error_message = "One or more matching choice is missing."
                    add_error_message(question, error_message)
                    raise MATMissingChoiceError(error_message)
                except Exception as e:
                    pass
            else:
                if mat_object.get_matching_choice_by_text(mat_choice_text):
                    mat_choice = mat_object.get_matching_choice_by_text(mat_choice_text)
                    mat_choice.save()
                else:
                    mat_choice = MatchingChoice.objects.create(matching=mat_object)
                    mat_choice.choice_text = mat_choice_text
                    mat_choice.save()

            mat_answer = None
            if mat_choice.has_matching_answer(mat_answer_text):
                # duplicate matching_answer
                pass
            else:
                mat_answer = MatchingAnswer.objects.create(matching_choice=mat_choice)

            if mat_answer_text == "":
                try:
                    error_message = "One or more matching answer is missing."
                    add_error_message(question, error_message)
                    raise MATMissingAnswerError(error_message)
                except Exception as e:
                    pass
            else:
                mat_answer.answer_text = mat_answer_text
                mat_answer.save()


        else:
            try:
                error_message = "One or more matching choice/answer choices missing"
                add_error_message(question, error_message)
                raise MATMissingOptionError(error_message)
            except Exception as e:
                pass
