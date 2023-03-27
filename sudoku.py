import random


class sudoku:
    """puzzle solver"""

    def __init__(self, n):
        # utility lists for examining nine-tants
        self.done = 0
        self.n_sqrd = n * n
        self.order = n
        self.bounds = range(1, self.n_sqrd + 1)
        self.guesses = []
        self.guessresults = []
        self.uppers = []
        self.unguesscount = 0
        for i in range(0, n):
            for j in range(0, n):
                self.uppers.append([i * n + 1, j * n + 1])
        if n < 100:
            self.fullformat = "%4d"
            self.emptyformat = "____"
        if n < 31:
            self.fullformat = "%3d"
            self.emptyformat = "___"
        if n < 10:
            self.fullformat = "%2d"
            self.emptyformat = "__"
        if n < 4:
            self.fullformat = "%1d"
            self.emptyformat = "_"

        self.deltas = []
        for i in range(0, n):
            for j in range(0, n):
                self.deltas.append([i, j])
        self.gl = [None]
        self.gc = [None]
        for i in self.bounds:
            self.gl.append([None])
            self.gc.append([None])
            for j in self.bounds:
                self.gl[i].append(None)
                self.gc[i].append(0)
        print("gl is ", self.gl)
        print("gc is ", self.gc)

    def setpuzzle(self, puzzle):
        self.puzzle = puzzle

    def pretty(self, a):
        """convinience routine for printing"""
        if a:
            return self.fullformat % a
        else:
            return self.emptyformat

    def printpuzzle(self):
        for i in self.bounds:
            for j in self.bounds:
                print( self.pretty(self.puzzle[i][j]),end=" ")
            print("")

    def inittaken(self):
        """builds taken set for each cell, initially empty"""
        self.taken = [None]
        for i in self.bounds:
            self.taken.append([None])
            for j in self.bounds:
                self.taken[i].append({})

    def all_taken(self):
        """sees if all ones are taken, etc. if they are, they're taken
        for every cell"""

        full = 0
        counts = [0]
        for i in self.bounds:
            counts.append(0)

        for i in self.bounds:
            for j in self.bounds:
                val = self.puzzle[i][j]
                if val:
                    counts[val] = counts[val] + 1

        print("all_taken: counts ", counts)

        for k in self.bounds:
            if counts[k] == self.n_sqrd:
                full = full + 1
                for i in self.bounds:
                    for j in self.bounds:
                        self.taken[i][j][k] = 1

        if full == self.n_sqrd:
            self.done = 1

    #

    def update_taken(self):
        """updates taken set for each cell"""
        for i in self.bounds:
            for j in self.bounds:
                for k in self.bounds:
                    if self.puzzle[i][k]:
                        self.taken[i][j][self.puzzle[i][k]] = 1
                for k in self.bounds:
                    if self.puzzle[k][j]:
                        self.taken[i][j][self.puzzle[k][j]] = 1

        for ui, uj in self.uppers:
            for di, dj in self.deltas:
                for ei, ej in self.deltas:
                    if self.puzzle[ui + ei][uj + ej]:
                        self.taken[ui + di][uj + dj][self.puzzle[ui + ei][uj + ej]] = 1

    def missing(self, set):
        """if one item is missing from the set, return that item"""
        for i in self.bounds:
            if not (i in set):
                return i
        raise "Can't happen: missing:" + str(set)

    def one_round(self):
        """try increasingly computational heuristics..."""

        if self.force() or self.pigeonhole():
            return 1
        else:
            self.all_taken()
            if self.done:
                return 0
            self.pairs()
            if self.force() or self.pigeonhole():
                return 1

        if self.guessone():
            return 1

        self.unguess()
        if self.force() or self.pigeonhole():
            return 1
        if self.guessone():
            return 1
        return 0

    def onebits(self, n):
        res = 0
        while n & 1:
            res = res + 1
            n = n / 2
        return res

    def unguess(self):
        k = self.onebits(self.unguesscount) + 1
        self.unguesscount = self.unguesscount + 1
        if self.unguesscount > self.n_sqrd:
            return
        if len(self.guesses) == 0:
            print( "no guesses left to undo...")
            return
        while len(self.guesses) and k > 0:
            k = k - 1
            first = self.guesses.pop()
            results = self.guessresults.pop()
            for i, j in results:
                self.puzzle[i][j] = None
            print("unguessing at ", first)
            self.puzzle[first[0]][first[1]] = None
        self.inittaken()
        self.update_taken()
        self.all_taken()

    def force(self):
        """look for cells whose taken set has 8 members, so must be the
        remaining one"""
        res = 0
        for i in self.bounds:
            for j in self.bounds:
                if (
                    self.puzzle[i][j] == None
                    and len(self.taken[i][j]) == self.n_sqrd - 1
                ):
                    mustbe = self.missing(self.taken[i][j])
                    print("force: at ", i, j, "can only be ", mustbe)
                    if self.checkmove(i, j, mustbe):
                        print("did that...")
                        return 1
                    else:
                        print("contradictory state -- back out guesses...")
                        self.unguess()

        return res

    #
    def pigeonhole(self):
        """look for rows, columns, or nine-tants that have only one cell
        that can be a given integer"""
        res = 0
        for n in self.bounds:
            for i in self.bounds:
                rcount = 0
                rslot = None
                ccount = 0
                cslot = None
                for k in self.bounds:
                    if not (n in self.taken[i][k]) and None == self.puzzle[i][k]:
                        rcount = rcount + 1
                        rslot = k
                    if not (n in self.taken[k][i]) and None == self.puzzle[k][i]:
                        ccount = ccount + 1
                        cslot = k
                if rcount == 1:
                    print("pigeonhole: row ", i, "has just one possible", n)
                    if self.checkmove(i, rslot, n):
                        print("did that...")
                        return 1
                if ccount == 1:
                    print("pigeonhole: col ", i, "has just one possible", n)
                    if self.checkmove(cslot, i, n):
                        print( "did that...")
                        return 1

            for ui, uj in self.uppers:
                bcount = 0
                for di, dj in self.deltas:
                    if (
                        self.puzzle[ui + di][uj + dj] == None
                        and not n in self.taken[ui + di][uj + dj]
                    ):
                        bi, bj = (ui + di, uj + dj)
                        bcount = bcount + 1

                if bcount == 1:
                    print("pigeonhole: corner ", ui, uj, " has just one possible", n,end="")
                    print("at ", bi, bj)
                    if self.checkmove(bi, bj, n):
                        print("did that...")
                        return 1

        return res

    def get_avail(self, i, j):
        res = []
        for k in self.bounds:
            if not k in self.taken[i][j]:
                res.append(k)
        return res

    def pairs(self):

        # go through each sub-square
        for ui, uj in self.uppers:
            # pmap gets a list of coordinates where only pairs
            # of numbers are possible, that is
            # {[2,3]: [[1,1],[3,3]]} means that locations 1,1 and 3,3
            # are restricted to values 2 and 3
            pmap = {}
            bcount = 0
            for di, dj in self.deltas:
                i = ui + di
                j = uj + dj
                if (
                    self.puzzle[i][j] == None
                    and len(self.taken[i][j]) == self.n_sqrd - 2
                ):
                    # cell has two values possible, find them
                    pair = tuple(self.get_avail(i, j))
                    # update pmap
                    if pair not in pmap:
                        pmap[pair] = [[i, j]]
                    else:
                        pmap[pair].append([i, j])

            for pair in pmap:
                print("pairs: %s" % repr(pmap))
                if len(pmap[pair]) == 2:
                    print("pairs: pair of %s at %s" % (repr(pair), repr(pmap[pair])))
                    if pmap[pair][0][0] == pmap[pair][1][0]:
                        # same row
                        r = pmap[pair][0][0]
                        c = pmap[pair][0][1]
                        d = pmap[pair][1][1]
                        for k in self.bounds:
                            if k != c and k != d:
                                print("putting %s on %s" % (pair, [r, k]))
                                self.taken[r][k][pair[0]] = 1
                                self.taken[r][k][pair[1]] = 1
                    if pmap[pair][0][1] == pmap[pair][1][1]:
                        # same row
                        c = pmap[pair][0][1]
                        print("updating col: %d" % c)
                        r = pmap[pair][0][0]
                        s = pmap[pair][1][0]
                        for k in self.bounds:
                            if k != r and k != s:
                                print("putting %s on %s" % (pair, [k, c]))
                                self.taken[k][c][pair[0]] = 1
                                self.taken[k][c][pair[1]] = 1

                    for di, dj in self.deltas:
                        i = ui + di
                        j = uj + dj
                        if [i, j] not in pmap[pair]:
                            print("putting %s on %s" % (pair, [i, j]))
                            self.taken[i][j][pair[0]] = 1
                            self.taken[i][j][pair[1]] = 1

    def checkmove(self, i, j, n):
        for k in self.bounds:
            if (
                k != j
                and self.puzzle[i][k] == None
                and len(self.taken[i][k]) == self.n_sqrd - 1
                and self.missing(self.taken[i][k]) == n
            ):
                print("checkmove: setting", i, j, " to ", n, "wedges row", i, k)
                return 0
            if (
                k != i
                and self.puzzle[k][j] == None
                and len(self.taken[k][j]) == self.n_sqrd - 1
                and self.missing(self.taken[k][j]) == n
            ):
                print("checkmove: setting", i, j, " to ", n, "wedges col", k, j)
                return 0

        ui = int((i - 1) / self.order) * self.order + 1
        uj = int((j - 1) / self.order) * self.order + 1
        for di, dj in self.deltas:
            ti = ui + di
            tj = uj + dj
            if (
                ti != i
                and tj != j
                and self.puzzle[ti][tj] == None
                and len(self.taken[ti][tj]) == self.n_sqrd - 1
                and self.missing(self.taken[ti][tj]) == n
            ):
                print("checkmove: setting", i, j, " to ", n, " wedges n-tant", ui + di, uj + dj)
                return 0

        if len(self.guessresults) > 0:
            self.guessresults[-1].append([i, j])
        self.puzzle[i][j] = n
        self.update_taken()
        return 1

    def guessone(self):
        print("okay, guessing...")
        maxlen = 0
        minlen = self.n_sqrd
        maxi = 0
        maxj = 0
        mini = 0
        minj = 0
        for i in self.bounds:
            for j in self.bounds:
                l = len(self.taken[i][j])
                if l >= maxlen and l < self.n_sqrd and self.puzzle[i][j] == None:
                    maxlen = l
                    maxi = i
                    maxj = j
                if l <= minlen and self.puzzle[i][j] == None:
                    minlen = l
                    mini = i
                    minj = j

        if minlen == 0:
            print("freebee at ", mini, minj)
            if self.checkmove(mini, minj, 1):
                print("did that...")
                self.guesses.append([mini, minj])
                self.guessresults.append([])
                return 1

        if maxlen > 0:
            print("maxlen ", maxlen, " is at ", maxi, maxj, "taken is ", 
               self.taken[maxi][maxj])
            r = self.bounds
            if self.gl[maxi][maxj] == None:
                gl = []
                for k in r:
                    if not k in self.taken[maxi][maxj]:
                        gl.append(k)
                self.gl[maxi][maxj] = gl
            else:
                gl = self.gl[maxi][maxj]
            skipcount = self.gc[maxi][maxj] % len(gl)
            self.gc[maxi][maxj] = skipcount + 1

            for k in gl:
                print("trying ", k)
                skipcount = skipcount - 1
                if skipcount < 0 and self.checkmove(maxi, maxj, k):
                    print("did that...")
                    print("guessone: at", maxi, maxj, "guessed", k)
                    self.guesses.append([maxi, maxj])
                    self.guessresults.append([])
                    return 1
        return 0

    def solver(self):
        self.inittaken()
        self.update_taken()
        self.printpuzzle()
        self.pairs()
        while self.one_round():
            self.printpuzzle()
        # self.printpuzzle()


#

_ = None
__ = None
if 1:
    x = sudoku(3)
    x.setpuzzle(
        [
            _,
            [_, _, 2, _, _, 9, _, _, _, 6],
            [_, _, _, 9, 7, _, 8, _, _, 1],
            [_, _, _, _, 1, 2, 5, _, _, _],
            [_, _, 7, _, _, _, _, 1, _, _],
            [_, 4, 6, _, _, _, _, _, 2, 8],
            [_, _, _, 3, _, _, _, _, 5, _],
            [_, _, _, _, 5, 7, 1, _, _, _],
            [_, 8, _, _, 9, _, 6, 7, _, _],
            [_, 3, _, _, _, 4, _, _, 1, _],
        ]
    )
if 0:
    x = sudoku(4)
    x.setpuzzle(
        [
            _,
            [_, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _],
            [_, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _],
            [_, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _],
            [_, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _],
            [_, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _],
            [_, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _],
            [_, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _],
            [_, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _],
            [_, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _],
            [_, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _],
            [_, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _],
            [_, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _],
            [_, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _],
            [_, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _],
            [_, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _],
            [_, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _],
        ]
    )
if 0:
    x = sudoku(3)
    x.setpuzzle(
        [
            _,
            [_, _, _, _, _, _, _, _, _, _],
            [_, _, _, _, _, _, _, _, _, _],
            [_, _, _, _, _, _, _, _, _, _],
            [_, _, _, _, _, _, _, _, _, _],
            [_, _, _, _, _, _, _, _, _, _],
            [_, _, _, _, _, _, _, _, _, _],
            [_, _, _, _, _, _, _, _, _, _],
            [_, _, _, _, _, _, _, _, _, _],
            [_, _, _, _, _, _, _, _, _, _],
        ]
    )
if 0:
    x = sudoku(2)
    x.setpuzzle(
        [
            _,
            [_, _, _, _, _],
            [_, _, _, _, _],
            [_, _, _, _, _],
            [_, _, _, _, _],
        ]
    )
if 0:
    x = sudoku(4)
    x.setpuzzle(
        [
            _,
            [_, 5, _, 2, _, 4, _, 3, _, _, _, _, _, _, _, _, _],
            [_, 4, _, _, _, _, _, 7, _, 2, _, _, _, _, _, _, _],
            [_, _, 1, _, _, _, _, 5, _, _, 6, _, _, _, _, _, _],
            [_, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _],
            [_, _, 3, _, _, _, 9, _, _, _, _, 2, _, _, _, _, _],
            [_, _, 8, _, _, _, _, _, _, _, 4, _, _, _, _, _, _],
            [_, 7, _, _, _, _, 4, _, _, _, 1, _, _, _, _, _, _],
            [_, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _],
            [_, _, 2, _, _, 1, _, _, _, _, 9, _, _, _, _, _, _],
            [_, _, _, 8, _, 3, _, _, _, _, _, 6, _, _, _, _, _],
            [_, _, _, _, _, 6, _, 9, _, 8, _, 4, _, _, _, _, _],
            [_, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _],
            [_, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _],
            [_, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _],
            [_, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _],
            [_, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _],
        ]
    )
if 0:
    x = sudoku(4)
    x.setpuzzle(
        [
            _,
            [_, 5, _, 2, _, 4, _, 3, _, _, _, _, _, _, _, _, _],
            [_, 4, _, _, _, _, _, 7, _, 2, _, _, _, _, _, _, _],
            [_, _, 1, _, _, _, _, 5, _, _, 6, _, _, _, _, _, _],
            [_, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _],
            [_, _, 3, _, _, _, 9, _, _, _, _, 2, _, _, _, _, _],
            [_, _, 8, _, _, _, _, _, _, _, 4, _, _, _, _, _, _],
            [_, 7, _, _, _, _, 4, _, _, _, 1, _, _, _, _, _, _],
            [_, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _],
            [_, _, 2, _, _, 1, _, _, _, _, 9, _, _, _, _, _, _],
            [_, _, _, 8, _, 3, _, _, _, _, _, 6, _, _, _, _, _],
            [_, _, _, _, _, 6, _, 9, _, 8, _, 4, _, _, _, _, _],
            [_, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _],
            [_, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _],
            [_, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _],
            [_, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _],
            [_, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _],
        ]
    )
if 0:
    x = sudoku(3)
    x.setpuzzle(
        [
            _,
            [_, 5, _, 2, 4, _, 3, _, _, _],
            [_, 4, _, _, _, _, 7, 2, _, _],
            [_, _, 1, _, _, _, 5, _, 6, _],
            [_, _, 3, _, _, 9, _, _, _, 2],
            [_, _, 8, _, _, _, _, _, 4, _],
            [_, 7, _, _, _, 4, _, _, 1, _],
            [_, _, 2, _, 1, _, _, _, 9, _],
            [_, _, _, 8, 3, _, _, _, _, 6],
            [_, _, _, _, 6, _, 9, 8, _, 4],
        ]
    )
if 0:
    x = sudoku(3)
    x.setpuzzle(
        [
            _,
            [_, 3, _, _, 4, 1, _, _, 7, _],
            [_, _, 5, 1, _, _, 2, _, _, _],
            [_, _, 4, _, _, 6, _, _, _, _],
            [_, _, _, 7, _, 5, 8, 1, 6, _],
            [_, _, _, _, _, 7, _, _, _, _],
            [_, _, 1, 5, 2, 9, _, 8, _, _],
            [_, _, _, _, _, 3, _, _, 9, _],
            [_, _, _, _, 6, _, _, 7, 5, _],
            [_, _, 3, _, _, 4, 7, _, _, 6],
        ]
    )
if 0:
    x = sudoku(3)
    # hard puzzle from nyt
    x.setpuzzle(
        [
            _,
            [_, _, _, _, _, _, _, _, _, _],
            [_, 4, 1, _, 5, _, _, 7, _, _],
            [_, _, 5, _, _, 9, _, 8, _, 1],
            [_, 6, _, _, _, 4, _, _, _, 3],
            [_, 8, _, 9, _, 1, _, 4, _, _],
            [_, _, 7, _, _, _, _, 2, _, _],
            [_, _, _, _, _, 3, _, 3, _, 8],
            [_, _, _, _, 1, _, _, _, _, _],
            [_, _, _, 3, 7, _, 2, _, 6, _],
        ]
    )
x.solver()
