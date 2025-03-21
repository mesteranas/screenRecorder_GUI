import sys
from custome_errors import *
sys.excepthook = my_excepthook
import os
from moviepy.editor import VideoFileClip, AudioFileClip
from PyQt6.QtMultimedia import QMediaCaptureSession,QMediaRecorder,QAudioInput,QMediaFormat
import pyscreenrec
import update
import gui
import guiTools
from settings import *
import PyQt6.QtWidgets as qt
import PyQt6.QtGui as qt1
import PyQt6.QtCore as qt2
language.init_translation()
class ScreenObjects(qt2.QObject):
    finish=qt2.pyqtSignal(bool)
class converting(qt2.QRunnable):
    def __init__(self,path):
        super().__init__()
        self.path=path
        self.objects=ScreenObjects()
    def run(self):
        video_clip = VideoFileClip(self.path + "/video.mp4")
        new_audio_clip = AudioFileClip(self.path + "/audio.m4a")
        video_clip = video_clip.set_audio(new_audio_clip)
        video_clip.write_videofile(self.path + "/screen recorder .mp4", codec='libx264', audio_codec='aac')
        self.objects.finish.emit(True)
class ScreenRecorder(qt2.QRunnable):
    def __init__(self,path):
        super().__init__()
        self.screen=None
        self.path=path
    def run(self):
        self.screen=pyscreenrec.ScreenRecorder()
        self.screen.start_recording(self.path,20)
class main (qt.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(app.name + _("version : ") + str(app.version))
        layout=qt.QVBoxLayout()
        self.screen=None
        self.session=QMediaCaptureSession()
        self.input=QAudioInput()
        self.session.setAudioInput(self.input)
        self.recorder=QMediaRecorder()
        self.session.setRecorder(self.recorder)
        self.format=QMediaFormat()
        self.format.setAudioCodec(self.format.AudioCodec.MP3)
        self.recorder.setMediaFormat(self.format)
        self.record=qt.QPushButton(_("record"))
        self.record.setDefault(True)
        self.record.clicked.connect(self.on_record)
        layout.addWidget(self.record)
        self.stop=qt.QPushButton(_("stop"))
        self.stop.setDefault(True)
        self.stop.setDisabled(True)
        self.stop.clicked.connect(self.on_stop)
        layout.addWidget(self.stop)
        self.setting=qt.QPushButton(_("settings"))
        self.setting.setDefault(True)
        self.setting.clicked.connect(lambda: settings(self).exec())
        layout.addWidget(self.setting)
        w=qt.QWidget()
        w.setLayout(layout)
        self.setCentralWidget(w)

        mb=self.menuBar()
        self.path=None
        select=qt1.QAction(_("select folder"),self)
        mb.addAction(select)
        select.triggered.connect(self.on_select)
        help=mb.addMenu(_("help"))
        helpFile=qt1.QAction(_("help file"),self)
        help.addAction(helpFile)
        helpFile.triggered.connect(lambda:guiTools.HelpFile())
        helpFile.setShortcut("f1")
        cus=help.addMenu(_("contact us"))
        telegram=qt1.QAction("telegram",self)
        cus.addAction(telegram)
        telegram.triggered.connect(lambda:guiTools.OpenLink(self,"https://t.me/mesteranasm"))
        telegramc=qt1.QAction(_("telegram channel"),self)
        cus.addAction(telegramc)
        telegramc.triggered.connect(lambda:guiTools.OpenLink(self,"https://t.me/tprogrammers"))
        githup=qt1.QAction(_("Github"),self)
        cus.addAction(githup)
        githup.triggered.connect(lambda: guiTools.OpenLink(self,"https://Github.com/mesteranas"))
        X=qt1.QAction(_("x"),self)
        cus.addAction(X)
        X.triggered.connect(lambda:guiTools.OpenLink(self,"https://x.com/mesteranasm"))
        email=qt1.QAction(_("email"),self)
        cus.addAction(email)
        email.triggered.connect(lambda: guiTools.sendEmail("anasformohammed@gmail.com","project_type=GUI app={} version={}".format(app.name,app.version),""))
        Github_project=qt1.QAction(_("visite project on Github"),self)
        help.addAction(Github_project)
        Github_project.triggered.connect(lambda:guiTools.OpenLink(self,"https://Github.com/mesteranas/{}".format(settings_handler.appName)))
        Checkupdate=qt1.QAction(_("check for update"),self)
        help.addAction(Checkupdate)
        Checkupdate.triggered.connect(lambda:update.check(self))
        licence=qt1.QAction(_("license"),self)
        help.addAction(licence)
        licence.triggered.connect(lambda: Licence(self))
        donate=qt1.QAction(_("donate"),self)
        help.addAction(donate)
        donate.triggered.connect(lambda:guiTools.OpenLink(self,"https://www.paypal.me/AMohammed231"))
        about=qt1.QAction(_("about"),self)
        help.addAction(about)
        about.triggered.connect(lambda:qt.QMessageBox.information(self,_("about"),_("{} version: {} description: {} developer: {}").format(app.name,str(app.version),app.description,app.creater)))
        self.setMenuBar(mb)
        if settings_handler.get("update","autoCheck")=="True":
            update.check(self,message=False)
    def closeEvent(self, event):
        try:
            os.remove(self.path + "/audio.m4a")
            os.remove(self.path + "/video.mp4")
        except:pass

        if settings_handler.get("g","exitDialog")=="True":
            m=guiTools.ExitApp(self)
            m.exec()
            if m:
                event.ignore()
        else:
            self.close()
    def on_record(self):
        self.recorder.setOutputLocation(qt2.QUrl.fromLocalFile(self.path + "/audio"))
        self.recorder.record()
        self.screen=ScreenRecorder(self.path + "/video.mp4")
        qt2.QThreadPool(self).start(self.screen)
        self.record.setDisabled(True)
        self.stop.setDisabled(False)
    def on_stop(self):
        self.recorder.stop()
        self.screen.screen.stop_recording()
        self.record.setDisabled(False)
        self.stop.setDisabled(True)
        thread=converting(self.path)
        thread.objects.finish.connect(self.on_finish_loading)
        qt2.QThreadPool(self).start(thread)
    def on_select(self):
        file=qt.QFileDialog(self)
        file.setFileMode(file.FileMode.Directory)
        if file.exec()==file.DialogCode.Accepted:
            self.path=file.selectedFiles()[0]
    def on_finish_loading(self,state):
        qt.QMessageBox.information(self,_("done"),_("saved"))
App=qt.QApplication([])
w=main()
w.show()
App.setStyle('fusion')
App.exec()