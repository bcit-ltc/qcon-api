import re
import pypandoc

def add_info_message(question, info_message):
    if question.info:
        if info_message not in question.info:
            question.info = question.info + "\n" + info_message
            question.save()

    else:
        question.info =  info_message
        question.save()

def add_warning_message(question, warning_message):
    if question.warning:
        if warning_message not in question.warning:
            question.warning = question.warning + "\n" + warning_message
            question.save()

    else:
        question.warning =  warning_message
        question.save()

def add_error_message(obj, error_message):
    if obj.error:
        if error_message not in obj.error:
            obj.error = obj.error + "\n" + error_message
            obj.save()

    else:
        obj.error =  error_message
        obj.save()

def trim_text(txt):
    text = txt.strip()
    text = re.sub('<!-- -->', '', text)
    text = re.sub('<!-- NewLine -->', '\n', text, flags=re.IGNORECASE)
    text = text.strip(" \n")
    return text

def markdown_to_plain(text):
    plain_text = pypandoc.convert_text(text, format="markdown_github+fancy_lists+emoji", to="plain", extra_args=['--wrap=none'])
    return plain_text

def html_to_plain(text):
    plain_text = pypandoc.convert_text(text, format="html", to="plain", extra_args=['--wrap=none'])
    return plain_text

def markdown_to_html(text):
    html_text = pypandoc.convert_text(text, format="markdown_github+fancy_lists+emoji+task_lists+hard_line_breaks+pipe_tables+all_symbols_escapable+tex_math_dollars", to="html", extra_args=['--mathml', '--ascii'])
    str_text = str(html_text)
    str_text = re.sub('<table>', lambda x: '<table style="width:100%;border:1px solid black;">', str_text)
    str_text = re.sub('<th>', lambda x: '<th style="border:1px solid black;">', str_text)
    str_text = re.sub('<td>', lambda x: '<td style="border:1px solid black;">', str_text)
    return str_text

def trim_md_to_plain(text):
    text_content = trim_text(text)
    text_content = markdown_to_plain(text_content)
    return text_content

def trim_md_to_html(text):
    text_content = trim_text(text)
    text_content = markdown_to_html(text_content)
    text_content = text_content.strip('\n')
    return text_content
