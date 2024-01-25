import streamlit as st
import pandas as pd
import os
import json
import html

def read_json(f_path):
    return json.loads(open(f_path).read())

def render_html(raw_string):
    escaped_string = html.escape(raw_string)
    return escaped_string

def read_and_display_csvs(folder_path):
    # Get a list of all CSV files in the folder
    csv_files = sorted([file for file in os.listdir(folder_path) if file.endswith('.csv')]) # i want to see 5 before 6

    # Create an empty dictionary to store dataframes
    dfs = {}

    # Loop through each CSV file, read it into a dataframe, and store it in the dictionary
    for file in csv_files:
        file_path = os.path.join(folder_path, file)
        df_name = os.path.splitext(file)[0]  # Use the filename without extension as the dataframe name
        dfs[df_name] = pd.read_csv(file_path)
    return dfs

# to render the chat as a chat bubbles
def render_chat(chat_df: pd.DataFrame):
    # retrieve context before chat
    st.image('images/lawyer.png', width=100)
    context_raw = "There is a potential alibi for Emily during the time of the poisoning, involving a witness not yet presented in court.Mark possesses an anonymous letter received by the Thorntons, hinting at threats from an unknown source.Richard was involved in a secret business deal that might have contributed to his strained relationships."
    context_html = render_html(context_raw)
    st.markdown(
        f'<div style="background-color: #add8e6; padding: 10px; margin: 10px; border-radius: 10px; display: inline-block; margin-left: 60px;">'
        f'<b>Agent:</b> Mark (Retrieveing 🧠...)<br>'
        f'<b>Retrieved Context:</b> {context_html}<br>'
        '</div>', unsafe_allow_html=True
    )

    st.divider()
    # Dictionary mapping speakers to image paths
    speaker_images = {
        'Mark': 'images/lawyer.png',  # TODO: change this to be configurable
        'Sarah': 'images/biz_women.png',
        'Sarah Reynolds': 'images/biz_women.png',
        'Emily Thorton': 'images/biz_women.png',
        'Mark Turner': 'images/lawyer.png'
    }
    
    for index, row in chat_df.iterrows():
            # Display speaker's image if available
            if row['speaker'] in speaker_images:
                st.image(speaker_images[row['speaker']], width=100)
            st.markdown(
                f'<div style="background-color: #F0F0F0; padding: 10px; margin: 10px; border-radius: 10px; display: inline-block; margin-left: 60px;">'
                f'<b>Agent:</b> {row["speaker"]}<br>'
                f'<b>Utterance:</b> {row["utterance"]}'
                '</div>', unsafe_allow_html=True
            )

 
    # place for the reflection
    st.divider()

    st.image('images/lawyer.png', width=50)
    raw_string = "The anonymous letter could provide significant insight into Richard's"
    raw_string = read_json('mark_reflection1.json')
    escaped_string = ''.join([render_html(a) for a in raw_string])
    st.markdown(
        f'<div style="background-color: #add8e6; padding: 10px; margin: 10px; border-radius: 10px; display: inline-block; margin-left: 60px;">'
        f'<b>Agent:</b> Mark (Reflecting 🤔...)<br>'
        f'<b>Reflection: </b> <em> {escaped_string} </em>'
        '</div>', unsafe_allow_html=True
    )


def visualize_chat_dataframes(folder_path):
    # find all csv files
    df_list = read_and_display_csvs(folder_path)

    # render each chat as an expander
    for name, chat_df in df_list.items():
        with st.expander(f"Chat {name} 💬"):
            st.subheader("Mark is helping Sarah prepare for taking the stand")
            # Display each row of each chat as a bubble with an image
            render_chat(chat_df)
        
def main():
    st.title("Mythos")
    st.header("Shadows of Deceit")
    folder_path = "test_dialogues/"
    # memory_before_path = "memory_before.json"
    # memory_before = json.loads(open(memory_before_path).read())
    # mark_facts = [
    # "Richard had business rivals who might have had motives to harm him.",
    # "There is a potential alibi for Emily during the time of the poisoning, involving a witness not yet presented in court.",
    # "Inconsistencies exist in the initial police investigation, including gaps in the timeline and overlooked potential suspects.",
    # "Richard was involved in a secret business deal that might have contributed to his strained relationships.",
    # "Mark possesses an anonymous letter received by the Thorntons, hinting at threats from an unknown source."
    # ]
    # mark_memory_after = json.loads(open('mark_facts_after.json').read())
    # mark_memory_after = read_json('mark_facts_after.json')

    to_visualize = read_json('actually_done.json')
    print(to_visualize.keys())
    # print(to_visualize.keys())
    ###### --------------MEMORY BEFORE--------------######
    mark_initial_memory = to_visualize['mark_inital_memory']
    print(mark_initial_memory)
    with st.expander("Mark's Memory Before 🧠"):
        for i, fact in enumerate(mark_initial_memory):
            st.markdown(f"{i}: {fact}")
        # st.write(mark_initial_memory)
        # st.markdown(":green[NEW MEMORY: There is a potential alibi for Emily during the time of the poisoning, involving a witness not yet presented in court.]")
    
    #### --------------DIALOGUES--------------######
    # visualize_chat_dataframes(folder_path)
    dialogue1 = to_visualize['mark_emily_dialogue']
    dialogue2 = to_visualize['mark_emily_dialogue_2']
    reflection = '\n'.join(to_visualize['mark_reflection'])
    act = to_visualize['mark_next_steps']
    mark_memory_after = to_visualize['mark_new_memory']

    with st.expander("Mark's Dialogue with Sarah 🗣"):
        speaker_images = {
            'Mark': 'images/lawyer.png',  # TODO: change this to be configurable
            'Sarah': 'images/biz_women.png',
            'Sarah Reynolds': 'images/biz_women.png',
            'Emily Thorton': 'images/biz_women.png',
            'Mark Turner': 'images/lawyer.png'
        }
        for line in dialogue1:
            speaker = line["speaker"]
            utterance = line["utterance"]
            if speaker in speaker_images:
                st.image(speaker_images[speaker], width=100)
            st.markdown(
                f'<div style="background-color: #F0F0F0; padding: 10px; margin: 10px; border-radius: 10px; display: inline-block; margin-left: 60px;">'
                f'<b>Agent:</b> {speaker}<br>'
                f'<b>Utterance:</b> {utterance}'
                '</div>', unsafe_allow_html=True
            )
        st.divider()
        st.subheader('Reflection')
        st.image(speaker_images[speaker], width=100)
        st.markdown(
        f'<div style="background-color: #add8e6; padding: 10px; margin: 10px; border-radius: 10px; display: inline-block; margin-left: 60px;">'
        f'<b>Agent:</b> Mark (Reflecting 🤔...)<br>'
        f'<b>Reflection: </b> <em> {reflection} </em>'
        f'<b>{act} </b>'
        '</div>', unsafe_allow_html=True
        )
    # with st.expander("Mark's Dialogue with Emily 🗣"):
    #     speaker_images = {
    #         'Mark': 'images/lawyer.png',  # TODO: change this to be configurable
    #         'Sarah': 'images/biz_women.png',
    #         'Sarah Reynolds': 'images/biz_women.png',
    #         'Emily Thorton': 'images/biz_women.png',
    #         'Mark Turner': 'images/lawyer.png'
    #     }
    #     for line in dialogue2:
    #         speaker = line["speaker"]
    #         utterance = line["utterance"]
    #         if speaker in speaker_images:
    #             st.image(speaker_images[speaker], width=100)
    #         st.markdown(
    #             f'<div style="background-color: #F0F0F0; padding: 10px; margin: 10px; border-radius: 10px; display: inline-block; margin-left: 60px;">'
    #             f'<b>Agent:</b> {speaker}<br>'
    #             f'<b>Utterance:</b> {utterance}'
    #             '</div>', unsafe_allow_html=True
    #         )
    
    #### --------------MEMORY AFTER--------------######
    with st.expander("Memory After 🧠"):
        for i, fact in enumerate(mark_memory_after[:3]+mark_memory_after[6:]):
            if i > 2:
                fact_string = f":green[{i}: NEW MEMORY: {fact}]"
            else:
                fact_string = f"{i}: {fact}"
            st.markdown(fact_string)
    
if __name__ == "__main__":
    main()
