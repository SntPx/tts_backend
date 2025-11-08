# Code comes from official Misaki repo: https://github.com/hexgrad/misaki/blob/main/EN_PHONES.md
import re
FROM_ESPEAKS = sorted({
                          '\u0303': '',
                          'a^ɪ': 'I',
                          'a^ʊ': 'W',
                          'd^ʒ': 'ʤ',
                          'e': 'A',
                          'e^ɪ': 'A',
                          'r': 'ɹ',
                          't^ʃ': 'ʧ',
                          'x': 'k',
                          'ç': 'k',
                          'ɐ': 'ə',
                          'ɔ^ɪ': 'Y',
                          'ə^l': 'ᵊl',
                          'ɚ': 'əɹ',
                          'ɬ': 'l',
                          'ʔ': 't',
                          'ʔn': 'tᵊn',
                          'ʔˌn\u0329': 'tᵊn',
                          'ʲ': '',
                          'ʲO': 'jO',
                          'ʲQ': 'jQ'
                      }.items(), key=lambda kv: -len(kv[0]))


def from_espeak(ps, british):
    for old, new in FROM_ESPEAKS:
        ps = ps.replace(old, new)
    ps = re.sub(r'(\S)\u0329', r'ᵊ\1', ps).replace(chr(809), '')
    if british:
        ps = ps.replace('e^ə', 'ɛː')
        ps = ps.replace('iə', 'ɪə')
        ps = ps.replace('ə^ʊ', 'Q')
    else:
        ps = ps.replace('o^ʊ', 'O')
        ps = ps.replace('ɜːɹ', 'ɜɹ')
        ps = ps.replace('ɜː', 'ɜɹ')
        ps = ps.replace('ɪə', 'iə')
        ps = ps.replace('ː', '')
    return ps.replace('^', '')


def to_espeak(ps):
    # Optionally, you can add a tie character in between the 2 replacement characters.
    ps = ps.replace('ʤ', 'dʒ').replace('ʧ', 'tʃ')
    ps = ps.replace('A', 'eɪ').replace('I', 'aɪ').replace('Y', 'ɔɪ')
    ps = ps.replace('O', 'oʊ').replace('Q', 'əʊ').replace('W', 'aʊ')
    return ps.replace('ᵊ', 'ə')
