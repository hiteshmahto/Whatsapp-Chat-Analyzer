import numpy as np
import pandas as pd
from urlextract import URLExtract
from wordcloud import WordCloud
from PIL import Image, ImageOps  # ImageOps to invert the mask
from collections import Counter

extractor = URLExtract()

def style_plot(ax, fig, spine_color='white', tick_color='white', label_color = "white"):
    ax.tick_params(colors=tick_color)  # Set tick color
    ax.spines['bottom'].set_color(spine_color)  # Set bottom spine color
    ax.spines['left'].set_color(spine_color)  # Set left spine color
    ax.spines[['right', 'top']].set_visible(False)  # Hide right and top spines
    ax.set_facecolor('none')  # Set axes background to transparent
    fig.patch.set_alpha(0.0)  # Make figure background transparent
    ax.xaxis.label.set_color(label_color)
    ax.yaxis.label.set_color(label_color)


def fetch_stats(selected_user, df):
    if selected_user != "Overall":
        df = df[df['user'] == selected_user]
    # fetch the number of messages
    num_messages = df.shape[0]

    # fetch the total number of words
    words = []
    for msg in df['message']:
        words.extend(msg.split())

    # fetch number of media shared
    num_media_msg = df[df['message'] == '<Media omitted>'].shape[0]
    
    # fetch number of links shared
    links = []
    for msg in df['message']:
        links.extend(extractor.find_urls(msg))

    return num_messages, len(words), num_media_msg, len(links)

def most_busy_user(df):
    x = df['user'].value_counts().head()
    df = round((df['user'].value_counts() / df.shape[0])*100, 2).reset_index().rename(columns={'user': "User", 'count':"Percentage %"})
    return x, df

def create_wordcloud(selected_user, df):
    if selected_user != "Overall":
        df = df[df['user'] == selected_user]
        
    mask = np.array(Image.open("whatsapp.png"))

    # Generate the word cloud with transparent background
    wordcloud = WordCloud(
        width=200, 
        height=200, 
        mask=mask, 
        background_color=None,  # Transparent background
        mode='RGBA',  # Supports transparency in the image
        max_words=1000, 
        scale=3, 
        margin=1, 
        max_font_size=100
    ).generate(''.join(df['clean_message']))
    
    return wordcloud

def start_end_date(selected_user, df):
    if selected_user != "Overall":
        df = df[df['user'] == selected_user].reset_index(drop=True)
    
    # Get the first and last date from the DataFrame
    first_date = df['msg_date'][0]
    last_date = df['msg_date'].iloc[-1]

    # Helper function to add ordinal suffix to day
    def add_ordinal_suffix(day):
        if 11 <= day <= 13:
            return f"{day}th"
        else:
            suffix = {1: 'st', 2: 'nd', 3: 'rd'}.get(day % 10, 'th')
            return f"{day}{suffix}"

    # Format the first and last date
    first_date = f"{first_date.strftime('%B')} {add_ordinal_suffix(first_date.day)}, {first_date.year}"
    last_date = f"{last_date.strftime('%B')} {add_ordinal_suffix(last_date.day)}, {last_date.year}"
    chatted_for_days = len(df['date'].unique())

    return first_date, last_date, chatted_for_days


def monthly_timeline(selected_user ,df):
    if selected_user != "Overall":
        df = df[df['user'] == selected_user]
    timeline = df.groupby(['year', 'month_num', 'month']).count()['message'].reset_index()
    time = []
    for i in range(timeline.shape[0]):
        time.append(timeline['month'][i] + "-" + str(timeline['year'][i]))

    timeline['time'] = time
    return timeline

def daily_timeline(selected_user ,df):
    if selected_user != "Overall":
        df = df[df['user'] == selected_user]
    daily_timeline = df.groupby('date').count()['message'].reset_index()
    return daily_timeline

def week_activity_map(selected_user, df):
    if selected_user != "Overall":
        df = df[df['user'] == selected_user]
    
    return df['day_name'].value_counts()

def month_activity_map(selected_user, df):
    if selected_user != "Overall":
        df = df[df['user'] == selected_user]
    
    return df['month'].value_counts()

def activity_heatmap(selected_user, df):
    if selected_user != "Overall":
        df = df[df['user'] == selected_user]
    
    period = []
    new_dff=df[['hour', 'minute', 'day_name', 'message']]
    new_dff = new_dff.sort_values(by='hour').reset_index()

    for hour in new_dff['hour']:
        if hour == 23:
            period.append("23-00")
        elif hour == 0:
            period.append("0-1")
        else:
            period.append(str(hour) + "-" + str(hour+1))

    new_dff['period'] = period

    new_dff['period'] = pd.Categorical(new_dff['period'], categories=[
        "0-1", "1-2", "2-3", "3-4", "4-5", "5-6", "6-7", "7-8", "8-9", "9-10", 
        "10-11", "11-12", "12-13", "13-14", "14-15", "15-16", "16-17", "17-18", 
        "18-19", "19-20", "20-21", "21-22", "22-23", "23-00"], ordered=True)
    
    user_heatmap = new_dff.pivot_table(index='day_name', columns='period', values='message', aggfunc='count').fillna(0)
    return user_heatmap

def emoji_helper(selected_user, df):
    if selected_user != "Overall":
        df = df[df['user'] == selected_user]
    emojis = []
    for e in df['emoji']:
        if e != "":
            emojis.extend(e)

    messages_with_emoji = len(df[df['emoji'] != ""])
    messages_without_emoji = len(df) - messages_with_emoji
    sizes = [messages_with_emoji, messages_without_emoji]
    
    # sediment analysis of emoji
    emoji_sentiment_dict = {
    # Positive emojis
    "😀": "positive", "😃": "positive", "😄": "positive", "😁": "positive", "😆": "positive", "😅": "positive",
    "😂": "positive", "🤣": "positive", "😊": "positive", "😇": "positive", "😍": "positive", "😘": "positive",
    "😚": "positive", "😋": "positive", "😜": "positive", "😎": "positive", "🤩": "positive", "🥳": "positive",
    "🤗": "positive", "💖": "positive", "💓": "positive", "💕": "positive", "💞": "positive", "💝": "positive",
    "💙": "positive", "💚": "positive", "💛": "positive", "💜": "positive", "❤️": "positive", "🧡": "positive",
    "💗": "positive", "🎉": "positive", "🎊": "positive", "🥰": "positive", "😻": "positive", "👍": "positive",
    "🙏": "positive", "✨": "positive", "🌟": "positive", "🥹": "positive", "🔥": "positive", "💪": "positive",
    "🦄": "positive", "🌻": "positive", "🌼": "positive", "🥳": "positive", "🍀": "positive", "🎈": "positive",
    "🍰": "positive", "💌": "positive", "🧁": "positive", "☀️": "positive", "🌊": "positive", "🥲": 'positive',

    # Negative emojis
    "😞": "negative", "😔": "negative", "😟": "negative", "😕": "negative", "🙁": "negative", "☹️": "negative",
    "😣": "negative", "😖": "negative", "😫": "negative", "😩": "negative", "😭": "negative", "😢": "negative",
    "😨": "negative", "😰": "negative", "😱": "negative", "😡": "negative", "😠": "negative", "🤬": "negative",
    "👿": "negative", "😤": "negative", "😓": "negative", "🤒": "negative", "🤕": "negative", "🥵": "negative",
    "🥶": "negative", "😳": "negative", "😖": "negative", "💔": "negative", "💀": "negative", "☠️": "negative",
    "👎": "negative", "😵": "negative", "😧": "negative", "🤢": "negative", "🤮": "negative", "🤧": "negative",
    "😬": "negative", "😱": "negative", "😵‍💫": "negative", "🥺": "negative", "😧": "negative", "🖤": "negative",
    "💩": "negative", "😿": "negative", "😤": "negative"
    }

    
    sentiment_count = {"positive": 0, "neutral": 0, "negative": 0}
    for emoji in emojis:
        sentiment = emoji_sentiment_dict.get(emoji, "neutral")  # Default to 'neutral' if not found
        sentiment_count[sentiment] += 1

    emoji_df = pd.DataFrame(Counter(emojis).most_common(len(Counter(emojis))))[:51]
    return emoji_df, sizes, sentiment_count