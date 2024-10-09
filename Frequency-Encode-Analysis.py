# Frequency-Encode-Analysis
# 10/8/2024
# Author: Rick Wallert
# SPEC: Takes in song filepath as command line argument, prompt user for input, and encode data as ultrasonic sound into an output WAV file called "combined.wav"

# Imports
import os                                   # OS for filepath comparison
import subprocess                           # subprocess for ffmpeg call
import sys                                  # sys for command line arguments
import numpy as np                          # numpy for numpy arrays
from scipy.io import wavfile                # scipy.io for wavfile data exports
from scipy.fft import fft                   # scipy.fft for Fast Fourier Transformation
from scipy.io.wavfile import write, read    # scipy.io.wavfile for reading / writing to a WAV file

# Function to convert a .mp3 file to a .wav file (uses ffmpeg)
def convertToWAV(mp3Filepath, wavFilepath):
    # Check if both the input filepath or output filepaths exist
    if os.path.exists(mp3Filepath):
        if os.path.exists(wavFilepath):
            print("ERROR: Output filepath already exists. Exiting without converting to .wav...")
            return 1
        
        # Actually convert the file using an ffmpeg subprocess call
        subprocess.call(['ffmpeg', '-i', mp3Filepath, wavFilepath], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print("File converted to WAV!")
        return 0
    else:
        print("ERROR: Input file not found")
        return 1

# Function to clear created files
def clearFiles(ultrasonicWavPath, originalSongWavPath):
    # Remove the ultrasonicWavPath and originalSongWavPath
    # Create a list to see which files were deleted
    successes = []
    if os.path.exists(ultrasonicPath):
        os.remove(ultrasonicWavPath)
        successes.append("ultrasonicWavPath")
    if os.path.exists(originalSongWavPath):
        os.remove(originalSongWavPath)
        successes.append("originalSongWavPath")
    printStr = "Successfully deleted: "
    for success in successes:
        printStr += success + ", "
    print(printStr[0:-2])

# Function to prompt user for input and convert it to a binary string
def userInput(duration):
    # Prompt user for input
    inputRaw = input("Enter a word or phrase to hide: ")

    # Convert to binary
    binaryString = ''.join(format(ord(i), '08b') for i in inputRaw)
    print(f"Binary: {binaryString}\n")

    # Check if the amount of bits in the string is greater than the number of seconds in the song, warn if so
    if len(binaryString) >  duration:
        print("WARNING: Encoded message is longer than the song can hold. Truncating message... (this may result in miscommuniation).")

    # Return the binary
    return binaryString

# Function to generate a WAV file for binary data
def generateUltrasonicWav(binaryData, stereo, sampleRate, ultrasonicPath, duration=1):
    # Parameters for 1s and 0s (21kHz for "1" and 20.5kHz for "0")
    freq1 = 21000
    freq0 = 20500

    # Time axis for 1 second
    t = np.linspace(0, duration, int(sampleRate * duration), endpoint=False)

    # Generate audio signal
    audioSignal = np.array([])

    # Loop over the input binary data
    for bit in binaryData:
        if bit == "1":
            # Generate a 21kHz tone
            signal = np.sin(2 * np.pi * freq1 * t)
        else:
            # Generate a 20.5kHz tone
            signal = np.sin(2 * np.pi * freq0 * t)
        audioSignal = np.concatenate([audioSignal, signal])

    # Normalize the signal (Convert to 16-bit PCM)
    audioSignal = np.int16(audioSignal / np.max(np.abs(audioSignal)) * 32767)

    # Check for stereo audio
    if stereo:
        # Duplicate the mono signal to both channels for stereo
        audioSignal = np.column_stack((audioSignal, audioSignal))

    # Write to temporary WAV file
    write(ultrasonicPath, sampleRate, audioSignal)

# Function to load the original WAV file (song) and combine with ultrasonic tones
def combineWavFiles(songWavPath, ultrasonicWavPath, combinedFilepath):
    # Read in the original song data
    songSampleRate, songData = wavfile.read(songWavPath)

    # Convert song data to float to avoid integer overflows during processing
    songData = songData.astype(float)

    # Check if the song is stereo or mono
    if len(songData.shape) == 2:
        isStereo = True
        numChannels = songData.shape[1]
    else:
        isStereo = False
        numChannels = 1

    # Read the ultrasonic file
    ultrasonicSampleRate, ultrasonicData = read(ultrasonicWavPath)

    # Convert ultrasonic data to float as well
    ultrasonicData = ultrasonicData.astype(float)

    # Check that the sample rates match
    if songSampleRate != ultrasonicSampleRate:
        print(f"songSampleRate: {songSampleRate}\nultrasonicSampleRate: {ultrasonicSampleRate}")
        raise ValueError("Sample rates of the two WAV files must match.")
    
    # Ensure the ultrasonic data matches the length of the song
    if len(ultrasonicData) < len(songData):
        # Adjust the padding for stereo or mono correctly
        if isStereo:
            # Pad stereo data (2 channels)
            padSize = len(songData) - len(ultrasonicData)
            ultrasonicData = np.pad(ultrasonicData, ((0, padSize), (0,0)), 'constant')
        else:
            ultrasonicData = np.pad(ultrasonicData, (0, len(songData) - len(ultrasonicData)), 'constant')
    else:
        ultrasonicData = ultrasonicData[:len(songData)]

    # Combine the audio data
    if isStereo:
        # If ultrasonic is mono, expand to stereo
        if ultrasonicData.ndim == 1:
            ultrasonicData = np.column_stack((ultrasonicData, ultrasonicData))
        combinedData = songData + ultrasonicData[:, :numChannels]
    else:
        combinedData = songData + ultrasonicData

    # Normalize combined data to ensure no clipping
    # Normalization should lower the data to avoid exceeding the 16-bit range
    # Normalize to a range of -1 to 1
    combinedData = combinedData / np.max(np.abs(combinedData))
    # Convert back to 16-bit PCM
    combinedData = np.int16(combinedData * 32767)

    # Delete output WAV file if exists
    if os.path.exists(combinedFilepath):
        os.remove(combinedFilepath)
        print(f"Filepath {combinedFilepath} already existed, deleted old instance.")

    # Write the output WAV file
    write(combinedFilepath, songSampleRate, combinedData)

# Main method
if __name__ == "__main__":
    print("\n---------------------------\n Frequency-Encode-Analysis\n---------------------------\n")

    # Pull the filepaths from command line arguments
    if len(sys.argv) < 2:
        print("ERROR: song filepath not found.\nUsage: Frequency-Encode-Analysis.py <song-filepath>")
        quit()

    # Set the original song filepath based on the command line argument
    originalSongPath = sys.argv[1]

    # Check if the filepath exists
    if not os.path.exists(originalSongPath):
        print("ERROR: invalid song filepath.")
        quit()

    # Store the working directory for other files
    workingDir = os.getcwd()

    # Set the other filepaths
    originalSongWavPath = workingDir + "\\song.wav"
    ultrasonicPath = workingDir + "\\ultrasonic.wav"
    combinedWavPath = workingDir + "\\combined.wav"

    # Create WAV file of original song (needed for future calculations)
    convertToWAV(originalSongPath, originalSongWavPath)

    # Get the length of the song in seconds (used to warn about binary output length)
    # Read in the original song data
    songSampleRate, songData = wavfile.read(originalSongWavPath)

    # Check if the song is stereo or mono
    if len(songData.shape) == 2:
        isStereo = True

    # Calculate the number of samples to extrapolate how long the song is in seconds
    # Floor divide to round down
    # NOTE: This seems to result in a length a few seconds too short, but this shouldn't be a problem (can help prevent overflowings of data)
    duration = len(songData) // songSampleRate
    print(f"Duration of the song in seconds: {duration}")

    # Get user input (prints out data)
    userInputBinary = userInput(duration)

    # Generate ultrasonic WAV based on binary
    generateUltrasonicWav(userInputBinary, isStereo, songSampleRate, ultrasonicPath)

    combineWavFiles(originalSongWavPath, ultrasonicPath, combinedWavPath)
    print("WAV files have been generated / combined")

    # Clear created files
    clearFiles(ultrasonicPath, originalSongWavPath)

    print("\n---------------\n   Complete!\n---------------")