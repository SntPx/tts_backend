#! /usr/bin/python3

# This script is meant to turn the original irregular verb json file into an enriched one, with phonetics.
# The resulting phonetics should be used with a TTS model using misaki under the hood
# Author : Christophe "SntPx" RIVIERE

import phonemizer.backend
import time
import json
import argparse
from rich import print
from utils import from_espeak

# -- argparse config --
parser = argparse.ArgumentParser("augment_verbs.py")
parser.add_argument('source', help="Source json file, in the correct format.")
parser.add_argument("dest", help="Name for destination file.")
args = parser.parse_args()

# -- CONFIG --
BATCH_SIZE = 25
PHONEME_CACHE = {}

# -- Backend --
GB_BACKEND = phonemizer.backend.EspeakBackend(
        language="en-gb",
        preserve_punctuation=False,
        with_stress=True,
        tie='^',
    )
US_BACKEND = phonemizer.backend.EspeakBackend(
        language="en-us",
        preserve_punctuation=False,
        with_stress=True,
        tie='^',
    )


def phonemize_word(word: str):
    """Phonemize a single word with caching"""
    if word not in PHONEME_CACHE:
        gb_ph = GB_BACKEND.phonemize([word])[0].strip()
        us_ph = US_BACKEND.phonemize([word])[0].strip()
        PHONEME_CACHE[word] = {
            "gb": from_espeak(gb_ph, True),
            "us": from_espeak(us_ph, False)
        }
    return PHONEME_CACHE[word]


def expand_forms(form_str: str):
    """Split a string with '/' into a list of dicts with 'w' and 'ph'"""
    return [{"w": w, "ph": phonemize_word(w)} for w in form_str.split('/')]


def phonemize_batch(words):
    """
    Returns a list of dicts for each form
    :param words: string list
    :return: [{"gb": ..., "us": ... }, ...]
    """
    results = []

    for i in range(0, len(words), BATCH_SIZE):
        batch = words[i:i+BATCH_SIZE]

        # Words that are not cached yet
        missing = [w for w in batch if w not in PHONEME_CACHE]

        if missing:
            gb_ph = GB_BACKEND.phonemize(missing)
            us_ph = US_BACKEND.phonemize(missing)
            for w, g, u in zip(missing, gb_ph, us_ph):
                PHONEME_CACHE[w] = {"gb": from_espeak(g.strip(), True), "us": from_espeak(u.strip(), False)}
        results.extend(PHONEME_CACHE[w] for w in batch)

    return results


def main():
    with open(args.source) as jsf:
        irrverbs = json.load(jsf)

    headers = list(irrverbs[0].keys())
    p_headers = headers[0:3]

    # -- Step 1: Extract all words to be phonemized --
    all_words = [w for verb in irrverbs for k,v in verb.items() if k in p_headers for w in v.split('/')]

    # -- Step 2: Batch phonemizing
    _ = phonemize_batch(all_words)

    # -- Step 3: rebuild final list
    n_l = [
        {
            k: (expand_forms(v) if k in p_headers else v)
            for k, v in verb.items()
        }
        for verb in irrverbs
    ]

    with open(args.dest, 'w') as njsf:
        json.dump(n_l, njsf, ensure_ascii=False)


if __name__ == "__main__":
    start_time = time.time()
    main()
    print(f"[bold]Finished augmenting Irregular verbs in [red]{time.time() - start_time}[/red] seconds.[/bold]")
    exit(0)
