import streamlit as st
from hitsterpy import hitster_from_playlist

st.title("MUSIC QUIZ GENERATOR")

"""
---
### Paste a Spotify Playlist URL below

Example:

``https://open.spotify.com/playlist/7vMHiyFxMMV7PshlyUuQw8?si=2fbc4e3490dd4736``
"""

playlist_url = st.text_input(label='playlist_url',
                             label_visibility='hidden')

if st.button("Generate PDF"):
    st.write("PDF is being generated... This may take a minute...")
    pdf_bytes = hitster_from_playlist(playlist_url)
    if pdf_bytes:
        st.download_button(
            label="Download PDF",
            data=pdf_bytes,
            file_name="musicquiz_export.pdf",
            mime="application/pdf",
        )
    else:
        st.write("No plots generated.")

"""
---
### How it works

1. Open a Spotify playlist you want to use for your quiz.
2. Click the 3-dots symbol and choose *share*.
3. Click *Copy link to playlist*
4. Paste the link in the text-field above and click "Generate PDF".
5. After the PDF is generated, a download button will appear.

"""