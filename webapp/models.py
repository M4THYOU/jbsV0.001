from django.db.models import *

# Create your models here.


class EmailInterest(Model):
    created_at = DateTimeField(auto_now_add=True, verbose_name='Creation Date')
    updated_at = DateTimeField(auto_now=True, verbose_name='Last Updated')

    email = EmailField(verbose_name='Email')
    ip_address = GenericIPAddressField(protocol='both', unpack_ipv4=True, verbose_name='IP Address')

    def __str__(self):
        return self.email

    class Meta:
        verbose_name = 'Email Interest'
        verbose_name_plural = 'Email Interests'
