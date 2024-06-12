import numpy as np
import matplotlib.pyplot as plt
import subprocess
import os
from moviepy.editor import VideoFileClip
from scipy.io import wavfile
from scipy.fft import fft, fftfreq
from scipy.signal import spectrogram

class ParseAudio:
    def __init__(self):
        self.ffmpeg_path = os.path.abspath("./ffmpeg/ffmpeg.exe")
        self.ffprobe_path = os.path.abspath("./ffmpeg/ffprobe.exe")
        self.ffplay_path = os.path.abspath("./ffmpeg/ffplay.exe")
    
    def determine_file_type(self, input_path) -> str:
        result = subprocess.run(
                                [self.ffprobe_path, "-loglevel", "error", "-show_entries", "stream=codec_type", "-of", "csv=p=0", input_path], 
                                capture_output=True, 
                                text=True
                                )
        return result.stdout.strip()
     
    def extract_audio_from_video(self, video_path, audio_path) -> None:
        codec='pcm_s16le'
        video = VideoFileClip(video_path)
        video.audio.write_audiofile(audio_path, codec=codec)
        return None
    
    # converts audio file to wav
    def convert_audio(self, original_audio_path, new_audio_path) -> str:
        new_audio_path = os.path.join(new_audio_path, "extracted_audio.wav")
        subprocess.call([self.ffmpeg_path, "-i", original_audio_path, new_audio_path])
        return new_audio_path
        
    # plots the audio data as a sinusoidal function of time
    # returns all data in the format [time_values, audio_data]
    def plot_time_domain(self, audio_path) -> dict:
        sample_rate, audio_data = wavfile.read(audio_path)
        
        # check if audio is stereo
        if audio_data.ndim > 1:
            audio_data = audio_data[:, 0]
        
        # generate time values
        duration = len(audio_data) / sample_rate
        time_values = np.linspace(0, duration, len(audio_data))
        
        # create the plot for the time-domain signal
        plt.figure(figsize=(10, 8))
        plt.subplot(2, 1, 1)  # 2 rows, 1 column, first plot
        plt.plot(time_values, audio_data)
        plt.xlabel("Time (seconds)")
        plt.ylabel("Amplitude")
        plt.title("Time-Domain Signal of Audio File")
        
        # Parameters for windowing
        window_size = int(sample_rate * 0.05)  # 50 ms window
        hop_size = int(sample_rate * 0.025)  # 25 ms hop
        num_windows = (len(audio_data) - window_size) // hop_size
        
        # Prepare the frequency-time data
        time_freq_data = []
        
        for i in range(num_windows):
            start = i * hop_size
            end = start + window_size
            windowed_data = audio_data[start:end]
            
            # Perform FFT on the windowed data
            fft_result = fft(windowed_data)
            freqs = fftfreq(window_size, d=1/sample_rate)
            
            # Get the positive frequencies
            positive_freqs = freqs[:window_size // 2]
            magnitudes = np.abs(fft_result[:window_size // 2])
            
            # Find the dominant frequency
            dominant_freq = positive_freqs[np.argmax(magnitudes)]
            time_point = time_values[start]
            
            time_freq_data.append((time_point, dominant_freq))
        
        # Unzip the time-frequency data
        time_points, dominant_freqs = zip(*time_freq_data)
        
        # Plot the frequency-time data
        plt.subplot(2, 1, 2)  # 2 rows, 1 column, second plot
        plt.plot(time_points, dominant_freqs)
        plt.xlabel("Time (seconds)")
        plt.ylabel("Frequency (Hz)")
        plt.title("Dominant Frequency Over Time")
        
        plt.tight_layout()
        plt.show()
        
        # Create the raw_data dictionary
        if len(time_values) == len(audio_data):
            raw_data = {time_values[i]: audio_data[i] for i in range(len(time_values))}
        else:
            raw_data = {}
        
        return raw_data
    
    # returns all data in the format [sample_rate, audio_data, frequencies, times, STFT]
    # STFT = Short-Time Fourier Transform
    def plot_spectrogram(self, audio_path) -> list:
        sample_rate, audio_data = wavfile.read(audio_path)
        
        # check if audio is stereo
        if audio_data.ndim > 1:
            audio_data = audio_data[:, 0]
        
        frequencies, times, STFT = spectrogram(audio_data, sample_rate)
        
        # set up the plot
        plt.figure(figsize=(10, 6))
        plt.pcolormesh(times, frequencies, 10 * np.log10(STFT), shading="gouraud")
        plt.ylabel("Frequency (Hz)")
        plt.xlabel("Time (sec)")
        plt.title("Spectrogram")
        plt.colorbar(label="Intensity (dB)")
        plt.show()
        return [sample_rate, audio_data, frequencies, times, STFT]