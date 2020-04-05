import pandas as pd
import os
import re
import argparse
import sys
import webbrowser
import chatalyzer.analysis
from datetime import datetime
from tqdm import tqdm
from jinja2 import Environment, FileSystemLoader


# chat parsing functions taken from https://towardsdatascience.com/build-your-own-whatsapp-chat-analyzer-9590acca9014
def startsWithDateTime(s):
    patterns = [
        '([0-2][0-9]|(3)[0-1])(\/)(((0)[0-9])|((1)[0-2]))(\/)(\d{2}|\d{4}), ([0-9][0-9]):([0-9][0-9]) -',
        '([0-2][0-9]|(3)[0-1])(\/)(((0)[0-9])|((1)[0-2]))(\/)(\d{2}|\d{4}), ([0-9][0-9]):([0-9][0-9]) am -',
        '([0-2][0-9]|(3)[0-1])(\/)(((0)[0-9])|((1)[0-2]))(\/)(\d{2}|\d{4}), ([0-9]):([0-9][0-9]) am -',
        '([0-2][0-9]|(3)[0-1])(\/)(((0)[0-9])|((1)[0-2]))(\/)(\d{2}|\d{4}), ([0-9][0-9]):([0-9][0-9]) pm -',
        '([0-2][0-9]|(3)[0-1])(\/)(((0)[0-9])|((1)[0-2]))(\/)(\d{2}|\d{4}), ([0-9]):([0-9][0-9]) pm -'
    ]

    pattern = '^' + '|'.join(patterns)
    result = re.match(pattern, s)

    if result:
        return True
    return False


def startsWithAuthor(s):
    patterns = [
        '([\w]+):',  # first Name
        '([\w]+[\s]+[\w]+):',  # first Name + Last Name
        '([\w]+[\s]+[\w]+[\s]+[\w]+):',  # first Name + Middle Name + Last Name
        '([+]\d{2} \d{5} \d{5}):',  # mobile Number (India)
        '([+]\d{2} \d{3} \d{3} \d{4}):',  # mobile Number (US)
        '([+]\d{2} \d{4} \d{7})'  # mobile Number (Europe)
    ]
    pattern = '^' + '|'.join(patterns)
    result = re.match(pattern, s)

    if result:
        return True
    return False


def getDataPoint(line):
    # line = 18/06/17, 22:47 - Loki: Why do you have 2 numbers, Banner?
    splitLine = line.split(' - ')  # splitLine = ['18/06/17, 22:47', 'Loki: Why do you have 2 numbers, Banner?']
    dateTime = splitLine[0]  # dateTime = '18/06/17, 22:47'
    date, time = dateTime.split(', ')  # date = '18/06/17'; time = '22:47'
    message = ' '.join(splitLine[1:])  # message = 'Loki: Why do you have 2 numbers, Banner?'

    if startsWithAuthor(message):  # True
        splitMessage = message.split(': ')  # splitMessage = ['Loki', 'Why do you have 2 numbers, Banner?']
        author = splitMessage[0]  # author = 'Loki'
        message = ' '.join(splitMessage[1:])  # message = 'Why do you have 2 numbers, Banner?'
    else:
        author = None

    return date, time, author, message


def getChats(chatfile):
    with open(chatfile, "r", encoding="utf-8") as in_file:  # storing the chat data in the variable lines
        lines = in_file.readlines()

    parsedData = []  # list to keep track of data so it can be used by a Pandas dataframe
    pbar = tqdm(lines, desc="Reading chats")  # displaying a progress bar to show the amount of the chat data loaded
    messageBuffer = []  # buffer to capture intermediate output for multi-line messages
    date, time, author = None, None, None  # intermediate variables to keep track of the current message being processed

    for i, line in enumerate(pbar):
        line = line.strip()  # guarding against erroneous leading and trailing whitespaces
        if startsWithDateTime(line):  # if a line starts with a Date Time pattern, then this indicates the beginning of a new message
            if len(messageBuffer) > 0:  # check if the message buffer contains characters from previous iterations
                parsedData.append([date, time, author, ' '.join(messageBuffer)])  # save the tokens from the previous message in parsedData
            messageBuffer.clear()  # clear the message buffer so that it can be used for the next message
            date, time, author, message = getDataPoint(line)  # identify and extract tokens from the line
            messageBuffer.append(message)
        else:
            messageBuffer.append(line)  # if a line doesn't start with a Date Time pattern, then it is part of a multi-line message. So, just append to buffer"""

    df = pd.DataFrame(parsedData, columns=['Date', 'Time', 'Author', 'Message'])

    return df


def main():
    parser = argparse.ArgumentParser()  # parsing the arguments given to get the chat data
    parser.add_argument("chatfile", help="Path to the chat file obtained by exporting from Whatsapp")
    parser.add_argument("--output", "-o", help="Path of output html file containing the analysis",
                        default="analysis.html")
    args = parser.parse_args()

    df = getChats(args.chatfile)  # parse the chat data

    pkg_dir = os.path.dirname(__file__)
    file_loader = FileSystemLoader(os.path.join(pkg_dir, "templates"))
    env = Environment(loader=file_loader)
    template = env.get_template("chat_analysis.html")
    output = template.render(name="H")
    with open(args.output, 'w') as f:
        f.write(output)
    print(output)

    webbrowser.open("file://" + os.path.abspath(args.output))  # display the results of the analysis on a web-page


if __name__ == "__main__":  # to start the analysis of the chat data
    main()
