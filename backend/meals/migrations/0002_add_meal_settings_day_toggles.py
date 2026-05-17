from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('meals', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='mealsettings',
            name='monday_enabled',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='mealsettings',
            name='tuesday_enabled',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='mealsettings',
            name='wednesday_enabled',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='mealsettings',
            name='thursday_enabled',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='mealsettings',
            name='friday_enabled',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='mealsettings',
            name='saturday_enabled',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='mealsettings',
            name='sunday_enabled',
            field=models.BooleanField(default=True),
        ),
    ]
