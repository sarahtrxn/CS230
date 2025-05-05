"""Class: CS230--Section 3 
Name: Sarah Tran
Description: McDonald's Review
I pledge that I have completed the programming assignment independently. 
I have not copied the code from a student or any source.
I have not given my code to any student. """
import pandas as pd
import numpy as np
import streamlit as st
import matplotlib.pyplot as plt
import pydeck as pdk
import seaborn as sns
import mapbox as mb
from wordcloud import WordCloud, STOPWORDS

DATA_FILE = 'McDonald_s_Reviews.csv'
BANNER = "CS 230 Website Banner.png"
@st.cache_data

# [DA1] Clean and load data
def load_data(data):
    df = pd.read_csv(data,encoding='latin1')
    df['rating'] = df['rating'].str.extract(r'(\d+\.?\d*)')
    df['rating'] = pd.to_numeric(df['rating'], errors='coerce')
    df.columns = df.columns.str.strip().str.lower()
    df[['city', 'state']] = df['store_address'].str.extract(r',\s*([^,]+),\s*([A-Z]{2})\s+\d{5}')
    return df


def store_map(df):
    st.subheader(':red[Locations of McDonald\'s]')

    view_state = pdk.ViewState(
        latitude = df['latitude'].mean(),
        longitude = df['longitude'].mean(),
        zoom = 3
    )

    station_layer = pdk.Layer(
        'ScatterplotLayer',
        data=df,
        get_position='[longitude, latitude]',
        get_radius='scaled_radius',
        radius_scale = 2,
        radius_min_pixels= 5,
        radius_max_pixels = 15,
        get_color=[255, 255, 143],
        pickable=True
    )

    tool_tip = {
        "html": "McDonald\'s Address:<br/> <b>{store_address}</b> ",
        "style": { "backgroundColor": 'lightyellow',"color": "black"}
    }

    map = pdk.Deck(
        map_style='mapbox://styles/mapbox/light-v9',
        initial_view_state=view_state,
        layers=[station_layer],
        tooltip=tool_tip
    )

    st.pydeck_chart(map)
def main():
    st.set_page_config(page_title='CS230 Final',
                            page_icon='🍔',
                            layout='centered',
                            initial_sidebar_state='collapsed')
    st.image(BANNER)
    st.title("McDonald's Store Reviews Explorer")
    data = load_data(DATA_FILE)

    st.markdown('''Please use this to help explore customer reviews from all McDonald's stores across the U.S. 
        You are able to filter the city, state, and the average rating of each location. You can view top-rated locations, rating
        distribution boxplot, and a map locator. As a bonus, check out the wordmap to show common positive and negative keywords in reviews.''')
    store_map(data)
    # [SEA1] Charts made with Seaborn
    fig, ax = plt.subplots(figsize=(10, 5))
    sns.boxplot(data=data, x='state', y='rating', ax=ax)
    ax.set_title('Ratings by State')
    st.pyplot(fig)

    st.subheader('View McDonald\'s Best and Worst Ratings by Location')
    states = data['state'].dropna().unique()
    selected_state = st.selectbox('Select state:', sorted(states))

    state_data = data[data['state'] == selected_state]

    if not state_data.empty:
        cities = state_data['city'].dropna().unique()
        selected_city = st.selectbox('Select a city:', sorted(cities))

        city_data = state_data[state_data['city'] == selected_city]
        city_data_group = city_data.groupby(by=['city', 'store_address'])['rating'].agg("mean")
        city_data_group_sorted = city_data_group.sort_values(ascending=False)
        st.dataframe(city_data_group_sorted)

    st.subheader("Word Map of Positive and Negative Reviews")

    if 'review' in city_data.columns:

        city_data['review'] = city_data['review'].astype(str)
        city_data['rating'] = pd.to_numeric(city_data['rating'], errors='coerce')

        positive_reviews = city_data[city_data['rating'] >= 4]['review'].dropna()
        negative_reviews = city_data[city_data['rating'] <= 2]['review'].dropna()

        positive_text = " ".join(positive_reviews)
        negative_text = " ".join(negative_reviews)

        stopwords = set(STOPWORDS)

        # Generate Word Clouds with the help of chatGPT
        if positive_text.strip():
            st.markdown("#### Positive Reviews")
            positive_wc = WordCloud(width=600, height=400, background_color='white', stopwords=stopwords).generate(positive_text)
            fig1, ax1 = plt.subplots()
            ax1.imshow(positive_wc, interpolation='bilinear')
            ax1.axis('off')
            st.pyplot(fig1)
        else:
            st.info("No positive reviews found for this location.")

        if negative_text.strip():
            st.markdown("#### Negative Reviews")
            negative_wc = WordCloud(width=600, height=400, background_color='black', colormap='Reds', stopwords=stopwords).generate(negative_text)
            fig2, ax2 = plt.subplots()
            ax2.imshow(negative_wc, interpolation='bilinear')
            ax2.axis('off')
            st.pyplot(fig2)
        else:
            st.info("No negative reviews found for this location.")
    else:
        st.warning("No 'review_text' column found in the dataset.")

    st.sidebar.header('Feedback & Suggestions')

    with st.sidebar.form('feedback_form'):
        name = st.text_input('Your name (optional):')
        feedback_type = st.selectbox("What would you like to share?",
                                     ["Bug Report", "Feature Request", "Chart Suggestion", "General Comment"])
        feedback_text = st.text_area("Your feedback:",
                                     placeholder="Describe the bug, idea, or chart you'd like to see...")
        submitted = st.form_submit_button("Submit")

    if submitted:
        st.sidebar.success("Thanks for your feedback!")
        print("--- Feedback Submitted ---")
        print("Name:", name)
        print("Type:", feedback_type)
        print("Message:", feedback_text)

if __name__ == "__main__":
    main()
