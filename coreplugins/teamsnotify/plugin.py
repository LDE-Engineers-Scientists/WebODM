from app.plugins import PluginBase, Menu, MountPoint
from django.utils.translation import gettext as _
from django.shortcuts import render
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django import forms
from . import teams
from . import config


class ConfigurationForm(forms.Form):
    webhook_url = forms.URLField(
        label='Teams Webhook URL',
        max_length=500,
        required=True,
        widget=forms.URLInput(attrs={
            'class': 'form-control',
            'placeholder': 'https://prod-XX.westus.logic.azure.com/workflows/...'
        }),
    )
    notify_task_completed = forms.BooleanField(
        label='Notify on Task Completed',
        required=False,
    )
    notify_task_failed = forms.BooleanField(
        label='Notify on Task Failed',
        required=False,
    )
    notify_task_removed = forms.BooleanField(
        label='Notify on Task Removed',
        required=False,
    )

    def test_settings(self, request):
        try:
            teams.send_card(
                self.cleaned_data['webhook_url'],
                'WebODM - Test Notification',
                'This is a test notification from WebODM Teams Notification plugin.',
                status_color='good',
            )
            messages.success(request, "Test message sent to Teams successfully!")
        except Exception as e:
            messages.error(request, "Failed to send test message: %s" % str(e))

    def save_settings(self):
        config.save(self.cleaned_data)


class Plugin(PluginBase):
    def main_menu(self):
        return [Menu(_("Teams Notification"), self.public_url(""), "fa fa-bell fa-fw")]

    def app_mount_points(self):

        @login_required
        def index(request):
            if request.method == "POST":
                form = ConfigurationForm(request.POST)
                test_configuration = request.POST.get("test_configuration")
                if form.is_valid() and test_configuration:
                    form.test_settings(request)
                elif form.is_valid() and not test_configuration:
                    form.save_settings()
                    messages.success(request, "Teams notification settings saved!")
            else:
                config_data = config.load()
                form = ConfigurationForm(initial=config_data)

            return render(request, self.template_path('index.html'), {
                'form': form,
                'title': 'Teams Notification',
            })

        return [
            MountPoint('$', index),
        ]
