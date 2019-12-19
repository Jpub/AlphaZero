# ====================
# 베스트 플레이어 평가
# ====================

# 패키지 임포트
from game import State, random_action, alpha_beta_action, mcts_action
from pv_mcts import pv_mcts_action
from tensorflow.keras.models import load_model
from tensorflow.keras import backend as K
from pathlib import Path
import numpy as np

# 파라미터 준비
EP_GAME_COUNT = 10  # 평가 1회당 게임 수


# 선 수를 둔 플레이어의 포인트
def first_player_point(ended_state):
    # 1: 선 수 플레이어 승리, 0: 선 수 플레이어 패배, 0.5: 무승부
    if ended_state.is_lose():
        return 0 if ended_state.is_first_player() else 1
    return 0.5


# 1 게임 실행
def play(next_actions):
    # 상태 생성
    state = State()

    # 게임 종료 시까지 반복
    while True:
        # 게임 종료 시
        if state.is_done():
            break

        # 행동 얻기
        next_action = next_actions[0] if state.is_first_player() else next_actions[1]
        action = next_action(state)

        # 次の状態の取得
        state = state.next(action)

    # 선 수 플레이어의 포인트 반환
    return first_player_point(state)


# 임의의 알고리즘 평가
def evaluate_algorithm_of(label, next_actions):
    # 여러 차례 대전을 반복
    total_point = 0
    for i in range(EP_GAME_COUNT):
        # 1 게임 실행
        if i % 2 == 0:
            total_point += play(next_actions)
        else:
            total_point += 1 - play(list(reversed(next_actions)))

        # 출력
        print('\rEvaluate {}/{}'.format(i + 1, EP_GAME_COUNT), end='')
    print('')

    # 평균 포인트 계산
    average_point = total_point / EP_GAME_COUNT
    print(label, average_point)


# 베스트 플레이어 평가
def evaluate_best_player():
    # 베스트 플레이어 모델 로드
    model = load_model('./model/best.h5')

    # PV MCTS로 행동 선택을 수행하는 함수 생성
    next_pv_mcts_action = pv_mcts_action(model, 0.0)

    # VS 랜덤
    next_actions = (next_pv_mcts_action, random_action)
    evaluate_algorithm_of('VS_Random', next_actions)

    # VS 알파베타법
    next_actions = (next_pv_mcts_action, alpha_beta_action)
    evaluate_algorithm_of('VS_AlphaBeta', next_actions)

    # VS 몬테카를로 트리 탐색
    next_actions = (next_pv_mcts_action, mcts_action)
    evaluate_algorithm_of('VS_MCTS', next_actions)

    # 모델 파기
    K.clear_session()
    del model


# 동작 확인
if __name__ == '__main__':
    evaluate_best_player()
