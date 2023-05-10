from datetime import datetime
from django.db import models
from django.contrib.auth.models import User


class Directory(models.Model):
    name = models.CharField(max_length=32)
    description = models.CharField(blank=True, max_length=150)
    creation_date = models.DateField(auto_now_add=True)
    modified_date = models.DateField(auto_now=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    parent = models.ForeignKey('Directory', on_delete=models.CASCADE, null=True, blank=True, default=None)
    active = models.BooleanField(default=True)


class File(models.Model):
    name = models.CharField(max_length=32)
    description = models.CharField(blank=True, max_length=150)
    creation_date = models.DateField(auto_now_add=True)
    modified_date = models.DateField(auto_now=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    parent = models.ForeignKey(Directory, on_delete=models.CASCADE, null=True, blank=True, default=None)
    active = models.BooleanField(default=True)
    code = models.TextField(blank=True, default="// type your code here", null=True)


class Section(models.Model):
    name = models.CharField(max_length=32, blank=True)
    description = models.TextField(blank=True)
    creation_date = models.DateField(auto_now_add=True)
    begin = models.IntegerField()
    end = models.IntegerField()
    file = models.ForeignKey(File, on_delete=models.CASCADE)
    content = models.TextField()
    parent = models.ForeignKey('Section', on_delete=models.CASCADE, null=True, blank=True, default=None)

    class Type(models.TextChoices):
        ASM_INPUT = "ASM", "Asm Input"
        DIRECTIVE = "D", "Directive"
        VARIABLE = "VAR", "Variable Declaration"
        EMPTY = "EMP", "Empty Line"
        COMMENT = "COM", "Comment"
        PROCEDURE = "PRC", "Procedure"
    type = models.CharField(max_length=3, choices=Type.choices, default=Type.PROCEDURE)

    class Status(models.IntegerChoices):
        OK = 0
        ERR = 1
        WAR = 2
    status = models.IntegerField(choices=Status.choices, default=Status.OK)
    data = models.IntegerField(blank=True, default=None, null=True)
