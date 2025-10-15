# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

import json
from rest_framework import viewsets
from .serializers import JsonToScormSerializer, QuestionLibraryPackageSerializer, WordToJsonSerializer
from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.response import Response
from django.http import FileResponse, JsonResponse
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.authentication import TokenAuthentication
from rest_framework.parsers import MultiPartParser
from rest_framework.parsers import JSONParser


from django.core.files.base import ContentFile
from django.conf import settings

from .models import QuestionLibrary

import logging
logger = logging.getLogger(__name__)
from .logging.contextfilter import QuestionlibraryFilenameFilter
loggingfilter = QuestionlibraryFilenameFilter()
logger.addFilter(loggingfilter)

class TokenAuthenticationWithBearer(TokenAuthentication):
    keyword = 'Bearer'

    def __init__(self):
        super(TokenAuthenticationWithBearer, self).__init__()

class WordToJson(APIView):
    parser_classes = [MultiPartParser]
    permission_classes = [AllowAny]
    authentication_classes = [TokenAuthenticationWithBearer]
    serializer_class = WordToJsonSerializer

    def post(self, request, format=None):

        is_random = False
        if 'randomize' in request.POST:
            if request.POST['randomize'].lower() in ("true", "yes"):
                is_random = True

        file_obj = request.data['temp_file']
        serializer = WordToJsonSerializer(data={
            'temp_file': file_obj,
            'randomize': is_random
        })

        if serializer.is_valid():
            instance = serializer.save()

            # question_library = QuestionLibrary.objects.first()

            # question_library = instance

            # ==============  start the process  ========
            from .process.process import process
            process(instance)

            # question_library_serializer = QuestionLibraryPackageSerializer(question_library)

            
            json_string = '{"main_title":"Exam Title","randomize_answer":false,"total_question_errors":"1","total_document_errors":"0","sections":[{"is_main_content":true,"title":"Section title","is_title_displayed":false,"text":null,"is_text_displayed":false,"shuffle":false,"questions":[{"title":"MC title","text":"Question text","points":3.5,"difficulty":3,"mandatory":false,"hint":"Question hint","feedback":"Question feedback","multiple_choice":[{"randomize":true,"enumeration":1,"multiple_choice_answers":[{"answer":"MC first answer text","answer_feedback":"MC first answer feedback","weight":100},{"answer":"MC second answer text","answer_feedback":"MC second answer feedback","weight":0}]}],"true_false":null,"fib":null,"multiple_select":null,"ordering":null,"matching":null,"written_response":null},{"title":"TF title","text":"Question text","points":1,"difficulty":1,"mandatory":false,"hint":"Question hint","feedback":"Question feedback","multiple_choice":null,"true_false":[{"true_weight":100,"true_feedback":"true feedback","false_weight":0,"false_feedback":"true feedback","enumeration":2}],"fib":null,"multiple_select":null,"ordering":null,"matching":null,"written_response":null},{"title":"MS title","text":"Question text","points":1,"difficulty":1,"mandatory":false,"hint":"Question hint","feedback":"Question feedback","multiple_choice":null,"true_false":null,"fib":null,"multiple_select":[{"randomize":true,"enumeration":1,"style":2,"multiple_select_answers":[{"answer":"MS first answer text","answer_feedback":"MS first answer feedback","is_correct":true},{"answer":"MS second answer text","answer_feedback":"MS second answer feedback","is_correct":true}]}],"ordering":null,"matching":null,"written_response":null},{"title":"WR title","text":"Question text","points":5,"difficulty":5,"mandatory":false,"hint":"Question hint","feedback":"Question feedback","multiple_choice":null,"true_false":null,"fib":null,"multiple_select":null,"ordering":null,"matching":null,"written_response":[{"enable_student_editor":false,"initial_text":null,"answer_key":"WR answer key","enable_attachments":false}]},{"title":"FIB title","text":"Question text","points":4,"difficulty":3,"mandatory":false,"hint":"Question hint","feedback":"Question feedback","multiple_choice":null,"true_false":null,"fib":[{"type":"fibquestion","text":"1+15?","order":1,"size":null,"weight":null},{"type":"fibanswer","text":"16","order":2,"size":3,"weight":100}],"multiple_select":null,"ordering":null,"matching":null,"written_response":null},{"title":"Ordering title","text":"Question text","points":6,"difficulty":2,"mandatory":false,"hint":"Question hint","feedback":"Question feedback","multiple_choice":null,"true_false":null,"fib":null,"multiple_select":null,"ordering":[{"text":"Order 1","order":1,"ord_feedback":"Ordering 1 feedback"},{"text":"Order 1","order":2,"ord_feedback":"Ordering 2 feedback"},{"text":"Order 1","order":3,"ord_feedback":"Ordering 3 feedback"}],"matching":null,"written_response":null},{"title":"Matching title","text":"Question text","points":6,"difficulty":2,"mandatory":false,"hint":"Question hint","feedback":"Question feedback","multiple_choice":null,"true_false":null,"fib":null,"multiple_select":null,"ordering":null,"matching":[{"grading_type":1,"matching_choices":[{"choice_text":"Choice 1","matching_answers":[{"answer_text":"Choice 1 answer a"},{"answer_text":"Choice 1 answer b"}]},{"choice_text":"Choice 2","matching_answers":[{"answer_text":"Choice 2 answer a"},{"answer_text":"Choice 2 answer b"}]}]}],"written_response":null}]}]}'
            json_data = json.loads(json_string)
            for item in json_data:
                match item:
                    case "main_title":
                        print(json_data["main_title"])
                    case "randomize_answer":
                        print(json_data["randomize_answer"])
                    case "total_question_errors":
                        print(json_data["total_question_errors"])
                    case "total_document_errors":
                        print(json_data["total_document_errors"])
                    case "sections":
                        for section in json_data["sections"]:
                            print("\t", section["title"])
                            print("\t", section["is_title_displayed"])
                            print("\t", section["text"])
                            print("\t", section["is_text_displayed"])
                            print("\t", section["shuffle"])

                            for question in section["questions"]:
                                print("\t\t", question["title"])
                                print("\t\t", question["text"])
                                print("\t\t", question["points"])
                                print("\t\t", question["difficulty"])
                                print("\t\t", question["mandatory"])
                                print("\t\t", question["hint"])
                                print("\t\t", question["feedback"])
                                
                                if question["multiple_choice"]:
                                    print("\t\t\tmultiple_choice")
                                    for multiple_choice in question["multiple_choice"]:

                                        print("\t\t\t\t", multiple_choice["randomize"])
                                        print("\t\t\t\t", multiple_choice["enumeration"])

                                        print("\t\t\t\tmultiple_choices_answers")
                                        for mc_answers in multiple_choice["multiple_choices_answers"]:
                                            print("\t\t\t\t\t", mc_answers["answer"])
                                            print("\t\t\t\t\t", mc_answers["answer_feedback"])
                                            print("\t\t\t\t\t", mc_answers["weight"])
                                            print("")
                                                    
                                elif question["true_false"]:
                                    for true_false in question["true_false"]:
                                        print("\t\t\ttrue_false")
                                        print("\t\t\t\t", true_false["true_weight"])
                                        print("\t\t\t\t", true_false["true_feedback"])
                                        print("\t\t\t\t", true_false["false_weight"])
                                        print("\t\t\t\t", true_false["false_feedback"])
                                        print("\t\t\t\t", true_false["enumeration"])

                                elif question["fib"] :
                                    print("\t\t\tfib")
                                    for fib in question["fib"]:
                                        print("\t\t\t\t", fib["type"])
                                        print("\t\t\t\t", fib["text"])
                                        print("\t\t\t\t", fib["order"])
                                        print("\t\t\t\t", fib["size"])
                                        print("\t\t\t\t", fib["weight"])
                                        print("")
                                elif question["multiple_select"]:
                                    for multiple_select in question["multiple_select"]:
                                        print("\t\t\tmultiple_select")
                                        print("\t\t\t\t", multiple_select["randomize"])
                                        print("\t\t\t\t", multiple_select["enumeration"])
                                        print("\t\t\t\t", multiple_select["style"])

                                        print("\t\t\t\tmultiple_select_answers")
                                        for ms_answers in multiple_select["multiple_select_answers"]:
                                            print("\t\t\t\t\t", ms_answers["answer"])
                                            print("\t\t\t\t\t", ms_answers["answer_feedback"])
                                            print("\t\t\t\t\t", ms_answers["is_correct"])
                                            print("")

                                elif question["written_response"]:
                                    for written_response in question["written_response"]:
                                        print("\t\t\twritten_response")
                                        print("\t\t\t\t",written_response["enable_student_editor"])
                                        print("\t\t\t\t", written_response["initial_text"])
                                        print("\t\t\t\t", written_response["answer_key"])
                                        print("\t\t\t\t", written_response["enable_attachments"])

                                elif question["matching"]:
                                    for matching in question["matching"]:
                                        print("\t\t\tmatching")
                                        print("\t\t\t\t", matching["grading_type"])

                                        print("\t\t\t\tmatching_choices")
                                        for matching_choice in matching["matching_choices"]:
                                            print("\t\t\t\t\t", matching_choice["choice_text"])
                                            if matching_choice["matching_answers"]:
                                                for matching_answer in matching_choice["matching_answers"]:
                                                    print("\t\t\t\t\t\t", matching_answer["answer_text"])
                                                    print("")
                                
                                elif question["ordering"]:
                                    print("\t\t\tordering")
                                    for ordering in question["ordering"]:
                                        print("\t\t\t\t", ordering["text"])
                                        print("\t\t\t\t", ordering["order"])
                                        print("\t\t\t\t", ordering["ord_feedback"])
                                        print("")
                                else:
                                    print("******************************************************")
                                    print("NO QUESTION TYPE\n\n")
                                    print(question)
                                    print("******************************************************")



               


            instance.json_data = json_data
            instance.save()
            # print(instance.json_data)
            instance.cleanup()
            return JsonResponse(json_data, status=200)

        return JsonResponse(serializer.errors, status=400)


class JsonToScorm(APIView):
    parser_classes = [JSONParser]
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthenticationWithBearer]
    serializer_class = JsonToScormSerializer

    def post(self, request, format=None):

        json_data = request.data
        ql_serializer = QuestionLibraryPackageSerializer(data=json_data['data'])
        if ql_serializer.is_valid():
            ql_instance = ql_serializer.save()
            ql_instance.filter_main_title()
            ql_instance.folder_path = settings.MEDIA_ROOT + str(ql_instance.id)
            ql_instance.image_path = ql_instance.folder_path + settings.MEDIA_URL
            ql_instance.create_directory()
            ql_instance.save()
            file_name = ql_instance.filtered_main_title
            # if (ql_instance.total_question_errors + ql_instance.total_document_errors == 0):
            ql_instance.create_xml_files()
            ql_instance.zip_files()
            file_response = FileResponse(ql_instance.zip_file)
            file_response['Content-Disposition'] = 'attachment; filename="' + file_name + '"'
            logger.addFilter(QuestionlibraryFilenameFilter(ql_instance))
            logger.info("[" + str(ql_instance.id) + "] " +">>>>>>>>>>Transaction Finished>>>>>>>>>>")

            ql_instance.cleanup()

            return file_response
                
        return JsonResponse({"hostname": settings.APP_VERSION, "serializer_errors": ql_serializer.errors}, status=400)

class RootPath(APIView):
    permission_classes = [AllowAny]

    def get(self, request, format=None):
        from .models import StatusResponse
        from .serializers import StatusResponseSerializer

        status = StatusResponse(version_number=settings.APP_VERSION)
        serializer = StatusResponseSerializer(status)

        return JsonResponse(serializer.data,
                            json_dumps_params={'indent': 2},
                            status=200)


from django.shortcuts import redirect


def view_404(request, exception=None):
    return redirect('/')


def redirect_view(request, namespace, name, slug, actualurl):
    print(slug)
    print(actualurl)
    return redirect('/' + actualurl)
    # return None


def redirect_root(request, namespace, name, slug):
    print(slug)
    return redirect('/')
