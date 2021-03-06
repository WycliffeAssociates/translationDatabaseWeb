from __future__ import absolute_import

import logging
import json
import requests
import types

from django.contrib.contenttypes.models import ContentType
from django.core.cache import cache
from django.core.mail import send_mail
from django.db import connection, IntegrityError, models

from celery import task
from pinax.eventlog.models import log

from td import settings
from td.commenting.models import CommentTag
from td.imports.models import (
    EthnologueLanguageCode,
    EthnologueCountryCode,
    IMBPeopleGroup,
    SIL_ISO_639_3,
    WikipediaISOCountry,
    WikipediaISOLanguage
)
from td.resources.models import Title, Resource, Media

from .models import AdditionalLanguage, Country, Language, Region, JSONData
from .signals import languages_integrated


logger = logging.getLogger(__name__)


class TaskStatus(object):
    def __init__(self, success=False):
        self.success = success
        self.message = []


@task()
def create_comment_tag(instance):
    try:
        content_type = ContentType.objects.get_for_model(instance)
        pk = instance.id
        delete_comment_tag(instance)
        CommentTag.objects.create(name=instance.tag_slug, slug=instance.tag_slug, object_id=pk,
                                  content_type=content_type)
    except IntegrityError as e:
        logger.warning("CommentTag object cannot be created for object %s." % instance.__str__())
        logger.error(e.message)
        pass


@task()
def delete_comment_tag(instance):
    content_type = ContentType.objects.get_for_model(instance)
    tags = CommentTag.objects.filter(content_type=content_type, object_id=instance.id)
    tags.delete()


@task()
def update_alt_names(code):
    # Filter instead of get because diff langs may have the same
    #    iso-639-3 code. Specific example: 'pt' and 'pt-br'.
    for language in Language.objects.filter(iso_639_3=code):
        language.alt_names = ", ".join(sorted(language.alt_name_all))
        language.save()


@task()
def update_langnames_data():
    """
    Temporary way (using DB and management command) to solve langnames.json problem
    """
    langnames, created = JSONData.objects.get_or_create(name="langnames")
    langnames.data = Language.names_data()
    langnames.save()


@task()
def reset_langnames_cache(short=False):
    key = "langnames_short" if short else "langnames"
    fetching = "_".join([key, "fetching"])
    cache.set(fetching, True)
    cache.delete(key)
    cache.set(key, Language.names_data(short=short), None)
    cache.set(fetching, False)


@task()
def integrate_imports():
    """
    Integrate imported language data into the language model
    """
    cursor = connection.cursor()
    cursor.execute("""
select coalesce(nullif(x.part_1, ''), x.code) as code,
       coalesce(nullif(nn1.native_name, ''), nullif(nn2.native_name, ''), x.ref_name) as name,
       coalesce(nullif(nn1.language_name, ''), nn2.language_name, lc.name, '') as anglicized_name,
       coalesce(cc.code, ''),
       nullif(nn1.native_name, '') as nn1name,
       nn1.id,
       nullif(nn2.native_name, '') as nn2name,
       nn2.id,
       x.ref_name as xname,
       x.id,
       x.code as iso_639_3
  from imports_sil_iso_639_3 x
left join imports_ethnologuelanguagecode lc on x.code = lc.code
left join imports_wikipediaisolanguage nn1 on x.part_1 = nn1.iso_639_1
left join imports_wikipediaisolanguage nn2 on x.code = nn2.iso_639_3
left join imports_ethnologuecountrycode cc on lc.country_code = cc.code
 where lc.status = %s or lc.status is NULL order by code;
""", [EthnologueLanguageCode.STATUS_LIVING])
    rows = cursor.fetchall()
    rows.extend([
        (
            x.merge_code(), x.merge_name(), x.native_name, None, "", None, "",
            None, "!ADDL", x.id, x.three_letter
        )
        for x in AdditionalLanguage.objects.all()
    ])
    rows.sort()
    for r in rows:
        if r[0] is not None:
            language, _ = Language.objects.get_or_create(code=r[0])
            language.name = r[1]
            language.anglicized_name = r[2]
            if r[1] == r[4]:
                language.source = WikipediaISOLanguage.objects.get(pk=r[5])
            if r[1] == r[6]:
                language.source = WikipediaISOLanguage.objects.get(pk=r[7])
            if r[1] == r[8]:
                language.source = SIL_ISO_639_3.objects.get(pk=r[9])
            if r[8] == "!ADDL":
                language.source = AdditionalLanguage.objects.get(pk=r[9])
            if r[10] != "":
                language.iso_639_3 = r[10]
            language.save()
            if r[3]:
                language.country = next(iter(Country.objects.filter(code=r[3])), None)
                language.source = EthnologueCountryCode.objects.get(code=r[3])
                language.save()
    languages_integrated.send(sender=Language)
    log(user=None, action="INTEGRATED_SOURCE_DATA", extra={})


def _get_or_create_object(model, slug, name):
    o, c = model.objects.get_or_create(slug=slug)
    if c:
        o.name = name
        o.save()
    return o


@task()
def update_countries_from_imports():
    for ecountry in EthnologueCountryCode.objects.all():
        country, _ = Country.objects.get_or_create(code=ecountry.code)
        country.region = next(iter(Region.objects.filter(name=ecountry.area)), None)
        country.name = ecountry.name
        country.source = ecountry
        country.save()
    for wcountry in WikipediaISOCountry.objects.all():
        country, created_flag = Country.objects.get_or_create(code=wcountry.alpha_2)
        if created_flag:
            country.name = wcountry.english_short_name
        country.alpha_3_code = wcountry.alpha_3
        country.save()


@task()
def integrate_imb_language_data():
    imb_map = {
        "bible_stories": ("onestory-bible-stories", "OneStory Bible Storires", "audio", "Audio"),
        "jesus_film": ("jesus-film", "The Jesus Film", "video", "Video"),
        "gospel_recording": ("gospel-recording-grn", "Gospel Recording (GRN)", "audio", "Audio"),
        "radio_broadcast": ("radio-broadcast-twr-febc", "Radio Broadcast (TWR/FEBC)", "audio", "Audio"),
        "written_scripture": ("bible-portions", "Bible (Portions)", "print", "Print")
    }
    for imb in IMBPeopleGroup.objects.order_by("language").distinct("language"):
        language = next(iter(Language.objects.filter(iso_639_3=imb.rol)), None)
        if not language:
            language = next(iter(Language.objects.filter(code=imb.rol)), None)
        if language:
            for k in imb_map.keys():
                if getattr(imb, k):
                    title = _get_or_create_object(Title, imb_map[k][0], imb_map[k][1])
                    media = _get_or_create_object(Media, imb_map[k][2], imb_map[k][3])
                    resource, _ = Resource.objects.get_or_create(language=language, title=title)
                    resource.published_flag = True
                    resource.save()
                    resource.medias.add(media)
    for imb in IMBPeopleGroup.objects.order_by("language"):
        language = next(iter(Language.objects.filter(iso_639_3=imb.rol)), None)
        if not language:
            language = next(iter(Language.objects.filter(code=imb.rol)), None)
        if language:
            country = next(iter(Country.objects.filter(name=imb.country)), None)
            if country is not None:
                language.country = country
                language.source = imb
                language.save()


@task()
def notify_external_apps(action="", instance=None):
    """ Make a POST request based on action types to urls registered in EXT_APP_PUSH under settings """

    task_status = TaskStatus()

    if not isinstance(instance, models.Model):
        task_status.message.append("function is called with invalid 'instance'")
        return task_status
    if not isinstance(action, (str, unicode)) or action.strip() == "":
        task_status.message.append("function is called with invalid 'action'")
        return task_status
    if not isinstance(settings.EXT_APP_PUSH, types.ListType):
        task_status.message.append("settings.EXT_APP_PUSH is not a list")
        return task_status

    data = None

    if action == "CREATE":
        # If instance is created, serialize all concrete fields and assign them as data
        # serialized_instances = serializers.serialize('json', [instance])
        # serialized_data = json.loads(serialized_instances)[0]
        # data = serialized_data
        # data.update({"code": instance.code})
        task_status.message.append("%s is not supported at this moment" % action)
        return task_status
    elif action == "UPDATE":
        # If instance is edited, only pass the changed fields as data
        data = {
            "pk": instance.id,
            "code": instance.tracker.previous("code") if instance.tracker.has_changed("code") else instance.code,
            "fields": {key.replace("_id", ""): getattr(instance, key, "") for key in instance.tracker.changed().keys()}
        }
    elif action == "DELETE":
        # If instance is deleted, just pass the id
        # data = {
        #     "pk": instance.id,
        #     "code": instance.code,
        # }
        task_status.message.append("%s is not supported at this moment" % action)
        return task_status
    else:
        task_status.message.append("%s is not a valid option for 'action'" % action)
        return task_status

    # Include model name and action type in data to meet the spec. If action is 'CREATE', 'model' will be overridden by
    #    class name instead of what the serializer sets.
    # Also include (previous) code to help identify records, especially the ones created by outside apps.
    data.update({
        "model": instance.__class__.__name__,
        "action": action,
    })

    data = [data]

    # NOTE: Maybe this can be abstracted into a function for easier testing
    for app in settings.EXT_APP_PUSH:
        url = app.get("url")
        if "key" in app:
            key = app.get("key")
            url += "?key=" + key if key is not None else ""
        headers = {'Content-Type': 'application/json'}

        post_to_ext_app.delay(url, json.dumps(data), headers)

    task_status.success = True
    return task_status


@task()
def post_to_ext_app(url, data, headers):
    response = requests.post(url, data=data, headers=headers)
    if response.status_code != 202 or response.content != "":
        message = "POST to %s has failed." % url
        message += "\n"
        message += "\nsite_id: %s" % settings.SITE_ID
        message += "\ncontent: %s" % response.content
        message += "\ndata: %s" % data
        message += "\nstatus_code: %s" % response.status_code
        send_mail(
            "PORT shim rejects POST",
            message,
            "admin@unfoldingword.org",
            ["vicky_leong@wycliffeassociates.org"],
        )
