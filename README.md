## A wakeword detector for Rhasspy.

The [Rhasspy](https://github.com/rhasspy/rhasspy) project already has several wake word detectors to choose from.
Unfortunately the existing wake word detectors fall in two categories: the not very good and the limited.

OpenWakeWordListener is sensitive, accurate, fast, and you can choose any wake word you like - you can even have multiple wake words or offload the wake word detection to another computer entirely.
The trade-off is that OpenWakeWordListener requires more computing resources.

### Configuring Rhasspy
1. Open the Rhasspy web UI.
2. Click the little cog icon in the left margin to open the settings.
3. To the right of "MQTT", press the drop-down menu and select "External".
4. To the right of "Wake Word" press the drop-down menu and select "Hermes MQTT".
5. Click "Save Settings"

That's it! While you're in the settings, make note of which MQTT settings Rhasspy uses - you need to use the same settings for OpenWakeWordListener.

If you are running Rhasspy as a [Home Assistant](https://www.home-assistant.io/) add-on, make sure you have also installed the [Mosquitto MQTT broker add-on](https://github.com/home-assistant/addons/tree/master/mosquitto).

### Running
To run the detector standalone:
`python src/openwakewordlistener/main.py`

Give the `-h` command line switch for a list of command line arguments.

## Dependencies
OpenWakeWordListener uses [Silero VAD](https://github.com/snakers4/silero-vad) for speech detection and [Whisper](https://github.com/openai/whisper) for speech decoding.


