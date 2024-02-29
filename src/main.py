from sys import argv
from src.Lexer import Lexer

class Node:
    def __init__(self, value, children=None, parent=None):
        self.value = value
        self.children = children if children is not None else []
        self.parent = parent

def print_tree(node, depth=0):
    indent = "  " * depth
    if node.value in ['list', 'concat', 'root', 'plus', 'lambda']:
        print(indent + f"{node.value}:")
        for child in node.children:
            print_tree(child, depth + 1)
    else:
        parent_info = f" : Parent {node.parent.value}" if node.parent else ''
        print(indent + f"{node.value}: {', '.join(node.children) if node.children else ''}{parent_info}")


def parse(tokens):
    stack = []
    root = Node('root')
    current = root
    for token in tokens:
        token_type, token_value = token

        if token_type == 'LPAREN':
            new_node = Node('list', parent=current)
            current.children.append(new_node)
            stack.append(current)
            current = new_node
        elif token_type == 'RPAREN':
            current = stack.pop()
        elif token_type == 'NUMBER':
            current.children.append(Node('number', [token_value], current))
        elif token_type == 'CONCAT':
            new_node = Node('concat', parent=current)
            current.children.append(new_node)
            current = new_node
        elif token_type == 'PLUS':
            new_node = Node('plus', parent=current)
            current.children.append(new_node)
            current = new_node
        elif token_type == 'EMPTY_LIST':
            current.children.append(Node('empty_list', parent=current))
        elif token_type == 'LAMBDA':
            lambda_node = Node('lambda', parent=current)
            current.children.append(lambda_node)
            stack.append(current)
            current = lambda_node
        elif token_type == 'IDENTIFIER':
            current.children.append(Node('identifier', [token_value], current))
    return root  # Return the root node

bool = False
def print_lambda(node):
    if node.value == 'lambda':
        param = node.children[0].children[0]
        body = node.children[1]
        argv = node.children[2]
        return f"(lambda {param}: {print_lambda(body)}) ({print_lambda(argv)})"
    elif node.value == 'list':
        return '(' + ' '.join(print_lambda(child) for child in node.children) + ')'
    elif node.value == 'number':
        return str(node.children[0])
    elif node.value == 'concat':
        return '++'
    elif node.value == 'plus':
        return '+'
    elif node.value == 'empty_list':
        return '()'
    elif node.value == 'identifier':
        return node.children[0]
    else:
        return ''


def evaluate(node, in_concat=False):
    global bool
    if node.value == 'list':
        result = []
        #print("number of children", len(node.children))
        for child in node.children:
            result.extend(evaluate(child, in_concat))
        if not in_concat and not bool:
            return ['('] + result + [')']
        return result
    elif node.value == 'number':
        return [int(node.children[0])]
    elif node.value == 'concat':
        # For concat nodes, evaluate each child and concatenate the results
        concat_results = [evaluate(child, True) for child in node.children]
        return flatten(concat_results)
    elif node.value == 'plus':
        in_plus = True
        bool = True
        plus_results = [evaluate(child, True) for child in node.children]
        return [sum(item for item in flatten(plus_results) if isinstance(item, int))]
    elif node.value == 'lambda':
        param = node.children[0]
        body = node.children[1]
        argv = node.children[2]
        param_list = create_param_list(node)
        arg_list = create_arg_list(node)

        d = create_dict(param_list, arg_list)

        most_inner_body = find_most_inner_body(body)
        if most_inner_body.value == 'lambda':
            my_body = most_inner_body.children[1]
        else:
            my_body = most_inner_body
            while my_body.value != 'identifier' and my_body.children[0].value != 'identifier':
                my_body = my_body.children[0]
                parent = my_body.parent

        replaced_body = my_body
        if my_body.value == 'list':
            if my_body.parent.value == 'plus':
                replaced_body = Node('list', parent= my_body)
                replaced_body = Node('plus', parent= replaced_body)
            else:
                replaced_body = Node('list', parent= node)
            for child in my_body.children:
                for param, value in d.items():
                    if child.children[0] == param:
                        replaced_body.children.append(value)

        elif my_body.value == 'identifier':
            bool = True
            for param, value in d.items():
                if my_body.children[0] == param:
                    replaced_body = value

        return evaluate(replaced_body)

    elif node.value == 'empty_list':
        parent = node.parent
        grandparent = node.parent.parent
        if grandparent and grandparent.value == 'concat':
            return []
        else:
            return ['()']

def create_param_list(node):
    param_list = []
    if node.value == 'lambda':
        param = node.children[0].children[0]
        body = node.children[1]
        argv = node.children[2]
        param_list.append(param)
        param_list.extend(create_param_list(body))
        param_list.extend(create_param_list(argv))
    return param_list

def create_arg_list(node):
    arg_list = []
    if node.value == 'lambda':
        param = node.children[0].children[0]
        body = node.children[1]
        argv = node.children[2]
        arg_list.append(argv)
        arg_list.extend(create_arg_list(body))
    return arg_list

def create_dict(param_list, arg_list):
    d = {}
    arg_list.reverse()
    for i in range(len(param_list)):
        d[param_list[i]] = arg_list[i]
    return d


def remove_redundant_parentheses(input_list):

    if len(input_list) == 3 and input_list[0] == '(' and input_list[-1] == ')':
        input_list.pop(0)
        input_list.pop(-1)
        return input_list

    count = 0
    for i in range(len(input_list)):
        if input_list[i] != '(' and input_list[i] != ')':
            count += 1
    if count == 1:
        i = 0
        j = -1
        while input_list[i] == '(' and input_list[j] == ')':
            input_list.pop(i)
            input_list.pop(j)
            i += 1
            j -= 1
    else:
        i = 1
        j = -2

    while input_list[i] == '(' and input_list[j] == ')':
        input_list.pop(i)
        input_list.pop(j)
        i += 1
        j -= 1


    return input_list
def find_most_inner_body(node):
    body = node
    if node.value == 'lambda':
        body = node.children[1]
        if node.children[1] == 'lambda':
            body = find_most_inner_body(node.children[1])

    return body


def flatten(lst):
    return [item for sublist in lst for item in sublist]

def formatted_output(result):
    result = remove_redundant_parentheses(result)
    #print(result)
    if not result:
        return "()"

    if len(result) == 1 and isinstance(result[0], int):
        return str(result[0])

    if result[0] != '(' and result[-1] != ')':

        return "( " + " ".join(map(str, result)) + " )"
    else:

        return " ".join(map(str, result))

def main():
    spec = [
        ("LAMBDA", "lambda"),
        ("CONCAT", r"\+\+"),
        ("PLUS", r"\+"),
        ("EMPTY_LIST", r"\(\)"),
        ("LPAREN", r"\("),
        ("RPAREN", r"\)"),
        ("NUMBER", "([1-9][0-9]*)|0"),
        ("IDENTIFIER", "([a-z]|[A-Z])+"),
        ("WHITESPACE", r"\ "),
        ("NEWLINE", "\n"),
        ("TAB", "\t"),
        ("COLON", ":")
    ]
    lexer = Lexer(spec)
    if len(argv) != 2:
        print("Usage: python3 main.py <input>")
        return
    file = argv[1]
    with open(file, 'r') as f:
        code = f.read()

    # tokens = lexer.lex("(lambda x: (+ (x x)) (1 2 3))")
    tokens = lexer.lex(code)
    # print(tokens)
    parsed = parse(tokens)
    # print_tree(parsed)
    #print_tree(parsed.children[0])
    result = evaluate(parsed.children[0])
    # print(result)
    formatted_result = formatted_output(result)
    print(formatted_result)

if __name__ == '__main__':
    main()
