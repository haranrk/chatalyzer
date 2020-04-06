import pandas as pd
import ipdb


KEY_DATE = 'Date'
KEY_TIME = 'Time'
KEY_AUTHOR = 'Author'
KEY_MESSAGE = 'Message'
KEY_MESSAGE_COUNT = 'Message Count'

TAG_MEDIA_OMITTED = '<Media omitted>'


def am_pm_to_24hr(df):
    df2 = df.copy()
    df2[KEY_TIME] = pd.to_datetime(df2[KEY_TIME]).dt.strftime('%H:%M:%S')
    return df2


def drop_none_author(df):
    df2 = df.dropna()
    return df2


def drop_media_messages(df):
    media_messages = get_media_messages(df)
    media_indices = media_messages.index
    df2 = df.drop(index=media_indices)
    return df2


def get_media_messages(df):
    media_messages = df.loc[df[KEY_MESSAGE] == TAG_MEDIA_OMITTED]
    return media_messages


def add_hour_minute_second(df):
    pass


def add_letter_count(df):
    pass


def add_word_count(df):
    pass


def get_top_message_senders(df, n_authors=10):
    df2 = df.goupby(KEY_AUTHOR, sort=True).count()
    df3 = pd.DataFrame(df2[[KEY_AUTHOR, KEY_MESSAGE]].values, columns=[KEY_AUTHOR, KEY_MESSAGE_COUNT])
    return df3.loc[:(n_authors-1)]


def get_top_media_senders(df, n_authors=10):
    media_messages = get_media_messages(df)
    df2 = media_messages.groupby(KEY_AUTHOR, sort=True).count()
    df3 = pd.DataFrame(df2[[KEY_AUTHOR, KEY_MESSAGE]].values, columns=[KEY_AUTHOR, KEY_MESSAGE_COUNT])
    return df3.loc[:(n_authors-1)]


def get_busy_dates(df, n_days=10):
    pass


def get_busy_time_of_day(df, n_points=10):
    pass


def get_busy_hours(df, n_hours=10):
    pass


def debug_df(df):
    df = am_pm_to_24hr(df)
    ipdb.set_trace()
