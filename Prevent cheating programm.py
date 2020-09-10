import wx
import pyautogui
import keyboard
import mouse
import win32api
import cv2
from threading import *


class ShowCapture(wx.Panel):
    def __init__(self, parent, capture, fps=15):

        #wx.Frame.__init__(self, parent, id, style=wx.CAPTION | wx.STAY_ON_TOP)
        #wx.Panel.__init__(self, -1)
        pyautogui.press('f11')
        #keyboard.block_key('f11')

        wx.Panel.__init__(self, parent)

        self.SetWindowStyle(wx.NO_BORDER | wx.STAY_ON_TOP)
        self.capture = capture
        ret, frame = self.capture.read()

        height, width = frame.shape[:2]
        parent.SetSize((width, height))
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        self.bmp = wx.BitmapFromBuffer(width, height, frame)

        self.timer = wx.Timer(self)
        self.timer.Start(1000./fps)

        self.Bind(wx.EVT_PAINT, self.OnPaint)
        self.Bind(wx.EVT_TIMER, self.NextFrame)
       

    def OnPaint(self, evt):
        dc = wx.BufferedPaintDC(self)
        dc.DrawBitmap(self.bmp, 0, 0)

    def NextFrame(self, event):
        ret, frame = self.capture.read()
        if ret:
            frame = cv2.flip(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB), 1)
            self.bmp.CopyFromBuffer(frame)
            self.Refresh()


capture = cv2.VideoCapture(0)

app = wx.App()
frame = wx.Frame(None)
cap = ShowCapture(frame, capture)
frame.Show()
app.MainLoop()
