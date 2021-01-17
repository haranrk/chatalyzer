import pandas as pd
import datetime
import json
import emoji
import string
import os
from collections import Counter

KEY_DATE = 'Date'
KEY_TIME = 'Time'
KEY_AUTHOR = 'Author'
KEY_MESSAGE = 'Message'
KEY_DATE_TIME = 'Date Time'
KEY_YEAR = 'Year'
KEY_MONTH = 'Month'
KEY_DAY = 'Day'
KEY_HOUR = 'Hour'
KEY_MINUTE = 'Minute'
KEY_SECOND = 'Second'
KEY_LETTER_COUNT = 'Letter Count'
KEY_WORD_COUNT = 'Word Count'
KEY_MESSAGE_COUNT = 'Message Count'
KEY_BUSY_X = 'Busy X'
KEY_WORD = 'Word'
KEY_EMOJI = 'Emoji'
KEY_EMOJI_COUNT = 'Emoji Count'

TAG_MEDIA_OMITTED = '<Media omitted>'


class DateTimeEncoder(json.JSONEncoder):
    """
    Overrides the default json encoder to handle datetime objects
    """

    def default(self, obj):
        if isinstance(obj, (datetime.date, datetime.datetime)):
            return obj.isoformat()


def am_pm_to_24hr(df):
    """
    Returns a Pandas DataFrame with time format changed from am/pm to 24hr in the 'Time' column

    Arguments:
        df (Pandas.DataFrame) - DataFrame of chats having the 'Time' column

    Returns:
        Pandas.DataFrame
    """
    df2 = df.copy()
    df2[KEY_TIME] = pd.to_datetime(df2[KEY_TIME]).dt.strftime('%H:%M:%S')
    return df2


def drop_none_author(df, reset_index=True):
    """
    Returns a Pandas DataFrame in which the rows not associated with an author are removed

    Arguments:
        df (Pandas.DataFrame) - DataFrame of chats
        reset_index (bool, default True) - Set True if indices are to be reset after dropping the rows

    Returns:
        Pandas.DataFrame
    """
    df2 = df.dropna()
    if reset_index:
        df2.reset_index(drop=True, inplace=True)
    return df2


def drop_media_messages(df, reset_index=True):
    """
        Returns a Pandas DataFrame in which the rows not associated with a media message are removed

        Arguments:
            df (Pandas.DataFrame) - DataFrame of chats
            reset_index (bool, default True) - Set True if indices are to be reset after dropping the rows

        Returns:
            Pandas.DataFrame
    """
    media_message_df = get_media_messages(df)
    media_indices = media_message_df.index
    media_omitted_df = df.drop(index=media_indices)
    if reset_index:
        media_omitted_df.reset_index(drop=True, inplace=True)
    return media_omitted_df


def get_media_messages(df):
    """
        Returns a Pandas DataFrame containing rows associated with media messages

        Arguments:
            df (Pandas.DataFrame) - DataFrame of chats

        Returns:
            Pandas.DataFrame
    """
    media_messages = df.loc[df[KEY_MESSAGE] == TAG_MEDIA_OMITTED]
    return media_messages


def get_date_time(df):
    """
        Returns a Pandas DatetimeIndex object for easy manipulation of dates and times

        Arguments:
            df (Pandas.DataFrame) - DataFrame of chats containing 'Date' and 'Time' columns

        Returns:
            Pandas.DatatimeIndex
    """
    df2 = am_pm_to_24hr(df)

    potential_formats = [
            '%d/%m/%y:%H:%M:%S',
            '%m/%d/%y:%H:%M:%S',
            '%Y/%m/%d:%H:%M:%S'
            ]
    for potential_format in potential_formats:
        try:
            date_time = pd.to_datetime(df2[KEY_DATE] + ':' + df2[KEY_TIME], format=potential_format)
        except ValueError:
            continue

    return date_time


def get_top_x_count(df, x, n_authors=10):
    """
    Returns a Pandas DataFrame containing the names and word/letter count of top senders
    sorted in descending order of the word/letter count

        Arguments:
            df (Pandas.DataFrame) - DataFrame of chats
            x (str) - KEY_LETTER_COUNT, KEY_WORD_COUNT
            n_authors (int, default 10) - Number of top authors required (-1 to get all rows)

        Returns:
            Pandas.DataFrame ('Author', x)
    """
    df2 = df.groupby(KEY_AUTHOR, as_index=False).sum() \
        .sort_values(by=[x], ascending=False) \
        .reset_index(drop=True)

    top_x_df = df2[[KEY_AUTHOR, x]]
    if n_authors == -1:
        return top_x_df
    else:
        return top_x_df.head(n_authors)


def get_top_message_senders(df, n_authors=10):
    """
    Returns a Pandas DataFrame containing the names and message count of top message senders
    sorted in descending order of the message count

        Arguments:
            df (Pandas.DataFrame) - DataFrame of chats
            n_authors (int, default 10) - Number of top authors required (-1 to get all rows)

        Returns:
            Pandas.DataFrame ('Author', 'Message Count')
    """
    df2 = df.groupby(KEY_AUTHOR, as_index=False).count() \
        .sort_values(by=[KEY_MESSAGE], ascending=False) \
        .reset_index(drop=True) \
        .rename(columns={KEY_MESSAGE: KEY_MESSAGE_COUNT})

    top_message_df = df2[[KEY_AUTHOR, KEY_MESSAGE_COUNT]]
    if n_authors == -1:
        return top_message_df
    else:
        return top_message_df.head(n_authors)


def get_top_media_senders(df, n_authors=10):
    """
    Returns a Pandas DataFrame containing the names and message count of top media senders
    sorted in descending order of the message count

        Arguments:
            df (Pandas.DataFrame) - DataFrame of chats
            n_authors (int, default 10) - Number of top authors required (-1 to get all rows)

        Returns:
            Pandas.DataFrame ('Author', 'Message Count')
    """
    media_messages = get_media_messages(df)
    df2 = media_messages.groupby(KEY_AUTHOR, as_index=False).count() \
        .sort_values(by=[KEY_MESSAGE], ascending=False) \
        .reset_index(drop=True) \
        .rename(columns={KEY_MESSAGE: KEY_MESSAGE_COUNT})

    top_media_df = df2[[KEY_AUTHOR, KEY_MESSAGE_COUNT]]
    if n_authors == -1:
        return top_media_df
    else:
        return top_media_df.head(n_authors)


def get_busy_x(df, x, n_x=10, sort=False, drop_none=True):
    """
    Returns a Pandas DataFrame containing the values of x and the number of messages corresponding to the x
    Here, x is 'Date', 'Time', 'Year', 'Month'...
        Arguments:
            df (Pandas.DataFrame) - DataFrame of chats
            x (str) - 'Date', 'Time', 'Year', 'Month', 'Day', 'Hour', 'Minute', 'Second'
            n_x (int, default 10) - Number of instances required required (-1 to get all rows)
            sort (bool) - If True, sorts by x. Else, sort by date.
            drop_none (bool) - If True, drops the 'None' author if not already removed.

        Returns:
            Pandas.DataFrame ('Busy X', 'Message Count')
    """

    df2 = df.copy()
    if drop_none:
        df2 = drop_none_author(df2)

    date_time = df2[KEY_DATE_TIME].dt
    x_data_dict = {
        KEY_DATE: date_time.date,
        KEY_TIME: date_time.time,
        KEY_YEAR: date_time.year,
        KEY_MONTH: date_time.month,
        KEY_DAY: date_time.day,
        KEY_HOUR: date_time.hour,
        KEY_MINUTE: date_time.minute,
        KEY_SECOND: date_time.second
    }

    df2[KEY_BUSY_X] = x_data_dict[x]
    df3 = df2.groupby(KEY_BUSY_X, as_index=False).count() 
    if sort==True:
        df3 = df3.sort_values(by=[KEY_MESSAGE], ascending=False)
    df3 = df3.reset_index(drop=True)\
        .rename(columns={KEY_MESSAGE: KEY_MESSAGE_COUNT})

    busy_x_df = df3[[KEY_BUSY_X, KEY_MESSAGE_COUNT]]
    if n_x == -1:
        return busy_x_df
    else:
        return busy_x_df.head(n_x)

def get_busy_x_authorwise(df,x,n_x, return_json, add_cumulative=False, sort=False, drop_none=True ):
    """
    Authorwise, returns data containing the values of x and the number of messages corresponding to the x
    Here, x is 'Date', 'Time', 'Year', 'Month'...
        Arguments:
            df (Pandas.DataFrame) - DataFrame of chats
            x (str) - 'Date', 'Time', 'Year', 'Month', 'Day', 'Hour', 'Minute', 'Second'
            n_x (int, default 10) - Number of instances required required (-1 to get all rows)
            add_cumulative (bool) - If True, adds another author row "Cumulative" that has the totals of all authors
            return_json - If True, returns in json instead of a dict of DataFrame
            sort (bool) - If True, sorts by x. Else, sort by date.
            drop_none (bool) - If True, drops the 'None' author if not already removed.

        Returns:
        if return_json is False,
           dict - Key: Author, Value: Corresponding Pandas.DataFrame ('Busy X', 'Message Count')
        otherwise,
           str - the json string of the data
    """
    df2 = df.copy()
    if drop_none:
        df2 = drop_none_author(df2)
    participant_list = get_participant_list(df2)

    data_list = []
    for participant in participant_list:
        participant_df = df2[df2[KEY_AUTHOR]==participant]
        data_list.append([participant, get_busy_x(participant_df,x,n_x=n_x, sort=sort)])

    if add_cumulative==True:
        data_list.append(["Cumulative", get_busy_x(df2,x=x, n_x=n_x, sort=sort)])

    if return_json==True:
        for i in range(len(data_list)):
            data_list[i][1] = data_list[i][1].values.tolist()

        data_json = json.dumps(data_list, cls=DateTimeEncoder)
        return data_json
    else:
        return data_list


def get_most_used_words(df, n_words=10, other=False):
    """
    Returns a Pandas DataFrame containing the common words and their count sorted in descending order

        Arguments:
            df (Pandas.DataFrame) - DataFrame of chats
            n_words (int, default 10) - Number of common words required (-1 to get all rows)
            other (bool, default False) - Set True if count of other words is to be added to the DataFrame

        Returns:
            Pandas.DataFrame ('Word', 'Word Count')
    """
    df = drop_media_messages(df)

    trivial_words_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), "static","misc","trivial_words.txt") #File containing the words comma-separated
    with open(trivial_words_path,'r') as f:
        unwanted_words = [x.strip() for x in f.readlines()]
    unwanted_words.extend([x.capitalize() for x in unwanted_words])
    # unwanted_words.extend(list(string.ascii_letters))
    unwanted_words.extend(list(string.digits))

    word_list = []
    for message in df[KEY_MESSAGE]:
        message = message.translate(message.maketrans('', '', string.punctuation))  # Removing punctuation
        word_list.extend(word for word in message.split()
                         if word not in emoji.UNICODE_EMOJI and word not in unwanted_words)

    counter = Counter(word_list)

    if n_words == -1:
        most_used_words_and_count = list(counter.items())
    else:
        most_used_words_and_count = counter.most_common(n_words)

    if other:
        total_words = len(word_list)
        total_used_words = sum(map(lambda x: x[1], most_used_words_and_count))
        most_used_words_and_count.append(('other', total_words - total_used_words))

    common_words_df = pd.DataFrame(most_used_words_and_count, columns=[KEY_WORD, KEY_WORD_COUNT])
    return common_words_df


def get_most_used_emojis(df, n_emojis=10, other=False):
    """
    Returns a Pandas DataFrame containing the common emojis and their count sorted in descending order

        Arguments:
            df (Pandas.DataFrame) - DataFrame of chats
            n_emojis (int, default 10) - Number of common emojis required (-1 to get all rows)
            other (bool, default False) - Set True if count of other emojis is to be added to the DataFrame

        Returns:
            Pandas.DataFrame ('Emoji', 'Emoji Count')
    """
    emoji_list = []
    for message in df[KEY_MESSAGE]:
        emoji_list.extend([c for c in message if c in emoji.UNICODE_EMOJI])

    counter = Counter(emoji_list)

    if n_emojis == -1:
        most_used_emojis_and_count= list(counter.items())
    else:
        most_used_emojis_and_count = counter.most_common(n_emojis)

    if other:
        total_emojis = len(emoji_list)
        total_used_emojis = sum(map(lambda x: x[1], most_used_emojis_and_count))
        most_used_emojis_and_count.append(('other', total_emojis - total_used_emojis))

    most_used_emojis_df = pd.DataFrame(most_used_emojis_and_count, columns=[KEY_EMOJI, KEY_EMOJI_COUNT])
    return most_used_emojis_df


def add_date_time(df):
    """
    Returns a Pandas DataFrame in which 'Date Time' column as a pandas DatetimeIndex object is appended to the parameter
    df

        Arguments:
            df (Pandas.DataFrame) - DataFrame of chats containing 'Date' and 'Time' columns

        Returns:
            Pandas.DataFrame
    """
    df2 = df.copy()
    date_time = get_date_time(df)
    df2[KEY_DATE_TIME] = date_time
    pd.DataFrame().dropna()
    return df2


def add_letter_count(df):
    """
    Returns a Pandas DataFrame in which 'Letter Count' column object is appended to the parameter df
    Letter Count is the number of characters in the 'Message' column of a row

        Arguments:
            df (Pandas.DataFrame) - DataFrame of chats containing 'Message' column

        Returns:
            Pandas.DataFrame
    """
    df2 = df.copy()
    df2[KEY_LETTER_COUNT] = df2[KEY_MESSAGE].apply(len)
    return df2


def add_word_count(df):
    """
    Returns a Pandas DataFrame in which 'Word Count' column object is appended to the parameter df
    Word Count is the number of words in the 'Message' column of a row

        Arguments:
            df (Pandas.DataFrame) - DataFrame of chats containing 'Message' column

        Returns:
            Pandas.DataFrame
    """
    df2 = df.copy()
    df2[KEY_WORD_COUNT] = df2[KEY_MESSAGE].apply(lambda x: len(x.split()))
    return df2


def get_participant_list(df):
    """
    Returns a list of the group participants

    Arguments:
        df (pandas.DataFrame) - DataFrame of the chat having at least the "Author" column

    Returns:
        list - List containing the participants
    """
    participant_list = list(drop_none_author(df)[KEY_AUTHOR].unique())
    return participant_list


def get_group_timeline(df):
    """
    Returns data containing when participants joined and left the group
    """
    pass
