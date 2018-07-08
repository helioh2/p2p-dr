from p2pdr import *
from sys import argv

DIRECTORY = "."
try:
    dir_mark = argv.index("-d")
    DIRECTORY = argv[dir_mark + 1]
except:
    pass

files_mark = argv.index("-f")

CONTEXTS = {}
CONTEXT_RULES = {}
LITERALS = {}

def save_literal(literal_text, context):
    negation = False
    literal_name, context_name = [lit.strip() for lit in literal_text.split("_")]  

    if literal_name[0] == '~':
        literal_name = literal_name[1:]
        negation = True                            
    if literal_name not in LITERALS.keys():
        if context_name == "local":
            context_name = context
        else:
            context_name = context_name.split("peer")[-1].upper()                                                        
        LITERALS[literal_name] = Literal(literal_name, CONTEXTS[context_name])

    if negation:
        return LITERALS[literal_name].negation
    else:
        return LITERALS[literal_name]
    
def create_contexts_and_preferences():
    for arg in argv[files_mark+1:]:
        CONTEXTS[arg] = Context(arg)
        try:
            with open(DIRECTORY+"/peer"+arg+"_trust.txt", "r") as f:
                mylist = f.read().splitlines()
                preferences = [x.split("peer")[-1].strip() for x in mylist if x != ""]
                CONTEXTS[arg].preferences = preferences
        except:
            pass

def create_literals_and_rules_by_context():
    for arg in argv[files_mark+1:]:
        with open(DIRECTORY+"/peer"+arg+"_rules.txt", "r") as f:
            mylist = f.read().splitlines()
            mylist = [line for line in mylist if line != "" and line[0] != "#"]
            for line in mylist:
                rule_type_id, rule_text = tuple(line.split(":"))
                body_text, head_text = tuple(rule_text.split("->"))
                literals_body = [x.strip() for x in body_text.split(",") if x.strip() != ""]
                head_text = head_text.strip()
                
                body = set()
                for x in literals_body:
                    body.add(save_literal(x, arg))                                               
                head = save_literal(head_text, arg)

                rule_type = rule_type_id[0]
                if rule_type == "L":
                    rule = LocalStrictRule(head, body)
                elif rule_type == "M":
                    rule = DefeasibleRule(head, body)
                if arg not in CONTEXT_RULES:
                    CONTEXT_RULES[arg] = {rule}
                else:
                    CONTEXT_RULES[arg].add(rule)


def main_loop():
    print("Contexts loaded:")
    print(CONTEXTS.keys())
    print("\n")
    context = input("Choose context to query from: ")
    while True:
        literal = input("Type query (literal): ")
        if literal[0] == "~":
            value, ss, bs = CONTEXTS[context].p2p_dr(LITERALS[literal[1:]].negation)
        else:
            value, ss, bs = CONTEXTS[context].p2p_dr(LITERALS[literal])
        print(value, [str(x) for x in ss], [str(x) for x in bs])


#MAIN
create_contexts_and_preferences()
create_literals_and_rules_by_context()

main_loop()


