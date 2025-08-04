## A wakeword detector for Rhasspy.

The [Rhasspy](https://github.com/rhasspy/rhasspy) project already has several wake word detectors to choose from.
Unfortunately the existing wake word detectors fall in two categories: the not very good and the limited.

OpenWakeWordListener is sensitive, accurate, fast, and you can choose any wake word you like - you can even have multiple wake words or offload the wake word detection to another computer entirely. The wake word(s) are defined on the command line, you do not need to train a model for each wake word.
The trade-off is that OpenWakeWordListener requires more computing resources.

## Language support
OpenWakeWordListener supports [all languages supported by Whisper](https://raw.githubusercontent.com/openai/whisper/refs/heads/main/language-breakdown.svg).

## Installation
`pip install openwakewordlistener`

## Configuring Rhasspy
1. Open the Rhasspy web UI.
2. Click the little cog icon in the left margin to open the settings.
3. To the right of "MQTT", press the drop-down menu and select "External".
4. To the right of "Wake Word" press the drop-down menu and select "Hermes MQTT".
5. Click "Save Settings"

That's it! While you're in the settings, make note of which MQTT settings Rhasspy uses - you need to use the same settings for OpenWakeWordListener.

If you are running Rhasspy as a [Home Assistant](https://www.home-assistant.io/) add-on, make sure you have also installed the [Mosquitto MQTT broker add-on](https://github.com/home-assistant/addons/tree/master/mosquitto).

## Running
To run the detector standalone:

    python -m openwakewordlistener

Give the `-h` command line switch for a list of command line arguments.

These are the currently supported arguments:

    -w, --wakewords WAKEWORDS
                        A comma-separated list of wake words to listen for.
                        (default: computer)
    -v, --verbose         Enable verbose mode. (default: False)
    -q, --quiet           Only print warnings and errors. (default: False)
    -s, --server SERVER   The hostname or IP address of the MQTT broker Rhasspy
                        is using. (default: localhost)
    -p, --port_number PORT_NUMBER
                        The port number of the MQTT broker Rhasspy is using.
                        (default: 1883)
    --pwd PWD             The password of the MQTT broker Rhasspy is using.
                        (default: rhasspy)
    --usr USR             The user name of the MQTT broker Rhasspy is using.
                        (default: rhasspy)
    -l, --language LANGUAGE
                        The language to use. One of the OpenAI Whisper
                        languages: https://github.com/openai/whisper. Set to
                        "any" to accept any language (default: english)
    -b, --buffer BUFFER   The buffer size to use, in seconds. Should be a little
                        longer than the time it takes to say the longest wake
                        word. Larger buffer is more CPU intensive. (default: 1)
    --chunks CHUNKS       The number of chunks to add before processing the
                        buffer. Lower value means lower latency but more CPU
                        intensive. A chunk is usually 64 ms long, so the
                        default value of 3 processes the buffer every 192 ms,
                        or roughly 5 times/second. (default: 3)
    --threshold THRESHOLD
                        The threshold to use when deciding if sound is speech.
                        Lower value means fewer false negatives but is more
                        CPU intensive. (default: 0.1)`

Example usage:

    python -m openwakewordlistener -s rhasspyhost -p 12456 -l french -b 1.5 -w "harold,maurice"

This will start OpenWakeWordListener and connect to the Rhasspy MQTT broker at rhasspyhost port 12456, listen for French speech and the wake words "harold" and "maurice" with a 1.5 second buffer.
The default arguments are fine if you are using English and OpenWakeWord is running on the same host as Rhasspy.

## Including in your own project

After installing the package, all you have to do is:

1. Import the package: 

    `from openwakewordlistener import wakeword_listener`
2. Instantiate a listener:

    `listener = wakeword_listener.WakeWordListener()`
3. Start the listener:

    `listener.run()`

## Dependencies
OpenWakeWordListener uses [Silero VAD](https://github.com/snakers4/silero-vad) for speech detection and [Whisper](https://github.com/openai/whisper) for speech decoding.


