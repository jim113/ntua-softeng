# Generated by Django 2.1.2 on 2018-11-03 21:53

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('cheapiesgr', '0002_shop'),
    ]

    operations = [
        migrations.CreateModel(
            name='Answer',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('answer_text', models.CharField(max_length=2000)),
            ],
        ),
        migrations.CreateModel(
            name='Question',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('question_text', models.CharField(max_length=2000)),
            ],
        ),
        migrations.RenameField(
            model_name='category',
            old_name='Category1_id',
            new_name='category1',
        ),
        migrations.RenameField(
            model_name='category',
            old_name='Category_discription',
            new_name='category_description',
        ),
        migrations.RenameField(
            model_name='category1',
            old_name='Category1_discription',
            new_name='category1_description',
        ),
        migrations.RenameField(
            model_name='category1',
            old_name='Category2_id',
            new_name='category2',
        ),
        migrations.RenameField(
            model_name='category2',
            old_name='Category2_discription',
            new_name='category2_description',
        ),
        migrations.RenameField(
            model_name='rating',
            old_name='Rate_explanation',
            new_name='rate_explanation',
        ),
        migrations.RenameField(
            model_name='rating',
            old_name='Registration_id',
            new_name='registration',
        ),
        migrations.RenameField(
            model_name='rating',
            old_name='Stars',
            new_name='stars',
        ),
        migrations.RenameField(
            model_name='rating',
            old_name='Validity_of_this_rate',
            new_name='validity_of_this_rate',
        ),
        migrations.RenameField(
            model_name='rating',
            old_name='Volunteer_id',
            new_name='volunteer',
        ),
        migrations.RenameField(
            model_name='shop',
            old_name='Location',
            new_name='location',
        ),
        migrations.AddField(
            model_name='registration',
            name='category',
            field=models.ForeignKey(default='', on_delete=django.db.models.deletion.CASCADE, to='cheapiesgr.Category'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='registration',
            name='date_of_registration',
            field=models.DateField(default='0000-00-00'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='registration',
            name='price',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='registration',
            name='product_description',
            field=models.CharField(default='', max_length=200),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='registration',
            name='shop',
            field=models.ForeignKey(default='', on_delete=django.db.models.deletion.CASCADE, to='cheapiesgr.Shop'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='registration',
            name='volunteer',
            field=models.ForeignKey(default='', on_delete=django.db.models.deletion.CASCADE, to='cheapiesgr.Volunteer'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='question',
            name='registration',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='cheapiesgr.Registration'),
        ),
        migrations.AddField(
            model_name='answer',
            name='question',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='cheapiesgr.Question'),
        ),
    ]
