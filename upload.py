#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Upload videos to youtube

Usage example:
  $ python upload.py

"""

import os

import google_auth_oauthlib.flow
import googleapiclient.discovery
import googleapiclient.errors

from googleapiclient.http import MediaFileUpload

from sqlite import *
import re

COMPILATION_FOLDER = 'compilations'

scopes = ['https://www.googleapis.com/auth/youtube.upload']

def upload(file,number):
    # Disable OAuthlib's HTTPS verification when running locally.
    # *DO NOT* leave this option enabled in production.
    os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

    api_service_name = 'youtube'
    api_version = 'v3'
    client_secrets_file = 'client_secrets.json'

    # Get credentials and create an API client
    flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(
        client_secrets_file, scopes)
    credentials = flow.run_console()
    youtube = googleapiclient.discovery.build(
        api_service_name, api_version, credentials=credentials)

    '''
    # Video options
        options = {
            title : 'Example title',
            description : 'Example description',
            tags : ['tag1', 'tag2', 'tag3'],
            categoryId : '22',
            privacyStatus : 'private',
            kids : False
            thumbnailLink : 'https://cdn.havecamerawilltravel.com/photographer/files/2020/01/youtube-logo-new-1068x510.jpg'
        }
    '''


    options = {}
    body = {
        'snippet': {
            'title': 'lol WUT #{}'.format(number),
            'description': 'Compilation of funny and weird videos',
            'tags': 'funny,wtf,compilation',
            'categoryId': '24'
        },
        'status': {
            'privacyStatus': 'public',
            'selfDeclaredMadeForKids': False
        }
    }            
    

    request = youtube.videos().insert(
        part=",".join(list(body.keys())),
        body=body,
        media_body=MediaFileUpload(file)
    )
    response = request.execute()

    print(response)

if __name__ == "__main__":
    # get compilations from DB
    sql = Sqlite()
    result = sql.run('''
        SELECT compilation
        FROM videos
        WHERE uploaded = 0
          AND compilation IS NOT NULL
        GROUP BY compilation
    ''')

    # get list of files
    files = [ row['compilation'] for row in result ]

    for file in files:
        # build the filepath
        filepath = os.path.join(os.getcwd(),COMPILATION_FOLDER,file)
        # extract the video count
        number = re.findall(r'\d+', file)[0]

        # upload them
        upload(filepath, number)

        # update the DB
        sql.run('''
            UPDATE videos 
            SET uploaded = 1
            WHERE 
                compilation = '{compilation}'
        '''.format(
            compilation=file
        ))
