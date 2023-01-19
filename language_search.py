
from nltk.corpus import stopwords
from nltk.tokenize import RegexpTokenizer

stop_words = set(stopwords.words('english')).union({'domain', 'metaphor'})

# Don't remove the words that are used in query processing
for word in ('or','and', 'not', "isn't"):
    stop_words.remove(word)

tokenizer = RegexpTokenizer(r'\w+|"')

# Map similar words to respective fields
word_mapping = {
    'lyricist': 'lyricist', 'written': 'lyricist',
    'artist': 'artist', 'sung': 'artist', 'singer': 'artist',
    'source': 'source', 'about': 'source',
    'target': 'target'
}


def language_to_bool_query(query: str) -> str:
    """Convert natural language query to a boolean query"""
    
    # Remove stopwords
    word_tokens = tokenizer.tokenize(query.lower())
    filtered = [w for w in word_tokens if not w.lower() in stop_words]
    
    query = ""
    current_str = cur_logic = ""
    not_flag = term_started = False
    
    for term in filtered:
        # If word corresponds to any field
        if term in word_mapping:
            cur_logic += word_mapping[term].capitalize() + '=='
        elif term == '"':
            # Ending of a search term
            if term_started:
                cur_logic += f'"{current_str[:-1]}"'
                
                # Add NOT if not flag triggered
                query += f" NOT {cur_logic}" if not_flag else cur_logic
                
                # Reset variables
                current_str = cur_logic = ""
                term_started = not_flag = False
            # Beginning of a search term
            else:
                term_started = True
        # Term within the quotes
        elif term_started:
            current_str += term + ' '
        # Operator terms: and / or
        elif term in ('and', 'or'):
            query += " " + term.upper() + " "
        # Operator term: not
        elif term in ('not', "isn't"):
            not_flag = True
    
    return query.strip()
