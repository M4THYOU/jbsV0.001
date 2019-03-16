from django.contrib import admin

from .models import CompanyId, MetricEvent, PermissionBuffer

# Register your models here.

admin.site.register(CompanyId)
admin.site.register(MetricEvent)
admin.site.register(PermissionBuffer)
