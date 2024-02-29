from collections.abc import Callable
from dataclasses import dataclass


@dataclass
class DFA[STATE]:
    S: set[str]  # alphabet
    K: set[STATE]  # states
    q0: STATE  # initial state
    d: dict[tuple[STATE, str], STATE]  # transition function
    F: set[STATE]  # final states

    # d[(q, a), q'] means that if the dfa is in state q and reads input a, it will transition to state q'
    def accept(self, word: str) -> bool:
        # simulate the dfa on the given word. return true if the dfa accepts the word, false otherwise
        current_state = self.q0
        for c in word:
            if (current_state, c) not in self.d:
                return False
            current_state = self.d[(current_state, c)]  # transition to next state
        return current_state in self.F  # check if the final state is in the set of final states

    def remap_states[OTHER_STATE](self, f: Callable[[STATE], 'OTHER_STATE']) -> 'DFA[OTHER_STATE]':
        # optional, but might be useful for subset construction and the lexer to avoid state name conflicts.
        # this method generates a new dfa, with renamed state labels, while keeping the overall structure of the
        # automaton.

        # for example, given this dfa:

        # > (0) -a,b-> (1) ----a----> ((2))
        #               \-b-> (3) <-a,b-/
        #                   /     ⬉
        #                   \-a,b-/

        # applying the x -> x+2 function would create the following dfa:

        # > (2) -a,b-> (3) ----a----> ((4))
        #               \-b-> (5) <-a,b-/
        #                   /     ⬉
        #                   \-a,b-/

        pass

