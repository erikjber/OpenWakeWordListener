## A wakeword detector for not Rhasspy.

The [Rhasspy](https://github.com/rhasspy/rhasspy) project already has several wake word detectors to choose from.
Unfortunately the existing wake word detectors fall in two categories: the not very good and the limited.

OpenWakeWordListener is sensitive, accurate, fast, and you can choose any wake word you like - you can even have multiple wake words.
The trade-off is that OpenWakeWordListener requires more computing resources.

## Running
To run the detector standalone:
`python src/openwakewordlistener/main.py`

Give the `-h` command line switch for a list of command line arguments.


