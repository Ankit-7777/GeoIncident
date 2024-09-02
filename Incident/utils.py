from django.core.mail import EmailMessage
import os
import requests
from django.conf import settings



class Utils:
    @staticmethod
    def send_email(data):
        email = EmailMessage(
            subject=data['email_subject'],
            body=data['body'],
            from_email=os.getenv('EMAIL_FROM'),
            to=[data['to_email']]
        )
        email.send()


def get_location_data(pincode):
    try:
        api_key = 'vtmpacLwwN4y0SUBwIXXFIgf9mQk5Kglvw7fX7eewlA' 
        response = requests.get(f'https://geocode.search.hereapi.com/v1/geocode?q={pincode}&apiKey={api_key}')
        response.raise_for_status() 
        data = response.json()

        items = data.get('items', [])
        if items:
            location = items[0]
            address = location.get('address', {})
            return {
                'city': address.get('city', 'N/A'),
                'state': address.get('state', 'N/A'),
                'country': address.get('countryName', 'N/A'),
                'address': address.get('label', 'N/A')
            }
        return {}
    except requests.RequestException as e:
        print(f"Error fetching location data: {e}")
        return {}

