import wave
import contextlib
from os import path, listdir, makedirs, getcwd
import chardet
from shutil import copy, rmtree
from tqdm import tqdm
import logging
from tqdm.contrib.logging import logging_redirect_tqdm
from operator import attrgetter
from json import loads, dumps
from math import inf

LOG = logging.getLogger(__name__)

cdir = getcwd()

lang_map = {
    "bra": "Brazilian",
    "dan": "Danish",
    "dut": "Dutch",
    "fin": "Finnish",
    "fre": "French",
    "ger": "German",
    "int": "English (UK)",
    "ita": "Italian",
    "jap": "Japanese",
    "nor": "Norwegian",
    "pol": "Polish",
    "por": "Portuguese",
    "spa": "Spanish",
    "swe": "Swedish",
    "usa": "English (US)"
}

class VoiceLine:    
    def __init__(self, key: str, lang: str, voiceLine: str, duration: float = -1):
        self.lang = lang
        self.key = key
        self.voiceLine = voiceLine
        self.wavFile = path.join(cdir, 'langs', lang, 'audio', f"{key}.wav")
        if duration <= 0:
            self.duration = self.get_wav_duration()
        else:
            self.duration = duration
        
    def get_wav_file_path(self):
        p = path.join(cdir, 'langs', self.lang, 'audio')
        filenames = listdir(p)
        for fname in filenames:
            if fname.lower() == self.key.lower():
                return path.join(p, fname)
        return ""

    def exists(self):
        return path.exists(self.wavFile)

    def get_wav_duration(self):
        if self.exists():
            with contextlib.closing(wave.open(self.wavFile, 'r')) as f:
                frames = f.getnframes()
                rate = f.getframerate()
                return frames / float(rate)
            
    def __str__(self) -> str:
        return f'{{\n\t"lang": "{self.lang}",\n\t"key": "{self.key}",\n\t"voiceLine": "{self.voiceLine}",\n\t"duration": {self.get_wav_duration()}\n}}\n'


def voiceline_from_json(d):
    return VoiceLine(d['key'], d['lang'], d['voiceLine'], d['duration'])


def get_encoding(file):
    with open(file, 'rb') as raw_file:
        return chardet.detect(raw_file.read())

bumppath = './backup/bump'
voicepath = './backup/voice'

storage_path = './ready_for_export/shortest_lines'
audio_path = path.join(storage_path, 'audio_files')
lines_path = path.join(storage_path, 'system')

empty_voiceline = VoiceLine('', '', '', inf)

def main():
    if not path.exists('./backup'):
        print('Run main program first, to generate the backup folder')
        return
    else:
        if not path.exists(bumppath):
            print('Bumplines not available')
            return
        if not path.exists(voicepath):
            print('Voicelines not available')
            return
        
    # create the folder that stores the files
    if path.exists('./ready_for_export/shortest_lines'):
        rmtree(storage_path)
    makedirs(path.join(storage_path, 'Sounds'))
    makedirs(path.join(storage_path, 'system'))
    makedirs(audio_path)
    
    # Get the shortest voicelines
    voicelines = listdir(voicepath)
    
    voicelines_lines = "[All]\n"
    
    voicelines_langs_amount = {}
    
    for voiceline in tqdm(voicelines, desc='All Voicelines', unit="voiceline"):
        available_langs = listdir(path.join(voicepath, voiceline))
        current_shortest = empty_voiceline
        for lang in available_langs:
            with open(path.join(voicepath, voiceline, lang), 'r', encoding='utf-16') as file:
                lines = file.read()
                json = loads(lines)
                vl = voiceline_from_json(json)
                if vl.duration > 0 and vl.duration < current_shortest.duration and vl.exists():
                    current_shortest = vl   
        if current_shortest.key != "":   
            split = current_shortest.voiceLine.split("]")
            if (len(split) > 1):
                mood, line = split
            mood += "]"
            voicelines_lines += f"{current_shortest.key}={mood}[{lang_map[current_shortest.lang]}] {line}\n"
            copy(current_shortest.wavFile, path.join(audio_path, f"{current_shortest.key}.wav"))
            
            voicelines_langs_amount[lang_map[current_shortest.lang]] = voicelines_langs_amount.get(lang_map[current_shortest.lang], 0) + 1
        else:
            # print(voiceline, current_shortest)
            pass
        
    with open(path.join(lines_path, 'hpdialog.int'), 'w', encoding='utf-16') as hpdialog:
        hpdialog.write(voicelines_lines)
    
    print(dumps(voicelines_langs_amount, indent=4))
    
    with open(path.join(storage_path, 'stats_voice.json'), 'w') as stats:
        stats.write(dumps(voicelines_langs_amount, indent=4))
        
    
    
    
    # Get the shortest bumplines
    bumplines = listdir(bumppath)
    
    bumplines_lines = "[All]\n"
    
    bumplines_langs_amount = {}
    
    for bumpline in tqdm(bumplines, desc='All Bumplines', unit="bumpline"):
        available_langs = listdir(path.join(bumppath, bumpline))
        current_shortest = empty_voiceline
        for lang in available_langs:
            with open(path.join(bumppath, bumpline, lang), 'r', encoding='utf-16') as file:
                lines = file.read()
                json = loads(lines)
                vl = voiceline_from_json(json)
                if vl.duration > 0 and vl.duration < current_shortest.duration and vl.exists():
                    current_shortest = vl   
        if current_shortest.key != "":   
            split = current_shortest.voiceLine.split("]")
            if (len(split) > 1):
                mood, line = split
            mood += "]"
            bumplines_lines += f"{current_shortest.key}={mood}[{lang_map[current_shortest.lang]}] {line}\n"
            copy(current_shortest.wavFile, path.join(audio_path, f"{current_shortest.key}.wav"))
            
            bumplines_langs_amount[lang_map[current_shortest.lang]] = bumplines_langs_amount.get(lang_map[current_shortest.lang], 0) + 1
        else:
            # print(voiceline, current_shortest)
            pass
        
    with open(path.join(lines_path, 'BumpDialog.int'), 'w', encoding='utf-16') as bumpdialog:
        bumpdialog.write(voicelines_lines)
    
    print(dumps(bumplines_langs_amount, indent=4))
    
    with open(path.join(storage_path, 'stats_bump.json'), 'w') as stats:
        stats.write(dumps(bumplines_langs_amount, indent=4))
    
        
            
 
  
if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
        
    main()
    

