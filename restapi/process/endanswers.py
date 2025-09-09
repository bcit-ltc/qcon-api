import os
import subprocess
import xml.etree.ElementTree as ET
from ..models import EndAnswer
import re

def get_endanswers(questionlibrary):
    if questionlibrary.end_answers_raw == None:
        return 0
    os.chdir('/antlr_build/endanswers')
    result = subprocess.run(
        'java -cp endanswers.jar:* endanswers',
        shell=True,
        input=questionlibrary.end_answers_raw.encode("utf-8"),
        capture_output=True)
    os.chdir('/code')
    root = None
    try:
        root = ET.fromstring(result.stdout.decode("utf-8"))
    except:
        raise EndAnswerError("Cannot read endanswers")
    answers = root.findall("answer")   
    endanswers_found = 0
    if answers is not None:
        for answer in answers:
            endanswer = EndAnswer.objects.create(question_library=questionlibrary)      
            content = answer.find('content').text
            index  = answer.find('index').text
            indexdigit = re.search(r'\d+', index)
            endanswer.index = indexdigit.group(0)
            endanswer.answer = content
            endanswers_found += 1
            endanswer.save()
    else:
        raise EndAnswerError("No Answers in EndAnswer")
    questionlibrary.save()
    return endanswers_found

class EndAnswerError(Exception):
    def __init__(self, reason, message="EndAnswer Error"):
        self.reason = reason
        self.message = message

    def __str__(self):
        return f'{self.message} -> {self.reason}'