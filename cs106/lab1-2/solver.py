import sys
import collections
import numpy as np
import heapq
import time
from functools import lru_cache
import numpy as np

global posWalls, posGoals


class PriorityQueue:
    """Define a PriorityQueue data structure that will be used"""

    def __init__(self):
        self.Heap = []
        self.Count = 0
        self.len = 0

    def push(self, item, priority):
        entry = (priority, self.Count, item)
        heapq.heappush(self.Heap, entry)
        self.Count += 1

    def pop(self):
        (_, _, item) = heapq.heappop(self.Heap)
        return item

    def isEmpty(self):
        return len(self.Heap) == 0


"""Load puzzles and define the rules of sokoban"""


def transferToGameState(layout):
    """Transfer the layout of initial puzzle"""
    layout = [x.replace("\n", "") for x in layout]
    layout = [",".join(layout[i]) for i in range(len(layout))]
    layout = [x.split(",") for x in layout]
    maxColsNum = max([len(x) for x in layout])
    for irow in range(len(layout)):
        for icol in range(len(layout[irow])):
            if layout[irow][icol] == " ":
                layout[irow][icol] = 0  # free space
            elif layout[irow][icol] == "#":
                layout[irow][icol] = 1  # wall
            elif layout[irow][icol] == "&":
                layout[irow][icol] = 2  # player
            elif layout[irow][icol] == "B":
                layout[irow][icol] = 3  # box
            elif layout[irow][icol] == ".":
                layout[irow][icol] = 4  # goal
            elif layout[irow][icol] == "X":
                layout[irow][icol] = 5  # box on goal
        colsNum = len(layout[irow])
        if colsNum < maxColsNum:
            layout[irow].extend([1 for _ in range(maxColsNum - colsNum)])

    # print(layout)
    return np.array(layout)


def transferToGameState2(layout, player_pos):
    """Transfer the layout of initial puzzle"""
    maxColsNum = max([len(x) for x in layout])
    temp = np.ones((len(layout), maxColsNum))
    for i, row in enumerate(layout):
        for j, val in enumerate(row):
            temp[i][j] = layout[i][j]

    temp[player_pos[1]][player_pos[0]] = 2
    return temp


def PosOfPlayer(gameState):
    """Return the position of agent"""
    return tuple(np.argwhere(gameState == 2)[0])  # e.g. (2, 2)


def PosOfBoxes(gameState):
    """Return the positions of boxes"""
    return tuple(
        tuple(x) for x in np.argwhere((gameState == 3) | (gameState == 5))
    )  # e.g. ((2, 3), (3, 4), (4, 4), (6, 1), (6, 4), (6, 5))


def PosOfWalls(gameState):
    """Return the positions of walls"""
    return tuple(tuple(x) for x in np.argwhere(gameState == 1))  # e.g. like those above


def PosOfGoals(gameState):
    """Return the positions of goals"""
    return tuple(
        tuple(x) for x in np.argwhere((gameState == 4) | (gameState == 5))
    )  # e.g. like those above


def isEndState(posBox):
    """Check if all boxes are on the goals (i.e. pass the game)"""
    return sorted(posBox) == sorted(posGoals)


def isLegalAction(action, posPlayer, posBox):
    """Check if the given action is legal"""
    xPlayer, yPlayer = posPlayer
    if action[-1].isupper():  # the move was a push
        x1, y1 = xPlayer + 2 * action[0], yPlayer + 2 * action[1]
    else:
        x1, y1 = xPlayer + action[0], yPlayer + action[1]
    return (x1, y1) not in posBox + posWalls


def legalActions(posPlayer, posBox):
    """Return all legal actions for the agent in the current game state"""
    allActions = [
        [-1, 0, "u", "U"],
        [1, 0, "d", "D"],
        [0, -1, "l", "L"],
        [0, 1, "r", "R"],
    ]
    xPlayer, yPlayer = posPlayer
    legalActions = []
    for action in allActions:
        x1, y1 = xPlayer + action[0], yPlayer + action[1]
        if (x1, y1) in posBox:  # the move was a push
            action.pop(2)  # drop the little letter
        else:
            action.pop(3)  # drop the upper letter
        if isLegalAction(action, posPlayer, posBox):
            legalActions.append(action)
        else:
            continue

    return tuple(tuple(x) for x in legalActions)  # e.g. ((0, -1, 'l'), (0, 1, 'R'))


def updateState(posPlayer, posBox, action):
    """Return updated game state after an action is taken"""
    xPlayer, yPlayer = posPlayer  # the previous position of player
    newPosPlayer = [
        xPlayer + action[0],
        yPlayer + action[1],
    ]  # the current position of player
    posBox = [list(x) for x in posBox]
    if action[-1].isupper():  # if pushing, update the position of box
        posBox.remove(newPosPlayer)
        posBox.append([xPlayer + 2 * action[0], yPlayer + 2 * action[1]])
    posBox = tuple(tuple(x) for x in posBox)
    newPosPlayer = tuple(newPosPlayer)
    return newPosPlayer, posBox


def isFailed(posBox):
    """This function used to observe if the state is potentially failed, then prune the search"""
    rotatePattern = [
        [0, 1, 2, 3, 4, 5, 6, 7, 8],
        [2, 5, 8, 1, 4, 7, 0, 3, 6],
        [0, 1, 2, 3, 4, 5, 6, 7, 8][::-1],
        [2, 5, 8, 1, 4, 7, 0, 3, 6][::-1],
    ]
    flipPattern = [
        [2, 1, 0, 5, 4, 3, 8, 7, 6],
        [0, 3, 6, 1, 4, 7, 2, 5, 8],
        [2, 1, 0, 5, 4, 3, 8, 7, 6][::-1],
        [0, 3, 6, 1, 4, 7, 2, 5, 8][::-1],
    ]
    allPattern = rotatePattern + flipPattern

    for box in posBox:
        if box not in posGoals:
            board = [
                (box[0] - 1, box[1] - 1),
                (box[0] - 1, box[1]),
                (box[0] - 1, box[1] + 1),
                (box[0], box[1] - 1),
                (box[0], box[1]),
                (box[0], box[1] + 1),
                (box[0] + 1, box[1] - 1),
                (box[0] + 1, box[1]),
                (box[0] + 1, box[1] + 1),
            ]
            for pattern in allPattern:
                newBoard = [board[i] for i in pattern]
                if newBoard[1] in posWalls and newBoard[5] in posWalls:
                    return True
                elif (
                    newBoard[1] in posBox
                    and newBoard[2] in posWalls
                    and newBoard[5] in posWalls
                ):
                    return True
                elif (
                    newBoard[1] in posBox
                    and newBoard[2] in posWalls
                    and newBoard[5] in posBox
                ):
                    return True
                elif (
                    newBoard[1] in posBox
                    and newBoard[2] in posBox
                    and newBoard[5] in posBox
                ):
                    return True
                elif (
                    newBoard[1] in posBox
                    and newBoard[6] in posBox
                    and newBoard[2] in posWalls
                    and newBoard[3] in posWalls
                    and newBoard[8] in posWalls
                ):
                    return True
    return False


"""Implement all approcahes"""


def depthFirstSearch(gameState):
    """Implement depthFirstSearch approach"""
    beginBox = PosOfBoxes(gameState)
    beginPlayer = PosOfPlayer(gameState)

    startState = (beginPlayer, beginBox)
    frontier = collections.deque([[startState]])
    exploredSet = set()
    actions = [[0]]
    temp = []
    while frontier:
        node = frontier.pop()
        node_action = actions.pop()
        if isEndState(node[-1][-1]):
            temp += node_action[1:]
            break
        if node[-1] not in exploredSet:
            exploredSet.add(node[-1])
            for action in legalActions(node[-1][0], node[-1][1]):
                newPosPlayer, newPosBox = updateState(node[-1][0], node[-1][1], action)
                if isFailed(newPosBox):
                    continue
                frontier.append(node + [(newPosPlayer, newPosBox)])
                actions.append(node_action + [action[-1]])
    return temp


def breadthFirstSearch(gameState):
    """Implement breadthFirstSearch approach"""
    beginBox = PosOfBoxes(gameState)
    beginPlayer = PosOfPlayer(gameState)

    startState = (beginPlayer, beginBox)
    frontier = collections.deque([[startState]])
    exploredSet = set()
    actions = collections.deque([[0]])
    temp = []
    ### CODING FROM HERE ###

    # Check if the frontier is empty -> terminate the search
    while frontier:

        # Because deque (bidirectional queue) is used and we append new nodes to the right,
        # we need to pop nodes from the left -> right so that the deque can work as a queue (FIFO)
        # to implement BFS. In contrast, for DFS, we pop nodes from the right -> left so that
        # the deque can work as a stack (LIFO).
        node = frontier.popleft()
        node_action = actions.popleft()

        # Check if the current node is the end state (win state) -> terminate the search
        # and return the actions leading to the end state.
        if isEndState(node[-1][-1]):
            temp += node_action[1:]
            break

        # Check if the current node has been explored before -> if not, we add it to the explored
        # set and expand the current node.
        if node[-1] not in exploredSet:
            exploredSet.add(node[-1])

            # Expanding the current node by iterating through all legal actions (defined by the current
            # pos of player + current pos of boxes).
            for action in legalActions(node[-1][0], node[-1][-1]):

                # Update the game state after taking an action sampling from legal actions.
                newPosPlayer, newPosBox = updateState(node[-1][0], node[-1][-1], action)

                # Check if the new state is potentially failed -> if yes, simply prune this branch.
                if isFailed(newPosBox):
                    continue

                # If the new state is not failed, we add it and the corresponding actions leading
                # to this new state to the frontier.
                frontier.append(node + [(newPosPlayer, newPosBox)])
                actions.append(node_action + [action[-1]])

    # Return the actions leading to the end state (solutions) if exists, otherwise return an empty list.
    return temp


def cost(actions):
    """A cost function"""
    return len([x for x in actions if x.islower()])


def uniformCostSearch(gameState):
    """Implement uniformCostSearch approach"""

    start = time.time()

    beginBox = PosOfBoxes(gameState)
    beginPlayer = PosOfPlayer(gameState)
    startState = (beginPlayer, beginBox)
    frontier = PriorityQueue()
    frontier.push([startState], 0)
    exploredSet = set()
    actions = PriorityQueue()
    actions.push([0], 0)
    temp = []
    ### CODING FROM HERE ###

    # Check if the frontier is empty -> terminate the search
    while not frontier.isEmpty():

        # To implement UCS with a priority queue (min-heap) -> we need to pop to get the node with the lowest cost
        # (i.e. the node has the lowest number of "move without push" actions in the set of actions leading to this node).
        node = frontier.pop()
        node_action = actions.pop()

        # Check if the current node is the end state (win state) -> terminate the search
        if isEndState(node[-1][-1]):
            temp += node_action[1:]
            break

        # Check if the current node has been explored before -> if not, we add it to the explored
        if node[-1] not in exploredSet:
            exploredSet.add(node[-1])

            # Expanding the current node by iterating through all legal actions
            for action in legalActions(node[-1][0], node[-1][-1]):

                # Update the game state after taking an action sampling from legal actions.
                newPosPlayer, newPosBox = updateState(node[-1][0], node[-1][-1], action)

                # Check if the new state is potentially failed -> if yes, simply prune this branch.
                if isFailed(newPosBox):
                    continue

                # If the new state is not failed, we add it and the corresponding actions leading
                # to this new state to the frontier. Note that we need to calculate the cost of
                # the new node and the corresponding actions leading to this new node, and push them
                # to the priority queue (min-heap) so that the node with the lowest cost can be popped
                # first in the next iteration.
                curr_actions = node_action + [action[-1]]
                g = cost(curr_actions[1:])

                # Push the new node and the corresponding actions leading to this new node to the priority queue
                # (min-heap) with the cost.
                frontier.push(node + [(newPosPlayer, newPosBox)], g)
                actions.push(curr_actions, g)

    end = time.time()
    print("- UCS:")
    print(" + Runtime of UCS: %.2f second." % (end - start))
    print(" + Expanded nodes: %d" % len(exploredSet))

    # Return the actions leading to the end state (solutions) if exists, otherwise return an empty list.
    return temp


def manhattanDistance(pos1, pos2):
    """Calculates the L1 distance (grid distance) between two (r, c) points."""
    return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])


def remainingBoxesAndGoals(posBox):
    """
    Identifies boxes and goals that are not yet matched.
    Completed boxes (boxes already on goal squares) are excluded to simplify the search.
    """
    # Find the intersection of current box positions and goal positions
    completed = set(posGoals) & set(posBox)

    # Filter out completed boxes and goals, returning them as sorted tuples for consistency
    remaining_boxes = tuple(sorted(set(posBox).difference(completed)))
    remaining_goals = tuple(sorted(set(posGoals).difference(completed)))
    return remaining_boxes, remaining_goals


def heuristicMinimumMatching(posPlayer, posBox):
    """
    Match unfinished boxes and goals to minimize total Manhattan distance.
    This is a 'Minimum Cost Perfect Matching' approach in a bipartite graph.
    """
    remaining_boxes, remaining_goals = remainingBoxesAndGoals(posBox)

    # If all boxes are on goals, the remaining cost is zero
    if not remaining_boxes:
        return 0

    @lru_cache(maxsize=None)
    def dp(box_index, used_mask):
        """
        Recursive Dynamic Programming with Bitmask to find the optimal box-to-goal assignment.
        box_index: current box we are trying to pair.
        used_mask: bitmask representing which goals have already been assigned to a box.
        """
        # Base case: all boxes have been assigned to a goal
        if box_index == len(remaining_boxes):
            return 0

        best = float("inf")
        # Try pairing the current box with every available goal
        for goal_index, goal in enumerate(remaining_goals):

            # Check if this goal has already been 'used' by another box via bitmask
            if used_mask & (1 << goal_index):
                continue

            # Calculate cost: Manhattan distance for this pair + recursive cost for remaining pairs
            candidate = manhattanDistance(remaining_boxes[box_index], goal) + dp(
                box_index + 1, used_mask | (1 << goal_index)
            )

            # Keep the minimum total distance found
            best = min(best, candidate)
        return best

    return dp(0, 0)


def heuristicPlayerBoxGoal(posPlayer, posBox):
    """
    An improved heuristic: Sum of (Minimum Box-to-Goal matching) + (Player-to-nearest-pushable-box).
    This accounts for the fact that the player must first travel to a box to move it.
    """
    remaining_boxes, _ = remainingBoxesAndGoals(posBox)
    if not remaining_boxes:
        return 0

    # Part 1: Minimum distance to get all boxes onto goals
    matching_cost = heuristicMinimumMatching(posPlayer, posBox)

    occupied_boxes = set(posBox)
    player_to_box = float("inf")
    directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]  # Up, Down, Left, Right

    # Part 2: Find the distance from the player to the nearest box they can actually push
    for box_row, box_col in remaining_boxes:
        for d_row, d_col in directions:

            # player_cell: Where the player must stand to push the box
            player_cell = (box_row - d_row, box_col - d_col)

            # next_box_cell: Where the box will land after being pushed
            next_box_cell = (box_row + d_row, box_col + d_col)

            # Check if the push is physically possible (no walls blocking player or box)
            if player_cell in posWalls or next_box_cell in posWalls:
                continue

            # Ensure the player isn't blocked by another box
            if player_cell in occupied_boxes:
                continue

            # Update the distance to the closest reachable push-position
            player_to_box = min(
                player_to_box, manhattanDistance(posPlayer, player_cell)
            )

    # If no push is possible, we don't add to the cost (or handle as dead-end)
    if player_to_box == float("inf"):
        player_to_box = 0

    return matching_cost + player_to_box


def heuristic(posPlayer, posBox):
    """Default heuristic used by A*. Change this wrapper to test another heuristic."""
    return heuristicPlayerBoxGoal(posPlayer, posBox)


def aStarSearch(gameState):
    """Implement aStarSearch approach"""

    start = time.time()

    beginBox = PosOfBoxes(gameState)
    beginPlayer = PosOfPlayer(gameState)
    temp = []
    start_state = (beginPlayer, beginBox)
    frontier = PriorityQueue()
    frontier.push([start_state], heuristic(beginPlayer, beginBox))
    exploredSet = set()
    actions = PriorityQueue()
    actions.push([0], heuristic(beginPlayer, start_state[1]))

    # Check if the frontier is empty -> terminate the search
    while not frontier.isEmpty():

        # To implement A* Search with a priority queue (min-heap) -> we need to pop
        # to get the node and the corresponding node_action with the lowest f(n) = g(n) + h(n)
        node = frontier.pop()
        node_action = actions.pop()

        # Check if the current node is the end state (win state) -> terminate the search
        # and return the actions leading to the end state.
        if isEndState(node[-1][-1]):
            temp += node_action[1:]
            break

        # Check if the current node has been explored before -> if not, we add it to the explored
        # set and expand the current node.
        if node[-1] not in exploredSet:
            exploredSet.add(node[-1])

            # Expanding the current node by iterating through all legal actions (defined by the current
            # pos of player + current pos of boxes).
            for action in legalActions(node[-1][0], node[-1][-1]):

                # Update the game state after taking an action sampling from legal actions.
                newPosPlayer, newPosBox = updateState(node[-1][0], node[-1][-1], action)

                # Check if the new state is potentially failed -> if yes, simply prune this branch.
                if isFailed(newPosBox):
                    continue

                # If the new state is not failed, we add it and the corresponding actions leading
                # to this new state to the frontier. Note that we need to calculate the cost g(n)
                # of the new node and the heuristic h(n) of the new node, and push them to the
                # priority queue (min-heap) with f(n) = g(n) + h(n) so that the node with the
                # lowest f(n) can be popped first in the next iteration.
                new_action = node_action + [action[-1]]
                g = cost(new_action[1:])
                h = heuristic(newPosPlayer, newPosBox)
                f = g + h

                # Push the new node and the corresponding actions leading to this new node to the
                # priority queue with f(n) = g(n) + h(n).
                frontier.push(node + [(newPosPlayer, newPosBox)], f)
                actions.push(new_action, f)

    end = time.time()
    print("- A*:")
    print(" + Runtime of A* Search: %.2f second." % (end - start))
    print(" + Expanded nodes: %d" % len(exploredSet))

    return temp


"""Read command"""


def readCommand(argv):
    from optparse import OptionParser

    parser = OptionParser()
    parser.add_option(
        "-l",
        "--level",
        dest="sokobanLevels",
        help="level of game to play",
        default="level1.txt",
    )
    parser.add_option(
        "-m", "--method", dest="agentMethod", help="research method", default="bfs"
    )
    args = dict()
    options, _ = parser.parse_args(argv)
    with open("assets/levels/" + options.sokobanLevels, "r") as f:
        layout = f.readlines()
    args["layout"] = layout
    args["method"] = options.agentMethod
    return args


def get_move(layout, player_pos, method):
    time_start = time.time()
    global posWalls, posGoals
    # layout, method = readCommand(sys.argv[1:]).values()
    gameState = transferToGameState2(layout, player_pos)
    posWalls = PosOfWalls(gameState)
    posGoals = PosOfGoals(gameState)

    if method == "dfs":
        result = depthFirstSearch(gameState)
    elif method == "bfs":
        result = breadthFirstSearch(gameState)
    elif method == "ucs":
        result = uniformCostSearch(gameState)
    elif method == "astar":
        result = aStarSearch(gameState)
    else:
        raise ValueError("Invalid method.")
    time_end = time.time()
    # print("Runtime of %s: %.2f second." % (method, time_end - time_start))
    print(result)
    print("Number of moves:", len(result))
    return result
