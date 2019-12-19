# ====================
# 틱택토
# ====================

# 패키지 임포트
import random
import math


# 게임 상태
class State:
    # 초기화
    def __init__(self, pieces=None, enemy_pieces=None):
        # 돌의 배치
        self.pieces = pieces if pieces != None else [0] * 9
        self.enemy_pieces = enemy_pieces if enemy_pieces != None else [0] * 9

    # 돌의 수 얻기
    def piece_count(self, pieces):
        count = 0
        for i in pieces:
            if i == 1:
                count += 1
        return count

    # 패배 여부 판정
    def is_lose(self):
        # 돌 3개 연결 여부 확인
        def is_comp(x, y, dx, dy):
            for k in range(3):
                if y < 0 or 2 < y or x < 0 or 2 < x or \
                        self.enemy_pieces[x + y * 3] == 0:
                    return False
                x, y = x + dx, y + dy
            return True

        # 패배 여부 판정
        if is_comp(0, 0, 1, 1) or is_comp(0, 2, 1, -1):
            return True
        for i in range(3):
            if is_comp(0, i, 1, 0) or is_comp(i, 0, 0, 1):
                return True
        return False

    # 무승부 여부 확인
    def is_draw(self):
        return self.piece_count(self.pieces) + self.piece_count(self.enemy_pieces) == 9

    # 게임 종료 여부 확인
    def is_done(self):
        return self.is_lose() or self.is_draw()

    # 다음 상태 얻기
    def next(self, action):
        pieces = self.pieces.copy()
        pieces[action] = 1
        return State(self.enemy_pieces, pieces)

    # 합법적인 수의 리스트 얻기
    def legal_actions(self):
        actions = []
        for i in range(9):
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
        for i in range(9):
            if self.pieces[i] == 1:
                str += ox[0]
            elif self.enemy_pieces[i] == 1:
                str += ox[1]
            else:
                str += '-'
            if i % 3 == 2:
                str += '\n'
        return str


# 랜덤으로 행동 선택
def random_action(state):
    legal_actions = state.legal_actions()
    return legal_actions[random.randint(0, len(legal_actions) - 1)]


# 알파베타법을 활용한 상태 가치 계산
def alpha_beta(state, alpha, beta):
    # 패배 시 상태 가치 -1
    if state.is_lose():
        return -1

    # 무승부 시, 상테 가치 0
    if state.is_draw():
        return 0

    # 합법적인 수의 상태 가치 계산
    for action in state.legal_actions():
        score = -alpha_beta(state.next(action), -beta, -alpha)
        if score > alpha:
            alpha = score

        # 현재 노드의 베스트 스코어가 부모 노드보다 크면 탐색 종료
        if alpha >= beta:
            return alpha

    # 합법적인 수의 강태 가치의 최대값을 반환
    return alpha


# 알파베타법을 활용한 생동 선택
def alpha_beta_action(state):
    # 합법적인 수의 상태 가치 계산
    best_action = 0
    alpha = -float('inf')
    for action in state.legal_actions():
        score = -alpha_beta(state.next(action), -float('inf'), -alpha)
        if score > alpha:
            best_action = action
            alpha = score

    # 합법적인 수의 상태 가치의 최대값을 갖는 행동 반환
    return best_action


# 플레이아웃
def playout(state):
    # 패배 시, 상태 가치 -1
    if state.is_lose():
        return -1

    # 무승부 시, 상태 가치 0
    if state.is_draw():
        return 0

    # 다음 상태의 상태 가치
    return -playout(state.next(random_action(state)))


# 최대값의 인덱스 반환
def argmax(collection):
    return collection.index(max(collection))


# 몬테카를로 트리 탐색을 활용한 행동 선택
def mcts_action(state):
    # 몬테카를로 트리 탐색 노드
    class node:
        # 초기화
        def __init__(self, state):
            self.state = state  # 상태
            self.w = 0  # 가치 누계
            self.n = 0  # 시행 횟수
            self.child_nodes = None  # 자녀 노드군

        # 평가
        def evaluate(self):
            # 게임 종료 시
            if self.state.is_done():
                # 승패 결과로 가치 얻기
                value = -1 if self.state.is_lose() else 0  # 패배 시 -1, 무승부 시 0

                # 가치 누계와 시행 횟수 갱신
                self.w += value
                self.n += 1
                return value

            # 자녀 노드가 존재하지 않는 경우
            if not self.child_nodes:
                # 플레이아웃으로 가치 얻기
                value = playout(self.state)

                # 가치 누계와 시행 횟수 갱신
                self.w += value
                self.n += 1

                # 자녀 노드 전개
                if self.n == 10:
                    self.expand()
                return value

            # 자녀 노드가 존재하는 경우
            else:
                # UCB1이 가장 큰 자녀 노드를 평가해 가치 얻기
                value = -self.next_child_node().evaluate()

                # 보상 누계와 시행 횟수 갱신
                self.w += value
                self.n += 1
                return value

        # 자녀 노드 전개
        def expand(self):
            legal_actions = self.state.legal_actions()
            self.child_nodes = []
            for action in legal_actions:
                self.child_nodes.append(node(self.state.next(action)))

        # UCB1가 가장 큰 자녀 노드 얻기
        def next_child_node(self):
            # 시행 횟수 n이 0인 자녀 노드를 반환
            for child_node in self.child_nodes:
                if child_node.n == 0:
                    return child_node

            # UCB1 계산
            t = 0
            for c in self.child_nodes:
                t += c.n
            ucb1_values = []
            for child_node in self.child_nodes:
                ucb1_values.append(-child_node.w / child_node.n + 2 * (2 * math.log(t) / child_node.n) ** 0.5)

            # UCB1가 가장 큰 자녀 노드를 반환
            return self.child_nodes[argmax(ucb1_values)]

    # 루트 노드 생성
    root_node = node(state)
    root_node.expand()

    # 루트 노드를 100회 평가
    for _ in range(100):
        root_node.evaluate()

    # 시행 횟수 최대값을 갖는 행동 반환
    legal_actions = state.legal_actions()
    n_list = []
    for c in root_node.child_nodes:
        n_list.append(c.n)
    return legal_actions[argmax(n_list)]


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
