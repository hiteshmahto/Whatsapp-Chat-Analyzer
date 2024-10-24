import re
import pandas as pd
import emoji

def preprocess(data):
    data = data.replace("\n", "")
    pattern = r"\d{2}\/\d{2}\/\d{2},\s\d{1,2}:\d{2}\u202f(?:am|pm)\s\-|\d{2}\/\d{2}\/\d{2},\s\d{2}:\d{2}\s\-"
    messages = re.split(pattern, data)[1:]
    users = []
    messages_list = []
    for message in messages:
        entry = re.split(r"([\w\W]+?):\s", message)
        if entry[1:]:
            users.append(entry[1])
            messages_list.append(entry[2])
        else:
            users.append('group_notifications')
            messages_list.append(entry[0])

    dates = re.findall(pattern, data)

    df = pd.DataFrame({"msg_date": dates, "user": users, "message": messages_list})

    df['msg_date'] = df['msg_date'].str.strip().str.replace(r'\s-\s*$', '', regex=True)

    if any('am' in date or 'pm' in date for date in df['msg_date']):
        df['msg_date'] = pd.to_datetime(df['msg_date'], format='%d/%m/%y, %I:%M %p')
    else:
        df['msg_date'] = pd.to_datetime(df['msg_date'], format='%d/%m/%y, %H:%M')

    df['year'] = df['msg_date'].dt.year
    df['month'] = df['msg_date'].dt.month_name()
    df['day'] = df['msg_date'].dt.day
    df['hour'] = df['msg_date'].dt.hour
    df['minute'] = df['msg_date'].dt.minute
    df['user'] = df['user'].str.strip().str.title()
    df['date'] = df['msg_date'].dt.date
    df['month_num'] = df['msg_date'].dt.month
    df = df[df['user'] != 'Group_Notifications'].reset_index(drop=True)
    df['day_name'] = df['msg_date'].dt.day_name()

    def extract_emojis(text):
        return ''.join(char for char in text if char in emoji.EMOJI_DATA)

    df['emoji'] = df['message'].apply(extract_emojis)

    def clean_message(text):
        cleaned_text = emoji.replace_emoji(text, replace="")  # Remove emojis
        cleaned_text = re.sub(r'<media omitted>', '', cleaned_text, flags=re.IGNORECASE)  # Remove media mentions
        cleaned_text = re.sub(r'<This message was edited>', '', cleaned_text, flags=re.IGNORECASE)
        cleaned_text = re.sub(r'This message was deleted', '', cleaned_text, flags=re.IGNORECASE)
        cleaned_text = re.sub(r'null', '', cleaned_text, flags=re.IGNORECASE)
        cleaned_text = re.sub(r'http\S+|www\S+', '', cleaned_text)
        cleaned_text = re.sub(r'\s+', ' ', cleaned_text).strip()  # Remove extra spaces
        return cleaned_text if cleaned_text else ""  # Return empty string if no content

    df['clean_message'] = df['message'].apply(clean_message)

    return df