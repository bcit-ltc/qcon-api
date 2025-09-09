# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

from django.db import models

# import pypandoc
from datetime import datetime
from .scorm.XmlWriter import XmlWriter
from .scorm.manifest import ManifestEntity, ManifestResourceEntity

from xml.dom.minidom import parseString
import xml.etree.cElementTree as ET
from zipfile import *
from os import makedirs, path, walk, rmdir, remove, urandom

import re
import base64
from django.core.files.base import ContentFile

from rest_framework.authtoken.models import Token

from django.conf import settings
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db.models.signals import post_delete
from django.dispatch import receiver


import logging
newlogger = logging.getLogger(__name__)
from .logging.logging_adapter import FilenameLoggingAdapter

def format_file_path(instance, file_name):
    # file will be uploaded to MEDIA_ROOT/user_<id>/<filename>
    # print('{0}/{1}'.format(instance.id, file_name))
    return '{0}/{1}'.format(instance.id, file_name)

class QuestionLibrary(models.Model):
    id = models.AutoField(primary_key=True)
    folder_path = models.FilePathField(path="/code", match=None, recursive=False, max_length=None)
    temp_file = models.FileField(upload_to=format_file_path, blank=True, null=True)
    is_busy_processing = models.BooleanField(default=False, blank=True)
    session_id = models.TextField(blank=True, null=True)
    user_ip = models.GenericIPAddressField(protocol='both', unpack_ipv4=False, blank=True, null=True)
    randomize_answer = models.BooleanField(blank=True, null=True, default=None)
    media_folder = models.TextField(blank=True, null=True)
    enumeration = models.PositiveSmallIntegerField(null=True, validators=[MinValueValidator(1), MaxValueValidator(6)])
    image_path = models.FilePathField(path=None, match=None, recursive=False, max_length=None)
    shuffle = models.BooleanField(blank=True, null=True)
    main_title = models.TextField(blank=True, null=True)
    filtered_main_title = models.TextField(blank=True, null=True)
    end_answers_raw = models.TextField(blank=True, null=True)
    formatter_error = models.TextField(blank=True, null=True)
    formatter_output = models.TextField(blank=True, null=True)
    pandoc_output_file = models.FileField(upload_to=format_file_path, blank=True, null=True)
    pandoc_output = models.TextField(blank=True, null=True)
    txt_output = models.TextField(blank=True, null=True)
    sectioner_output = models.TextField(blank=True, null=True)
    imsmanifest_string = models.TextField(blank=True, null=True)
    imsmanifest_file = models.FileField(upload_to=format_file_path, blank=True, null=True)
    questiondb_string = models.TextField(blank=True, null=True)
    questiondb_file = models.FileField(upload_to=format_file_path, blank=True, null=True)
    zip_file = models.FileField(upload_to=format_file_path, blank=True, null=True)
    json_data = models.JSONField(null=True, blank=True, default=dict)
    output_zip_file = models.FileField(upload_to=format_file_path, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    total_question_errors = models.DecimalField(max_digits=6, decimal_places=0, blank=True, null=True)
    total_document_errors = models.DecimalField(max_digits=6, decimal_places=0, blank=True, null=True)

    class Meta:
        verbose_name_plural = "question libraries"

    def get_root_section(self):
        return Section.objects.filter(question_library=self.id, is_main_content=True).first()

    def get_sections(self):
        return Section.objects.filter(question_library=self.id).order_by('order')

    def get_image(self, id):
        return Image.objects.get(pk=id)

# Prevents illegal characters for the filename

    def filter_main_title(self):
        main_title = self.main_title.strip()
        main_title = main_title.lower()
        filtered_main_title = re.sub('[\W_]+', ' ', main_title).strip()
        filtered_main_title = filtered_main_title.replace(' ', '-')

        # If the file name is illegal Windows string, replace with "Converted-Exam"
        filtered_main_title = filtered_main_title.replace('^(CON|PRN|AUX|NUL|COM[1-9]|LPT[1-9])$', 'Converted-Exam', re.IGNORECASE)

        # Limit the filename to 50 characters including the timestamp
        current_time = datetime.now()
        time_stamp = current_time.timestamp()
        str_timestamp = str(time_stamp).replace('.', '')
        filtered_main_title = str_timestamp + '_' + filtered_main_title
        filtered_main_title = (filtered_main_title[:50]) if len(filtered_main_title) > 50 else filtered_main_title

        self.filtered_main_title = filtered_main_title

    def create_directory(self):
        # self.folder_path('/code/temp/' + str(self.id))
        if not path.exists(self.folder_path):
            makedirs(self.folder_path)

    def create_xml_files(self):
        logger = FilenameLoggingAdapter(newlogger, {'filename': str(self.id)})
        try:
            ql_obj = QuestionLibrary.objects.filter(id=self.id).first()
            parsed_xml = XmlWriter(ql_obj)
            manifest_entity = ManifestEntity()
            manifest_resource_entity = ManifestResourceEntity('res_question_library', 'webcontent', 'd2lquestionlibrary', 'questiondb.xml', 'Question Library')
            manifest_entity.add_resource(manifest_resource_entity)
            manifest = parsed_xml.create_manifest(manifest_entity, self.folder_path)
            parsed_imsmanifest = ET.tostring(manifest.getroot(), encoding='utf-8', xml_declaration=True).decode()
            parsed_imsmanifest = parseString(parsed_imsmanifest)
            parsed_imsmanifest = parsed_imsmanifest.toprettyxml(indent="\t")
            self.imsmanifest_string = parsed_imsmanifest
            self.save()
            logger.info("imsmanifest String Created")
        except Exception as e:
            logger.error("imsmanifest String Failed")
            self.error = "imsmanifest String Failed"
            self.save()

        try:
            questiondb_string = parsed_xml.questiondb_string
            media_folder = self.media_folder if self.media_folder != None else f'./assessment-assets/{self.filtered_main_title}/'
            img_elements = re.findall(r"\<img.*?\>", questiondb_string, re.MULTILINE)

            for idx, img in enumerate(img_elements):
                img_src = re.findall(r"src=\"(.*?)\"", img, re.MULTILINE)
                base64_img = img_src[0].split(';base64,')
                img_string = base64_img[1]
                img_ext = base64_img[0].split("/")[1]
                image_data = base64.b64decode(img_string)
                new_image_name = "image_" + str(idx+1) + "." + img_ext
                img_path = ql_obj.image_path + new_image_name

                if not path.exists(ql_obj.image_path):
                    makedirs(ql_obj.image_path)

                try:
                    with open(img_path, "wb") as fh:
                        fh.write(image_data)
                except IOError as e:
                    logger.error(f"Cannot proccess image with error: {e}")

                new_img_src = path.join(media_folder, new_image_name)
                new_img = f'<img src="{new_img_src}" alt="{new_image_name}" style="max-width:100%;" />'
                questiondb_string = questiondb_string.replace(img_elements[idx], new_img)

            self.questiondb_string = questiondb_string
            self.save()

            imsmanifest_file = ContentFile(self.imsmanifest_string, name="imsmanifest.xml")
            self.imsmanifest_file = imsmanifest_file
            self.save()
            logger.info("QuestionDB String Created")

        except Exception as e:
            logger.error("QuestionDB String Failed")

            self.error = "QuestionDB String Failed"
            self.save()

        try:
            questiondb_file = ContentFile(self.questiondb_string, name="questiondb.xml")
            self.questiondb_file = questiondb_file
            # question_library.checkpoint = 5;
            self.save()
            logger.info("XML files Created")
            # print(datetime.now().strftime("%H:%M:%S"), "imsmanifest.xml and questiondb.xml created!")

        except Exception as e:
            logger.error("XML files Failed")
            self.error = "XML files Failed"
            self.save()

    def zip_files(self):
        logger = FilenameLoggingAdapter(newlogger, {'filename': str(self.id)})
        try:
            with ZipFile(self.folder_path + "/" + self.filtered_main_title + '.zip', 'w') as myzip:
                myzip.write(self.questiondb_file.path, "questiondb.xml")
                myzip.write(self.imsmanifest_file.path, "imsmanifest.xml")
                media_folder = self.media_folder if self.media_folder != None else f'./assessment-assets/{self.filtered_main_title}/'

                for root, dirs, files in walk(self.image_path):
                    for filename in files:
                        myzip.write(path.join(root, filename), path.join(media_folder, filename))

            self.zip_file.name = str(self.id) + "/" + self.filtered_main_title + '.zip'
            self.save()
            logger.info("ZIP file Created")

        except Exception as e:
            logger.error("ZIP file Failed")

            self.error = "ZIP file Failed"
            self.save()

    def create_zip_file_package(self):
        logger = FilenameLoggingAdapter(newlogger, {'filename': str(self.id)})
        try:
            with ZipFile(self.folder_path + "/" + self.filtered_main_title, 'w') as myzip:
                myzip.write(self.zip_file.path, self.filtered_main_title + '.zip')
                myzip.write(self.json_file.path, 'result.json')

            self.output_zip_file.name = str(self.id) + "/" + self.filtered_main_title
            self.save()
            logger.info("ZIP file with JSON package Created")
        except Exception as e:
            logger.error("ZIP file with JSON package Failed")
            self.error = "ZIP file Failed"
            self.save()

    def cleanup(self):
        if not settings.DEBUG:
            self.delete()

    def __str__(self):
        return str(self.id)

class Image(models.Model):
    id = models.AutoField(primary_key=True)
    question_library = models.ForeignKey(QuestionLibrary, related_name='images', on_delete=models.CASCADE)
    image = models.TextField(blank=True, null=True)

class EndAnswer(models.Model):
    id = models.AutoField(primary_key=True)
    question_library = models.ForeignKey(QuestionLibrary, related_name='endanswers', on_delete=models.CASCADE)
    index = models.TextField(blank=True, null=True)
    answer = models.TextField(blank=True, null=True)

class Section(models.Model):
    id = models.AutoField(primary_key=True)
    question_library = models.ForeignKey(QuestionLibrary, related_name='sections', on_delete=models.CASCADE)
    is_main_content = models.BooleanField(blank=True, null=True, default=False)
    order = models.PositiveSmallIntegerField(null=True, validators=[MinValueValidator(1)])
    validated = models.BooleanField(blank=True, null=True, default=False)
    finished_processing = models.BooleanField(blank=True, null=True, default=False)
    raw_content = models.TextField(blank=True, null=True)
    questions_processed = models.DecimalField(max_digits=3, decimal_places=0, null=True)
    questions_expected = models.DecimalField(max_digits=3, decimal_places=0, null=True)
    processing_time = models.DecimalField(max_digits=3, decimal_places=0, null=True)
    title = models.TextField(blank=True, null=True)
    is_title_displayed = models.BooleanField(blank=True, null=True)
    text = models.TextField(blank=True, null=True)
    is_text_displayed = models.BooleanField(blank=True, null=True)
    shuffle = models.BooleanField(blank=True, null=True)
    error = models.TextField(blank=True, null=True)

    def __str__(self):
        return str(self.order)

    def get_questions(self):
        return Question.objects.filter(section=self.id).order_by('index')


class Question(models.Model):
    id = models.AutoField(primary_key=True)
    section = models.ForeignKey(Section, related_name='questions', on_delete=models.CASCADE)
    index = models.IntegerField(blank=True, null=True)
    number_provided = models.PositiveSmallIntegerField(null=True, validators=[MinValueValidator(1)])
    raw_header = models.TextField(blank=True, null=True)
    raw_content = models.TextField(blank=True, null=True)
    parser_output_xml = models.TextField(blank=True, null=True)
    title = models.TextField(blank=True, null=True)
    questiontype = models.TextField(blank=True, null=True)
    text = models.TextField(blank=True, null=True)
    points = models.DecimalField(unique=False, max_digits=8, decimal_places=4, null=True, default=1)
    difficulty = models.PositiveSmallIntegerField(blank=True, null=True, validators=[MinValueValidator(1), MaxValueValidator(5)], default=1)
    mandatory = models.BooleanField(blank=True, null=True)
    hint = models.TextField(blank=True, null=True)
    feedback = models.TextField(blank=True, null=True)
    info = models.TextField(blank=True, null=True)
    warning = models.TextField(blank=True, null=True)
    error = models.TextField(blank=True, null=True)

    def __str__(self):
        text = ''
        number_provided = ''
        if self.text is not None:
            text = self.text
        if self.number_provided is not None:
            number_provided = str(self.number_provided)
        return f"{number_provided}-{text[0:60]}"

    def get_multiple_choice(self):
        return MultipleChoice.objects.filter(question=self.id).first()

    def get_true_false(self):
        return TrueFalse.objects.filter(question=self.id).first()

    def get_fibs(self):
        return Fib.objects.filter(question=self.id).order_by('order')

    def get_fib_answers(self):
        return Fib.objects.filter(question=self.id, type='fibanswer').order_by('order')

    def get_multiple_select(self):
        return MultipleSelect.objects.filter(question=self.id).first()

    def get_matching(self):
        return Matching.objects.filter(question=self.id).first()

    def get_orderings(self):
        return Ordering.objects.filter(question=self.id).order_by('order')

    def get_written_response(self):
        return WrittenResponse.objects.filter(question=self.id).first()

    def get_question_type(self):
        if self.get_multiple_choice():
            return 'MC'
        elif self.get_true_false():
            return 'TF'
        elif self.get_multiple_select():
            return 'MS'
        elif self.get_fibs():
            return 'FIB'
        elif self.get_orderings():
            return 'ORD'
        elif self.get_written_response():
            return 'WR'
        elif self.get_matching():
            return 'MAT'


class MultipleChoice(models.Model):
    id = models.AutoField(primary_key=True)
    question = models.ForeignKey(Question, related_name='multiple_choice', on_delete=models.CASCADE)
    randomize = models.BooleanField(blank=True, null=True)
    enumeration = models.PositiveSmallIntegerField(blank=True, null=True, default=4)

    def __str__(self):
        return str(self.id)

    def get_multiple_choice_answers(self):
        return MultipleChoiceAnswer.objects.filter(multiple_choice=self.id).order_by('order')


class MultipleChoiceAnswer(models.Model):
    id = models.AutoField(primary_key=True)
    multiple_choice = models.ForeignKey(MultipleChoice, related_name='multiple_choice_answers', on_delete=models.CASCADE)
    index = models.TextField(blank=True, null=True)
    order = models.PositiveSmallIntegerField(blank=True, null=True)
    answer = models.TextField(blank=True, null=True)
    answer_feedback = models.TextField(blank=True, null=True)
    weight = models.DecimalField(unique=False, max_digits=8, decimal_places=4, null=True)

    def __str__(self):
        return str(self.id)


class TrueFalse(models.Model):
    id = models.AutoField(primary_key=True)
    question = models.ForeignKey(Question, related_name='true_false', on_delete=models.CASCADE)
    true_weight = models.DecimalField(unique=False, max_digits=8, decimal_places=4, null=True)
    true_feedback = models.TextField(blank=True, null=True)
    false_weight = models.DecimalField(unique=False, max_digits=8, decimal_places=4, null=True)
    false_feedback = models.TextField(blank=True, null=True)
    enumeration = models.PositiveSmallIntegerField(blank=True, null=True, default=4)

    def __str__(self):
        return str(self.id)


class Fib(models.Model):
    id = models.AutoField(primary_key=True)
    question = models.ForeignKey(Question, related_name='fib', on_delete=models.CASCADE)
    type = models.CharField(max_length=11, null=False)
    text = models.TextField(blank=True, null=True)
    order = models.PositiveSmallIntegerField(blank=True, null=True)
    size = models.DecimalField(unique=False, max_digits=3, decimal_places=0, null=True)
    weight = models.DecimalField(unique=False, max_digits=8, decimal_places=4, null=True)

    def __str__(self):
        return str(self.id)


class MultipleSelect(models.Model):
    id = models.AutoField(primary_key=True)
    question = models.ForeignKey(Question, related_name='multiple_select', on_delete=models.CASCADE)
    randomize = models.BooleanField(blank=True, null=True)
    enumeration = models.PositiveSmallIntegerField(blank=True, null=True, validators=[MinValueValidator(1), MaxValueValidator(6)], default=4)
    style = models.PositiveSmallIntegerField(blank=True, null=True, validators=[MinValueValidator(1), MaxValueValidator(3)], default=2)
    grading_type = models.PositiveSmallIntegerField(blank=True, null=True, validators=[MaxValueValidator(3)], default=2)

    def __str__(self):
        return str(self.id)

    def get_multiple_select_answers(self):
        return MultipleSelectAnswer.objects.filter(multiple_select=self.id).order_by('order')


class MultipleSelectAnswer(models.Model):
    id = models.AutoField(primary_key=True)
    multiple_select = models.ForeignKey(MultipleSelect, related_name='multiple_select_answers', on_delete=models.CASCADE)
    index = models.TextField(blank=True, null=True)
    order = models.PositiveSmallIntegerField(blank=True, null=True)
    answer = models.TextField(blank=True, null=True)
    answer_feedback = models.TextField(blank=True, null=True)
    is_correct = models.BooleanField(blank=True, null=True)
    
    def __str__(self):
        return str(self.id)


class Matching(models.Model):
    id = models.AutoField(primary_key=True)
    question = models.ForeignKey(Question, related_name='matching', on_delete=models.CASCADE)
    grading_type = models.PositiveSmallIntegerField(blank=True, null=True, validators=[MaxValueValidator(3)], default=3)

    def __str__(self):
        return str(self.id)

    def get_matching_choices(self):
        return MatchingChoice.objects.filter(matching=self.id).order_by('id')

    def get_matching_choice_by_text(self, choice_text):
        return MatchingChoice.objects.filter(matching=self.id, choice_text=choice_text).order_by('id').first()

    def get_unique_matching_answers(self):
        matching_answers = MatchingAnswer.objects.filter(matching_choice__matching__id=self.id).order_by('answer_text').values_list('answer_text', flat=True).distinct()
        return matching_answers


class MatchingChoice(models.Model):
    id = models.AutoField(primary_key=True)
    matching = models.ForeignKey(Matching, related_name='matching_choices', on_delete=models.CASCADE)
    choice_text = models.TextField(blank=True, null=True)

    def __str__(self):
        return str(self.id)

    def has_matching_answer(self, text_value):
        matching_answers = MatchingAnswer.objects.filter(matching_choice=self.id, answer_text=text_value).order_by('answer_text').values_list('answer_text', flat=True)
        return len(matching_answers) > 0


class MatchingAnswer(models.Model):
    id = models.AutoField(primary_key=True)
    matching_choice = models.ForeignKey(MatchingChoice, related_name='matching_answers', on_delete=models.CASCADE)
    answer_text = models.TextField(blank=True, null=True)

    def __str__(self):
        return str(self.id)


class Ordering(models.Model):
    id = models.AutoField(primary_key=True)
    question = models.ForeignKey(Question, related_name='ordering', on_delete=models.CASCADE)
    text = models.TextField(blank=True, null=True)
    order = models.PositiveSmallIntegerField(blank=True, null=True)
    ord_feedback = models.TextField(blank=True, null=True)

    def __str__(self):
        return str(self.id)


class WrittenResponse(models.Model):
    id = models.AutoField(primary_key=True)
    question = models.ForeignKey(Question, related_name='written_response', on_delete=models.CASCADE)
    enable_student_editor = models.BooleanField(blank=True, null=True)
    initial_text = models.TextField(blank=True, null=True)
    answer_key = models.TextField(blank=True, null=True)
    enable_attachments = models.BooleanField(blank=True, null=True)

    def __str__(self):
        return str(self.id)

@receiver(post_delete, sender=QuestionLibrary, dispatch_uid="delete_files")
def delete_files(sender, instance, **kwargs):
    logger = FilenameLoggingAdapter(newlogger, {'filename': str(instance)})
    if path.exists(settings.MEDIA_ROOT + str(instance)):
        try:
            for root, dirs, files in walk(settings.MEDIA_ROOT + str(instance), topdown=False):
                for name in files:
                    remove(path.join(root, name))
                for name in dirs:
                    rmdir(path.join(root, name))
        except OSError as e:
            logger.error("Error deleting files")
        try:
            rmdir(settings.MEDIA_ROOT + str(instance))
        except OSError as e:
            # print("Error: %s : %s" % (settings.MEDIA_ROOT, e.strerror))
            logger.error("Error: %s : %s" % (settings.MEDIA_ROOT, e.strerror))
    logger.info("Questionlibrary and Files Deleted")


class CustomToken(Token):
    """
    The extended authorization token model to support tokens generated from external sources
    """
    def save(self, *args, **kwargs):
        # print(self.user)
        # print(self.key)
        if not self.key:
            self.key = self.generate_key()
        return super().save(*args, **kwargs)

    @classmethod
    def generate_key(cls):
        return binascii.hexlify(os.urandom(20)).decode()
        # return '1111111111111111111111111111111111111111'

class StatusResponse:

    def __init__(self, version_number, created=None):
        self.version_number = version_number
