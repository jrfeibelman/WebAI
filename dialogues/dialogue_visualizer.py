import streamlit as st
import pandas as pd

def visualize_chat_dataframe(chat_df):
    # Dictionary mapping speakers to image paths
    speaker_images = {
        'Mark': 'images/lawyer.png',  # TODO: change this to be configurable
        'Sarah': 'images/biz_women.jpeg',
        'Emily Thorton': 'images/biz_women.jpeg',
        'Mark Turner': 'images/lawyer.png'
        # Add more speakers and their image paths as needed
    }

    # Display each row as a bubble with an image
    for index, row in chat_df.iterrows():
        # Display speaker's image if available
        if row['speaker'] in speaker_images:
            st.image(speaker_images[row['speaker']], width=50)

        st.markdown(
            f'<div style="background-color: #F0F0F0; padding: 10px; margin: 10px; border-radius: 10px; display: inline-block; margin-left: 60px;">'
            f'<b>Speaker:</b> {row["speaker"]}<br>'
            f'<b>Utterance:</b> {row["utterance"]}'
            '</div>', unsafe_allow_html=True
        )

def main():
    st.title("Chat Visualization from CSV Upload")

    # Upload the CSV file
    uploaded_file = st.file_uploader("Upload CSV File", type=["csv"])

    if uploaded_file is not None:
        # Read the CSV file into a DataFrame
        chat_df = pd.read_csv(uploaded_file)

        st.success("File successfully uploaded!")

        # Display the DataFrame
        st.dataframe(chat_df)

        st.title("Visualizing Chat")

        # Visualize the chat from the DataFrame
        visualize_chat_dataframe(chat_df)

if __name__ == "__main__":
    main()
