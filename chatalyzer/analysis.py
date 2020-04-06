import pandas as pd
import ipdb


KEY_DATE = 'Date'
KEY_TIME = 'Time'
KEY_AUTHOR = 'Author'
KEY_MESSAGE = 'Message'
KEY_MESSAGE_COUNT = 'Message Count'
KEY_DATE_TIME = 'Date Time'

TAG_MEDIA_OMITTED = '<Media omitted>'


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
    date_time_df = pd.to_datetime(df2[KEY_DATE]+':'+df2[KEY_TIME], format='%d/%m/%y:%H:%M:%S')
    return date_time_df


def get_top_message_senders(df, n_authors=10):
    df2 = df.groupby(KEY_AUTHOR, as_index=False).count()\
        .sort_values(by=[KEY_MESSAGE], ascending=False)\
        .reset_index(drop=True)\
        .rename(columns={KEY_MESSAGE: KEY_MESSAGE_COUNT})

    top_message_df = df2[[KEY_AUTHOR, KEY_MESSAGE_COUNT]]
    return top_message_df.head(n_authors)


def get_top_media_senders(df, n_authors=10):
    media_messages = get_media_messages(df)
    df2 = media_messages.groupby(KEY_AUTHOR, as_index=False).count()\
        .sort_values(by=[KEY_MESSAGE], ascending=False)\
        .reset_index(drop=True)\
        .rename(columns={KEY_MESSAGE: KEY_MESSAGE_COUNT})

    top_media_df = df2[[KEY_AUTHOR, KEY_MESSAGE_COUNT]]
    return top_media_df.head(n_authors)


def get_busy_dates(df, n_dates=10):
    pass


def get_busy_hours(df, n_hours=10):
    pass


def add_word_count(df):
    pass


def add_letter_count(df):
    pass


def add_date_time(df):
    df2 = df.copy()
    date_time_df = get_date_time(df)
    df2[KEY_DATE_TIME] = date_time_df
    return df2


def debug_df(df):
    ipdb.set_trace()
