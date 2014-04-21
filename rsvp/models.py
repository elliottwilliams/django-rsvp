import datetime
import pytz
from django.db import models
from django.db.models import permalink
from django.core.mail import send_mass_mail
from django.template import loader, Context
from django.conf import settings
from django.contrib.sites.models import Site
from itertools import chain


ATTENDING_CHOICES = (
    ('yes', 'Yes'),
    ('no', 'No'),
    ('maybe', 'Maybe'),
    ('no_rsvp', 'Hasn\'t RSVPed yet')
)


class Event(models.Model):
    title = models.CharField(max_length=255)
    slug = models.SlugField()
    description = models.TextField()
    date_of_event = models.DateTimeField()
    verification_code = models.CharField(max_length=32, blank=True, default='', help_text='Present for future extension/guest verification.')
    email_subject = models.CharField(max_length=255, help_text='The subject line for the e-mail sent out as a reminder to guests.')
    email_message = models.TextField(help_text='The body of the e-mail sent out as a reminder to guests.')
    hosted_by = models.CharField(max_length=255, help_text='The name of the person/organization hosting the event.', blank=True, default='')
    street_address = models.CharField(max_length=255, help_text='The street address where the event is being held.', blank=True, default='')
    city = models.CharField(max_length=64, help_text='The city where the event is being held.', blank=True, default='')
    state = models.CharField(max_length=64, help_text='The state where the event is being held.', blank=True, default='')
    zip_code = models.CharField(max_length=10, help_text='The zip code where the event is being held.', blank=True, default='')
    telephone = models.CharField(max_length=20, blank=True, default='')
    created = models.DateTimeField(default=datetime.datetime.now)
    updated = models.DateTimeField(blank=True, null=True)
    
    def __unicode__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        self.updated = datetime.datetime.now()
        super(Event, self).save(*args, **kwargs)
    
    def get_absolute_url(self):
        return ('rsvp_event_view', [self.slug])
    get_absolute_url = permalink(get_absolute_url)
    
    def guests_attending(self):
        return self.guests.filter(attending_status='yes')
    
    def guests_not_attending(self):
        return self.guests.filter(attending_status='no')
    
    def guests_may_attend(self):
        return self.guests.filter(attending_status='maybe')
    
    def guests_no_rsvp(self):
        return self.guests.filter(attending_status='no_rsvp')

    def is_past(self):
        if datetime.datetime.now(pytz.utc) > self.date_of_event:
            return True
        else:
            return False

    def send_reminder_email(self):
        """
        Sends an email reminding all guests who have selected "Yes" or "Maybe"
        about the upcoming event. Returns a count of the number of guests
        emailed.
        """
        mass_mail_data = []
        from_email = getattr(settings, 'RSVP_FROM_EMAIL', '')

        sending_to = list(chain(self.guests_attending(), self.guests_may_attend()))
        num_sent = 0

        for guest in sending_to:
            t = loader.get_template('rsvp/event_email.txt')
            c = Context({
                'event': self,
                'site': Site.objects.get_current(),
                'guest': guest
            })
            message = t.render(c)
            mass_mail_data.append([self.email_subject, message, from_email, [guest.email]])
            num_sent += 1
        
        send_mass_mail(mass_mail_data, fail_silently=True)
        return num_sent


class Guest(models.Model):
    event = models.ForeignKey(Event, related_name='guests')
    email = models.EmailField(max_length=255, blank=True, default='')
    name = models.CharField(max_length=128, default='')
    attending_status = models.CharField(max_length=32, choices=ATTENDING_CHOICES, default='no_rsvp')
    number_of_guests = models.SmallIntegerField(default=0)
    comment = models.CharField(max_length=255, blank=True, default='')
    created = models.DateTimeField(default=datetime.datetime.now)
    updated = models.DateTimeField(blank=True, null=True)
    
    def __unicode__(self):
        return u"%s - %s (%s)- %s" % (self.event.title, self.name, self.email, self.attending_status)
    
    def save(self, *args, **kwargs):
        self.updated = datetime.datetime.now()
        super(Guest, self).save(*args, **kwargs)
