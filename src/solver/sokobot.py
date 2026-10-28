import time
import heapq
from collections import deque


class SokoBot:

    def getCoordinates(self, width,height, mapData, itemsData):
        # Sorts the map into coordinate pairs so that we can store the locations
        # of important puzzle data instead of searching multiple times

        walls = set()
        targets = set()
        crates = set()
        player = None

        # Get the coordinates of each
        for row in range(height):
            for col in range(width):
                if mapData[row][col] == "#":
                    walls.add((row,col))
                elif mapData[row][col] == ".":
                    targets.add((row, col))

                if itemsData[row][col] == "$":
                    crates.add((row, col))
                elif itemsData[row][col] == "@":
                   player = (row, col)

        return walls, targets, crates, player

    def getHeuristics(self, crates, targets):
        #Calculates a heuristic value based on a set formula
        # using the current of all boxes on all targets

        # Total Heuristic is 0 because the calculations have not started
        totalHeuristic = 0

        #Loop calculates the heuristic values between a crate and a set of targets.
        #The minimum heuristic calculated from this loop is then added to the total.
        #This repeats until all current positions of crates and all targets have been accounted for.
        for crateY, crateX in crates:
            minHeuristic = None
            for targetY, targetX in targets:
                hX = abs(targetX - crateX)
                hY = abs(targetY - crateY)
                h = hX + hY
                if minHeuristic == None or h < minHeuristic:
                    minHeuristic = h
            totalHeuristic += minHeuristic

        return totalHeuristic, None, None

    def getAliveTargets(self, crates, targets, walls):
        #Reverse-BFS that 'pulls' crates backwards because any square a crate can be pulled to means it could be pushed from
        # crates standing on any other square are in dead position

        # every target is an alive square
        alive = set(targets)
        # BFS queue to explore all tiles that a crate can be pulled to
        queue = deque(targets)

        # loop while no new alive targets are found
        while queue:
            # take the next tile from the front of the queue
            r, c = queue.popleft()
            # move crate in all four directions
            for dr, dc in self.DIRS.values():
                crateFrom = (r + dr, c + dc) #where crate originally is from before push
                playerFrom = (r + 2 * dr, c + 2 * dc) #where player originally is from before movement

                # if the crate or player would be in a wall, then skip
                if crateFrom in walls or playerFrom in walls:
                    continue
                # if the crate has already been found to be alive, then skip
                if crateFrom in alive:
                    continue

                # if the crate can be pulled to the current tile, then add to alive set
                alive.add(crateFrom)
                # queue the crate's original position to explore all tiles that a crate can be pulled to from there
                queue.append(crateFrom)

        return alive # returns set of all tiles that a crate can be pulled to

    def isDeadEnd(self, crate, crates, walls, targets, aliveTargets):
        # Returns True if moving a crate here will never lead to a solution
        # Checks:
        # 1. Dead squares from reverse BFS
        # 2. 2x2 frozen blocks made of walls and crates

        # Check whether the crate is on a dead square
        if crate not in aliveTargets:
            return True

        row, col = crate

        # Four possible 2x2 blocks that contain this crate
        offsets = [
            (0, 0),
            (-1, 0),
            (0, -1),
            (-1, -1)
        ]

        for rowOffset, colOffset in offsets:

            block = [
                (row + rowOffset,     col + colOffset),
                (row + rowOffset + 1, col + colOffset),
                (row + rowOffset,     col + colOffset + 1),
                (row + rowOffset + 1, col + colOffset + 1)
            ]

            # Assume every tile in this block is blocked
            blocked = True

            # Store every crate that appears in this block
            cratesInBlock = []

            for tile in block:

                if tile in walls:
                    continue

                elif tile in crates:
                    cratesInBlock.append(tile)

                else:
                    blocked = False
                    break

            # If every tile is blocked, check whether all crates inside the block are already on targets
            if blocked:

                allCratesOnTargets = True

                for cratePosition in cratesInBlock:
                    if cratePosition not in targets:
                        allCratesOnTargets = False
                        break

                # Frozen block containing at least one crate that is not on a target
                if not allCratesOnTargets:
                    return True

        return False
    

    def isValidMove(self, player, direction, crates, walls, targets, aliveTargets):
        # Checks if the player's next move is legal
        # Returns True if the player can move or push a crate
        # Returns False if the move is blocked by a wall
        # or if a crate cannot be pushed

        # Get the row and column change based on the direction
        dr, dc = self.DIRS[direction]

        # Calculate the player's next position
        nextPlayer = (player[0] + dr, player[1] + dc)

        # Check if the player walks into a wall
        if nextPlayer in walls:
            return False

        # Check if the player is attempting to push a crate
        if nextPlayer in crates:

            # Calculate where the crate would move
            nextCrate = (nextPlayer[0] + dr, nextPlayer[1] + dc)

            # Check if the crate would hit a wall
            if nextCrate in walls or nextCrate in crates:
                return False

            newCrates = crates - {nextPlayer} | {nextCrate}
            if self.isDeadEnd(nextCrate, newCrates, walls, targets, aliveTargets):
                return False  # The crate would be pushed into a dead end

        # Otherwise, the move is valid
        return True
        
    
    def aStarSearch(self, width, height, mapData, itemsData):
        #this function will implement the A* search algorithm to find the best path to move a crate to a target
        # State is (player, crate), crate is frozenset of crate positions, player is a tuple of player position
        # Move is the crate push, walking is done by BFS then added to move string
        # Cost is g which is total number of player moves so far
        # returns a string of direcctional moves or /none if no solution is found
        # each search move is a crate push

        #read the map and get coordinates of all important data
        walls, targets, crates, player = self.getCoordinates(width, height, mapData, itemsData)

        # tiles that a crate could still be pushed to a target from
        aliveTargets = self.getAliveTargets(crates, targets, walls)
        goal = frozenset(targets) #goal meaning every crate is on a target (frozenset because it will be used to compare with ccrate sets)
        crates = frozenset(crates) #crate locations are stored as a frozenset so that it is hashable

        def stateKey(p, cr):
            #finds every tile the player can walk to without pushing a crate
            reach = self.BFS(p, cr, walls)
            # min(reach) is the top left most tile which is the player position, returns reach because it will give the walk to each push spot
            return (min(reach), cr), reach

        # key and reachable tiles for the starting state
        startKey, startReach = stateKey(player, crates)

        # parent will store the previous state and moves used to get here
        parent = {startKey: None}
        # bestG is the lowest cost to reach a state
        bestG = {startKey: 0}
        # states that have will be explored and not revisited
        closed = set()

        #tie-breaker for the heap
        counter = 0

        # the openlist is a heap ordered by f = g + h, where g is the cost to reach a state and h is the heuristic value of that state
        openHeap = [(self.getHeuristics(crates, targets)[0], counter, startKey, startReach)]

        while openHeap:
            # pop the state with the lowest f value
            _, _, currentKey, currentreach = heapq.heappop(openHeap)

            # remove older and higher cost states from the open list
            if currentKey in closed:
                continue
            closed.add(currentKey)

            # unpack the current state
            currentPlayer, currentCrates = currentKey

            # check if every crate is on a target, if so return the path to get here
            if currentCrates <= goal:
                return self.getPath(parent, currentKey)

            for crate in currentCrates:
                for direction, (dr, dc) in self.DIRS.items():
                    standAt = (crate[0] - dr, crate[1] - dc) #where player must stand to push

                    # rejects push if player can't reach the square to push from
                    if standAt not in currentreach:
                        continue
                    # rejects push if it is not a valid move
                    if not self.isValidMove(standAt, direction, currentCrates, walls, targets, aliveTargets):
                        continue

                    # the crate's new position and the crate set after the push
                    nextCrate = (crate[0] + dr, crate[1] + dc)
                    nextCrates = currentCrates - {crate} | {nextCrate}

                    # after a push, the player will be in the crate's former position
                    nextKey, nextReach = stateKey(crate, nextCrates)
                    # if it is already fully expanded, put into closed and skip it
                    if nextKey in closed:
                        continue

                    # the moves to get to the push position and the push itself
                    moves = self.getPath(currentreach, standAt) + direction
                    # cost so far to the new state is the cost to get to the current state added to the cost of the moves to get the crate to the new position
                    g = bestG[currentKey] + 1

                    if nextKey not in bestG or g < bestG[nextKey]:
                        # store the current state as the parent of the new state and the moves to get there
                        parent[nextKey] = (currentKey, moves)
                        # store the cost to reach the new state
                        bestG[nextKey] = g
                        # tie breaker
                        counter += 1

                        # estimate the cost to reach the goal from the new state using the heuristic function
                        h = self.getHeuristics(nextCrates, targets,)[0]
                        # add to the open list with the total estimated cost f = g + 2h, the tie breaker, the new state, and the reachable tiles from that state
                        # 2 multiplied to h to give the heuristic more weight
                        heapq.heappush(openHeap, (g + 2 * h, counter, nextKey, nextReach))

        return None  # No solution found

    DIRS = {"u": (-1, 0), "d": (1, 0), "l": (0, -1), "r": (0, 1)}

    def BFS(self, player, crates, walls):
        # uses BFS to search where the player can walk without pushing anything

        visited = {player: None}  # tile we came from

        queue = deque([player])  # tiles that are waiting to be visited/checked
        while queue:
            r, c = queue.popleft()
            for letter, (dr,dc) in self.DIRS.items():
                next = (r + dr, c + dc)  # let next be equal to the old + the change in direction
                if next not in visited and next not in walls and next not in crates:
                    visited[next] = ((r,c), letter)  #remember where we came from and how
                    queue.append(next)  # check the tiles adjacent to it later

        return visited
        
    
    # getPath returns the string path from initial position to goal
    # it searches a cameFrom dictionary that stores the coordinate,
    # the coordinate before it got there, and the direction it came from
    def getPath(self, cameFrom, goal):
        letters = []  # letters is a string that will append the path
        tile = goal
        while cameFrom[tile] is not None:
            prevTile, letter = cameFrom[tile]
            letters.append(letter)  # add the letter (u,d,l,r) into the string
            tile = prevTile

        letters.reverse()  # flip the string since we started from the goal/end
        return "".join(letters)  # makes it into one string instead of individual


    def solveSokobanPuzzle(self, width, height, mapData, itemsData):
        # YOU NEED TO REWRITE THE IMPLEMENTATION OF THIS METHOD TO MAKE THE BOT SMARTER
        # Default stupid behavior: Think (sleep) for 3 seconds, and then return a
        # sequence
        # that just moves left and right repeatedly.


        path = self.aStarSearch(width, height, mapData, itemsData)
        return path if path is not None else ""