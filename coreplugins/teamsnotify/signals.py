import logging
from django.dispatch import receiver
from app.plugins.signals import task_completed, task_failed, task_removed
from app.plugins.functions import get_current_plugin
from . import teams
from . import config
from app.models import Task

logger = logging.getLogger('app.logger')


def hours_minutes_secs(milliseconds):
    if milliseconds == 0 or milliseconds == -1:
        return "-- : -- : --"

    ch = 60 * 60 * 1000
    cm = 60 * 1000
    h = milliseconds // ch
    m = (milliseconds - h * ch) // cm
    s = round((milliseconds - h * ch - m * cm) / 1000)
    pad = lambda n: '0' + str(n) if n < 10 else str(n)

    if s == 60:
        m += 1
        s = 0
    if m == 60:
        h += 1
        m = 0

    return ':'.join([pad(h), pad(m), pad(s)])


@receiver(task_completed)
def handle_task_completed(sender, task_id, **kwargs):
    if get_current_plugin(only_active=True) is None:
        return

    config_data = config.load()
    if not config_data.get("notify_task_completed"):
        return

    webhook_url = config_data.get("webhook_url", "")
    if not webhook_url:
        return

    try:
        task = Task.objects.get(id=task_id)
        title = "Task Completed"
        message = (
            "**Project:** %s\n\n"
            "**Task:** %s\n\n"
            "**Processing time:** %s"
        ) % (task.project.name, task.name, hours_minutes_secs(task.processing_time))

        teams.send_card(webhook_url, title, message, status_color="good")
    except Exception as e:
        logger.error("TeamsNotify: Error sending completion notification: %s" % str(e))


@receiver(task_failed)
def handle_task_failed(sender, task_id, **kwargs):
    if get_current_plugin(only_active=True) is None:
        return

    config_data = config.load()
    if not config_data.get("notify_task_failed"):
        return

    webhook_url = config_data.get("webhook_url", "")
    if not webhook_url:
        return

    try:
        task = Task.objects.get(id=task_id)
        title = "Task Failed"
        message = (
            "**Project:** %s\n\n"
            "**Task:** %s\n\n"
            "**Error:** %s\n\n"
            "**Processing time:** %s"
        ) % (task.project.name, task.name, task.last_error, hours_minutes_secs(task.processing_time))

        teams.send_card(webhook_url, title, message, status_color="attention")
    except Exception as e:
        logger.error("TeamsNotify: Error sending failure notification: %s" % str(e))


@receiver(task_removed)
def handle_task_removed(sender, task_id, **kwargs):
    if get_current_plugin(only_active=True) is None:
        return

    config_data = config.load()
    if not config_data.get("notify_task_removed"):
        return

    webhook_url = config_data.get("webhook_url", "")
    if not webhook_url:
        return

    try:
        task = Task.objects.get(id=task_id)
        title = "Task Removed"
        message = (
            "**Project:** %s\n\n"
            "**Task:** %s was removed"
        ) % (task.project.name, task.name)

        teams.send_card(webhook_url, title, message, status_color="warning")
    except Exception as e:
        logger.error("TeamsNotify: Error sending removal notification: %s" % str(e))
