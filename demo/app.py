import streamlit as st
import pandas as pd
import os

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

    st.image('images/lawyer.png', width=100)
    st.markdown(
        f'<div style="background-color: #add8e6; padding: 10px; margin: 10px; border-radius: 10px; display: inline-block; margin-left: 60px;">'
        f'<b>Agent:</b> Mark (Retrieveing 🧠...)<br>'
        f'<b>Retrieved:</b> There is a potential alibi for Emily during the time of the poisoning, involving a witness not yet presented in court.Mark possesses an anonymous letter received by the Thorntons, hinting at threats from an unknown source.Richard was involved in a secret business deal that might have contributed to his strained relationships.<br>'
        '</div>', unsafe_allow_html=True
    )
    # place for the reflection
    st.divider()

    st.image('images/lawyer.png', width=50)
    st.markdown(
        f'<div style="background-color: #add8e6; padding: 10px; margin: 10px; border-radius: 10px; display: inline-block; margin-left: 60px;">'
        f'<b>Agent:</b> Mark (Reflecting 🤔...)<br>'
        f'<b>Reflection: </b> <em> Emily admitted to leaving the room after the heated argument with Richard, providing a potential gap in time for the poisoning to have occurred.There is a potential alibi for Emily during the time of the poisoning, involving a witness not yet presented in court. Emily\'s financial struggles and Richard\'s infidelity may have been motives for the poisoning, but they do not definitively prove Emily\'s guilt. These details add complexity to the case and make it more intriguing for Mark to investigate further.</em>'
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

    with st.expander("Memory Before 🧠"):
        st.markdown(":green[NEW MEMORY: There is a potential alibi for Emily during the time of the poisoning, involving a witness not yet presented in court.]")
    
    
    visualize_chat_dataframes(folder_path)
    with st.expander("Memory After 🧠"):
        st.json({
            "Mark": {
                "name": "Mark",
                "memory": [
                    "There is a potential alibi for Emily during the time of the poisoning, involving a witness not yet presented in court.",
                    "Mark possesses an anonymous letter received by the Thorntons, hinting at threats from an unknown source.",
                    "Richard was involved in a secret business deal that might have contributed to his strained relationships."
                ]
            }
        })
    # TODO: handle the escape chars
    with st.expander("Story 📖"):
        st.write(f'''As the sun dipped below the horizon, Mark Turner's mind remained wide awake, illuminated by the eerie glow of the moonlight. Sifting through intricate threads of evidence, he embarked on a journey for the truth. Raw intelligence danced in his eyes, as he sat before the fireplace engulfed in the dimly-lit room.
    "Just a whisper of doubt lingered in the air, arising from Sarah Reynolds' hesitant testimony. ""I saw a man in a red tie leave the room,"" she had confided, but Mark could sense her unease. He wondered if she was holding backी"\n"
    "Mark's gaze automatically swung to his reflection in the polished glass facade, zeroing in on the deep creases that tugged at the corners of his eyes. ""We'll get to the bottom of this, Sarah,"" he assured her earlier that day, but uncertainty lurked in the shadows."\n
    "Across the bustling courtroom, Starchy-haired Emily Thorton patiently awaited her fate, her pastel gown a stark contrast to the smoky room. Her eyes, dancing with a mixture of nervous anticipation and stubborn resolve, told a compelling story of a woman falsely accused."\n
    "Her tale of a marital strife gone awry now inextricably linked to Sarah's fragmented account. Three dots connected: one unearthed secret, two shrouded truths, and a wealth of deception."\n
    "Mark knew Emily couldn't possibly have orchestrated Richard's untimely demise, but who orchestrated the web of lies? The burning question gnawed at him, desperate for an answer."\n
    "As Mark continued to sift through the intricate threads of the case, he couldn't shake the feeling that something was amiss. He needed another piece of the puzzle, a revelation that would clear the murky waters and shed light on the mystery that the moonlit night could not quite reveal.''')

if __name__ == "__main__":
    main()
