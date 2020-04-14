import pandas as pd
import datetime
import json


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

TAG_MEDIA_OMITTED = '<Media omitted>'


class DateTimeEncoder(json.JSONEncoder):
    '''
    Overrides th default json encoder to handle datetim objects
    '''
    def default(self, obj):
        if isinstance(obj, (datetime.date, datetime.datetime)):
            return obj.isoformat()


def am_pm_to_24hr(df):
    df2 = df.copy()
    df2[KEY_TIME] = pd.to_datetime(df2[KEY_TIME]).dt.strftime('%H:%M:%S')
    return df2


def drop_none_author(df, reset_index=True):
    df2 = df.dropna()
    if reset_index:
        df2.reset_index(drop=True, inplace=True)
    return df2


def drop_media_messages(df, reset_index=True):
    media_message_df = get_media_messages(df)
    media_indices = media_message_df.index
    media_omitted_df = df.drop(index=media_indices)
    if reset_index:
        media_omitted_df.reset_index(drop=True, inplace=True)
    return media_omitted_df


def get_media_messages(df):
    media_messages = df.loc[df[KEY_MESSAGE] == TAG_MEDIA_OMITTED]
    return media_messages


def get_date_time(df):
    df2 = am_pm_to_24hr(df)
    date_time = pd.to_datetime(df2[KEY_DATE]+':'+df2[KEY_TIME], format='%d/%m/%y:%H:%M:%S')
    return date_time


def get_top_message_senders(df, n_authors=10):
    df2 = df.groupby(KEY_AUTHOR, as_index=False).count()\
        .sort_values(by=[KEY_MESSAGE], ascending=False)\
        .reset_index(drop=True)\
        .rename(columns={KEY_MESSAGE: KEY_MESSAGE_COUNT})

    top_message_df = df2[[KEY_AUTHOR, KEY_MESSAGE_COUNT]]
    if n_authors == -1:
        return top_message_df
    else:
        return top_message_df.head(n_authors)


def get_top_media_senders(df, n_authors=10):
    media_messages = get_media_messages(df)
    df2 = media_messages.groupby(KEY_AUTHOR, as_index=False).count()\
        .sort_values(by=[KEY_MESSAGE], ascending=False)\
        .reset_index(drop=True)\
        .rename(columns={KEY_MESSAGE: KEY_MESSAGE_COUNT})

    top_media_df = df2[[KEY_AUTHOR, KEY_MESSAGE_COUNT]]
    if n_authors == -1:
        return top_media_df
    else:
        return top_media_df.head(n_authors)


def get_busy_x(df, x, n_x=10, drop_none=True):
    df2 = df.copy()
    if drop_none==True:
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
    df3 = df2.groupby(KEY_BUSY_X, as_index=False).count() \
        .sort_values(by=[KEY_MESSAGE], ascending=False) \
        .reset_index(drop=True)\
        .rename(columns={KEY_MESSAGE: KEY_MESSAGE_COUNT})

    busy_x_df = df3[[KEY_BUSY_X, KEY_MESSAGE_COUNT]]
    if n_x == -1:
        return busy_x_df
    else:
        return busy_x_df.head(n_x)


def add_date_time(df):
    df2 = df.copy()
    date_time = get_date_time(df)
    df2[KEY_DATE_TIME] = date_time
    return df2


def add_letter_count(df):
    df2 = df.copy()
    df2[KEY_LETTER_COUNT] = df2[KEY_MESSAGE].apply(len)
    return df2


def add_word_count(df):
    df2 = df.copy()
    df2[KEY_WORD_COUNT] = df2[KEY_MESSAGE].apply(lambda x: len(x.split()))
    return df2

def list_participants(df):
    '''
    Returns a list of the group participants
    Arguments:
        df (pandas.DataFrame) - Dataframe of the chat having at least the "Author" column
    
    Returns:
        list - List containing the participants
    '''
    participant_list = list(drop_none_author(df)["Author"].unique())
    return participant_list


def group_timeline(df):
    '''
    Returns data containing when particpants joind and left the group
    '''
    pass


def messages_per_day(df):
    df1 = drop_none_author(df)







