import os
import sys
import argparse

from nltk.stem import WordNetLemmatizer


class Subs_Words_Extractor(object):

    def __init__(self):

        self.known_words = set()
        self.new_words = set()
        self.sub_words = set()
        self.ignored_words = set()
        self.known_words_file = os.path.abspath('./swe_word_list_known')
        self.ignored_words_file = os.path.abspath('./swe_word_list_ignored')
        self.new_words_file = os.path.abspath('./swe_word_list_new')
        self.subs_file = None

        self.parse_cmd_args()

        try:
            WordNetLemmatizer.lemmatize('zebra', 'v')
        except LookupError:
            print('wordnet dictionary not found, download it')
            import nltk
            nltk.download('wordnet')
        self.WNL = WordNetLemmatizer()

        self.load_known_words()
        self.load_ignored_words()

    def parse_cmd_args(self):
        description = 'script for extrating new words from english subtitles'

        self.parser = argparse.ArgumentParser(description=description)
        self.parser.add_argument(
            "--sub", help="subtitle file (with .ssa format)")

        self.args = self.parser.parse_args()

        self.subs_file = self.args.sub

    def load_known_words(self):
        if os.path.isfile(self.known_words_file):
            with open(self.known_words_file, encoding='utf-8') as f:
                for line in f:
                    word = line.strip()
                    if word and not word.startswith('#'):
                        self.known_words.add(word)
        else:
            with open(self.known_words_file, 'wt', encoding='utf-8') as f:
                pass  # create empty file

    def load_ignored_words(self):
        if os.path.isfile(self.ignored_words_file):
            with open(self.ignored_words_file, encoding='utf-8') as f:
                for line in f:
                    word = line.strip()
                    if word and not word.startswith('#'):
                        self.ignored_words.add(word)
        else:
            with open(self.ingnored_words_file, 'wt', encoding='utf-8') as f:
                pass  # create empty file

    def extract_new_words(self):
        if not self.subs_file:
            print('exit, subtitle file not specified {}\n'.format(
                self.subs_file))
            self.parser.print_help()
            sys.exit(1)
        if not self.subs_file.endswith('.ssa'):
            print('exit, unsupported file format\n')
            sys.exit(1)

        text_block_index = 0
        with open(self.subs_file, encoding='utf-8') as f:
            for line in f:
                if line.startswith('Format:') and 'Text' in line:
                    text_block_index = len(line.split(',')) - 1
                if line.startswith('Dialogue:'):
                    text = line.split(',', text_block_index)[-1].strip()
                    self.parse_ssa_text_line(text)

        self.filter_new_words()

        output_words = ''
        for el in sorted(self.new_words):
            output_words += el + '\n'
        with open(self.new_words_file, 'wt', encoding='utf-8') as f:
            f.write(output_words)

    def parse_ssa_text_line(self, text):
        line_sep = '\\N'
        sub_lines = text.split(line_sep)

        line_words = set()
        for sl in sub_lines:
            words = sl.split(' ')
            for w in words:
                w = w.lower()
                if "'" in w:
                    w = w.split("'")[0]
                if w.startswith('{'):
                    w = w.split('}')[-1]
                if w.endswith('}'):
                    w = w.split('{')[0]
                w = w.strip('!?., \t\n\\"\'0123456789:')
                if w:
                    line_words.add(
                        self.WNL.lemmatize(w, pos='v'))

        self.sub_words.update(line_words)

    def filter_new_words(self):
        self.new_words = (self.sub_words -
                          self.known_words) - self.ignored_words


def main():
    swe = Subs_Words_Extractor()
    swe.extract_new_words()
    print('all OK, open file words_list_new')


if __name__ == '__main__':
    main()
