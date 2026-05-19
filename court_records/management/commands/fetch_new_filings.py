from django.core.management.base import BaseCommand, CommandError
from django.utils.timezone import localdate, now
from datetime import timedelta
import requests
import os
import json
from django.apps import apps
import re


from requests.adapters import HTTPAdapter, Retry
from . import geocode #import geocode_street_address

from court_records.models import CourtCase, Court, Address, Phone, Identifier, Actors, Relationship, Event, Minutes, CourtPayment, Charge, SentenceLength, Sentence, Disposition, Receivable, Mailing, API_Usage

BASE_URL = os.environ.get('DOXPOP_URL', 'https://demo-api.doxpop.com/')
USERNAME = os.environ.get('DOXPOP_USER', 'demo')
PASSWORD = os.environ.get('DOXPOP_PASS', 'demo')            



def fetch_courts(s, county_fips):

    resp = s.get(BASE_URL+f'courts.json?county_fips={county_fips}', auth=(USERNAME, PASSWORD) )
    if resp.status_code == 200 and len(resp.text)>10:
        courts_json = resp.json()
        for court in courts_json:
            c = Court.objects.create(
                county_fips = court.get('county_fips'),
                court_case_prefix = court.get('court_case_prefix'),
                court_display_name = court.get('court_display_name'),
                court_jurisdiction = court.get('court_jurisdiction'),
                court_type = court.get('court_type'),
                court_time_zone = court.get('court_time_zone'),
                uri  = court.get('court_uri'),
                json_source = json.dumps(court),
            )
            if 'Superior Court' in court.get('court_display_name'):
                c.court_consolidated_display_name =  re.sub(r'\d+', '', court.get('court_display_name')).strip()
            c.save()

# This is used for Events, Minutes, CourtPayment, Charge, Disposition, Receivable
DETAIL_TYPES = [
    ['Event', 'events', 'events_uri'], 
    ['Minutes', 'minutes', 'minutes_uri'], 
  #  ['CourtPayment', 'payments', 'payments_uri'], 
   # ['Charge', 'charges', 'charges_uri'],
   # ['Disposition', 'dispositions', 'dispositions_uri'],
   # ['Receivable', 'receivables', 'receivables_uri'],
]
def fetch_details(s, model_name, uri, case_uri):
    model_obj = apps.get_model('court_records', model_name)
    print(f'Fetching {uri}')
    resp = s.get(BASE_URL+uri+'.json', auth=(USERNAME, PASSWORD) )   
   # print(f'Response: {resp.status_code}: {resp.text}')
    if resp.status_code == 200 and len(resp.text)>10:
        resp_json = resp.json()
        objects = []
        for record in resp_json:
            record.update({'json_source': json.dumps(record)})
            obj = model_obj.objects.create(**record)
            objects.append(obj)
        return objects
    else:
        print(f'Error: {resp.status_code}: {resp.text}')
        return


def fetch_actor(s, uri):
        if uri is None:
            return None
        resp = s.get(BASE_URL+uri+'.json', auth=(USERNAME, PASSWORD) )
        resp_json = resp.json()
        obj, created = Actors.objects.update_or_create(**{'actor_uri':uri }, defaults=resp_json[0])
        return obj 


def fetch_actors(s, uri, case_uri):
    resp = s.get(BASE_URL+uri+'.json', auth=(USERNAME, PASSWORD) )
    if resp.status_code == 200 and len(resp.text)>10:
        resp_json = resp.json()
        for a in resp_json:
            print(a)
            defaults = {
                'full_name': a['actor']['actor_full_name'],
                'last_name': a['actor']['actor_person_last_name'],
                'first_name': a['actor']['actor_person_first_name'],
                'date_of_birth': a['actor']['actor_person_date_of_birth'],
                'entity_type': a['actor']['actor_entity_type'],
                'json_source' : json.dumps(a),

            }
            obj, created = Actors.objects.update_or_create(**{'actor_uri':a['actor']['actor_uri'] }, defaults=defaults)
            for address in a['actor']['addresses']:

                address_object = Address.objects.filter(
                    address_line1 = address.get('address_line1'),
                    address_line2 = address.get('address_line2'),
                    address_city = address.get('address_city'),
                    address_state_province_code = address.get('address_state_province_code'),
                    address_postal_code = address.get('address_postal_code'),
                ).first()
                if address_object is None:
                    address_object = Address.objects.create(
                        address_line1 = address.get('address_line1'),
                        address_line2 = address.get('address_line2'),
                        address_city = address.get('address_city'),
                        address_state_province_code = address.get('address_state_province_code'),
                        address_postal_code = address.get('address_postal_code'),
                    )
                if address_object.geometry is None:
                    address_to_locate = address_object.__str__()
                    location = geocode.geocode_street_address(address_to_locate)
                    if location['Geocoding Accuracy'] in ['rooftop', 'parcel', 'point', 'interpolated']:
                        address_object.geometry = location['PNT_WKT']
                    address_object.geocoding_accuracy = location['Geocoding Accuracy']
                    address_object.save()
                obj.addresses.add(address_object)    

            for phone in a['actor']['phones']:
                phone_object = Phone.objects.filter(
                    phone_number = phone['phone_number'],
                    phone_type = phone['phone_type'],
                    voice_or_fax_code = phone['voice_or_fax_code']
                ).first()
                if phone_object is None:
                    phone_object = Phone.objects.create(
                        phone_number = phone['phone_number'],
                        phone_type = phone['phone_type'],
                        voice_or_fax_code = phone['voice_or_fax_code']
                    )
                obj.phones.add(phone_object)

            for identifier in a['actor']['actor_identifiers']:
                identifier_object = Identifier.objects.filter(
                    identifier_subtype = identifier['actor_identifier_subtype'],
                    identifier_type = identifier['actor_identifier_type'],
                    identifier_text = identifier['actor_identifier_text'],
                ).first()

                if identifier_object is None:
                    identifier_object = Identifier.objects.create(
                    identifier_subtype = identifier['actor_identifier_subtype'],
                    identifier_type = identifier['actor_identifier_type'],
                    identifier_text = identifier['actor_identifier_text'],
                )

                obj.identifiers.add(identifier_object)

            other_actor = None
            relationship_verb = None
            try:
                other_actor_uri = a['relationships'][0]['other_actor_uri']
                other_actor = Actors.objects.filter(actor_uri=other_actor_uri).first()
                relationship_verb = a['relationships'][0]['relationship_verb']
            except:
                pass 
            finally:
                relationship = Relationship.objects.get_or_create(
                    actor=obj,
                    court_case=CourtCase.objects.get(uri=case_uri),
                    assigned_case_role=a['assigned_case_role'],
                    other_actor=other_actor,
                    relationship_verb=relationship_verb,
                )
                print(relationship)


def fetch_case_updates(s):
    open_cases = CourtCase.objects.exclude(local_status_code='Decided').exclude(filed_date__gte=localdate(now()-timedelta(days=2)))
    for new_case in open_cases:
        fetch_actors(s, new_case.actors_uri, new_case.uri)

        for model, field, uri_field in DETAIL_TYPES:
            print(f'Fetching {model}')
            uri_value = getattr(new_case, uri_field)
            obj_field = getattr(new_case, field)
            if uri_value is not None:
                objects = fetch_details(s, model, uri_value, new_case.uri)
                if objects is not None:
                    for x in objects:
                        obj_field.add(x)
                        new_case.save()
                    

class Command(BaseCommand):
    help = "Download new court cases from DoxPop"
         

    def add_arguments(self, parser):
        try:
            last_case_filed = CourtCase.objects.all().order_by('-filed_date').first().filed_date
            start_date_str = (last_case_filed+timedelta(days=1)).strftime('%Y-%m-%d')
        except:
            start_date_str = localdate(now()-timedelta(days=1)).strftime('%Y-%m-%d')
        parser.add_argument("--start_date", dest='start_date', default=start_date_str)
        parser.add_argument("--end_date", dest='end_date', default=localdate().strftime('%Y-%m-%d'))
        parser.add_argument("--fetch_courts", help="Retreive court data by FIPS county code")
        parser.add_argument("--fetch_details", help="Retreive case details by URI")
        parser.add_argument("--fetch_updates", help="Retreive minutes, events, actors on open cases.")


    def handle(self, *args, **options):


        FILINGS_QUERY = "cases.json?case_local_type_code=EV&county_fips=18097"
        DATES_FILED = f'&case_filed_date={options['start_date']},{options['end_date']}'

        offset = 0
        limit = 200
        cases_processed = 0

        s = requests.Session()
        retries = Retry(total=5, backoff_factor=1, status_forcelist=[ 502, 503, 504 ])
        s.mount('https://', HTTPAdapter(max_retries=retries))


        if options['fetch_courts']:
            fetch_courts(s, options['fetch_courts'])
            return

        if options['fetch_details']:
            fetch_details(s, options['fetch_details'], '/case/1819041063441')
            return

        if options['fetch_updates']:
            fetch_case_updates(s)
            return

        while True:
            
            LIMITS = f'&offset={offset}&limit={limit}&order_by=case_filed_date:asc'
            self.stdout.write(BASE_URL+FILINGS_QUERY+DATES_FILED+LIMITS)
            resp = s.get(BASE_URL+FILINGS_QUERY+DATES_FILED+LIMITS, auth=(USERNAME, PASSWORD) )
            record_api = API_Usage.objects.create(
                called_url=resp.request.url, 
                records_returned=len(resp.json()) or 0, 
                status_code=resp.status_code,
            )
            if resp.status_code == 200 and len(resp.text)>10:
                cases_json = resp.json()
                cases_processed = len(cases_json)
                for c in cases_json:
                    print(c)
                    new_case, created = CourtCase.objects.update_or_create(
                        uri=c.get('case_uri'),
                        defaults={
                            'case_number' : c.get('case_number'),
                            'case_caption' : c.get('case_caption'),
                            'filed_date' : c.get('case_filed_date'),
                            'reopen_date' : c.get('case_reopen_date'),
                            'disposition_date' : c.get('case_disposition_date'),
                            'local_disposition_code' : c.get('case_local_disposition_code', ''),
                            'local_type_code' : c.get('case_local_type_code', ''),
                            'local_subtype_code' : c.get('case_local_subtype_code',''),
                            'local_status_code' : c.get('case_local_status_code', ''),
                            'is_marked_expunged' : c.get('case_is_marked_expunged'),
                            'as_of_timestamp' : c.get('as_of_timestamp'),
                            'court_uri' : c.get('court_uri'),
                            'payments_uri' : c.get('court_payments_uri'),
                            'charges_uri' : c.get('charges_uri'),
                            'dispositions_uri' : c.get('dispositions_uri'),
                            'events_uri' : c.get('events_uri'),
                            'sentences_uri' : c.get('sentences_uri'),
                            'minutes_uri' : c.get('minutes_uri'),
                            'actors_uri' : c.get('case_actors_uri'),
                            'receivables_uri' : c.get('court_receivables_uri'),
                            'json_source' : json.dumps(c),
                        }
                    )

                    new_case.court = Court.objects.get(uri=c.get('court_uri'))
                    new_case.save()

                    print('Fetching actors')
                    fetch_actors(s, new_case.actors_uri, new_case.uri)

                    for model, field, uri_field in DETAIL_TYPES:
                        print(f'Fetching {model}')
                        uri_value = getattr(new_case, uri_field)
                        obj_field = getattr(new_case, field)
                        if uri_value is not None:
                            objects = fetch_details(s, model, uri_value, new_case.uri)
                            if objects is not None:
                                for x in objects:
                                    obj_field.add(x)
                                    new_case.save()
                                
                if cases_processed < 200:
                    break
            else:
                print(f'No additional filings fetched: {resp.status_code}, {resp.text}')
                #print(resp.text)
                break
            offset += limit

       # fetch_case_updates(s)

        self.stdout.write(
            self.style.SUCCESS('Successfully downloaded new cases') 
        )
