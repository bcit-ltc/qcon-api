from rest_framework.decorators import api_view, permission_classes, authentication_classes, parser_classes
from rest_framework.parsers import JSONParser
from rest_framework.response import Response
from rest_framework import authentication, permissions
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from django.conf import settings

from .serializers import FormatSerializer
from .serializers import SectionListSerializer, SectionSerializer
from .serializers import QuestionListSerializer, QuestionBaseSerializer, QuestionSerializer
from .models import Format
from .models import SectionList, QuestionList
from .models import BaseQuestion, BaseTextAnswer
from .process.common.extract_images import extract_images
from .process.common.restore_images import restore_images
# from .process.sectioner.sectioner import run_sectioner
# from .process.splitter.splitter import run_splitter
from .process.splitter.splitter import Splitter
from .process.questionparser.questionparser import run_questionparser

import logging
logger = logging.getLogger(__name__)

@authentication_classes([])
@permission_classes([])
@api_view(['POST'])
def format(request):
    maincontent_title = request.data['file'].name.split(".")[0]
    filename = request.data['file'].name
    temp_file_path = request.data['file'].temporary_file_path()
    temp_file_name = request.data['file'].name

    format = Format(temp_file_path, temp_file_name, filename, maincontent_title)
    format.convert_pandoc().extract_images().convert_txt().fix_numbering().run_formatter().restore_images()
    serializer = FormatSerializer(format)
    return Response(serializer.data, status=200)

@parser_classes([JSONParser])
@authentication_classes([])
@permission_classes([])
@api_view(['POST'])
def sections(request):
    serializer = FormatSerializer(data=request.data)
    if serializer.is_valid(raise_exception=True):

        sectionlist = SectionList(
            content = serializer.validated_data['body'])
        
        sectionlist.content, images_list = extract_images(
            sectionlist.content)
        
        sectionlist.run_sectioner()

        for section in sectionlist.sections_list:
            sectionheader = restore_images(section.sectionheader, 
                                         images_list)
            setattr(section, 'sectionheader', sectionheader) 
            sectioncontent = restore_images(section.sectioncontent, 
                                         images_list)
            setattr(section, 'sectioncontent', sectioncontent) 

        serializer = SectionListSerializer(sectionlist)

        return Response(serializer.data, status=200)
    return Response(serializer.errors, status=400)

@parser_classes([JSONParser])
@authentication_classes([])
@permission_classes([])
@api_view(['POST'])
def splitter(request):
    serializer = SectionSerializer(data=request.data)
    if serializer.is_valid(raise_exception=True):
        questionlist = QuestionList(
            content=serializer.validated_data['sectioncontent'],
        )
 
        questionlist.content, images_list = extract_images(
            questionlist.content)   
        
        splitter = Splitter(questionlist.content)
        splitter.add_newlines_before_question().split_questions()
        questionlist = super(splitter.__class__,splitter)
        for question in questionlist.question_list:
            questioncontent = restore_images(question.questioncontent, 
                                         images_list)
            setattr(question, 'questioncontent', questioncontent) 
        serializer = QuestionListSerializer(questionlist)
        return Response(serializer.data, status=200)
    return Response(serializer.errors, status=400)

@parser_classes([JSONParser])
@authentication_classes([])
@permission_classes([])
@api_view(['POST'])
def parsequestion(request):
    serializer = QuestionSerializer(data=request.data)
    if serializer.is_valid(raise_exception=True):
        basequestion = BaseQuestion(
            questioncontent=serializer.validated_data['questioncontent'],
        )
        basequestion.questioncontent, images_list = extract_images(
            basequestion.questioncontent)   
        
        basequestion.get_line_elements()
        basequestion.extract_question_header_elements()
        basequestion.get_question_body_parts_list()
        basequestion.get_number_provided()
        basequestion.separate_question_and_answers()
        basequestion.check_questiontype()
        basequestion.compare_user_type_with_processed_type()

        serializernew = QuestionSerializer(basequestion)
        return Response(serializernew.data, status=200)
    return Response(serializer.errors, status=400)


@parser_classes([JSONParser])
@authentication_classes([])
@permission_classes([])
@api_view(['POST'])
def endanswer(request):

    return Response("endanswer")


class RootPath(APIView):
    permission_classes = [AllowAny]

    def get(self, request, format=None):
        return Response(settings.GIT_TAG, status=200)