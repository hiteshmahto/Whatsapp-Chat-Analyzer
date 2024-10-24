import streamlit as st
import preprocessor, helper
import matplotlib.pyplot as plt
import seaborn as sns

# Set the page layout
st.set_page_config(page_title="WhatsApp Chat Analyzer", page_icon=":speech_balloon:")

st.title(":green[WhatsApp] Chat Analyzer 📊")
st.sidebar.title(":green[WhatsApp] Chat Analyzer 📊")


st.sidebar.text("Date should be in format DD/MM/YY")
uploaded_file = st.sidebar.file_uploader("Choose a txt file", type='txt')
if uploaded_file is not None:
    bytes_data = uploaded_file.getvalue()
    data = bytes_data.decode("utf-8")
    df = preprocessor.preprocess(data)
    st.sidebar.info("File is Successfully Uploaded", icon="📁")
    
    # fetch unique users
    user_list = df['user'].unique().tolist()
    user_list.sort()
    user_list.insert(0, "Overall")
    selected_user = st.sidebar.selectbox("Show analysis wrt", user_list)
    
    if st.sidebar.button("Show Analysis"):
        first_date, last_date, chatted_for_days = helper.start_end_date(selected_user, df)
        if selected_user == "Overall":
            st.header(f":orange[Overall Analysis]", divider="orange")
        else:
            st.header(f":orange[{selected_user}'s Analysis - chatted for {chatted_for_days} Days!!!]", divider="orange")
        

        col1, col2 = st.columns(2)

        with col1:
            st.subheader(":grey[First Message]")
            st.title(f"{first_date}")
        with col2:
            st.subheader(":grey[Last Message]")
            st.title(f"{last_date}")
        
        st.header(":orange[Top Statistics]", divider="orange")
        num_messages, words, num_media_msgs, num_links = helper.fetch_stats(selected_user, df)
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.subheader(":grey[Total Messages]")
            st.title(num_messages)
        with col2:
            st.subheader(":grey[Total Words]")
            st.title(words)
        with col3:
            st.subheader(":grey[Media Shared]")
            st.title(num_media_msgs)
        with col4:
            st.subheader(":grey[Links Shared]")
            st.title(num_links)
        
        # finding the busiest user in the group (Group Level)
        if selected_user == "Overall":
            st.header(":orange[Most Busy User]", divider="orange")
            x, new_df = helper.most_busy_user(df)
            
            col1, col2 = st.columns([2, 1])
            
            with col1:
                fig, ax = plt.subplots()
                ax.bar(x.index, x.values, color='lightyellow')
                if len(user_list) > 5:
                    plt.xticks(rotation='vertical')
                ax.set_ylabel('Message Count', fontsize=12)
                helper.style_plot(ax, fig)
                st.pyplot(fig)
            with col2:
                st.dataframe(new_df)
        

        # monthly timeline
        monthly_timeline = helper.monthly_timeline(selected_user, df)
        st.header(":orange[Monthly Timeline]", divider='orange')
        fig, ax = plt.subplots(figsize=(8, 4))
        ax.plot(monthly_timeline['time'], monthly_timeline['message'], color='lightgreen')
        if len(monthly_timeline['time']) > 5:
            plt.xticks(rotation='vertical')
        ax.set_ylabel('Message Count', fontsize=12)
        helper.style_plot(ax, fig)
        st.pyplot(fig)

        # daily timeline
        daily_timeline = helper.daily_timeline(selected_user, df)
        st.header(":orange[Daily Timeline]", divider='orange')
        fig, ax = plt.subplots(figsize=(8, 4))
        ax.plot(daily_timeline['date'], daily_timeline['message'], color='lightgreen')
        plt.xticks(rotation='vertical')
        ax.set_ylabel('Message Count', fontsize=12)
        helper.style_plot(ax, fig)
        st.pyplot(fig)

        # activity map
        st.header(":orange[Activity Map]", divider='orange')
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Most busy day")
            busy_day = helper.week_activity_map(selected_user, df)
            fig, ax = plt.subplots()
            ax.bar(busy_day.index, busy_day.values, color='lightgreen')
            plt.xticks(rotation='vertical')
            ax.set_ylabel("Message Count", fontsize=12)
            helper.style_plot(ax, fig)
            st.pyplot(fig)

        with col2:
            st.subheader("Most busy month")
            busy_month = helper.month_activity_map(selected_user, df)
            fig, ax = plt.subplots()
            ax.bar(busy_month.index, busy_month.values, color='lightpink')            
            plt.xticks(rotation='vertical')
            ax.set_ylabel("Message Count", fontsize=12)
            helper.style_plot(ax, fig)
            st.pyplot(fig)
        
        st.header(":orange[Word Cloud]", divider="orange")
        col1, col2 = st.columns([2,1])
        with col1:
            wordcloud = helper.create_wordcloud(selected_user, df)
            fig, ax = plt.subplots(figsize=(10, 5))
            ax.imshow(wordcloud, interpolation='bilinear')
            ax.axis("off")  # Turn off axes (no border)
            fig.patch.set_alpha(0)  # Make the background of the figure transparent
            st.pyplot(fig)
            
        st.header(":orange[Weekly Activity Map]", divider="orange")
        user_heatmap = helper.activity_heatmap(selected_user, df)
        fig, ax = plt.subplots(figsize=(14, 7))
        ax = sns.heatmap(user_heatmap, cbar=True)
        color_bar = ax.collections[0].colorbar
        ax.set_xlabel('Time', fontsize=15)
        ax.set_ylabel('Weekdays', fontsize=15)
        helper.style_plot(ax, fig)
        color_bar.ax.yaxis.label.set_color("white")  # Set color bar label color
        color_bar.ax.tick_params(colors="white")  # Set color bar tick color
        st.pyplot(fig)
        
        
        emoji_df, chat_percent_with_emoji = helper.emoji_helper(selected_user, df)
        st.header(f":orange[Emoji Analysis]{emoji_df[0][0]}", divider="orange")
        st.subheader("Emoji Count")
        st.dataframe(emoji_df.T)
        
        st.subheader("HIIIE")
        