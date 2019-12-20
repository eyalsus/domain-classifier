    def _create_random_domain_name(self, model, word_statistics, initial_state):
        domain_name = None
        word_list = [initial_state]
        current_state = initial_state
        while len(word_statistics[current_state]['transitions']) > 0:
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


{
    'appeareance': 17,
    'index': Counter({
        0: 9,
        1: 5,
        3: 3
    }),
    'sentence_length': Counter({
        3: 6,
        4: 5,
        2: 5,
        5: 1
    }),
    'transitions': Counter({
        'pay': 0,
        'problems': 2,
        'la': 1,
        'x': 1,
        'certain': 1,
        'v': 1,
        'pack': 1,
        'io': 1,
        'you': 1,
        'm': 1,
        'only': 1,
        'bank': 1,
        '7158': 1
    })
}


{
    'appeareance': 15,
    'index': Counter({
        0: 8,
        1: 3,
        2: 3,
        3: 1
    }),
    'sentence_length': Counter({
        2: 4,
        3: 7,
        5: 1,
        4: 3
    }),
    'transitions': Counter({
        'free': 0,
        'liker': 1,
        'o': 1,
        'you': 1,
        'get': 1,
        'click': 1,
        'gift': 1,
        'l': 1,
        'game': 1,
        'ia': 1,
        'host': 1,
        'movies': 1
    })
}
