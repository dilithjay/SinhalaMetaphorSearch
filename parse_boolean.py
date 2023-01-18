def get_highest_operation(query):
    highest_op = (float('inf'), '', 0)
    for op in ('OR', 'AND', 'NOT'):
        cur_level = 0
        for i in range(len(query) - 3):
            if query[i] == '(':
                cur_level += 1
            elif query[i] == ')':
                cur_level -= 1
            elif cur_level < highest_op[0] and  query[i: i + len(op)] == op:
                highest_op = (cur_level, op, i)
    return highest_op


def expression_to_dict(query):
    key, value = list(map(lambda x: x.strip(), query.split('==')))
    
    return {
        "match": {
            key.capitalize() + '.case_insensitive_and_inflections': value[1: -1]
        }
    }


def get_formatted_boolean_query(query):
    highest_op = get_highest_operation(query)
    
    # Remove redundant external brackets
    if highest_op[1]:
        if highest_op[0] > 0:
            query = query[highest_op[0]: len(query) - highest_op[0]]
            highest_op = (0, highest_op[1], highest_op[2] - highest_op[0])
    else:
        cur_i = 0
        while query[cur_i] == '(':
            cur_i += 1
        query = query[cur_i: len(query) - cur_i]
    
    if highest_op[1] == 'AND':
        return {
            "bool": {
                "must": [
                    get_formatted_boolean_query(query[:highest_op[2]].strip()),
                    get_formatted_boolean_query(query[highest_op[2] + 3:].strip())
                ]
            }
        }
    elif highest_op[1] == 'OR':
        return {
            "bool": {
                "should": [
                    get_formatted_boolean_query(query[:highest_op[2]].strip()),
                    get_formatted_boolean_query(query[highest_op[2] + 2:].strip())
                ]
            }
        }
    elif highest_op[1] == 'NOT':
        return {
            "bool": {
                "must_not": [
                    get_formatted_boolean_query(query[highest_op[2] + 3:].strip())
                ]
            }
        }
    else:
        return expression_to_dict(query)
