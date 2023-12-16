# -*- coding: utf-8 -*-
"""DSP.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1_BtYECbhuPmr-W_F29JzjcHAUVbyOH_f
"""

from google.colab import drive
drive.mount('/content/drive')

import librosa
import librosa.display
import matplotlib.pyplot as plt
import numpy as np
import math

# Specify the path to the uploaded audio file
audio_file_path = '/content/drive/MyDrive/Dataset/AirportAnnouncement_11.wav'  # Replace with the copypath

# Load the audio file and convert it to a NumPy array
noisy_speech, sample_rate = librosa.load(audio_file_path, sr=16000)


# Now, the 'audio' variable contains the audio data as a NumPy array, and 'sample_rate' contains the sample rate of the audio.
plt.figure(figsize=(14, 4))
librosa.display.waveshow(noisy_speech, sr=sample_rate)
plt.xlabel("Time (s)")
plt.title("Audio Waveform")
plt.show()

print(noisy_speech)
print(type(noisy_speech))
print(noisy_speech.shape)
print(sample_rate)
print(type(sample_rate))

"""STFT and inverse STFT"""

n_fft = 2048
win_length = n_fft
hop_length = win_length // 2
STFT_noisy_speech = librosa.stft(noisy_speech,n_fft=n_fft, win_length = win_length, hop_length = hop_length)
print(STFT_noisy_speech.shape)
print(len(STFT_noisy_speech))
print(STFT_noisy_speech)
print(STFT_noisy_speech[:,1])

D = librosa.amplitude_to_db(np.abs(STFT_noisy_speech), ref=np.max)

librosa.display.specshow(D, x_axis='time', y_axis='log',sr=sample_rate,hop_length=hop_length)
plt.title('Spectrogram of Noisy Speech without Processing')
plt.show()

"""To sample the noise where no speech activity, we should replot the figure with more resolution from time 2 seconds to 4 seconds

"""

plt.figure(figsize=(14, 4))
librosa.display.waveshow(noisy_speech, sr=sample_rate)
plt.xlabel("Time (s)")
plt.title("Audio Waveform")

plt.figure(figsize=(14, 4))

start_time = 2
end_time = 3

# Find the corresponding sample indices for the specified time range
start_sample = int(start_time * sample_rate)
end_sample = int(end_time * sample_rate)

# Plot the audio waveform for the specified time range
librosa.display.waveshow(noisy_speech[start_sample:end_sample], sr=sample_rate, x_axis='s')

# Set the x-axis to show labels every 0.1 second within the range [2, 3]
time_points = [i * 0.1 for i in range(int((end_time - start_time) / 0.1) + 1)]
plt.xticks(time_points, [start_time + t for t in time_points])
plt.xlabel("Time (s)")
plt.title("Audio Waveform (2s to 3s)")
plt.show()

"""from the waveform plot, we can see sample from 2 seconds to 2.7 seconds to obtain the noise signal, next is to find the frame index in the STFT correpsonding to this time duration"""

start_time = 2
end_time = 2.7
start_sample = int(start_time * sample_rate)
end_sample = int(end_time * sample_rate)

start_frame = librosa.samples_to_frames(start_sample, hop_length=hop_length)
end_frame = librosa.samples_to_frames(end_sample, hop_length=hop_length)
print("Start Frame:", start_frame)
print("End Frame:", end_frame)
#taking the average of noise

STFT_noise = STFT_noisy_speech[:,start_frame:end_frame]
print(STFT_noise)
print(STFT_noise.shape)
noise_mean = np.mean(np.abs(STFT_noise),axis=1)

print(noise_mean)
print(noise_mean.shape)

# spectrogram plot of noise
D = librosa.amplitude_to_db(np.abs(STFT_noise), ref=np.max)

librosa.display.specshow(D, x_axis='time', y_axis='log',sr=sample_rate,hop_length=hop_length)
plt.title('Spectrogram of noise')
plt.show()

"""After obtain the mean of noise, then we should proceed to the spetral reduction part

"""

#obtain the magnitude of noise_mean, noisy speech, and the phase of noisy speech
mag_noise = np.abs(noise_mean)
print(mag_noise)
phase_speech = np.angle(STFT_noisy_speech)
mag_speech_noisy = np.abs(STFT_noisy_speech)
print(mag_speech_noisy)
#initialize magnitude of pure speech
mag_speech = np.zeros(mag_speech_noisy.shape)
print(len(mag_speech_noisy))
print(mag_speech_noisy.shape)

"""# Half Wave Rectification Technique"""

for x in range(mag_speech_noisy.shape[1]):
  for y in range(mag_speech_noisy.shape[0]):
    if mag_speech_noisy[y][x] - mag_noise[y] >= 0:
      mag_speech[y][x] = mag_speech_noisy[y][x] - mag_noise[y]
    else:
      mag_speech[y][x] = 0
print(mag_speech)
print(mag_speech.shape)

D = librosa.amplitude_to_db(mag_speech, ref=np.max)

librosa.display.specshow(D, x_axis='time', y_axis='log',sr=sample_rate,hop_length=hop_length)
plt.title('Spectrogram of Noisy Speech after Bias Subtraction and Rectification')
plt.show()

"""# Residual Noise Reduction"""

#again taking the noisy speech from 2 to 2.7 seconds
residual_noise = mag_speech[:,start_frame:end_frame]
print(residual_noise.shape)
residual_noise = np.max(residual_noise,axis = 1)
print(residual_noise.shape)
print(residual_noise)
print(mag_speech.shape)

mag_speech1 = np.zeros(mag_speech.shape)

for x in range(mag_speech.shape[1]):
  for y in range(mag_speech.shape[0]):
    if x == 0: #initial time frame
      if mag_speech[y][x] < residual_noise[y]:
        mag_speech1[y][x] = min(mag_speech[y][x],mag_speech[y][x+1])
      else:
        mag_speech1[y][x] = mag_speech[y][x]
    elif x == mag_speech.shape[1] - 1: #last time frame
      if mag_speech[y][x] < residual_noise[y]:
        mag_speech1[y][x] = min(mag_speech[y][x],mag_speech[y][x-1])
      else:
        mag_speech1[y][x] = mag_speech[y][x]
    else:
      if mag_speech[y][x] < residual_noise[y]:
        mag_speech1[y][x] = min(mag_speech[y][x],mag_speech[y][x-1],mag_speech[y][x+1])
      else:
        mag_speech1[y][x] = mag_speech[y][x]

print(mag_speech1)
print(mag_speech1.shape)

D = librosa.amplitude_to_db(mag_speech1, ref=np.max)

librosa.display.specshow(D, x_axis='time', y_axis='log',sr=sample_rate,hop_length=hop_length)
plt.title('Spectrogram of Noisy Speech after Residual Noise Reduction')
plt.show()

"""# Additional Signal Attenuation"""

column_noise_mean = noise_mean.reshape((-1,1))
print(column_noise_mean)
print(column_noise_mean.shape)

ratio = np.abs(mag_speech1) / np.abs(column_noise_mean)
print(ratio)
print(ratio.shape)

ratio_vector = np.sum(ratio,axis = 0)
ratio_vector = ratio_vector / (2*np.pi)
print(ratio_vector)
print(ratio_vector.shape)
T = 20 * np.log10(ratio_vector)
print(T)
print(T.shape)

c = 0.0316227766
mag_speech2 = np.zeros(mag_speech1.shape)
for x in range(mag_speech1.shape[1]):
  if T[x] >= -12:
    for y in range(mag_speech1.shape[0]):
      mag_speech2[y][x] = mag_speech1[y][x]
  else:
    for z in range(mag_speech1.shape[0]):
      mag_speech2[y][x] = c * mag_speech_noisy[y][x]

print(mag_speech2)
print(mag_speech2.shape)

D = librosa.amplitude_to_db(mag_speech2, ref=np.max)

librosa.display.specshow(D, x_axis='time', y_axis='log',sr=sample_rate,hop_length=hop_length)
plt.title('Spectrogram of Speech after Additional Signal Attenuation ')
plt.show()

speech = mag_speech2*phase_speech
print(speech)
reconstructed_speech = librosa.istft(speech,n_fft=n_fft, win_length = win_length, hop_length = hop_length)

plt.figure(figsize=(14, 4))
librosa.display.waveshow(reconstructed_speech, sr=sample_rate)
plt.xlabel("Time (s)")
plt.title("Audio Waveform after Noise Supression")
plt.show()
print(reconstructed_speech)
print(reconstructed_speech.shape)

plt.figure(figsize=(14, 8))

plt.subplot(2, 1, 1)
librosa.display.waveshow(noisy_speech, sr=sample_rate)
plt.xlabel("Time (s)")
plt.title("Audio Waveform")

plt.subplot(2, 1, 2)
librosa.display.waveshow(reconstructed_speech, sr=sample_rate)
plt.xlabel("Time (s)")
plt.title("Audio Waveform after Noise Supression")

plt.tight_layout()
plt.show()

from scipy.io import wavfile
import numpy as np

# Assuming you have modified the audio data and have it in a NumPy array called modified_audio_data
# Convert it to the appropriate PCM format (e.g., int16)
pcm_format = np.int16

# Normalize the audio data to the valid range for the chosen data type
reconstructed_speech = np.int16(reconstructed_speech * np.iinfo(pcm_format).max)

# Specify the path where you want to save the modified audio as a .wav file
output_file_path = 'modified_audio.wav'

# Write the modified audio data to the .wav file
wavfile.write(output_file_path, sample_rate, reconstructed_speech)