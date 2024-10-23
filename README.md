# EchoCrypt -- An Ultrasonic Covert Channel
Rick Wallert | RIT CSEC BS/MS '25

### Overall Concept:
Within this GitHub repo you can find the code for an ultrasonic audo-based Covert Communications Channel.  The general premise is this: human hearing can only perceive sounds up to ~20kHz frequencies, while audio is capable of reaching frequencies far beyond this.  Is it then possible to take a message, encode it into ultrasonic frequencies, and then inlay this overtop an existing song?  The answer: yes, yes you can!

### The Code Itself:
You can find two python files within this repository: `Frequency-Decode-Analysis.py` and `Frequency-Encode-Analysis.py`.  These python files will either decode or encode audio files, respectively.  Each are ran on the command line, with the "Encode" file requiring the filepath to a .mp3 audio file to use as the base "song" to inlay the ultrasonic frequencies into.  The "Decode" file requires the "Encode" file to have already been run, and it executes a Fast Fourier Transformation on the produced combined audio file (defaults to "combined.wav") in order to extract the ultrasonic frequencies and decode the message.

### Encoding Schema:
While I am well aware that there are numerous ways to encode data into audio formats, I was simply creating this as a proof of concept.  So, I seem to have chosen the least efficient way to actually encode user messages -- but it works!  When the "Encode" file is ran properly, it prompts the user to enter a `string` message to hide.  This string is then converted into a binary representation, where each binary bit is converted into an ultrasonic frequency.  For simplicity's sake, I encode each "1" as a 21kHz frequency and each "0" as a 20.5kHz frequency, each being present for a full second.  This method allows for each ultrasonic frequency to become the dominant one as well, making it simpler to extract during the FFT.

### Optimizations / Future Works:
There are ***many***, many ways to optimize this code.  As I said, this is simply a proof of concept.  However, I did create a list of potential optimizations below should anyone (myself included) want to build on this idea:
- **Decrease frequency burst times:** You can decrease the time for each ultrasonic binary bit representation to as short as 50-100ms long.  Really, the only limitation to the size decrease should be FFT itself.
- **Don't use binary:** You can use any numeric format such as hexadecimal, octal, really anything that is a more efficient representation of string information.  I just chose binary because it was the simplest
- **Decrease the strength of the ultrasonic tones:** As of right now, I am making the ultrasonic frequencies the dominant frequencies.  This just makes it easier to differentiate during the FFT.  However, this also makes the channel significantly less covert.  In order to fix this, you would need to decrease the strength of the tones significantly and then filter by dominant *high pitched* frequencies.

### Important Notes:
- Unfortunately, the MP3 audio format is a file optimization algorithm.  So, it completely removes all ultrasonic sounds, meaning this entire Covert Channel is removed if the audio is converted back to an MP3.  This is why the output stays in .WAV format.
- Since the audio is being sent as files instead of played through speakers, the difference between the ultrasonic frequencies can be very close together (you'll notice mine are only 500Hz apart).  However, if trying to play this audio through a speaker and pick it up through a microphone, loss would need to be taken into account.
- Despite the fact that the audio is imperceivable, this does make a lot of noise.  By this I mean that temporary files are created and deleted, which can be caught by an OS easily.  Additionally, if you compare a frequency visualization of the original audio file and the "combined.wav" file, you can visually see a significant difference.
