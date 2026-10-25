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

    def getHeursitic(self, width, height, crateX, crateY,
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

    def solveSokobanPuzzle(self, width, height, mapData, itemsData):
        # YOU NEED TO REWRITE THE IMPLEMENTATION OF THIS METHOD TO MAKE THE BOT SMARTER
        # Default stupid behavior: Think (sleep) for 3 seconds, and then return a
        # sequence
        # that just moves left and right repeatedly.

        DIRS = {"u": (-1, 0), "d": (1, 0), "l": (0, -1), "r": (0, 1)}

        walls, targets, crates, player = self.getCoordinates(width, height, mapData, itemsData)

        def BFS(player, crates):
            # uses BFS to search where the player can walk without pushing anything

            visited = {player}  # tiles found

            queue = deque([player])  # tiles that are waiting to be visited/checked
            while queue:
                r, c = queue.popleft()
                for dr, dc in DIRS.values():
                    next = (r + dr, c + dc)     # let next be equal to the old + the change in direction
                    if next not in visited and next not in walls and next not in crates:
                        visited.add(next)   # mark tile as visited/reachable
                        queue.append(next)  # check the tiles adjacent to it later

            return visited

        print("Player:", player)
        print("BFS reachable:", sorted(BFS(player, crates)))



        try:
            time.sleep(3)
        except Exception as ex:
            print(ex)
        return "lrlrlrlrlrlrlrlrlrlrlrlrlrlrlrlrlrlrlrlrlrlrlrlrlrlrlrlrlrlrlrlrlrlrlrlrlrlr"