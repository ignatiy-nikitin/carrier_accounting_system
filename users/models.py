from django.contrib.auth.models import AbstractUser
from django.db import models

# from companies.models import Company
from companies.models import Company


class User(AbstractUser):
    # нужна ли отдельная модель (думаю, что да)
    # company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='users')
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='users', null=True, blank=True)
    # key = models.CharField(max_length=64, unique=True)  # зачем? не подойдет ли обычный Token?
    blocked = models.BooleanField(default=False)
    name = models.CharField(max_length=264, blank=True)

    first_name = None
    last_name = None
    # email = models.EmailField(required=False)
    # role -> models.Role


