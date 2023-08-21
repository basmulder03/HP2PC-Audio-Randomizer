import hasami
import jphones as j2p
import japanese_numbers

Phonetizer = j2p.phonetizer.Phonetizer()

replace_map = {
    '！': '! ',
    '？': '? ',
    '。': '.',
    '、': ' ',
    '･': ' ',
    '～': '~ ',
    '「': '"',
    '」': '" ',
    '､': ' ',
    '\u3000': ' ',
    '『': '"',
    '』': '" ',
    '－': '-',
    '．': '.',
    'Ｑ': 'Q.'
}

bumplines = ['[All]']

with open('./langs/jap/BumpDialog.jap.backup', 'r', encoding='utf-16') as f:
    lines = f.read().strip().split("\n")[1:]
    for line in lines:
        key, value = line.split("=")
        mood, text = value.split(']')
        mood += "]"
        segments = hasami.segment_sentences(text)
        new_line = key + "=" + mood + " ".join([''.join(Phonetizer.get_phonemes({'token': segment, 'type': 'word'})['phonemes']) for segment in segments]) + "\n"
        for char in new_line:
            if not char.isascii() and not char.isnumeric():
                new_line = new_line.replace(char, replace_map[char])
        bumplines.append(new_line)

with open('./langs/jap/BumpDialog.jap', 'w', encoding='utf-8') as f:
    f.writelines(bumplines)

dialoglines = ['[All]']
    
with open('./langs/jap/HpDialog.jap.backup', 'r', encoding='utf-16') as f:
    lines = f.read().strip().split("\n")[1:]
    for line in lines:
        key, value = line.split("=")
        mood, text = value.split(']')
        mood += "]"
        segments = hasami.segment_sentences(text)
        new_line = key + "=" + mood + " ".join([''.join(Phonetizer.get_phonemes({'token': segment, 'type': 'word'})['phonemes']) for segment in segments]) + "\n"
        for char in new_line:
            if not char.isascii() and not char.isnumeric():
                new_line = new_line.replace(char, replace_map[char])
        dialoglines.append(new_line)

with open('./langs/jap/HpDialog.jap', 'w', encoding='utf-8') as f:
    f.writelines(dialoglines)