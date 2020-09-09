import wx
import pyautogui
import keyboard
import mouse
import win32api
from threading import *

class MyFrame(wx.Frame):
    def __init__(self, parent, id,title):
        #Frame 생성
        wx.Frame.__init__(self, parent,id,title,size=(300,170),pos=wx.DefaultPosition,
            style = wx.CAPTION | wx.STAY_ON_TOP)
        #panel 생성
        panel=wx.Panel(self,-1)


        #text 추가
        wx.StaticText(panel, label="웹캠이 녹화중입니다.", pos=(70, 30), style=wx.ALIGN_CENTER)
        #버튼 추가
        self.btnEnd = wx.Button(panel, wx.ID_ANY, pos=(95, 70), label='종료')
        #버튼 이벤트 추가
        self.Bind(wx.EVT_BUTTON, self.actEnd, self.btnEnd)
        #마우스 범위 제한-버그있음
        self.Bind(wx.EVT_ACTIVATE, self.actCursor)


    def actCursor(self, evt):
        print("y")
        width = win32api.GetSystemMetrics(0)
        height = win32api.GetSystemMetrics(1)
        win32api.ClipCursor((0, 20, width, height))

    def actEnd(self, evt):
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


