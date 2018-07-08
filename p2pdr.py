
from enum import Enum


def rank(p, preferences):
    return 0 if p.context not in preferences else preferences.index(p.context) + 1




class TruthValue(Enum):
    TRUE = 1
    FALSE = 2
    UNDEFINED = 3

class Context:
    def __init__(self, name, preferences=[]):
        self.name = name
        self.preferences = preferences
        self.vocabulary = set()
        self.local_strict_rules = set()
        self.defeasible_rules = set()

    def __str__(self):
        return self.name

    def __eq__(self, other):
        return self.name == other

    def __hash__(self):
        return hash(self.name)

    def rank(self, p):
        return 0 if p.context == self \
                    else self.preferences.index(p.context) + 1

    def stronger(self, set_a, set_b):   
        the_stronger = None
        for a in set_a:
            found = False
            for b in set_b:
                if self.rank(a) < self.rank(b):
                    found = True
                    break
            if not found:
                the_stronger = "not A"
                break
        if the_stronger != "not A":
            return True

        for b in set_b:
            found = False
            for a in set_a:
                if self.rank(b) < self.rank(a):
                    found = True
                    break
            if not found:
                the_stronger = "not B"
                break
        if the_stronger != "not B":
            return False

        return None

    def p2p_dr(self, p):
        '''
        p is a literal
        self is the context that issues the query
        returns (ans:Boolean, ss:List, bs:List)
        '''
        local_ans_p = p.local_alg()
        if local_ans_p:
            p.supportive_set = p.blocking_set = set()
            return TruthValue.TRUE, p.supportive_set, p.blocking_set
        local_ans_not_p = p.negation.local_alg()
        if local_ans_not_p:
            p.supportive_set = p.blocking_set = set()
            return TruthValue.FALSE, p.supportive_set, p.blocking_set
        
        #call Support for p
        sup_p, unb_p = p.support()
        if not unb_p:
            return TruthValue.FALSE, p.supportive_set, p.blocking_set
               
        p.negation.hist = (p.hist - {p}) | {p.negation}
        #call Support for not p
        sup_not_p, unb_not_p =  p.negation.support()
        if sup_p and (not unb_not_p or self.stronger(p.supportive_set, 
                                    p.negation.blocking_set)):
            if self != p.context:
                p.supportive_set = p.blocking_set = set()
            return TruthValue.TRUE, p.supportive_set, p.blocking_set
        elif sup_not_p and not self.stronger(p.blocking_set, 
                                    p.negation.supportive_set):
            return TruthValue.FALSE, p.negation.supportive_set, p.negation.blocking_set
        else:
            if self != p.context:
                p.supportive_set = p.blocking_set = set()
            return TruthValue.UNDEFINED, p.supportive_set, p.blocking_set


class Literal:
    def __init__(self, name, context, negation=False):
        self.name = name
        self.context = context
        self.context.vocabulary.add(self)
        self.local_strict_rules = set()
        self.defeasible_rules = set()
        if not negation:
            self.negation = Literal("~"+name, context, self)
        else:
            self.negation = negation

        self.reset()

    def reset(self):
        self.supportive_set = set()
        self.blocking_set = set()
        self.hist = set()

    @property
    def rules(self):
        return self.local_strict_rules | self.defeasible_rules

    def local_alg(self):
        if not self.local_strict_rules:
            return False
        for r in self.local_strict_rules:
            for b in r.body:
                local_ans_b = b.local_alg()
                if not local_ans_b:
                    return False
        return True

    def support(self):
        sup = unb = False
        for r in self.rules:
            res = r.traverse_body(self)
            if not res: continue
            if not unb or self.context.stronger(r.blocking_set, self.blocking_set):
                self.blocking_set = r.blocking_set
            unb = True
            if not r.cycle:
                if not sup or self.context.stronger(r.supportive_set, self.supportive_set):
                    self.supportive_set = r.supportive_set
                sup = True
        return sup, unb

    def __str__(self):
        return self.name

    def __eq__(self, other):
        return self.name == other

    def __hash__(self):
        return hash(self.name)


class Rule:
    def __init__(self, head, body=set()):
        self.body = body
        self.head = head
        self.cycle = False
        self.reset()

    def reset(self):
        self.supportive_set = set()
        self.blocking_set = set()

    def traverse_body(self, p):
        self.cycle = False
        self.reset()
        for b in self.body:
            if b in p.hist:
                self.cycle = True
                self.blocking_set.add(b)
            else:
                b.hist = p.hist | {b}
                ans_b,_,_ = p.context.p2p_dr(b)
                if ans_b is TruthValue.FALSE:
                    return False
                elif ans_b is TruthValue.UNDEFINED or self.cycle:
                    self.cycle = True
                    if b not in p.context.vocabulary:
                        self.blocking_set.add(b)
                    else:
                        self.blocking_set = self.blocking_set | b.blocking_set
                else: #ans_b is true
                    if b not in p.context.vocabulary:
                        self.blocking_set.add(b)
                        self.supportive_set.add(b)
                    else:
                        self.blocking_set = self.blocking_set | b.blocking_set
                        self.supportive_set = self.supportive_set | b.supportive_set
        return True



class DefeasibleRule(Rule):
    def __init__(self, *args, **kwargs):
        Rule.__init__(self, *args, **kwargs)     
        self.head.defeasible_rules.add(self)
        self.head.context.defeasible_rules.add(self)

class LocalStrictRule(Rule):
    def __init__(self, *args, **kwargs):
        Rule.__init__(self, *args, **kwargs)
        self.head.local_strict_rules.add(self)
        self.head.context.defeasible_rules.add(self)
