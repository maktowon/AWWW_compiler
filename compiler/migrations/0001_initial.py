# Generated by Django 4.1.7 on 2023-05-29 16:53

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Directory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=32)),
                ('description', models.CharField(blank=True, max_length=150)),
                ('creation_date', models.DateField(auto_now_add=True)),
                ('modified_date', models.DateField(auto_now=True)),
                ('active', models.BooleanField(default=True)),
                ('owner', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('parent', models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.CASCADE, to='compiler.directory')),
            ],
        ),
        migrations.CreateModel(
            name='File',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=32)),
                ('description', models.CharField(blank=True, max_length=150)),
                ('creation_date', models.DateField(auto_now_add=True)),
                ('modified_date', models.DateField(auto_now=True)),
                ('active', models.BooleanField(default=True)),
                ('code', models.TextField(blank=True, default='// type your code here', null=True)),
                ('owner', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('parent', models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.CASCADE, to='compiler.directory')),
            ],
        ),
        migrations.CreateModel(
            name='Section',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, max_length=32)),
                ('description', models.CharField(blank=True, max_length=150)),
                ('creation_date', models.DateField(auto_now_add=True)),
                ('begin', models.IntegerField()),
                ('end', models.IntegerField()),
                ('content', models.TextField()),
                ('type', models.CharField(choices=[('ASM', 'Asm Input'), ('D', 'Directive'), ('VAR', 'Variable Declaration'), ('EMP', 'Empty Line'), ('COM', 'Comment'), ('PRC', 'Procedure')], default='PRC', max_length=3)),
                ('status', models.IntegerField(choices=[(0, 'Ok'), (1, 'Err'), (2, 'War')], default=0)),
                ('data', models.IntegerField(blank=True, default=None, null=True)),
                ('file', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='compiler.file')),
                ('owner', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('parent', models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.CASCADE, to='compiler.section')),
            ],
        ),
    ]