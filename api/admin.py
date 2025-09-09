# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

from django.contrib import admin


# Register your models here.

from .models import Fib, Matching, MatchingAnswer, MatchingChoice, \
MultipleChoice, MultipleChoiceAnswer, MultipleSelect, MultipleSelectAnswer, \
Ordering, Question, QuestionLibrary, Section, TrueFalse, WrittenResponse, Image, EndAnswer

admin.site.register(QuestionLibrary)
admin.site.register(Section)
admin.site.register(Question)
admin.site.register(MultipleChoice)
admin.site.register(MultipleChoiceAnswer)
admin.site.register(TrueFalse)
admin.site.register(MultipleSelect)
admin.site.register(MultipleSelectAnswer)
admin.site.register(Fib)
admin.site.register(WrittenResponse)
admin.site.register(Ordering)
admin.site.register(Matching)
admin.site.register(MatchingChoice)
admin.site.register(MatchingAnswer)
admin.site.register(Image)
admin.site.register(EndAnswer)
