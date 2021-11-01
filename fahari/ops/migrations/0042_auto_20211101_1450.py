# Generated by Django 3.2.7 on 2021-11-01 11:50

import datetime
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
from django.utils.timezone import utc
import fahari.common.models.base_models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('common', '0024_auto_20210919_1704'),
        ('ops', '0041_auto_20211029_1229'),
    ]

    operations = [
        migrations.CreateModel(
            name='NotApplicableAnswer',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('active', models.BooleanField(default=True)),
                ('created', models.DateTimeField(default=django.utils.timezone.now)),
                ('created_by', models.UUIDField(blank=True, null=True)),
                ('updated', models.DateTimeField(default=django.utils.timezone.now)),
                ('updated_by', models.UUIDField(blank=True, null=True)),
                ('answered_on', models.DateTimeField(default=datetime.datetime.today)),
            ],
            options={
                'ordering': ('-updated', '-created'),
                'abstract': False,
            },
            managers=[
                ('objects', fahari.common.models.base_models.AbstractBaseManager()),
            ],
        ),
        migrations.AlterModelOptions(
            name='booleananswer',
            options={'ordering': ('-updated', '-created')},
        ),
        migrations.AlterModelOptions(
            name='groupsection',
            options={'ordering': ('precedence', 'title')},
        ),
        migrations.AlterModelOptions(
            name='numberanswer',
            options={'ordering': ('-updated', '-created')},
        ),
        migrations.AlterModelOptions(
            name='paragraphanswer',
            options={'ordering': ('-updated', '-created')},
        ),
        migrations.AlterModelOptions(
            name='questiongroup',
            options={'ordering': ('precedence', 'title')},
        ),
        migrations.AlterModelOptions(
            name='radiooptionanswer',
            options={'ordering': ('-updated', '-created')},
        ),
        migrations.AlterModelOptions(
            name='selectlistanswer',
            options={'ordering': ('-updated', '-created')},
        ),
        migrations.AlterModelOptions(
            name='shortanswer',
            options={'ordering': ('-updated', '-created')},
        ),
        migrations.RemoveConstraint(
            model_name='groupsection',
            name='unique_group_precedence',
        ),
        migrations.RemoveConstraint(
            model_name='questiongroup',
            name='unique_questiongroup_precedence',
        ),
        migrations.RenameField(
            model_name='booleananswer',
            old_name='answer_date',
            new_name='answered_on',
        ),
        migrations.RenameField(
            model_name='numberanswer',
            old_name='answer_date',
            new_name='answered_on',
        ),
        migrations.RenameField(
            model_name='paragraphanswer',
            old_name='answer_date',
            new_name='answered_on',
        ),
        migrations.RenameField(
            model_name='radiooptionanswer',
            old_name='answer_date',
            new_name='answered_on',
        ),
        migrations.RenameField(
            model_name='selectlistanswer',
            old_name='answer_date',
            new_name='answered_on',
        ),
        migrations.RenameField(
            model_name='shortanswer',
            old_name='answer_date',
            new_name='answered_on',
        ),
        migrations.AddField(
            model_name='booleananswer',
            name='questionnaire',
            field=models.ForeignKey(default='1587bf94-860b-4f4a-b939-ca7fbe7a0b67', on_delete=django.db.models.deletion.PROTECT, to='ops.mentorshipquestionnaire'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='mentorshipquestionnaire',
            name='start_date',
            field=models.DateTimeField(default=datetime.datetime(2021, 11, 1, 11, 44, 26, 155066, tzinfo=utc), editable=False),
        ),
        migrations.AddField(
            model_name='numberanswer',
            name='questionnaire',
            field=models.ForeignKey(default='1587bf94-860b-4f4a-b939-ca7fbe7a0b67', on_delete=django.db.models.deletion.PROTECT, to='ops.mentorshipquestionnaire'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='paragraphanswer',
            name='questionnaire',
            field=models.ForeignKey(default='1587bf94-860b-4f4a-b939-ca7fbe7a0b67', on_delete=django.db.models.deletion.PROTECT, to='ops.mentorshipquestionnaire'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='radiooptionanswer',
            name='questionnaire',
            field=models.ForeignKey(default='1587bf94-860b-4f4a-b939-ca7fbe7a0b67', on_delete=django.db.models.deletion.PROTECT, to='ops.mentorshipquestionnaire'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='selectlistanswer',
            name='questionnaire',
            field=models.ForeignKey(default='1587bf94-860b-4f4a-b939-ca7fbe7a0b67', on_delete=django.db.models.deletion.PROTECT, to='ops.mentorshipquestionnaire'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='shortanswer',
            name='questionnaire',
            field=models.ForeignKey(default='1587bf94-860b-4f4a-b939-ca7fbe7a0b67', on_delete=django.db.models.deletion.PROTECT, to='ops.mentorshipquestionnaire'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='groupsection',
            name='precedence',
            field=models.SmallIntegerField(),
        ),
        migrations.AlterField(
            model_name='mentorshipquestionnaire',
            name='submit_date',
            field=models.DateTimeField(blank=True, editable=False, null=True),
        ),
        migrations.AlterField(
            model_name='question',
            name='answer_type',
            field=models.CharField(choices=[('true_false', 'True/False'), ('yes_no', 'Yes/No'), ('number', 'Number'), ('short_answer', 'Short answer'), ('paragraph', 'Long answer'), ('radio_option', 'Pick an option'), ('select_list', 'Check options'), ('none', 'Not Applicable')], default='short_answer', help_text='Answer type', max_length=15),
        ),
        migrations.AlterField(
            model_name='question',
            name='query',
            field=models.TextField(verbose_name='Question'),
        ),
        migrations.AlterField(
            model_name='questiongroup',
            name='precedence',
            field=models.SmallIntegerField(),
        ),
        migrations.AlterUniqueTogether(
            name='booleananswer',
            unique_together={('questionnaire', 'question')},
        ),
        migrations.AlterUniqueTogether(
            name='numberanswer',
            unique_together={('questionnaire', 'question')},
        ),
        migrations.AlterUniqueTogether(
            name='paragraphanswer',
            unique_together={('questionnaire', 'question')},
        ),
        migrations.AlterUniqueTogether(
            name='radiooptionanswer',
            unique_together={('questionnaire', 'question')},
        ),
        migrations.AlterUniqueTogether(
            name='selectlistanswer',
            unique_together={('questionnaire', 'question')},
        ),
        migrations.AlterUniqueTogether(
            name='shortanswer',
            unique_together={('questionnaire', 'question')},
        ),
        migrations.AddField(
            model_name='notapplicableanswer',
            name='organisation',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='ops_notapplicableanswer_related', to='common.organisation'),
        ),
        migrations.AddField(
            model_name='notapplicableanswer',
            name='question',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='ops.question'),
        ),
        migrations.AddField(
            model_name='notapplicableanswer',
            name='questionnaire',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='ops.mentorshipquestionnaire'),
        ),
        migrations.RemoveField(
            model_name='booleananswer',
            name='facility',
        ),
        migrations.RemoveField(
            model_name='numberanswer',
            name='facility',
        ),
        migrations.RemoveField(
            model_name='paragraphanswer',
            name='facility',
        ),
        migrations.RemoveField(
            model_name='radiooptionanswer',
            name='facility',
        ),
        migrations.RemoveField(
            model_name='selectlistanswer',
            name='facility',
        ),
        migrations.RemoveField(
            model_name='shortanswer',
            name='facility',
        ),
        migrations.AlterUniqueTogether(
            name='notapplicableanswer',
            unique_together={('questionnaire', 'question')},
        ),
    ]
