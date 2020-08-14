#!python2
import csv
import sys
import os
from copy import deepcopy
import numpy as np

class sudokuNode():
    def __init__(self, val, x, y):
        self.value = val
        self.avail = [i for i in range(1, 10)]
        self.x = x
        self.y = y

    def positions(self):
        return self.x, self.y

    ##Need to check within rows, columns, and within a 3x3 block
    ##3x3 block will be separated into 9 quadrants based on ceil(x/3), ceil(y/3)
class SudokuBoard():
    def __init__(self, Board):
        self.Board = self.MakeBoard(Board)
        self.CheckNodes = []

    def MakeBoard(self, Board):
        row, col = Board.shape
        NewBoard = Board.copy()
        for i in range(0, row):
            for j in range(0, col):
                NewBoard[i, j] = sudokuNode(Board[i, j], i, j)
        return NewBoard

    ##Constrains on horizontal axis
    def CheckHorizontal(self, row, col):
        curnode = self.Board[row, col].avail
        for c in range(0, 9):
            checkagainst = self.Board[row, c]
            if checkagainst.value in curnode:
                curnode.remove(checkagainst.value)

        return

    ##Constrains on vertical axis
    def CheckVertical(self, row, col):
        curnode = self.Board[row, col].avail
        for r in range(0, 9):
            checkagainst = self.Board[r, col].value
            if checkagainst in curnode:
                curnode.remove(checkagainst)

        return

    ##Constrains on each quadrant
    def CheckQuadrants(self, row, col):
        curnode = self.Board[row, col].avail
        quadx, quady = determineQuadrants(row, col)
        for x in range(0, 3):
            for y in range(0, 3):
                checkagainst = self.Board[quadx*3+x, quady*3+y].value
                if checkagainst in curnode:
                    curnode.remove(checkagainst)

        return


    ##Checks the constraints within checkNodes in horizontal, vertical, or quadrant constraints
    def CheckConstraints(self, CheckNodes):
        counts = [0] * 10
        for row in CheckNodes:
            for x in row.avail:
                counts[x] += 1

        ##Looks up whether a constraint value occurs a single time, if it does, add the value and call AC_3 again
        ones = np.where(np.array(counts) == 1)  # [i for i, x in enumerate(counts) if x == 1]
        for i in range(0, len(ones[0])):
            for j in range(0, len(CheckNodes)):
                if ones[0][i] in CheckNodes[j].avail:
                    CheckNodes[j].avail = [ones[0][i]]
                    AC_3(self)
        return


    def printBoard(self):
        for i in range(0, 9):
            for j in range(0, 9):
                test = self.Board[i, j]
                sys.stdout.write(str(test.value))
                if j != 8:
                    sys.stdout.write(',')
            if i != 8:
                sys.stdout.write('\n')

    def solved(self):
        for i in range(0, 9):
            for j in range(0, 9):
                if self.Board[i, j].value == 0:
                    return False
        return True

    ##Determines if there are any 0's with available nodes left to search
    def searchQueue(self):
        searchQueue = {}
        for i in range(0, 9):
            for j in range(0, 9):
                if self.Board[i, j].value == 0 and len(self.Board[i, j].avail) > 0:
                    searchQueue[self.Board[i, j]] = self.Board[i, j].avail


        return searchQueue
def AC_3(Board):
    ##Initiate first with ALL 0s available
    #X = Board
    #D = domains (.avail)
    #C = constraints

    ##Keep the queue ordered with the minimal remaining value heuristi. Priority queue?
    #while queue is not empty:
        ##Pop
        #if revise() is true:


    ##First initial constraints
    for j in range(0, 9):
        for k in range(0, 9):
            curBoard = Board.Board[j, k]
            if curBoard.value == 0:
                Board.CheckHorizontal(j, k)
                Board.CheckVertical(j, k)
                Board.CheckQuadrants(j, k)

                if len(curBoard.avail) == 1:
                    curBoard.value = curBoard.avail[0]
                    AC_3(Board) ##Recursively call AC_3 after adding a value in

    ##Here we check constraint satisfaction between nodes by finding unique values within one another
    for allrow in range(0, 9):
        for allcol in range(0, 9):
            ##Horizontal
            quadx, quady = determineQuadrants(allrow, allcol)
            CheckNodes = []
            for c in range(0, 9):
                checkagainst = Board.Board[allrow, c]
                if checkagainst.value == 0:
                    CheckNodes.append(checkagainst)

            Board.CheckConstraints(CheckNodes)

            ##Vertical
            CheckNodes = []
            for r in range(0, 9):
                checkagainst = Board.Board[r, allcol].value
                if checkagainst == 0:
                    CheckNodes.append(Board.Board[r, allcol])

            Board.CheckConstraints(CheckNodes)

            ##Quadrant
            CheckNodes = []
            for x in range(0, 3):
                for y in range(0, 3):
                    checkagainst = Board.Board[quadx*3+x, quady*3+y].value
                    if checkagainst == 0:
                        CheckNodes.append(Board.Board[quadx*3+x, quady*3+y])

            Board.CheckConstraints(CheckNodes)


    return

##Backtracking algorithm doing a DFS recursive search on uncertain nodes
def backtrack(Board):

    if Board.solved():
        return Board

    copyboard = deepcopy(Board)
    makequeue = copyboard.searchQueue()
    while True:

        ##Once the search is finished, do not call again
        if len(makequeue) == 0:
            return copyboard

        ##Ordering the nodes based on MRV
        newdict = sorted(makequeue, key=lambda k: len(makequeue[k]))
        newdict = deepcopy(newdict)
        ##Trying to pop
        try:
            addVal = newdict[0].avail.pop()
        except:
            makequeue.pop(newdict[0])
            continue

        ##Grab values and recursively call backtrack algorithm
        x, y = newdict[0].positions()
        copyboard.Board[x, y].value = addVal
        AC_3(copyboard)
        backtrack(copyboard)
        # makequeue[newdict[0]].append(addVal)
        copyboard.Board[x, y].value = 0

    return copyboard


##Figure out which quadrant a certain number is in based on 0 - 8 where 8 is the bottom right corner, 0 is top left
def determineQuadrants(row, col):
    quadx = int(np.floor(row/3))
    quady = int(np.floor(col/3))
    return quadx, quady

if __name__ == '__main__':
    Board = []
    with open(os.path.join(os.getcwd(), 'suinput.csv'), 'r') as csvfile:
        csvdata = csv.reader(csvfile, delimiter=',')
        for i in csvdata:
            ##Grabs everything in list and strips whitespace
            Board.append([int(strdata.strip()) for strdata in i])

    Board = np.array(Board, dtype=np.object)
    Board = SudokuBoard(Board)
    ##Store all zeros in a priority queue where it's based on the number of values available
    AC_3(Board)
    backtrack(Board)
    print("Finished backtracking")
    Board.printBoard()


    ##Outputting data
    with open(os.path.join(os.getcwd(), 'suoutput.txt'), 'w') as csvfile:
        for i in range(0, 9):
            for j in range(0, 9):
                csvfile.write(str(Board.Board[i, j].value))
                if j != 8:
                    csvfile.write(',')
            if i != 8:
                csvfile.write('\n')
