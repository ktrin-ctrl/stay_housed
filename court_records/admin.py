from django.contrib.gis import admin
from django.contrib.gis.forms.widgets import OpenLayersWidget
from django.utils.translation import ngettext
from django.contrib import messages
from django.contrib.gis.db import models

from court_records.models import CourtCase, Court, Address, Phone, Identifier, Actors, Relationship, Event, Minutes, CourtPayment, Charge, SentenceLength, Sentence, Disposition, Receivable, Mailing, API_Usage

from .management.commands import geocode #import geocode_street_address

class API_UsageAdmin(admin.ModelAdmin):
    readonly_fields = ['created_at', 'called_url', 'records_returned', 'status_code']

class AddressAdmin(admin.GISModelAdmin):

    @admin.action(description="Re-try geocoding location")
    def retry_geocode(self, request, queryset):
        updated_count = 0
        total_count = queryset.count()
        for addy in queryset:
            address_to_locate = addy.__str__()
            location = geocode.geocode_street_address(address_to_locate)
            print(address_to_locate, location)
            try: 
                geocode_accuracy = location['Geocoding Accuracy']
            except:
                if addy.address_line2 is not None:
                    address_to_locate = f'{addy.address_line2}, {addy.address_city}, {addy.address_state_province_code} {addy.address_postal_code}'
                    location = geocode.geocode_street_address(address_to_locate)
                    print(f'Second attempt: {address_to_locate}, {location}')
                    geocode_accuracy = location['Geocoding Accuracy']
            else: 
                if geocode_accuracy in ['rooftop', 'parcel', 'point', 'interpolated']:
                    addy.geometry = location['PNT_WKT']
                    updated_count += 1
                addy.geocoding_accuracy = location['Geocoding Accuracy']
                addy.save()
                    
                #break
        self.message_user(
            request,
            ngettext(
                "%(count)d out of %(total)d address was successfully geocoded.",
                "%(count)d out of %(total)d addresses were successfully geocoded.",
                updated_count,
            )
            % {'count': updated_count, 'total': total_count},
            messages.SUCCESS,
        )
    formfield_overrides = {
        models.PointField: {"widget": OpenLayersWidget},
    }
    actions = [retry_geocode]
    #readonly_fields = ['geometry',]

class CourtCaseAdmin(admin.ModelAdmin):
    list_display = ('case_number', 'case_caption', 'filed_date', 'subject_property')
    #readonly_fields = ('')
    readonly_fields = ('subject_prop_address', 'subject_prop_location', 'subject_prop_location_lat', 'subject_prop_location_lon', 'subject_property', 'defendants', 'plaintiffs', 'actors', 'events', 'minutes', 'charges', 'sentences', 'payments', 'receivables', 'dispositions')
    #excluded = ['']
    list_filter = ['court', 'filed_date', 'local_status_code', 'is_marked_expunged']
    search_fields = ["subject_prop_hardcode__address_line1","subject_prop_hardcode__address_line2", "subject_prop_hardcode__address_postal_code",  "subject_prop_hardcode__address_city", "actors__full_name", "case_number", "case_caption"]


admin.site.register(CourtCase, CourtCaseAdmin)
admin.site.register(Court)
admin.site.register(Address, AddressAdmin)
admin.site.register(Phone)
admin.site.register(Identifier)
admin.site.register(Actors)
admin.site.register(Relationship)
admin.site.register(Event)
admin.site.register(Minutes)
admin.site.register(API_Usage, API_UsageAdmin)
admin.site.register(CourtPayment)
admin.site.register(Charge)
admin.site.register(SentenceLength)
admin.site.register(Sentence)
admin.site.register(Disposition)
admin.site.register(Receivable)
admin.site.register(Mailing)
