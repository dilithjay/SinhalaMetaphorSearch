
from nltk.corpus import stopwords
from nltk.tokenize import RegexpTokenizer

from es import search_filter

stop_words = set(stopwords.words('english')).union({'domain', 'metaphor'})
stop_words.remove('or')
stop_words.remove('and')
stop_words.remove('not')
tokenizer = RegexpTokenizer(r'\w+|"')
word_mapping = {
    'lyricist': 'lyricist', 'written': 'lyricist',
    'artist': 'artist', 'sung': 'artist', 'singer': 'artist',
    'source': 'source', 'about': 'source',
    'target': 'target'
}


def get_search_terms(query: str) -> list:
    word_tokens = tokenizer.tokenize(query.lower())
    
    filtered = [w for w in word_tokens if not w.lower() in stop_words]
    
    search_keys = []
    search_vals = []
    current_str = ''
    term_started = False
    
    for term in filtered:
        if term in word_mapping:
            search_keys.append(word_mapping[term].capitalize() + '.case_insensitive_and_inflections')
        elif term == '"':
            if term_started:
                search_vals.append(current_str[:-1])
                current_str = ''
                term_started = False
            else:
                term_started = True
        elif term_started:
            current_str += term + ' '
    
    assert len(search_keys) == len(search_vals), \
           f"Error in interpreting the query; Keys: {search_keys}, Vals: {search_vals}"
    
    return tuple(zip(search_keys, search_vals))


def search_query(query: str):
    search_terms = get_search_terms(query)        
    
    return search_filter(search_terms)
