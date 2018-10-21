from django.db import models

# Create your models here.

class CompanyId(models.Model):
    name = models.CharField(max_length=100)
    company_code = models.CharField(max_length=100)

    def __str__(self):
        return self.name
