def load():
    from app.plugins.functions import get_current_plugin
    plugin = get_current_plugin(only_active=True)
    data_store = plugin.get_global_data_store()

    return {
        'webhook_url': data_store.get_string('webhook_url', default=""),
        'notify_task_completed': data_store.get_bool('notify_task_completed', default=True),
        'notify_task_failed': data_store.get_bool('notify_task_failed', default=True),
        'notify_task_removed': data_store.get_bool('notify_task_removed', default=False),
    }


def save(data: dict):
    from app.plugins.functions import get_current_plugin
    plugin = get_current_plugin(only_active=True)
    data_store = plugin.get_global_data_store()

    data_store.set_string('webhook_url', data.get('webhook_url'))
    data_store.set_bool('notify_task_completed', data.get('notify_task_completed'))
    data_store.set_bool('notify_task_failed', data.get('notify_task_failed'))
    data_store.set_bool('notify_task_removed', data.get('notify_task_removed'))
