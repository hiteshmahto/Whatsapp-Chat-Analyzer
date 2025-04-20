import re
import pandas as pd
import emoji

def get_year_format(date_str):
    date_part = date_str.split(',')[0].strip()
    year = date_part.split('/')[-1]
    if len(year) == 2:
        return 'YY'
    elif len(year) == 4:
        return 'YYYY'
    else:
        raise ValueError(f"Invalid year format in date: {date_str}")

def preprocess(data):
    # Remove newlines
    data = data.replace("\n", "")
    
    # Regex for timestamps: DD/MM/YY or DD/MM/YYYY, with optional am/pm
    pattern = r"\d{2}\/\d{2}\/(?:\d{2}|\d{4}),\s\d{1,2}:\d{2}(?:\u202f(?:am|pm))?\s\-"
    messages = re.split(pattern, data)[1:]
    dates = re.findall(pattern, data)
    
    users = []
    messages_list = []
    for message in messages:
        entry = re.split(r"([\w\W]+?):\s", message, maxsplit=1)
        if len(entry) > 1:  # User message
            users.append(entry[1].strip().title())
            messages_list.append(entry[2])
        else:  # Group notification
            users.append("group_notifications")
            messages_list.append(entry[0])
    
    # Create DataFrame
    df = pd.DataFrame({"msg_date": dates, "user": users, "message": messages_list})
    
    # Clean up timestamp format
    df["msg_date"] = df["msg_date"].str.strip().str.replace(r"\s-\s*$", "", regex=True)
    
    # Determine year format from the first date
    if not df.empty:
        first_date = df['msg_date'].iloc[0]
        year_format = get_year_format(first_date)
    else:
        raise ValueError("No messages found in the chat data.")
    
    # Determine time format
    if any('am' in date or 'pm' in date for date in df['msg_date']):
        time_format = '%I:%M %p'
    else:
        time_format = '%H:%M'
    
    # Set the date format
    if year_format == 'YY':
        date_format = f'%d/%m/%y, {time_format}'
    else:
        date_format = f'%d/%m/%Y, {time_format}'
    
    # Parse the dates
    df['msg_date'] = pd.to_datetime(df['msg_date'], format=date_format, errors='coerce')
    
    # Drop rows with invalid dates
    df = df.dropna(subset=['msg_date']).reset_index(drop=True)
    
    # Derive date components
    df["year"] = df["msg_date"].dt.year
    df["month"] = df["msg_date"].dt.month_name()
    df["day"] = df["msg_date"].dt.day
    df["hour"] = df["msg_date"].dt.hour
    df["minute"] = df["msg_date"].dt.minute
    df["date"] = df["msg_date"].dt.date
    df["month_num"] = df["msg_date"].dt.month
    df["day_name"] = df["msg_date"].dt.day_name()
    
    # Filter out group notifications
    df = df[df["user"] != "group_notifications"].reset_index(drop=True)
    
    # Extract emojis
    def extract_emojis(text):
        return "".join(char for char in text if char in emoji.EMOJI_DATA)
    
    df["emoji"] = df["message"].apply(extract_emojis)
    
    # Clean messages
    def clean_message(text):
        cleaned_text = emoji.replace_emoji(text, replace="")
        cleaned_text = re.sub(r"<media omitted>|<this message was edited>|this message was deleted|null", "", cleaned_text, flags=re.IGNORECASE)
        cleaned_text = re.sub(r"http\S+|www\S+", "", cleaned_text)
        cleaned_text = re.sub(r"\s+", " ", cleaned_text).strip()
        return cleaned_text if cleaned_text else ""
    
    df["clean_message"] = df["message"].apply(clean_message)
    df["is_empty_after_cleaning"] = df["clean_message"] == ""
    
    return df