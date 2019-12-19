# ====================
# 몬테카를로 트리 탐색 생성
# ====================

# 패키지 임포트
from game import State
from dual_network import DN_INPUT_SHAPE
from math import sqrt
from tensorflow.keras.models import load_model
from pathlib import Path
import numpy as np

# 파라미터 준비
PV_EVALUATE_COUNT = 50  # 추론 1회당 시뮬레이션 횟수(오리지널: 1600회)


# 추론
def predict(model, state):
    # 추론을 위한 입력 데이터 셰이프 변환
    a, b, c = DN_INPUT_SHAPE
    x = np.array([state.pieces, state.enemy_pieces])
    x = x.reshape(c, a, b).transpose(1, 2, 0).reshape(1, a, b, c)

    # 추론
    y = model.predict(x, batch_size=1)

    # 정책 얻기
    policies = y[0][0][list(state.legal_actions())]  # 합법적인 수만
    policies /= sum(policies) if sum(policies) else 1  # 합계 1의 확률분호로 변환

    # 가치 얻기
    value = y[1][0][0]
    return policies, value


# 노드 리스트를 시행 횟수 리스트로 변환
def nodes_to_scores(nodes):
    scores = []
    for c in nodes:
        scores.append(c.n)
    return scores


# 몬테카를로 트리 탐색 스코어 얻기
def pv_mcts_scores(model, state, temperature):
    # 몬테카를로 트리 탐색 노드 정의
    class Node:
        # 노드 초기화
        def __init__(self, state, p):
            self.state = state  # 상태
            self.p = p  # 정책
            self.w = 0  # 가치 누계
            self.n = 0  # 시행 횟수
            self.child_nodes = None  # 子ノード群

        # 국면 가치 누계
        def evaluate(self):
            # 게임 종료 시
            if self.state.is_done():
                # 승패 결과로 가치 얻기
                value = -1 if self.state.is_lose() else 0

                # 누계 가치와 시행 횟수 갱신
                self.w += value
                self.n += 1
                return value

            # 자녀 노드가 존재하지 않는 경우
            if not self.child_nodes:
                # 뉴럴 네트워크 추론을 활용한 정책과 가치 얻기
                policies, value = predict(model, self.state)

                # 누계 가치와 시행 횟수 갱신
                self.w += value
                self.n += 1

                # 자녀 노드 전개
                self.child_nodes = []
                for action, policy in zip(self.state.legal_actions(), policies):
                    self.child_nodes.append(Node(self.state.next(action), policy))
                return value

            # 자녀 노드가 존재하지 않는 경우
            else:
                # 아크 평갓값이 가장 큰 자녀 노드를 평가해 가치 얻기
                value = -self.next_child_node().evaluate()

                # 누계 가치와 시행 횟수 갱신
                self.w += value
                self.n += 1
                return value

        # 아크 평가가 가장 큰 자녀 노드 얻기
        def next_child_node(self):
            # 아크 평가 계산
            C_PUCT = 1.0
            t = sum(nodes_to_scores(self.child_nodes))
            pucb_values = []
            for child_node in self.child_nodes:
                pucb_values.append((-child_node.w / child_node.n if child_node.n else 0.0) +
                                   C_PUCT * child_node.p * sqrt(t) / (1 + child_node.n))

            # 아크 평갓값이 가장 큰 자녀 노드 반환
            return self.child_nodes[np.argmax(pucb_values)]

    # 현재 국면의 노드 생성
    root_node = Node(state, 0)

    # 여러 차례 평가 실행
    for _ in range(PV_EVALUATE_COUNT):
        root_node.evaluate()

    # 합법적인 수의 확률 분포
    scores = nodes_to_scores(root_node.child_nodes)
    if temperature == 0:  # 최대값인 경우에만 1
        action = np.argmax(scores)
        scores = np.zeros(len(scores))
        scores[action] = 1
    else:  # 볼츠만 분포를 기반으로 분산 추가
        scores = boltzman(scores, temperature)
    return scores


# 몬테카를로 트리 탐색을 활용한 행동 선택
def pv_mcts_action(model, temperature=0):
    def pv_mcts_action(state):
        scores = pv_mcts_scores(model, state, temperature)
        return np.random.choice(state.legal_actions(), p=scores)

    return pv_mcts_action


# 볼츠만 분포
def boltzman(xs, temperature):
    xs = [x ** (1 / temperature) for x in xs]
    return [x / sum(xs) for x in xs]


# 동작 확인
if __name__ == '__main__':
    # 모델 로드
    path = sorted(Path('./model').glob('*.h5'))[-1]
    model = load_model(str(path))

    # 상태 생성
    state = State()

    # 몬테카를로 트리 탐색을 활용해 행동을 얻는 함수 생성
    next_action = pv_mcts_action(model, 1.0)

    # 게임 종료 시까지 반복
    while True:
        # 게임 종료 시
        if state.is_done():
            break

        # 행동 얻기
        action = next_action(state)

        # 다음 상태 얻기
        state = state.next(action)

        # 문자열 출력
        print(state)
