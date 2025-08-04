import logging
from argparse import ArgumentParser,ArgumentDefaultsHelpFormatter

from .wakeword_listener import WakeWordListener

def _parse_args():
    parser = ArgumentParser(
        prog="WakeWordListener",
        description="Listens for wake words and notifies Rhasspy if it hears any.",
        formatter_class=ArgumentDefaultsHelpFormatter
    )
    parser.add_argument("-w", "--wakewords",type=str,default="computer",help="A comma-separated list of wake words to listen for.")
    parser.add_argument("-v", "--verbose",action="store_true",default=False,help="Enable verbose mode.")
    parser.add_argument("-q", "--quiet",action="store_true",default=False,help="Only print warnings and errors.")
    parser.add_argument("-s","--server",type=str,default="localhost",help="The hostname or IP address of the MQTT broker Rhasspy is using.")
    parser.add_argument("-p","--port_number",type=int,default=1883,help="The port number of the MQTT broker Rhasspy is using.")
    parser.add_argument("--pwd",type=str,default="rhasspy",help="The password of the MQTT broker Rhasspy is using.")
    parser.add_argument("--usr",type=str,default="rhasspy",help="The user name of the MQTT broker Rhasspy is using.")
    parser.add_argument("-l","--language",type=str,default="english",help="The language to use. One of the OpenAI Whisper languages: https://github.com/openai/whisper. Set to \"any\" to accept any language")
    parser.add_argument("-b","--buffer",type=float,default=1,help="The buffer size to use, in seconds. Should be a little longer than the time it takes to say the longest wake word. Larger buffer is more CPU intensive.")
    parser.add_argument("--chunks",type=int,default=3,help="The number of chunks to add before processing the buffer. Lower value means faster reaction but more CPU intensive. A chunk is usually 64 ms long, so the default value of 3 processes the buffer every 192 ms, or roughly 5 times/second.")
    parser.add_argument("--threshold",type=float,default=0.1,help="The threshold to use when deciding if sound is speech. Lower value means fewer false negatives but is more CPU intensive. Range: 0 to 1.")

    return parser.parse_args()

def main():
    args = _parse_args()
    loglevel = logging.INFO
    if args.verbose:
        loglevel = logging.DEBUG
    elif args.quiet:
        loglevel = logging.WARNING
    if args.language.lower() == "any":
        args.language = None
    wakeword_listener = WakeWordListener(wakewords=args.wakewords,loglevel=loglevel,
                                         hostname=args.server,port_number=args.port_number,
                                         password=args.pwd,username=args.usr,
                                         language=args.language,buffer_time_seconds=args.buffer,
                                         chunks_between_scans=args.chunks,speech_threshold=args.threshold)
    wakeword_listener.run()

if __name__ == "__main__":
    main()
