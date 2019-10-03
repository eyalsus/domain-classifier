import pandas as pd
import numpy as np 
from collections import Counter
from MarkovChain import MarkovChain
import splitter
from sqlalchemy import create_engine
import tldextract
import argparse
import os
import pickle
def main():

    parser = argparse.ArgumentParser()
    parser.add_argument("--input-pickle", type=str, help="path to words features pickle input")
    parser.add_argument("--output-pickle", type=str, help="path to words features pickle output")
    parser.add_argument("--output-domains", type=str, help="path domain names output")
    parser.add_argument("--limit", type=int, default=1000, help="limit")
    args = parser.parse_args()

    word_statistics = states_set = words_in_domain_counter = None
    if args.input_pickle:
        if os.path.isfile(args.input_pickle):
            with open(args.input_pickle, 'rb') as f:
                word_statistics, states_set, words_in_domain_counter = pickle.load(f)
    else:
        query_string = f'''
        SELECT DISTINCT lower(base_domain) as base_domain
        FROM domains
        WHERE label = 1
        AND base_domain NOT IN ('000webhostapp.com', 'azurewebsites.net')
        AND domain_name NOT LIKE '%%-%%'
        LIMIT {args.limit}
        '''

        engine = create_engine('postgresql://postgres:mypassword@localhost:5432/')
        input_df = pd.read_sql_query(query_string, engine)
        print (f'input_df: {len(input_df)}')
        word_statistics, states_set, words_in_domain_counter = domain_to_word_features(list(input_df['base_domain']))


        if args.output_pickle:
            with open(args.output_pickle, 'wb') as f:
                pickle.dump((word_statistics, states_set, words_in_domain_counter), f)
    
    words_transitions_prob = extract_transitions_probabilities(word_statistics, states_set)
    model = convert_probabilities_to_model(words_transitions_prob)
    domain_name_set = set()
    for word in states_set:
        for _ in range(5):
            domain_name_set.add(create_random_domain_name(model, word_statistics, word))
    series = pd.Series(list(domain_name_set))
    series.to_csv(args.output_domains, index=False, header=False)

def create_random_domain_name(model, word_statistics, initial_state):
    domain_name = None
    word_list = [initial_state]
    current_state = initial_state
    while len(word_list) < 25 and len(word_statistics[current_state]['transitions']) > 0:
        current_state = model.next_state(current_state)
        word_list.append(current_state)
        p = convert_counter_to_probabilities(word_statistics[current_state]['sentence_length'])
        current_word_sentence_length = np.random.choice(list(p.keys()), p=list(p.values()))
        if current_word_sentence_length <= len(word_list):
            break
    if len(word_list) > 1:                
        domain_name = ''.join(word_list)
    return domain_name


def domain_to_word_features(domain_list):
    states_set = set()
    words_in_domain_counter = Counter()
    word_statistics = {}

    domain_index = 0
    for domain in domain_list:         
        if domain_index % 100 == 0:
            print (domain_index)

        domain_index += 1
        exr = tldextract.extract(domain)
        words = splitter.split(exr.domain) #.replace('-','')) #.replace('2', 'to').replace('4', 'for'))
        words = [word.lower() for word in words]
       
        words_in_domain_counter.update([len(words)])
        word_index = 0
        if type(words) == list and len(words) > 1:
            for word in words:
                if word not in word_statistics:
                    word_statistics[word] = {}
                    word_statistics[word]['appeareance'] = 0
                    word_statistics[word]['index'] = Counter()
                    word_statistics[word]['sentence_length'] = Counter()
                    word_statistics[word]['transitions'] = Counter()

                word_statistics[word]['appeareance'] += 1
                word_statistics[word]['sentence_length'].update([len(words)])
                word_statistics[word]['index'].update([word_index])
                word_index += 1

            next_word = words[-1]
            for word in reversed(words[:-1]):
                word_statistics[word]['transitions'].update({word: 0})
                word_statistics[word]['transitions'].update({next_word: 1})
                states_set.add(word)
                states_set.add(next_word)
    return word_statistics, states_set, words_in_domain_counter
                    
                    
def convert_counter_to_probabilities(transitions_counter, round_ndigits=8):    
    transitions_probabilities = {}
    word_sum = sum(transitions_counter.values())

    for next_word, val in transitions_counter.items():
        transitions_probabilities[next_word] = round(val / word_sum, round_ndigits)
    row_sum = round(sum(transitions_probabilities.values()), round_ndigits)
    
    if row_sum != 1:
        error = round((row_sum - 1) * (10 ** round_ndigits))
        sign = -1 if error > 0 else 1
        adj_count = np.abs(error)
        for key in list(transitions_probabilities.keys())[1:]:
            transitions_probabilities[key] += sign * (10 ** (-1 * round_ndigits))
            adj_count -= 1
            if adj_count == 0:
                break
                
    return transitions_probabilities


def extract_transitions_probabilities(word_statistics, states_set):
    words_transitions_prob = {}
    for word in states_set:
        words_transitions_prob[word] = convert_counter_to_probabilities(word_statistics[word]['transitions'])
        
    for state in states_set:
        if state not in words_transitions_prob:
            words_transitions_prob[state] = {}
    
    return words_transitions_prob


def convert_probabilities_to_model(words_transitions_prob):
    df = pd.DataFrame.from_dict(words_transitions_prob).T
    df.fillna(0, inplace=True)
    transition_matrix = df[df.index].to_numpy()
    model = MarkovChain(transition_matrix=transition_matrix, states=list(df.index))
    return model


if __name__ == "__main__":
    main()
