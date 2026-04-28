# multiAgents.py
# --------------
# Licensing Information:  You are free to use or extend these projects for
# educational purposes provided that (1) you do not distribute or publish
# solutions, (2) you retain this notice, and (3) you provide clear
# attribution to UC Berkeley, including a link to http://ai.berkeley.edu.
#
# Attribution Information: The Pacman AI projects were developed at UC Berkeley.
# The core projects and autograders were primarily created by John DeNero
# (denero@cs.berkeley.edu) and Dan Klein (klein@cs.berkeley.edu).
# Student side autograding was added by Brad Miller, Nick Hay, and
# Pieter Abbeel (pabbeel@cs.berkeley.edu).


from util import manhattanDistance
from game import Directions
import random, util

from game import Agent


class ReflexAgent(Agent):
    """
    A reflex agent chooses an action at each choice point by examining
    its alternatives via a state evaluation function.

    The code below is provided as a guide.  You are welcome to change
    it in any way you see fit, so long as you don't touch our method
    headers.
    """

    def getAction(self, gameState):
        """
        You do not need to change this method, but you're welcome to.

        getAction chooses among the best options according to the evaluation function.

        Just like in the previous project, getAction takes a GameState and returns
        some Directions.X for some X in the set {NORTH, SOUTH, WEST, EAST, STOP}
        """
        # Collect legal moves and successor states
        legalMoves = gameState.getLegalActions()

        # Choose one of the best actions
        scores = [self.evaluationFunction(gameState, action) for action in legalMoves]
        bestScore = max(scores)
        bestIndices = [
            index for index in range(len(scores)) if scores[index] == bestScore
        ]
        chosenIndex = random.choice(bestIndices)  # Pick randomly among the best

        "Add more of your code here if you want to"

        return legalMoves[chosenIndex]

    def evaluationFunction(self, currentGameState, action):
        """
        Design a better evaluation function here.

        The evaluation function takes in the current and proposed successor
        GameStates (pacman.py) and returns a number, where higher numbers are better.

        The code below extracts some useful information from the state, like the
        remaining food (newFood) and Pacman position after moving (newPos).
        newScaredTimes holds the number of moves that each ghost will remain
        scared because of Pacman having eaten a power pellet.

        Print out these variables to see what you're getting, then combine them
        to create a masterful evaluation function.
        """
        # Useful information you can extract from a GameState (pacman.py)
        successorGameState = currentGameState.generatePacmanSuccessor(action)
        newPos = successorGameState.getPacmanPosition()
        newFood = successorGameState.getFood()
        newGhostStates = successorGameState.getGhostStates()
        newScaredTimes = [ghostState.scaredTimer for ghostState in newGhostStates]

        "*** YOUR CODE HERE ***"
        # return successorGameState.getScore()
        food = currentGameState.getFood()
        currentPos = list(successorGameState.getPacmanPosition())
        distance = float("-Inf")

        foodList = food.asList()

        if action == "Stop":
            return float("-Inf")

        for state in newGhostStates:
            if state.getPosition() == tuple(currentPos) and (state.scaredTimer == 0):
                return float("-Inf")

        for x in foodList:
            tempDistance = -1 * (manhattanDistance(currentPos, x))
            if tempDistance > distance:
                distance = tempDistance

        return distance


def scoreEvaluationFunction(currentGameState):
    """
    This default evaluation function just returns the score of the state.
    The score is the same one displayed in the Pacman GUI.

    This evaluation function is meant for use with adversarial search agents
    (not reflex agents).
    """
    return currentGameState.getScore()


class MultiAgentSearchAgent(Agent):
    """
    This class provides some common elements to all of your
    multi-agent searchers.  Any methods defined here will be available
    to the MinimaxPacmanAgent, AlphaBetaPacmanAgent & ExpectimaxPacmanAgent.

    You *do not* need to make any changes here, but you can if you want to
    add functionality to all your adversarial search agents.  Please do not
    remove anything, however.

    Note: this is an abstract class: one that should not be instantiated.  It's
    only partially specified, and designed to be extended.  Agent (game.py)
    is another abstract class.
    """

    def __init__(self, evalFn="scoreEvaluationFunction", depth="2"):
        self.index = 0  # Pacman is always agent index 0
        self.evaluationFunction = util.lookup(evalFn, globals())
        self.depth = int(depth)


class MinimaxAgent(MultiAgentSearchAgent):
    """
    Your minimax agent (question 2)
    """

    def getAction(self, gameState):
        """
        Returns the minimax action from the current gameState using self.depth
        and self.evaluationFunction.
        """

        def value(gameState, agentIndex, depth):
            if gameState.isWin() or gameState.isLose() or depth == self.depth:
                return self.evaluationFunction(gameState)
            if agentIndex == 0:
                return maxValue(gameState, agentIndex, depth)
            else:
                return minValue(gameState, agentIndex, depth)

        def maxValue(gameState, agentIndex, depth):
            v = float("-inf")
            for action in gameState.getLegalActions(agentIndex):
                v = max(
                    v, value(gameState.generateSuccessor(agentIndex, action), 1, depth)
                )
            return v

        def minValue(gameState, agentIndex, depth):
            v = float("inf")
            nextAgent = agentIndex + 1
            nextDepth = depth
            if nextAgent == gameState.getNumAgents():
                nextAgent = 0
                nextDepth += 1
            for action in gameState.getLegalActions(agentIndex):
                v = min(
                    v,
                    value(
                        gameState.generateSuccessor(agentIndex, action),
                        nextAgent,
                        nextDepth,
                    ),
                )
            return v

        bestAction = None
        bestValue = float("-inf")
        for action in gameState.getLegalActions(0):
            val = value(gameState.generateSuccessor(0, action), 1, 0)
            if val > bestValue or bestAction is None:
                bestValue = val
                bestAction = action
        return bestAction


class AlphaBetaAgent(MultiAgentSearchAgent):
    """
    Your minimax agent with alpha-beta pruning (question 3)
    """

    def getAction(self, gameState):
        """
        Returns the minimax action using self.depth and self.evaluationFunction
        """

        def value(gameState, agentIndex, depth, alpha, beta):
            if gameState.isWin() or gameState.isLose() or depth == self.depth:
                return self.evaluationFunction(gameState)
            if agentIndex == 0:
                return maxValue(gameState, agentIndex, depth, alpha, beta)
            else:
                return minValue(gameState, agentIndex, depth, alpha, beta)

        def maxValue(gameState, agentIndex, depth, alpha, beta):
            v = float("-inf")
            for action in gameState.getLegalActions(agentIndex):
                v = max(
                    v,
                    value(
                        gameState.generateSuccessor(agentIndex, action),
                        1,
                        depth,
                        alpha,
                        beta,
                    ),
                )
                if v > beta:
                    return v
                alpha = max(alpha, v)
            return v

        def minValue(gameState, agentIndex, depth, alpha, beta):
            v = float("inf")
            nextAgent = agentIndex + 1
            nextDepth = depth
            if nextAgent == gameState.getNumAgents():
                nextAgent = 0
                nextDepth += 1
            for action in gameState.getLegalActions(agentIndex):
                v = min(
                    v,
                    value(
                        gameState.generateSuccessor(agentIndex, action),
                        nextAgent,
                        nextDepth,
                        alpha,
                        beta,
                    ),
                )
                if v < alpha:
                    return v
                beta = min(beta, v)
            return v

        bestAction = None
        bestValue = float("-inf")
        alpha = float("-inf")
        beta = float("inf")
        for action in gameState.getLegalActions(0):
            val = value(gameState.generateSuccessor(0, action), 1, 0, alpha, beta)
            if val > bestValue or bestAction is None:
                bestValue = val
                bestAction = action
            alpha = max(alpha, bestValue)
        return bestAction


class ExpectimaxAgent(MultiAgentSearchAgent):
    """
    Your expectimax agent (question 4)
    """

    def getAction(self, gameState):
        """
        Returns the expectimax action using self.depth and self.evaluationFunction

        All ghosts should be modeled as choosing uniformly at random from their
        legal moves.
        """

        def value(gameState, agentIndex, depth):
            if gameState.isWin() or gameState.isLose() or depth == self.depth:
                return self.evaluationFunction(gameState)
            if agentIndex == 0:
                return maxValue(gameState, agentIndex, depth)
            else:
                return expValue(gameState, agentIndex, depth)

        def maxValue(gameState, agentIndex, depth):
            v = float("-inf")
            for action in gameState.getLegalActions(agentIndex):
                v = max(
                    v, value(gameState.generateSuccessor(agentIndex, action), 1, depth)
                )
            return v

        def expValue(gameState, agentIndex, depth):
            v = 0
            actions = gameState.getLegalActions(agentIndex)
            nextAgent = agentIndex + 1
            nextDepth = depth
            if nextAgent == gameState.getNumAgents():
                nextAgent = 0
                nextDepth += 1
            for action in actions:
                v += value(
                    gameState.generateSuccessor(agentIndex, action),
                    nextAgent,
                    nextDepth,
                )
            return v / len(actions)

        bestAction = None
        bestValue = float("-inf")
        for action in gameState.getLegalActions(0):
            val = value(gameState.generateSuccessor(0, action), 1, 0)
            if val > bestValue or bestAction is None:
                bestValue = val
                bestAction = action
        return bestAction


mazeDistanceCache = {}


def getMazeDistance(point1, point2, gameState):
    """
    Finds the shortest path between point1 and point2 ignoring ghosts but considering walls.
    Uses BFS and caches the results to ensure high performance.
    """
    x1, y1 = int(point1[0]), int(point1[1])
    x2, y2 = int(point2[0]), int(point2[1])
    p1, p2 = (x1, y1), (x2, y2)

    if p1 == p2:
        return 0
    if (p1, p2) in mazeDistanceCache:
        return mazeDistanceCache[(p1, p2)]

    walls = gameState.getWalls()
    queue = [(p1, 0)]
    visited = {p1}

    while queue:
        current, dist = queue.pop(0)

        # Cache the distance to all nodes seen along the way from p1
        mazeDistanceCache[(p1, current)] = dist
        mazeDistanceCache[(current, p1)] = dist

        if current == p2:
            return dist

        x, y = current
        for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
            nx, ny = x + dx, y + dy
            if not walls[nx][ny] and (nx, ny) not in visited:
                visited.add((nx, ny))
                queue.append(((nx, ny), dist + 1))

    return float("inf")


def betterEvaluationFunction(currentGameState):
    """
    Your extreme ghost-hunting, pellet-nabbing, food-gobbling, unstoppable
    evaluation function (question 5).

    DESCRIPTION: Uses a BFS-based fast mazeDistance (fully respecting walls) instead of Manhattan distance. It rewards finding the closest optimal path to food, eating scared ghosts, and avoiding non-scared ghosts correctly navigating around corners.
    """

    food_reward = 10.0
    ghost_eat_reward = 200.0
    win_reward = 500.0

    newPos = currentGameState.getPacmanPosition()
    newFood = currentGameState.getFood()
    newGhostStates = currentGameState.getGhostStates()
    newCapsules = currentGameState.getCapsules()
    newScaredTimes = [ghostState.scaredTimer for ghostState in newGhostStates]

    score = currentGameState.getScore()
    foodList = newFood.asList()

    # Calculate real maze distances to all food
    if foodList:
        food_distances = [
            getMazeDistance(newPos, food, currentGameState) for food in foodList
        ]
        closest_food = min(food_distances) if food_distances else 1

        # Breakthrough: Food Density (How much food is within 5 steps?)
        food_density = sum(1 for dist in food_distances if dist <= 5)

        # Reward going to the immediate closest food
        score += food_reward / max(closest_food, 1)

        # Reward moving into dense clusters of food
        score += 2 * food_density

        # Standard penalty for remaining food
        score -= 5 * len(foodList)

    capsule_dists = [
        getMazeDistance(newPos, capsule, currentGameState) for capsule in newCapsules
    ]
    closest_capsule = min(capsule_dists) if capsule_dists else float("inf")

    for i in range(len(newGhostStates)):
        ghostDist = getMazeDistance(
            newPos, newGhostStates[i].getPosition(), currentGameState
        )
        scaredTime = newScaredTimes[i]

        virtualDist = scaredTime - ghostDist

        if virtualDist > 0:
            # Scared Ghost Priority!
            score += ghost_eat_reward / max(ghostDist, 1)
        else:
            # Ghost is NOT scared or scared time runs out before reaching it
            if ghostDist <= 5:  # Danger zone!
                score -= win_reward / max(ghostDist, 0.1)
                if ghostDist <= 2:
                    score -= 3 * win_reward  # fatal danger

                # Breakthrough: "Ghost Baiting" Synergy
                # Only value capsules if a non-scared ghost is actively chasing us within 5 blocks.
                # Do NOT eat a capsule when ghosts are far away (wastes the powerup).
                if capsule_dists:
                    score += (
                        0.5 * max(ghostDist - closest_capsule, 0) * ghost_eat_reward
                    )

    return score


# Abbreviation
better = betterEvaluationFunction
