import wx
import pyautogui
import keyboard
import mouse
import win32api
import win32gui

class MyFrame(wx.Frame):
    def __init__(self, parent, id,title):
        #Frame 생성
        wx.Frame.__init__(self, parent,id,title,size=(300,170),pos=wx.DefaultPosition,
            style = wx.CAPTION | wx.STAY_ON_TOP)
        #panel 생성
        panel=wx.Panel(self,-1)

        wx.Frame.SetFocus(self)

        #text 추가
        wx.StaticText(panel, label="웹캠이 녹화중입니다.", pos=(70, 30), style=wx.ALIGN_CENTER)
        #버튼 추가
        self.btnEnd = wx.Button(panel, wx.ID_ANY, pos=(95, 70), label='종료')
        #버튼 이벤트 추가
        self.Bind(wx.EVT_BUTTON, self.actEnd, self.btnEnd)

        #마우스 범위 지정
        self.Bind(wx.EVT_UPDATE_UI, self.actClipCursor)

        #창활성화
        ForeWindow = win32gui.GetActiveWindow()
        win32gui.SetForegroundWindow(ForeWindow)

    def actClipCursor(self, evt):
        # 마우스 범위 제어
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

        self.Destroy()

class MyApp(wx.App):
    def OnInit(self):
        #전체화면
        pyautogui.press('f11')

        #키제한 - 작업관리자 창 따로 해줘야함
        keyboard.block_key('Alt')
        keyboard.block_key('f11')

        wx.InitAllImageHandlers()
        self.frame = MyFrame(None,-1,'Anti-Fraud Program')
        self.frame.Show()

        return True

if __name__ == '__main__':
    app=MyApp(0)
    app.MainLoop()


