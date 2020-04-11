import pandas as pd


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
    date_time = pd.to_datetime(df2[KEY_DATE]+':'+df2[KEY_TIME], format='%d/%m/%y:%H:%M:%S')
    return date_time


def get_top_message_senders(df, n_authors=10):
    """
    Returns a Pandas DataFrame containing the names and message count of top message senders
    sorted in descending order of the message count

        Arguments:
            df (Pandas.DataFrame) - DataFrame of chats
            n_authors (int, default 10) - Number of top authors required

        Returns:
            Pandas.DataFrame ('Author', 'Message Count')
    """
    df2 = df.groupby(KEY_AUTHOR, as_index=False).count()\
        .sort_values(by=[KEY_MESSAGE], ascending=False)\
        .reset_index(drop=True)\
        .rename(columns={KEY_MESSAGE: KEY_MESSAGE_COUNT})

    top_message_df = df2[[KEY_AUTHOR, KEY_MESSAGE_COUNT]]
    return top_message_df.head(n_authors)


def get_top_media_senders(df, n_authors=10):
    """
    Returns a Pandas DataFrame containing the names and message count of top media senders
    sorted in descending order of the message count

        Arguments:
            df (Pandas.DataFrame) - DataFrame of chats
            n_authors (int, default 10) - Number of top authors required

        Returns:
            Pandas.DataFrame ('Author', 'Message Count')
    """
    media_messages = get_media_messages(df)
    df2 = media_messages.groupby(KEY_AUTHOR, as_index=False).count()\
        .sort_values(by=[KEY_MESSAGE], ascending=False)\
        .reset_index(drop=True)\
        .rename(columns={KEY_MESSAGE: KEY_MESSAGE_COUNT})

    top_media_df = df2[[KEY_AUTHOR, KEY_MESSAGE_COUNT]]
    return top_media_df.head(n_authors)


def get_busy_x(df, x, n_x=10):
    """
    Returns a Pandas DataFrame containing the values of x and the number of messages corresponding to the x
    Here, x is 'Date', 'Time', 'Year', 'Month'...
        Arguments:
            df (Pandas.DataFrame) - DataFrame of chats
            x (str) - 'Date', 'Time', 'Year', 'Month', 'Day', 'Hour', 'Minute', 'Second'
            n_x (int, default 10) - Number of instances required required

        Returns:
            Pandas.DataFrame ('Busy X', 'Message Count')
    """

    date_time = df[KEY_DATE_TIME].dt
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

    df2 = df.copy()
    df2[KEY_BUSY_X] = x_data_dict[x]
    df3 = df2.groupby(KEY_BUSY_X, as_index=False).count() \
        .sort_values(by=[KEY_MESSAGE], ascending=False) \
        .reset_index(drop=True)\
        .rename(columns={KEY_MESSAGE: KEY_MESSAGE_COUNT})

    busy_x_df = df3[[KEY_BUSY_X, KEY_MESSAGE_COUNT]]
    return busy_x_df.head(n_x)


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


def list_participants(df):
    """
    Returns a list of the group participants

    Arguments:
        df (pandas.DataFrame) - DataFrame of the chat having at least the "Author" column

    Returns:
        list - List containing the participants
    """
    participant_list = list(drop_none_author(df)[KEY_AUTHOR].unique())
    return participant_list
