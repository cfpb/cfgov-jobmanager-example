from __future__ import absolute_import

from django.db import models

from wagtail.wagtailadmin.edit_handlers import (
    FieldPanel, FieldRowPanel, InlinePanel, MultiFieldPanel, ObjectList,
    TabbedInterface
)
from wagtail.wagtailcore.fields import RichTextField
from wagtail.wagtailcore.models import PageManager

from jobmanager.models.django import (
    JobCategory, JobLength, JobLocation, ServiceType
)
from v1.models import CFGOVPage
from v1.models.snippets import ReusableText


class JobListingPage(CFGOVPage):
    description = RichTextField('Summary')
    open_date = models.DateField('Open date')
    close_date = models.DateField('Close date')
    salary_min = models.DecimalField(
        'Minimum salary',
        max_digits=11,
        decimal_places=2
    )
    salary_max = models.DecimalField(
        'Maximum salary',
        max_digits=11,
        decimal_places=2
    )
    division = models.ForeignKey(
        JobCategory,
        on_delete=models.PROTECT,
        null=True
    )
    job_length = models.ForeignKey(
        JobLength,
        on_delete=models.PROTECT,
        null=True,
        verbose_name="Position length",
        blank=True
    )
    service_type = models.ForeignKey(
        ServiceType,
        on_delete=models.PROTECT,
        null=True,
        blank=True
    )
    location = models.ForeignKey(
        JobLocation,
        related_name='job_listings',
        on_delete=models.PROTECT
    )
    allow_remote = models.BooleanField(
        default=False,
        help_text='Adds remote option to jobs with office locations.',
        verbose_name="Location can also be remote"
    )
    responsibilities = RichTextField(
        'Responsibilities',
        null=True,
        blank=True
    )
    travel_required = models.BooleanField(
        blank=False,
        default=False,
        help_text=(
            'Optional: Check to add a "Travel required" section to the '
            'job description. Section content defaults to "Yes".'
        )
    )
    travel_details = RichTextField(
        null=True,
        blank=True,
        help_text='Optional: Add content for "Travel required" section.'
    )
    additional_section_title = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        help_text='Optional: Add title for an additional section '
                  'that will display at end of job description.'
    )
    additional_section_content = RichTextField(
        null=True,
        blank=True,
        help_text='Optional: Add content for an additional section '
                  'that will display at end of job description.'
    )
    content_panels = CFGOVPage.content_panels + [
        MultiFieldPanel([
            FieldPanel('division', classname='full'),
            InlinePanel('grades', label='Grades'),
            FieldRowPanel([
                FieldPanel('open_date', classname='col6'),
                FieldPanel('close_date', classname='col6'),
            ]),
            FieldRowPanel([
                FieldPanel('salary_min', classname='col6'),
                FieldPanel('salary_max', classname='col6'),
            ]),
            FieldRowPanel([
                FieldPanel('service_type', classname='col6'),
                FieldPanel('job_length', classname='col6'),
            ]),
        ], heading='Details'),
        MultiFieldPanel([
            FieldPanel('location', classname='full'),
            FieldPanel('allow_remote', classname='full'),
        ], heading='Location'),
        MultiFieldPanel([
            FieldPanel('description', classname='full'),
            FieldPanel('responsibilities', classname='full'),
            FieldPanel('travel_required', classname='full'),
            FieldPanel('travel_details', classname='full'),
            FieldPanel('additional_section_title', classname='full'),
            FieldPanel('additional_section_content', classname='full'),
        ], heading='Description'),
        InlinePanel(
            'usajobs_application_links',
            label='USAJobs application links'
        ),
        InlinePanel(
            'email_application_links',
            label='Email application links'
        ),
    ]

    edit_handler = TabbedInterface([
        ObjectList(content_panels, heading='Content'),
        ObjectList(CFGOVPage.settings_panels, heading='Configuration'),
    ])

    template = 'jobmanager/job-description-page/index.html'

    objects = PageManager()

    def get_context(self, request, *args, **kwargs):
        context = super(JobListingPage, self).get_context(request)
        try:
            context['about_us'] = ReusableText.objects.get(
                title='About us (For consumers)')
        except Exception:
            pass
        if hasattr(self.location, 'region'):
            context['states'] = [state.abbreviation for state in
                                 self.location.region.states.all()]
            context['location_type'] = 'region'
        else:
            context['states'] = []
            context['location_type'] = 'office'
        context['cities'] = self.location.cities.all()
        return context

    @property
    def page_js(self):
        return super(JobListingPage, self).page_js + ['read-more.js']

    @property
    def ordered_grades(self):
        """Return a list of job grades in numerical order.
        Non-numeric grades are sorted alphabetically after numeric grades.
        """
        grades = set(g.grade.grade for g in self.grades.all())
        return sorted(grades, key=lambda g: int(g) if g.isdigit() else g)
