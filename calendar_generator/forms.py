"""Forms for calendars"""

from typing import Dict, Optional
from datetime import date

from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _

from . import models


class CustomCalendarForm(forms.Form):
    """Form to generate a custom calendar"""

    title = forms.CharField(max_length=255)
    start_date = forms.DateField(widget=forms.DateInput(attrs={"type": "date"}))
    end_date = forms.DateField(widget=forms.DateInput(attrs={"type": "date"}))

    def __init__(
        self, *args, calendar: models.Calendar, initial: Optional[Dict] = None, **kwargs
    ):
        self._calendar = calendar
        super().__init__(*args, initial=initial, **kwargs)

    def clean_start_date(self):
        """Make sure the start date is appropriate"""

        start_date = self.cleaned_data["start_date"]
        if start_date > self._calendar.end_date:
            raise ValidationError(
                _("Start date must be before the calendar's end date")
            )

        return start_date

    def clean_end_date(self):
        """Make sure the end date is appropriate"""

        end_date = self.cleaned_data["end_date"]
        if end_date < self._calendar.start_date:
            raise ValidationError(_("End date must be after the calendar's start date"))

        return end_date

    def clean(self):
        """Cross-validate all fields"""

        cleaned_data = super().clean()

        start_date = cleaned_data.get("start_date")
        end_date = cleaned_data.get("end_date")

        if start_date and end_date:
            assert isinstance(start_date, date)
            assert isinstance(end_date, date)

            if (end_date - start_date).days < 1:
                raise ValidationError(_("End date must be after start date"))

        return cleaned_data
