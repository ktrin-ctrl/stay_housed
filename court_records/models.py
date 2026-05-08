from django.contrib.gis.db import models


class API_Usage(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    called_url = models.URLField()
    records_returned = models.IntegerField()
    status_code = models.CharField(max_length=5)

    class Meta:
        ordering = ['created_at']
        verbose_name = 'API Usage Record'
        verbose_name_plural = 'API Usage Records'
        
    def __str__(self):
        return f'{self.created_at.strftime("%Y-%m-%d %H:%M:%S")} ({self.status_code}), Records: {self.records_returned}'

class Court(models.Model):
    county_fips = models.CharField(blank=True, null=True, max_length=5)
    court_case_prefix = models.CharField(blank=True, null=True, max_length=254)
    court_display_name = models.CharField(blank=True, null=True, max_length=254)
    court_jurisdiction = models.CharField(blank=True, null=True, max_length=254)
    court_type = models.CharField(blank=True, null=True, max_length=254)
    court_time_zone = models.CharField(blank=True, null=True, max_length=254)
    court_consolidated_display_name = models.CharField(blank=True, null=True, max_length=254)
    uri = models.CharField(primary_key=True, max_length=1024)
    json_source = models.JSONField()

    def __str__(self):
        return self.court_display_name

class Address(models.Model):

    address_line1 = models.CharField(blank=True, null=True, max_length=254)
    address_line2 = models.CharField(blank=True, null=True, max_length=254)
    address_city = models.CharField(blank=True, null=True, max_length=254)
    address_state_province_code = models.CharField(blank=True, null=True, max_length=254)
    address_postal_code = models.CharField(blank=True, null=True, max_length=254)

    #pnt_geom = models.PointField(null=True)
    geometry = models.PointField(null=True)
    geocoding_accuracy = models.CharField(blank=True, null=True)
    #uri = models.CharField(primary_key=True, max_length=1024)
    #json_source = models.JSONField(null=True, blank=True)

    def lat(self):
        return self.geometry.x

    def lon(self):
        return self.geometry.y

    class Meta:
        verbose_name_plural = "Addresses"
    
    def __str__(self):
        if self.address_line2 is not None and len(self.address_line2 )>0:
            return f'{self.address_line1}, {self.address_line2}, {self.address_city}, {self.address_state_province_code} {self.address_postal_code}' 
        else:
            return f'{self.address_line1}, {self.address_city}, {self.address_state_province_code} {self.address_postal_code}' 

class Phone(models.Model):

    phone_number = models.CharField(blank=True, null=True, max_length=26)
    phone_type = models.CharField(blank=True, null=True, max_length=50)
    voice_or_fax_code = models.CharField(blank=True, null=True, max_length=50)

    def __str__(self):
        return self.phone_number

class Identifier(models.Model):
    
    identifier_subtype = models.CharField(blank=True, null=True, max_length=254)
    identifier_type = models.CharField(blank=True, null=True, max_length=254)
    identifier_text = models.CharField(blank=True, null=True, max_length=254)

    def __str__(self):
        return f'{self.identifier_type}: {self.identifier_text}'

class Actors(models.Model):

    identifiers = models.ManyToManyField(Identifier)
    addresses = models.ManyToManyField(Address)
    phones = models.ManyToManyField(Phone)

    full_name = models.CharField(blank=True, null=True, max_length=254)
    last_name = models.CharField(blank=True, null=True, max_length=254)
    first_name = models.CharField(blank=True, null=True, max_length=254)
    entity_type = models.CharField(blank=True, null=True, max_length=254)

    date_of_birth = models.DateField(blank=True, null=True)

    actor_uri = models.CharField(primary_key=True, max_length=1024)
    json_source = models.JSONField(null=True, blank=True)


    class Meta:
        verbose_name_plural = "Actors"

    def __str__(self):
        return f'{self.full_name}'

class Relationship(models.Model):
    actor = models.ForeignKey(Actors, on_delete=models.CASCADE, related_name='primary_actor')
    court_case = models.ForeignKey("CourtCase", on_delete=models.CASCADE)
    role = models.CharField(blank=True, null=True, max_length=254)
    assigned_case_role = models.CharField(blank=True, null=True, max_length=50)
    other_actor = models.ForeignKey(Actors, on_delete=models.CASCADE, related_name='other_actor', blank=True, null=True)
    relationship_verb = models.CharField(blank=True, null=True, max_length=50)

    def __str__(self):
        return f'{self.actor}, {self.court_case}'

class Event(models.Model):
    event_hearing_type_desc = models.CharField(blank=True, null=True, max_length=254)
    event_revision_number = models.IntegerField(blank=True, null=True)
    event_duration_minutes = models.CharField(blank=True, null=True, max_length=10)
    event_name = models.CharField(blank=True, null=True, max_length=254)
    event_summary = models.CharField(blank=True, null=True, max_length=1024)
    event_location_name = models.CharField(blank=True, null=True, max_length=254)
    event_room = models.CharField(blank=True, null=True, max_length=254)
    event_type_code = models.CharField(blank=True, null=True, max_length=254)
    event_ical_status = models.CharField(blank=True, null=True, max_length=254)
    event_date_time = models.DateTimeField(blank=True, null=True)
    event_hearing_type_code = models.CharField(blank=True, null=True, max_length=10)

    #event_uri = models.CharField(primary_key=True, max_length=1024)
    json_source = models.JSONField(null=True, blank=True)

    def __str__(self):
        return f'{self.event_hearing_type_desc}: {self.event_date_time}'

class Minutes(models.Model):
    minute_entry_text = models.TextField(blank=True, null=True, max_length=254)
    minute_entry_date = models.DateField(blank=True, null=True, max_length=254)
    minute_hard_copy_entry_page = models.CharField(blank=True, null=True, max_length=254) 
    minute_entry_type_text = models.CharField(blank=True, null=True, max_length=254)
    minute_hard_copy_entry_flag = models.CharField(blank=True, null=True, max_length=254)
    minute_notice_sent_flag = models.CharField(blank=True, null=True, max_length=254)
    minute_hard_copy_entry_date = models.CharField(blank=True, null=True, max_length=254)
    minute_entry_number = models.CharField(blank=True, null=True, max_length=254)
    minute_entry_type_code = models.CharField(blank=True, null=True, max_length=254)
    minute_hard_copy_entry_book = models.CharField(blank=True, null=True, max_length=254)
    minute_order_on_file_flag = models.CharField(blank=True, null=True, max_length=254)
    minute_creation_date_time = models.DateTimeField(blank=True, null=True)
    minute_hard_copy_physical_location = models.CharField(blank=True, null=True, max_length=254)

    #minutes_uri = models.CharField(primary_key=True, max_length=1024)
    json_source = models.JSONField(null=True, blank=True)

    def __str__(self):
        return f'{self.minute_entry_type_text}: {self.minute_entry_type_text[0:20]}'

class CourtPayment(models.Model):

    court_payment_reference_number = models.CharField(blank=True, null=True, max_length=254)
    court_payment_account_description = models.CharField(blank=True, null=True, max_length=254)

    court_payment_account_code = models.CharField(blank=True, null=True, max_length=254)
    court_payment_receipt_number = models.IntegerField(blank=True, null=True)
    court_payment_payment_type = models.CharField(blank=True, null=True, max_length=254)
    court_payment_amount = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    court_payment_date = models.DateField(blank=True, null=True)

    court_payment_case_uri = models.CharField(blank=True, null=True, max_length=1024) 
    court_payment_court_case = models.ForeignKey("CourtCase", on_delete=models.CASCADE, blank=True, null=True)

    court_payment_payor_actor_uri = models.CharField(blank=True, null=True, max_length=1024)
    court_payment_payor_actor = models.ForeignKey("Actors", on_delete=models.CASCADE, related_name='payor', blank=True, null=True)

    court_payment_recipient_actor = models.ForeignKey("Actors", on_delete=models.CASCADE, related_name='recipent', blank=True, null=True)
    court_payment_recipient_actor_uri = models.CharField(blank=True, null=True, max_length=1024)

    #court_payment_uri = models.CharField(primary_key=True, max_length=1024)
    json_source = models.JSONField(null=True, blank=True)

    def __str__(self):
        return f'{self.court_payment_amount} - {self.court_payment_account_description}'

class Charge(models.Model):
    
    charge_state_offense_code = models.CharField(blank=True, null=True, max_length=254)
    charge_state_offense_modifier_code = models.CharField(blank=True, null=True, max_length=254)
    charge_state_degree_code = models.CharField(blank=True, null=True, max_length=254)
    charge_statute_reference = models.CharField(blank=True, null=True, max_length=254)
    charge_local_code = models.CharField(blank=True, null=True, max_length=254)

    charge_convicted_as_code = models.CharField(blank=True, null=True, max_length=254)
    charge_convicted_as_description = models.CharField(blank=True, null=True, max_length=254)
    
    charge_reduced_to_misdemeanor = models.CharField(blank=True, null=True, max_length=254)

    charge_version = models.CharField(blank=True, null=True, max_length=254)

    charge_charge_type = models.CharField(blank=True, null=True, max_length=254)
    charge_charge_class = models.CharField(blank=True, null=True, max_length=254)
    
    charge_driver_speed = models.IntegerField(blank=True, null=True)
    charge_speed_limit = models.IntegerField(blank=True, null=True)

    charge_count = models.CharField(blank=True, null=True, max_length=254)
    charge_text = models.CharField(blank=True, null=True, max_length=10244)
    charge_description = models.CharField(blank=True, null=True, max_length=1024)
    charge_number = models.CharField(blank=True, null=True, max_length=10)

    charge_qualifier = models.CharField(blank=True, null=True, max_length=254)
    charge_appearance_required = models.CharField(blank=True, null=True, max_length=254)
    charge_utt = models.CharField(blank=True, null=True, max_length=254)

    charge_plea_description = models.CharField(blank=True, null=True, max_length=254)
    charge_plea_code = models.CharField(blank=True, null=True, max_length=254)

    charge_date = models.DateField(blank=True, null=True)
    charge_offense_date_time = models.DateTimeField(blank=True, null=True)
    
    case_uri = models.CharField(blank=True, null=True, max_length=1024)
    court_case = models.ForeignKey("CourtCase", on_delete=models.CASCADE, blank=True, null=True)
    
    dispositions_uri = models.CharField(blank=True, null=True, max_length=1024)
    dispositions = models.ManyToManyField("Disposition", related_name="parent_dispositions")

    sentences_uri = models.CharField(blank=True, null=True, max_length=1024)
    sentences = models.ManyToManyField("Sentence", related_name="parent_sentences")
    
    actor_uri = models.CharField(blank=True, null=True, max_length=1024)
    actor = models.ForeignKey(Actors, on_delete=models.CASCADE, blank=True, null=True)


   # uri = models.CharField(primary_key=True, max_length=1024)
    json_source = models.JSONField(null=True, blank=True)

    def __str__(self):
        return f'{self.charge_text} - {self.charge_description}'

class SentenceLength(models.Model):
    sentence_length_time = models.DecimalField(max_digits=6, decimal_places=3, blank=True, null=True)
    sentence_length_unit = models.CharField(blank=False, max_length=10)

    def __str__(self):
        return f'{self.sentence_length_time} {self.sentence_length_unit}'

class Sentence(models.Model):
    sentence_amount = models.CharField(blank=True, null=True, max_length=254)
    sentence_lengths = models.ManyToManyField(SentenceLength)
    sentence_type_code = models.CharField(blank=True, null=True, max_length=254)
    sentence_code = models.CharField(blank=True, null=True, max_length=254)
    sentence_date = models.DateField(blank=True, null=True)
    sentence_number = models.CharField(blank=True, null=True, max_length=254)
    sentence_concurrency_group = models.CharField(blank=True, null=True, max_length=254)
    sentence_description = models.CharField(blank=True, null=True, max_length=254)
    charges_uri = models.CharField(blank=True, null=True, max_length=1024)
    charges = models.ManyToManyField(Charge, related_name="parent_charges")

   # uri = models.CharField(primary_key=True, max_length=1024)
    json_source = models.JSONField(null=True, blank=True)

    def __str__(self):
        return self.sentence_description

class Disposition(models.Model):

    criminal_disposition_desc = models.CharField(blank=True, null=True, max_length=254)
    criminal_disposition_mode = models.CharField(blank=True, null=True, max_length=254)
    criminal_disposition_date = models.DateField(blank=True, null=True)
    criminal_disposition_state_disposition_code = models.CharField(blank=True, null=True, max_length=254)
    criminal_disposition_local_disposition_code = models.CharField(blank=True, null=True, max_length=254)
    criminal_disposition_number = models.IntegerField(blank=True, null=True)
    criminal_disposition_type = models.CharField(blank=True, null=True, max_length=254)

    charge_uri = models.CharField(blank=True, null=True, max_length=1024) 
    charge = models.ForeignKey("Charge", on_delete=models.CASCADE)

    #uri = models.CharField(primary_key=True, max_length=1024)
    json_source = models.JSONField(null=True, blank=True)

    def __str__(self):
        return f'{self.criminal_disposition_desc} - {self.criminal_disposition_date}'

class Receivable(models.Model):
    court_receivable_due_date = models.DateField(blank=True)
    court_receivable_satisfied_date = models.DateField(blank=True)

    court_receivable_date  = models.DateField(blank=True)
    court_receivable_last_payment_date  = models.DateField(blank=True)

    court_receivable_portion = models.CharField(blank=True, null=True, max_length=254)

    court_receivable_account_code = models.CharField(blank=True, null=True, max_length=254)

    court_receivable_amount = models.DecimalField(max_digits=10,decimal_places=2, blank=True, null=True)
    court_receivable_balance = models.DecimalField(max_digits=10,decimal_places=2, blank=True, null=True)

    court_receivable_hold_action = models.CharField(blank=True, null=True, max_length=254)
    court_receivable_account_desc = models.CharField(blank=True, null=True, max_length=254)

    court_case = models.ForeignKey("CourtCase", on_delete=models.CASCADE, related_name="parent_court_case", blank=True, null=True)
    case_uri = models.CharField(blank=True, null=True, max_length=1024)

    recipient_actor = models.ForeignKey(Actors, on_delete=models.CASCADE, related_name="recipient_actors", blank=True, null=True)
    recipient_actor_uri = models.CharField(blank=True, null=True, max_length=1024)

    payor_actor = models.ForeignKey(Actors, on_delete=models.CASCADE, related_name="payor_actors", blank=True, null=True)
    payor_actor_uri = models.CharField(blank=True, null=True, max_length=1024)

  #  uri = models.CharField(primary_key=True, max_length=1024)
    json_source = models.JSONField(null=True, blank=True)

    def __str__(self):
        return f'{self.court_receivable_account_desc}: {self.court_receivable_amount} of {self.court_receivable_balance}' 

class CourtCase(models.Model):
    
    filed_date = models.DateField(blank=True, null=True)
    reopen_date = models.DateField(null=True, blank=True)
    disposition_date = models.DateField(null=True, blank=True)

    case_number = models.CharField(blank=True, null=True, max_length=254)
    case_caption = models.CharField(blank=True, null=True, max_length=254)

    local_type_code = models.CharField(blank=True, null=True, max_length=254)
    local_subtype_code = models.CharField(null=True, blank=True, max_length=254)
    global_type_code = models.CharField(blank=True, null=True, max_length=254)
    
    local_disposition_code = models.CharField(null=True, blank=True, max_length=254)
    global_disposition_code = models.CharField(blank=True, null=True, max_length=254)
    local_status_code = models.CharField(blank=True, null=True, max_length=254)

    is_marked_expunged = models.BooleanField(blank=True, null=True)
    as_of_timestamp = models.DateTimeField(blank=True, null=True)

    court = models.ForeignKey(Court, on_delete=models.CASCADE, null=True, blank=True)
    court_uri = models.CharField(blank=True, null=True, max_length=1024)

    actors = models.ManyToManyField(Actors, through=Relationship, through_fields=('court_case', 'actor',))
    actors_uri = models.CharField(blank=True, null=True, max_length=1024)

    events = models.ManyToManyField(Event)
    events_uri = models.CharField(blank=True, null=True, max_length=1024)
    
    minutes = models.ManyToManyField(Minutes)
    minutes_uri = models.CharField(blank=True, null=True, max_length=1024)
    
    charges = models.ManyToManyField(Charge)
    charges_uri = models.CharField(blank=True, null=True, max_length=1024)

    dispositions = models.ManyToManyField(Disposition)
    dispositions_uri = models.CharField(blank=True, null=True, max_length=1024)

    sentences = models.ManyToManyField(Sentence)
    sentences_uri = models.CharField(blank=True, null=True, max_length=1024)

    payments = models.ManyToManyField(CourtPayment)
    payments_uri = models.CharField(blank=True, null=True, max_length=1024)

    receivables = models.ManyToManyField(Receivable)
    receivables_uri = models.CharField(blank=True, null=True, max_length=1024)

    uri = models.CharField(primary_key=True, max_length=1024)
    json_source = models.JSONField()

    @property
    def subject_property(self):
        return Address.objects.filter(actors__primary_actor__court_case=self).filter(actors__primary_actor__assigned_case_role='Defendant').order_by('id').first()

    subject_prop_hardcode = models.ForeignKey(Address, blank=True, null=True, on_delete=models.SET_NULL)
    subject_prop_address = models.CharField(max_length=254, blank=True, null=True)
    subject_prop_location = models.PointField(null=True)
    subject_prop_location_lat = models.FloatField(blank=True, null=True)
    subject_prop_location_lon = models.FloatField(blank=True, null=True)

    @property
    def defendants(self):
        return Actors.objects.filter(primary_actor__court_case=self).filter(primary_actor__assigned_case_role='Defendant')

    @property
    def plaintiffs(self):
        return Actors.objects.filter(primary_actor__court_case=self).filter(primary_actor__assigned_case_role='Plaintiff')


    def save(self, *args, **kwargs):
        if self.subject_property is not None and self.subject_property.geometry is not None and self.subject_prop_location_lat is None:
            self.subject_prop_hardcode = self.subject_property
            self.subject_prop_location_lat  = self.subject_property.geometry.y
            self.subject_prop_location_lon  = self.subject_property.geometry.x
            self.subject_prop_location = self.subject_property.geometry
            self.subject_prop_address = self.subject_property.__str__()

        super().save(*args, **kwargs)


    def __str__(self):
        return f'{self.case_caption}'




class Mailing(models.Model):
    # type of mailing
    # confirmation number
    # date ordered
    # date sent
    # case - person - address
    pass