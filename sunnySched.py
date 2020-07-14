from __future__ import print_function
import datetime
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

from datetime import datetime, date, time, timedelta
import config
from google.oauth2 import service_account

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/calendar', 'https://www.googleapis.com/auth/calendar.events']

def getTodaysScheduleEntry(userSchedule):
    today = datetime.today().weekday()
    for scheduleEntry in userSchedule:
        if scheduleEntry["day"] == today:
            return scheduleEntry
    return {}

def generateEventName(userObject):
    event_name = '{}, {}, {}'.format(userObject["name"], userObject["phone_number"], userObject["watercraft"])
    return event_name

def main():
    """Shows basic usage of the Google Calendar API.
    Prints the start and name of the next 10 events on the user's calendar.
    """
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('calendar', 'v3', credentials=creds)
    # BOILER PLATE END

    for user in config.USER_LIST:
        scheduleEntry = getTodaysScheduleEntry(user["schedule"])
        if bool(scheduleEntry):
            start_time = (datetime.today() + timedelta(days=7)).replace(hour=scheduleEntry["start_time_hour"], minute=scheduleEntry["start_time_minute"], second=0, microsecond=0)
            end_time = start_time + timedelta(hours=1)

            event_payload = {
                'summary': generateEventName(user),
                'start': {
                    'dateTime': start_time.strftime("%Y-%m-%dT%H:%M:%S"),
                    'timeZone': 'America/Toronto',
                },
                'end': {
                    'dateTime': end_time.strftime("%Y-%m-%dT%H:%M:%S"),
                    'timeZone': 'America/Toronto',
                }
            }

            # service.events().insert(calendarId=config.TEST_CALENDAR_ID, body=event_payload).execute()
            service.events().insert(calendarId=config.GROUP_CALENDAR_ID, body=event_payload).execute()
            service.events().insert(calendarId=config.SUNNYSIDE_CALENDAR_ID, body=event_payload).execute()
            print('Event created: \n{} \ntoday @ {}'.format(event_payload, datetime.now().strftime("%Y-%m-%dT%H:%M:%S")))

if __name__ == '__main__':
    main()
