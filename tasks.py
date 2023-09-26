from celery import shared_task
from django.core.management import call_command

@shared_task
def update_productivity_levels_task():
    call_command('update_productivity_levels')
