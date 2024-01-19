import streamlit as st
import pandas as pd
import re

def parse_chat_messages(log_file_path):
    with open(log_file_path, 'r') as file:
        log_data = file.readlines()

    # Define a regular expression pattern to extract relevant information
    pattern = r'\[([\d:APM ]+)\] \[([^\]]+)\] \[([^\]]+)\] (.+)'

    # Extract relevant information using the regular expression pattern
    parsed_data = [re.match(pattern, line).groups() for line in log_data if re.match(pattern, line)]

    # Create a DataFrame with the parsed data
    df = pd.DataFrame(parsed_data, columns=['Timestamp', 'Speaker', 'Type', 'Message'])

    return df

def visualize_log_file(log_file_path):
    df = parse_chat_messages(log_file_path)

    # Dictionary mapping speakers to image paths
    speaker_images = {
        'Hank Thompson': '/Users/nyeung/Projects/mythos/WebAI/frontend/images/hank.jpg',  # TODO: change this to be configurable
        'Claire Reynolds': '/Users/nyeung/Projects/mythos/WebAI/frontend/images/claire.jpg'
        # Add more speakers and their image paths as needed
    }

    # Display each row as a bubble with an image
    for index, row in df.iterrows():
        # st.balloons()
        # Display speaker's image if available
        if row['Speaker'] in speaker_images:
            st.image(speaker_images[row['Speaker']], width=100)

        st.markdown(
            f'<div style="background-color: #F0F0F0; padding: 10px; margin: 10px; border-radius: 10px;">'
            f'<b>Timestamp:</b> {row["Timestamp"]}<br>'
            f'<b>Speaker:</b> {row["Speaker"]}<br>'
            f'<b>Type:</b> {row["Type"]}<br>'
            f'<b>Message:</b> {row["Message"]}'
            '</div>', unsafe_allow_html=True
        )

def main():
    st.title("Log File Chat Visualization")

    # Upload the log file
    log_file = st.file_uploader("Upload Log File", type=["log", "txt"])

    if log_file is not None:
        st.success("File successfully uploaded!")
        visualize_log_file(log_file.name)

if __name__ == "__main__":
    main()
