import cv2
import numpy as np
import dlib
from math import hypot

#웹캠
cap = cv2.VideoCapture(0)
font = cv2.FONT_HERSHEY_COMPLEX_SMALL
#전면부 얼굴 인식
detector = dlib.get_frontal_face_detector()
#얼굴의 각 특징을 예측하는 모델
predictor = dlib.shape_predictor("C:/Users/user/py38_tensorflow/shape_predictor_68_face_landmarks.dat")

def get_blinking_ratio(eye_points, facial_landmarks):
    # 36지점과 39지점을 선으로 연결
    left_point = (facial_landmarks.part(eye_points[0]).x, facial_landmarks.part(eye_points[0]).y)
    right_point = (facial_landmarks.part(eye_points[3]).x, facial_landmarks.part(eye_points[3]).y)
    #선 그리기
    hor_line = cv2.line(frame, left_point, right_point, (0, 255, 0), 2)

    # 눈 깜박임 인식을 위한 눈 중앙부 세로선 긋기
    center_top = midpoint(facial_landmarks.part(eye_points[1]), facial_landmarks.part(eye_points[2]))
    center_bottom = midpoint(facial_landmarks.part(eye_points[5]), (facial_landmarks.part(eye_points[4])))
    # 선 그리기
    ver_line = cv2.line(frame, center_top, center_bottom, (0, 255, 0), 2)

    # 가로선의 길이
    hor_line_length = hypot((left_point[0] - right_point[0]), (left_point[1] - right_point[1]))
    # 세로선의 길이
    ver_line_length = hypot((center_top[0] - center_bottom[0]), (center_top[1] - center_bottom[1]))
    # 단순히 길이가 짧아지는 것으로 눈깜박임으로 판단하면 안된다. 화면에서 얼굴이 멀어지는 경우 선의 길이가
    # 짧아지기 떄문에 가로선과 세로선의 비율을 이용해서 눈 깜박임을 인식하도록 한다.
    ratio = hor_line_length / ver_line_length
    return ratio

def get_side_face_ratio(face_points, facial_landmarks):
    out_face_point = (facial_landmarks.part(face_points[0]).x, facial_landmarks.part(face_points[0]).y)
    inner_face_point = (facial_landmarks.part(face_points[1]).x, facial_landmarks.part(face_points[1]).y)
    hor_line_length = hypot((out_face_point[0] - inner_face_point[0]), (out_face_point[1] - inner_face_point[1]))

    hor_line = cv2.line(frame, out_face_point, inner_face_point, (0, 255, 0), 2)

    return hor_line_length

def get_updown_face_ratio(face_points, facial_landmarks):
    u_face_point = (facial_landmarks.part(face_points[0]).x, facial_landmarks.part(face_points[0]).y)
    d_face_point = (facial_landmarks.part(face_points[1]).x, facial_landmarks.part(face_points[1]).y)
    ver_line_length = hypot((u_face_point[0] - d_face_point[0]), (u_face_point[1] - d_face_point[1]))

    ver_line = cv2.line(frame, u_face_point, d_face_point, (0, 255, 0), 2)

    return ver_line_length

#두 점의 중점 구하는 함수
def midpoint(p1, p2):
    return int((p1.x + p2.x) / 2), int((p1.y + p2.y) / 2)


'''
#화면 8방향으로 점찍기
#8방향 별로 얼굴 각도 비율, 눈의 흰자와 검은자 비율 계산
#각각 각도 비율 min, max구하기
'''
standard_side_face_ratio = []
standard_ud_face_ratio = []
standard_eye_ratio = []

total_cheat = 0
total_blink = 0

print("초기값 셋팅입니다.")
i = 0
while i < 8:
    print("모니터의 8방향을 보고 스페이스바를 누른 후 엔터를 입력해 주세요")
    if input() == ' ':
        _, frame = cap.read()
        # -----얼굴의 grayscale
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        # 얼굴부위를 사각형으로 인식
        faces = detector(gray)

        if len(faces) == 0:
            print("얼굴을 웹캠에 위치시켜 주세요")
            continue
        for face in faces:
            landmarks = predictor(gray, face)
            left_eye_ratio = get_blinking_ratio([36, 37, 38, 39, 40, 41], landmarks)
            right_eye_ratio = get_blinking_ratio([42, 43, 44, 45, 46, 47], landmarks)

            left_face_length = get_side_face_ratio([1, 29], landmarks)
            right_face_length = get_side_face_ratio([15, 29], landmarks)

            up_face_length = get_updown_face_ratio([57, 8], landmarks)
            down_face_length = get_updown_face_ratio([28, 30], landmarks)

            side_face_ratio = (left_face_length / right_face_length)
            standard_side_face_ratio.append(side_face_ratio)
            ud_face_ratio = (up_face_length / down_face_length)
            standard_ud_face_ratio.append(ud_face_ratio)

            # 눈동자 인식부분
            left_eye_region = np.array([(landmarks.part(36).x, landmarks.part(36).y),
                                        (landmarks.part(37).x, landmarks.part(37).y),
                                        (landmarks.part(38).x, landmarks.part(38).y),
                                        (landmarks.part(39).x, landmarks.part(39).y),
                                        (landmarks.part(40).x, landmarks.part(40).y),
                                        (landmarks.part(41).x, landmarks.part(41).y)], np.int32)

            right_eye_region = np.array([(landmarks.part(42).x, landmarks.part(42).y),
                                        (landmarks.part(43).x, landmarks.part(43).y),
                                        (landmarks.part(44).x, landmarks.part(44).y),
                                        (landmarks.part(45).x, landmarks.part(45).y),
                                        (landmarks.part(46).x, landmarks.part(46).y),
                                        (landmarks.part(47).x, landmarks.part(47).y)], np.int32)

            # 흰자와 검은자만 있는 눈 부위
            cv2.polylines(frame, [left_eye_region], True, (0, 0, 255), 1)
            cv2.polylines(frame, [right_eye_region], True, (0, 0, 255), 1)
            height, width, _ = frame.shape
            mask_left = np.zeros((height, width), np.uint8)
            mask_right = np.zeros((height, width), np.uint8)
            cv2.polylines(mask_left, [left_eye_region], True, 255, 1)
            cv2.fillPoly(mask_left, [left_eye_region], 255)


            cv2.polylines(mask_right, [right_eye_region], True, 255, 1)
            cv2.fillPoly(mask_right, [right_eye_region], 255)
            left_eye = cv2.bitwise_and(gray, gray, mask=mask_left)
            right_eye = cv2.bitwise_and(gray, gray, mask=mask_right)

            min_x_for_left = np.min(left_eye_region[:, 0])
            max_x_for_left = np.max(left_eye_region[:, 0])
            min_y_for_left = np.min(left_eye_region[:, 1])
            max_y_for_left = np.max(left_eye_region[:, 1])

            min_x_for_right = np.min(right_eye_region[:, 0])
            max_x_for_right = np.max(right_eye_region[:, 0])
            min_y_for_right = np.min(right_eye_region[:, 1])
            max_y_for_right = np.max(right_eye_region[:, 1])

            gray_eye_left = left_eye[min_y_for_left: max_y_for_left, min_x_for_left: max_x_for_left]
            gray_eye_right = right_eye[min_y_for_right: max_y_for_right, min_x_for_right: max_x_for_right]

            _, left_threshold_eye = cv2.threshold(gray_eye_left, 70, 255, cv2.THRESH_BINARY)
            _, right_threshold_eye = cv2.threshold(gray_eye_right, 70, 255, cv2.THRESH_BINARY)

            leye = cv2.resize(gray_eye_left, None, fx=5, fy=5)
            reye = cv2.resize(gray_eye_right, None, fx=5, fy=5)

            left_threshold_eye = cv2.resize(left_threshold_eye, None, fx=5, fy=5)
            right_threshold_eye = cv2.resize(right_threshold_eye, None, fx=5, fy=5)

            white_l = cv2.countNonZero(left_threshold_eye)
            white_r = cv2.countNonZero(right_threshold_eye)
            standard_eye_ratio.append((white_l + white_r) / 2)
        i = i + 1

standard_eye_ratio = np.array(standard_eye_ratio)
standard_side_face_ratio = np.array(standard_side_face_ratio)
standard_ud_face_ratio = np.array(standard_ud_face_ratio)

while True:
    _, frame = cap.read()
    #-----얼굴의 grayscale
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    #얼굴부위를 사각형으로 인식
    faces = detector(gray)
    #---------------------
    #얼굴이 웹캠에 없다면 컨닝으로 간주
    if len(faces) == 0:
        cv2.putText(frame, "cheating", (50, 150), font, 3, (255, 0, 0))

    for face in faces:
        x, y = face.left(), face.top()
        x1, y1 = face.right(), face.bottom()
        # 얼굴 좌표로 사각형출력
        cv2.rectangle(frame, (x, y), (x1, y1), (0, 255, 0), 2)
        #shape dectector로 얼굴의 landmark 포인트들을 예측
        landmarks = predictor(gray, face)

        #왼쪽 눈과 오른쪽 눈 각각 눈을 감는 것을 인식
        left_eye_ratio = get_blinking_ratio([36, 37, 38, 39, 40, 41], landmarks)
        right_eye_ratio = get_blinking_ratio([42, 43, 44, 45, 46, 47], landmarks)
        #print(left_eye_ratio)

        left_face_length = get_side_face_ratio([1, 29], landmarks)
        right_face_length = get_side_face_ratio([15, 29], landmarks)

        up_face_length = get_updown_face_ratio([57, 8], landmarks)
        down_face_length = get_updown_face_ratio([28, 30], landmarks)

        #정면을 바라볼 시 1, 좌측은 6, 우측은 0
        side_face_ratio = (left_face_length / right_face_length)
        ud_face_ratio = (up_face_length / down_face_length)

        #print(side_face_ratio)
        #print(ud_face_ratio)

        #얼굴의 특징점 화면에 출력

        #if 각각 비율의 min, max사이를 벗어나면 컨닝

        for i in range(0, 68, 1):
            cv2.line(frame, (landmarks.part(i).x, landmarks.part(i).y), (landmarks.part(i).x, landmarks.part(i).y),(255, 0, 0), 5)


        #두 눈을 모두 감은 경우 깜박임으로 인식
        if left_eye_ratio > 5.6 and right_eye_ratio > 5.6:
            #눈을 깜박일 때
            total_blink = total_blink + 1
            cv2.putText(frame, "blinking", (50,150), font, 3, (255, 0, 0))

        #눈동자 인식부분
        left_eye_region = np.array([(landmarks.part(36).x, landmarks.part(36).y),
                                    (landmarks.part(37).x, landmarks.part(37).y),
                                    (landmarks.part(38).x, landmarks.part(38).y),
                                    (landmarks.part(39).x, landmarks.part(39).y),
                                    (landmarks.part(40).x, landmarks.part(40).y),
                                    (landmarks.part(41).x, landmarks.part(41).y)], np.int32)

        right_eye_region = np.array([(landmarks.part(42).x, landmarks.part(42).y),
                                     (landmarks.part(43).x, landmarks.part(43).y),
                                     (landmarks.part(44).x, landmarks.part(44).y),
                                     (landmarks.part(45).x, landmarks.part(45).y),
                                     (landmarks.part(46).x, landmarks.part(46).y),
                                     (landmarks.part(47).x, landmarks.part(47).y)], np.int32)

        #흰자와 검은자만 있는 눈 부위
        cv2.polylines(frame, [left_eye_region], True, (0, 0, 255), 1)
        height_l, width_l, _ = frame.shape

        cv2.polylines(frame, [right_eye_region], True, (0, 0, 255), 1)
        height_r, width_r, _ = frame.shape

        #mask_l = np.zeros((height_l, width_l), np.uint8)
        #mask_r = np.zeros((height_r, width_r), np.uint8)

        #cv2.polylines(mask_l, [left_eye_region], True, 255, 1)
        #cv2.fillPoly(mask_l, [left_eye_region], 255)
        #left_eye = cv2.bitwise_and(gray, gray, mask=mask_l)

        #cv2.polylines(mask_r, [right_eye_region], True, 255, 1)
        #cv2.fillPoly(mask_r, [right_eye_region], 255)
        #right_eye = cv2.bitwise_and(gray, gray, mask=mask_r)

        min_x_for_left = np.min(left_eye_region[:, 0])
        max_x_for_left = np.max(left_eye_region[:, 0])
        min_y_for_left = np.min(left_eye_region[:, 1])
        max_y_for_left = np.max(left_eye_region[:, 1])

        min_x_for_right = np.min(right_eye_region[:, 0])
        max_x_for_right = np.max(right_eye_region[:, 0])
        min_y_for_right = np.min(right_eye_region[:, 1])
        max_y_for_right = np.max(right_eye_region[:, 1])

        #흰자와 검은자만 있는 눈 부위 사각형으로
        #eye = frame[min_y : max_y, min_x : max_x]
        left_gray_eye = left_eye[min_y_for_left : max_y_for_left, min_x_for_left : max_x_for_left]
        right_gray_eye = right_eye[min_y_for_right : max_y_for_right, min_x_for_right : max_x_for_right]
        #그레이 스케일 및 이진화
        _, left_threshold_eye = cv2.threshold(left_gray_eye, 4, 255, cv2.THRESH_BINARY)
        _, right_threshold_eye = cv2.threshold(right_gray_eye, 4, 255, cv2.THRESH_BINARY)

        #리사이즈 및 출력
        #eye = cv2.resize(eye, None, fx=5, fy=5)
        left_eye = cv2.resize(left_gray_eye, None, fx=5, fy=5)
        right_eye = cv2.resize(right_gray_eye, None, fx=5, fy=5)

        left_threshold_eye = cv2.resize(left_threshold_eye, None, fx=5, fy=5)
        right_threshold_eye = cv2.resize(right_threshold_eye, None, fx=5, fy=5)

        left_pupil = cv2.HoughCircles(left_threshold_eye, cv2.HOUGH_GRADIENT, 1, 200, param1=50, param2=5, minRadius=20, maxRadius=25)
        if left_pupil is not None:
            left_pupil = np.uint16(left_pupil)
        else:
            continue
        right_pupil = cv2.HoughCircles(right_threshold_eye, cv2.HOUGH_GRADIENT, 1, 200, param1=50, param2=5, minRadius=20, maxRadius=25)
        if right_pupil is not None:
            right_pupil = np.uint16(right_pupil)
        else:
            continue

        for i in left_pupil[0]:
            cv2.circle(left_eye, (i[0], i[1]), i[2], (255, 0, 0), 1)

        for i in left_pupil[0]:
            cv2.circle(right_eye, (i[0], i[1]), i[2], (255, 0, 0), 1)

        cv2.imshow("left_Eye", left_eye)
        cv2.imshow("right_Eye", right_eye)

        cv2.imshow("left_Threshold", left_threshold_eye)
        cv2.imshow("right_Threshold", right_threshold_eye)

        #흰 픽셀의 수
        white_l = cv2.countNonZero(left_threshold_eye)
        white_r = cv2.countNonZero(right_threshold_eye)
        white = (white_r + white_l) / 2
        #print(white)
        if (left_eye_ratio <= 5.6 and right_eye_ratio <= 5.6) and (standard_ud_face_ratio.max() < ud_face_ratio or standard_ud_face_ratio.min() > ud_face_ratio):
            total_cheat = total_cheat + 1
            cv2.putText(frame, "cheating", (50, 150), font, 3, (255, 0, 0))
        if standard_side_face_ratio.max() < side_face_ratio or standard_side_face_ratio.min() > side_face_ratio:
            total_cheat = total_cheat + 1
            cv2.putText(frame, "cheating", (50, 150), font, 3, (255, 0, 0))
        if standard_eye_ratio.max() < white:
            total_cheat = total_cheat + 1
            cv2.putText(frame, "cheating", (50, 150), font, 3, (255, 0, 0))

    #웹캠 화면 출력
    cv2.imshow("Frame", frame)

    key = cv2.waitKey(1)
    if key == 27:
        break
print(total_cheat)
print(total_blink)
cap.release()
cv2.destroyAllWindows()