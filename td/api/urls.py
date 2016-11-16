from django.conf.urls import url

from .views import QuestionnaireView, templanguages_json, lang_assignment_json, lang_assignment_changed_json, countries_json
from td.views import names_json_export


urlpatterns = [
    url(r"^questionnaire/$", QuestionnaireView.as_view(), name="questionnaire"),
    url(r"^templanguages/$", templanguages_json, name="templanguages"),
    url(r"^templanguages/assignment/$", lang_assignment_json, name="templanguages_assignment"),
    url(r"^templanguages/assignment/changed/$", lang_assignment_changed_json, name="templanguages_changed"),

    url(r"^languages/$", names_json_export, name="languages"),
    url(r"^countries/$", countries_json, name="countries"),
]
