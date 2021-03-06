from django import forms
from django.core.exceptions import ObjectDoesNotExist
from rsvp.models import ATTENDING_CHOICES, Guest, Event


VISIBLE_ATTENDING_CHOICES = [choice for choice in ATTENDING_CHOICES if choice[0] != 'no_rsvp']


class RSVPForm(forms.Form):
    attending = forms.ChoiceField(choices=VISIBLE_ATTENDING_CHOICES, initial='yes', widget=forms.RadioSelect)
    name = forms.CharField(max_length=128)
    email = forms.EmailField()
    number_of_guests = forms.IntegerField(initial=0)
    comment = forms.CharField(max_length=255, required=False, widget=forms.Textarea)
    
    def __init__(self, *args, **kwargs):
        if 'guest_class' in kwargs:
            self.guest_class = kwargs['guest_class']
            del(kwargs['guest_class'])
        else:
            self.guest_class = Guest

        if 'event_class' in kwargs:
            self.event_class = kwargs['event_class']
            del(kwargs['event_class'])
        else:
            self.event_class = Event

        if 'event' in kwargs:
            self.event = kwargs['event']
            del(kwargs['event'])

        super(RSVPForm, self).__init__(*args, **kwargs)
    
    # def clean_email(self):
    #     try:
    #         guest = self.guest_class._default_manager.get(email=self.cleaned_data['email'])
    #     except ObjectDoesNotExist:
    #         d = self.cleaned_data
            
    #         # raise forms.ValidationError, 'That e-mail is not on the guest list.'
        
    #     if hasattr(guest, 'attending_status') and guest.attending_status != 'no_rsvp':
    #         raise forms.ValidationError, 'You have already provided RSVP information.'
        
    #     return self.cleaned_data['email']
    
    def clean_number_of_guests(self):
        if self.cleaned_data['number_of_guests'] < 0:
            raise forms.ValidationError, "The number of guests you're bringing can not be negative."
        return self.cleaned_data['number_of_guests']
        
    def save(self):
        try:
            guest = self.guest_class._default_manager.get(email=self.cleaned_data['email'])
        except ObjectDoesNotExist:
            guest = self.guest_class._default_manager.create(email=self.cleaned_data['email'], event=self.event)
        
        if self.cleaned_data['name']:
            guest.name = self.cleaned_data['name']
        
        guest.attending_status = self.cleaned_data['attending']
        guest.number_of_guests = self.cleaned_data['number_of_guests']
        guest.comment = self.cleaned_data['comment']
        guest.save()
        return guest
