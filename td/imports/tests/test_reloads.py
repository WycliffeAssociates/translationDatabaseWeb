import os

from django.test import TestCase

from eventlog.models import Log
from mock import patch, Mock

from ..models import (
    EthnologueCountryCode,
    EthnologueLanguageCode,
    EthnologueLanguageIndex,
    SIL_ISO_639_3,
    WikipediaISOLanguage
)


class BaseReloadTestMixin(object):

    ModelClass = None
    filename = ""
    expected_success_count = 0
    log_reload_failed_action = ""

    @classmethod
    def setUpClass(cls):
        cls.data = open(os.path.join(os.path.dirname(__file__), "data", cls.filename)).read()

    def test_reload(self):
        with patch("td.imports.models.requests") as mock_requests:
            mock_requests.get.return_value = mock_response = Mock()
            mock_response.status_code = 200
            mock_response.content = self.data
            self.ModelClass.reload()
            self.assertEquals(self.ModelClass.objects.count(), self.expected_success_count)

    def test_reload_no_content(self):
        with patch("td.imports.models.requests") as mock_requests:
            mock_requests.get.return_value = mock_response = Mock()
            mock_response.status_code = 200
            mock_response.content = ""
            self.ModelClass.reload()
            self.assertEquals(self.ModelClass.objects.count(), 0)

    def test_reload_bad_response(self):
        with patch("td.imports.models.requests") as mock_requests:
            mock_requests.get.return_value = mock_response = Mock()
            mock_response.status_code = 500
            mock_response.content = ""
            self.ModelClass.reload()
            self.assertEquals(self.ModelClass.objects.count(), 0)
            self.assertTrue(Log.objects.filter(action=self.log_reload_failed_action).exists())


class WikipediaReloadTests(BaseReloadTestMixin, TestCase):

    ModelClass = WikipediaISOLanguage
    filename = "wikipedia.html"
    expected_success_count = 184
    log_reload_failed_action = "SOURCE_WIKIPEDIA_RELOAD_FAILED"


class SILISO639_3ReloadTests(BaseReloadTestMixin, TestCase):

    ModelClass = SIL_ISO_639_3
    filename = "iso_639_3.tab"
    expected_success_count = 7879
    log_reload_failed_action = "SOURCE_SIL_ISO_639_3_RELOAD_FAILED"


class EthnologueCountryCodeReloadTests(BaseReloadTestMixin, TestCase):

    ModelClass = EthnologueCountryCode
    filename = "CountryCodes.tab"
    expected_success_count = 234
    log_reload_failed_action = "SOURCE_ETHNOLOGUE_COUNTRY_CODE_RELOAD_FAILED"


class EthnologueLanguageCodeReloadTests(BaseReloadTestMixin, TestCase):

    ModelClass = EthnologueLanguageCode
    filename = "LanguageCodes.tab"
    expected_success_count = 7479
    log_reload_failed_action = "SOURCE_ETHNOLOGUE_LANG_CODE_RELOAD_FAILED"


class EthnologueLanguageIndexReloadTests(BaseReloadTestMixin, TestCase):

    ModelClass = EthnologueLanguageIndex
    filename = "LanguageIndex.tab"
    expected_success_count = 57197
    log_reload_failed_action = "SOURCE_ETHNOLOGUE_LANG_INDEX_RELOAD_FAILED"
