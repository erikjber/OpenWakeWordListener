"""A simple class to read WAV RIFF audio data from a buffer."""

import struct
import numpy as np


class AudioData:
    def __init__(self, buffer):
        """Read the data from the buffer"""
        self.filesize = struct.unpack("<i", buffer[4:8])[0]
        self.format = struct.unpack("<h", buffer[20:22])[0]
        self.num_channels = struct.unpack("<h", buffer[22:24])[0]
        # Sample rate in samples per second
        self.sample_rate = struct.unpack("<i", buffer[24:28])[0]
        self.bits_per_sample = struct.unpack("<h", buffer[34:36])[0]
        # Number of bytes in the data
        self.size = struct.unpack("<i", buffer[40:44])[0]
        self.data = buffer[44:]


    def add(self, other):
        """Add another AudioData to this one"""
        if self.format != other.format or self.num_channels != other.num_channels or self.sample_rate != other.sample_rate or self.bits_per_sample != other.bits_per_sample:
            raise ValueError("Different data formats")
        self.data += other.data
        self.size += other.size
        self.filesize += other.size

    def get_length_seconds(self):
        return self.size / (self.sample_rate*self.bits_per_sample/8)

    def to_whisper_format(self):
        """Convert from 16 bit signed int to float in the range [-1, 1]"""
        return np.frombuffer(self.data, np.int16).flatten().astype(np.float32) / 32768.0

    def remove_samples_from_start(self, samples_to_remove):
        self.size -= samples_to_remove
        self.filesize -= samples_to_remove
        self.data = self.data[samples_to_remove:]

    def save(self, filename):
        with open(filename, "wb") as f:
            f.write("RIFF".encode("ascii"))
            f.write(struct.pack("<i", self.filesize))
            f.write("WAVEfmt ".encode("ascii"))
            f.write(struct.pack("<i", 16))
            f.write(struct.pack("<h", self.format))
            f.write(struct.pack("<h", self.num_channels))
            f.write(struct.pack("<i", self.sample_rate))
            f.write(struct.pack("<i", int(self.sample_rate*self.bits_per_sample*self.num_channels/8)))
            f.write(struct.pack("<h", int(self.bits_per_sample*self.num_channels/8)))
            f.write(struct.pack("<h", self.bits_per_sample))
            f.write("data".encode("ascii"))
            f.write(struct.pack("<i", self.size))
            f.write(self.data)
