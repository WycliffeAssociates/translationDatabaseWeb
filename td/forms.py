from __future__ import absolute_import

from django import forms

from .models import Network, Language, Country, TempLanguage
from .utils import fill_language_data
from .fields import LanguageCharField
from .resources.forms import EntityTrackingForm
from .resources.models import Questionnaire


class TempLanguageForm(forms.ModelForm):
    required_css_class = "required"

    def __init__(self, *args, **kwargs):
        super(TempLanguageForm, self).__init__(*args, **kwargs)
        questionnaire_pk = Questionnaire.objects.latest("created_at").pk
        self.fields["questionnaire"].widget = forms.HiddenInput(attrs={"value": questionnaire_pk})

    class Meta:
        model = TempLanguage
        fields = ["code", "questionnaire"]
        labels = {"code": "Temporary Tag"}
        widgets = {"code": forms.HiddenInput()}


class NetworkForm(EntityTrackingForm):
    required_css_class = "required"

    class Meta:
        model = Network
        fields = ["name"]


class CountryForm(EntityTrackingForm):
    required_css_class = "required"
    gl = forms.CharField(max_length=12)

    def clean_gl(self):
        pk = self.cleaned_data["gl"]
        if pk:
            return Language.objects.get(pk=pk).code

    def __init__(self, *args, **kwargs):
        super(CountryForm, self).__init__(*args, **kwargs)
        self.fields["primary_networks"].widget.attrs["class"] = "select2-multiple"
        self.fields["primary_networks"].help_text = ""
        self.fields["gl"] = LanguageCharField(required=False, label="Gateway Language")
        if self.instance.pk is not None:
            if self.instance.gateway_language():
                lang = self.instance.gateway_language()
                self.fields["gl"].initial = lang.pk
                self.fields["gl"] = fill_language_data(self.fields["gl"], lang)

    def save(self, commit=True):
        self.instance.extra_data.update({"gateway_language": self.cleaned_data["gl"]})
        return super(CountryForm, self).save(commit=commit)

    class Meta:
        model = Country
        fields = ["name", "region", "population", "primary_networks"]


class LanguageForm(EntityTrackingForm):
    required_css_class = "required"

    def clean_gateway_language(self):
        pk = self.cleaned_data["gateway_language"]
        if pk:
            return Language.objects.get(pk=pk)

    def __init__(self, *args, **kwargs):
        super(LanguageForm, self).__init__(*args, **kwargs)
        self.fields["networks_translating"].widget.attrs["class"] = "select2-multiple"
        self.fields["networks_translating"].help_text = ""
        self.fields["gateway_language"] = LanguageCharField(required=False)
        if self.instance.pk is not None:
            lang = self.instance.gateway_language
            if lang:
                self.fields["gateway_language"] = fill_language_data(self.fields["gateway_language"], lang)

    class Meta:
        model = Language
        exclude = ["alt_name", "alt_names", "variant_of", "extra_data", "tracker"]
        widgets = {"code": forms.HiddenInput()}


class UploadGatewayForm(forms.Form):
    required_css_class = "required"
    languages = forms.CharField(widget=forms.Textarea())

    def clean_languages(self):
        lang_ids = [l.strip() for l in self.cleaned_data["languages"].split("\n")]
        errors = [lid for lid in lang_ids if not Language.objects.filter(code=lid)]
        if errors:
            raise forms.ValidationError("You entered some invalid language codes: {}".format(", ".join(errors)))
        return lang_ids
