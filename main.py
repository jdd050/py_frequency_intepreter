import tkinter as tk
import os
from parse_audio import ParseAudio
from tkinter.filedialog import askopenfilename, askdirectory
from tkinter.messagebox import showinfo

if __name__ == "__main__":
    global fileType
    # Audio parser class instance
    parse_funcs = ParseAudio()
    # get the directory for the video file
    showinfo("Input File Prompt", "Please provide the path to the video/audio file you would like to use.")
    INPUT_PATH = askopenfilename()
    while not os.path.isfile(INPUT_PATH):
        print("Invalid file path provided. Try again")
        INPUT_PATH = askopenfilename()
    
    
    # determine if file is video or audio
    file_type = parse_funcs.determine_file_type(INPUT_PATH)
    if "video" in file_type:
        fileType = "video"
    elif "audio" in file_type:
        fileType = "audio"
    else:
        fileType = "invalid"
        

    # also ask for where to save the extracted audio
    showinfo("Audio File Prompt", "Please provide the directory you would like to save the temporary audio file in.")
    AUDIO_DIRECTORY = askdirectory()
    while not os.path.isdir(AUDIO_DIRECTORY):
        print("Invalid audio save path provided. Please try again")
        AUDIO_DIRECTORY = askdirectory()
    AUDIO_PATH = AUDIO_DIRECTORY
    print(AUDIO_PATH)
    
    # parse audio
    if fileType == "video":
        AUDIO_PATH = os.path.join(AUDIO_DIRECTORY, "extracted_audio.wav")
        parse_funcs.extract_audio_from_video(INPUT_PATH, AUDIO_PATH)
        raw_data = parse_funcs.plot_time_domain(AUDIO_PATH)
    elif fileType == "audio":
        raw_data = parse_funcs.plot_time_domain(parse_funcs.convert_audio(INPUT_PATH, AUDIO_PATH))
    

    with open("time_frequency_data.txt", 'w') as f:
        for x, y in raw_data.items():
            f.write(f"[{x}, {y}]\n")
        f.close()

