from django.db.models import *
from django.contrib.postgres.fields import *

from datetime import datetime
import pytz
import uuid

# Create your models here.


class CompanyId(Model):
    name = CharField(max_length=100)
    company_code = CharField(max_length=100)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Company ID'
        verbose_name_plural = 'Company IDs'


class MetricEvent(Model):
    email = CharField(max_length=254, verbose_name='Email')
    company = CharField(max_length=300, verbose_name='Company')
    department = CharField(max_length=300, verbose_name='Department')
    account_type = IntegerField(verbose_name='Account Type')

    date = CharField(max_length=11, verbose_name='Date')
    time = ArrayField(IntegerField(), verbose_name='Time')
    timezone_abbreviation = CharField(max_length=100, verbose_name='Timezone')

    event_type = CharField(max_length=100, verbose_name='Event Type')
    session_id = CharField(max_length=100, verbose_name='Session ID')
    data = CharField(max_length=600, verbose_name='Data')  # actually a dict, stored as a json string.

    def __str__(self):
        return self.event_type

    class Meta:
        verbose_name = 'Metric Event'
        verbose_name_plural = 'Metric Events'


class PermissionBuffer(Model):
    creation_date = DateTimeField(auto_now_add=True)

    # session_id = CharField(max_length=100, verbose_name='Session ID')
    session_id = UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    encoded_email = CharField(max_length=254, verbose_name='Encoded Email', blank=True)
    company = CharField(max_length=300, verbose_name='Company', blank=True)
    department = CharField(max_length=300, verbose_name='Department', blank=True)
    account_type = IntegerField(verbose_name='Account Type', blank=True, null=True)

    @property
    def is_obsolete(self):
        utc = pytz.UTC
        now_utc = utc.localize(datetime.now())

        date_difference = now_utc - self.creation_date
        date_difference_hours = date_difference.seconds * 0.0002

        if date_difference_hours >= 1:
            return True
        else:
            return False

    def __str__(self):
        return '{}'.format(self.session_id)

    class Meta:
        verbose_name = 'Permission Buffer'
        verbose_name_plural = 'Permission Buffers'
