import wave
import contextlib
from os import path, listdir, makedirs, getcwd
import chardet
from random import choice
from shutil import copy, rmtree
from tqdm import tqdm
import logging
from tqdm.contrib.logging import logging_redirect_tqdm
from operator import attrgetter

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
    def __init__(self, key: str, lang: str, voiceLine: str):
        self.lang = lang
        self.key = key
        self.voiceLine = voiceLine
        self.wavFile = path.join(cdir, 'langs', lang, 'audio', f"{key}.wav")
        self.duration = self.get_wav_duration()
        
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


def get_encoding(file):
    with open(file, 'rb') as raw_file:
        return chardet.detect(raw_file.read())



def main():
    bumplines = {}
    voicelines = {}

    langs = listdir('./langs')

    bumpline_keys = set()
    voiceline_keys = set()
    
    for lang in tqdm(langs, desc="Extracting all voicelines for all different languages", unit="language"):     
        # Load all the textual voicelines inside the program
        enc = get_encoding(path.join(cdir, 'langs', lang, f"BumpDialog.{lang}"))
        with open(path.join(cdir, 'langs', lang, f"BumpDialog.{lang}"), 'r', encoding=enc['encoding']) as b:
            lines = b.read().strip().split("\n")[1:]
            for line in lines:
                key, text = line.split("=")
                if not key in bumplines:
                    bumplines[key] = {}
                bumpline_keys.add(key)
                vl = VoiceLine(key, lang, text)
                if vl.exists():
                    bumplines[key][lang] = vl

        enc = get_encoding(path.join(cdir, 'langs', lang, f"HpDialog.{lang}"))
        with open(path.join(cdir, 'langs', lang, f"HpDialog.{lang}"), 'r', encoding=enc['encoding']) as d:
            lines = d.read().strip().split("\n")[1:]
            for line in lines:
                key, text = line.split("=")
                if not key in voicelines:
                    voicelines[key] = {}
                voiceline_keys.add(key)
                vl = VoiceLine(key, lang, text)
                if vl.exists():
                    voicelines[key][lang] = vl
                    
    if not path.exists('./lines'):
        makedirs("./lines")
                    
    with open('./lines/bumplines.keys', 'w') as bl:
        bumplines_sorted_list = [f"{line}\n" for line in bumpline_keys]
        bumplines_sorted_list.sort()
        bl.writelines(bumplines_sorted_list)
    with open('./lines/voicelines.keys', 'w') as vl:
        voicelines_sorted_list = [f"{line}\n" for line in voiceline_keys]
        voicelines_sorted_list.sort()
        vl.writelines(voicelines_sorted_list)
    
    for key in tqdm(bumplines.keys(), desc="Backing up bumplines", unit="line"):
        if not path.exists(f'./backup/bump/{key}'):
            makedirs(f'./backup/bump/{key}')
        for lang in tqdm(bumplines[key].keys(), desc=f"Backing up langs, for line {key}", unit="lang", leave=False):
            with open(f'./backup/bump/{key}/{lang}.json', 'w', encoding='utf-16') as kll:
                kll.write(str(bumplines[key][lang]))
                
    for key in tqdm(voicelines.keys(), desc="Backing up voicelines", unit="line"):
        if not path.exists(f'./backup/voice/{key}'):
            makedirs(f'./backup/voice/{key}')
        for lang in tqdm(voicelines[key].keys(), desc=f"Backing up langs, for line {key}", unit="lang", leave=False):
            with open(f'./backup/voice/{key}/{lang}.json', 'w', encoding='utf-16') as kll:
                kll.write(str(voicelines[key][lang]))            
        
        
    # pick a random voicelines from each voicelines
    folder = 'longest_lines'
    if path.exists(f"./ready_for_export/{folder}"):
        rmtree(f'ready_for_export/{folder}')
    makedirs(f"./ready_for_export/{folder}/Sounds")
    makedirs(f"./ready_for_export/{folder}/system")
    
    bumplines_str = "[All]\n"
    voicelines_str = "[All]\n"
    
    bumplines_missing_list = []
    voicelines_missing_list = []
    
    used_langs = {}
    
    with logging_redirect_tqdm():  
        for key in tqdm(bumplines.keys(), desc="Getting random bumplines", unit="line"):
            if len(list(bumplines[key])) > 0:
                # lang = choice(list(bumplines[key].keys()))
                # line = bumplines[key][lang]
                line = max(list(bumplines[key].values()), key=attrgetter('duration'))
                lang = line.lang
                while line.get_wav_duration() <= 0:
                    lang = choice(list(bumplines[key].keys()))
                    line = bumplines[key][lang]
                used_langs[lang] = used_langs.get(lang, 0) + 1
                split_line = line.voiceLine.split("]")
                bumplines_str += f"{line.key}={split_line[0]}][{lang_map[lang]}] {split_line[1]}\n"
                copy(line.wavFile, path.join(cdir, 'ready_for_export', str(folder), 'Sounds', f"{line.key}.wav"))
            else: 
                bumplines_missing_list.append(line)
                
        for key in tqdm(voicelines.keys(), desc="Getting random voicelines", unit="line"):
            if len(list(voicelines[key])) > 0:
                # lang = choice(list(voicelines[key].keys()))
                # line = voicelines[key][lang]
                line = max(list(voicelines[key].values()), key=attrgetter('duration'))
                lang = line.lang
                while line.get_wav_duration() <= 0:
                    lang = choice(list(voicelines[key].keys()))
                    line = voicelines[key][lang]
                used_langs[lang] = used_langs.get(lang, 0) + 1
                split_line = line.voiceLine.split("]")
                voicelines_str += f"{line.key}={split_line[0]}][{lang_map[lang]}] {split_line[1]}\n"
                copy(line.wavFile, path.join(cdir, 'ready_for_export', str(folder), 'Sounds', f"{line.key}.wav"))
            else: 
                voicelines_missing_list.append(line)
        
        print(f"Missing {len(bumplines_missing_list)} bumplines\nMissing {len(voicelines_missing_list)} voicelines")
        
        with open(f'./ready_for_export/{str(folder)}/missing-lines.txt', 'w', encoding='utf-16') as ml:     
            lines = bumplines_missing_list + voicelines_missing_list  
            ml.writelines([str(line) for line in lines])
            
        with open(f'./ready_for_export/{str(folder)}/system/BumpDialog.int', 'w', encoding='utf-16') as bl:
            bl.write(bumplines_str)
            
        with open(f'./ready_for_export/{str(folder)}/system/hpdialog.int', 'w', encoding='utf-16') as vl:
            vl.write(voicelines_str)
        
        with open(f'./ready_for_export/{str(folder)}/stats.txt', 'w') as st:
            st.writelines([f"{lang_map[key]} is used {used_langs[key]} times\n" for key in used_langs.keys()])
        
        print(f"Finished: {folder}")
                
 
  
if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
        
    main()
    

