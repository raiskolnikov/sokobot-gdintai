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
        
    def isValidMove(self, player, direction, crates, walls):
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
            if nextCrate in walls:
                return False

            # Check if the crate would hit another crate
            if nextCrate in crates:
                return False

        # Otherwise, the move is valid
        return True
        
    def isDeadEnd(self, crate, walls, targets):
        # Checks whether a crate has been pushed into a dead end
        # Currently detects corner dead ends caused by walls
        # Returns True if the crate can no longer reach a target
        # Returns False otherwise

        # If the crate is already on a target, it is not considered a dead end
        if crate in targets:
            return False

        row, col = crate

        # Get the positions surrounding the crate
        up = (row - 1, col)
        down = (row + 1, col)
        left = (row, col - 1)
        right = (row, col + 1)

        # Check if the crate is trapped in the upper-left corner
        if up in walls and left in walls:
            return True

        # Check if the crate is trapped in the upper-right corner
        if up in walls and right in walls:
            return True

        # Check if the crate is trapped in the lower-left corner
        if down in walls and left in walls:
            return True

        # Check if the crate is trapped in the lower-right corner
        if down in walls and right in walls:
            return True

        # Otherwise, the crate is not in a dead end
        return False

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

        cameFrom = self.BFS(player, crates, walls)

    
        try:
            time.sleep(3)
        except Exception as ex:
            print(ex)
        #return "lrlrlrlrlrlrlrlrlrlrlrlrlrlrlrlrlrlrlrlrlrlrlrlrlrlrlrlrlrlrlrlrlrlrlrlrlrlr"
        return self.getPath(cameFrom, (3, 5))