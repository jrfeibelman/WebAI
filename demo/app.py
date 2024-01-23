import streamlit as st
import pandas as pd
import os

def read_and_display_csvs(folder_path):
    # Get a list of all CSV files in the folder
    csv_files = [file for file in os.listdir(folder_path) if file.endswith('.csv')]

    # Create an empty dictionary to store dataframes
    dfs = {}

    # Loop through each CSV file, read it into a dataframe, and store it in the dictionary
    for file in csv_files:
        file_path = os.path.join(folder_path, file)
        df_name = os.path.splitext(file)[0]  # Use the filename without extension as the dataframe name
        dfs[df_name] = pd.read_csv(file_path)
    return dfs

    # Display the dataframes
    # for df_name, df in dfs.items():
    #     st.subheader(f"DataFrame: {df_name}")
    #     st.write(df)

# to render the chat as a chat bubbles
def render_chat(chat_df: pd.DataFrame):
    # Dictionary mapping speakers to image paths
    speaker_images = {
        'Mark': 'images/lawyer.png',  # TODO: change this to be configurable
        'Sarah': 'images/biz_women.jpeg',
        'Sarah Reynolds': 'images/biz_women.jpeg',
        'Emily Thorton': 'images/biz_women.jpeg',
        'Mark Turner': 'images/lawyer.png'
    }
    
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

def visualize_chat_dataframes(folder_path):
    # find all csv files
    df_list = read_and_display_csvs(folder_path)

    # render each chat as an expander
    for name, chat_df in df_list.items():
        with st.expander(f"Chat {name}"):
            # Display each row of each chat as a bubble with an image
            render_chat(chat_df)
        
def main():
    st.title("Mythos")
    folder_path = "dialogues/"
    
    visualize_chat_dataframes(folder_path)

if __name__ == "__main__":
    main()
