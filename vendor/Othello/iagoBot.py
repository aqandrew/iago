from random import choice
import time  
import sys
#import othelloDiagnostics
oo = 9876 ## infinity for alpha-beta
ALPHA_DEPTH = 5 ## max depth for alpha-beta
CORNER = 9.5
SIDE = 1.5


def timeit(method):

    def timed(*args, **kw):
        ts = time.time()
        result = method(*args, **kw)
        te = time.time()

        print '%r (%r, %r) %2.2f sec' % \
              (method.__name__, args, kw, te-ts)
        return result

    return timed

def free_space(board):
    free = 0
    for i in xrange(8):
            for j in xrange(8):
                if board[i][j] == 0:
                    free = free + 1
    return free

def print_board(board):
    for i in xrange(8):
        for j in xrange(8):
            sys.stdout.write(str(board[i][j]))
            sys.stdout.write(",")
        print ""
    print ""   

class IagoBot(object):
    """Simple bot using a shallow alpha-beta pruning search for 
        finding moves.
    """
    def __init__(self, color):
        self.color = color
        self.board = [[0] * 8 for _ in xrange(8)]
        self.score = [0, 0]
        ## place initial
        self.place(3, 3, 1)
        self.place(4, 4, 1)
        self.place(3, 4, 0)
        self.place(4, 3, 0)
        
        
    def check_board(self, board):
        """checks if the bot has correct information about the world"""
        for i in xrange(8):
            for j in xrange(8):
                assert self.board[i][j] == board[i][j], (i, j, self.board[i][j], board[i][j])

        #print_board(board)

    def list_flips(self, c, r, color):
        """lists stones to flip when player "color" places a stone at c, r"""
        if self.board[c][r]:
            return []
        solution = []
        for dx, dy in ((a, b) for a in xrange(-1,2) for b in xrange(-1,2)):
            toadd = []
            x, y = c + dx, r + dy
            while 0 <= x < 8 and 0 <= y < 8:
                if self.board[x][y] == 1 + color:
                    solution.extend(toadd)
                    break
                elif self.board[x][y] == 0:
                    #empty square
                    break
                #print [x, y, color]
                toadd.append((x, y))
                x += dx
                y += dy
        #print color,solution
        return solution
    
    def place(self, a, b, color, flip = False):
        self.board[a][b] = 1 + color
        if a in (0, 7) and b in (0, 7):
            ## corners cannot be turned
            self.score[color] += CORNER
        elif a in (0, 7) or b in (0, 7):
            self.score[color] += SIDE
            if flip:
                self.score[1 - color] -= SIDE
        else:
            self.score[color] += 1
            if flip:
                self.score[1 - color] -= 1                
    
    def make_move(self, x, y, flips, player):
        for a, b in flips:
            self.place(a, b, player, True)
        self.place(x, y, player)
    
    def undo_move(self, x, y, flips, player):
        for a, b in flips:
            self.place(a, b, 1 - player, True)
        self.board[x][y] = 0
        if x in (0, 7) and y in (0, 7):
            self.score[player] -= CORNER
        elif x in (0, 7) and y in (0, 7):
            self.score[player] -= SIDE
        else:
            self.score[player] -= 1     
    
    def get_ordering(self, player):
        ## Returns ordered list of moves player can make.
        result = []
        for x in xrange(8):
            for y in xrange(8):
                moves = self.list_flips(x, y, player)
                if len(moves):
                    result.append((len(moves), (x, y)))
        ## Returns [] if no appropriate move is found.
        result.sort(reverse = True)
        return result
    @timeit
    def get_move2(self):
        ## backup move generator - returns the move that will generate most gain this turn!
        moves = self.get_ordering(self.color)
        if moves:
            ## place the move
            x, y = moves[0][1]
            for a, b in self.list_flips(x, y, self.color):
                self.place(a, b, self.color, True)
            self.place(x, y, self.color)
            return x, y #(x, y)
        ## Returns None if no moves are found.
    @timeit
    def get_move(self):
        #return self.get_move2()
        ## Gets the best move with alpha_beta
        print free_space(self.board)
        global ALPHA_DEPTH
        if free_space(self.board) < 12:
            ALPHA_DEPTH = 8
        moves = self.get_ordering(self.color)
        if moves:
            x, y = moves[0][1]
            flips = self.list_flips(x, y, self.color)
            self.make_move(x, y, flips, self.color)
            bestAlpha = self.alpha_beta(ALPHA_DEPTH, 1 - self.color, -oo, oo)
            self.undo_move(x, y, flips, self.color)
            bestMove = [(x, y)]
            for _, (x, y) in moves[1:]:
                flips = self.list_flips(x, y, self.color)
                self.make_move(x, y, flips, self.color)
                ## call next round of alpha-betaing.
                result = self.alpha_beta(ALPHA_DEPTH, 1 - self.color, bestAlpha, oo)
                if result > bestAlpha:
                    bestAlpha = result
                    bestMove = [(x, y)]
                elif result == bestAlpha:
                    bestMove.append((x, y))
                ## undo move
                self.undo_move(x, y, flips, self.color)     
            if bestMove is not None:
                bestMove = choice(bestMove) ## pick one of the "best" moves at random. :)
                flips = self.list_flips(bestMove[0], bestMove[1], self.color)
                self.make_move(bestMove[0], bestMove[1], flips, self.color)      
            return bestMove
    
    def heuristic(self):
        """Heuristic - just count the buttons on both sides, giving more value to
            the ones in the corners and sides
            """
        return self.score[self.color] - self.score[1 - self.color] 
    
    def heuristic2(self):
        ## find power spot score & multiply weight
        p = self.p_score()
        p *= 10

        ## find coin parity & multiply weight
        c = self_.c_score()
        c *= .1

        ## find mobility & multiply weight
        m = self.m_score()
        m *= 1
        ## find stability & multiply weight
        s = self.s_score()
        s *= 1

        ## return score
        score = p + c + m + s
        return score
    
    def alpha_beta(self, depth, player, alpha = oo, beta = oo):
        if depth == 0:
            return self.heuristic()

        children = self.get_ordering(player)
        ## print len(children)
        if not children:
            ## player must pass?
            if player == self.color:
                return max(alpha, self.alpha_beta(depth - 1, 1 - player, alpha, beta))
            else:
                return min(beta, self.alpha_beta(depth - 1, 1 - player, alpha, beta))

        for _, (x, y) in children:
            ## make the move first, ask the questions later!
            flips = self.list_flips(x, y, player)
            self.make_move(x, y, flips, player)
            ## call next round of alpha-betaing.
            result = self.alpha_beta(depth - 1, 1 - player, alpha, beta)
            ## undo move
            self.undo_move(x, y, flips, player)
            
            if player == self.color: ## maximizing player
                alpha = max(alpha, result)
            else: ## minimizing player
                beta = min(beta, result)
            if beta <= alpha: break ## alpha cutoff
        if player == self.color:
            return alpha
        else:
            return beta

#############################################################################################

def heuristic2(self):
        ## find power spot score & multiply weight
        p = self.p_score()
        p *= 10

        ## find coin parity & multiply weight
        c = self_.c_score()
        c *= .1

        ## find mobility & multiply weight
        m = self.m_score()
        m *= 1
        ## find stability & multiply weight
        s = self.s_score()
        s *= 1

        ## return score
        score = p + c + m + s
        return score


def is_column_full(col):
    for i in xrange(8):
        if self.board[i][col] == NULL:
            return 0
    return 1

def is_row_full(row):
    for i in xrange(8):
        if self.board[row][i] == NULL:
            return 0
    return 1

def out_of_range(mynum):
    ## makes sure the given index (column or row is on the board)
    if mynum < 0 or mynum > 7:
        return 1 ## true - out of range
    else:
        return 0 ## false - on the board

def increment_direction(k,i,j):
    ##        0 | 1 | 2  
    ##        7 | X | 3
    ##        6 | 5 | 4
    if k == 0:
        a = i - 1
        b = j - 1
        return a,b
    elif k == 1:
        a = i - 1
        b = j
        return a,b
    elif k == 2:
        a = i - 1
        b = j + 1
        return a,b
    elif k == 3:
        a = i
        b = j + 1
        return a,b
    elif k == 4:
        a = i + 1
        b = j + 1
        return a,b
    elif k == 5:
        a = i + 1
        b = j
        return a,b
    elif k== 6:
        a = i + 1
        b = j - 1
        return a,b
    elif k == 7:
        a = i
        b = j - 1
        return a,b

def get_opposite(k):
    ##        0 | 1 | 2  
    ##        7 | X | 3
    ##        6 | 5 | 4
    if k == 0:
        return 4
    elif k == 1:
        return 5
    elif k == 2:
        return 6
    elif k == 3:
        return 7
    elif k == 4:
        return 0
    elif k == 5:
        return 1
    elif k == 6:
        return 2
    elif k == 7:
        return 3

def diagonal_check(self,i,j,direction):
    ## 1 - down - left
    a = i
    b = j
    a,b = self.increment_direction(direction,a,b)
    while 1:
        if self.out_of_range(a) == 0 or self.out_of_range(b) == 0:
            ## successfully reached the end of the diagonal
            return 1
        elif self.board[a][b] == "empty":
            return 0
        ## increment direction
        a,b = self.increment_direction(direction,a,b)

def is_stable(self,stability_board,i,j):
    if self.board[0][0] == 0 or self.board[0][1] == 0 or self.board[1][0] == 0 or \
        self.board[0][7] == 0 or self.board[0][6] == 0 or self.board[1][7] == 0 or \
        self.board[7][7] == 0 or self.board[7][6] == 0 or self.board[6][7] == 0 or \
        self.board[7][0] == 0 or self.board[7][1] == 0 or self.board[6][0] == 0:

        ## count stable squares
        ## its column, row, and both diagonals all need either -
        ##      A) adjacent stable square
        ##      B) its line to be completely filled
        skip = 0
        column = 0
        row = 0
        positive_diagonal = 0
        negative_diagonal = 0

        ## column check
        ## check if line is full
        if self.columns_full(i) == 1:
            column = 1
        ## check if on edge
        elif self.out_of_range(i+1) == 1 or self.out_of_range(i-1) == 1:
                column = 1
        ## adjacent is stable
        elif self.stability_board[i+1][j] == 1 or self.stability_board[i-1][j] == 1:
                column = 1
        ## adjacent is unknown - break function
        elif self.stability_board[i+1][j] == 8 or self.stability_board[i-1][j] == 8:
            return 8
        else:
            column = 0

        ## row check
        ## check if line is full
        if self.rows_full(j) == 1:
            row = 1
        ## check if on edge
        elif self.out_of_range(j+1) == 1 or self.out_of_range(j-1) == 1:
            row = 1
        ## adjacent is stable
        elif self.stability_board[i][j+1] == 1 or self.stability_board[i][j-1] == 1:
            row = 1
        ## adjacent is unknown - break function
        elif self.stability_board[i][j+1] == 8 or self.stability_board[i][j-1] == 8:
            return 8
        else:
            row = 0

        ## positive diagonal check
        ## check if line is full
        if self.diagonal_check(i,j,6) == 1 and self.diagonal_check(i,j,2) == 1:
            positive_diagonal = 1
        ## check if on edge
        elif self.out_of_range(j+1) == 1 or self.out_of_range(j-1) == 1 or self.out_of_range(i+1) or self.out_of_range(i-1):
            positive_diagonal = 1
        ## adjacent is stable
        elif self.stability_board[i+1][j-1] == 1 or self.stability_board[i-1][j+1] == 1:
            positive_diagonal = 1
        ## adjacent is unknown - break function
        elif self.stability_board[i+1][j-1] == 8 or self.stability_board[i-1][j+1] == 8:
            return 8

        ## negative diagonal check
        ## check if line is full
        if self.diagonal_check(i,j,0) == 1 and self.diagonal_check(i,j,4) == 1:
            negative_diagonal = 1
        ## check if on edge
        elif self.out_of_range(j+1) == 1 or self.out_of_range(j-1) == 1 or self.out_of_range(i+1) or self.out_of_range(i-1):
            negative_diagonal = 1
        ## adjacent is stable
        elif self.stability_board[i+1][j+1] == 1 or self.stability_board[i-1][j-1] == 1:
            negative_diagonal = 1
        ## adjacent is unknown - break function
        elif self.stability_board[i+1][j+1] == 8 or self.stability_board[i-1][j-1] == 8:
            return 8

        ## all four directions have been checked and there are no unknowns surrounding it
        ## sum up attributes, if != 4, then it's not stable
        my_sum = column + row + positive_diagonal + negative_diagonal
        if my_sum == 4:
            return 1
        else:
            return 0

    else:
        return 0

def is_unstable(self, i, j):
    a = i
    b = j
    ## find a surrounding opponent piece
    for k in xrange(8):
        possible = 0
        a,b = self.increment_direction(k,a,b)

        while 1:
            if self.out_of_range(a) == 1 or self.out_of_range (b):
                break
            elif self.board[a][b] == "opp color":
                possible = 1
                break
            elif self.board[a][b] == "empty":
                break
            else:
                a,b = self.increment_direction(k,a,b)

        ## if possible - check for empty space across
        if possible == 1:
            x = self.get_opposite(k)
            a = i
            b = j
            a,b = self.increment_direction(x,a,b)
            while 1:
                if self.out_of_range(a) == 1 or self.out_of_range (b):
                    break
                elif self.board[a][b] == "opp color":
                    break
                elif self.board[a][b] == "empty":
                    return 1
                else:
                    ##incremement
                    a,b = self.increment_direction(x)
    return 0

def s_score(self):
    ## find stability score - +1 for stable, 0 for semi-stable, -1 unstable
    
    ## board to save score of each space
    stability_board = [[8] * 8 for _ in range(8)]

    ## list of remaining spaces to get scored - mark "0" for all empty/opponent spaces
    ## mark "-1" if unstable
    ## otherwise save coordinates and move to next space
    to_do_list = []
    for i in xrange(8):
        for j  in xrange(8):
            ## space is empty or opponent's, mark it 0
            if self.board[i][j] != "my color":
                stability_board[i][j] = 0
            ## check if my piece unstable
            elif self.is_unstable(i,j) == 1:
                    ## is unstable
                    stability_board[i][j] = -1
            else:
                ## looking at my pieces
                tup = (i,j)
                to_do_list.append(tup)

    ## create lists of full columns and rows, (columns_full, rows_full)
    columns_full = [0, 0, 0, 0, 0, 0, 0, 0]
    rows_full = [0, 0, 0, 0, 0, 0, 0, 0]
    for i in xrange(8):
        columns_full[i] = self.is_column_full(i)
    for i in xrange(8):
        rows_full[i] = self.is_row_full(i)

    ## go through to_do_list until all spaces have been scored
    ## only examining my pieces that aren't unstable
    ## must either be stable or semi-stable
    while ( len(to_do_list) > 0 ):
        for item in to_do_list:
            i = item[0]
            j = item[1]
            ## check if stable
            if self.is_stable(stability_board,i,j) == 8:
                continue
            elif self.is_stable(stability_board,i,j) == 1:
                stability_board[i][j] = 1
                tup = (i,j)
                to_do_list.remove(tup)
                continue

            ##else - it's semi-stable - value of 0
            else:
                stability_board[i][j] = 0
                tup = (i,j)
                to_do_list.remove(tup)


def c_score(self):
    my_score = 0
    opp_score = 0
    for i in xrange(8):
        for j in xrange(8):
            if self.board[i][j] == "my color":
                my_score += 1
            elif self.board[i][j] == "opp color":
                opp_score += 1
    return my_score - opp_score

def is_legal(self,color,i,j):
    ## return 0 if not legal, 1 if legal
    ## check if space is empty
    if self.board[i][j] != "empty":
        return 0
    ## check in each direction must have an opp then same
    for i in xrange(8):
        a = i
        b = j
        has_opp = 0
        a,b = self.increment_direction(i,a,b)
        while 1:
            ## hits an edge
            if self.out_of_range(a) == 1 or self.out_of_range(b):
                continue
            ## hits same color
            elif self.board[a][b] == "my color":
                if has_opp == 1:
                    return 1
                else:
                    continue

            ## hits empty space
            elif self.board[a][b] == "empty":
                continue
            ## hits opp's color
            elif self.board[a][b] == "opp color":
                has_opp = 1
    return 0

def m_score(self):
    my_moves = 0
    opp_moves = 0
    for i in xrange(8):
        for j in xrange(8):    
            if self.is_legal("my color",i,j) == 1:
                my_moves += 1
            if self.is_legal(" opp color",i,j) == 1:
                opp_moves += 1
    return my_moves - opp_moves

def p_score(self):
    my_score = 0
    opp_score = 0
    ## check for 1 value pt. spots
    ## [2][2],[5][5],[2][5],[5][2]
    if self.board[2][2] == "my color":
        my_score += 1
    elif self.board[2][2] == "opp color":
        opp_score += 1
    
    if self.board[5][5] == "my color":
        my_score += 1
    elif self.board[5][5] == "opp color":
        opp_score += 1
    
    if self.board[2][5] == "my color":
        my_score += 1
    elif self.board[2][5] == "opp color":
        opp_score += 1
    
    if self.board[5][2] == "my color":
        my_score += 1
    elif self.board[5][2] == "opp color":
        opp_score += 1

    ##check for 2 value pt. spots
    ## [0][2],[0][5],[1][0],[1][7],[6][0],[6][7],[7][2],[7][5]
    if self.board[0][2] == "my color":
        my_score += 1
    elif self.board[0][2] == "opp color":
        opp_score += 1

    if self.board[0][5] == "my color":
        my_score += 1
    elif self.board[0][5] == "opp color":
        opp_score += 1

    if self.board[1][0] == "my color":
        my_score += 1
    elif self.board[1][0] == "opp color":
        opp_score += 1

    if self.board[1][7] == "my color":
        my_score += 1
    elif self.board[1][7] == "opp color":
        opp_score += 1

    if self.board[6][0] == "my color":
        my_score += 1
    elif self.board[6][0] == "opp color":
        opp_score += 1

    if self.board[6][7] == "my color":
        my_score += 1
    elif self.board[6][7] == "opp color":
        opp_score += 1

    if self.board[7][2] == "my color":
        my_score += 1
    elif self.board[7][2] == "opp color":
        opp_score += 1

    if self.board[7][5] == "my color":
        my_score += 1
    elif self.board[7][5] == "opp color":
        opp_score += 1

    ## check for 3 value pt. spots
    ## [0][0],[0][7],[7][0],[7][7]
    ## if empty check surrounding -1 value point spots
    ## [0][0] -> surrounding spaces: [0][1],[1][0],[1][1]
    if self.board[0][0] == "my color":
        my_score += 1
    elif self.board[0][0] == "opp color":
        opp_score += 1
    else:
        if self.board[0][1] == "my color":
            my_score -= 2
        elif self.board[0][1] == "opp color":
            opp_score -= 2
        if self.board[1][0] == "my color":
            my_score -= 2
        elif self.board[1][0] == "opp color":
            opp_score -= 2
        if self.board[1][1] == "my color":
            my_score -= 2
        elif self.board[1][1] == "opp color":
            opp_score -= 2

    ## [0][7] -> surrounding spaces: [0][6],[1][7],[1][6]
    if self.board[0][7] == "my color":
        my_score += 1
    elif self.board[0][7] == "opp color":
        opp_score += 1
    else:
        if self.board[0][6] == "my color":
            my_score -= 2
        elif self.board[0][6] == "opp color":
            opp_score -= 2
        if self.board[1][7] == "my color":
            my_score -= 2
        elif self.board[1][7] == "opp color":
            opp_score -= 2
        if self.board[1][6] == "my color":
            my_score -= 2
        elif self.board[1][6] == "opp color":
            opp_score -= 2

    ## [7][0] -> surrounding spaces: [6][0],[7][1],[6][1]
    if self.board[7][0] == "my color":
        my_score += 1
    elif self.board[7][0] == "opp color":
        opp_score += 1
    else:
        if self.board[6][0] == "my color":
            my_score -= 2
        elif self.board[6][0] == "opp color":
            opp_score -= 2
        if self.board[7][1] == "my color":
            my_score -= 2
        elif self.board[7][1] == "opp color":
            opp_score -= 2
        if self.board[6][1] == "my color":
            my_score -= 2
        elif self.board[6][1] == "opp color":
            opp_score -= 2

    ## [7][7] -> surrounding spaces: [7][6],[6][7],[6][6]
    if self.board[7][7] == "my color":
        my_score += 1
    elif self.board[7][7] == "opp color":
        opp_score += 1
    else:
        if self.board[7][6] == "my color":
            my_score -= 2
        elif self.board[7][6] == "opp color":
            opp_score -= 2
        if self.board[6][7] == "my color":
            my_score -= 2
        elif self.board[6][7] == "opp color":
            opp_score -= 2
        if self.board[6][6] == "my color":
            my_score -= 2
        elif self.board[6][6] == "opp color":
            opp_score -= 2

##############################################################################################
            