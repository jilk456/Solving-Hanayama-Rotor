from enum import Enum
from collections import deque

# A piece's 'line' (three per piece).
class Spoke(Enum):
    S05 = 0 # The one with the gap.
    S25 = 1 # The one to the right (clockwise) of S05
    S45 = 2 # The one to the left (anti-clockwise) of S05 (and of course clockwise of S25).

# A piece's opening (three along the outside).
# Each escape has two sides: '1' and '2' for E12, '3' and '4' for E34, and likewise '5' and '6' for E56.
# For each of the escapes, the side with the lower number is the one that comes first when measuring clockwise around the
# piece, assuming the piece's larger 'gap' is facing upwards.
# It's important to consider the two 'sides' of each opening to determine whether the puzzle's current state is 
# ascending or descending (see comments in RotorState for more info).
class Escape(Enum):
    E12 = 0 # The opening to the right (clockwise) of Spoke.05 (with the bigger 'gap' facing upwards).
    E34 = 1 # The opening to the right (clockwise) of E12.
    E56 = 2 # The opening to the right (clockwise) of E34.


# Represents the current state of the puzzle.
class RotorState:

    # The contact between gold's escape and silver's spoke when trying to pull the pieces apart.
    g_escape: Escape
    s_spoke: Spoke

    # The contact between silver's escape and gold's spoke when trying to pull the pieces apart.
    s_escape: Escape
    g_spoke: Spoke

    # Whether the contact points are in the 'ascending' direction.
    # Steps to determine if the puzzle's current state is ascending/descending:
    #   1. Look at one of the contact points. Hold the puzzle so that the piece whose spoke is part of the contact point
    #      is facing upwards. You only need to consider one contact point, because both will always give the same result.
    #   2. Now consider the two sides of the escape. If the escape's side with the lower number is above the side with 
    #      the higher number, the puzzle is ascending; otherwise, it's descending. 
    ascending: bool

    def __init__(self, g_escape: Escape, s_spoke: Spoke, s_escape: Escape, g_spoke: Spoke, ascending: bool):

        self.g_escape = g_escape
        self.s_spoke = s_spoke
        self.g_spoke = g_spoke
        self.s_escape = s_escape
        self.ascending = ascending

    def __eq__(self, other):

        if not isinstance(other, RotorState):
            return NotImplemented
        return (
            self.g_escape == other.g_escape and
            self.s_spoke == other.s_spoke and

            self.s_escape == other.s_escape and
            self.g_spoke == other.g_spoke and

            self.ascending == other.ascending
        )

    def __hash__(self):

        return hash((
            self.g_escape,
            self.s_spoke,
            self.s_escape,
            self.g_spoke,
            self.ascending,
        ))

    def print_self(self):

        col_width = 8

        headers = [
            "g_escape", "s_spoke", "s_escape", "g_spoke", "ascend",
        ]

        values = [
            self.g_escape.name, str(self.s_spoke.name), self.s_escape.name, str(self.g_spoke.name), str(self.ascending),
        ]

        header_row = " | ".join(f"{h[:col_width]:<{col_width}}" for h in headers)
        value_row = " | ".join(f"{v[:col_width]:<{col_width}}" for v in values)

        print(header_row)
        print("-" * len(header_row))
        print(value_row)


# Gives the next escape in a circular pattern 
# (just so I don't have to deal with 56 -> 12 in the main code)
def moveEscape(escape: Escape, clockwise: bool) -> Escape:

    if clockwise:
        if(escape == Escape.E56):
            return Escape.E12
        else:
            return Escape(escape.value+1)
    else:
        if(escape == Escape.E12):
            return Escape.E56
        else:
            return Escape(escape.value-1)


# Gives the next spoke in a circular pattern 
# (just so I don't have to deal with 45 -> 05 in the main code)
def moveSpoke(spoke: Spoke, clockwise: bool) -> Spoke:

    if clockwise:
        if(spoke == Spoke.S45):
            return Spoke.S05
        else:
            return Spoke(spoke.value+1)
    else:
        if(spoke == Spoke.S05):
            return Spoke.S45
        else:
            return Spoke(spoke.value-1)


# Determines if the given escape is positioned clockwise of the given spoke.
# The directions assume you're looking at the piece with its larger gap face-up.
# E12: cw of S05, acw of S25 and S45.
# E34: cw of S05 and S25, acw of S45.
# E56: cw of S25 and S45, acw of S05.
def isEscapeClockwiseOfSpoke(escape: Escape, spoke: Spoke):

    if (escape == Escape.E12):
        return spoke == Spoke.S05
    elif (escape == Escape.E34):
        return spoke == Spoke.S05 or spoke == Spoke.S25
    elif (escape == Escape.E56):
        return spoke == Spoke.S25 or spoke == Spoke.S45


# =========== ACTIONS =========== #

# Performs a 'loop on gold' action.
def loop_on_gold(state: RotorState):

    # Looping on gold changes gold's escape and silver's spoke.
    g_escape = moveEscape(state.g_escape, not isEscapeClockwiseOfSpoke(state.g_escape, state.g_spoke))
    s_poke = moveSpoke(state.s_spoke, isEscapeClockwiseOfSpoke(state.s_escape, state.s_spoke))

    s_escape = state.s_escape
    g_spoke = state.g_spoke

    # Looping inverts the puzzle's ascending/descending orientation.
    ascending = not state.ascending

    return RotorState(g_escape, s_poke, s_escape, g_spoke, ascending)

# Performs a 'loop on silver' action.
def loop_on_silver(state: RotorState):

    # Looping on silver changes silver's escape and gold's spoke.
    s_escape = moveEscape(state.s_escape, not isEscapeClockwiseOfSpoke(state.s_escape, state.s_spoke))
    g_spoke = moveSpoke(state.g_spoke, isEscapeClockwiseOfSpoke(state.g_escape, state.g_spoke))

    g_escape = state.g_escape
    s_spoke = state.s_spoke

    # Looping inverts the puzzle's ascending/descending orientation.
    ascending = not state.ascending

    return RotorState(g_escape, s_spoke, s_escape, g_spoke, ascending)


# Returns whether a 'slide on gold' action can be performed in the current state.
def check_gold_slideable(state: RotorState) -> bool:

    # If silver's escape is clockwise of silver's spoke, that mean's gold's escape will slide over the silver spoke in the anti-clockwise direction of silver's current spoke.

    # Get the spoke that gold's escape will have to slide over.
    # slide_spoke = moveSpoke(state.s_line, not state.s_line_ascending) # Journey's approach.
    slide_spoke = moveSpoke(state.s_spoke, not isEscapeClockwiseOfSpoke(state.s_escape, state.s_spoke))

    if (slide_spoke == Spoke.S45):
        # S45 is too thick for any escape to get over.
        return False
    elif (slide_spoke == Spoke.S25):
        # Only the E12 escape can't get over the S25 spoke.
        return state.g_escape != Escape.E12

    # Any escape can get over the S05 spoke (the one with the gap in it).
    return True


# Returns whether a 'slide on silver' action can be performed in the current state.
def check_silver_slideable(state: RotorState) -> bool:

    # Get the spoke that silver's escape will have to slide over.
    # slide_spoke = moveSpoke(state.g_spoke, not state.g_line_ascending)
    slide_spoke = moveSpoke(state.g_spoke, not isEscapeClockwiseOfSpoke(state.g_escape, state.g_spoke))

    if (slide_spoke == Spoke.S45):
        # S45 is too thick for any escape to get over.
        return False
    elif (slide_spoke == Spoke.S25):
        # Only the E12 escape can't get over the S25 spoke.
        return state.s_escape != Escape.E12

    # Any escape can get over the S05 spoke (the one with the gap in it).
    return True


# Performs a 'slide on gold' action.
def slide_on_gold(state: RotorState) -> RotorState | None:

    if(not check_gold_slideable(state)):
        return None

    # Sliding doesn't change the escapes.
    g_escape = state.g_escape
    s_escape = state.s_escape

    # Sliding on gold only change's silver's spoke.
    # s_line = moveSpoke(state.s_spoke, state.s_line_ascending) # Journey's approach.
    s_spoke = moveSpoke(state.s_spoke, isEscapeClockwiseOfSpoke(state.s_escape, state.s_spoke))

    # Sliding on gold doesn't change gold's spoke.
    g_spoke = state.g_spoke

    # Sliding doesn't change whether the puzzle is ascending.
    ascending = state.ascending

    return RotorState(g_escape, s_spoke, s_escape, g_spoke, ascending)


# Performs a 'slide on silver' action.
def slide_on_silver(state: RotorState) -> RotorState | None:

    if(not check_silver_slideable(state)):
        return None

    # Sliding doesn't change the escapes.
    g_escape = state.g_escape
    s_escape = state.s_escape

    # Sliding on silver only change's gold's spoke.
    g_spoke = moveSpoke(state.g_spoke, isEscapeClockwiseOfSpoke(state.g_escape, state.g_spoke))

    # Sliding one silver doesn't change silver's spoke.
    s_spoke = state.s_spoke

    # Sliding doesn't change whether the puzzle is ascending.
    ascending = state.ascending

    return RotorState(g_escape, s_spoke, s_escape, g_spoke, ascending)

# A class to map a state of the puzzle with a list of the moves that were required to get there (from a starting point).
class StateTracker:

    # The current state.
    state: RotorState | None

    # The previous moves.
    prevMoves: list[str]

    def __init__(self, state: RotorState | None, prevMoves: list[str]):

        self.state = state
        self.prevMoves = prevMoves


# A breadth-first search algorithm that finds the quickest path to get from an initial puzzle state to another.
def search(initial: RotorState, final: RotorState) -> StateTracker | None:

    # The states that have already been visited.
    visited_states : set[RotorState] = set()

    # A queue to implement BFS.
    queue : deque[StateTracker] = deque()

    # Add the initial state to the queue.
    queue.append(StateTracker(initial, []))

    # Execute BFS. It goes row by row down the tree until it finds the final state.
    while (len(queue) > 0):

        next = queue.popleft()
        next_state = next.state
        
        # Skip over states that have already been visited.
        if next_state in visited_states:
            continue

        # Check that it's a real state (might be None).
        if not isinstance(next_state, RotorState):
            continue

        # Check if final state, in which case the puzzle is solved.
        if (next_state == final):
            return next

        # Record this state as visited.
        visited_states.add(next_state)

        # Generate all possible states and add them to queue (4 possible moves: loop and slide for each piece).

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

    # If the queue runs out that means there are no solutions.
    return None


# The solved state.
final_state = RotorState(Escape.E12, Spoke.S05, Escape.E12, Spoke.S05, True)

# Values that define the contact points of the puzzle (modify these to match your puzzle).
g_escape : Escape = Escape.E34
s_escape : Escape = Escape.E56
g_spoke : Spoke = Spoke.S45
s_spoke : Spoke = Spoke.S45

# The current state (modify this to match whatever position your puzzle is in) (don't forget the 'ascending' flag).
current_state = RotorState(g_escape, s_spoke, s_escape, g_spoke, True)

# Search for a solution.
solution : StateTracker | None = search(current_state, final_state)

# Print the solution.
if not isinstance(solution, StateTracker):
    print("Unable to solve the puzzle.")
else:
    print(solution.prevMoves)