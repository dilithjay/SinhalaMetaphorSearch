
from nltk.corpus import stopwords
from nltk.tokenize import RegexpTokenizer

from es import search_filter

stop_words = set(stopwords.words('english')).union({'domain', 'metaphor'})
stop_words.remove('or')
stop_words.remove('and')
stop_words.remove('not')
stop_words.remove("isn't")
tokenizer = RegexpTokenizer(r'\w+|"')
word_mapping = {
    'lyricist': 'lyricist', 'written': 'lyricist',
    'artist': 'artist', 'sung': 'artist', 'singer': 'artist',
    'source': 'source', 'about': 'source',
    'target': 'target'
}


def language_to_bool_query(query: str) -> list:
    word_tokens = tokenizer.tokenize(query.lower())
    filtered = [w for w in word_tokens if not w.lower() in stop_words]
    
    query = ""
    current_str = cur_logic = ""
    not_flag = term_started = False
    
    for term in filtered:
        if term in word_mapping:
            cur_logic += word_mapping[term].capitalize() + '=='
        elif term == '"':
            if term_started:
                cur_logic += f'"{current_str[:-1]}"'
                query += f" (NOT {cur_logic})" if not_flag else cur_logic
                
                current_str = cur_logic = ""
                term_started = not_flag = False
            else:
                term_started = True
        elif term_started:
            current_str += term + ' '
        elif term in ('and', 'or'):
            query += " " + term.upper() + " "
        elif term in ('not', "isn't"):
            not_flag = True
    
    return query.strip()


def search_query(query: str):
    search_terms = language_to_bool_query(query)        
    
    return search_filter(search_terms)
