#! /usr/bin/python3

# This script is meant generate audio files from a list of English irregular verbs from a json file with the proper
# structure.
# Author : Christophe "SntPx" RIVIERE

from kokoro import KPipeline
import json
import argparse
from rich import print
import hashlib
import soundfile as sf
from pathlib import PosixPath
import time
import logging

# a => US, b=> GB
FILE_DEST_PREFIX = "audio_files"
DEFAULT_JSON_FILE = "Augmented_IrregularVerbs_2.json"
NB_FILES = 0

# -- argparse config --
parser = argparse.ArgumentParser("generate_audio_files.py")
parser.add_argument('-i', '--json_file',
                    default=DEFAULT_JSON_FILE,
                    type=str,
                    help="Source json file, generated with augment_irrverbs, containing irregular verbs."
                    )
parser.add_argument('-f', '--format',
                    default='ogg',
                    type=str,
                    help="Format of the output audio files. possible values are: WAV, OGG, FLAC, MP3."
                    )
parser.add_argument('--headers',
                    type=str,
                    help='Comma separated list of headers to use. Leave blank if unsure or if using --p_headers.'
                    )
parser.add_argument('--p_headers',
                    type=str,
                    help='Comma separated list of the headers to be processed. Leav blank if unsure or using --headers.'
                    )
parser.add_argument('-s', '--sampling_rate',
                    default=24000,
                    type=int,
                    help='Sampling rate to be used when generating audio files. Defaults to 24000.'
                    )
args = parser.parse_args()


console = logging.StreamHandler()
console.setLevel(logging.INFO)
console.setFormatter(logging.Formatter('%(name)-12s: %(levelname)-8s %(message)s'))
logging.getLogger('').addHandler(console)


def hash_file_name(elems: list) -> str:
    normalized = [elem.replace(" ", "-").lower() for elem in elems]
    return hashlib.sha1("_".join(normalized).encode('utf-8')).hexdigest()


def get_verbs(data, headers=None, p_headers=None):
    """
    Takes in a JSON representation of the list of verbs and transforms it, so that it can be processed.
    :param data: parsed JSON
    :param headers: list of headers present in the JSON file. If None, defaults to using the keys of the 1st level
     of JSON structure as headers.
    :param p_headers: the list headers whose data is going to be processed. If none, defaults to the first 3 keys of
    headers
    :return: a list of dicts representing each a unique form of a verb, with its written foirm and its phonological
    realisations
    """
    headers = headers if headers is not None else list(data[0].keys())
    p_headers = p_headers if p_headers is not None else headers[:3]
    seen = set()
    r = [
        form
        for verb in data
        for k, v in verb.items()
        if k in p_headers
        for form in v
        if (s := json.dumps(form, sort_keys=True, ensure_ascii=False)) not in seen and not seen.add(s)
    ]
    return r


def generate_sound_files(verb_data: list, s_rate=24000, fmt='ogg'):
    """
    Take a list of objects obtained from properly formatted JSON file, representing individual irregular verbs and, for
    each of them, creates an audio file of expected type, with a definite sampling rate.
    :param verb_data: list of objects (dicts) representing a verb, with its spelling and phonological representation
    :param s_rate: an int representing the sampling rate. Defaults to 24000.
    :param fmt: audio format to use. Defaults to "ogg".
    :return: void
    """
    global NB_FILES
    logging.info('Creating pipeline for language code en-US...')
    pipeline_us = KPipeline(lang_code='a', repo_id='hexgrad/Kokoro-82M')
    logging.info('Creating pipeline for language code en-GB...')
    pipeline_gb = KPipeline(lang_code='b', repo_id='hexgrad/Kokoro-82M')

    for verb in verb_data:
        spelling, gb_pron, us_pron = verb["w"], verb['ph']['gb'], verb["ph"]["us"]
        gb_data = f'[{spelling}](/{gb_pron}/)'
        us_data = f'[{spelling}](/{us_pron}/)'
        gb_file_name = hash_file_name([spelling, gb_pron, "gb"])
        us_file_name = hash_file_name([spelling, us_pron, "us"])
        gb_generator = pipeline_gb(
            gb_data,
            voice="bf_emma",
            speed=1,
        )
        us_generator = pipeline_us(
            us_data,
            voice="af_heart",
            speed=1
        )
        for i, (gs, ps, audio) in enumerate(gb_generator):
            dest = PosixPath(FILE_DEST_PREFIX, 'gb', f'{gb_file_name}.{fmt}')
            print(f'Writing [bold][red]{dest}[/bold][/red]([bold][yellow]<GB>{gs}[/bold][/yellow])')
            sf.write(dest, audio, s_rate)
        NB_FILES += 1
        for i, (gs, ps, audio) in enumerate(us_generator):
            dest = PosixPath(FILE_DEST_PREFIX, 'us', f'{us_file_name}.{fmt}')
            print(f'Writing [bold][red]{dest}[/bold][/red]([bold][yellow]<US>{gs}[/bold][/yellow])')
            sf.write(dest, audio, s_rate)
        NB_FILES += 1


def main():
    headers = args.headers if args.headers else None
    p_headers = args.p_headers if args.p_headers else None
    fmt = args.format.lower()
    with open(args.json_file) as jsf:
        irrverbs = json.load(jsf)
    generate_sound_files(get_verbs(irrverbs, headers=headers, p_headers=p_headers), fmt=fmt)


if __name__ == "__main__":
    start_time = time.time()
    main()
    print(
        f"Finished generating [bold]{NB_FILES} files[/bold] in [bold][yellow]{time.time() - start_time}"
        f"[/yellow][/bold] seconds.")
