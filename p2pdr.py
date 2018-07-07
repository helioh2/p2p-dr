
from enum import Enum


def rank(p, preferences):
    return 0 if p.context not in preferences else preferences.index(p.context) + 1

def stronger(set_a, set_b, preferences):
    
    the_stronger = None
    for a in set_a:
        found = False
        for b in set_b:
            if rank(a, preferences) < rank(b, preferences):
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
            if rank(b, preferences) < rank(a, preferences):
                found = True
                break
        if not found:
            the_stronger = "not B"
            break
    if the_stronger != "not B":
        return False

    return None


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
            if not unb or stronger(r.blocking_set, self.blocking_set, self.context.preferences):
                self.blocking_set = r.blocking_set
            unb = True
            if not r.cycle:
                if not sup or stronger(r.supportive_set, self.supportive_set, self.context.preferences):
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
                ans_b = p2p_dr(b, p.context)
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


def p2p_dr(p, context_0):
    '''
    p is a literal
    context_0 is the context that issues the query
    returns (ans:Boolean, ss:List, bs:List)
    '''
    local_ans_p = p.local_alg()
    if local_ans_p:
        p.supportive_set = p.blocking_set = set()
        return TruthValue.TRUE
    local_ans_not_p = p.negation.local_alg()
    if local_ans_not_p:
        p.supportive_set = p.blocking_set = set()
        return TruthValue.FALSE
    #call Support for p
    sup_p, unb_p = p.support()
    if not unb_p:
        return TruthValue.FALSE
    
    #call Support for not p
    p.negation.hist = (p.hist - {p}) | {p.negation}
    sup_not_p, unb_not_p =  p.negation.support()
    if sup_p and (not unb_not_p or stronger(p.supportive_set, 
                                p.negation.blocking_set, p.context.preferences)):
        if context_0 != p.context:
            p.supportive_set = p.blocking_set = set()
        return TruthValue.TRUE
    elif sup_not_p and not stronger(p.blocking_set, 
                                p.negation.supportive_set, p.context.preferences):
        return TruthValue.FALSE
    else:
        if context_0 != p.context:
            p.supportive_set = p.blocking_set = set()
        return TruthValue.UNDEFINED


# FAZER PARSER DE ARQUIVO!!






#MAIN
C1 = Context("C1", ["C3", "C2", "C4", "C5", "C6"])
C2 = Context("C2")
C3 = Context("C3")
C4 = Context("C4")
C5 = Context("C5")
C6 = Context("C6")

x1 = Literal("x1", C1)
a1 = Literal("a1", C1)
a2 = Literal("a2", C2)
a3 = Literal("a3", C3)
a4 = Literal("a4", C4)
a5 = Literal("a5", C5)
a6 = Literal("a6", C6)

rl11 = LocalStrictRule(x1, {a1})
rm12 = DefeasibleRule(a1, {a2})
rm13 = DefeasibleRule(a1.negation, {a3,a4})

rm21 = DefeasibleRule(a2, {a5})
rm22 = DefeasibleRule(a2.negation, {a6})

rl31 = LocalStrictRule(a3)
rl41 = LocalStrictRule(a4)
rl51 = LocalStrictRule(a5)

rd61 = DefeasibleRule(a6)
rl62 = LocalStrictRule(a6.negation)


print(p2p_dr(a4, C1))







    