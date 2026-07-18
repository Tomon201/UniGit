from django.db import models
from django.contrib.auth.models import User # Стандартная модель юзера

class Repository(models.Model):
    # Привязываем репозиторий к конкретному юзеру
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='repositories')
    name = models.CharField(max_length=255)
    full_name = models.CharField(max_length=255)

    def __str__(self):
        return self.name

class Commit(models.Model):
    repository = models.ForeignKey(Repository, on_delete=models.CASCADE, related_name='commits')
    message = models.TextField()
    sha = models.CharField(max_length=40, unique=True)

    def __str__(self):
        return self.message[:50]