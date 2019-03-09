# Round 1

### Round 1 知识

一、Django xadmin 的搭建指导
关于 xadmin 的相关知识，网络上已经有很多了，但是每个知识点都是零零散散的，我自己在搭建的过程中也遇到了一些问题，每次都需要重新查找资料，这里做个简单的总结，希望对大家能有帮助。

二、基于 wxPython 的聊天程序
其实这个是在实验楼上看到的课程，跟着做了下来，感觉收获还可以，记录下自己的学习心得，也许以后有的用呢。




### Django xadmin 搭建

#### 安装方式

这里有两种安装方式，pip 安装和源码安装，因为本文主要介绍 xadmin 的安装，所以一些 Django 的基础配置操作，就不再令行说明。
当前 pip 安装的 xadmin 还不支持 django 2.0，所以如果我们使用最新的 django 版本，那么就只能使用源码安装了，我这里也主要介绍该种方法。

#### 下载源码

进入到 xadmin 的 GitHub 主页（https://github.com/sshwsfc/xadmin），切换至 django2 分支，然后下载源码到本地。

#### 安装配置

我这使用的是 Python 3.6 + Django 2.1。
首先创建 Django 项目，不多说，例如我创建的 Django 项目名称为 test_xadmin，再创建名称为 app_xadmin 的 app 应用。在该项目的顶级目录下，即与 manage.py 文件同目录下，创建 extra_apps 目录，并将 xadmin 项目源码解压出的 xadmin 目录拷贝至该目录下。
在 Django 项目的 setting.py 文件中添加如下代码：
```python
import sys
sys.path.insert(0, os.path.join(BASE_DIR, 'extra_apps'))
INSTALL_APP = [
'app_xadmin',
'xadmin',
'crispy_forms',
]
```
再在 url.py 中加入如下代码，注册 xadmin 路由
```python
import xadmin
urlpatterns = [
	url('xadmin/', xadmin.site.urls),
]
```
查看 xadmin 的源码可以看到，xadmin 还是自带了一些数据库表的，所以需要先在数据库中生成这些表，执行代码：
```shell
python manage.py makemigrations
然后执行
python manage.py migrate 
```
接下来安装一些依赖包，
```shell
pip install future six httplib2
```
到这里，xadmin 基本就安装完毕。我们打开页面 x.x.x.x:5000，就能够看到一个功能更加强大的 xadmin 页面了。
>如果出现添加 user widget 报错的情况，需要将 xadmin/views/dashborad.py 中的 render() 函数添加一个参数 renderer=None 即可。如下所示：
def render(self, name, value, attrs=None, renderer=None):
        ...


#### 功能完善

##### 配置导入导出功能

xadmin 默认的功能只有导出，并不能支持文件的导入，我们需要下载 django-import-export 依赖包来支持导入导出功能。
```shell
pip install django-import-export
```
在setting.py中添加如下：
```python
INSTALLED_APPS = (
    ...
    'import_export',
)
```
在 app 应用 app_xadmin 的 models.py 文件中添加代码：
```python
from django.db import models

class Article(models.Model):
    title = models.CharField('title', max_length=256)
    content =  models.TextField('content')
    pub_date = models.DateTimeField('pub_time', auto_now_add=True, editable=True)
    update_time = models.DateTimeField('up_time', auto_now=True, null=True)
    
    def __str__(self):
        return self.title
```
同时在该目录下创建 resources.py 文件，添加代码：
```python
from import_export import resources
from .models import Article
class ArticleXResource(resources.ModelResource):
    class Meta:
        model = Article
```
再创建 adminx.py 文件，添加代码：
```python
from xadmin import views
import xadmin
from .models import  Article
from import_export import resources
from .resources import ArticleXResource

@xadmin.sites.register(Article)
class ArticleAdmin(object):
    list_display = ['title', 'content']
    import_export_args = {'import_resource_class': ArticleXResource, 'export_resource_class': ArticleXResource}
    list_export = () # 去掉 Django 默认的导出按钮
```


##### 运行 django 程序

使用 gunicorn 部署 django，安装 gunicorn
```shell
pip install gunicorn
```

首先在 url.py 中加入：
```python
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

...

urlpatterns += staticfiles_urlpatterns()
```
然后，在 manage.py 的同级目录下，运行
```shell
/usr/local/python/bin/gunicorn test_xadmin.wsgi -b 0.0.0.0:8000
```
这样，就在本地的 8000 端口启动了服务
>如果出现默写 css 样式展示的问题，可以执行下 python manage.py collectstatic 命令，来搜集静态文件到 settings.py 中设置的 STATIC_ROOT 文件夹中。

### 基于 wxPython 的聊天程序

#### 入门 Hello World
```python
import wx
app = wx.App(false)
frame = wx.Frame(None, title="Hello World")
frame.Show() #展示
app.MainLoop() #启动事件循环
```


##### 编写 server 端

使用 asynchat 和 asyncore 两个 Python 的异步通信模块
```python
import asynchat
import asyncore

PORT = 6666


class EndSession(Exception):
    pass


class ChatSession(asynchat.async_chat):
    def __init__(self, server, sock):
        asynchat.async_chat.__init__(self, sock)
        self.server = server
        self.set_terminator(b'\n')
        self.data = []
        self.name = None
        self.enter(LoginRoom(server))

    def enter(self, room):
        try:
            cur = self.room
        except AttributeError:
            pass
        else:
            cur.remove(self)
        self.room = room
        room.add(self)

    def collect_incoming_data(self, data):
        self.data.append(data.decode("utf-8"))

    def found_terminator(self):
        line = ''.join(self.data)
        self.data = []
        try:
            self.room.handle(self, line.encode("utf-8"))
        except EndSession:
            self.handle_close()

    def handle_close(self):
        asynchat.async_chat.handle_close(self)
        self.enter(LoginRoom(self.server))


class ChatServer(asyncore.dispatcher):
    def __init__(self, port):
        asyncore.dispatcher.__init__(self)
        self.create_socket()
        self.set_reuse_addr()
        self.bind(('', port))
        self.listen(5)
        self.users = {}
        self.main_room = ChatRoom(self)

    def handle_accept(self):
        comm, addr = self.accept()
        ChatSession(self, comm)


class CommandHandler:
    def unknown(self, session, cmd):
        session.push(('Unknown command {} \n'.format(cmd))).encode("utf-8")

    def handle(self, session, line):
        line = line.decode()
        if not line.strip():
            return
        parts = line.split(' ', 1)
        cmd = parts[0]
        try:
            line = parts[1].strip()
        except IndexError:
            line = ''
        method = getattr(self, 'do_' + cmd, None)
        try:
            method(session, line)
        except TypeError:
            self.unknown(session, cmd)


class Room(CommandHandler):
    def __init__(self, server):
        self.server = server
        self.sessions = []

    def add(self, session):
        self.sessions.append(session)

    def remove(self, session):
        self.sessions.remove(session)

    def broadcast(self, line):
        for session in self.sessions:
            session.push(line)

    def do_logout(self, session, line):
        raise EndSession


class LoginRoom(Room):
    def add(self, session):
        Room.add(self, session)
        session.push(b'Connect Success')

    def do_login(self, session, line):
        name = line.strip()
        if not name:
            session.push(b'UserName Empty')
        elif name in self.server.users:
            session.push(b'UserName Exist')
        else:
            session.name = name
            session.enter(self.server.main_room)


class LogoutRoom(Room):
    def add(self, session):
        try:
            del self.server.users[session.name]
        except KeyError:
            pass


class ChatRoom(Room):
    def add(self, session):
        session.push(b'Login Success')
        self.broadcast((session.name + 'has entered the room.\n').encode("utf-8"))
        self.server.users[session.name] = session
        Room.add(self, session)

    def remove(self, session):
        Room.remove(self, session)
        self.broadcast((session.name + 'has left the room.\n').encode("utf-8"))

    def do_say(self, session, line):
        self.broadcast((session.name + ':' + line + '\n').encode("utf-8"))

    def do_look(self, session, line):
        session.push(b'Online Users:\n')
        for other in self.sessions:
            session.push((other.name + '\n').encode("utf-8"))


if __name__ == '__main__':
    s = ChatServer(PORT)
    try:
        print("chat server run at '0.0.0.0:{0}'".format(PORT))
        asyncore.loop()
    except KeyboardInterrupt:
        print("chat server exit")
```
##### 编写 client 端
使用 telnet 的方式来登陆，所以需要用到 telnetlib 模块
```python
import wx
import telnetlib
from time import sleep
import _thread as thread


class LoginFrame(wx.Frame):
    def __init__(self, parent, id, title, size):
        wx.Frame.__init__(self, parent, id, title)
        self.SetSize(size)
        self.Center()
        self.serverAddressLabel = wx.StaticText(self, label="Server Address", pos=(10, 50), size=(120, 25))
        self.userNameLabel = wx.StaticText(self, label="UserName", pos=(40, 100), size=(120, 25))
        self.serverAddress = wx.TextCtrl(self, pos=(120, 47), size=(150, 25))
        self.userName = wx.TextCtrl(self, pos=(120, 97), size=(150, 25))
        self.loginButton = wx.Button(self, label='Login', pos=(80, 145), size=(130, 30))
        self.loginButton.Bind(wx.EVT_BUTTON, self.login)
        self.Show()

    def login(self, event):
        try:
            serverAddress = self.serverAddress.GetLineText(0).split(':')
            con.open(serverAddress[0], port=int(serverAddress[1]), timeout=10)
            response = con.read_some()
            if response != b'Connect Success':
                self.showDialog('Error', 'Connect Fail!', (200, 100))
                return
            con.write(('login ' + str(self.userName.GetLineText(0)) + '\n').encode("utf-8"))
            response = con.read_some()
            if response == b'UserName Empty':
                self.showDialog('Error', 'UserName Empty!', (200, 100))
            elif response == b'UserName Exist':
                self.showDialog('Error', 'UserNmae Exist!', (200, 100))
            else:
                self.Close()
                ChatFrame(None, 2, title='My Chat Client', size=(500, 400))
        except Exception:
            self.showDialog('Error', 'Connect Fail!', (95, 20))

    def showDialog(self, title, content, size):
        dialog = wx.Dialog(self, title=title, size=size)
        dialog.Center()
        wx.StaticText(dialog, label=content)
        dialog.ShowModal()


class ChatFrame(wx.Frame):
    def __init__(self, parent, id, title, size):
        wx.Frame.__init__(self, parent, id, title)
        self.SetSize(size)
        self.Center()
        self.chatFrame = wx.TextCtrl(self, pos=(5, 5), size=(490, 310), style=wx.TE_MULTILINE | wx.TE_READONLY)
        self.message = wx.TextCtrl(self, pos=(5, 320), size=(300, 25))
        self.sendButton = wx.Button(self, label="Send", pos=(310, 320), size=(58, 25))
        self.usersButton = wx.Button(self, label="Users", pos=(373, 320), size=(58, 25))
        self.closeButton = wx.Button(self, label="Close", pos=(436, 320), size=(58, 25))

        self.sendButton.Bind(wx.EVT_BUTTON, self.send)

        self.usersButton.Bind(wx.EVT_BUTTON, self.lookUsers)

        self.closeButton.Bind(wx.EVT_BUTTON, self.close)
        thread.start_new_thread(self.receive, ())
        self.Show()

    def send(self, event):

        message = str(self.message.GetLineText(0)).strip()
        if message != '':
            con.write(('say ' + message + '\n').encode("utf-8"))
            self.message.Clear()

    def lookUsers(self, event):

        con.write(b'look\n')

    def close(self, event):

        con.write(b'logout\n')
        con.close()
        self.Close()

    def receive(self):

        while True:
            sleep(0.6)
            result = con.read_very_eager()
            if result != '':
                self.chatFrame.AppendText(result)


if __name__ == '__main__':
    app = wx.App()
    con = telnetlib.Telnet()
    LoginFrame(None, -1, title="Login", size=(320, 250))
    app.MainLoop()
```
这样，我们启动 server 端，开始监听。再打开两个 client 端，进行交流

