from .NFA import NFA


class Regex:
    def __init__(self, data):
        self.data = data
        self.left = None
        self.right = None

    def __str__(self):
        return '(' + str(self.left) + ' ' + self.data + ' ' + str(self.right) + ')'

    def thompson(self) -> NFA[int]:
        stack = [self]
        nfa = NFA(set(), set(), 0, dict(), set())
        nfa.K.add(0)
        nfa.K.add(1)
        nfa.q0 = 0
        nfa.F = set()
        nfa.F.add(1)
        idx = 1
        transitions = [(0, 1)]

        while stack:
            tree = stack.pop()
            symbol = tree.data
            trans = transitions.pop()
            if tree.left == None and tree.right == None:
                nfa.d[(trans[0], symbol)] = {trans[1]}
                nfa.S.add(tree.data)
            else:
                if symbol == '&':
                    #  0 ------ a.b ------- 1
                    #  0 ------ a ------- 2 ------ eps ------ 3 ------- b ------- 1

                    old = idx  # old = 1
                    idx += 2  # idx = 3

                    nfa.K.add(old + 1)  # 2
                    nfa.K.add(old + 2)  # 3

                    nfa.d[old+1, ''] = {old+2}  # 2 -> 3

                    if tree.right:
                        transitions.append((idx, trans[1]))  # (3, 1)
                        stack.append(tree.right)
                    if tree.left:
                        transitions.append((trans[0], idx - 1))  # (0, 2)
                        stack.append(tree.left)

                elif symbol == '|':
                    #  0 ------ a|b ------- 1
                    #     | 2 --- a --- 4 |
                    #     0                1
                    #     | 3 --- b --- 5 |

                    old = idx  # old = 1
                    idx += 4 # idx = 5 , adaug 4 noi stari

                    for i in range(old+1, idx+1):
                        nfa.K.add(i)

                    nfa.d[trans[0], ''] = {old + 1, old + 2}  # 0 -> 2, 0 -> 3
                    nfa.d[idx - 1, ''] = {trans[1]}  # 4 -> 1
                    nfa.d[idx, ''] = {trans[1]}  # 5 -> 1

                    if tree.right:
                        transitions.append((idx-2, idx))  # (4, 5)
                        stack.append(tree.right)
                    if tree.left:
                        transitions.append((idx-3, idx))  # (2, 3)
                        stack.append(tree.left)

                elif symbol in {'*', '?', '+'}:

                    #  0 ------ a* ------- 1
                    #               <----eps----- la ? nu am asta
                    #  0 ---eps-----2-----a-----3-----eps-----1
                    #  ------------------eps------------------>  la plus nu am asta

                    old = idx  # old = 1 la inceput
                    idx += 2  # idx = 3

                    for i in range(old+1, idx+1):
                        nfa.K.add(i)

                    if symbol == '*':
                        nfa.d[trans[0], ''] = {old+1, trans[1]}  # 0 -> 1, 0 -> 2
                        nfa.d[idx, ''] = {trans[1], idx-1}  # 3 -> 1
                    elif symbol == '?':
                        nfa.d[trans[0], ''] = {trans[1], old + 1}  # 0 -> 1, 0 -> 2
                        nfa.d[idx, ''] = {trans[1]}  # 3 -> 1
                    elif symbol == '+':
                        nfa.d[trans[0], ''] = {old+1}  # 0 -> 2
                        nfa.d[idx, ''] = {trans[1], idx - 1}  # 3 -> 1 / 3 -> 2

                    if tree.left:
                        transitions.append((idx-1, idx))  # (2, 3)
                        stack.append(tree.left)
        return nfa


def function(s: list) -> list:

    if len(s) == 1:
        return [Regex(s[0])]
    while '(' in s:
        counter = 0
        start = s.index('(')
        end = 0
        for i in range(start, len(s)):
            if s[i] == '(':
                counter += 1
            elif s[i] == ')':
                counter -= 1
            if counter == 0:
                end = i
                break
        s = s[:start] + function(s[start+1:end]) + s[end+1:]

    i = 1
    while i < len(s):
        if s[i] in {'*', '?', '+'}:
            aux = s[i-1]
            s[i] = Regex(s[i])
            s[i].left = Regex(aux) if not isinstance(aux, Regex) else aux
            s = s[:i-1] + s[i:]
        else:
            i += 1

    i = 1
    while i < len(s):
        if s[i] == '&':
            first = s[i-1]
            second = s[i+1]
            s[i] = Regex('&')
            s[i].left = Regex(first) if not isinstance(first, Regex) else first
            s[i].right = Regex(second) if not isinstance(second, Regex) else second
            s = s[:i-1] + [s[i]] + s[i+2:]
        else:
            i += 1

    i = 1
    while i < len(s):
        if s[i] == '|':
            first = s[i-1]
            second = s[i+1]
            s[i] = Regex('|')
            s[i].left = Regex(first) if not isinstance(first, Regex) else first
            s[i].right = Regex(second) if not isinstance(second, Regex) else second
            s = s[:i-1] + [s[i]] + s[i+2:]
        else:
            i += 1

    return s


def parse_regex(regex: str) -> Regex:

    prio = {'&', '|', '*', "+", '?', '(', ')'}
    s = ''
    regex = regex.replace("[a-z]", '(a|b|c|d|e|f|g|h|i|j|k|l|m|n|o|p|q|r|s|t|u|w|v|x|y|z)')
    regex = regex.replace("[A-Z]", '(A|B|C|D|E|F|G|H|I|J|K|L|M|N|O|P|Q|R|S|T|U|W|V|X|Y|Z)')
    regex = regex.replace("[0-9]", '(0|1|2|3|4|5|6|7|8|9)')
    regex = regex.replace("[1-9]", '(1|2|3|4|5|6|7|8|9)')
    s_list = []
    ok = False
    aux = ''
    for i in range(len(regex)):
        if regex[i] == '\\':
            ok = True
            continue
        if ok:
            ok = False
            if i > 1 and ((regex[i] not in prio and aux not in prio) or (regex[i] == '(' and aux not in prio) or (aux in {'+', '*', '?'} and regex[i] == '(') or (aux in {'+', '*', '?'} and regex[i] not in prio) or (regex[i] == '(' and aux == ')') or aux in {'*', '?', '+', ')'} or s_list[-1] not in prio or (aux == ')' and regex[i] not in prio)):
                s_list.append('&')
            s_list.append(Regex(regex[i]))
            continue
        if regex[i] == ' ':
            continue

        if (i > 0) and ((regex[i] not in prio and aux not in prio) or (regex[i] == '(' and aux not in prio) or (aux in {'+', '*', '?'} and regex[i] == '(') or (aux in {'+', '*', '?'} and regex[i] not in prio) or (regex[i] == '(' and aux == ')') or (s_list[-1] not in prio and regex[i] == '(') or (aux == ')' and regex[i] not in prio)):
            s_list.append('&')
            s_list.append(regex[i])
            aux = regex[i]
        else:
            s_list.append(regex[i])
            aux = regex[i]

    tree = function(s_list)
    return tree[0]
