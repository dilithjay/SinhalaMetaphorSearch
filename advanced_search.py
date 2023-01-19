# Define fields to be used for advanced search
fields_no_analyzers = ['Lyricist', 'Artist', 'Source', 'Target']
fields = [
    'Lyricist.case_insensitive',
    'Artist.case_insensitive',
    'Source.case_insensitive_and_inflections',
    'Target.case_insensitive_and_inflections'
]


def advanced_search_to_formatted_query(all_these, this_exact, any_these, none_these):
    query = {}
    if all_these:
        query['must'] = []
        for term in all_these.split():
            query['must'].append(
                {'query_string': {
                    'query': term, 
                    'fields': fields}
                 }
            )
    if this_exact:
        query['must'] = query.get('must', [])
        query['must'].append(
            {
                'query_string': {
                    'query': f'"{this_exact}"', 
                    'fields': fields_no_analyzers
                }
            }
        )
    if any_these:
        query['should'] = []
        for term in any_these.split():
            query['should'].append(
                {
                    'query_string': {
                        'query': term, 
                        'fields': fields
                    }
                }
            )
    if none_these:
        query['must_not'] = []
        for term in none_these.split():
            query['must_not'].append(
                {
                    'query_string': {
                        'query': term, 
                        'fields': fields
                    }
                }
            )
    return {'bool': query}