import time
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

    def getHeuristics(self, width, height, crates, targets, itemsData):
        # Calculates a heuristic value based on a set formula
        # using the current position of a box to a target

        # Get the number of crates "n"
        # [REVISION] - USE CRATES

        #Calculates a heuristic value based on a set formula
        # using the current position of a box to a target

        #Get the number of crates "n"
        #[REVISION] - USE CRATES
        n = 0
        for row in range(height):
            for col in range(width):
                if itemsData[row][col] == "$" or itemsData[row][col] == "*":
                    n += 1

        #Fixed something
        tempCrates = []
        tempTargets = []
        tempValues = []
        tempHeuristics = []


        # Calculate the Heuristic Value between all crates and targets
        for crateY, crateX in crates:
            for targetY, targetX in targets:
                hX = abs(targetX - crateX)
                hY = abs(targetY - crateY)

                h = (hX + hY) + n

                tempHeuristics.append(h)

                tempValues.append(h)
                tempValues.append(targetY)
                tempValues.append(targetX)

                tempTuple = tuple(tempValues)

                tempTargets.append(tempTuple)

                tempValues.clear()

                tempValues.append(h)
                tempValues.append(crateY)
                tempValues.append(crateX)

                tempTuple = tuple(tempValues)

                tempCrates.append(tempTuple)

                tempValues.clear()

        minHeuristic = min(tempHeuristics)
        finalCrate = tuple()
        finalTarget = tuple()

        for x in range(len(tempCrates)):
            if tempHeuristics[x]== minHeuristic:
                finalCrate = tempCrates[x]

        for y in range(len(tempTargets)):
            if tempHeuristics[y] == minHeuristic:
                finalTarget = tempTargets[y]

        return minHeuristic, finalCrate, finalTarget

    def getAliveTargets(self, crates, targets, walls):
        #Reverse-BFS that 'pulls' crates backwards because any square a crate can be pulled to means it could be pushed from

        alive = set(targets)
        queue = deque(targets)

        while queue:
            r, c = queue.popleft()
            for dr, dc in self.DIRS.values():
                crateFrom = (r + dr, c + dc) #where crate originally is from before push
                playerFrom = (r + 2 * dr, c + 2 * dc) #where player originally is from before movement

                if crateFrom in walls or playerFrom in walls:
                    continue
                if crateFrom in alive:
                    continue

                alive.add(crateFrom)
                queue.append(crateFrom)

        return alive

    def isDeadEnd(self, crate, walls, targets, aliveTargets):
            # Returns True if the crate movement will not lead to a solution
            # Returns False otherwise
    
            # If the crate is already on a target, it is not considered a dead end
            if crate in targets:
                return False
    
            # If the crate is not in the set of alive targets, it is considered a dead end
            if crate not in aliveTargets:
                return True
    
            r, c = crate
            for dr, dc in self.DIRS.values():
                adjacent = (r + dr, c + dc)
                if adjacent not in walls:
                    return False  # There is at least one adjacent square that is not a wall        
            return False
    

    def isValidMove(self, player, direction, crates, walls, targets, aliveSquares):
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
            if self.isDeadEnd(nextCrate, walls, targets, aliveSquares):
                return False  # The crate would be pushed into a dead end

        # Otherwise, the move is valid
        return True
        
    
    def aStarSearch(self, width, height, mapData, itemsData):
        #this function will implement the A* search algorithm to find the best path to move a crate to a target
        #it will return the path as a string of directions

        #initialize the open and closed lists
        openList = []
        closedList = set()

        #get the coordinates of the player, crates, and targets
        walls, targets, crates, player = self.getCoordinates(width, height, mapData, itemsData)

        #initialize the starting node
        #startNode = (player, priorityCrate)
        #openList.append(startNode)

        while openList:
            #get the node with the lowest f value
            currentNode = min(openList, key=lambda x: self.getHeuristic(width, height, x[1][0], x[1][1],  itemsData))
            openList.remove(currentNode)
            closedList.add(currentNode)

            #check if we have reached the goal
            if currentNode[1] in targets:
                return self.reconstructPath(currentNode)

            #generate the neighbors of the current node
            neighbors = self.getNeighbors(currentNode, walls, crates)

            for neighbor in neighbors:
                if neighbor in closedList:
                    continue

                if neighbor not in openList:
                    openList.append(neighbor)

        return None  # no path found

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


        walls, targets, crates, player = self.getCoordinates(width, height, mapData, itemsData)
        aliveSquares = self.getAliveTargets(crates, targets, walls)
        crates = frozenset(crates)
        cameFrom = self.BFS(player, crates, walls)

        try:
            time.sleep(3)
        except Exception as ex:
            print(ex)
        #return "lrlrlrlrlrlrlrlrlrlrlrlrlrlrlrlrlrlrlrlrlrlrlrlrlrlrlrlrlrlrlrlrlrlrlrlrlrlr"
        return self.getPath(cameFrom, (3, 5))