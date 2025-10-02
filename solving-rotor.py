from enum import Enum
from collections import deque

class Edge(Enum):
    E12 = 0
    E34 = 1
    E56 = 2

# Gives the next edge in a circular pattern 
# (just so I don't have to deal with 56 -> 12 in the main code)
def moveEdge(edge: Edge, ascending: bool):
    if ascending:
        if(edge == Edge.E56):
            return Edge.E12
        else:
            return Edge(edge.value+1)
    else:
        if(edge == Edge.E12):
            return Edge.E56
        else:
            return Edge(edge.value-1)

class Line(Enum):
    L05 = 0
    L25 = 1
    L45 = 2

# Gives the next line/spoke in a circular pattern 
# (just so I don't have to deal with 45 -> 05 in the main code)
def moveLine(line: Line, ascending: bool):
    if ascending:
        if(line == Line.L45):
            return Line.L05
        else:
            return Line(line.value+1)
    else:
        if(line == Line.L05):
            return Line.L45
        else:
            return Line(line.value-1)

class Rotor_state:
    g_escape: Edge
    s_line: Line
    s_escape: Edge
    g_line: Line
    ascending: bool

    # These refer to how the next moves will be impacted
    g_escape_ascending: bool
    s_line_ascending: bool
    s_escape_ascending: bool
    g_line_ascending: bool

    def __init__(self, g_escape: Edge, s_line: Line, s_escape: Edge, g_line: Line, 
                 ascending: bool, g_escape_ascending: bool, s_line_ascending: bool, 
                 s_escape_ascending: bool, g_line_ascending: bool):
        self.g_escape = g_escape
        self.s_line = s_line
        self.g_line = g_line
        self.s_escape = s_escape
        self.ascending = ascending
        self.g_escape_ascending = g_escape_ascending
        self.s_line_ascending = s_line_ascending
        self.s_escape_ascending = s_escape_ascending
        self.g_line_ascending = g_line_ascending


    def __eq__(self, other):
        if not isinstance(other, Rotor_state):
            return NotImplemented
        return (
            self.g_escape == other.g_escape and
            self.s_line == other.s_line and
            self.s_escape == other.s_escape and
            self.g_line == other.g_line and
            self.ascending == other.ascending and
            self.g_escape_ascending == other.g_escape_ascending and
            self.s_line_ascending == other.s_line_ascending and
            self.s_escape_ascending == other.s_escape_ascending and
            self.g_line_ascending == other. g_line_ascending
        )

    def __hash__(self):
        return hash((
            self.g_escape,
            self.s_line,
            self.s_escape,
            self.g_line,
            self.ascending,
            self.g_escape_ascending, 
            self.s_line_ascending, 
            self.s_escape_ascending,
            self.g_line_ascending
        ))

    def print_self(self):
        col_width = 8
        headers = [
            "g_escape", "s_line", "s_escape", "g_line", "ascend",
            "g_esc_asc", "s_lin_asc", "s_esc_asc", "g_lin_asc"
        ]
        values = [
            self.g_escape.name, str(self.s_line.name), self.s_escape.name, str(self.g_line.name),
            str(self.ascending), str(self.g_escape_ascending), str(self.s_line_ascending),
            str(self.s_escape_ascending), str(self.g_line_ascending)
        ]

        header_row = " | ".join(f"{h[:col_width]:<{col_width}}" for h in headers)
        value_row = " | ".join(f"{v[:col_width]:<{col_width}}" for v in values)

        print(header_row)
        print("-" * len(header_row))
        print(value_row)
    

# =========== ACTIONS =========== #

def loop_on_gold(state: Rotor_state):
    g_escape = moveEdge(state.g_escape, state.g_escape_ascending)
    s_line = moveLine(state.s_line, state.s_line_ascending)
    s_escape = state.s_escape
    g_line = state.g_line
    ascending = not state.ascending

    g_escape_ascending = not state.g_escape_ascending
    s_line_ascending = not state.s_line_ascending
    s_escape_ascending = not state.s_escape_ascending
    g_line_ascending = not state.g_line_ascending

    return Rotor_state(g_escape, s_line, s_escape, g_line, ascending, g_escape_ascending, s_line_ascending, s_escape_ascending, g_line_ascending)

def loop_on_silver(state: Rotor_state):
    g_escape = state.g_escape
    s_line = state.s_line
    s_escape = moveEdge(state.s_escape, state.s_escape_ascending)
    g_line = moveLine(state.g_line, state.g_line_ascending)
    ascending = not state.ascending

    g_escape_ascending = not state.g_escape_ascending
    s_line_ascending = not state.s_line_ascending
    s_escape_ascending = not state.s_escape_ascending
    g_line_ascending = not state.g_line_ascending

    return Rotor_state(g_escape, s_line, s_escape, g_line, ascending, g_escape_ascending, s_line_ascending, s_escape_ascending, g_line_ascending)

def check_gold_slideable(state: Rotor_state):
    slide_spoke = moveLine(state.s_line, not state.s_line_ascending)
    if(slide_spoke == Line.L45):
        return False
    elif(slide_spoke == Line.L25):
        if(state.g_escape == Edge.E12):
            return False
    return True

def check_silver_slideable(state: Rotor_state):
    slide_spoke = moveLine(state.g_line, not state.g_line_ascending)
    if(slide_spoke == Line.L45):
        return False
    elif(slide_spoke == Line.L25):
        if(state.s_escape == Edge.E12):
            return False
    return True

def slide_on_gold(state: Rotor_state):

    if(not check_gold_slideable(state)):
        return None

    g_escape = state.g_escape
    s_line = moveLine(state.s_line, state.s_line_ascending)
    s_escape = state.s_escape
    g_line = state.g_line
    ascending = state.ascending

    g_escape_ascending = state.g_escape_ascending
    s_line_ascending = not state.s_line_ascending
    s_escape_ascending = not state.s_escape_ascending
    g_line_ascending = state.g_line_ascending

    return Rotor_state(g_escape, s_line, s_escape, g_line, ascending, g_escape_ascending, s_line_ascending, s_escape_ascending, g_line_ascending)

def slide_on_silver(state: Rotor_state):

    if(not check_silver_slideable(state)):
        return None

    g_escape = state.g_escape
    s_line = state.s_line
    s_escape = state.s_escape
    g_line = moveLine(state.g_line, state.g_line_ascending)
    ascending = state.ascending

    g_escape_ascending = not state.g_escape_ascending
    s_line_ascending = state.s_line_ascending
    s_escape_ascending = state.s_escape_ascending
    g_line_ascending = not state.g_line_ascending

    return Rotor_state(g_escape, s_line, s_escape, g_line, ascending, g_escape_ascending, s_line_ascending, s_escape_ascending, g_line_ascending)

def isFinal(state: Rotor_state, final: Rotor_state):
    if(
        state.g_escape == final.g_escape and
        state.s_line == final.s_line and
        state.s_escape == final.s_escape and
        state.g_line == final.g_line and
        state.ascending == final.ascending
    ):
        return True
    return False

# ======= BREADTH FIRST SEARCH ======= #

class StateTracker:
    state: Rotor_state
    prevMoves: list[str]

    def __init__(self, state: Rotor_state, prevMoves: list[str]):
        self.state = state
        self.prevMoves = prevMoves

def bfs(initial: Rotor_state, final: Rotor_state):

    visited_states = {}
    queue: deque[StateTracker] = deque()


    queue.append(StateTracker(initial, []))

    while(len(queue) > 0):
        next = queue.popleft()
        next_state = next.state

        if next_state not in visited_states:

            # Check that it is a real state
            if not isinstance(next_state, Rotor_state):
                continue

            # Check if final state
            if(isFinal(next_state, final)):
                return next

            # Add to visited
            visited_states[next_state] = True 

            # Generate all possible moves and add them to queue
            gold_loop_state = loop_on_gold(next_state)
            gold_loop_actions = [action for action in next.prevMoves]
            gold_loop_actions.append("L/G")
            queue.append(StateTracker(gold_loop_state, gold_loop_actions))

            silver_loop_state = loop_on_silver(next_state)
            silver_loop_actions = [action for action in next.prevMoves]
            silver_loop_actions.append("L/S")
            queue.append(StateTracker(silver_loop_state, silver_loop_actions))

            gold_slide_state = slide_on_gold(next_state)
            gold_slide_actions = [action for action in next.prevMoves]
            gold_slide_actions.append("S/G")
            queue.append(StateTracker(gold_slide_state, gold_slide_actions))

            silver_slide_state = slide_on_silver(next_state)
            silver_slide_actions = [action for action in next.prevMoves]
            silver_slide_actions.append("S/S")
            queue.append(StateTracker(silver_slide_state, silver_slide_actions))
        
    # If the queue runs out
    return False

# For when you don't know the movement of the initial state
def solve_rotor(initial: Rotor_state, final: Rotor_state):
    base_state = Rotor_state(Edge.E34, Line.L25, Edge.E34, Line.L45, False, True, True, False, False)

    full_initial = bfs(base_state, initial).state
    if(full_initial == False):
        return False
    
    return bfs(full_initial, final)

# ============ TESTING ============ #

# I don't actually know whether g and s values are ascending (but it doesn't matter)
final_state = Rotor_state(Edge.E12, Line.L05, Edge.E12, Line.L05, True, True, True, True, True)
current_state = Rotor_state(Edge.E56, Line.L45, Edge.E56, Line.L05, True, True, True, True, True)

solution = solve_rotor(current_state, final_state)
print(solution.prevMoves)