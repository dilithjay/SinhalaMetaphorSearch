from elasticsearch import Elasticsearch

es = Elasticsearch([{"host": 'localhost', "port": 9200, "scheme": 'http'}], http_auth=('elastic', 'elastic'))
assert es.ping()

aggregations = {
    "solo_lyricists": {
        "terms": { "field": "Lyricist.keyword" }
    },
    "year_stats": { 
        "stats": { "field": "Year" } 
    }
}

def search_all():
    return es.search(
        index='sinhala-song-metaphors',
        body={
            "size": 1000,
            "query" : { "match_all" : {} },
            "aggs": aggregations
        }
    )


def search_filter(search_terms: tuple):
    return es.search(
        index='sinhala-song-metaphors',
        body={
            "size": 1000,
            "query": {
                "bool": {
                    "must": [
                        {"match": {key: value}} for key, value in search_terms
                    ]
                }
            },
            "aggs": aggregations
        }
    )


def search_regular(query: str):
    return es.search(
        index='sinhala-song-metaphors',
        body={
            "size": 1000,
            "query": query,
            "aggs": aggregations
        }
    )
