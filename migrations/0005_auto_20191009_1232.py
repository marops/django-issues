# Generated by Django 2.1.7 on 2019-10-09 16:32

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('issues', '0004_auto_20190904_1246'),
    ]

    operations = [
        migrations.RenameField(
            model_name='document',
            old_name='response_id',
            new_name='response',
        ),
        migrations.AddField(
            model_name='document',
            name='issue',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='issues.Issue'),
        ),
    ]
