import wx
import pyautogui
import keyboard
import mouse
import win32api
import win32gui
import win32con
import psutil
import os

class MyFrame(wx.MiniFrame):
    def __init__(self, parent, id,title):
        #Frame 생성
        wx.MiniFrame.__init__(self, parent,id,title,size=(300,170),pos=wx.DefaultPosition,
            style = wx.CAPTION | wx.STAY_ON_TOP )
        #panel 생성
        panel=wx.Panel(self,-1)

        #text 추가
        wx.StaticText(panel, label="웹캠이 녹화중입니다.", pos=(70, 30), style=wx.ALIGN_CENTER)

        #버튼 추가
        self.btnEnd = wx.Button(panel, wx.ID_ANY, pos=(95, 70), label='종료')
        #버튼 이벤트 추가
        self.Bind(wx.EVT_BUTTON, self.actEnd, self.btnEnd)

        #마우스 범위 지정
        self.Bind(wx.EVT_UPDATE_UI, self.actClipCursor)

        #작업표시줄 숨기기
        taskBar = win32gui.FindWindow("Shell_TrayWnd", None)
        win32gui.ShowWindow(taskBar, win32con.SW_HIDE)

        f = open(r"C:\Users\s_0hyeon\Desktop\list.txt", 'rt', encoding='utf-8')
        lines = f.readlines()
        for line in lines:
            programName = line.rstrip('\n')
            for proc in psutil.process_iter():
                try:
                    # 프로세스 이름, PID값 가져오기
                    processName = proc.name()
                    processID = proc.pid

                    if processName == programName:
                        parent_pid = processID  # PID
                        parent = psutil.Process(parent_pid)  # PID 찾기
                        for child in parent.children(recursive=True):  # 자식-부모 종료
                            child.kill()
                        parent.kill()

                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):  # 예외처리
                    pass
        f.close()

    def actClipCursor(self, evt):
        # 마우스 범위 제어
        #전역변수로 빼기
        width = win32api.GetSystemMetrics(0)
        height = win32api.GetSystemMetrics(1)
        win32api.ClipCursor((0, 20, width, height))

    def actEnd(self, evt):
        #키해제
        keyboard.unblock_key

        #창전환
        pyautogui.keyDown('Alt')
        pyautogui.press('Tab')
        pyautogui.keyUp('Alt')

        #전체화면 해제
        pyautogui.press('f11')

        taskBar = win32gui.FindWindow("Shell_TrayWnd", None)
        win32gui.ShowWindow(taskBar, win32con.SW_SHOW)

        self.Destroy()

class MyApp(wx.App):
    def OnInit(self):
        #전체화면
        ExploreWindow = win32gui.GetForegroundWindow()
        exploreClientRect = win32gui.GetClientRect(ExploreWindow)
        height = win32api.GetSystemMetrics(1)
        if exploreClientRect[3] < height:
            pyautogui.press('f11')

        #키제한 - 작업관리자 창 따로 해줘야함
        keyboard.block_key('Tab')
        keyboard.block_key('Alt')
        keyboard.block_key('f11')

        wx.InitAllImageHandlers()
        self.frame = MyFrame(None,-1,'Anti-Fraud Program')
        self.frame.Show()

        return True

if __name__ == '__main__':
    app=MyApp(0)
    app.MainLoop()


