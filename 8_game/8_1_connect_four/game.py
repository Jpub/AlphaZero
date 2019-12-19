# ====================
# 컨넥트4
# ====================

# 패키지 임포트
import random
import math


# 게임 상태
class State:
    # 초기화
    def __init__(self, pieces=None, enemy_pieces=None):
        # 돌의 배치
        self.pieces = pieces if pieces != None else [0] * 42
        self.enemy_pieces = enemy_pieces if enemy_pieces != None else [0] * 42

    # 돌의 수 얻기
    def piece_count(self, pieces):
        count = 0
        for i in pieces:
            if i == 1:
                count += 1
        return count

    # 패배 여부 판정
    def is_lose(self):
        # 돌 4개 연결 여부 판정
        def is_comp(x, y, dx, dy):
            for k in range(4):
                if y < 0 or 5 < y or x < 0 or 6 < x or \
                        self.enemy_pieces[x + y * 7] == 0:
                    return False
                x, y = x + dx, y + dy
            return True

        # 패배 여부 판정
        for j in range(6):
            for i in range(7):
                if is_comp(i, j, 1, 0) or is_comp(i, j, 0, 1) or \
                        is_comp(i, j, 1, -1) or is_comp(i, j, 1, 1):
                    return True
        return False

    # 무승부 여부 판정
    def is_draw(self):
        return self.piece_count(self.pieces) + self.piece_count(self.enemy_pieces) == 42

    # 게임 종료 여부 판정
    def is_done(self):
        return self.is_lose() or self.is_draw()

    # 다음 상태 얻기
    def next(self, action):
        pieces = self.pieces.copy()
        for j in range(5, -1, -1):
            if self.pieces[action + j * 7] == 0 and self.enemy_pieces[action + j * 7] == 0:
                pieces[action + j * 7] = 1
                break
        return State(self.enemy_pieces, pieces)

    # 합법적인 수 리스트 얻기
    def legal_actions(self):
        actions = []
        for i in range(7):
            if self.pieces[i] == 0 and self.enemy_pieces[i] == 0:
                actions.append(i)
        return actions

    # 선 수 여부 확인
    def is_first_player(self):
        return self.piece_count(self.pieces) == self.piece_count(self.enemy_pieces)

    # 문자열 표시
    def __str__(self):
        ox = ('o', 'x') if self.is_first_player() else ('x', 'o')
        str = ''
        for i in range(42):
            if self.pieces[i] == 1:
                str += ox[0]
            elif self.enemy_pieces[i] == 1:
                str += ox[1]
            else:
                str += '-'
            if i % 7 == 6:
                str += '\n'
        return str


# 랜덤으로 행동 선택
def random_action(state):
    legal_actions = state.legal_actions()
    return legal_actions[random.randint(0, len(legal_actions) - 1)]


# 동작 확인
if __name__ == '__main__':
    # 상태 생성
    state = State()

    # 게임 종료 시까지 반복
    while True:
        # 게임 종료 시
        if state.is_done():
            break

        # 다음 상태 얻기
        state = state.next(random_action(state))

        # 문자열 표시
        print(state)
        print()
