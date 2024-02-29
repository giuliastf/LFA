from src.NFA import NFA
from src.Regex import Regex
from src.Regex import parse_regex
from src.DFA import DFA

EPSILON = ''
SINK = 's'


class Lexer:
    def __init__(self, spec: list[tuple[str, str]]) -> None:
        self.last_state = None
        self.dfas = []
        self.nfa = NFA(set(), set(), 0, dict(), set())
        self.nfa.K.add(0)
        self.nfa.q0 = 0
        self.nfa.F = set()
        self.final_states = {}
        numar = 1
        if (0, EPSILON) not in self.nfa.d:
            self.nfa.d[(0, EPSILON)] = set()
        index = 0
        ok = False
        for token, regex in spec:
            reg = parse_regex(regex)
            inner_nfa = reg.thompson()
            # if token == "IDENTIFIER":
            #     ok = True


            remap = {}
            for state in inner_nfa.K:
                remap[state] = state + numar
                last_state = state + numar
            numar = last_state + 1
            remapped_d = {}
            for (state, symbol), next_states in inner_nfa.d.items():
                if isinstance(symbol, Regex):
                    remapped_symbol = symbol.data
                else:
                    remapped_symbol = symbol
                remapped_state = remap[state]  # starea noua corespunzatoare
                remapped_next_states = {remap[next_state] for next_state in next_states}
                remapped_d[(remapped_state, remapped_symbol)] = remapped_next_states

            remapped_F = {remap[state] for state in inner_nfa.F}
            remapped_q0 = remap[inner_nfa.q0]
            remapped_states = {remap[state] for state in inner_nfa.K}

            remapped_symbols = set()
            for symbol in inner_nfa.S:
                if isinstance(symbol, Regex):
                    remapped_symbols.update(symbol.data)
                else:
                    remapped_symbols.add(symbol)

            remapped_nfa = NFA(remapped_symbols, remapped_states, remapped_q0, remapped_d, remapped_F)

            self.nfa.d[(0, EPSILON)].add(remapped_nfa.q0)
            self.nfa.d.update(remapped_nfa.d)
            self.nfa.F.update(remapped_nfa.F)

            for s in remapped_nfa.F:
                self.final_states[s] = (token, index)  # Add the tuple to the set

            dfa = remapped_nfa.subset_construction()
            self.dfas.append((token, dfa))
            index += 1
            self.nfa.S.update(remapped_nfa.S)
            self.nfa.K.update(remapped_nfa.K)
            # if ok:
            #     print("aici")
            #     print(f"token: {token}")
            #     print(f"regex: {regex}")
            #     print(remapped_nfa)
        self.dfa = self.nfa.subset_construction()

    def recursive_function(self, current_state: frozenset, rest: str, processed: str, longest_match: str, token: str) -> tuple[str, str]:
        # pas 1: verific daca sunt in stare finala
        if current_state is None:
            return token, longest_match
        common_final_states = self.nfa.F.intersection(current_state)
        if common_final_states:
            # aleg starea cu id ul cel mai mic
            selected_state = min(common_final_states, key=lambda state: self.final_states[state][1])
            token = self.final_states[selected_state][0]
            longest_match = processed
        # pas 2: verific daca am ajuns la finalul cuvantului
        if rest:
            next_char = rest[0]
            next_state = self.dfa.d.get((current_state, next_char))
            return self.recursive_function(next_state, rest[1:], processed + next_char, longest_match, token)

        return token, longest_match

    def lex(self, word: str) -> list[tuple[str, str]] | None:
        result = []
        current_index = 0
        state = self.dfa.q0

        while current_index < len(word):
            char = word[current_index]
            token, longest_match = self.recursive_function(state, word[current_index:], "", "", "")

            line = word.count('\n', 0, current_index)
            pos_in_line = current_index - word.rfind('\n', 0, current_index)
            # print(f"token: {token}, longest_match: {longest_match}, line: {line}, pos_in_line: {pos_in_line} char: {word[current_index]}")
            if longest_match == "":
                if char not in self.dfa.S:
                    #print(f"token: {token}, longest_match: {longest_match}, line: {line}, pos_in_line: {pos_in_line}")
                    print(f"1 No viable alternative at character {pos_in_line-1}, line {line}")
                    return [("", f"No viable alternative at character {pos_in_line-1}, line {line}")]
                else:
                    if current_index == len(word) - 1:
                        print(f"1 No viable alternative at character EOF, line {line}")
                        return [("", f"No viable alternative at character EOF, line {line}")]
                    else:
                        print(f"No viable alternative at character {pos_in_line}, line {line}")
                        return [("", f"No viable alternative at character {pos_in_line}, line {line}")]

            result.append((token, longest_match))
            current_index += len(longest_match)
            state = self.dfa.q0

        return result
