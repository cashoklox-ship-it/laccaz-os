#!/usr/bin/python3
import json, os, shlex, shutil, sys
from pathlib import Path
from PySide6.QtCore import QProcess, QTimer
from PySide6.QtWidgets import (QApplication,QMainWindow,QWidget,QVBoxLayout,QHBoxLayout,QLabel,QPushButton,QLineEdit,QComboBox,QPlainTextEdit,QMessageBox,QFileDialog,QGroupBox)
from core import create_project, TEMPLATES
class Hub(QMainWindow):
 def __init__(self):
  super().__init__();self.setWindowTitle('Laccaz OS · Dev Hub');self.resize(1060,740)
  self.current=Path.home();self.proc=None
  w=QWidget();self.setCentralWidget(w);v=QVBoxLayout(w);v.setContentsMargins(32,28,32,28);v.setSpacing(18)
  title=QLabel('LACCAZ <span style="color:#b7ef62">OS</span>');title.setStyleSheet('font-size:30px;font-weight:700');v.addWidget(title)
  v.addWidget(QLabel('DEV HUB / 01     •     Твоё пространство разработки'))
  row=QHBoxLayout();v.addLayout(row)
  for label,fn in [('Открыть проект',self.choose),('Редактор',lambda:self.launch('kate',str(self.current))),('Терминал',lambda:self.launch('konsole','--workdir',str(self.current))),('Файлы',lambda:self.launch('dolphin',str(self.current)))]:
   b=QPushButton(label);b.clicked.connect(fn);row.addWidget(b)
  self.location=QLabel();v.addWidget(self.location)
  box=QGroupBox('НОВЫЙ ПРОЕКТ');r=QHBoxLayout(box);v.addWidget(box)
  self.name=QLineEdit();self.name.setPlaceholderText('Название проекта');r.addWidget(self.name)
  self.lang=QComboBox();self.lang.addItems(TEMPLATES);r.addWidget(self.lang)
  b=QPushButton('Создать');b.clicked.connect(self.create);r.addWidget(b)
  row=QHBoxLayout();v.addLayout(row)
  for label,cmd in [('Python venv',['python3','-m','venv','.venv']),('Git init',['git','init']),('Git status',['git','status','--short','--branch']),('Docker',['docker','ps']),('Инструменты',['laccaz-doctor'])]:
   b=QPushButton(label);b.clicked.connect(lambda checked=False,c=cmd:self.run(c));row.addWidget(b)
  row=QHBoxLayout();v.addLayout(row);self.command=QLineEdit();self.command.setPlaceholderText('Команда, например: python3 main.py (без shell-конвейеров)');self.command.returnPressed.connect(self.custom);row.addWidget(self.command)
  b=QPushButton('Запустить');b.clicked.connect(self.custom);row.addWidget(b)
  b=QPushButton('Остановить');b.clicked.connect(self.stop);row.addWidget(b)
  self.output=QPlainTextEdit();self.output.setReadOnly(True);self.output.setMaximumBlockCount(5000);v.addWidget(self.output)
  v.addWidget(QLabel('Debian 13 • KDE Plasma • Laccaz OS 0.1 Developer Preview'))
  self.update_path()
 def update_path(self): self.location.setText('ПРОЕКТ  /  '+str(self.current))
 def choose(self):
  d=QFileDialog.getExistingDirectory(self,'Открыть проект',str(Path.home()/'Projects'))
  if d:self.current=Path(d);self.update_path()
 def create(self):
  try:
   self.current=create_project(Path.home()/'Projects',self.name.text().strip(),self.lang.currentText());self.update_path();self.output.appendPlainText('Создан: '+str(self.current))
  except Exception as e: QMessageBox.warning(self,'Проект',str(e))
 def launch(self,program,*args):
  if not QProcess.startDetached(program,list(args)): QMessageBox.warning(self,'Запуск','Не удалось открыть '+program)
 def custom(self):
  try:cmd=shlex.split(self.command.text())
  except ValueError as e:QMessageBox.warning(self,'Команда',str(e));return
  if cmd:self.run(cmd)
 def run(self,cmd):
  if self.proc is not None: QMessageBox.information(self,'Процесс','Сначала дождись завершения или нажми Остановить.');return
  self.output.appendPlainText('\n$ '+shlex.join(cmd));p=QProcess(self);self.proc=p;p.setWorkingDirectory(str(self.current));p.setProcessChannelMode(QProcess.MergedChannels)
  p.readyReadStandardOutput.connect(lambda:self.output.appendPlainText(bytes(p.readAllStandardOutput()).decode(errors='replace').rstrip()))
  p.finished.connect(lambda code,status:self.done(p,code));p.errorOccurred.connect(lambda error:self.failed(p,error));p.start(cmd[0],cmd[1:])
 def failed(self,p,error):
  self.output.appendPlainText(p.errorString())
  if error==QProcess.FailedToStart:self.proc=None;p.deleteLater()
 def done(self,p,code):
  self.output.appendPlainText('Код завершения: '+str(code));self.proc=None;p.deleteLater()
 def stop(self):
  if self.proc:
   p=self.proc;p.terminate();QTimer.singleShot(2000,lambda:p.kill() if self.proc is p else None)
 def closeEvent(self,event):
  if self.proc:
   QMessageBox.information(self,'Процесс','Останови команду перед закрытием.');event.ignore()
  else:event.accept()
if __name__=='__main__':
 app=QApplication(sys.argv);app.setStyle('Fusion');app.setStyleSheet('QWidget{background:#101214;color:#e7e9e5;font-size:14px} QGroupBox{border:1px solid #32372e;border-radius:12px;margin-top:12px;padding:18px} QPushButton{background:#232923;border:1px solid #394432;border-radius:8px;padding:12px} QPushButton:hover{background:#394a2b;color:#c8ff8a} QLineEdit,QComboBox,QPlainTextEdit{background:#181c19;border:1px solid #353c32;border-radius:7px;padding:10px} QPlainTextEdit{font-family:monospace}')
 h=Hub();h.show();sys.exit(app.exec())
