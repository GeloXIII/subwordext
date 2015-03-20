import os
import sys
import argparse

import nltk
from nltk.stem import WordNetLemmatizer



class Subs_Words_Extractor(object):

    ptp_to_wn_map = {
        'JJ': 'a',
        'JJR': 'a',
        'JJS': 'a',
        'VB': 'v',
        'VBD': 'v',
        'VBG': 'v',
        'VBN': 'v',
        'VBP': 'v',
        'VBZ ': 'v',
        'RB': 'r',
        'RBR': 'r',
        'RBS': 'r',
        'RP ': 'r',
        'NN': 'n',
        'NNS': 'n',
        'NNP': 'n',
        'NNPS': 'n'
    }

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
            tmp = nltk.word_tokenize('zebra text')
            nltk.pos_tag(tmp)
        except LookupError:
            nltk.download('wordnet')
            nltk.download('maxent_treebank_pos_tagger')
            nltk.download('punkt')

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

        return len(self.new_words)

    def parse_ssa_text_line(self, text):
        line_sep = '\\N'
        sub_lines = text.split(line_sep)

        line_words = set()
        for sl in sub_lines:
            words_tag_pairs = nltk.pos_tag(nltk.word_tokenize(sl))
            for w, tag in words_tag_pairs:
                w = w.lower()
                w = w.strip(',')
                if w.isalpha():
                    wn_pos = self.ptp_to_wn_map.get(tag, 'x')
                    if wn_pos == 'x':
                        line_words.add(self.WNL.lemmatize(w))
                    else:
                        line_words.add(self.WNL.lemmatize(w, pos=wn_pos))

        self.sub_words.update(line_words)

    def filter_new_words(self):
        self.new_words = (self.sub_words -
                          self.known_words) - self.ignored_words


def main():
    swe = Subs_Words_Extractor()
    count = swe.extract_new_words()
    print('all OK, {} new words found'.format(count))


if __name__ == '__main__':
    main()
