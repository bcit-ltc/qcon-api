# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

import copy
from difflib import Match
import os
import random
import shutil
import datetime
import re
import time
import xml.etree.cElementTree as ET
from uuid import UUID
from .xmlcdata import CDATA
from os import makedirs, path, walk
from os.path import basename
from django.conf import settings
from xml.dom.minidom import parseString
from zipfile import *


class XmlWriter:
    def __init__(self, question_library):
        ident = datetime.datetime.now().strftime("%Y%m%d%H%M%S%f")
        questionLibraryIdent = "QLIB_" + ident
        root_el = ET.Element("questestinterop")
        objectbank_el = ET.SubElement(root_el, "objectbank", {"ident": questionLibraryIdent, "xmlns:d2l_2p0": "http://desire2learn.com/xsd/d2lcp_v2p0"})
        
        # root_section_obj = question_library.get_root_section()
        # root_section_el = self.create_section(objectbank_el, root_section_obj)

        base_ident = "SECT_" + str(datetime.datetime.now().strftime("%Y%m%d%H%M%S")) + str(int(UUID(int=0x12345678123456781234567812345678)))
        base_section_el = ET.SubElement(objectbank_el, "section", {"ident": base_ident, "title": question_library.main_title})
        if question_library.shuffle is True:
            self.create_section_shuffle(base_section_el)

        self.create_presentation_material(base_section_el, "") # we currently not catching any base section text and it's ignored in ANTLR
        
        sec_proc = ET.SubElement(base_section_el, "sectionproc_extension")
        sec_proc_dis_name = ET.SubElement(sec_proc, "d2l_2p0:display_section_name")
        # TODO: add is_title_displayed and text to QuestionLibrary because not all exam has root section
        sec_proc_dis_name.text = "yes" # section_obj.is_title_displayed if section_obj.is_title_displayed else "yes"
        sec_proc_dis_line = ET.SubElement(sec_proc, "d2l_2p0:display_section_line")
        sec_proc_dis_line.text = "no"
        sec_proc_dis_sec = ET.SubElement(sec_proc, "d2l_2p0:type_display_section")
        sec_proc_dis_sec.text = "0" # "1" if section_obj.is_text_displayed else "0"


        section_objs = question_library.get_sections()
        for section_obj in section_objs:
            if section_obj.is_main_content is True:
                root_question_objs = section_obj.get_questions()
                self.create_questions(base_section_el, root_question_objs)
            else:
                current_section_el = self.create_section(base_section_el, section_obj)
                question_objs = section_obj.get_questions()
                self.create_questions(current_section_el, question_objs)
        self.questiondb_string = self.xml_to_string(root_el)


    def create_section(self, parent_el, section_obj):
        sectionIdent = "SECT_" + str(datetime.datetime.now().strftime("%Y%m%d%H%M%S")) + str(int(UUID(int=0x12345678123456781234567812345678)))
        section_el = ET.SubElement(parent_el, "section", {"ident": sectionIdent, "title": section_obj.title})
        if section_obj.shuffle is True:
            self.create_section_shuffle(section_el)

        self.create_presentation_material(section_el, section_obj.text)
        self.create_sectionproc_extension(section_el, section_obj)

        return section_el


    def create_section_shuffle(self, section_el):
        # section > selection_ordering > order
        sel_ord = ET.SubElement(section_el, "selection_ordering")
        sel_ord_ord = ET.SubElement(sel_ord, "order", {"order_type": "Random"})


    def create_presentation_material(self, section_el, section_text):
        # presentation_material Node
        sec_pres_mat = ET.SubElement(section_el, "presentation_material")
        sec_pres_mat_flo = ET.SubElement(sec_pres_mat, "flow_mat")
        sec_pres_mat_flo_flo = ET.SubElement(sec_pres_mat_flo, "flow_mat")
        sec_pres_mat_flo_flo_mat = ET.SubElement(sec_pres_mat_flo_flo, "material")
        sec_pres_mat_flo_flo_mat_text = ET.SubElement(sec_pres_mat_flo_flo_mat, "mattext", {"texttype": "text/html"})
        if section_text:
            sec_pres_mat_flo_flo_mat_text.append(CDATA(section_text))


    def create_sectionproc_extension(self, section_el, section_obj):
        # presentation_material Node
        sec_proc = ET.SubElement(section_el, "sectionproc_extension")
        sec_proc_dis_name = ET.SubElement(sec_proc, "d2l_2p0:display_section_name")
        sec_proc_dis_name.text = section_obj.is_title_displayed if section_obj.is_title_displayed else "yes"
        sec_proc_dis_line = ET.SubElement(sec_proc, "d2l_2p0:display_section_line")
        sec_proc_dis_line.text = "no"
        sec_proc_dis_sec = ET.SubElement(sec_proc, "d2l_2p0:type_display_section")
        sec_proc_dis_sec.text = "1" if section_obj.is_text_displayed else "0"


    def create_questions(self, section_el, question_objs):
        for question in question_objs:
            time_ns = str(time.process_time_ns())
            random_int = str(random.randint(1000000, 9999999))
            ident = time_ns + random_int
            question_ident = "QUES_" + ident
            item_el = ET.Element("item", {"ident": "OBJ_" + ident, "label": question_ident, "d2l_2p0:page": "1", "title": question.title})
            # question_type = question.get_question_type()
            question_type = question.questiontype
            match question_type:
                case "MC":
                    self.generate_multiple_choice(item_el, question_ident, question)
                case "TF":
                    self.generate_true_false(item_el, question_ident, question)
                case "FIB" | "FMB":
                    self.generate_fill_in_the_blanks(item_el, question_ident, question)
                case "MS" | "MR":
                    self.generate_multi_select(item_el, question_ident, question)
                case "MAT" | "MT":
                    self.generate_matching(item_el, question_ident, question)
                case "ORD":
                    self.generate_ordering(item_el, question_ident, question)
                case "WR" | "E":
                    self.generate_written_response(item_el, question_ident, question)

            section_el.append(item_el)


    def itemetadata(self, it, question_type, question):
        # ItemData Node
        it_metadata = ET.SubElement(it, "itemmetadata")
        it_metadata_qtidata = ET.SubElement(it_metadata, "qtimetadata")
        it_computer_scored = ET.SubElement(it_metadata_qtidata, "qti_metadatafield")
        it_computer_scored_label = ET.SubElement(it_computer_scored, "fieldlabel")
        it_computer_scored_label.text = "qmd_computerscored"
        it_computer_scored_entry = ET.SubElement(it_computer_scored, "fieldentry")
        it_computer_scored_entry.text = "yes"
        it_question_type = ET.SubElement(it_metadata_qtidata, "qti_metadatafield")
        it_question_type_label = ET.SubElement(it_question_type, "fieldlabel")
        it_question_type_label.text = "qmd_questiontype"
        it_question_type_entry = ET.SubElement(it_question_type, "fieldentry")
        it_question_type_entry.text = question_type
        it_weighting = ET.SubElement(it_metadata_qtidata, "qti_metadatafield")
        it_weighting_label = ET.SubElement(it_weighting, "fieldlabel")
        it_weighting_label.text = "qmd_weighting"
        it_weighting_entry = ET.SubElement(it_weighting, "fieldentry")
        it_weighting_entry.text = "{:.4f}".format(question.points)


    def itemproc_extension(self, it):
        # Itemproc_extension Node
        it_proc = ET.SubElement(it, "itemproc_extension")
        it_proc_difficulty = ET.SubElement(it_proc, "d2l_2p0:difficulty")
        it_proc_difficulty.text = "1"
        it_proc_isbonus = ET.SubElement(it_proc, "d2l_2p0:isbonus")
        it_proc_isbonus.text = "no"
        it_proc_ismandatory = ET.SubElement(it_proc, "d2l_2p0:ismandatory")
        it_proc_ismandatory.text = "no"


    def generate_feedback(self, it, ident, feedback):
        it_fb = ET.SubElement(it, "itemfeedback", {"ident": ident})
        it_fb_mat = ET.SubElement(it_fb, "material")
        it_fb_mat_text = ET.SubElement(it_fb_mat, "mattext", {"texttype": "text/html"})
        it_fb_mat_text.append(CDATA(feedback))


    def generate_hint(self, it, hint):
        it_hint = ET.SubElement(it, "hint")
        it_hint_mat = ET.SubElement(it_hint, "hintmaterial")
        it_hint_mat_flow = ET.SubElement(it_hint_mat, "flow_mat")
        it_hint_mat_flow_mat = ET.SubElement(it_hint_mat_flow, "material")
        it_hint_mat_flow_text = ET.SubElement(it_hint_mat_flow_mat, "mattext", {"texttype": "text/html"})
        it_hint_mat_flow_text.append(CDATA(hint))


    def xml_to_string(self, xml):
        rough_string = ET.tostring(xml, "utf-8")
        reparsed = parseString(rough_string)
        pretty_xml = reparsed.toprettyxml(indent="\t")
        return pretty_xml


    def create_manifest(self, manifest_entity, folder_path):
        path = folder_path + "/imsmanifest.xml"
        root = ET.Element("manifest", {"xmlns:d2l_2p0": "http://desire2learn.com/xsd/d2lcp_v2p0", "xmlns": "http://www.imsglobal.org/xsd/imscp_v1p1", "identifier": "MANIFEST_1"})
        doc = ET.SubElement(root, "resources")

        for resource in manifest_entity.resources:
            ET.SubElement(
                doc, "resource", {"identifier": resource.identifier, "type": resource.resource_type, "d2l_2p0:material_type": resource.material_type, "href": resource.href, "d2l_2p0:link_target": resource.link_target, "title": resource.title}
            )

        tree = ET.ElementTree(root)
        # tree.write(path)
        return tree


    def generate_multiple_choice(self, it, question_ident, question):
        self.itemetadata(it, "Multiple Choice", question)
        self.itemproc_extension(it)
        question_lid = question_ident + "_LID"
        question_ident_answer = question_ident + "_A"
        question_ident_feedback = question_ident + "_IF"

        # Presentation Node
        it_pre = ET.SubElement(it, "presentation")
        it_pre_flow = ET.SubElement(it_pre, "flow")

        # Presentation -> Flow
        it_pre_flow_mat = ET.SubElement(it_pre_flow, "material")

        # Presentation -> Material
        multiple_choice = question.get_multiple_choice()
        it_pre_flow_mat_text = ET.SubElement(it_pre_flow_mat, "mattext", {"texttype": "text/html"})
        question_text = question.text
        it_pre_flow_mat_text.append(CDATA(question_text))

        # Presentation -> Flow -> Response_extension
        it_pre_flow_res = ET.SubElement(it_pre_flow, "response_extension")
        it_pre_flow_res_display_style = ET.SubElement(it_pre_flow_res, "d2l_2p0:display_style")
        it_pre_flow_res_display_style.text = "2"
        it_pre_flow_res_enumeration = ET.SubElement(it_pre_flow_res, "d2l_2p0:enumeration")
        it_pre_flow_res_enumeration.text = str(multiple_choice.enumeration) if multiple_choice.enumeration else "4"
        it_pre_flow_res_grading_type = ET.SubElement(it_pre_flow_res, "d2l_2p0:grading_type")
        it_pre_flow_res_grading_type.text = "0"
        # Presentation -> Flow -> Response_lid
        it_pre_flow_lid = ET.SubElement(it_pre_flow, "response_lid", {"ident": question_lid, "rcardinality": "Multiple"})

        # Commented this to deactivate MC randomized answer order
        it_pre_flow_lid_render_choice = ET.SubElement(it_pre_flow_lid, "render_choice", {"shuffle": ("yes" if multiple_choice.randomize else "no")})

        # Add hint
        if question.hint:
            self.generate_hint(it, question.hint)

        # Reprocessing
        it_res = ET.SubElement(it, "resprocessing")

        # Add General feedback
        if question.feedback:
            self.generate_feedback(it, question_ident, question.feedback)

        mc_answer_index = 1
        for mc_answer in multiple_choice.get_multiple_choice_answers():

            # Presentation -> Flow -> Response_lid -> Render_choice -> Flow_label
            flow = ET.SubElement(it_pre_flow_lid_render_choice, "flow_label", {"class": "Block"})
            response_label = ET.SubElement(flow, "response_label", {"ident": question_ident_answer + str(mc_answer_index)})
            flow_mat = ET.SubElement(response_label, "flow_mat")
            material = ET.SubElement(flow_mat, "material")
            mattext = ET.SubElement(material, "mattext", {"texttype": "text/html"})
            mattext.append(CDATA(mc_answer.answer))

            # Reprocessing -> Respcondition
            it_res_con = ET.SubElement(it_res, "respcondition", {"title": "Response Condition" + str(mc_answer_index)})
            it_res_con_var = ET.SubElement(it_res_con, "conditionvar")
            it_res_con_var_equal = ET.SubElement(it_res_con_var, "varequal", {"respident": question_lid})
            it_res_con_var_equal.text = question_ident_answer + str(mc_answer_index)
            it_res_set_var = ET.SubElement(it_res_con, "setvar", {"action": "Set"})
            it_res_set_var.text = str(mc_answer.weight) if mc_answer.weight else "0.0000"
            it_res_dis = ET.SubElement(it_res_con, "displayfeedback", {"feedbacktype": "Response", "linkrefid": question_ident_feedback + str(mc_answer_index)})

            # Add Answer specific feedback
            if mc_answer.answer_feedback:
                self.generate_feedback(it, question_ident_feedback + str(mc_answer_index), mc_answer.answer_feedback)
            mc_answer_index += 1


    def generate_true_false(self, it, question_ident, question):
        self.itemetadata(it, "True/False", question)
        self.itemproc_extension(it)

        question_lid = question_ident + "_LID"
        question_ident_answer = question_ident + "_A"
        question_ident_feedback = question_ident + "_IF"

        # Presentation Node
        it_pre = ET.SubElement(it, "presentation")
        it_pre_flow = ET.SubElement(it_pre, "flow")

        # Presentation -> Flow
        it_pre_flow_mat = ET.SubElement(it_pre_flow, "material")

        true_false = question.get_true_false()
        # Presentation -> Material
        it_pre_flow_mat_text = ET.SubElement(it_pre_flow_mat, "mattext", {"texttype": "text/html"})
        question_text = question.text
        it_pre_flow_mat_text.append(CDATA(question_text))

        # Presentation -> Flow -> Response_extension
        it_pre_flow_res = ET.SubElement(it_pre_flow, "response_extension")
        it_pre_flow_res_display_style = ET.SubElement(it_pre_flow_res, "d2l_2p0:display_style")
        it_pre_flow_res_display_style.text = "2"
        it_pre_flow_res_enumeration = ET.SubElement(it_pre_flow_res, "d2l_2p0:enumeration")
        it_pre_flow_res_enumeration.text = str(true_false.enumeration) if true_false.enumeration else "4"
        it_pre_flow_res_grading_type = ET.SubElement(it_pre_flow_res, "d2l_2p0:grading_type")
        it_pre_flow_res_grading_type.text = "0"

        # Presentation -> Flow -> Response_lid
        it_pre_flow_lid = ET.SubElement(it_pre_flow, "response_lid", {"ident": question_lid, "rcardinality": "Single"})
        it_pre_flow_lid_render_choice = ET.SubElement(it_pre_flow_lid, "render_choice", {"shuffle": "no"})

        # Reprocessing
        it_res = ET.SubElement(it, "resprocessing")

        # Add General feedback
        if question.feedback:
            self.generate_feedback(it, question_ident, question.feedback)

        tf_index = 0
        answer_text = ["True", "False"]
        while tf_index < 2:
            # Presentation -> Flow -> Response_lid -> Render_choice -> Flow_label
            flow = ET.SubElement(it_pre_flow_lid_render_choice, "flow_label", {"class": "Block"})
            response_label = ET.SubElement(flow, "response_label", {"ident": question_ident_answer + str(tf_index)})
            flow_mat = ET.SubElement(response_label, "flow_mat")
            material = ET.SubElement(flow_mat, "material")
            mattext = ET.SubElement(material, "mattext", {"texttype": "text/plain"})
            mattext.text = answer_text[tf_index]

            # Reprocessing -> Respcondition
            it_res_con = ET.SubElement(it_res, "respcondition", {"title": "Response Condition" + str(tf_index)})
            it_res_con_var = ET.SubElement(it_res_con, "conditionvar")
            it_res_con_var_equal = ET.SubElement(it_res_con_var, "varequal", {"respident": question_lid})
            it_res_con_var_equal.text = question_ident_answer + str(tf_index)
            it_res_set_var = ET.SubElement(it_res_con, "setvar", {"action": "Set"})

            if tf_index == 0:
                current_weight = true_false.true_weight
                current_feedback = true_false.true_feedback
            else:
                current_weight = true_false.false_weight
                current_feedback = true_false.false_feedback

            it_res_set_var.text = str(current_weight) if current_weight else "0.0000"
            it_res_dis = ET.SubElement(it_res_con, "displayfeedback", {"feedbacktype": "Response", "linkrefid": question_ident_feedback + str(tf_index)})

            # Add Answer specific feedback
            if current_feedback:
                self.generate_feedback(it, question_ident_feedback + str(tf_index), current_feedback)
            tf_index += 1


    def generate_fill_in_the_blanks(self, it, question_ident, question):
        self.itemetadata(it, "Fill in the Blanks", question)
        self.itemproc_extension(it)

        # Presentation Node
        it_pre = ET.SubElement(it, "presentation")
        it_pre_flow = ET.SubElement(it_pre, "flow")
        # Presentation -> Flow

        idx = 1
        for fib in question.get_fibs():
            question_str = question_ident + str(idx) + "_STR"
            question_ans = question_ident + str(idx) + "_ANS"
            if fib.type == "fibanswer":
                # Presentation -> Flow -> Response_str
                it_pre_flow_str = ET.SubElement(it_pre_flow, "response_str", {"rcardinality": "Single", "ident": question_str})
                it_pre_flow_str_render = ET.SubElement(it_pre_flow_str, "render_fib", {"fibtype": "String", "prompt": "Box", "columns": "30", "rows": "1"})
                it_pre_flow_str_render_label = ET.SubElement(it_pre_flow_str_render, "response_label", {"ident": question_ans})
                idx += 1
            elif fib.type == "fibquestion":
                # Presentation -> Flow -> Material
                it_pre_flow_mat = ET.SubElement(it_pre_flow, "material")
                it_pre_flow_mat_text = ET.SubElement(it_pre_flow_mat, "mattext", {"texttype": "text/html"})
                question_text = fib.text
                it_pre_flow_mat_text.append(CDATA(question_text))

        # Add hint
        if question.hint:
            self.generate_hint(it, question.hint)

        # Resprocessing
        it_res = ET.SubElement(it, "resprocessing")
        it_out = ET.SubElement(it_res, "outcomes")

        index = 1
        for fib_answers in question.get_fib_answers():
            answers = [a.strip() for a in fib_answers.text.split(",")]

            answer_weight = str(100.0 / len(question.get_fib_answers()))
            question_ans = question_ident + str(index) + "_ANS"
            for answer in answers:
                it_res_con = ET.SubElement(it_res, "respcondition")
                it_res_con_var = ET.SubElement(it_res_con, "conditionvar")
                it_res_con_var_equal = ET.SubElement(it_res_con_var, "varequal", {"case": "no", "respident": question_ans})
                it_res_con_var_equal.text = answer
                it_res_set_var = ET.SubElement(it_res_con, "setvar", {"action": "Set"})
                it_res_set_var.text = answer_weight

            it_out_score = ET.SubElement(it_out, "decvar", {"varname": "Blank_" + str(index), "maxvalue": "100", "minvalue": "0", "vartype": "Integer"})

            index += 1

        # Add General feedback
        if question.feedback:
            self.generate_feedback(it, question_ident, question.feedback)


    def generate_multi_select(self, it, question_ident, question):
        self.itemetadata(it, "Multi-Select", question)
        self.itemproc_extension(it)

        question_lid = question_ident + "_LID"
        question_ident_answer = question_ident + "_A"
        question_ident_feedback = question_ident + "_IF"

        # Presentation Node
        it_pre = ET.SubElement(it, "presentation")
        it_pre_flow = ET.SubElement(it_pre, "flow")

        # Presentation -> Flow
        it_pre_flow_mat = ET.SubElement(it_pre_flow, "material")

        multiple_select = question.get_multiple_select()
        # Presentation -> Material
        it_pre_flow_mat_text = ET.SubElement(it_pre_flow_mat, "mattext", {"texttype": "text/html"})
        question_text = question.text
        it_pre_flow_mat_text.append(CDATA(question_text))

        # Presentation -> Flow -> Response_extension
        it_pre_flow_res = ET.SubElement(it_pre_flow, "response_extension")
        it_pre_flow_res_display_style = ET.SubElement(it_pre_flow_res, "d2l_2p0:display_style")
        it_pre_flow_res_display_style.text = "2"
        it_pre_flow_res_enumeration = ET.SubElement(it_pre_flow_res, "d2l_2p0:enumeration")
        it_pre_flow_res_enumeration.text = str(multiple_select.enumeration) if multiple_select.enumeration else "4"
        it_pre_flow_res_grading_type = ET.SubElement(it_pre_flow_res, "d2l_2p0:grading_type")
        it_pre_flow_res_grading_type.text = "2"

        # Presentation -> Flow -> Response_lid
        it_pre_flow_lid = ET.SubElement(it_pre_flow, "response_lid", {"ident": question_lid, "rcardinality": "Multiple"})
        it_pre_flow_lid_render_choice = ET.SubElement(it_pre_flow_lid, "render_choice", {"shuffle": ("yes" if multiple_select.randomize else "no")})

        # Add hint
        if question.hint:
            self.generate_hint(it, question.hint)

        # Reprocessing
        it_res = ET.SubElement(it, "resprocessing")
        it_out = ET.SubElement(it_res, "outcomes")
        it_out_score = ET.SubElement(it_out, "decvar", {"vartype": "Integer", "defaultval": "0", "varname": "que_score", "minvalue": "0", "maxvalue": "100"})
        it_out_correct = ET.SubElement(it_out, "decvar", {"vartype": "Integer", "defaultval": "0", "varname": "D2L_Correct", "minvalue": "0"})
        it_out_incorrect = ET.SubElement(it_out, "decvar", {"vartype": "Integer", "defaultval": "0", "varname": "D2L_Incorrect", "minvalue": "0"})

        # Add General feedback
        if question.feedback:
            self.generate_feedback(it, question_ident, question.feedback)

        ms_index = 1
        for ms_answer in multiple_select.get_multiple_select_answers():

            # Presentation -> Flow -> Response_lid -> Render_choice -> Flow_label
            flow = ET.SubElement(it_pre_flow_lid_render_choice, "flow_label", {"class": "Block"})
            response_label = ET.SubElement(flow, "response_label", {"ident": question_ident_answer + str(ms_index)})
            flow_mat = ET.SubElement(response_label, "flow_mat")
            material = ET.SubElement(flow_mat, "material")
            mattext = ET.SubElement(material, "mattext", {"texttype": "text/html"})
            mattext.text = ms_answer.answer

            # Reprocessing -> Respcondition
            it_res_con = ET.SubElement(it_res, "respcondition", {"title": "Response Condition", "continue": "yes"})
            it_res_con_var = ET.SubElement(it_res_con, "conditionvar")
            it_res_con_var_equal = ET.SubElement(it_res_con_var, "varequal", {"respident": question_lid})
            it_res_con_var_equal.text = question_ident_answer

            it_res_con_var_equal.text = question_ident_answer + str(ms_index)
            if ms_answer.is_correct == True:
                it_res_set_var = ET.SubElement(it_res_con, "setvar", {"varname": "D2L_Correct", "action": "Add"})
            else:
                it_res_set_var = ET.SubElement(it_res_con, "setvar", {"varname": "D2L_Incorrect", "action": "Add"})

            # Add Answer specific feedback
            if ms_answer.answer_feedback:
                self.generate_feedback(it, question_ident_feedback + str(ms_index), ms_answer.answer_feedback)
            ms_index += 1

        it_res_con = ET.SubElement(it_res, "respcondition")
        it_res_set_var = ET.SubElement(it_res_con, "setvar", {"varname": "que_score", "action": "Set"})
        it_res_set_var.text = "D2L_Correct"


    def generate_matching(self, it, question_ident, question):
        self.itemetadata(it, "Matching", question)
        self.itemproc_extension(it)
        matching = question.get_matching()
        question_ident_choice = question_ident + "_C"
        question_ident_answer = question_ident + "_A"
        question_ident_feedback = question_ident + "_IF"

        # Presentation Node
        it_pre = ET.SubElement(it, "presentation")
        it_pre_flow = ET.SubElement(it_pre, "flow")

        # Add hint
        if question.hint:
            self.generate_hint(it, question.hint)

        # Resprocessing Node
        it_res = ET.SubElement(it, "resprocessing")

        # Resprocessing -> Outcomes
        it_res_out = ET.SubElement(it_res, "outcomes")
        it_res_out_dec_correct = ET.SubElement(it_res_out, "decvar", {"vartype": "Integer", "defaultval": "0", "varname": "D2L_Correct", "minvalue": "0", "maxvalue": "100"})
        it_res_out_dec_incorrect = ET.SubElement(it_res_out, "decvar", {"vartype": "Integer", "defaultval": "0", "varname": "D2L_Incorrect", "minvalue": "0", "maxvalue": "100"})
        it_res_out_dec_score = ET.SubElement(it_res_out, "decvar", {"vartype": "Decimal", "defaultval": "0", "varname": "que_score", "minvalue": "0", "maxvalue": "100"})

        # Presentation -> Flow
        it_pre_flow_mat = ET.SubElement(it_pre_flow, "material")

        # Presentation -> Material
        it_pre_flow_mat_text = ET.SubElement(it_pre_flow_mat, "mattext", {"texttype": "text/html"})
        question_text = question.text
        it_pre_flow_mat_text.append(CDATA(question_text))

        # Presentation -> Flow -> Response_extension
        it_pre_flow_res = ET.SubElement(it_pre_flow, "response_extension")
        it_pre_flow_res_grading_type = ET.SubElement(it_pre_flow_res, "d2l_2p0:grading_type")
        it_pre_flow_res_grading_type.text = '2' #str(matching.grading_type)

        # Presentation -> Flow -> Response_grp -> Render_choice
        it_pre_flow_res_grp_ren = ET.Element("render_choice", {"shuffle": "yes"})  # add to response_grp later
        it_pre_flow_res_grp_ren_flow = ET.SubElement(it_pre_flow_res_grp_ren, "flow_label", {"class": "Block"})

        it_temp = ET.Element("temp")
        matching_answers = matching.get_unique_matching_answers()

        ma_index = 1
        for matching_answer_text in matching_answers:
            matching_answer_index = question_ident_answer + str(ma_index)
            it_grp_ren_flow_lab = ET.SubElement(it_pre_flow_res_grp_ren_flow, "response_label", {"ident": matching_answer_index})
            it_grp_ren_flow_lab_flow = ET.SubElement(it_grp_ren_flow_lab, "flow_mat")
            it_grp_ren_flow_lab_flow_mat = ET.SubElement(it_grp_ren_flow_lab_flow, "material")
            it_grp_ren_flow_lab_flow_mat_text = ET.SubElement(it_grp_ren_flow_lab_flow_mat, "mattext", {"texttype": "text/html"})
            it_grp_ren_flow_lab_flow_mat_text.append(CDATA(matching_answer_text))

            it_respcondition = ET.SubElement(it_temp, "respcondition")
            it_respcondition_conditionvar = ET.SubElement(it_respcondition, "conditionvar")
            it_respcondition_varequal = ET.SubElement(it_respcondition_conditionvar, "varequal")
            it_respcondition_varequal.text = matching_answer_index
            it_respcondition_setvar = ET.SubElement(it_respcondition, "setvar", {"action": "Add"})
            it_respcondition_setvar.text = "1"

            ma_index += 1

        mc_index = 1
        for matching_choice in matching.get_matching_choices():
            matching_choice_index = question_ident_choice + str(mc_index)

            # Presentation -> Flow -> Response_grp
            it_pre_flow_res_grp = ET.SubElement(it_pre_flow, "response_grp", {"respident": matching_choice_index, "rcardinality": "Single"})

            # Presentation -> Flow -> Response_grp -> Material
            it_pre_flow_res_grp_mat = ET.SubElement(it_pre_flow_res_grp, "material")
            it_pre_flow_res_grp_mattext = ET.SubElement(it_pre_flow_res_grp_mat, "mattext", {"texttype": "text/html"})
            it_pre_flow_res_grp_mattext.append(CDATA(matching_choice.choice_text))
            it_pre_flow_res_grp.append(it_pre_flow_res_grp_ren)

            for respcondition in it_temp:
                conditionvar = respcondition.find("conditionvar")
                varequal = conditionvar.find("varequal")
                varequal.set("respident", matching_choice_index)
                setvar = respcondition.find("setvar")
                answer_mattext = it_pre_flow.find("response_grp[@respident='" + matching_choice_index + "'].//response_label[@ident='" + varequal.text + "'].//mattext")
                is_correct = matching_choice.has_matching_answer(answer_mattext[0].text)
                if is_correct is True:
                    setvar.set("varname", "D2L_Correct")
                else:
                    setvar.set("varname", "D2L_Incorrect")
                it_res.append(copy.deepcopy(respcondition))
            mc_index += 1

        match matching.grading_type:
            case 0:
                it_respcondition = ET.SubElement(it_res, "respcondition")
                it_respcondition_var = ET.SubElement(it_respcondition, "conditionvar")
                it_respcondition_var_other = ET.SubElement(it_respcondition_var, "other")
                it_resp_setvar = ET.SubElement(it_respcondition, "setvar", {"varname": "que_score", "action": "Set"})
                it_resp_setvar.text = "D2L_Correct"
            case 1:
                it_respcondition = ET.SubElement(it_res, "respcondition")
                it_respcondition_var = ET.SubElement(it_respcondition, "conditionvar")
                it_respcondition_var_vargte = ET.SubElement(it_respcondition_var, "vargte", {"respident": "D2L_Incorrect"})
                it_respcondition_var_vargte.text = "0"
                it_resp_setvar = ET.SubElement(it_respcondition, "setvar", {"varname": "que_score", "action": "Set"})
                it_resp_setvar.text = "0"

                it_respcondition2 = copy.deepcopy(it_respcondition)
                it_resp_setvar2 = it_respcondition2.find("setvar")
                it_resp_setvar2.text = "1"
                it_res.append(it_respcondition2)
            case 2:
                it_respcondition = ET.SubElement(it_res, "respcondition")
                it_respcondition_var = ET.SubElement(it_respcondition, "conditionvar")
                it_respcondition_var_vargte = ET.SubElement(it_respcondition_var, "vargte", {"respident": "D2L_Incorrect"})
                it_respcondition_var_vargte.text = "D2L_Correct"
                it_resp_setvar = ET.SubElement(it_respcondition, "setvar", {"varname": "que_score", "action": "Set"})
                it_resp_setvar.text = "0"

                it_respcondition2 = ET.SubElement(it_res, "respcondition")
                it_respcondition_var2 = ET.SubElement(it_respcondition2, "conditionvar")
                it_respcondition_var_varlt = ET.SubElement(it_respcondition_var2, "varlt", {"respident": "D2L_Incorrect"})
                it_respcondition_var_vargte.text = "D2L_Correct"
                it_resp_setvar2 = ET.SubElement(it_respcondition2, "setvar", {"varname": "que_score", "action": "Set"})
                it_resp_setvar2.text = "D2L_Correct"
                it_resp_setvar3 = ET.SubElement(it_respcondition2, "setvar", {"varname": "que_score", "action": "Subtract"})
                it_resp_setvar3.text = "D2L_Incorrect"

        # Add General feedback
        if question.feedback:
            self.generate_feedback(it, question_ident, question.feedback)


    def generate_ordering(self, it, question_ident, question):
        self.itemetadata(it, "Ordering", question)
        self.itemproc_extension(it)

        question_o = question_ident + "_O"
        question_ident_feedback = question_ident + "_IF"

        # Presentation Node
        it_pre = ET.SubElement(it, "presentation")
        it_pre_flow = ET.SubElement(it_pre, "flow")

        # Presentation -> Flow

        # Presentation -> Flow -> Material
        it_pre_flow_mat = ET.SubElement(it_pre_flow, "material")
        it_pre_flow_mat_text = ET.SubElement(it_pre_flow_mat, "mattext", {"texttype": "text/html"})
        question_text = question.text
        it_pre_flow_mat_text.append(CDATA(question_text))

        # Presentation -> Flow -> Response_extension
        it_pre_flow_res_ext = ET.SubElement(it_pre_flow, "response_extension")
        it_pre_flow_res_ext_grading = ET.SubElement(it_pre_flow_res_ext, "d2l_2p0:grading_type")
        grading_type = 2  # Equally weighted, All or nothing, Right minus wrong
        it_pre_flow_res_ext_grading.append(CDATA(grading_type))

        # Presentation -> Flow -> Response_grp
        it_pre_flow_res_grp = ET.SubElement(it_pre_flow, "response_grp", {"ident": question_o, "rcardinality": "Ordered"})
        it_pre_flow_res_grp_render = ET.SubElement(it_pre_flow_res_grp, "render_choice", {"shuffle": "yes"})
        it_pre_flow_res_grp_render_flow = ET.SubElement(it_pre_flow_res_grp_render, "flow_label", {"class": "Block"})  # populated in the loop

        # Add hint
        if question.hint:
            self.generate_hint(it, question.hint)

        # Resprocessing
        it_res = ET.SubElement(it, "resprocessing")  # populated in the loop
        it_out = ET.SubElement(it_res, "outcomes")

        it_out_correct = ET.SubElement(it_out, "decvar", {"maxvalue": "100", "minvalue": "0", "varname": "D2L_Correct", "defaultval": "0", "vartype": "Integer"})
        it_out_incorrect = ET.SubElement(it_out, "decvar", {"minvalue": "0", "varname": "D2L_Incorrect", "defaultval": "0", "vartype": "Integer"})
        it_out_que_score = ET.SubElement(it_out, "decvar", {"minvalue": "0", "varname": "que_score", "defaultval": "0", "vartype": "Integer"})

        it_res_con_other = ET.SubElement(it_res, "respcondition")
        it_res_con_other_var = ET.SubElement(it_res_con_other, "conditionvar")
        it_res_con_other_var_other = ET.SubElement(it_res_con_other_var, "other")
        it_res_con_other_setvar = ET.SubElement(it_res_con_other, "setvar", {"varname": "que_score", "action": "Set"})
        it_res_con_other_setvar.text = "D2L_Correct"

        # Add General feedback
        if question.feedback:
            self.generate_feedback(it, question_ident, question.feedback)

        ord_index = 1
        for ord in question.get_orderings():
            ident_num = question_o + str(ord_index)
            # Presentation -> Flow -> Response_grp -> response_label
            it_pre_flow_res_grp_render_flow_res = ET.SubElement(it_pre_flow_res_grp_render_flow, "response_label", {"ident": ident_num})
            it_pre_flow_res_grp_render_flow_res_flow = ET.SubElement(it_pre_flow_res_grp_render_flow_res, "flow_mat")
            it_pre_flow_res_grp_render_flow_res_flow_mat = ET.SubElement(it_pre_flow_res_grp_render_flow_res_flow, "material")
            it_pre_flow_res_grp_render_flow_res_flow_mat_text = ET.SubElement(it_pre_flow_res_grp_render_flow_res_flow_mat, "mattext", {"texttype": "text/html"})
            question_text = ord.text
            it_pre_flow_res_grp_render_flow_res_flow_mat_text.append(CDATA(question_text))

            # Resprocessing -> Respcondition
            it_res_con_correct = ET.SubElement(it_res, "respcondition", {"title": "Correct Condition"})
            it_res_con_correct_var = ET.SubElement(it_res_con_correct, "conditionvar")
            it_res_con_correct_var_equal = ET.SubElement(it_res_con_correct_var, "varequal", {"respident": ident_num})
            it_res_con_correct_var_equal.text = str(ord_index)
            it_res_con_correct_setvar = ET.SubElement(it_res_con_correct, "setvar", {"varname": "D2L_Correct", "action": "Add"})
            it_res_con_correct_setvar.text = str(1)

            it_res_con_incorrect = ET.SubElement(it_res, "respcondition", {"title": "Incorrect Condition"})
            it_res_con_incorrect_var = ET.SubElement(it_res_con_incorrect, "conditionvar")
            it_res_con_incorrect_var_not = ET.SubElement(it_res_con_incorrect_var, "not")
            it_res_con_incorrect_var_not_equal = ET.SubElement(it_res_con_incorrect_var_not, "varequal", {"respident": ident_num})
            it_res_con_incorrect_var_not_equal.text = str(ord_index)
            it_res_con_incorrect_setvar = ET.SubElement(it_res_con_incorrect, "setvar", {"varname": "D2L_Incorrect", "action": "Add"})
            it_res_con_incorrect_setvar.text = str(1)

            # Add Answer specific feedback
            if ord.ord_feedback:
                self.generate_feedback(it, question_ident_feedback + str(ord_index), ord.ord_feedback)
            ord_index += 1


    def generate_written_response(self, it, question_ident, question):
        self.itemetadata(it, "Long Answer", question)
        self.itemproc_extension(it)

        question_ident_str = question_ident + "_STR"
        question_ident_la = question_ident + "_LA"

        # Presentation Node
        it_pre = ET.SubElement(it, "presentation")
        it_pre_flow = ET.SubElement(it_pre, "flow")

        written_response = question.get_written_response()

        # Presentation -> Flow
        # Presentation -> Flow -> Material
        it_pre_flow_mat = ET.SubElement(it_pre_flow, "material")
        it_pre_flow_mat_text = ET.SubElement(it_pre_flow_mat, "mattext", {"texttype": "text/html"})
        question_text = question.text
        it_pre_flow_mat_text.append(CDATA(question_text))

        # Presentation -> Flow -> Response_extension
        it_pre_flow_mat_res_ext = ET.SubElement(it_pre_flow, "response_extension")
        it_pre_flow_mat_res_ext_sign = ET.SubElement(it_pre_flow_mat_res_ext, "d2l_2p0:has_signed_comments")
        it_pre_flow_mat_res_ext_sign.append(CDATA("no"))
        it_pre_flow_mat_res_ext_editor = ET.SubElement(it_pre_flow_mat_res_ext, "d2l_2p0:has_htmleditor")

        # Change it to "no" to deactivate student HTML editor answer
        it_pre_flow_mat_res_ext_editor.append(CDATA("no"))

        # Presentation -> Flow -> Response_str
        it_pre_flow_mat_res_str = ET.SubElement(it_pre_flow, "response_str", {"rcardinality": "Multiple", "ident": question_ident_str})
        it_pre_flow_mat_res_str_render = ET.SubElement(it_pre_flow_mat_res_str, "render_fib", {"fibtype": "String", "prompt": "Box", "columns": "100", "rows": "15"})
        it_pre_flow_mat_res_str_render_label = ET.SubElement(it_pre_flow_mat_res_str_render, "response_label", {"ident": question_ident_la})
        it_pre_flow_mat_res_str_render_label_mat = ET.SubElement(it_pre_flow_mat_res_str_render_label, "material")
        it_pre_flow_mat_res_str_render_label_mat_text = ET.SubElement(it_pre_flow_mat_res_str_render_label_mat, "mattext", {"texttype": "text/html"})

        # Add hint
        if question.hint:
            self.generate_hint(it, question.hint)
        # Add General feedback
        if question.feedback:
            self.generate_feedback(it, question_ident, question.feedback)
        # Initial_text
        it_init_text = ET.SubElement(it, "initial_text")
        it_init_text_mat = ET.SubElement(it, "initial_text_material")
        it_init_text_mat_flow = ET.SubElement(it_init_text_mat, "flow_mat")
        it_init_text_mat_flow_mat = ET.SubElement(it_init_text_mat_flow, "material")
        it_init_text_mat_flow_mat_text = ET.SubElement(it_init_text_mat_flow_mat, "mattext", {"texttype": "text/html"})
        # Answer_key
        it_ans = ET.SubElement(it, "answer_key")
        it_ans_mat = ET.SubElement(it_ans, "answer_key_material")
        it_ans_mat_flow = ET.SubElement(it_ans_mat, "flow_mat")
        it_ans_mat_flow_mat = ET.SubElement(it_ans_mat_flow, "material")
        it_ans_mat_flow_mat_text = ET.SubElement(it_ans_mat_flow_mat, "mattext", {"texttype": "text/html"})
        it_ans_mat_flow_mat_text.append(CDATA(written_response.answer_key))
