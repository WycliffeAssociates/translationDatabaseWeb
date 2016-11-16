from __future__ import absolute_import

import logging

from celery import task

from .models import Translator, Material, Charter, Event, Facilitator

logger = logging.getLogger(__name__)


@task
def export_facilitator_data():
    return Facilitator.export_data()


@task()
def export_event_data():
    return Event.export_data()


@task()
def export_charter_data():
    return Charter.export_data()


@task()
def export_material_data():
    return Material.export_data()


@task()
def export_translator_data():
    return Translator.export_data()
