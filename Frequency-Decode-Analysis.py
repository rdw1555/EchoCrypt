# Frequency-Decode-Analysis
# 10/8/2024
# Author: Rick Wallert
# SPEC: Program to decode data from an encoded "combined.wav" audio file

# Imports
import os                                   # OS for filepath comparison
import numpy as np                          # numpy for numpy arrays
from scipy.io import wavfile                # scipy.io for wavfile data exports
from scipy.fft import fft                   # scipy.fft for Fast Fourier Transformation
from scipy.io.wavfile import write, read    # scipy.io.wavfile for reading / writing to a WAV file
    
# Function to extract the highest frequencies from each <segment_duration> interval (hardcoded to 30 seconds, makes testing quicker and easier)
def extractHighestFrequencies(filepath, segment_duration=1):
    # Load the WAV file
    sample_rate, data = wavfile.read(filepath)

    # Convert to mono if stereo, doesn't matter since both channels have the same data
    if len(data.shape) == 2:
        data = np.mean(data, axis=1)
    
    # Calculate segment size based on segment duration (in seconds)
    segment_size = segment_duration * sample_rate
    num_segments = len(data) // segment_size

    # Initialize a list of the highest frequencies
    highest_frequencies = []

    # Loop over all audio segments
    for i in range(num_segments):
        segment = data[i*segment_size : (i+1)*segment_size]

        # Apply FFT to the extracted segment
        fft_result = fft(segment)

        # Get magnitude spectrum (needed to make sure frequency actually appears)
        magnitude = np.abs(fft_result)

        # Frequency axis (all possible frequencies, usually 44.1kHz / 2)
        freqs = np.fft.fftfreq(len(segment), 1/sample_rate)

        # Only consider positive frequencies (negative ones are mathematical artifacts)
        positive_freqs = freqs[:len(segment)//2]
        positive_magnitude = magnitude[:len(segment)//2]

        # Find indices of magnitudes above 100000 (should return the ultrasonic ones)
        valid_indices = np.where(positive_magnitude > 100000)[0]

        # If there are valid frequencies with the high magnitude
        if len(valid_indices) > 0:
            # Get the corresponding frequencies and magnitudes
            valid_frequencies = positive_freqs[valid_indices]
            valid_magnitudes = positive_magnitude[valid_indices]

            # Find the index of the highest frequency among the valid ones
            highest_freq_index = np.argmax(valid_frequencies)
            highest_frequency = int(valid_frequencies[highest_freq_index])
            highest_magnitude = int(valid_magnitudes[highest_freq_index])
        else:
            # If no frequencies meet the threshold, return 0
            highest_frequency = 0
            highest_magnitude = 0

        # Append the highest frequency and its magnitude for this segment
        highest_frequencies.append((highest_frequency, highest_magnitude))

    # Actually return the frequencies (I forgot this a couple times and wasted a lot of brain power trying to fix a nonexistant problem)
    return highest_frequencies

# Function to decode all of the frequency information and return the binary string
def decodeFrequencies(highestFrequencies):
    # Pull out only the frequency information
    allFreqs = []
    for element in highestFrequencies:
        allFreqs.append(element[0])

    # Store all of the relevant frequencies (those 20500 Hz and above)
    relevantFreqs = []
    for freq in allFreqs:
        if freq >= 20500:
            relevantFreqs.append(freq)

    # Convert the relevantFreqs into binary
    binaryString = ""
    for freq in relevantFreqs:
        if str(freq) == "20500":
            binaryString += "0"
        else:
            binaryString += "1"
    
    return binaryString

# Function to convert the binary to ASCII
def convertBinary(binaryString):
    # Make sure the binary string's length is a multiple of 8 for valid ASCII/UTF-8 decoding
    if len(binaryString) % 8 != 0:
        # Pad the binary string
        paddingLength = 8 - (len(binaryString) % 8)
        binaryString = binaryString + '0' * paddingLength

    try:
        # Convert the binary string to an ASCII string
        binaryArray = bytearray(int(binaryString[i:i+8], 2) for i in range(0, len(binaryString), 8))
        # Handle invalid bytes by ignoring them
        asciiText = binaryArray.decode('utf-8', errors='ignore')
    except UnicodeDecodeError as e:
        print(f"Error during binary to ASCII conversion: {e}")
        asciiText = ""

    return asciiText

# Main method
if __name__ == "__main__":
    print("\n---------------------------\n Frequency-Decode-Analysis\n---------------------------")

    # Use the combined WAV file (needs to stay as WAV because mp3 uses psychoacoustic modeling and removes / attenuates audio above 20kHz)
    workingDir = os.getcwd()
    combinedWavPath = workingDir + "\\combined.wav"

    # Extract the highest frequency + magnitude combos (useful for testing / comparison)
    highestFrequencies = extractHighestFrequencies(combinedWavPath)

    # Decode the frequency information
    binaryString = decodeFrequencies(highestFrequencies)
    print(f"Binary String: {binaryString}")

    # Convert the binary string into human readable text
    result = convertBinary(binaryString)
    print(f"Decoded message:\n{result}")

    print("\n---------------\n   Complete!\n---------------")