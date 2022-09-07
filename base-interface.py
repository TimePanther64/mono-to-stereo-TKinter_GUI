import os
import shutil
import librosa
import sox
import concurrent.futures as cf
import threading as td
import tkinter as tk
import numpy as np
from tkinter import Toplevel, filedialog as fd, ttk
from pathlib import Path
from pydub import AudioSegment
from pydub.playback import play
from pydub.silence import split_on_silence
from math import *
from glob import glob
from scipy.signal import butter, lfilter

class guiApp(object):
  def __init__(self):
    self.root = tk.Tk()
    self.root.tk.call('wm', 'iconphoto', self.root._w, tk.PhotoImage(file='./headphones.png'))
    self.root.geometry("600x600")
    self.root.title("Audio Processing Software")
    self.style = ttk.Style().theme_use("xpnative")

    self.tabControl = ttk.Notebook(self.root)
    self.tab1 = ttk.Frame(self.tabControl)
    self.tab2 = ttk.Frame(self.tabControl)
    self.tab3 = ttk.Frame(self.tabControl)
    self.tabControl.add(self.tab1, text='Ambisonic Conversion')
    self.tabControl.add(self.tab2, text='Audio Enhancement')
    self.tabControl.add(self.tab3, text='Audio Trimmer')
    self.tabControl.place(relx=0.025, rely=0.025, relheight=0.95, relwidth=0.95)

    self.theme_frame_single = ttk.LabelFrame(self.tab1, text="Single File Coversion")
    self.theme_frame_single.place(relx=.125, rely=.03, relwidth=.75, relheight=.5)

    self.theme_frame_batch = ttk.LabelFrame(self.tab1, text="Batch File Conversion")
    self.theme_frame_batch.place(relx=.125, rely=.55, relwidth=.75, relheight=.25)

    self.file_label = ttk.Label(self.tab1, text="Select a file to convert: ")
    self.file_label.place(relx=.2, rely=.125)

    self.select_button = ttk.Button(self.tab1, text="Select", command=lambda: self.select_file(1))
    self.select_button.place(relx=.55, rely=.125)

    self.select_label = ttk.Label(self.tab1, text="You have selected: ")
    self.select_label.place(relx=.2, rely=.255)

    self.show_label = ttk.Label(self.tab1, text="")
    self.show_label.place(relx=.5525, rely=.255)

    self.convert_button = ttk.Button(self.tab1, text="Convert", command=self.convert_file)
    self.convert_button.place(relx=.3, rely=.4)

    self.play_button = ttk.Button(self.tab1, text='Play', command=lambda: self.play_file(0))
    self.play_button.place(relx=.55, rely=.4)

    self.folder_label = ttk.Label(self.tab1, text="Select the folder(s) you wish to \nconvert: ")
    self.folder_label.place(relx=.2, rely=.65)

    self.batch_convert_button = ttk.Button(self.tab1, text="Batch Convert", command=self.start_batch_convert)
    self.batch_convert_button.place(relx=.575, rely=.65, relwidth=.25)

    self.quitButton1 = ttk.Button(self.tab1, text="Quit", command=self.root.quit)
    self.quitButton1.place(relx=.738, rely=.85)

    self.theme_frame_modify = ttk.LabelFrame(self.tab2, text="Modify Audio File")
    self.theme_frame_modify.place(relx=.125, rely=.03, relwidth=.75, relheight=.775)

    self.current_value_reverb = tk.IntVar()
    self.current_value_treble = tk.IntVar()
    self.current_value_bass = tk.IntVar()
    self.current_value_volume = tk.IntVar()

    self.slider_label_reverb = ttk.Label(self.tab2, text='Reverb:')
    self.slider_label_reverb.place(relx=.2, rely=.375)
    self.slider_reverb = ttk.Scale(self.tab2, from_=15, to=30, orient='horizontal', command=self.slider_changed_reverb, variable=self.current_value_reverb, length=150)
    self.slider_reverb.place(relx=.4, rely=.375)
    self.value_label_reverb = ttk.Label(self.tab2, text=self.current_value_reverb.get())
    self.value_label_reverb.place(relx=.7, rely=.375)

    self.slider_label_treble = ttk.Label(self.tab2, text='Treble:')
    self.slider_label_treble.place(relx=.2, rely=.45)
    self.slider_treble = ttk.Scale(self.tab2, from_=2, to=12, orient='horizontal', command=self.slider_changed_treble, variable=self.current_value_treble, length=150)
    self.slider_treble.place(relx=.4, rely=.45)
    self.value_label_treble = ttk.Label(self.tab2, text=self.current_value_treble.get())
    self.value_label_treble.place(relx=.7, rely=.45)

    self.slider_label_bass = ttk.Label(self.tab2, text='Bass:')
    self.slider_label_bass.place(relx=.2, rely=.525)
    self.slider_bass = ttk.Scale(self.tab2, from_=2, to=12, orient='horizontal', command=self.slider_changed_bass, variable=self.current_value_bass, length=150)
    self.slider_bass.place(relx=.4, rely=.525)
    self.value_label_bass = ttk.Label(self.tab2, text=self.current_value_bass.get())
    self.value_label_bass.place(relx=.7, rely=.525)

    self.slider_label_volume = ttk.Label(self.tab2, text="Volume:")
    self.slider_label_volume.place(relx=.2, rely=.6)
    self.slider_volume = ttk.Scale(self.tab2, from_=-36, to=36, orient='horizontal', command=self.slider_changed_volume, variable=self.current_value_volume, length=150)
    self.slider_volume.place(relx=.4, rely=.6)
    self.value_label_volume = ttk.Label(self.tab2, text=self.current_value_volume.get())
    self.value_label_volume.place(relx=.7, rely=.6)

    self.file_label_modify = ttk.Label(self.tab2, text="Select a file to modify: ")
    self.file_label_modify.place(relx=.2, rely=.125)

    self.select_button_modify = ttk.Button(self.tab2, text="Select", command=lambda: self.select_file(0))
    self.select_button_modify.place(relx=.55, rely=.125)

    self.select_label_modify = ttk.Label(self.tab2, text="You have selected: ")
    self.select_label_modify.place(relx=.2, rely=.25)

    self.show_label_modify = ttk.Label(self.tab2, text="")
    self.show_label_modify.place(relx=.525, rely=.25)

    self.modifyButton = ttk.Button(self.tab2, text="Modify", command=lambda: self.modify_volume(self.current_value_volume.get()))
    self.modifyButton.place(relx=.3, rely=.7)

    self.play_button2 = ttk.Button(self.tab2, text="Play", command=lambda: self.play_file(1))
    self.play_button2.place(relx=.55, rely=.7)

    self.quitButton2 = ttk.Button(self.tab2, text="Quit", command=self.root.quit)
    self.quitButton2.place(relx=.738, rely=.85)

    self.theme_frame_silence = ttk.LabelFrame(self.tab3, text="Silence Detection")
    self.theme_frame_silence.place(relx=.125, rely=.03, relwidth=.75, relheight=.5)

    self.file_label2 = ttk.Label(self.tab3, text="Select a file containing ads: ")
    self.file_label2.place(relx=.2, rely=.125)

    self.select_button2 = ttk.Button(self.tab3, text="Select", command=lambda: self.select_file(2))
    self.select_button2.place(relx=.55, rely=.125)

    self.select_label2 = ttk.Label(self.tab3, text="You have selected: ")
    self.select_label2.place(relx=.2, rely=.255)

    self.show_label2 = ttk.Label(self.tab3, text="")
    self.show_label2.place(relx=.5525, rely=.255)

    self.convert_button2 = ttk.Button(self.tab3, text="Remove Ads", command=self.ad_removal)
    self.convert_button2.place(relx=.3, rely=.4)

    self.play_button2 = ttk.Button(self.tab3, text="Play", command=lambda: self.play_file(0))
    self.play_button2.place(relx=.55, rely=.4)

    self.quitButton3 = ttk.Button(self.tab3, text="Quit", command=self.root.quit)
    self.quitButton3.place(relx=.738, rely=.575)
  
  global file_path
  file_path = ''
  global des
  des = ''

  def slider_changed_reverb(self, event):
    self.value_label_reverb.config(text=self.current_value_reverb.get())

  def slider_changed_treble(self, event):
    self.value_label_treble.config(text=self.current_value_treble.get())

  def slider_changed_bass(self, event):
    self.value_label_bass.config(text=self.current_value_bass.get())

  def slider_changed_volume(self, event):
    self.value_label_volume.config(text=self.current_value_volume.get())

  def calc_pan(self, index):
    return cos(radians(index))

  def select_file(self, value):

    global file_path
    file_path = fd.askopenfilename(initialdir="C:/", title="Select a file: ", filetypes=[('WAV file', '*.wav'), ('MP3 file', '*.mp3'), ('All files', '*.*')])
    global des
    des = ''
    if file_path != '':
      global name
      global ext
      name = Path(str(file_path)).stem
      ext = Path(str(file_path)).suffix
      if value == 0:
        self.show_label.config(text=name+ext)
        self.show_label2.config(text='')
        self.show_label_modify.config(text='')
      elif value == 1:
        self.show_label.config(text='')
        self.show_label2.config(text='')
        self.show_label_modify.config(text=name+ext)
      else:
        self.show_label.config(text='')
        self.show_label2.config(text=name+ext)
        self.show_label_modify.config(text='')

  def convert_file(self):
    interval = 0.175 * 1000
 
    song = AudioSegment.from_file(file=file_path, format=ext[1:])
    song_inverted = song.invert_phase()
    song.overlay(song_inverted)

    splitted_song = []
    song_start_point = 0

    while song_start_point+interval < len(song):
        splitted_song.append(song[song_start_point:song_start_point+interval])
        song_start_point += interval

    if song_start_point < len(song):
        splitted_song.append(song[song_start_point:])

    ambisonics_song = splitted_song.pop(0)
    phase_index = 0
    for segment in splitted_song:
        phase_index += 5
        segment = segment.pan(self.calc_pan(phase_index))
        ambisonics_song = ambisonics_song.append(segment, crossfade=interval/35)

    global des
    des = str(fd.asksaveasfilename(title="Where would you want to save the file: ", filetypes=[('WAV file', '*.wav'), ('MP3 file', '*.mp3'), ('All files', '*.*')]))+ext
    self.show_label.config(text=Path(str(des)).stem+Path(str(des)).suffix)

    out_song = open(des, 'wb')
    ambisonics_song.export(out_song, format=ext[1:])

  def start_batch_convert(self):
    td.Thread(target=self.batch_convert).start()

  def batch_convert(self):
    batch = mProcess()
    batch.batch_convert()
    top = Toplevel(self.root)
    top.title("Confirmation")
    top.geometry("400x125")
    top_label = ttk.Label(top, text="All files have been converted!!!", font=("Times New Roman", 14))
    top_label.place(relx=.15, rely=.15)
    top_button = ttk.Button(top, text="OKAY", command=top.quit)
    top_button.place(relx=.35, rely=.55)

  def play_file(self, value):
    if file_path == '' and des == '':
      audiofile = fd.askopenfilename(initialdir="C:/", title="Select a file: ", filetypes=[('WAV file', '*.wav'), ('MP3 file', '*.mp3'), ('All files', '*.*')])
    elif file_path != ''and des == '':
      audiofile = file_path
    elif des != '':
      audiofile = des
    
    ext = Path(str(audiofile)).suffix

    conv_file = AudioSegment.from_file(file=audiofile, format=ext[1:])
    play(conv_file)


  def modify_volume(self, value):
    song = AudioSegment.from_file(file=file_path, format=ext[1:])
    song += value
    global des
    des = str(fd.asksaveasfilename(title="Where would you want to save the file: ", filetypes=[('WAV file', '*.wav'), ('MP3 file', '*.mp3'), ('All files', '*.*')]))+ext
    self.show_label_modify.config(text=Path(str(des)).stem+Path(str(des)).suffix)
    out_song = open(des, 'wb')
    song.export(out_song, format=ext[1:])

  def ad_removal(self):
    global file_path
    song = AudioSegment.from_mp3(file_path)

    section = split_on_silence(song, min_silence_len = 2500, silence_thresh = -22)

    for i, sec in enumerate(section):

        if len(sec) >= 25000:
          silence = AudioSegment.silent(duration=1500)
          sec = silence + sec + silence
          sec.export("modified.mp3".format(i), bitrate = "192k", format = "mp3")
    
    self.show_label2.config(text='modified.mp3')

class mProcess(object):

  def calc_pan(self, index):
    return cos(radians(index))

  def ignore_files(self, dir, files):
    return [f for f in files if os.path.isfile(os.path.join(dir, f))]

  def batch_convert(self):
    folder_path = fd.askdirectory(initialdir='C:/', title="Select the folder containing the audio files: ")
    folder_path_len = len(folder_path)
    audio_files = glob(folder_path+'/*/*.*')

    shutil.copytree(folder_path, folder_path+'_conv', ignore=self.ignore_files)

    with cf.ProcessPoolExecutor() as exe:  
      converted_ambisonics = exe.map(self.convert_file_batch, audio_files)

    audio_tuple = zip(converted_ambisonics, audio_files)
    
    for audio in audio_tuple:
      exte = Path(str(audio[1])).suffix
      ini = os.path.splitext(audio[1])[0]
      ini = ini[:folder_path_len] + '_conv' + ini[folder_path_len:]
      des = ini+'_conv'+exte

      out_song = open(des, 'wb')
      audio[0].export(out_song, format=exte[1:])    

  def convert_file_batch(self, audio_file):
    interval = 0.175 * 1000
    exte = Path(str(audio_file)).suffix
    song = AudioSegment.from_file(file=audio_file, format=exte[1:])
    song_inverted = song.invert_phase()
    song.overlay(song_inverted)

    splitted_song = []
    song_start_point = 0

    while song_start_point+interval < len(song):
        splitted_song.append(song[song_start_point:song_start_point+interval])
        song_start_point += interval

    if song_start_point < len(song):
        splitted_song.append(song[song_start_point:])

    ambisonics_song = splitted_song.pop(0)
    phase_index = 0
    for segment in splitted_song:
        phase_index += 5
        segment = segment.pan(self.calc_pan(phase_index))
        ambisonics_song = ambisonics_song.append(segment, crossfade=interval/35)

    return ambisonics_song

class audioManipulation(object):
  def __init__(self, file_name):
    self.file_name = file_name

  def song_features(self, file_name):

    wav_mono, sampling_rate = librosa.load(file_name, duration=270)
    wav_stereo, sampling_rate = librosa.load(file_name, mono=False, duration=270)
    tempo, _ = librosa.beat.beat_track(y=wav_stereo[0], sr=sampling_rate)
    return wav_mono, sampling_rate, tempo


  def add_effects(self, input, rev, treble, bass):
    tfm = sox.Transformer()
    tfm.reverb(reverberance=rev)
    tfm.treble(gain_db=treble, slope=.3)
    tfm.bass(gain_db=bass, slope=.3)
    tfm.build(input, './out/effectz.wav')
    return

  def butter_lowpass(self, cutoff, fs, order=5):
    nyq = 0.5 * fs
    normal_cutoff = cutoff / nyq
    b, a = butter(order, normal_cutoff, btype='low', analog=False)
    return b, a

  def butter_lowpass_filter(self, data, cutoff, fs, order=5):
    b, a = self.butter_lowpass(cutoff, fs, order=order)
    y = lfilter(b, a, data)
    return y

  def butter_highpass(self, cutoff, fs, order=5):
    nyq = 0.5 * fs
    normal_cutoff = cutoff / nyq
    b, a = butter(order, normal_cutoff, btype='high', analog=False)
    return b, a

  def butter_highpass_filter(self, data, cutoff, fs, order=5):
    b, a = self.butter_lowpass(cutoff, fs, order=order)
    y = lfilter(b, a, data)
    return y


  def elevation(self, file_name):

    wav_mono, sampling_rate, tempo = self.song_features(file_name)
    length = len(wav_mono)
    end_of_beat = int((tempo / 120) * sampling_rate)*2

    order = 6
    fs = 30.0
    i = 1
    y = np.empty(0)

    while i < length:
        #low pass filter with cutoff decreasing
        cutoff = 10
        y = np.append(y, self.butter_lowpass_filter(wav_mono[i:i+end_of_beat], cutoff, fs, order))
        cutoff = 9.25
        y = np.append(y, self.butter_lowpass_filter(wav_mono[i+end_of_beat-1:i+2*end_of_beat], cutoff, fs, order))
        cutoff = 8.75
        y = np.append(y, self.butter_lowpass_filter(wav_mono[i+2*end_of_beat-1:i+3*end_of_beat], cutoff, fs, order))
        cutoff = 8
        y = np.append(y, self.butter_lowpass_filter(wav_mono[i+3*end_of_beat-1:i+4*end_of_beat], cutoff, fs, order))

        i += 4*end_of_beat

        #high pass filter with cutoff increasing
        cutoff = 8
        y = np.append(y, self.butter_highpass_filter(wav_mono[i-1:i+end_of_beat], cutoff, fs, order))
        cutoff = 8.75
        y = np.append(y, self.butter_highpass_filter(wav_mono[i+end_of_beat-1:i+2*end_of_beat], cutoff, fs, order))
        cutoff = 9.25
        y = np.append(y, self.butter_highpass_filter(wav_mono[i+2*end_of_beat-1:i+3*end_of_beat], cutoff, fs, order))
        cutoff = 10
        y = np.append(y, self.butter_highpass_filter(wav_mono[i+3*end_of_beat-1:i+4*end_of_beat], cutoff, fs, order))

        i += 4*end_of_beat

    return y

if __name__ == '__main__':

  gui = guiApp()
  gui.root.mainloop()
