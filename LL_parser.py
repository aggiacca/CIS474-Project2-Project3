from copy import deepcopy

class State:
    def __init__(self, num, targetRs,):
        self.number = num

        # rules to check / interested in (underlined ones in example)
        # list of Rule
        self.targetRules = targetRs

        # closure of target rules
        # list of Rule
        # self.closureExtras = dependency


        # add next character its checking for transition diagram later?
        # keep track of previous or next state?
        # list of tuple (symbol: Rule) representing goto
        self.gotoStates = []

        self.transitions = {}

class Rule:
    def __init__(self, num, nonterminal, dependency):
        self.order = num
        self.lhs = nonterminal
        self.rhs = dependency

    def print_rule(self):
        print("Original Rule Number: {0}, Left-hand side: {1}, Right-hand-side: {2}".format(self.order, self.lhs, self.rhs))


def addDotToStart(rule):
    rule.rhs = "." + rule.rhs
    return rule


# rules = original grammar and list of Rule
def closure(targetNT, rules, nonterminals):

    # to avoid modifying rules outside of scope
    tempRules = deepcopy(rules)
    # first take any rules where targetChar is on the left hand side
    #   then add dot to beginning of rhs
    finalClosure = [addDotToStart(i) for i in tempRules if i.lhs is targetNT]

    # consider adding start symbol case here

    queue = []

    for rule in finalClosure:
        dotPos = rule.rhs.find(".")
        nextChar = rule.rhs[dotPos+1]
        if nextChar not in queue and nextChar in nonterminals and nextChar is not targetNT:
            queue.append(nextChar)

    # check sub rules
    while not len(queue) == 0:
        target = queue.pop()
        # consider removing rules already checked in case of possible edge cases
        subClosure = [addDotToStart(i) for i in tempRules if i.lhs is target]
        for rule in subClosure:
            dotPos = rule.rhs.find(".")
            nextChar = rule.rhs[dotPos + 1]
            finalClosure.append(rule)
            if nextChar not in queue and nextChar in nonterminals and nextChar is not target:
                queue.append(nextChar)

    return finalClosure

    # check subclosure
    # option 1 to recursivly take closure of chars to the right of dots
    # option 2 use stack to avoid duplicates


def checkItems(items, rhs):
    for state in items:
        for rule in state.targetRules:
            if rule.rhs == rhs:
                return True
    return False


# curState : State
# X : terminal or nonterminal char
def goto(curState, originalRules, X, nonterminals, terminals):
    J = []

    closuresAdded = []
    for rule in curState.targetRules:
        pos = rule.rhs.find("." + X)
        if pos != -1:
            # 1 for start a 0 and 1 for checking if X is last in list
            if pos+2 >= len(rule.rhs):
                # .X is last so just move over and add. no closure
                temp = rule.rhs[:pos] + rule.rhs[pos+1:] + "."

                # can't just do rule.rhs = temp as it will update original since its just reference
                J.append(Rule(rule.order, rule.lhs, temp))
            else:
                # grab char in front of dot after wouldbe move
                nextChar = rule.rhs[pos+2:pos+3]

                # move dot over
                temp = rule.rhs[:pos] + rule.rhs[pos+1:pos+2] + "." + rule.rhs[pos+2:]
                # can't just do rule.rhs = temp as it will update original since its just reference
                J.append(Rule(rule.order, rule.lhs, temp))
                if nextChar in nonterminals and nextChar not in closuresAdded:
                    # copy of orginal rules since closure modifies original rules
                    tempList = deepcopy(closure(nextChar, originalRules, nonterminals))
                    J.extend(tempList)
                    closuresAdded.append(nextChar)
    # TODO: consider returning a object that seprates the closure rules and rules that had the dot moved over
    return J



# checks if a state's rules's rhs are the exact same
def compareStateRules(state1, state2):
    if len(state1.targetRules) != len(state2.targetRules):
        return False

    isEqual = False
    # not sure we can gaurentee order is same so more elaborate check
    for rule1 in state1.targetRules:
        for rule2 in state2.targetRules:
            if rule1.rhs == rule2.rhs:
                isEqual = True
                # found match so stop checking the rest/avoid setting to false again is hit is middle
                break

        # no matches for rule1 in state2's rules so return False
        if not isEqual:
            return isEqual

    # all match. so return true
    return isEqual

# goes through states and checks if state already exists
def checkIfStateExists(states, targetState):
    for state in states:
        if compareStateRules(state, targetState):
            return True
    return False


def generate_items(rules, nonterminals, terminals):
    augmentedRule = deepcopy(rules[0])
    allSymbols = nonterminals + terminals
    items = []
    queue = []

    # double check augmented rule
    stateCounter = 0
    if augmentedRule.lhs.find("'") != -1:

        initialState = State(stateCounter, closure(augmentedRule.rhs, rules, nonterminals))

        # add start symbol rule as current closure function does not cover it
        initialState.targetRules.insert(0, addDotToStart(augmentedRule))

        items.append(initialState)
        queue.append(initialState)
        stateCounter += 1

        while not len(queue) == 0:
            # remove first
            curState = queue.pop(0)

            for symbol in allSymbols:
                newState = State(stateCounter, goto(curState, rules, symbol, nonterminals, terminals))
                if newState is not None and len(newState.targetRules) != 0 and not checkIfStateExists(items, newState):
                    # queue is not a deepcopy of state compared to items.
                    # So curState should reference same object in item meaning it should update item
                    # Add goto linkage
                    curState.gotoStates.append((symbol, newState))
                    curState.transitions[symbol] = newState.number

                    items.append(newState)
                    queue.append(newState)
                    stateCounter += 1
    else:
        print("augmented grammar start issue")

    return items

# Pre-conditions:
#   items is in state order and first state includes everything/grammar creates tiers
# Post-condition: each item (state) should have its transition dict updated
#
def generate_transition_diagram(items, follow_table, rules, nonterminals, terminals):

    # TODO: each char in the extra closure of a goto goes to the same state across all goto's
    # algo to find the state for nonspecial closure
    #   start at base state and check the goto links that match target char.
    # for special goto/target goto's. modify goto/set of items to build links between

    for state in items:
        # skip initial state as all transitions are done
        if state.number != 0:
            for rule in state.targetRules:
                print("change me")
                # check char after dot in each rule
                # check if that char is in transitions
                # if no in transitions find goto state:
                #   simple implmentation 1: of just checking the first state does not work for I11 in example
                #   simple implementation 2: starting at state 0, look at 0's transition table and then see if match
                #       if no match then go to state 1,2,3. hopefully grammar is setup so there are no closure repeats before all symbols have been goto'd once



    print("To    |", end='')
    for i in range(len(items)-1):
        print("{0} ".format(i), end='')

    print("\n-------------", end='')
    for i in range(len(items)-1):
        print("--", end='')

    # Decide whether this function shouldgenerate transition diagram to modify tables
    #   or if closure and goto should be updated





# items = list of States
def generate_parsing_table(items, follow_table, rules, nonterminals, terminals):

    # print table header
    print("s ", end='')
    for i in range(len(terminals)):
        if i == len(terminals) / 2:
            print('actions', end='')
            i += len('actions')
        else:
            print(' ')
    print('|', end='')
    print('Goto')




    # for state in items:
    #     for rule in state.targetRules
    #
