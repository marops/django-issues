# Generated by Django 2.1.8 on 2019-06-14 20:09

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('issues', '0007_auto_20190425_1004'),
    ]

    operations = [
        migrations.AlterField(
            model_name='issue',
            name='location',
            field=models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.CASCADE, to='issues.Location', to_field='lid'),
        ),
    ]