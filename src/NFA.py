from .DFA import DFA

from dataclasses import dataclass
from collections.abc import Callable

EPSILON = ''
SINK = 's'

@dataclass
class NFA[STATE]:
    S: set[str]  # alphabet
    K: set[STATE]  # states
    q0: STATE  # initial state
    d: dict[tuple[STATE, str], set[STATE]]  # transition function
    F: set[STATE]  # final states

    def epsilon_closure(self, state: STATE) -> set[STATE]:
        epsilon_set = set()
        visited = set()

        def explore_epsilon(current_state):
            if current_state in visited:
                return
            visited.add(current_state)  # mark as visited
            epsilon_transitions = self.d.get((current_state, EPSILON), set())  # get epsilon transitions
            epsilon_set.add(current_state)  # add to epsilon set
            for epsilon_state in epsilon_transitions:
                explore_epsilon(epsilon_state)  # explore epsilon transitions
        explore_epsilon(state)

        return epsilon_set

    def subset_construction(self) -> DFA[frozenset[STATE]]:
        alphabet = self.S
        # star_state = big state (set of states) from small state q0
        start_state = frozenset(self.epsilon_closure(self.q0))  # dfa start state = epsilon closure of nfa start state
        dfa_states = {start_state}  # set of dfa states
        unvisited = [start_state]  # unvisited dfa states
        dfa_transitions = {}    # dfa transitions

        while unvisited:
            outer_state = unvisited.pop()  # current state = big state (set of states)
            for symbol in alphabet:
                next_states = set()
                for inner_state in outer_state:  # inner_state = small state from the big one
                    transitions = self.d.get((inner_state, symbol), set())  # get transitions from the small state
                    for state in transitions:
                        e = self.epsilon_closure(state)
                        if e not in next_states:
                            next_states.update(e)   # add epsilon closure of the transition state to next states
                if next_states:
                    next_dfa_state = frozenset(next_states)
                else:
                    next_dfa_state = frozenset(SINK)
                dfa_transitions[(outer_state, symbol)] = next_dfa_state  # add transition to dfa transitions
                if next_dfa_state not in dfa_states:
                    dfa_states.add(next_dfa_state)
                    unvisited.append(next_dfa_state)

        dfa_final_states = {state for state in dfa_states if any(nfa_state in self.F for nfa_state in state)}

        return DFA(alphabet, dfa_states, start_state, dfa_transitions, dfa_final_states)

    def remap_states[OTHER_STATE](self, f: 'Callable[[STATE], OTHER_STATE]') -> 'NFA[OTHER_STATE]':
        # optional, but may be useful for the second stage of the project. Works similarly to 'remap_states'
        # from the DFA class. See the comments there for more details.
        pass
