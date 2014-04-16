from django.contrib import admin
from django.contrib.admin.models import LogEntry, ADDITION, CHANGE
from django.contrib.contenttypes.models import ContentType
from rsvp.models import Event, Guest


class GuestInline(admin.TabularInline):
    model = Guest
    extra = 0
    fields = ('name', 'email', 'attending_status', 'number_of_guests')


class EventAdmin(admin.ModelAdmin):
    date_hiearchy = 'date_of_event'
    fieldsets = (
        (None, {
            'fields': ('title', 'slug', 'description', 'date_of_event'),
        }),
        ('Reminder Email', {
            'fields': ('email_subject', 'email_message'),
        }),
        ('Event Details', {
            'fields': ('hosted_by', 'street_address', 'city', 'state', 'zip_code', 'telephone'),
            'classes': ('collapse',)
        })
    )
    inlines = [GuestInline]
    list_display = ('title', 'date_of_event')
    prepopulated_fields = {'slug': ('title',)}
    search_fields = ('title', 'description', 'hosted_by')
    
    def send_reminder_email(modeladmin, request, queryset):
        for event in queryset:
            num_sent = event.send_reminder_email()

            LogEntry.objects.log_action(
                user_id         = request.user.pk, 
                content_type_id = ContentType.objects.get_for_model(event).pk,
                object_id       = event.pk,
                object_repr     = event.__unicode__(),
                change_message  = "Sent reminder emails to %d guests." % num_sent,
                action_flag     = CHANGE
            )
    
    send_reminder_email.short_description = 'Send reminders to guests who are or might be coming'
    actions = [send_reminder_email]


class GuestAdmin(admin.ModelAdmin):
    fields = ('name', 'email', 'event', 'attending_status', 'number_of_guests', 'comment')
    list_display = ('event', 'email', 'name', 'attending_status', 'number_of_guests')
    list_filter = ('attending_status','event')
    search_fields = ('email', 'name')


admin.site.register(Event, EventAdmin)
admin.site.register(Guest, GuestAdmin)
