# ====================
# 신규 파라미터 평가 파트
# ====================

# 패키지 임포트
from game import State
from pv_mcts import pv_mcts_action
from tensorflow.keras.models import load_model
from tensorflow.keras import backend as K
from pathlib import Path
from shutil import copy
import numpy as np

# 파라미터 준비
EN_GAME_COUNT = 10  # 평가 1회 당 게임 수(오리지널: 400)
EN_TEMPERATURE = 1.0  # 볼츠만 분포 온도


# 선 수 플레이어의 포인트
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

        # 다음 상태 얻기
        state = state.next(action)

    # 선 수 플레이어의 포인트 반환
    return first_player_point(state)


# 베스트 플레이어 교대
def update_best_player():
    copy('./model/latest.h5', './model/best.h5')
    print('Change BestPlayer')


# 네트워크 평가
def evaluate_network():
    # 최신 플레이어 모델 로드
    model0 = load_model('./model/latest.h5')

    # 베스트 플레이어 모델 로드
    model1 = load_model('./model/best.h5')

    # PV MCTS를 활용해 행동 선택을 수행하는 함수 생성
    next_action0 = pv_mcts_action(model0, EN_TEMPERATURE)
    next_action1 = pv_mcts_action(model1, EN_TEMPERATURE)
    next_actions = (next_action0, next_action1)

    # 여러 차례 대전을 반복
    total_point = 0
    for i in range(EN_GAME_COUNT):
        # 1 게임 실행
        if i % 2 == 0:
            total_point += play(next_actions)
        else:
            total_point += 1 - play(list(reversed(next_actions)))

        # 출력
        print('\rEvaluate {}/{}'.format(i + 1, EN_GAME_COUNT), end='')
    print('')

    # 평균 포인트 계산
    average_point = total_point / EN_GAME_COUNT
    print('AveragePoint', average_point)

    # 모델 파기
    K.clear_session()
    del model0
    del model1

    # 베스트 플레이어 교대
    if average_point > 0.5:
        update_best_player()
        return True
    else:
        return False


# 동작 확인
if __name__ == '__main__':
    evaluate_network()
