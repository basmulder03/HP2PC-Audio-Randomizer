# HP2PC Audio Randomizer

## Used Languages

| # | Language | Language Code |
| --- | --- | --- |
| **1** | Brazilian | bra |
| **2** | Danish | dan |
| **3** | Dutch | dut |
| **4** | Finnish | fin |
| **5** | French | fre |
| **6** | German | ger |
| **7** | English (UK) | int |
| **8** | Italian | ita |
| **9** | Japanese | jap |
| **10** | Norwegian | nor |
| **11** | Polish | pol |
| **12** | Portuguese | por |
| **13** | Spanish | spa |
| **14** | Swedish | swe |
| **15** | English (US) | usa |

## What is available

*These files need to be downloaded because of GitHub file size limit [mediafire](https://www.mediafire.com/file/qwolxnfvxars3gm/langs.zip/file)*

In the subfolder langs are 15 different folders for all the different HP2PC langs that have voicelines (there are a few without voicelines like Chinese and Thai). Each of those language folders container three files and one folder. The first file is `AllDialog.{lang_code_uppercase}_uax`. These is the compressed audio files from unreal engine of that language in the game. 

Next to that is also the file `BumpDialog.{lang_code}`. This file contains all the subtitles from all the bumpdialogs of that language that are available in the game.

The last file in the folder is the file `HpDialog.{lang_code}`. This file contains all the subtitles from all the voicelines in the game (except the bumpdialog lines) of that specific language.

The folder that is available in each language folder called `audio` contains all the extracted voicelines and bumplines from the AllDialog.{lang_code_uppercase}_uax file.

## How it works

*The [requirements.txt](./requirements.txt) file contains the requirements for all different scripts to be able to run*

In the root of the project, there are different files, I will get to them one by one.

The first file is [convert_japanese_to_readable_format.py](./convert_japanese_to_readable_format.py). This file is ment change the default japanese characters that are in the subtitles of the [bumplines](./langs/jap/BumpDialog.jap.backup) and the [voicelines](./langs/jap/HpDialog.jap.backup) to the version that uses normal asciicharacters instead of the japanese characters (newly generated [bumplines](./langs/jap/BumpDialog.jap) and [voicelines](./langs/jap/HpDialog.jap))
The reason for this, is because the japanese characters are not rendered by the game by default, so the lines would be empty when the japanese subtitles should have been rendered.

The second file [longest.py](./longest.py) should be the script where instead of getting a random language, the shortest voiceline should be used this is still a work in progress is not yet functional.

The third file [script.py](./script.py) is the file will pick a random language for each voiceline. It will create the folder `backup` which contains the folders `bump` and `voice` which contains folders for each audio key for every bump and voiceline in the correct directory. Then it will create json files for each voice and bumpline with the nameformat `{language_code}.json`. An example of such a file is `bra.json` inside the `./backup/bump/PC_Drc_DracoNotHeir_23` folder.
```json
{
	"lang": "bra",
	"key": "PC_Drc_DracoNotHeir_23",
	"voiceLine": "[Normal]Vá logo, então. Eu não quero continuar vendo essa expressão de dor na sua cara. ",
	"duration": 3.867936507936508
}
```
There will also be a folder generated called `lines`. This folder contains two files, `bumplines.keys` and `voicelines.keys`. These files only contain each key that is available for use from all the voicelines and bumplines that are read and backed up.

The last and most import folder that is being created is `ready_for_export`. This folder will contain the changed subtitles files and the wav files that are moved. Each time that the program is run a new folder is created inside the `ready_for_export` folder with and uuidv4 as the name to make it unique. That folder contains two subfolders and two files. The files are `missing-lines.txt` whicha are the voicelines that couldn't be found or moved. For me that total amount is always the same 19 voicelines. 
Next to the `missing-lines.txt` there is also a `stats.txt` which contains the amount of times each language is used in this mod.
The folders that are created are `system` and `Sounds`. The `system` folder contains the files `BumpDialog.int` and `hpdialog.int` which will replace the default files to the modded ones so that the subtitles of the game change to reflect the different languages.
The folder `Sounds` contains all the wav files that are being used by the mod. These wav files still need to be compressed to an `AllDialog.uax` file using the `UnrealEd.exe` editor (Preferable [metallicafan212's editor](https://github.com/metallicafan212)).