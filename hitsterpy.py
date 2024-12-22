import qrcode
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from matplotlib.backends.backend_pdf import PdfPages
from PIL import Image
import numpy as np
import io

from spotify_get_list import playlist_to_df

# ------------------------------------------------------------
def generate_qr_code(data,border):
    """
    - Takes a string
    - Generates QR code image
    """
    qr = qrcode.QRCode(
        version=1,  # Adjust version for size
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=border,
    )
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black",
                        back_color="white")
    return img

# ------------------------------------------------------------
def create_qr_code_grid(data_list=['Test'], rows=5, cols=4, border=6):
    """
    - Takes a data list
    - Creates a grid of QR-codes
    - Returns matplotlib fig
    """
    # Create a list to hold the individual QR code images
    qr_code_images = []

    for data in data_list:
        qr_code_images.append(generate_qr_code(data,border))

    # Calculate the size of each individual QR code
    width, height = qr_code_images[0].size

    # Calculate the total width and height of the grid
    grid_width = cols * width
    grid_height = rows * height

    # Create a blank white image for the grid
    grid_image = Image.new("RGB", (grid_width, grid_height), "white")

    # Paste each QR code image into the grid
    for i in range(rows):
        for j in range(cols):
            index = i * cols + j
            if index>=len(data_list):
                break

            # ->->-> Filling from left to right:
            # grid_image.paste(qr_code_images[index], (j * width, i * height))

            # <-<-<- Filling from right to left:
            grid_image.paste(qr_code_images[index], ((cols-j-1) * width, i * height))

    fig, ax = plt.subplots()

    ax.imshow(grid_image)

    # --- ADD CUT-OUT-HELPER RECTANGLES TO IMAGE
    xmin = ax.get_xlim()[0]
    xmax = ax.get_xlim()[1]
    ymin = ax.get_ylim()[0]
    ymax = ax.get_ylim()[1]

    rect_width = (xmax-xmin)/cols
    rect_height = (ymin-ymax)/rows

    for i in range(rows):
        for j in range(cols):
            index = i * cols + j
            # if index>=len(data_list):
            #     break
            # Add cut-out helper rectangles
            ax.add_patch(Rectangle((j*rect_width, i*rect_height),width=rect_width,height=rect_height,
                                   fill=False,
                                   linewidth=0.5,
                                   linestyle="--"))

    # --- CLEAN PLOT
    # Remove x and y ticks and labels
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_xticklabels([])
    ax.set_yticklabels([])

    # Return matplotlib figure
    return fig

# ------------------------------------------------------------
def linebreaker(txtstr,Lmax=40,joined=False):
    """
    - Takes string input
    - Returns either
      - List of strings not longer than Lmax
      - Single string with linebreaks (\n) after every Lmax
    """
    # Initialize list for line-wise substrings
    breakstr = []

    str_elemens = txtstr.split()

    if(max([len(substr) for substr in str_elemens]))>Lmax:
        return "! LINEBREAK-ERROR !"

    # Go through text
    for _ in range(len(txtstr)):
        # Split text into words (split at empty-space)
        str_elemens = txtstr.split()

        # Go through words
        for i,_ in enumerate(str_elemens):
            # Rebuild substring from beginning
            # to word number i
            substr = " ".join(str_elemens[:i+1])
            # Check if rebuilt substring fits into max. length
            if len(substr)>Lmax:
                # If substr is too long, store it with one less word
                substr = " ".join(str_elemens[:i])
                # Store remaining text as new input text
                txtstr = " ".join(str_elemens[i:])
                # Leave subloop
                break
        # Append current substring to line-wise list
        breakstr.append(substr)
        # If substring and remaining text are the same, work is done
        if(len(substr)==len(txtstr)):
            break    
    
    if joined:
        # Join substrings into single string with linebreaks
        res = "".join([substr + "\n" for substr in breakstr])
    else:
        # Store array of substrings
        res = breakstr

    return res

# ------------------------------------------------------------
def create_annotation_grid(fontsize=4, data_list=[['track','artist','year']], rows=4, cols=4):
    """
    - Creates annotation grid from list of track-artist-year lists
    - Returns matplotlib figure
    """
    # Create new figure
    fig, ax = plt.subplots()

    # Create a grid of empty strings
    grid_data = [['' for _ in range(cols)] for _ in range(rows)]

    # Populate the grid with data
    for i in range(rows):
        for j in range(cols):
            index = i * cols + j
            if index>=len(data_list):
                break
            grid_data[i][j] = data_list[i * cols + j]

    # Create a heatmap with no data (just for grid structure)
    heatmap = ax.imshow(np.ones((rows, cols)),
                        cmap='gray',
                        vmin=0,
                        vmax=1,
                        extent=[0, cols, rows, 0]
                        )

    # Annotate each cell with centered text
    styles = ['italic','normal','normal']
    weights = ['normal','bold','normal']
    for i in range(rows):
        for j in range(cols):
            index = i * cols + j
            # if index>=len(data_list):
            #     break
            # Add annotations
            for k,substr in enumerate(grid_data[i][j]):
                linepitch = 0.26
                ax_txt = linebreaker(substr,Lmax=18,joined=True)
                ax.text(j+0.5, i+0.5 + k*linepitch - linepitch/1.5, ax_txt,
                        ha='center',
                        va='center',
                        color='black',
                        fontsize=fontsize,
                        weight=weights[k],
                        style=styles[k])
            # Add cut-out helper rectangles
            ax.add_patch(Rectangle((j, i),width=1,height=1,
                                   fill=False,
                                   linewidth=0.5,
                                   linestyle="--"))

    # Remove x and y ticks and labels
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_xticklabels([])
    ax.set_yticklabels([])

    # Return matplotlib figure
    return fig

# ------------------------------------------------------------
def page_info(index=0, fontsize=6):
    """
    - Creates little annotation at the top of the page
    """
    plt.annotate("Page " + ("%04d" % index),
                 (0,0),
                 va='bottom',
                 fontsize=fontsize)

# ------------------------------------------------------------
def hitster_from_playlist(playlist_url:str):
    # Get playlist DataFrame from Spotify-URL
    playlist_df = playlist_to_df(playlist_url)
    # Write necessary info to songlist_df
    songlist_df = playlist_df[['track_name','artist_name','album_release_date','track_url']]
    # Only keep year of release date
    songlist_df.loc[:,'album_release_date'] = songlist_df['album_release_date'].dt.year
    # Rename columns so it fit's with remaining code
    songlist_df.columns = ['Title','Artist','Year','Link']
    
    # Grid-size
    rows = 5
    cols = 4
    border = 6

    # --- FIGURE-LIST PREP
    figs =[]

    step = rows*cols
    for i in range(1+songlist_df.shape[0]//step):
        # Extract sublist per page
        sublist = songlist_df.iloc[i*step:(i+1)*step,:]
        
        # Create QR-Codes:
        create_qr_code_grid(list(sublist['Link']), rows, cols, border)

        # Add page info:
        page_info(index=i)

        # Get matplotlib-figure and append to list of figures
        fig_qr = plt.gcf()
        figs.append(fig_qr)

        # --- ANNOTATIONS
        annotations = sublist[['Title','Artist','Year']].values.astype(str).tolist()
        # Create Annotations:
        create_annotation_grid(data_list=list(annotations),
                            fontsize=12,
                            rows=rows,
                            cols=cols)

        # Add page info:
        page_info(index=i)

        # Get matplotlib-figure and append to list of figures
        fig_annot = plt.gcf()
        figs.append(fig_annot)

    # --- MULTIPAGE EXPORT local
    # with PdfPages("export/test_export.pdf") as pdf:
    #     for fig in figs:
    #         fig.set_size_inches((8.27, 11.69))
    #         fig.tight_layout(pad=1.5)
    #         # Saves the current figure to a new page
    #         pdf.savefig(fig,
    #                     dpi=300,
    #                     orientation='portrait') 
    #         #close the figure after saving to prevent memory issues
    #         plt.close(fig)

    # --- MULTIPAGE EXPORT online
    with io.BytesIO() as output:  # Use BytesIO for in-memory PDF
        with PdfPages(output, metadata={'Title': 'Multipage PDF Example', 'Author': 'Streamlit App'}) as pdf:
            for fig in figs:
                fig.set_size_inches((8.27, 11.69))
                fig.tight_layout(pad=1.5)
                # Saves the current figure to a new page
                pdf.savefig(fig,
                            dpi=300,
                            orientation='portrait')
                # Close the figure to prevent memory leaks
                plt.close(fig)
        return output.getvalue()