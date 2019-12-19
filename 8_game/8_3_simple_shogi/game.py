# ====================
# 간이 장기
# ====================

# 패키지 임포트
import random
import math


# 게임 상태
class State:
    # 초기화
    def __init__(self, pieces=None, enemy_pieces=None, depth=0):
        # 방향 정수
        self.dxy = ((0, -1), (1, -1), (1, 0), (1, 1), (0, 1), (-1, 1), (-1, 0), (-1, -1))

        # 말의 배치
        self.pieces = pieces if pieces != None else [0] * (12 + 3)
        self.enemy_pieces = enemy_pieces if enemy_pieces != None else [0] * (12 + 3)
        self.depth = depth

        # 말의 초기 배치
        if pieces == None or enemy_pieces == None:
            self.pieces = [0, 0, 0, 0, 0, 0, 0, 1, 0, 2, 4, 3, 0, 0, 0]
            self.enemy_pieces = [0, 0, 0, 0, 0, 0, 0, 1, 0, 2, 4, 3, 0, 0, 0]

    # 패배 여부 판정
    def is_lose(self):
        for i in range(12):
            if self.pieces[i] == 4:  # 사자 말 존재
                return False
        return True

    # 무승부 여부 판정
    def is_draw(self):
        return self.depth >= 300  # 300수

    # 게임 종료 여부 판정
    def is_done(self):
        return self.is_lose() or self.is_draw()

    # 듀얼 네트워크 입력 2차원 배열 얻기
    def pieces_array(self):
        # 플레이어 별 듀얼 네트워크 입력 1차원 배열 얻기
        def pieces_array_of(pieces):
            table_list = []
            # 0: 병아리, 1: 코끼리, 2: 기린, 3: 사자
            for j in range(1, 5):
                table = [0] * 12
                table_list.append(table)
                for i in range(12):
                    if pieces[i] == j:
                        table[i] = 1

            # 4: 획득한 상대방 병아리, 5: 획득한 상대방 코끼리, 6: 획득한 상대방 기린
            for j in range(1, 4):
                flag = 1 if pieces[11 + j] > 0 else 0
                table = [flag] * 12
                table_list.append(table)
            return table_list

        # 듀얼 네트워크 입력 2차원 배열 반환
        return [pieces_array_of(self.pieces), pieces_array_of(self.enemy_pieces)]

    # 말의 이동 도착 위치 및 이동 시작 위치를 행동으로 변환
    def position_to_action(self, position, direction):
        return position * 11 + direction

    # 행동을 말의 이동 도착 위치 및 이동 시작 위치로 변환
    def action_to_position(self, action):
        return (int(action / 11), action % 11)

    # 합법적인 수의 리스트 얻기
    def legal_actions(self):
        actions = []
        for p in range(12):
            # 말 이동 시
            if self.pieces[p] != 0:
                actions.extend(self.legal_actions_pos(p))

            # 획득한 상대방의 말 배치 시
            if self.pieces[p] == 0 and self.enemy_pieces[11 - p] == 0:
                for capture in range(1, 4):
                    if self.pieces[11 + capture] != 0:
                        actions.append(self.position_to_action(p, 8 - 1 + capture))
        return actions

    # 말이 이동하는 경우의 합법적인 수의 리스트 얻기
    def legal_actions_pos(self, position_src):
        actions = []

        # 말이 이동 가능한 방향
        piece_type = self.pieces[position_src]
        if piece_type > 4: piece_type - 4
        directions = []
        if piece_type == 1:  # 병아리
            directions = [0]
        elif piece_type == 2:  # 코끼리
            directions = [1, 3, 5, 7]
        elif piece_type == 3:  # 기린
            directions = [0, 2, 4, 6]
        elif piece_type == 4:  # 사자
            directions = [0, 1, 2, 3, 4, 5, 6, 7]

        # 합법적인 수 얻기
        for direction in directions:
            # 말의 이동 전 위치
            x = position_src % 3 + self.dxy[direction][0]
            y = int(position_src / 3) + self.dxy[direction][1]
            p = x + y * 3

            # 이동 가능한 경우에는 합법적인 수로 추가
            if 0 <= x and x <= 2 and 0 <= y and y <= 3 and self.pieces[p] == 0:
                actions.append(self.position_to_action(p, direction))
        return actions

    # 다음 상태 얻기
    def next(self, action):
        # 다음 상태 생성
        state = State(self.pieces.copy(), self.enemy_pieces.copy(), self.depth + 1)

        # 행동을 (이동 대상 위치, 이동 전 위치)로 변환
        position_dst, position_src = self.action_to_position(action)

        # 말 이동
        if position_src < 8:
            # 말 이동 대상 위치
            x = position_dst % 3 - self.dxy[position_src][0]
            y = int(position_dst / 3) - self.dxy[position_src][1]
            position_src = x + y * 3

            # 말 이동
            state.pieces[position_dst] = state.pieces[position_src]
            state.pieces[position_src] = 0

            # 상대의 말이 존재하는 경우에는 획득
            piece_type = state.enemy_pieces[11 - position_dst]
            if piece_type != 0:
                if piece_type != 4:
                    state.pieces[11 + piece_type] += 1  # 획득한 말 +1
                state.enemy_pieces[11 - position_dst] = 0

        # 획득한 상대방의 말 배치
        else:
            capture = position_src - 7
            state.pieces[position_dst] = capture
            state.pieces[11 + capture] -= 1  # 획득한 말 -1

        # 말 교대
        w = state.pieces
        state.pieces = state.enemy_pieces
        state.enemy_pieces = w
        return state

    # 선 수 여부 판정
    def is_first_player(self):
        return self.depth % 2 == 0

    # 문자열 표시
    def __str__(self):
        pieces0 = self.pieces if self.is_first_player() else self.enemy_pieces
        pieces1 = self.enemy_pieces if self.is_first_player() else self.pieces
        hzkr0 = ('', 'H', 'Z', 'K', 'R')
        hzkr1 = ('', 'h', 'z', 'k', 'r')

        # 선 수 플레이어가 획득한 말
        str = '['
        for i in range(12, 15):
            if pieces1[i] >= 2: str += hzkr1[i - 11]
            if pieces1[i] >= 1: str += hzkr1[i - 11]
        str += ']\n'

        # 보드
        for i in range(12):
            if pieces0[i] != 0:
                str += hzkr0[pieces0[i]]
            elif pieces1[11 - i] != 0:
                str += hzkr1[pieces1[11 - i]]
            else:
                str += '-'
            if i % 3 == 2:
                str += '\n'

        # 선 수 플레이어가 획득한 말
        str += '['
        for i in range(12, 15):
            if pieces0[i] >= 2: str += hzkr0[i - 11]
            if pieces0[i] >= 1: str += hzkr0[i - 11]
        str += ']\n'
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
