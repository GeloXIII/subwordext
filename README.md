Script for extracting new words from subtitles
----------------------------------------------


It extract **_new_** words from .ssa subs and translate.

And exclude all words from list of known and ignored.

For expamle: known word may be top 5000 english words.

###Dependecies

* **nltk**
* **numpy**
* **yandex-translate** - put api key to `swe_yandex_translate.key` file

###Example usage

`python3 subwordext.py --sub sutitle.ssa --translate en-ru --add-to-knew`

###Parametres

####requried
* *--sub* - subtitle file .ssa

####optional
* *--translate* - translate direction for example en-ru
* *--add-to-known* - bool flag, add all extracted words to list of known
