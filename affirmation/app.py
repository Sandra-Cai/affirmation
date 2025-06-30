from flask import Flask, render_template, request, redirect, url_for, flash
import random
import os
from twilio.rest import Client
from apscheduler.schedulers.background import BackgroundScheduler
import pytz

app = Flask(__name__)
app.secret_key = 'supersecretkey'  # Needed for flash messages

# Twilio config (replace with your actual credentials)
TWILIO_ACCOUNT_SID = os.environ.get('TWILIO_ACCOUNT_SID', 'your_account_sid')
TWILIO_AUTH_TOKEN = os.environ.get('TWILIO_AUTH_TOKEN', 'your_auth_token')
TWILIO_PHONE_NUMBER = os.environ.get('TWILIO_PHONE_NUMBER', '+1234567890')

TIMEZONE = os.environ.get('TIMEZONE', 'US/Eastern')

affirmations = [
    "You are capable of amazing things!",
    "Believe in yourself and all that you are.",
    "You are stronger than you think.",
    "Every day is a new opportunity to grow.",
    "Your potential is limitless.",
    "You are worthy of all the good things in life.",
    "Keep going, you are doing great!",
    "You have the power to create change."
]

SUBSCRIBERS_FILE = 'subscribers.txt'

def send_sms(to, message):
    client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
    client.messages.create(
        body=message,
        from_=TWILIO_PHONE_NUMBER,
        to=to
    )

@app.route('/', methods=['GET'])
def home():
    affirmation = random.choice(affirmations)
    return render_template('index.html', affirmation=affirmation)

@app.route('/subscribe', methods=['POST'])
def subscribe():
    phone = request.form.get('phone')
    if phone:
        # Save phone number if not already subscribed
        if not os.path.exists(SUBSCRIBERS_FILE):
            with open(SUBSCRIBERS_FILE, 'w') as f:
                pass
        with open(SUBSCRIBERS_FILE, 'r+') as f:
            numbers = set(line.strip() for line in f if line.strip())
            if phone not in numbers:
                f.write(phone + '\n')
                flash('Subscribed successfully! You will receive daily affirmations by text.')
            else:
                flash('You are already subscribed!')
    else:
        flash('Please enter a valid phone number.')
    return redirect(url_for('home'))

# Placeholder for daily job (e.g., use cron or APScheduler)
def send_daily_affirmations():
    if not os.path.exists(SUBSCRIBERS_FILE):
        return
    with open(SUBSCRIBERS_FILE, 'r') as f:
        numbers = [line.strip() for line in f if line.strip()]
    affirmation = random.choice(affirmations)
    for number in numbers:
        send_sms(number, affirmation)

if __name__ == '__main__':
    scheduler = BackgroundScheduler(timezone=pytz.timezone(TIMEZONE))
    scheduler.add_job(send_daily_affirmations, 'cron', hour=9, minute=0)  # Sends at 9:00 AM every day
    scheduler.start()
    try:
        app.run(debug=True)
    except (KeyboardInterrupt, SystemExit):
        scheduler.shutdown() 