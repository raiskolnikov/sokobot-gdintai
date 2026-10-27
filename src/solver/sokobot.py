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

    def getHeursitic(width, height, crateX, crateY,
                     targetX, targetY, itemsData):
        #Calculates a heuristic value based on a set formula
        # using the current position of a box to a target

        #Calculate the X and Y distance between a crate and a target
        hX = abs(targetX - crateX)
        hY = abs(targetY - crateY)

        #Get the number of crates "n"
        n = 0
        for row in range(height):
            for col in range(width):
                if itemsData[row][col] == "$" or itemsData[row][col] == "*":
                    n += 1

        h = (hX + hY) + n

        return h
        
    def choosePriorityCrate(self, width, height, crateX, crateY, targetX, targetY, itemsData):
        #this helper function will help the bot choose the correct crate
        #looks for the crate with the smallest heuristic value among the crate

        bestCrate = None
        bestValue = float("inf")

        for each in crates:

            smallestHeuristic = float("inf")

            for each in targets:

                heuristic = self.getHeuristic(width, height, crateX, crateY, targetX, targetY, itemsData)

                if heuristic < smallestHeuristic:
                    smallestHeuristic = heuristic

            if smallestHeuristic < bestValue:
                bestValue = smallestHeuristic
                bestCrate = crate

        return bestCrate

    def aStarSearch(self, width, height, mapData, itemsData):
        #this function will implement the A* search algorithm to find the best path to move a crate to a target
        #it will return the path as a string of directions

        #initialize the open and closed lists
        openList = []
        closedList = set()

        #get the coordinates of the player, crates, and targets
        walls, targets, crates, player = self.getCoordinates(width, height, mapData, itemsData)

        #choose priority target -- TODO
        #choose the priority crate to move
        priorityCrate = self.choosePriorityCrate(width, height, crateX, crateY, targetX, targetY, itemsData)

        #initialize the starting node
        startNode = (player, priorityCrate)
        openList.append(startNode)

        while openList:
            #get the node with the lowest f value
            currentNode = min(openList, key=lambda x: self.getHeuristic(width, height, x[1][0], x[1][1], targetX, targetY, itemsData))
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

    def solveSokobanPuzzle(self, width, height, mapData, itemsData):
        # YOU NEED TO REWRITE THE IMPLEMENTATION OF THIS METHOD TO MAKE THE BOT SMARTER
        # Default stupid behavior: Think (sleep) for 3 seconds, and then return a
        # sequence
        # that just moves left and right repeatedly.


        walls, targets, crates, player = self.getCoordinates(width, height, mapData, itemsData)

        print("Player:", player)
        print("BFS reachable:", sorted(BFS(player, crates)))



        try:
            time.sleep(3)
        except Exception as ex:
            print(ex)
        return "lrlrlrlrlrlrlrlrlrlrlrlrlrlrlrlrlrlrlrlrlrlrlrlrlrlrlrlrlrlrlrlrlrlrlrlrlrlr"