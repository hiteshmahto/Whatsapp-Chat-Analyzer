import streamlit as st
import preprocessor, helper
import matplotlib.pyplot as plt
import seaborn as sns

# Set the page layout
st.set_page_config(page_title="WhatsApp Chat Analyzer", page_icon=":speech_balloon:")

st.title(":green[WhatsApp] Chat Analyzer 📊")
st.sidebar.title(":green[Chat] Insights Dashboard 📊")


st.sidebar.text("Upload Your Chat Data (Format: DD/MM/YY)")
uploaded_file = st.sidebar.file_uploader("Choose a txt file", type='txt')
if uploaded_file is not None:
    bytes_data = uploaded_file.getvalue()
    data = bytes_data.decode("utf-8")
    df = preprocessor.preprocess(data)
    st.sidebar.info("Chat Data Uploaded Successfully!!", icon="📁")
    
    # fetch unique users
    user_list = df['user'].unique().tolist()
    user_list.sort()
    user_list.insert(0, "Overall")
    selected_user = st.sidebar.selectbox("Select User for Analysis", user_list)
    
    if st.sidebar.button("Show Analysis"):
        first_date, last_date, chatted_for_days = helper.start_end_date(selected_user, df)
        if selected_user == "Overall":
            st.header(f":blue[Overall Analysis] 📈", divider="blue")
        else:
            st.header(f":blue[{selected_user}'s Analysis - chatted for {chatted_for_days} Days!!!] 📈", divider="blue")
        

        col1, col2 = st.columns(2)

        with col1:
            st.subheader(":grey[First Message Date]")
            st.title(f"{first_date}")
        with col2:
            st.subheader(":grey[Last Message Date]")
            st.title(f"{last_date}")
        
        st.header(":blue[Top Statistics] 👀", divider="blue")
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
            st.header(":blue[Most Active User in Chats 👑]", divider="blue")
            x, new_df = helper.most_busy_user(df)
            
            col1, col2 = st.columns([2, 1])
            
            with col1:
                fig, ax = plt.subplots()
                ax.bar(x.index, x.values, color='lightblue')
                if len(user_list) > 5:
                    plt.xticks(rotation='vertical')
                ax.set_ylabel('Message Count', fontsize=12)
                helper.style_plot(ax, fig)
                st.pyplot(fig)
            with col2:
                st.dataframe(new_df)
        

        # Monthly Messaging Trends
        monthly_timeline = helper.monthly_timeline(selected_user, df)
        st.header(":blue[Monthly Messaging Trends 📅]", divider='blue')
        fig, ax = plt.subplots(figsize=(8, 4))
        ax.plot(monthly_timeline['time'], monthly_timeline['message'], color='lightblue')
        if len(monthly_timeline['time']) > 5:
            plt.xticks(rotation='vertical')
        ax.set_ylabel('Message Count', fontsize=12)
        helper.style_plot(ax, fig)
        st.pyplot(fig)

        # Daily Message Trends
        daily_timeline = helper.daily_timeline(selected_user, df)
        st.header(":blue[Daily Message Trends 📈]", divider='blue')
        fig, ax = plt.subplots(figsize=(8, 4))
        ax.plot(daily_timeline['date'], daily_timeline['message'], color='lightblue')
        plt.xticks(rotation='vertical')
        ax.set_ylabel('Message Count', fontsize=12)
        helper.style_plot(ax, fig)
        st.pyplot(fig)

        # Chat Activity Heatmap
        st.header(":blue[Chat Activity 📊]", divider='blue')
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Peak Day of the Week 📅")
            busy_day = helper.week_activity_map(selected_user, df)
            fig, ax = plt.subplots()
            ax.bar(busy_day.index, busy_day.values, color='lightblue')
            plt.xticks(rotation='vertical')
            ax.set_ylabel("Message Count", fontsize=12)
            helper.style_plot(ax, fig)
            st.pyplot(fig)

        with col2:
            st.subheader("Peak Month of the Year 📆")
            busy_month = helper.month_activity_map(selected_user, df)
            fig, ax = plt.subplots()
            ax.bar(busy_month.index, busy_month.values, color='lightpink')            
            plt.xticks(rotation='vertical')
            ax.set_ylabel("Message Count", fontsize=12)
            helper.style_plot(ax, fig)
            st.pyplot(fig)
        
        # word cloud
        st.header(":blue[Word Cloud] ☁️", divider="blue")
        col1, col2 = st.columns([2,1])
        with col1:
            try:
                wordcloud = helper.create_wordcloud(selected_user, df)
                fig, ax = plt.subplots(figsize=(10, 5))
                ax.imshow(wordcloud, interpolation='bilinear')
                ax.axis("off")  # Turn off axes (no border)
                fig.patch.set_alpha(0)  # Make the background of the figure transparent
                st.pyplot(fig)
            except ValueError as e:
                if str(e) == "We need at least 1 word to plot a word cloud, got 0.":
                    st.warning("No words found to generate a word cloud. Please check the input data.")
        
        # weekly activity map
        st.header(":blue[Weekly Activity Heatmap 🕒]", divider="blue")
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
        
        try:
            emoji_df, sizes, sentiment_count = helper.emoji_helper(selected_user, df)
            st.header(f":blue[Emoji's Analysis] 👀", divider="blue")
            st.subheader("Count of Emojis Used 🔢")
            st.dataframe(emoji_df.T)
        except KeyError as e:
            st.warning("No emojis found in the chat data. Please check the input data.")
        
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Emoji 🆚 Non-Emoji Messages", divider='grey')         
            fig, ax = plt.subplots()

            ax.pie(
                sizes, autopct='%1.1f%%', startangle=90, 
                colors=['#c2a1e1', '#7b5cbf'],
                textprops={'fontsize': 15}
            )
            
            ax.axis('equal')
            helper.style_plot(ax, fig)
            ax.legend(['With Emoji', 'Without Emoji'],frameon=False, labelcolor='white')
            st.pyplot(fig)
        with col2:
            st.subheader("Emoji Sentiment Analysis😁😐😕", divider='grey')
            sentiment_sizes = list(sentiment_count.values())
            fig, ax = plt.subplots()
            ax.pie(sentiment_sizes, autopct='%1.1f%%', startangle=90, colors=['#99ff99', '#66b3ff', '#ff9999'], textprops={'fontsize': 15})
            ax.axis('equal')
            helper.style_plot(ax, fig)
            ax.legend(sentiment_count.keys(),frameon=False, labelcolor='white')
            st.pyplot(fig)