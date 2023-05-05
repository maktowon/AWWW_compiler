from datetime import datetime
from django.db import models
from django.contrib.auth.models import User


class Directory(models.Model):
    name = models.CharField(max_length=32)
    description = models.TextField(blank=True)
    creation_date = models.DateField(auto_now_add=True)
    modified_date = models.DateField(auto_now=True, default=datetime.today)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    active = models.BooleanField(default=True)


class File(models.Model):
    name = models.CharField(max_length=32)
    description = models.TextField(blank=True)
    creation_date = models.DateField(auto_now_add=True)
    modified_date = models.DateField(auto_now=True, default=datetime.today)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    directory = models.ForeignKey(Directory, on_delete=models.CASCADE)
    active = models.BooleanField(default=True)


class Section(models.Model):
    name = models.CharField(max_length=32, blank=True)
    description = models.TextField(blank=True)
    creation_date = models.DateField(auto_now_add=True)
    begin = models.IntegerField()
    end = models.IntegerField()
    file = models.ForeignKey(File, on_delete=models.CASCADE)
    content = models.TextField()
    # TODO enum types for section
    # type =
    # status =
    # data =
