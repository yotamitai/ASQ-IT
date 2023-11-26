import time

from backend import GLOBAL_VARS
from queries.common import log_msg
from interfaces.globals import DATA2QERY, CONSTRAINTS, AP
from queries.ltlf_local.parser_ltlf_local import LTLfParser
from functools import reduce


class DFA(object):
    def __init__(self, accepting, transitions, ap_dict):
        self.accepting_states = accepting
        self.initial = 1
        self.transitions = transitions
        self.ap_dict = ap_dict

    def startRun(self):
        self.curState = 1

    def step(self, letter):
        '''
        letter -- a set of symbols
        '''
        for (p, q, label) in self.transitions:
            if self.curState == p and EvalFormula(label, letter, self.ap_dict):
                self.curState = q
                break
        else:
            assert (False)  # must find one valid transition

        return True if self.curState in self.accepting_states else False

    def startBackRun(self):
        self.S = self.accepting_states

    def stepBack(self, letter):
        nS = []
        for (p, q, label) in self.transitions:
            if p in nS:
                continue

            if q in self.S and EvalFormula(label, letter, self.ap_dict):
                nS.append(p)

        self.S = nS

        return True if 1 in nS else False


class LTLfQuery(object):
    def __init__(self, query_data, seq_min_len, seq_max_len, domain, start_time, user_id):
        log_msg(f'\tLTLf:')
        self.ap_dict = AP[domain]
        self.start_time = start_time
        self.data = query_data
        self.min_seq_len = seq_min_len
        self.max_seq_len = seq_max_len
        self.user_id = user_id
        self.constraint_dict = dict(enumerate([x[0] for x in CONSTRAINTS[domain]]))
        self.pre_padding = 'X ' * 7 if self.data["pre_padding"] else ''  # query_data["padding"]
        if self.user_id == 'free_hand_ltlf':
            self.formula_str = self.query = query_data
        else:
            self.verify_data()
            log_msg(
                f'\t\tdata verified, \t\t\t\t TIME: {round(time.time() - self.start_time, 5)}')
            self.query = DATA2QERY[domain](self.data)
            log_msg(f'\t\tdata translated to query, \t TIME: '
                    f'{round(time.time() - self.start_time, 5)}')
            self.formula_str = getFormula(self.query)
            log_msg(f'\t\tformula string obtained, \t TIME: '
                    f'{round(time.time() - self.start_time, 5)}')
        self.formula_str = self.pre_padding + self.formula_str
        log_msg(f'\t\t\tString: {self.formula_str}')
        self.create_dfa()

    def verify_data(self):
        """verify that the inputs are correct"""
        for k, v in self.data.items():
            self.data[k] = None if v == "None" else v

    def create_dfa(self):
        parser = LTLfParser()
        formula = parser(f'F ({self.formula_str})')
        log_msg(
            f'\t\tforward formula obtained, \t TIME: {round(time.time() - self.start_time, 5)}')
        log_msg(f'\t\t\t{formula}')
        accepting_states, transitions = formula.to_dfa()
        log_msg(f'\t\tforward formula to dfa, \t TIME: {round(time.time() - self.start_time, 5)}')
        self.forward_dfa = DFA(accepting_states, transitions, self.ap_dict)
        log_msg(
            f'\t\tforward dfa created,     \t TIME: {round(time.time() - self.start_time, 5)}')

        parser = LTLfParser()
        formula = parser(self.formula_str)
        log_msg(
            f'\t\tbackward formula obtained, \t TIME: {round(time.time() - self.start_time, 5)}')
        log_msg(f'\t\t\t{formula}')
        accepting_states, transitions = formula.to_dfa()
        log_msg(
            f'\t\tbackward formula to dfa, \t TIME: {round(time.time() - self.start_time, 5)}')
        self.backward_dfa = DFA(accepting_states, transitions, self.ap_dict)
        log_msg(f'\t\tbackward dfa created,   \t TIME: {round(time.time() - self.start_time, 5)}')

    def search_traces(self, traces_dict, trace_constrains=[]):
        valid_seqs = []
        # valid_traces = []
        # for c in trace_constrains:
        #     if c in self.data.values():
        #         valid_traces = trace_constrains[c]
        #         break
        # if valid_traces:
        #     traces_dict = {k: traces_dict[k] for k in traces_dict if
        #                    k.split("_")[0] in valid_traces}

        for group, traces in traces_dict.items():
            for t_idx, trace in enumerate(traces):
                start_idx = 0
                while start_idx < len(trace) - self.min_seq_len:
                    found, seq = self.run_dfa(trace, start_idx)
                    if found:
                        start_idx = seq[1][1] + 1
                        valid_seqs.append(tuple(seq + [group]))
                    else:
                        start_idx = seq + 1  # index of last possible state

        return valid_seqs

    def run_dfa(self, trace, start):
        # if found=True - do not iterate states before 'start'.
        self.forward_dfa.startRun()
        for s1, i1 in trace[start:]:
            if self.forward_dfa.step(s1):
                if len(trace[start:i1[1] + 1]) < self.min_seq_len: continue  # trace is too short
                self.backward_dfa.startBackRun()
                for s2, i2 in reversed(trace[start:i1[1] + 1]):
                    if self.backward_dfa.stepBack(s2):
                        if len(trace[i2[1]:i1[1] + 1]) < self.min_seq_len:  # trace is too short
                            continue
                        elif self.max_seq_len and len(trace[i2[1]:i1[1] + 1]) > self.max_seq_len:
                            return False, i2[1]
                        return True, [i2, i1]

        return False, i1[1]


# class Constraint(object):
#     def __init__(self, type, params):
#         self.type = type


def EvalFormula(f, s, ap_dict):
    """s - state (vector of strings - predicates)
    f.name = AP (name of peridace)
    """
    if f.is_Atom:
        if f.is_Boolean:
            return 'BooleanTrue' in str(type(f))
        return s[ap_dict[f.name]] == 1

    if f.is_Not:
        return not EvalFormula(f.args[0], s, ap_dict)
    l = [EvalFormula(x, s, ap_dict) for x in f.args]
    if str(type(f)) == 'Or':
        return reduce(lambda x, y: x or y, l)
    if str(type(f)) == 'And':
        return reduce(lambda x, y: x and y, l)


def changesTo(ap1, ap2):
    return f'F(({ap1} & !{ap2}) & X F ({ap2} & !{ap1}))'


def changes(ap1):
    return f'F (({ap1}) & F(!{ap1}))'


def constant(ap1):
    return f'G({ap1})'


def occurs(ap1):
    return f'F({ap1})'


def notOccurs(ap1):
    return f'G(!{ap1})'


def getState(APs):
    if not any(APs):
        # "don't care" state
        return 'True'
    return '(%s)' % (' & '.join([x for x in APs if x]))


funcDict = {'changes': changes, 'staysconstant': constant, 'changesinto': changesTo,
            'occurs': occurs, 'notoccurs': notOccurs}


def getFormula(query):
    """parser from query to LTLf formula string"""
    s = getState(query['start'])
    e = getState(query['end'])
    if not query['constraints']:
        return f'({s} & X F (G ({e})))'
    const_string = getConsts(query['constraints'])
    return f'({s} & X F (G ({e}))) & {const_string}'


def getConsts(constraints):
    const_formulas = []
    for c in constraints:
        const_formulas.append(funcDict[c[0]](*c[1:]))
    consts = ' & '.join(const_formulas)
    return consts


if __name__ == '__main__':
    parser = LTLfParser()
    formula_str = "F((a & X(b) & X(X((b U c)))))"

    w1 = [[], ['b'], ['a'], ['c'], ['b'], ['c']]
    w2 = [[], ['b'], ['a'], ['b'], ['b'], ['c']]

    # formula_str = "F(a1 & (c1 U (a2 & (X (c2 U a3)))))"

    formula = parser(formula_str)

    accepting_states, transitions = formula.to_dfa()

    print(accepting_states)
    print(transitions)

    dfa = DFA(accepting_states, transitions)

    dfa.startRun()

    print('---- w1 -----')
    for a in w1:
        print(dfa.step(a))

    dfa.startRun()

    print('----- w2 -----')
    for a in w2:
        print(dfa.step(a))

    print('----- reversed w2 -----')
    dfa.startBackRun()
    for a in reversed(w2):
        print(dfa.stepBack(a))
