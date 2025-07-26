import logging
import multiprocessing
import time

import paho.mqtt.client as mqtt
import torch
import whisper
from silero_vad import (load_silero_vad, get_speech_timestamps)

from audiodata import AudioData

torch.set_num_threads(max(multiprocessing.cpu_count() // 2, 1))


class WakeWordListener:
    def __init__(self,
                 buffer_time_seconds: float = 1,
                 chunks_between_scans: int = 3,
                 wakewords: str = "computer",
                 loglevel: int = logging.INFO,
                 hostname="localhost",
                 port_number: int = 1883,
                 username: str = "rhasspy",
                 password: str = "rhasspy",
                 language: str = "english",
                 speech_threshold: float = 0.1):
        """
        Constructs a WakeWordListener object. After the constructor returns, the listener is ready but not yet running.

        :param buffer_time_seconds: The size of the buffer, should be a little longer than the time it takes to say the longest wakeword.
        :param chunks_between_scans: How many audio chunks to add to the buffer before it is processed. Lower value = faster response but more CPU intensive.
        :param wakewords: A comma-separated list of words that will wake Rhasspy up.
        :param loglevel: How detailed logging should be displayed. logging.WARNING, logging.INFO, logging.DEBUG etc.
        :param hostname: The hostname or IP address of the MQTT broker Rhasspy is using.
        :param port_number: The port number of the MQTT broker Rhasspy is using.
        :param username: The username of the MQTT broker Rhasspy is using.
        :param password: The password of the MQTT broker Rhasspy is using.
        :param language: The language to listen for commands in, or None for any language.
        :param speech_threshold: How strict to be when deciding if a sound is speech. Range=(0,1). Lower values means fewer false negatives but more CPU intensive.
        """
        logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s', level=loglevel)
        self.logger = logging.getLogger(__name__)
        self.buffer_time_seconds = buffer_time_seconds
        self.chunks_between_scans = chunks_between_scans
        self.sample_size = None
        self.hostname = hostname
        self.port_number = port_number
        self.wakewords = wakewords.lower().split(",")
        self.username = username
        self.password = password
        self.speech_threshold = speech_threshold
        self.chunks_since_last_scan = 0

        start = time.time()
        self.silero_model = load_silero_vad(onnx=True)
        self.logger.info(f"Silero model loaded in {(time.time() - start):.6f} seconds")
        start = time.time()
        if language == "english":
            # Load the language-specific optimised model
            self.model = whisper.load_model("tiny.en")
        else:
            # Load a language-neutral model
            self.model = whisper.load_model("tiny")
        self.logger.info(f"Whisper model loaded in {(time.time() - start):.6f} seconds")
        self.logger.info(f"Model device: {self.model.device}")
        self.decoding_options = whisper.DecodingOptions(language=language)
        self.audiobuffer = None

    def on_connect(self, client, userdata, flags, rc):
        """Callback method for when we're connected to the MQTT broker."""
        self.logger.info(f"Connected with result code {rc}")
        client.subscribe("hermes/audioServer/default/audioFrame")

    def on_message(self, client, userdata, msg):
        """Callback method for when we received a message from the MQTT broker."""
        if msg.topic == "hermes/audioServer/default/audioFrame":
            if not self.audiobuffer:
                self.audiobuffer = AudioData(msg.payload)
                self.sample_size = self.audiobuffer.size
            else:
                self.audiobuffer.add(AudioData(msg.payload))
                while self.audiobuffer.get_length_seconds() > self.buffer_time_seconds:
                    self.audiobuffer.remove_samples_from_start(self.sample_size)
                self.chunks_since_last_scan += 1
                if self.chunks_since_last_scan >= self.chunks_between_scans:
                    start = time.time()
                    self.chunks_since_last_scan = 0
                    audio_whisper_format = self.audiobuffer.to_whisper_format()
                    speech_timestamps = get_speech_timestamps(audio_whisper_format, self.silero_model,
                                                              sampling_rate=self.audiobuffer.sample_rate, threshold=self.speech_threshold,
                                                              min_speech_duration_ms=50)
                    if speech_timestamps:
                        audio = whisper.pad_or_trim(audio_whisper_format)
                        mel = whisper.log_mel_spectrogram(audio, n_mels=self.model.dims.n_mels).to(self.model.device)
                        result = whisper.decode(self.model, mel, self.decoding_options)
                        result_text = (result.text.lower().replace(".", "")
                                       .replace(",", "").replace("?", "")
                                       .replace("!", "").replace("%", " percent"))
                        self.logger.debug(f"Detected speech: \"{result_text}\"")
                        for wakeword in self.wakewords:
                            if wakeword in result_text:
                                client.publish("hermes/hotword/default/detected",
                                               '{"model_id":"default"}')
                                self.logger.info(f"Detected wakeword \"{wakeword}\": in speech \"{result_text}\"")
                                # Purge remaining buffer
                                self.audiobuffer = None
                                break
                    self.logger.debug(f"Processed in {(time.time() - start):.6f} seconds")

        else:
            print(msg.topic + " " + str(msg.payload))

    def run(self):
        """Start the listener. This method never returns."""
        client = mqtt.Client()
        client.username_pw_set(self.username, self.password)
        client.on_connect = self.on_connect
        client.on_message = self.on_message
        client.connect(self.hostname, self.port_number, 60)
        client.loop_forever()

