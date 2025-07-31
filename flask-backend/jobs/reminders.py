import datetime
from flask import current_app
from celery import shared_task
from models import db, User, Reservation, ParkingLot
from mailer import send_email
import requests

@shared_task(ignore_results = False, name = "generate_msg")
def generate_msg(username, prime_location_name):
    text = f"Hi {username}, A new Parkin lot is Created in location = {prime_location_name}. If you want to book  Please check the app at http://127.0.0.1:5173"
    response = requests.post("https://chat.googleapis.com/v1/spaces/AAQATbkFpEk/messages?key=AIzaSyDdI0hCZtE6vySjMm-WEfRq3CPzqKqqsHI&token=ucraHObyF0iu86BspFuxp-POY9ODEXmDgJuuD1lu0Lo", json = {"text": text})
    print(response.status_code)
    return "The delivery is sent to user"