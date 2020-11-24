import wx
import pyautogui
import keyboard
import win32api
import win32gui
import win32con
import os
import cv2
import sys
import winreg
import numpy as np
import dlib
import time
from math import hypot
import webbrowser as wb
import module.killProcess as kp

def get_blinking_ratio(eye_points, facial_landmarks):
    global frame

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
    global frame
    out_face_point = (facial_landmarks.part(face_points[0]).x, facial_landmarks.part(face_points[0]).y)
    inner_face_point = (facial_landmarks.part(face_points[1]).x, facial_landmarks.part(face_points[1]).y)
    hor_line_length = hypot((out_face_point[0] - inner_face_point[0]), (out_face_point[1] - inner_face_point[1]))

    hor_line = cv2.line(frame, out_face_point, inner_face_point, (0, 255, 0), 2)

    return hor_line_length

def get_updown_face_ratio(face_points, facial_landmarks):
    global frame
    u_face_point = (facial_landmarks.part(face_points[0]).x, facial_landmarks.part(face_points[0]).y)
    d_face_point = (facial_landmarks.part(face_points[1]).x, facial_landmarks.part(face_points[1]).y)
    ver_line_length = hypot((u_face_point[0] - d_face_point[0]), (u_face_point[1] - d_face_point[1]))

    ver_line = cv2.line(frame, u_face_point, d_face_point, (0, 255, 0), 2)

    return ver_line_length

#두 점의 중점 구하는 함수
def midpoint(p1, p2):
    return int((p1.x + p2.x) / 2), int((p1.y + p2.y) / 2)

class MyFrame(wx.MiniFrame):
    def __init__(self, parent, id, title):
        screenWidth, screenHeight = pyautogui.size()
        # Frame 생성
        wx.MiniFrame.__init__(self, parent, id, title, size=(300, 170), pos=(screenWidth - 300, screenHeight - 170),
                              style=wx.CAPTION | wx.STAY_ON_TOP)
        # panel 생성
        panel = wx.Panel(self, -1)

        # text 추가
        wx.StaticText(panel, label="웹캠이 녹화중입니다.",
                      pos=(70, 30), style=wx.ALIGN_CENTER)

        # 버튼 추가
        self.btnEnd = wx.Button(panel, wx.ID_ANY, pos=(95, 70), label='종료')
        # 버튼 이벤트 추가
        self.Bind(wx.EVT_BUTTON, self.actEnd, self.btnEnd)

    def actEnd(self, evt):
        # 키해제
        keyboard.unhook_all()

        # 창전환
        pyautogui.keyDown('Alt')
        pyautogui.press('Tab')
        pyautogui.keyUp('Alt')

        # 전체화면 해제
        pyautogui.press('f11')

        # 작업표시줄 표시
        taskBar = win32gui.FindWindow("Shell_TrayWnd", None)
        win32gui.ShowWindow(taskBar, win32con.SW_SHOW)

        # 작업관리자 비활성화 해제
        key = winreg.HKEY_CURRENT_USER
        subkey = r"Software\Microsoft\Windows\CurrentVersion\Policies\System"
        registry = winreg.CreateKeyEx(key, subkey, 0, winreg.KEY_ALL_ACCESS)
        winreg.SetValueEx(registry, "DisableTaskmgr", 0, winreg.REG_DWORD, 0)

        f = open(os.path.expanduser("~/Desktop/test_result.txt"), 'w+t')
        f.write(repr(total_cheat / 15))
        f.close()

        capture.release()
        videoWriter.release()
        cv2.destroyAllWindows()

        self.Destroy()
        sys.exit()


class ShowCapture(wx.Panel):
    def __init__(self, parent, capture, fps=15.0):
        wx.Panel.__init__(self, parent)

        self.capture = capture
        ret, frame = self.capture.read()

        height, width = frame.shape[:2]
        parent.SetSize((width, height))
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        self.bmp = wx.BitmapFromBuffer(width, height, frame)

        self.timer = wx.Timer(self)
        self.timer.Start(1000. / fps)

        self.Bind(wx.EVT_PAINT, self.OnPaint)
        self.Bind(wx.EVT_TIMER, self.NextFrame)

    def OnPaint(self, evt):
        dc = wx.BufferedPaintDC(self)
        dc.DrawBitmap(self.bmp, 0, 0)

    def NextFrame(self, evt):
        global standard_side_face_ratio
        global standard_ud_face_ratio
        global standard_eye_ratio
        global total_cheat
        global total_blink
        global frame

        if (len(standard_eye_ratio) > 8):
            _, frame = capture.read()
            # -----얼굴의 grayscale
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            # 얼굴부위를 사각형으로 인식
            faces = detector(gray)
            # ---------------------
            # 얼굴이 웹캠에 없다면 컨닝으로 간주
            if len(faces) == 0:
                total_cheat = total_cheat + 1

            for face in faces:
                x, y = face.left(), face.top()
                x1, y1 = face.right(), face.bottom()
                # 얼굴 좌표로 사각형출력
                landmarks = predictor(gray, face)

                # 왼쪽 눈과 오른쪽 눈 각각 눈을 감는 것을 인식
                left_eye_ratio = get_blinking_ratio([36, 37, 38, 39, 40, 41], landmarks)
                right_eye_ratio = get_blinking_ratio([42, 43, 44, 45, 46, 47], landmarks)

                left_face_length = get_side_face_ratio([1, 29], landmarks)
                right_face_length = get_side_face_ratio([15, 29], landmarks)

                up_face_length = get_updown_face_ratio([57, 8], landmarks)
                down_face_length = get_updown_face_ratio([28, 30], landmarks)

                # 정면을 바라볼 시 1, 좌측은 6, 우측은 0
                side_face_ratio = (left_face_length / right_face_length)
                ud_face_ratio = (up_face_length / down_face_length)

                # 두 눈을 모두 감은 경우 깜박임으로 인식
                if left_eye_ratio > 5.6 and right_eye_ratio > 5.6:
                    # 눈을 깜박일 때
                    total_blink = total_blink + 1

                # 눈동자 인식부분
                left_eye_region = np.array([(landmarks.part(36).x, landmarks.part(36).y),
                                            (landmarks.part(37).x, landmarks.part(37).y),
                                            (landmarks.part(38).x, landmarks.part(38).y),
                                            (landmarks.part(39).x, landmarks.part(39).y),
                                            (landmarks.part(40).x, landmarks.part(40).y),
                                            (landmarks.part(41).x, landmarks.part(41).y)], np.int32)
                # 흰자와 검은자만 있는 눈 부위
                cv2.polylines(frame, [left_eye_region], True, (0, 0, 255), 1)
                height, width, _ = frame.shape
                mask = np.zeros((height, width), np.uint8)
                cv2.polylines(mask, [left_eye_region], True, 255, 1)
                cv2.fillPoly(mask, [left_eye_region], 255)
                left_eye = cv2.bitwise_and(gray, gray, mask=mask)

                min_x = np.min(left_eye_region[:, 0])
                max_x = np.max(left_eye_region[:, 0])
                min_y = np.min(left_eye_region[:, 1])
                max_y = np.max(left_eye_region[:, 1])
                # 흰자와 검은자만 있는 눈 부위 사각형으로
                gray_eye = left_eye[min_y: max_y, min_x: max_x]
                # 그레이 스케일 및 이진화
                _, threshold_eye = cv2.threshold(gray_eye, 70, 255, cv2.THRESH_BINARY)

                # 리사이즈 및 출력
                eye = cv2.resize(gray_eye, None, fx=5, fy=5)
                threshold_eye = cv2.resize(threshold_eye, None, fx=5, fy=5)
                # 흰 픽셀의 수
                white = cv2.countNonZero(threshold_eye)
                # print(white)
                if (left_eye_ratio <= 5.6 and right_eye_ratio <= 5.6) and (
                        standard_ud_face_ratio.max() < ud_face_ratio or standard_ud_face_ratio.min() > ud_face_ratio):
                    total_cheat = total_cheat + 1
                if standard_side_face_ratio.max() < side_face_ratio or standard_side_face_ratio.min() > side_face_ratio:
                    total_cheat = total_cheat + 1
                if standard_eye_ratio.max() < white:
                    total_cheat = total_cheat + 1

        ret, frame = self.capture.read()

        if ret:
            frame = cv2.flip(frame, 1)
            videoWriter.write(frame)
            self.bmp.CopyFromBuffer(frame)
            self.Refresh()


class MyApp(wx.App):
    def OnInit(self):
        settingFrame = SettingFrame(None, -1, 'Setting')
        settingFrame.Show()

        # 다중 모니터 감지 및 검은 화면으로 막기
        num_displays = wx.Display.GetCount()

        for display_num in range(1, num_displays):
            display = wx.Display(display_num)
            geometry = display.GetGeometry()

            frame = wx.Frame(None, -1, "BLOCK", geometry.GetTopLeft(), geometry.GetSize())
            frame.SetBackgroundColour('black')
            frame.SetWindowStyle(wx.STAY_ON_TOP)
            frame.Show()

        # 웹캠 설정
        capFrame = wx.Frame(None)
        cap = ShowCapture(capFrame, capture)

        # 웹사이트 열기
        wb.open("myclass.ssu.ac.kr", 0, True)
        time.sleep(0.8)
        pyautogui.press('f11')

        # 키제한 - 작업관리자 창 따로 해줘야함
        keyboard.block_key('Tab')
        keyboard.block_key('Alt')
        keyboard.block_key('f11')
        keyboard.block_key('win')
        keyboard.block_key('Ctrl')

        wx.InitAllImageHandlers()

        # 마우스 범위 지정
        self.Bind(wx.EVT_UPDATE_UI, self.actClipCursor)

        # 작업표시줄 숨기기
        taskBar = win32gui.FindWindow("Shell_TrayWnd", None)
        win32gui.ShowWindow(taskBar, win32con.SW_HIDE)

        # 작업관리자 비활성화
        key = winreg.HKEY_CURRENT_USER
        subkey = r"Software\Microsoft\Windows\CurrentVersion\Policies\System"
        registry = winreg.CreateKeyEx(key, subkey, 0, winreg.KEY_ALL_ACCESS)
        winreg.SetValueEx(registry, "DisableTaskmgr", 0, winreg.REG_DWORD, 1)
        
        return True

    def actClipCursor(self, evt):
        # 마우스 범위 제어
        # 전역변수로 빼기
        width = win32api.GetSystemMetrics(0)
        height = win32api.GetSystemMetrics(1)
        win32api.ClipCursor((0, 20, width, height))

class SettingFrame(wx.MiniFrame):
    step = 1
    global btnStart
    global btnNext
    global btnFinish
    global monitor

    def __init__(self, parent, id, title):

        wx.MiniFrame.__init__(self, parent, id, title, size=(400, 300), pos=wx.DefaultPosition, style=wx.CAPTION | wx.STAY_ON_TOP)
        self.readyPanel=wx.Panel(self)

        # text 추가
        wx.StaticText(self.readyPanel, label="초기값 설정중입니다.", pos=(120, 8), style=wx.ALIGN_CENTER)
        wx.StaticText(self.readyPanel, label="사용자 모니터에서 점의 위치를 바라봐주세요.", pos=(35, 25), style=wx.ALIGN_CENTER)
        wx.StaticText(self.readyPanel, label="모니터", pos=(165, 115), style=wx.ALIGN_CENTER)

        self.btnStart = wx.Button(self.readyPanel, label = "설정시작", pos=(148, 212), size=(80,30))
        self.btnNext = wx.Button(self.readyPanel, label ="다음", pos=(164, 212), size=(50, 30))
        self.btnNext.Hide()
        self.btnFinish = wx.Button(self.readyPanel, label="설정완료", pos=(148, 212), size=(80, 30))
        self.btnFinish.Hide()
        self.readyPanel.Bind(wx.EVT_PAINT, self.OnPaint)

        # 버튼 이벤트 추가
        self.Bind(wx.EVT_BUTTON, self.actNext, self.btnStart)

        # 버튼 이벤트 추가
        self.Bind(wx.EVT_BUTTON, self.actNext, self.btnNext)

        # 버튼 이벤트 추가
        self.Bind(wx.EVT_BUTTON, self.actFinish, self.btnFinish)

        self.Centre()
        self.Show()


    def OnPaint(self, evt):
        self.monitor = wx.ClientDC(self.readyPanel)
        self.monitor.SetPen(wx.Pen("grey", style=wx.SOLID))
        self.monitor.SetBrush(wx.Brush("grey", wx.TRANSPARENT))
        self.monitor.DrawRectangle(14, 50, 354, 151)

        self.Show(True)

    def actNext(self, evt):
        global capture
        global standard_side_face_ratio
        global standard_ud_face_ratio
        global standard_eye_ratio
        global frame
        global iter_for_standard

        _, frame = capture.read()
        # -----얼굴의 grayscale
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        # 얼굴부위를 사각형으로 인식
        faces = detector(gray)

        if len(faces) == 0:
            print("얼굴을 웹캠에 위치시켜 주세요")
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
            # 흰자와 검은자만 있는 눈 부위
            cv2.polylines(frame, [left_eye_region], True, (0, 0, 255), 1)
            height, width, _ = frame.shape
            mask = np.zeros((height, width), np.uint8)
            cv2.polylines(mask, [left_eye_region], True, 255, 1)
            cv2.fillPoly(mask, [left_eye_region], 255)
            left_eye = cv2.bitwise_and(gray, gray, mask=mask)

            min_x = np.min(left_eye_region[:, 0])
            max_x = np.max(left_eye_region[:, 0])
            min_y = np.min(left_eye_region[:, 1])
            max_y = np.max(left_eye_region[:, 1])
            gray_eye = left_eye[min_y: max_y, min_x: max_x]
            _, threshold_eye = cv2.threshold(gray_eye, 70, 255, cv2.THRESH_BINARY)

            eye = cv2.resize(gray_eye, None, fx=5, fy=5)
            threshold_eye = cv2.resize(threshold_eye, None, fx=5, fy=5)
            white = cv2.countNonZero(threshold_eye)
            standard_eye_ratio.append(white)
            iter_for_standard = iter_for_standard + 1

        if(iter_for_standard == 9):
            standard_eye_ratio = np.array(standard_eye_ratio)
            standard_side_face_ratio = np.array(standard_side_face_ratio)
            standard_ud_face_ratio = np.array(standard_ud_face_ratio)

        self.monitor.Clear()

        self.monitor = wx.ClientDC(self.readyPanel)
        self.monitor.SetPen(wx.Pen("grey", style=wx.SOLID))
        self.monitor.SetBrush(wx.Brush("grey", wx.TRANSPARENT))
        self.monitor.DrawRectangle(14, 50, 354, 151)

        self.monitor.SetPen(wx.Pen("black", style=wx.SOLID))
        self.monitor.SetBrush(wx.Brush("black", wx.SOLID))

        if self.step == 1:
            self.monitor.DrawCircle(20, 56, 5)
            self.btnStart.Hide()
            self.btnNext.Show()
            self.step = 2
        elif self.step == 2:
            self.monitor.DrawCircle(188, 56, 5)
            self.step = 3
        elif self.step == 3:
            self.monitor.DrawCircle(361, 56, 5)
            self.step = 4
        elif self.step == 4:
            self.monitor.DrawCircle(20, 126, 5)
            self.step = 5
        elif self.step == 5:
            self.monitor.DrawCircle(361, 126, 5)
            self.step = 6
        elif self.step == 6:
            self.monitor.DrawCircle(20, 194, 5)
            self.step = 7
        elif self.step == 7:
            self.monitor.DrawCircle(188, 194, 5)
            self.step = 8
        elif self.step == 8:
            self.monitor.DrawCircle(361, 194, 5)
            self.step = 0
        else:
            self.btnNext.Hide()
            self.btnFinish.Show()

    def actFinish(self, evt):
        SettingFrame.Hide(self)
        cheatFrame = MyFrame(None, -1, 'Anti-Fraud Program')
        cheatFrame.Show()

if __name__ == '__main__':
    global capture
    global videoWriter
    global standard_side_face_ratio
    global standard_ud_face_ratio
    global standard_eye_ratio
    global total_cheat
    global total_blink
    global frame
    global iter_for_standard

    iter_for_standard = 0
    # 전면부 얼굴 인식
    detector = dlib.get_frontal_face_detector()
    # 얼굴의 각 특징을 예측하는 모델
    predictor = dlib.shape_predictor("shape_predictor_68_face_landmarks.dat")

    capture = cv2.VideoCapture(0)
    codec = cv2.VideoWriter_fourcc('D', 'I', 'V', 'X')
    videoWriter = cv2.VideoWriter(os.path.expanduser(
        "~/Desktop/TestWebCam.avi"), codec, 15.0, (640, 480))

    #얼굴의 위, 아래 각도와 눈동자의 각도 판단을 위한 리스트

    standard_eye_ratio = []
    standard_side_face_ratio = []
    standard_ud_face_ratio = []

    #전체 cheating, blinking 횟수

    total_cheat = 0
    total_blink = 0

    # 지정 프로그램 종료
    kp.turnOffProgram()

    app = MyApp(0)
    app.MainLoop()