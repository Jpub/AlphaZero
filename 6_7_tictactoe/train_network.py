# ====================
# 파라미터 갱신 파트
# ====================

# 패키지 임포트
from dual_network import DN_INPUT_SHAPE
from tensorflow.keras.callbacks import LearningRateScheduler, LambdaCallback
from tensorflow.keras.models import load_model
from tensorflow.keras import backend as K
from pathlib import Path
import numpy as np
import pickle

# 파라미터 준비
RN_EPOCHS = 100  # 학습 횟수


# 학습 데이터 로드
def load_data():
    history_path = sorted(Path('./data').glob('*.history'))[-1]
    with history_path.open(mode='rb') as f:
        return pickle.load(f)


# 듀얼 네트워크 학습
def train_network():
    # 학습 데이터 로드
    history = load_data()
    xs, y_policies, y_values = zip(*history)

    # 학습을 위한 입력 데이터 셰이프로 변환
    a, b, c = DN_INPUT_SHAPE
    xs = np.array(xs)
    xs = xs.reshape(len(xs), c, a, b).transpose(0, 2, 3, 1)
    y_policies = np.array(y_policies)
    y_values = np.array(y_values)

    # 베스트 플레이어 모델 로드
    model = load_model('./model/best.h5')

    # 모델 컴파일
    model.compile(loss=['categorical_crossentropy', 'mse'], optimizer='adam')

    # 학습률
    def step_decay(epoch):
        x = 0.001
        if epoch >= 50: x = 0.0005
        if epoch >= 80: x = 0.00025
        return x

    lr_decay = LearningRateScheduler(step_decay)

    # 출력
    print_callback = LambdaCallback(
        on_epoch_begin=lambda epoch, logs:
        print('\rTrain {}/{}'.format(epoch + 1, RN_EPOCHS), end=''))

    # 학습 실행
    model.fit(xs, [y_policies, y_values], batch_size=128, epochs=RN_EPOCHS,
              verbose=0, callbacks=[lr_decay, print_callback])
    print('')

    # 최신 플레이어 모델 저장
    model.save('./model/latest.h5')

    # 모델 파기
    K.clear_session()
    del model


# 동작 확인
if __name__ == '__main__':
    train_network()
