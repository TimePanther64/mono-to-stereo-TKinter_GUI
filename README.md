# stereo-to-ambisonic
A GUI which gives users the option to convert either a single stereo audio file to an ambisonic audio file 
or do a batch conversion of several audio files with a few extra features integrated. 

The first is a reverberation slider having a range from 15 to 30 (inclusive)
The second is a treble slider having a range from 2 to 12 (inclusive)
The third is a bass slider having a range from 2 to 12 (inclusive)
The forth is a volume slider ranging from -36dB to +36dB

The batch conversion uses multiprocessing to speed up the process.
