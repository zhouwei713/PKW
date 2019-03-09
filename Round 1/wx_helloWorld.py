# coding = utf-8
"""
@author: zhou
@time:2019/3/9 15:09
"""


import wx
app = wx.App(False)
frame = wx.Frame(None, title="Hello World")

frame.Show()  # 展示
app.MainLoop()  # F启动事件循环