from django.db import models


class Company(models.Model):
    name = models.CharField(max_length=256)
    is_transport_company = models.BooleanField(default=False)

    def __str__(self):
        return self.name
