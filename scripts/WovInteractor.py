
class Interactor:
    CONTINUE = 0
    TERMINATE = 1
    FIRST_WINS = 0
    SECOND_WINS = 1

    def __init__(self):
        self.size = 10
        self.turn = 0
        self.last_remove = 0
        self.scores = [1, 1]
        self.field = [[0 for i in range(self.size)] for j in range(self.size)]
        self.field[0][0] = 1
        self.field[-1][-1] = 3
        pass

    def get_data(self, player):
        little_turn = self.turn % 3 + 1
        self.turn += 1
        lines = 1

        return '{} {}\n'.format(self.size, little_turn) + self.get_field(player), lines

    def can_turn(self, player):
        dx = [1, 1, 0, -1, -1, -1, 0, 1]
        dy = [0, 1, 1, 1, 0, -1, -1, -1]
        ally_soldier_number = 1 if player == 1 else 3
        enemy_soldier_number = 3 if player == 1 else 1
        enemy_corpes_number = 4 if player == 1 else 2

        used = dict()
        stack = []

        for y in range(self.size):
            for x in range(self.size):
                if self.field[y][x] == ally_soldier_number:
                    used[(y, x)] = True
                    stack.append((y, x))

        while len(stack) > 0:
            cur = stack.pop()

            for direction in range(8):
                next_cell = (cur[0] + dy[direction], cur[1] + dx[direction])
                if 0 <= next_cell[0] < self.size and 0 <= next_cell[1] < self.size and not used.get(next_cell):
                    if self.field[next_cell[0]][next_cell[1]] == 0:
                        return True
                    if self.field[next_cell[0]][next_cell[1]] == enemy_soldier_number:
                        return True
                    if self.field[next_cell[0]][next_cell[1]] == enemy_corpes_number:
                        used[next_cell] = True
                        stack.append(next_cell)

        return False

    def is_reachable(self, cell, player):
        dx = [1, 1, 0, -1, -1, -1, 0, 1]
        dy = [0, 1, 1, 1, 0, -1, -1, -1]
        ally_soldier_number = 1 if player == 1 else 3
        enemy_corpes_number = 4 if player == 1 else 2

        used = dict()
        used[cell] = True
        stack = [cell]

        while len(stack) > 0:
            cur = stack.pop()

            for direction in range(8):
                next_cell = (cur[0] + dy[direction], cur[1] + dx[direction])
                if 0 <= next_cell[0] < self.size and 0 <= next_cell[1] < self.size and not used.get(next_cell):
                    if self.field[next_cell[0]][next_cell[1]] == ally_soldier_number:
                        return True
                    if self.field[next_cell[0]][next_cell[1]] == enemy_corpes_number:
                        used[next_cell] = True
                        stack.append(next_cell)

        return False

    # player: 1 or 2
    def put_data(self, player, response):
        response = response.split('\n')

        little_turn = (self.turn - 1) % 3 + 1
        ally_soldier_number = 1 if player == 1 else 3
        enemy_soldier_number = 3 if player == 1 else 1
        enemy_corpes_number = 4 if player == 1 else 2

        next_player = (3 - player) if little_turn == 3 else player

        try:
            x, y = (int(z) for z in response[0].strip(' ').split())
        except ValueError as e:
            return self.TERMINATE, (3 - player, 0, 3), 'PE: {0}'.format(e)
        except IndexError as e:
            return self.TERMINATE, (3 - player, 0, 3), 'PE: {0}'.format(e)

        if x == 0 and y == 0 and not self.can_turn(player):
            if self.can_turn(3 - player):
                return self.CONTINUE, next_player, 'ok. Skip turn.'
            else:
                first_result = 1
                second_result = 1
                winner = 0
                if self.scores[player - 1] > self.scores[2 - player]:
                    first_result += 1
                    winner = player
                elif self.scores[2 - player] > self.scores[player - 1]:
                    second_result += 1
                    winner = 3 - player
                return self.TERMINATE, (winner, first_result, second_result), 'No turns'

        if not 0 < x <= self.size or not 0 < y <= self.size:
            return self.TERMINATE, (3 - player, 0, 3), 'PE: x={0} not in [1, {2}] or y={1} not in [1, {2}]'.format(
                x, y, self.size)

        if self.field[y - 1][x - 1] != 0 and self.field[y - 1][x - 1] != enemy_soldier_number:
            return self.TERMINATE, (3 - player, 0, 3), 'PE: cell ({0}, {1}) isn\'t available'.format(x, y)

        if not self.is_reachable((y - 1, x - 1), player):
            return self.TERMINATE, (3 - player, 0, 3), 'PE: cell ({0}, {1}) isn\'t reachable'.format(x, y)

        if self.field[y - 1][x - 1] == 0:
            self.field[y - 1][x - 1] = ally_soldier_number
            self.scores[player - 1] += 1
        else:
            self.field[y - 1][x - 1] = enemy_corpes_number
            self.scores[2 - player] -= 1

            if self.scores[2 - player] == 0:
                return self.TERMINATE, (player, 3, 0), 'End'

        return self.CONTINUE, next_player, 'ok'

    def represent_cell(self, player, value):
        if player == 1 or value == 0:
            return value
        if value > 2:
            return value - 2
        return value + 2

    def get_field(self, player):
        return '\n'.join([' '.join(str(self.represent_cell(player, x)) for x in self.field[i])
                          for i in range(len(self.field))])
