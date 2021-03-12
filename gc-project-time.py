from __future__ import print_function
import httplib2
import os

import googleapiclient.discovery as discovery
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage

import datetime

try:
    import argparse
    flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
    flags = None

# If modifying these scopes, delete your previously saved credentials
# at ~/.credentials/calendar-python-quickstart.json
SCOPES = 'https://www.googleapis.com/auth/calendar.readonly'
CLIENT_SECRET_FILE = 'credentials.json'
APPLICATION_NAME = 'Python Project time'


def get_credentials():
    """Gets valid user credentials from storage.
    If nothing has been stored, or if the stored credentials are invalid,
    the OAuth2 flow is completed to obtain the new credentials.

    Returns:
        Credentials, the obtained credential.
    """
    credential_dir = os.path.join(os.path.expanduser('~'))
    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)
    credential_path = os.path.join(credential_dir, 'credentials.json')

    store = Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
        flow.user_agent = APPLICATION_NAME
        if flags:
            credentials = tools.run_flow(flow, store, flags)
        else: # Needed only for compatibility with Python 2.6
            credentials = tools.run(flow, store)
        print('Storing credentials to ' + credential_path)
    return credentials

def main():
    """Shows basic usage of the Google Calendar API.
    Creates a Google Calendar API service object and outputs a list of the next
    10 events on the user's calendar.
    """
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    service = discovery.build('calendar', 'v3', http=http)

    # This code is to fetch the calendar ids shared with me
    # Src: https://developers.google.com/google-apps/calendar/v3/reference/calendarList/list
    page_token = None
    calendar_ids = []
    while True:
        calendar_list = service.calendarList().list(pageToken=page_token).execute()
        for calendar_list_entry in calendar_list['items']:
            if 'nikolajjsj@gmail.com' in calendar_list_entry['id']:
                calendar_ids.append(calendar_list_entry['id'])
        page_token = calendar_list.get('nextPageToken')
        if not page_token:
            break

    # This code is to look for all-day events in each calendar for the month of September
    # Src: https://developers.google.com/google-apps/calendar/v3/reference/events/list
    start_date = datetime.datetime(
        2021, 2, 1, 00, 00, 00, 0).isoformat() + 'Z'
    end_date = datetime.datetime.now().isoformat() + 'Z'

    for calendar_id in calendar_ids:
        count = 0
        total_time = 0
        print('\n----%s:\n' % calendar_id)
        eventsResult = service.events().list(
            calendarId=calendar_id,
            timeMin=start_date,
            timeMax=end_date,
            singleEvents=True).execute()
        events = eventsResult.get('items', [])
        if not events:
            print('No upcoming events found.')
        for event in events:
            if 'summary' in event:
                if 'Python Projekt' in event['summary']:
                    count += 1
                    start = event['start'].get(
                        'dateTime', event['start'].get('date')).replace('T','').split('+')[0]
                    end = event['end'].get(
                        'dateTime', event['end'].get('date')).replace('T','').split('+')[0]
                    date_time_start = datetime.datetime.strptime(start, '%Y-%m-%d%H:%M:%S')
                    date_time_end = datetime.datetime.strptime(end, '%Y-%m-%d%H:%M:%S')
                    total_time += int(str(date_time_end-date_time_start).split(':')[0])
        print('Total days off is %d' % (count))
        print('Total time used on project is %d' % (total_time))

if __name__ == '__main__':
    main()
