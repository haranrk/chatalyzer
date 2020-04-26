import pandas as pd
import os
import json
import re
import argparse
import sys
import uuid
from chatalyzer import analysis
from datetime import datetime
from tqdm import tqdm
from flask import Flask, render_template, request, redirect, url_for, flash
import uuid

UPLOAD_FOLDER = os.path.join(os.path.abspath(os.path.dirname(__file__)), "uploads")
if not os.path.isdir(UPLOAD_FOLDER):
    os.mkdir(UPLOAD_FOLDER)

ALLOWED_EXTENSIONS = {'txt'}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


# chat parsing functions taken from https://towardsdatascience.com/build-your-own-whatsapp-chat-analyzer-9590acca9014
def starts_with_date_time(s):
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


def starts_with_author(s):
    patterns = [
        '([\w]+):',  # First Name
        '([\w]+[\s]+[\w]+):',  # First Name + Last Name
        '([\w]+[\s]+[\w]+[\s]+[\w]+):',  # First Name + Middle Name + Last Name
        '([+]\d{2} \d{5} \d{5}):',  # Mobile Number (India)
        '([+]\d{2} \d{3} \d{3} \d{4}):',  # Mobile Number (US)
        '([+]\d{2} \d{4} \d{7})'  # Mobile Number (Europe)
    ]
    pattern = '^' + '|'.join(patterns)
    result = re.match(pattern, s)

    if result:
        return True
    return False


def get_data_point(line):
    # line = 18/06/17, 22:47 - Loki: Why do you have 2 numbers, Banner?
    split_line = line.split(' - ')  # split_line = ['18/06/17, 22:47', 'Loki: Why do you have 2 numbers, Banner?']
    date_time = split_line[0]  # date_time = '18/06/17, 22:47'
    date, time = date_time.split(', ')  # date = '18/06/17'; time = '22:47'
    message = ' '.join(split_line[1:])  # message = 'Loki: Why do you have 2 numbers, Banner?'

    if starts_with_author(message):  # True
        split_message = message.split(': ')  # split_message = ['Loki', 'Why do you have 2 numbers, Banner?']
        author = split_message[0]  # author = 'Loki'
        message = ' '.join(split_message[1:])  # message = 'Why do you have 2 numbers, Banner?'
    else:
        author = None

    return date, time, author, message


def get_chats(chatfile):
    with open(chatfile, "r", encoding="utf-8") as in_file:  # storing the chat data in the variable lines
        lines = in_file.readlines()

    parsed_data = []  # list to keep track of data so it can be used by a Pandas dataframe
    pbar = tqdm(lines, desc="Reading chats")  # displaying a progress bar to show the amount of the chat data loaded
    message_buffer = []  # buffer to capture intermediate output for multi-line messages
    date, time, author = None, None, None  # intermediate variables to keep track of the current message being processed

    for i, line in enumerate(pbar):
        line = line.strip()  # guarding against erroneous leading and trailing whitespaces
        if starts_with_date_time(
                line):  # if a line starts with a Date Time pattern, then this indicates the beginning of a new message
            if len(message_buffer) > 0:  # check if the message buffer contains characters from previous iterations
                parsed_data.append([date, time, author, ' '.join(
                    message_buffer)])  # save the tokens from the previous message in parsed_data
            message_buffer.clear()  # clear the message buffer so that it can be used for the next message
            date, time, author, message = get_data_point(line)  # identify and extract tokens from the line
            message_buffer.append(message)
        else:
            message_buffer.append(
                line)  # if a line doesn't start with a Date Time pattern, then it is part of a multi-line message. So, just append to buffer"""

    parsed_data.append(
        [date, time, author, ' '.join(message_buffer)])  # save the tokens from the previous message in parsed_data
    df = pd.DataFrame(parsed_data, columns=['Date', 'Time', 'Author', 'Message'])

    return df


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/analysis/<analysis_id>')
def show_analysis(analysis_id):
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], analysis_id) + '.txt'
    df = get_chats(file_path)
    df = analysis.add_date_time(df)
    df = analysis.add_letter_count(df)
    df = analysis.add_word_count(df)


    top_message_senders = json.dumps(analysis.get_top_message_senders(df, -1).values.tolist())
    word_count = json.dumps(analysis.get_top_x_count(df, analysis.KEY_WORD_COUNT, -1).values.tolist())
    letter_count = json.dumps(analysis.get_top_x_count(df, analysis.KEY_LETTER_COUNT, -1).values.tolist())
    busiest_days = analysis.get_busy_x(df, analysis.KEY_DATE, -1)
    daywise_message_count = busiest_days.sort_values("Busy X")
    daywise_message_count = json.dumps(daywise_message_count.values.tolist(), cls=analysis.DateTimeEncoder)

    authorwise_daywise_message_count = analysis.get_busy_x_authorwise(df,analysis.KEY_DATE,-1,True)
    # import ipdb; ipdb.set_trace()
    return render_template('chat_analysis.html',
                           authorwise_daywise_message_count=authorwise_daywise_message_count,
                           num_msgs=df.shape[0],
                           daywise_message_count=daywise_message_count,
                           letter_count=letter_count,
                           word_count=word_count,
                           top_message_senders=top_message_senders)


@app.route('/uploader', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']

        # if user does not select file, browser also
        # submit an empty part without filename
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)

        if file and allowed_file(file.filename):
            # filename = secure_filename(file.filename)
            analysis_id = uuid.uuid4().hex
            filename = analysis_id + '.txt'
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            return redirect(url_for('show_analysis', analysis_id=analysis_id))


@app.route('/')
def index():
    return render_template("index.html")


def main():
    app.config.update(
        TESTING=True,
        # SECRET_KEY=b'_5#y2L"F4Q8z\n\xec]/'
    )

    app.run(debug=True)


if __name__ == "__main__":  # to start the analysis of the chat data
    main()
