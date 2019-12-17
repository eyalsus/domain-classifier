from collections import Counter
import pandas as pd
import numpy as np
import splitter
import tldextract
from algorithms.MarkovChain import MarkovChain
from Model.Model import Model


class MarkovModel(Model):
    def __init__(self, logger=None):
        super().__init__(logger)
        self._word_statistics = None
        self._states_set = None
        self._words_in_domain_counter = None
        self._markov_chain = None
        self.domain_name_set = None

    def train(self, X, y=None):
        super().train(X, y)
        domain_name_blacklist = set(X['domain_name'])
        self._word_statistics, self._states_set, self._words_in_domain_counter = \
            self._domain_to_word_features(domain_name_blacklist)
        words_transitions_prob = self._extract_transitions_probabilities(
            self._word_statistics, self._states_set)
        self._markov_chain = self._convert_probabilities_to_model(
            words_transitions_prob)
        self.domain_name_set = set()
        for word in self._states_set:
            for _ in range(10):
                predict_domain_name = self._create_random_domain_name(self._markov_chain, self._word_statistics, word)
                if predict_domain_name not in domain_name_blacklist:
                    self.domain_name_set.add(predict_domain_name)

    def predict(self, X=None):
        return X['domain_name'].apply(lambda x: int(x in self.domain_name_set))

    def _create_random_domain_name(self, model, word_statistics, initial_state):
        domain_name = None
        word_list = [initial_state]
        current_state = initial_state
        while len(word_list) < 25 and len(word_statistics[current_state]['transitions']) > 0:
            current_state = model.next_state(current_state)
            word_list.append(current_state)
            prob_dict = self._convert_counter_to_probabilities(
                word_statistics[current_state]['sentence_length'])
            current_word_sentence_length = np.random.choice(
                list(prob_dict.keys()), p=list(prob_dict.values()))
            if current_word_sentence_length <= len(word_list):
                break
        if len(word_list) > 1:
            domain_name = ''.join(word_list)
        return domain_name

    def _domain_to_word_features(self, domain_name_set):
        states_set = set()
        words_in_domain_counter = Counter()
        word_statistics = {}

        domain_index = 0
        for domain in domain_name_set:
            if domain_index % 100 == 0:
                self.logger.debug(domain_index)

            domain_index += 1
            # exr = tldextract.extract(domain)
            # consider adding .replace('-','')) #.replace('2', 'to').replace('4', 'for'))
            # words = splitter.split(exr.domain)
            words = splitter.split(domain)
            words = [word.lower() for word in words]
            words_in_domain_counter.update([len(words)])
            word_index = 0
            if isinstance(words, list) and len(words) > 1:
                for word in words:
                    if word not in word_statistics:
                        word_statistics[word] = {}
                        word_statistics[word]['appeareance'] = 0
                        word_statistics[word]['index'] = Counter()
                        word_statistics[word]['sentence_length'] = Counter()
                        word_statistics[word]['transitions'] = Counter()

                    word_statistics[word]['appeareance'] += 1
                    word_statistics[word]['sentence_length'].update(
                        [len(words)])
                    word_statistics[word]['index'].update([word_index])
                    word_index += 1

                next_word = words[-1]
                for word in reversed(words[:-1]):
                    word_statistics[word]['transitions'].update({word: 0})
                    word_statistics[word]['transitions'].update({next_word: 1})
                    states_set.add(word)
                    states_set.add(next_word)
        return word_statistics, states_set, words_in_domain_counter

    def _convert_counter_to_probabilities(self, transitions_counter, round_ndigits=8):
        transitions_probabilities = {}
        word_sum = sum(transitions_counter.values())

        for next_word, val in transitions_counter.items():
            transitions_probabilities[next_word] = round(
                val / word_sum, round_ndigits)
        row_sum = round(sum(transitions_probabilities.values()), round_ndigits)

        if row_sum != 1:
            error = round((row_sum - 1) * (10 ** round_ndigits))
            sign = -1 if error > 0 else 1
            adj_count = np.abs(error)
            for key in list(transitions_probabilities.keys())[1:]:
                transitions_probabilities[key] += sign * \
                    (10 ** (-1 * round_ndigits))
                adj_count -= 1
                if adj_count == 0:
                    break
        return transitions_probabilities

    def _extract_transitions_probabilities(self, word_statistics, states_set):
        words_transitions_prob = {}
        for word in states_set:
            words_transitions_prob[word] = self._convert_counter_to_probabilities(
                word_statistics[word]['transitions'])
        for state in states_set:
            if state not in words_transitions_prob:
                words_transitions_prob[state] = {}
        return words_transitions_prob

    def _convert_probabilities_to_model(self, words_transitions_prob):
        df = pd.DataFrame.from_dict(words_transitions_prob).T
        df.fillna(0, inplace=True)
        transition_matrix = df[df.index].to_numpy()
        model = MarkovChain(
            transition_matrix=transition_matrix, states=list(df.index))
        return model
