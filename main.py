from h2o_wave import Q, main, app, ui, expando_to_dict
from es import search_all, search_regular

from language_search import language_to_bool_query
from parse_boolean import get_formatted_boolean_query


column_names = ['song', 'lyricist', 'artist', 'year', 'metaphor', 'source', 'target', 'meaning']
columns = [
    ui.table_column(name=f'tc_{col}', label=col.capitalize())
    for col in column_names
]

header_box = '1 1 -1 1'
search_box = '1 3 -1 2'
result_v_start = 5
result_h_end = 8
result_box = f'1 {result_v_start} {result_h_end} -1'
stat_box = f'{result_h_end + 1} {result_v_start} -1 6'
tabs_box = '1 2 3 1'
desc_box = '4 2 -1 1'
song_box = '2 2 4 5'


def get_header():
    return ui.header_card(
        box=header_box,
        title="Metaphor Search",
        subtitle="Sinhala Songs of the Last Decade",
        color='transparent',
        icon='MusicInCollectionFill',
        icon_color='#FFBF00'
    )


def initialize(q):
    q.page['meta'] = ui.meta_card(box='',
                                  title="Metaphor Search", 
                                  theme='h2o-dark',
                                  icon='https://cdn-icons-png.flaticon.com/512/5445/5445938.png')
    q.page['header'] = get_header()
    q.client.initialized = True
    q.client.tabs = 'filter'
    q.client.result_card_names = []
    

def get_tabs(q: Q):
    q.client.tabs = q.args.tabs or q.client.tabs or "filter"
    return ui.form_card(
        box=tabs_box,
        items=[
            ui.tabs(name='tabs', value=q.client.tabs, items=[
                ui.tab(name='filter', label='Filter Search'),
                ui.tab(name='language', label='Language Search'),
                ui.tab(name='bool', label='Boolean Search'),
            ])
        ]
    )
    

def get_description(tab: str):
    descriptions = {
        'filter': "Use the textboxes to specify the search criteria",
        'language': "Type a query in the search bar to search for metaphors. \
                Use `double quotes (\")` around search terms.\
                    \nE.g.: <span style=\"color: #00e1ff\">What are the metaphors with a source domain of `\"`tears`\"`? </span> ",
        'bool': "Type a boolean query in the search bar to search for metaphors. \
                \nE.g.: <span style=\"color: #00e1ff\">`(Artist==\"Ridma Weerawardena\" AND \
                (Lyricist==\"Chandrasena Thalangama\" AND NOT Lyricist==\"Charitha attalage\"))`</span>"
    }
    return ui.markdown_card(
        box=desc_box,
        title="",
        content=descriptions[tab]
    )


def get_stats_table(results):
    pass


def get_results_table(results):
    rows = []
    if results:
        for i, result in enumerate(results):
            rows.append(
                ui.table_row(
                    f"{i}",
                    cells=[
                        str(result['_source'][col.capitalize()])
                        for col in column_names
                    ]
                )
            )
    
    return ui.table(
        "result_table",
        columns=columns,
        rows=rows
    )


def get_metaphor_table(song_data: dict):
    metaphors = song_data['Metaphor'].split('\n')
    meanings = song_data['Meaning'].split('\n')
    source = song_data['Source'].split('\n')
    target = song_data['Target'].split('\n')
    metaphor_rows = list(zip(metaphors, meanings, source, target))
    
    return ui.table(
        'song_metaphor_table',
        columns=[ui.table_column(col, col.capitalize()) for col in ('metaphor', 'meaning', 'source', 'target')],
        rows=[ui.table_row(f'met_{i}', cells=list(met_row)) for i, met_row in enumerate(metaphor_rows)]
    )


def get_result_cards(results):
    if not results:
        return []
    cards = []
    card_height = 3
    for i, result in enumerate(results):
        cards.append(
            ui.form_card(
                box=f'1 {result_v_start + i * card_height} {result_h_end} {card_height}',
                items=[
                    ui.button(f'result_link_{i}', result['_source']['Song'], link=True),
                    ui.text(f"Lyricist(s): {result['_source']['Lyricist']}"),
                    ui.text("Metaphor(s):"),
                    get_metaphor_table(result['_source'])
                ]
            )
        )
    
    return cards


def get_stat_card(aggs):
    items = [
        ui.text_xl('Stats'),
        ui.separator(),
        ui.text_m(f"Year Range: `{int(aggs['year_stats']['min'])}` - `{int(aggs['year_stats']['max'])}`"),
        ui.separator(),
        ui.text_l('**Solo Lyricists**')
    ]
    
    for elem in aggs['solo_lyricists']['buckets']:
        items.append(ui.text(f"*{elem['key']}* ({elem['doc_count']})"))
    items.append(ui.text(f"Others ({aggs['solo_lyricists']['sum_other_doc_count']})"))
    
    
    return ui.form_card(
        box=stat_box,
        items=items
    )
            


def delete_result_cards(q: Q):
    for key in q.client.result_card_names:
        del q.page[key]
    q.client.result_card_names = []


def filter_search(q: Q):
    field_list = ('source', 'target', 'lyricist', 'artist')
    q.page['search_card'] = ui.form_card(
        box=search_box,
        title="",
        items=[
            ui.text_xl("Filter Search"),
            ui.inline([
                ui.textbox(
                    field, field.capitalize(), width='300px', value=q.args[field] if field in q.args else "")
                for field in field_list
            ], justify='between'),
            ui.inline([
                ui.toggle('tabular_results', "Tabular Results", value=q.client.tabular_results),
                ui.button('search_btn', "Search", primary=True)
            ], justify='end')
        ]
    )
    
    if q.args.search_btn:
        query = ""
        for field in field_list:
            if field in q.args and q.args[field]:
                query += f'{field} "{q.args[field]}" '
                q.client[field] = q.args[field]
        
        if query.strip():
            query = language_to_bool_query(query)
            formatted_query = get_formatted_boolean_query(query)
            res = search_regular(formatted_query)
        else:
            res = search_all()
            q.client.results = res['hits']['hits']
            q.client.aggs = res['aggregations']            


def query_search(q: Q, regular=True):
    q.page['search_card'] = ui.form_card(
        box=search_box,
        title="",
        items=[
            ui.text_xl("Query Search" if regular else "Boolean Search"),
            ui.textbox('search_bar', "", width='100%', value=q.args['search_bar'] or ""),
            ui.inline([
                ui.toggle('tabular_results', "Tabular Results", value=q.client.tabular_results),
                ui.button('search_btn', "Search", primary=True)
            ], justify='end')
        ]
    )
    
    if q.args.search_btn and q.args.search_bar:
        if regular:
            query = language_to_bool_query(q.args.search_bar)
        else:
            query = q.args.search_bar
        
        if query:
            formatted_query = get_formatted_boolean_query(query)
            res = search_regular(formatted_query)
        else:
            res = search_all()
        
        q.client.results = res['hits']['hits']
        q.client.aggs = res['aggregations']


def show_song_card(q, idx=None):
    if idx is not None:
        song_data = q.client.results[idx]['_source']
    else:
        song_data = q.client.results[int(q.args.result_table[0])]['_source']
    
    q.page['meta'].side_panel = ui.side_panel(
        title='',
        name="song_panel",
        items=[
            ui.text_xl(song_data['Song'] + f" ({song_data['Year']})"),
            ui.separator(),
            ui.text_l('Metaphors'),
            get_metaphor_table(song_data),
            ui.text_l('Artist(s)'),
            ui.text("* " + "\n* ".join(song_data['Artist'].split('; '))),
            ui.text_l('Lyricist(s)'),
            ui.text("* " + "\n* ".join(song_data['Lyricist'].split('; '))),
            ui.text_l('Composer(s)'),
            ui.text("* " + "\n* ".join(song_data['Composer'].split('; '))),
            ui.text_l('Lyrics'),
            ui.text("<span style=\"color: #87fdff\">" + song_data['Lyrics'].replace('\n', '<br>') + "</span>")
        ],
    )


@app('/')
async def serve(q: Q):
    # print(q.args)
    if not q.client.initialized:
        initialize(q)
    
    q.page['tabs_card'] = get_tabs(q)
    q.page['desc_card'] = get_description(q.client.tabs)
    
    idx = None
    arg_dict = expando_to_dict(q.args)
    for key in arg_dict:
        if arg_dict[key] and key.startswith('result_link_'):
            idx = int(key.split('_')[-1])
            break
    
    if q.args.tabular_results is not None:
        q.client.tabular_results = q.args.tabular_results
    
    if q.args.result_table or idx is not None:
        show_song_card(q, idx)
    else:
        delete_result_cards(q)
        q.page['meta'].side_panel = None
        
        if q.client.tabs == 'filter':
            filter_search(q)
        elif q.client.tabs == 'language':
            query_search(q)
        elif q.client.tabs == 'bool':
            query_search(q, False)
    
        if q.args.tabular_results:
            q.page['result_table'] = ui.form_card(
                box=result_box,
                items=[get_results_table(q.client.results)]
            )
            q.client.result_card_names.append('result_table')
        else:
            for i, card in enumerate(get_result_cards(q.client.results)):
                q.page[f'result_card_{i}'] = card
                q.client.result_card_names.append(f'result_card_{i}')
        
        if q.client.aggs:
            q.page['stat_card'] = get_stat_card(q.client.aggs)
    
    await q.page.save()
