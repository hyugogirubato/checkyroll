#!/usr/bin/python

from colorama import init
import platform
import os
import sys
import getopt
from api import CrunchyrollAPI, FunimationAPI

init()


def main(argv):
    combot_list = False
    account_list = []
    combot_list_path = 'null'
    checker_type = 'null'
    custom_config = False
    custom_config_path = 'null'
    try:
        opts, args = getopt.getopt(argv, "i:t:c:", ["input=", "type=", "config="])
    except getopt.GetoptError:
        error_message()

    for opt, arg in opts:
        if opt in ('-i', '--input'):
            if arg.__contains__(':'):
                account_list.append(arg)
            else:
                combot_list = True
                combot_list_path = arg

        elif opt in ('-t', '--type'):
            if arg == 'crunchyroll':
                checker_type = arg
            elif arg == 'funimation':
                checker_type = arg

        elif opt in ('-c', '--config'):
            custom_config = True
            custom_config_path = arg

    command_line_args = []
    for opt, arg in opts:
        command_line_args.append(opt)
        command_line_args.append(arg)

    if checker_type == 'null':
        error_message()

    if combot_list:
        if os.path.isfile(combot_list_path):
            with open(combot_list_path, "r") as f:
                content = f.readlines()
            for line in content:
                if line.__contains__(':'):
                    account_list.append(line.strip())
        else:
            error_message()
    elif len(account_list) == 0:
        error_message()

    if custom_config:
        if os.path.isfile(custom_config_path):
            header("['{}']".format(custom_config_path), command_line_args)
            checker(checker_type, account_list, custom_config_path)
        else:
            error_message()
    else:
        header("[]", command_line_args)
        checker(checker_type, account_list, 'null')


def error_message():
    print('test.py -i <input> -t <type>')
    sys.exit()


def header(custom_config, command_line_args):
    checker_version = "2020.12.1"
    python_version = platform.python_version() + ' (CPython)'
    if platform.platform().__contains__('-SP'):
        windows_version = platform.platform().split('-SP')[0].strip()
    else:
        windows_version = platform.platform()
    print('[debug] Custom config: {}'.format(custom_config))
    print('[debug] Command-line args: {}'.format(command_line_args))
    print('[debug] checker version {}'.format(checker_version))
    print('[debug] Python version {} - {}'.format(python_version, windows_version))


def checker(checkerType, accountList, customConfig):
    account_list = []
    if os.path.isfile('crunchyroll/already_analyzed.txt'):
        with open('crunchyroll/already_analyzed.txt', "r") as f:
            contentFile = f.readlines()
        for account in accountList:
            alreadyAnalyzed = False
            for contentLine in contentFile:
                if contentLine.__contains__(account):
                    alreadyAnalyzed = True

            if not alreadyAnalyzed:
                account_list.append(account)
    else:
        for account in accountList:
            account_list.append(account)

    print('[{}] Number of accounts to verify: {}'.format(checkerType, len(account_list)))

    if checkerType == 'crunchyroll':
        CallAPI = CrunchyrollAPI(customConfig)
        CallAPI.checker(account_list)
    elif checkerType == 'funimation':
        CallAPI = FunimationAPI(customConfig)
        CallAPI.checker(account_list)


if __name__ == "__main__":
    main(sys.argv[1:])
