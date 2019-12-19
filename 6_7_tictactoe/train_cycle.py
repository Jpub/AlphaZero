# ====================
# 학습 사이클 실행
# ====================

# 패키지 임포트
from dual_network import dual_network
from self_play import self_play
from train_network import train_network
from evaluate_network import evaluate_network
from evaluate_best_player import evaluate_best_player

# 듀얼 네트워크 생성
dual_network()

for i in range(10):
    print('Train', i, '====================')
    # 셀프 플레이 파트
    self_play()

    # 파라미터 갱신 파트
    train_network()

    # 신규 파라미터 평가 파트
    update_best_player = evaluate_network()

    # 베스트 플레이어 평가
    if update_best_player:
        evaluate_best_player()