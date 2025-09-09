# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

from rest_framework import serializers
from django.conf import settings

class FormatSerializer(serializers.Serializer):
    filename = serializers.CharField(required=False)
    maincontent_title = serializers.CharField(required=False)
    body = serializers.CharField()
    end_answers = serializers.CharField(required=False)


class SectionSerializer(serializers.Serializer):
    title = serializers.CharField(required=False)
    order = serializers.IntegerField(max_value=None, min_value=None, required=False)
    is_main_content = serializers.BooleanField(required=False)
    sectionheader = serializers.CharField(allow_null=True, required=False)
    sectioncontent = serializers.CharField()

class SectionListSerializer(serializers.Serializer):
    sections_list = SectionSerializer(many=True, required=False, allow_null=True)

class QuestionBaseSerializer(serializers.Serializer):
    index = serializers.IntegerField(max_value=None, min_value=None, required=False)
    questioncontent = serializers.CharField(required=False)
class QuestionListSerializer(serializers.Serializer):
    question_list = QuestionBaseSerializer(many=True)

class ProcessedQuestionSerializer(serializers.Serializer):
    randomize = serializers.CharField(required=False)
    enumeration = serializers.CharField(required=False)
#     answers = serializers.ListField(
#    child=serializers.IntegerField(min_value=0, max_value=100)
# )

class BasetextAnswerSerializer(serializers.Serializer):
    enumindex = serializers.CharField(required=False)
    answer_content = serializers.CharField(required=False)

class BaseTextAnswerField(serializers.Field):
    def to_representation(self, value):
        return f"{value.answer_prefix}" \
        , f"{value.MarkedWithStar}" \
        , f"{value.answer_content}"

class QuestionSerializer(serializers.Serializer):
    number_provided = serializers.CharField(required=False)
    question_header_type = serializers.CharField(required=False)
    question_header_title = serializers.CharField(required=False)
    question_header_points = serializers.CharField(required=False)
    questiontype_processed = serializers.CharField(required=False)
    questioncontent = serializers.CharField(required=False)
    basetextanswers = serializers.ListField(required=False,
        child=BaseTextAnswerField(required=False))
    # answers = serializers.CharField(required=False)
    # processedquestion = ProcessedQuestionSerializer(required=False)
