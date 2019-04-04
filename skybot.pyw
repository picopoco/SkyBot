# -*- coding: utf-8 -*-

프로그램정보 = [
    ['프로그램명','mymoneybot-eBEST'],
    ['Version','1.4'],
    ['개발일','2018-02-28'],
    ['2018-06-04','포트폴리오 더블클릭으로 삭제 기능 추가'],
    ['2018-05-23','시장가매도, query->ActiveX 오류수정'],
    ['2018-07-19','국내선물옵션, 해외선물옵션에 필요한 모듈을 XAQuery, XAReals에 추가'],
    ['2018-07-19','검색식에서 종목이 빠지는 경우, 손절 및 익절이 나가지 않는 부분 추가'],
    ['2018-07-20','체결시간과 종목검색에서 종목이 빠지는 시간차가 있는 경우 주문이 나가지 않는 부분추가'],
    ['2018-07-25','종목검색 중지시 계속 검색된 종목이 들어오는 문제 수정'],
    ['2018-08-01','종목검색, Chartindex에서 식별자를 사용하는 방법 통일'],
    ['2018-08-01','한번에 수량이 다 체결된 경우 포트에 반영되지 않는 것을 수정'],
    ['2018-08-07','조건검색시 다른 조건검색과 섞이는 것을 수정'],
    ['2018-08-07','API메뉴중 백업에 OnReceiveMessage 추가']
]

import sys, os
import datetime, time
import win32com.client
import pythoncom
import inspect

import pickle
import uuid
import base64
import subprocess
from subprocess import Popen
import webbrowser

import PyQt5
from PyQt5 import QtCore, QtGui, uic
from PyQt5 import QAxContainer
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtWidgets import QApplication, QLabel, QLineEdit, QMainWindow, QDialog, QMessageBox, QProgressBar
from PyQt5.QtGui import QPainter, QColor, QPen
from PyQt5.QAxContainer import *
from PyQt5.QtTest import QTest

import numpy as np
from numpy import NaN, Inf, arange, isscalar, asarray, array

import pandas as pd
import pandas.io.sql as pdsql
from pandas import DataFrame, Series

import sqlite3

import logging
import logging.handlers

#import threading
from threading import Timer
from multiprocessing import Pool, Process, Queue

from XASessions import *
from XAQueries import *
from XAReals import *

from FileWatcher import *
from Utils import *

import ctypes

#from apscheduler.jobstores.base import JobLookupError
#from apscheduler.schedulers.background import BackgroundScheduler

from enum import Enum
import timeit
import pyqtgraph as pg
import math
from bisect import bisect
import collections
from PIL import ImageGrab
import win32gui
import copy

pd.set_option('display.max_columns', None)
pd.set_option('display.expand_frame_repr', False)
pd.set_option('max_colwidth', -1)

주문지연 = 3000

DATABASE = 'DATA\\mymoneybot.sqlite'
UI_DIR = "UI\\"

# 전역변수
########################################################################################################################
time_delta = 0
START_ON = False
nRowCount = 99
Option_column = Enum('Option_column', '행사가 OLOH 기준가 월저 월고 전저 전고 종가 피봇 시가 시가갭 저가 현재가 고가 대비 진폭 OI OID')
Option_che_column = Enum('Option_che_column', '매도누적체결량 매도누적체결건수 매수누적체결량 매수누적체결건수')
Futures_column = Enum('Futures_column', '매수건수 매도건수 매수잔량 매도잔량 건수비 잔량비 전저 전고 종가 피봇 시가 시가갭 저가 현재가 고가 대비 진폭 거래량 VR OI OID')
Supply_column = Enum('Supply_column', '외인선옵 개인선옵 기관선옵 외인현물 프로그램')
Quote_column = Enum('Quote_column', 'C-MSCC C-MDCC C-MSCR C-MDCR P-MSCC P-MDCC P-MSCR P-MDCR 콜건수비 콜잔량비 풋건수비 풋잔량비 호가종합')
nCount_cm_option_pairs = 0

call_result = dict()
put_result = dict()

call_oi_percent_init_value = 0
put_oi_percent_init_value = 0

call_volume_total = 0
put_volume_total = 0

opt_x_idx = 0

call_below_atm_count = 0
put_above_atm_count = 0

call_background_color1 = [0] * nRowCount
call_foreground_color1 = [1] * nRowCount
call_background_color2 = [0] * nRowCount
call_foreground_color2 = [1] * nRowCount
call_background_color3 = [0] * nRowCount
call_foreground_color3 = [1] * nRowCount
call_background_color4 = [0] * nRowCount
call_foreground_color4 = [1] * nRowCount

put_background_color1 = [0] * nRowCount
put_foreground_color1 = [1] * nRowCount
put_background_color2 = [0] * nRowCount
put_foreground_color2 = [1] * nRowCount
put_background_color3 = [0] * nRowCount
put_foreground_color3 = [1] * nRowCount
put_background_color4 = [0] * nRowCount
put_foreground_color4 = [1] * nRowCount

call_1sec = [0, 3, 6, 9, 12, 15, 18, 21, 24, 27, 30, 33, 36, 39, 42, 45, 48, 51, 54, 57]
put_1sec = [1, 4, 7, 10, 13, 16, 19, 22, 25, 28, 31, 34, 37, 40, 43, 46, 49, 52, 55, 58]
ho_2sec = [0, 2, 4, 6, 8, 10, 12, 14, 16, 18, 20, 22, 24, 26, 28, 30, 32, 34, 36, 38, 40, 42, 44, 46, 48, 50, 52, 54, 56, 58]

call_2sec = [0, 6, 12, 18, 24, 30, 36, 42, 48, 54]
put_2sec = [2, 8, 14, 20, 26, 32, 38, 44, 50, 56]

call_3sec = [0, 9, 18, 27, 36, 45, 54]
put_3sec = [3, 12, 21, 30, 39, 48, 57]
ho_3sec = [6, 15, 24, 33, 42, 51]

ho_5sec = [0, 5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 55]

call_6sec = [3, 15, 27, 39, 51]
put_6sec = [6, 18, 30, 42, 54]
ho_6sec = [0, 12, 24, 36, 48]

call_10sec = [0, 20, 40]
put_10sec = [10, 30, 50]
ho_10sec = [15, 35, 55]
every_10sec = [0, 10, 20, 30, 40, 50]
every_20sec = [0, 20, 40]
every_30sec = [0, 30]
only_30sec = [30]
every_0sec = [0]

every_5min = [0, 5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 55]

ReceiveRealData = False

cm_option_title = ''

month_str = '201904'
nm_month_str = '201905'
month_firstday_str = '20190315'

today = datetime.date.today()
today_str = today.strftime('%Y%m%d')
today_str_title = today.strftime('%Y-%m-%d')

yesterday = today - datetime.timedelta(1)
yesterday_str = yesterday.strftime('%Y%m%d')

toggle_calltable = False
toggle_puttable = False

# 업종코드
KOSPI = '001'
KOSPI200 = '101'
KOSDAQ = '301'
OPT_CALL = '700'
OPT_PUT = '800'
FUTURES = '900'
CME = '950'

SAMSUNG	= '005930'
MOBIS = '012330'
NAVER = '035420'

STOCK = "0001"
BOHEOM = "0002"
TOOSIN = "0003"
BANK = "0004"
JONGGEUM = "0005"
GIGEUM = "0006"
GITA = "0007"
RETAIL = "0008"
FOREIGNER = "0017"
INSTITUTIONAL = "0018"

FUT_FOREIGNER_거래대금순매수 = 0
FUT_RETAIL_거래대금순매수 = 0
FUT_INSTITUTIONAL_거래대금순매수 = 0
FUT_STOCK_거래대금순매수 = 0
FUT_BOHEOM_거래대금순매수 = 0
FUT_TOOSIN_거래대금순매수 = 0
FUT_BANK_거래대금순매수 = 0
FUT_JONGGEUM_거래대금순매수 = 0
FUT_GIGEUM_거래대금순매수 = 0
FUT_GITA_거래대금순매수 = 0

FUT_FOREIGNER_거래대금순매수_직전대비 = 0
FUT_RETAIL_거래대금순매수_직전대비 = 0
FUT_INSTITUTIONAL_거래대금순매수_직전대비 = 0
FUT_STOCK_거래대금순매수_직전대비 = 0
FUT_BOHEOM_거래대금순매수_직전대비 = 0
FUT_TOOSIN_거래대금순매수_직전대비 = 0
FUT_BANK_거래대금순매수_직전대비 = 0
FUT_JONGGEUM_거래대금순매수_직전대비 = 0
FUT_GIGEUM_거래대금순매수_직전대비 = 0
FUT_GITA_거래대금순매수_직전대비 = 0

KOSPI_FOREIGNER_거래대금순매수 = 0
KOSPI_RETAIL_거래대금순매수 = 0
KOSPI_INSTITUTIONAL_거래대금순매수 = 0
KOSPI_STOCK_거래대금순매수 = 0
KOSPI_BOHEOM_거래대금순매수 = 0
KOSPI_TOOSIN_거래대금순매수 = 0
KOSPI_BANK_거래대금순매수 = 0
KOSPI_JONGGEUM_거래대금순매수 = 0
KOSPI_GIGEUM_거래대금순매수 = 0
KOSPI_GITA_거래대금순매수 = 0

KOSPI_FOREIGNER_거래대금순매수_직전대비 = 0
KOSPI_RETAIL_거래대금순매수_직전대비 = 0
KOSPI_INSTITUTIONAL_거래대금순매수_직전대비 = 0
KOSPI_STOCK_거래대금순매수_직전대비 = 0
KOSPI_BOHEOM_거래대금순매수_직전대비 = 0
KOSPI_TOOSIN_거래대금순매수_직전대비 = 0
KOSPI_BANK_거래대금순매수_직전대비 = 0
KOSPI_JONGGEUM_거래대금순매수_직전대비 = 0
KOSPI_GIGEUM_거래대금순매수_직전대비 = 0
KOSPI_GITA_거래대금순매수_직전대비 = 0

FUT_FOREIGNER_직전대비 = collections.deque([0, 0, 0], 3)
FUT_RETAIL_직전대비 = collections.deque([0, 0, 0], 3)
FUT_INSTITUTIONAL_직전대비 = collections.deque([0, 0, 0], 3)
KOSPI_FOREIGNER_직전대비 = collections.deque([0, 0, 0], 3)
PROGRAM_직전대비 = collections.deque([0, 0, 0], 3)
미결_직전대비 = collections.deque([0, 0, 0], 3)
거래량_직전대비 = collections.deque([0, 0, 0], 3)

actval_increased = False
nm_actval_increased = False

gmshcode = ''

call_atm_value = 0
put_atm_value = 0

kp200_realdata = dict()
fut_realdata = dict()

nm_opt_realdata = dict()
nm_opt_ho_realdata = dict()

cm_call_code = []
cm_put_code = []
cm_call_actval = []
cm_put_actval = []

cm_call_t8415_count = 0
cm_put_t8415_count = 0
cm_call_t8416_count = 0
cm_put_t8416_count = 0

df_nm_opt = pd.DataFrame()

df_cme = pd.DataFrame()
df_futures = pd.DataFrame()
df_cm_call = pd.DataFrame()
df_cm_put = pd.DataFrame()
df_cm_call_ho = pd.DataFrame()
df_cm_put_ho = pd.DataFrame()
df_cm_call_che = pd.DataFrame()
df_cm_put_che = pd.DataFrame()

call_quote = pd.Series()
put_quote = pd.Series()

call_che = pd.Series()
put_che = pd.Series()

nCount_nm_option_pairs = 0
nm_call_code = []
nm_put_code = []
nm_call_actval = []
nm_put_actval = []

nm_call_code_on = []
nm_put_code_on = []

nm_call_t8416_count = 0
nm_put_t8416_count = 0
df_nm_call = pd.DataFrame()
df_nm_put = pd.DataFrame()

call_ckbox = []
put_ckbox = []
nm_call_ckbox = []
nm_put_ckbox = []

atm_str = ''
atm_index = 0
old_atm_index = 0
atm_index_yj = 0
jgubun = ''

start_time = 0
start_time1 = 0

count = 0
global_blink = True

의미가 = [1.20, 2.50, 3.50, 4.85, 5.10, 5.50, 6.85, 7.10, 8.10]
coreval = []

cm_call_행사가 = []
cm_call_기준가 = []
cm_call_월저 = []
cm_call_월고 = []
cm_call_전저 = []
cm_call_전고 = []
cm_call_종가 = []
cm_call_피봇 = []
cm_call_시가 = []
cm_call_저가 = []
cm_call_고가 = []
콜_미결합 = 0
콜미결퍼센트 = 0

cm_call_기준가_extend = []
cm_call_월저_extend = []
cm_call_월고_extend = []
cm_call_전저_extend = []
cm_call_전고_extend = []
cm_call_종가_extend = []
cm_call_피봇_extend = []
cm_call_시가_extend = []
cm_call_저가_extend = []
cm_call_고가_extend = []

cm_put_행사가 = []
cm_put_기준가 = []
cm_put_월저 = []
cm_put_월고 = []
cm_put_전저 = []
cm_put_전고 = []
cm_put_종가 = []
cm_put_피봇 = []
cm_put_시가 = []
cm_put_저가 = []
cm_put_고가 = []
풋_미결합 = 0
풋미결퍼센트 = 0

cm_put_기준가_extend = []
cm_put_월저_extend = []
cm_put_월고_extend = []
cm_put_전저_extend = []
cm_put_전고_extend = []
cm_put_종가_extend = []
cm_put_피봇_extend = []
cm_put_시가_extend = []
cm_put_저가_extend = []
cm_put_고가_extend = []

nm_call_행사가 = []
nm_call_기준가 = []
nm_call_월저 = []
nm_call_월고 = []
nm_call_전저 = []
nm_call_전고 = []
nm_call_종가 = []
nm_call_피봇 = []
nm_call_시가 = []

nm_put_행사가 = []
nm_put_기준가 = []
nm_put_월저 = []
nm_put_월고 = []
nm_put_전저 = []
nm_put_전고 = []
nm_put_종가 = []
nm_put_피봇 = []
nm_put_시가 = []

df_plotdata_cm_call = pd.DataFrame()
df_plotdata_cm_put = pd.DataFrame()
df_plotdata_cm_call_volume = pd.DataFrame()
df_plotdata_cm_put_volume = pd.DataFrame()
df_plotdata_cm_volume_cha = pd.DataFrame()
df_plotdata_cm_call_oi = pd.DataFrame()
df_plotdata_cm_put_oi = pd.DataFrame()
df_plotdata_cm_oi_cha = pd.DataFrame()

df_plotdata_fut = pd.DataFrame()
df_plotdata_kp200 = pd.DataFrame()
df_plotdata_cme = pd.DataFrame()

df_plotdata_nm_call = pd.DataFrame()
df_plotdata_nm_put = pd.DataFrame()

start_hour = 9

blueviolet = QColor(138, 43, 226)
lightyellow = QColor(255, 255, 153)
aqua = QColor(0x00, 0xFF, 0xFF)
deepskyblue = QColor(0, 191, 255)
orangered = QColor(255, 69, 0)
magenta = QColor(255, 0, 255)
cyan = QColor(0, 255, 255)
lavender = QColor(230, 230, 250)
mistyrose = QColor(255, 228, 225)
chocolate = QColor(0xD2, 0x69, 0x1E)

gold = QColor(0xFF, 0xD7, 0x00)
goldenrod = QColor(0xDA, 0xA5, 0x20)
skyblue = QColor(0x87, 0xCE, 0xEB)
steelblue = QColor(0x46, 0x82, 0xB4)

darkorange = QColor(0xFF, 0x8C, 0x00)
crimson = QColor(0xDC, 0x14, 0x3C)
indigo = QColor(0x4B, 0x00, 0x82)
royalblue = QColor(0x41, 0x69, 0xE1)

기본바탕색 = Qt.white
검정색 = Qt.black
흰색 = Qt.white
옅은회색 = Qt.lightGray
적색 = Qt.red
청색 = Qt.blue
녹색 = Qt.green
노란색 = Qt.yellow

콜기준가색 = Qt.darkRed
콜월저색 = darkorange
콜월고색 = crimson
콜전저색 = goldenrod
콜전고색 = gold
콜종가색 = chocolate
콜피봇색 = magenta
콜시가색 = 적색

풋기준가색 = Qt.darkBlue
풋월저색 = indigo
풋월고색 = royalblue
풋전저색 = steelblue
풋전고색 = skyblue
풋종가색 = Qt.darkCyan
풋피봇색 = cyan
풋시가색 = 청색

대맥점색 = Qt.green

futpen=pg.mkPen(blueviolet, width=2, style=QtCore.Qt.SolidLine)
rpen=pg.mkPen('r', width=2, style=QtCore.Qt.SolidLine)
bpen=pg.mkPen('b', width=2, style=QtCore.Qt.SolidLine)
gpen=pg.mkPen('g', width=2, style=QtCore.Qt.SolidLine)
mvpen=pg.mkPen('g', width=1, style=QtCore.Qt.DotLine)
tpen=pg.mkPen(lightyellow, width=2, style=QtCore.Qt.DotLine)

fut_jl_pen=pg.mkPen(aqua, width=2, style=QtCore.Qt.DotLine)
fut_jh_pen=pg.mkPen(orangered, width=2, style=QtCore.Qt.DotLine)
fut_pvt_pen=pg.mkPen(magenta, width=2, style=QtCore.Qt.DotLine)

aqua_pen=pg.mkPen(aqua, width=2, style=QtCore.Qt.SolidLine)
magenta_pen=pg.mkPen(magenta, width=2, style=QtCore.Qt.SolidLine)
green_pen=pg.mkPen('g', width=2, style=QtCore.Qt.SolidLine)

fut_axY = []

overnight = False

call_scroll_begin_position = 0
call_scroll_end_position = 0
put_scroll_begin_position = 0
put_scroll_end_position = 0

nm_call_scroll_position = 0
nm_put_scroll_position = 0

x_idx = 0

pre_start = False

selected_call = []
selected_put = []

mv_curve = []
mv_line = []
time_line = None
time_line_fut = None

fut_curve = None
fut_pivot_line = None
fut_jl_line = None
fut_jh_line = None
kp200_curve = None
call_curve = []
put_curve = []

volume_base_line = None

cm_call_volume_curve = None
cm_put_volume_curve = None
cm_volume_cha_curve = None

cm_call_oi_curve = None
cm_put_oi_curve = None
cm_oi_cha_curve = None

volume_cha_sign = []

call_node_state = dict()
put_node_state = dict()

yoc_call_gap_percent = [NaN] * nRowCount
yoc_put_gap_percent = [NaN] * nRowCount

call_open = [False] * nRowCount
call_ol = [False] * nRowCount
call_oh = [False] * nRowCount
call_gap_percent = [NaN] * nRowCount
call_db_percent = [NaN] * nRowCount

put_open = [False] * nRowCount
put_ol = [False] * nRowCount
put_oh = [False] * nRowCount
put_gap_percent = [NaN] * nRowCount
put_db_percent = [NaN] * nRowCount

nm_call_open_count = 0
nm_put_open_count = 0

nm_call_ol_count = 0
nm_call_oh_count = 0
nm_put_ol_count = 0
nm_put_oh_count = 0

nm_call_ol = [False] * nRowCount
nm_call_oh = [False] * nRowCount
nm_put_ol = [False] * nRowCount
nm_put_oh = [False] * nRowCount

nm_call_gap_percent = [NaN] * nRowCount
nm_put_gap_percent = [NaN] * nRowCount

opt_callreal_update_counter = 0
opt_putreal_update_counter = 0
opt_call_ho_update_counter = 0
opt_put_ho_update_counter = 0

call_update = False
put_update = False
opt_ho_update = False

call_max_volume_index = 0
put_max_volume_index = 0

refresh_flag = False

oi_delta = 0
oi_delta_old = 0

volume_delta = 0
volume_delta_old = 0

delta_hour = 0
delta_minute = 0
delta_sec = 0

comboindex = 0

콜현재가 = ''
풋현재가 = ''
선물현재가 = 0

콜저가리스트 = None
콜고가리스트 = None

풋저가리스트 = None
풋고가리스트 = None

########################################################################################################################

def sqliteconn():
    conn = sqlite3.connect(DATABASE)
    return conn

# Xing 관리자모드 실행 체크함수
def XingAdminCheck():
    # 프로세스가 관리자 권한으로 실행 여부
    if ctypes.windll.shell32.IsUserAnAdmin():
        print('관리자권한으로 실행된 프로세스입니다.')
        return True
    else:
        print('일반권한으로 실행된 프로세스입니다.')
        return False

class PandasModel(QtCore.QAbstractTableModel):
    def __init__(self, data=None, parent=None):
        QtCore.QAbstractTableModel.__init__(self, parent)
        self._data = data
        if data is None:
            self._data = DataFrame()

    def rowCount(self, parent=None):
        return len(self._data.index)

    def columnCount(self, parent=None):
        return self._data.columns.size

    def data(self, index, role=Qt.DisplayRole):
        if index.isValid():
            if role == Qt.DisplayRole:
                return str(self._data.values[index.row()][index.column()])
        return None

    def headerData(self, column, orientation, role=Qt.DisplayRole):
        if role != Qt.DisplayRole:
            return None
        if orientation == Qt.Horizontal:
            return self._data.columns[column]
        return int(column + 1)

    def update(self, data):
        self._data = data
        self.reset()

    def reset(self):
        self.beginResetModel()
        self.endResetModel()

    def flags(self, index):
        return QtCore.Qt.ItemIsEnabled

class RealDataTableModel(QAbstractTableModel):
    def __init__(self, parent=None):
        QtCore.QAbstractTableModel.__init__(self, parent)
        self.realdata = {}
        self.headers = ['종목코드', '현재가' , '전일대비', '등락률' , '매도호가', '매수호가', '누적거래량', '시가' , '고가' , '저가' , '거래회전율', '시가총액']

    def rowCount(self, index=QModelIndex()):
        return len(self.realdata)

    def columnCount(self, index=QModelIndex()):
        return len(self.headers)

    def data(self, index, role=Qt.DisplayRole):
        if (not index.isValid() or not (0 <= index.row() < len(self.realdata))):
            return None

        if role == Qt.DisplayRole:
            rows = []
            for k in self.realdata.keys():
                rows.append(k)
            one_row = rows[index.row()]
            selected_row = self.realdata[one_row]

            return selected_row[index.column()]

        return None

    def headerData(self, column, orientation, role=Qt.DisplayRole):
        if role != Qt.DisplayRole:
            return None
        if orientation == Qt.Horizontal:
            return self.headers[column]
        return int(column + 1)

    def flags(self, index):
        return QtCore.Qt.ItemIsEnabled

    def reset(self):
        self.beginResetModel()
        self.endResetModel()

class CPluginManager:
    plugins = None
    @classmethod
    def plugin_loader(cls):
        path = "plugins/"
        result = {}

        # Load plugins
        sys.path.insert(0, path)
        for f in os.listdir(path):
            fname, ext = os.path.splitext(f)
            if ext == '.py':
                mod = __import__(fname)
                robot = mod.robot_loader()
                if robot != None:
                    result[robot.Name] = robot
        sys.path.pop(0)

        CPluginManager.plugins = result

        return result


Ui_계좌정보조회, QtBaseClass_계좌정보조회 = uic.loadUiType(UI_DIR+"계좌정보조회.ui")
class 화면_계좌정보(QDialog, Ui_계좌정보조회):
    def __init__(self, parent=None):
        super(화면_계좌정보, self).__init__(parent)
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.setupUi(self)
        self.parent = parent
        self.model1 = PandasModel()
        self.tableView_1.setModel(self.model1)
        self.model2 = PandasModel()
        self.tableView_2.setModel(self.model2)

        self.result = []
        self.connection = self.parent.connection

        # 계좌정보 불러오기
        nCount = self.connection.ActiveX.GetAccountListCount()
        for i in range(nCount):
            self.comboBox.addItem(self.connection.ActiveX.GetAccountList(i))

        self.XQ_t0424 = t0424(parent=self)

    def OnReceiveMessage(self, systemError, messageCode, message):
        # print(systemError, messageCode, message)
        pass

    def OnReceiveData(self, szTrCode, result):
        if szTrCode == 't0424':
            self.df1, self.df2 = result

            self.model1.update(self.df1)
            for i in range(len(self.df1.columns)):
                self.tableView_1.resizeColumnToContents(i)

            self.model2.update(self.df2)
            for i in range(len(self.df2.columns)):
                self.tableView_2.resizeColumnToContents(i)

            CTS_종목번호 = self.df1['CTS_종목번호'].values[0].strip()
            if CTS_종목번호 != '':
                self.XQ_t0424.Query(계좌번호=self.계좌번호, 비밀번호=self.비밀번호, 단가구분='1', 체결구분='0', 단일가구분='0', 제비용포함여부='1', CTS_종목번호=CTS_종목번호)

    def inquiry(self):
        self.계좌번호 = self.comboBox.currentText().strip()
        self.비밀번호 = self.lineEdit.text().strip()

        self.XQ_t0424.Query(계좌번호=self.계좌번호,비밀번호=self.비밀번호,단가구분='1',체결구분='0',단일가구분='0',제비용포함여부='1',CTS_종목번호='')

        QTimer().singleShot(3*1000, self.inquiry)


Ui_일별가격정보백업, QtBaseClass_일별가격정보백업 = uic.loadUiType(UI_DIR+"일별가격정보백업.ui")
class 화면_일별가격정보백업(QDialog, Ui_일별가격정보백업):
    def __init__(self, parent=None):
        super(화면_일별가격정보백업, self).__init__(parent)
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.setupUi(self)
        self.setWindowTitle('가격 정보 백업')
        self.parent = parent
        self.result = []

        d = datetime.date.today()
        self.lineEdit_date.setText(str(d))

        XQ_t8436 = t8436(parent=self)
        XQ_t8436.Query(구분='0')

        self.조회건수 = 10
        self.XQ_t1305 = t1305(parent=self)

    def OnReceiveMessage(self, systemError, messageCode, message):
        pass

    def OnReceiveData(self, szTrCode, result):
        if szTrCode == 't8436':
            self.종목코드테이블 = result[0]
            self.종목코드테이블['컬럼'] = ">> " + self.종목코드테이블['단축코드'] + " : " + self.종목코드테이블['종목명']
            self.종목코드테이블 = self.종목코드테이블.sort_values(['단축코드', '종목명'], ascending=[True, True])
            self.comboBox.addItems(self.종목코드테이블['컬럼'].values)

        if szTrCode == 't1305':
            CNT, 날짜, IDX, df = result
            # print(self.단축코드, CNT, 날짜, IDX)
            with sqlite3.connect(DATABASE) as conn:
                cursor = conn.cursor()
                query = "insert or replace into 일별주가( 날짜, 시가, 고가, 저가, 종가, 전일대비구분, 전일대비, 등락율, 누적거래량, 거래증가율, 체결강도, 소진율, 회전율, 외인순매수, 기관순매수, 종목코드, 누적거래대금, 개인순매수, 시가대비구분, 시가대비, 시가기준등락율, 고가대비구분, 고가대비, 고가기준등락율, 저가대비구분, 저가대비, 저가기준등락율, 시가총액) values(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"
                cursor.executemany(query, df.values.tolist())
                conn.commit()

            try:
                if int(CNT) == int(self.조회건수) and self.radioButton_all.isChecked() == True:
                    QTimer.singleShot(주문지연, lambda: self.Request(result=result))
                else:
                    self.백업한종목수 += 1
                    if len(self.백업할종목코드) > 0:
                        self.단축코드 = self.백업할종목코드.pop(0)
                        self.result = []

                        self.progressBar.setValue(int(self.백업한종목수 / (len(self.종목코드테이블.index) - self.comboBox.currentIndex()) * 100))
                        S = '%s %s' % (self.단축코드[0], self.단축코드[1])
                        self.label_codename.setText(S)

                        QTimer.singleShot(주문지연, lambda : self.Request([]))
                    else:
                        QMessageBox.about(self, "백업완료","백업을 완료하였습니다..")
            except Exception as e:
                pass

    def Request(self, result=[]):
        if len(result) > 0:
            CNT, 날짜, IDX, df = result
            self.XQ_t1305.Query(단축코드=self.단축코드[0], 일주월구분='1', 날짜=날짜, IDX=IDX, 건수=self.조회건수, 연속조회=True)
        else:
            try:
                # print('%s %s' % (self.단축코드[0], self.단축코드[1]))
                self.XQ_t1305.Query(단축코드=self.단축코드[0], 일주월구분='1', 날짜='', IDX='', 건수=self.조회건수, 연속조회=False)
            except Exception as e:
                pass

    def Backup_One(self):
        idx = self.comboBox.currentIndex()

        self.백업한종목수 = 1
        self.백업할종목코드 = []
        self.단축코드 = self.종목코드테이블[idx:idx + 1][['단축코드','종목명']].values[0]
        self.기준일자 = self.lineEdit_date.text().strip().replace('-','')
        self.result = []
        self.Request(result=[])

    def Backup_All(self):
        idx = self.comboBox.currentIndex()
        self.백업한종목수 = 1
        self.백업할종목코드 = list(self.종목코드테이블[idx:][['단축코드','종목명']].values)
        self.단축코드 = self.백업할종목코드.pop(0)
        self.기준일자 = self.lineEdit_date.text().strip().replace('-','')

        self.progressBar.setValue(int(self.백업한종목수 / (len(self.종목코드테이블.index) - self.comboBox.currentIndex()) * 100))
        S = '%s %s' % (self.단축코드[0], self.단축코드[1])
        self.label_codename.setText(S)

        self.result = []
        self.Request(result=[])


Ui_일별업종정보백업, QtBaseClass_일별업종정보백업 = uic.loadUiType(UI_DIR+"일별업종정보백업.ui")
class 화면_일별업종정보백업(QDialog, Ui_일별업종정보백업):
    def __init__(self, parent=None):
        super(화면_일별업종정보백업, self).__init__(parent)
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.setupUi(self)
        self.setWindowTitle('업종 정보 백업')
        self.parent = parent

        self.columns = ['현재가', '거래량', '일자', '시가', '고가', '저가','거래대금', '대업종구분', '소업종구분', '종목정보', '종목정보', '수정주가이벤트', '전일종가']

        self.result = []

        d = datetime.date.today()
        self.lineEdit_date.setText(str(d))

        XQ = t8424(parent=self)
        XQ.Query()

        self.조회건수 = 10
        self.XQ_t1514 = t1514(parent=self)

    def OnReceiveMessage(self, systemError, messageCode, message):
        pass

    def OnReceiveData(self, szTrCode, result):
        if szTrCode == 't8424':
            df = result[0]
            with sqlite3.connect(DATABASE) as conn:
                cursor = conn.cursor()
                query = "insert or replace into 업종코드(업종명, 업종코드) values(?, ?)"
                cursor.executemany(query, df.values.tolist())
                conn.commit()

            self.업종코드테이블 = result[0]
            self.업종코드테이블['컬럼'] = ">> " + self.업종코드테이블['업종코드'] + " : " + self.업종코드테이블['업종명']
            self.업종코드테이블 = self.업종코드테이블.sort_values(['업종코드', '업종명'], ascending=[True, True])
            self.comboBox.addItems(self.업종코드테이블['컬럼'].values)

        if szTrCode == 't1514':
            CTS일자, df = result
            # print(CTS일자)
            with sqlite3.connect(DATABASE) as conn:
                cursor = conn.cursor()
                query = "insert or replace into 업종정보(일자, 지수, 전일대비구분, 전일대비, 등락율, 거래량, 거래증가율, 거래대금1, 상승, 보합, 하락, 상승종목비율, 외인순매수, 시가, 고가, 저가, 거래대금2, 상한, 하한, 종목수, 기관순매수, 업종코드, 거래비중, 업종배당수익률) values(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"
                cursor.executemany(query, df.values.tolist())
                conn.commit()

            try:
                if len(df) == int(self.조회건수) and self.radioButton_all.isChecked() == True:
                    QTimer.singleShot(주문지연, lambda: self.Request(result=result))
                else:
                    self.백업한종목수 += 1
                    if len(self.백업할업종코드) > 0:
                        self.업종코드 = self.백업할업종코드.pop(0)
                        self.result = []

                        self.progressBar.setValue(int(self.백업한종목수 / (len(self.업종코드테이블.index) - self.comboBox.currentIndex()) * 100))
                        S = '%s %s' % (self.업종코드[0], self.업종코드[1])
                        self.label_codename.setText(S)

                        QTimer.singleShot(주문지연, lambda : self.Request([]))
                    else:
                        QMessageBox.about(self, "백업완료","백업을 완료하였습니다..")
            except Exception as e:
                pass

    def Request(self, result=[]):
        if len(result) > 0:
            CTS일자, df = result
            self.XQ_t1514.Query(업종코드=self.업종코드[0],구분1='',구분2='1',CTS일자=CTS일자, 조회건수=self.조회건수,비중구분='', 연속조회=True)
        else:
            # print('%s %s' % (self.업종코드[0], self.업종코드[1]))
            self.XQ_t1514.Query(업종코드=self.업종코드[0], 구분1='', 구분2='1', CTS일자='', 조회건수=self.조회건수, 비중구분='', 연속조회=False)

    def Backup_One(self):
        idx = self.comboBox.currentIndex()

        self.백업한종목수 = 1
        self.백업할업종코드 = []
        self.업종코드 = self.업종코드테이블[idx:idx + 1][['업종코드','업종명']].values[0]
        self.기준일자 = self.lineEdit_date.text().strip().replace('-','')
        self.result = []
        self.Request(result=[])

    def Backup_All(self):
        idx = self.comboBox.currentIndex()
        self.백업한종목수 = 1
        self.백업할업종코드 = list(self.업종코드테이블[idx:][['업종코드','업종명']].values)
        self.업종코드 = self.백업할업종코드.pop(0)
        self.기준일자 = self.lineEdit_date.text().strip().replace('-','')

        self.progressBar.setValue(int(self.백업한종목수 / (len(self.업종코드테이블.index) - self.comboBox.currentIndex()) * 100))
        S = '%s %s' % (self.업종코드[0], self.업종코드[1])
        self.label_codename.setText(S)

        self.result = []
        self.Request(result=[])


Ui_분별가격정보백업, QtBaseClass_분별가격정보백업 = uic.loadUiType(UI_DIR+"분별가격정보백업.ui")
class 화면_분별가격정보백업(QDialog, Ui_분별가격정보백업):
    def __init__(self, parent=None):
        super(화면_분별가격정보백업, self).__init__(parent)
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.setupUi(self)
        self.setWindowTitle('가격 정보 백업')
        self.parent = parent

        self.columns = ['체결시간', '현재가', '시가', '고가', '저가', '거래량']

        self.result = []

        XQ_t8436 = t8436(parent=self)
        XQ_t8436.Query(구분='0')

        self.조회건수 = 10
        self.XQ_t1302 = t1302(parent=self)

    def OnReceiveMessage(self, systemError, messageCode, message):
        pass

    def OnReceiveData(self, szTrCode, result):
        if szTrCode == 't8436':
            self.종목코드테이블 = result[0]
            self.종목코드테이블['컬럼'] = ">> " + self.종목코드테이블['단축코드'] + " : " + self.종목코드테이블['종목명']
            self.종목코드테이블 = self.종목코드테이블.sort_values(['단축코드', '종목명'], ascending=[True, True])
            self.comboBox.addItems(self.종목코드테이블['컬럼'].values)

        if szTrCode == 't1302':
            시간CTS, df = result
            df['단축코드'] = self.단축코드[0]
            # print(시간CTS)
            with sqlite3.connect(DATABASE) as conn:
                cursor = conn.cursor()
                query = "insert or replace into 분별주가(시간, 종가, 전일대비구분, 전일대비, 등락율, 체결강도, 매도체결수량, 매수체결수량, 순매수체결량, 매도체결건수, 매수체결건수, 순체결건수, 거래량, 시가, 고가, 저가, 체결량, 매도체결건수시간, 매수체결건수시간, 매도잔량, 매수잔량, 시간별매도체결량, 시간별매수체결량,단축코드) values(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"
                cursor.executemany(query, df.values.tolist())
                conn.commit()

            try:
                if len(df) == int(self.조회건수) and self.radioButton_all.isChecked() == True:
                    QTimer.singleShot(주문지연, lambda: self.Request(result=result))
                else:
                    self.백업한종목수 += 1
                    if len(self.백업할종목코드) > 0:
                        self.단축코드 = self.백업할종목코드.pop(0)
                        self.result = []

                        self.progressBar.setValue(int(self.백업한종목수 / (len(self.종목코드테이블.index) - self.comboBox.currentIndex()) * 100))
                        S = '%s %s' % (self.단축코드[0], self.단축코드[1])
                        self.label_codename.setText(S)

                        QTimer.singleShot(주문지연, lambda : self.Request([]))
                    else:
                        QMessageBox.about(self, "백업완료","백업을 완료하였습니다..")
            except Exception as e:
                pass

    def Request(self, result=[]):
        if len(result) > 0:
            시간CTS, df = result
            self.XQ_t1302.Query(단축코드=self.단축코드[0], 작업구분=self.틱범위, 시간=시간CTS, 건수=self.조회건수, 연속조회=True)
        else:
            # print('%s %s' % (self.단축코드[0], self.단축코드[1]))
            self.XQ_t1302.Query(단축코드=self.단축코드[0], 작업구분=self.틱범위, 시간='', 건수=self.조회건수, 연속조회=False)

    def Backup_One(self):
        idx = self.comboBox.currentIndex()

        self.백업한종목수 = 1
        self.백업할종목코드 = []
        self.단축코드 = self.종목코드테이블[idx:idx + 1][['단축코드','종목명']].values[0]
        self.틱범위 = self.comboBox_min.currentText()[0:1].strip()
        if self.틱범위[0] == '0':
            self.틱범위 = self.틱범위[1:]
        self.result = []
        self.Request(result=[])

    def Backup_All(self):
        idx = self.comboBox.currentIndex()
        self.백업한종목수 = 1
        self.백업할종목코드 = list(self.종목코드테이블[idx:][['단축코드','종목명']].values)
        self.단축코드 = self.백업할종목코드.pop(0)
        self.틱범위 = self.comboBox_min.currentText()[0:1].strip()
        if self.틱범위[0] == '0':
            self.틱범위 = self.틱범위[1:]

        self.progressBar.setValue(int(self.백업한종목수 / (len(self.종목코드테이블.index) - self.comboBox.currentIndex()) * 100))
        S = '%s %s' % (self.단축코드[0], self.단축코드[1])
        self.label_codename.setText(S)

        self.result = []
        self.Request(result=[])


Ui_종목별투자자정보백업, QtBaseClass_종목별투자자정보백업 = uic.loadUiType(UI_DIR+"종목별투자자정보백업.ui")
class 화면_종목별투자자정보백업(QDialog, Ui_종목별투자자정보백업):
    def __init__(self, parent=None):
        super(화면_종목별투자자정보백업, self).__init__(parent)
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.setupUi(self)
        self.setWindowTitle('종목별 투자자 정보 백업')
        self.parent = parent

        self.columns = ['일자', '현재가', '전일대비', '누적거래대금', '개인투자자', '외국인투자자','기관계','금융투자','보험','투신','기타금융','은행','연기금등','국가','내외국인','사모펀드','기타법인']

        d = datetime.date.today()
        self.lineEdit_date.setText(str(d))

        XQ_t8436 = t8436(parent=self)
        XQ_t8436.Query(구분='0')

        self.조회건수 = 10
        self.XQ_t1702 = t1702(parent=self)

    def OnReceiveMessage(self, systemError, messageCode, message):
        pass

    def OnReceiveData(self, szTrCode, result):
        if szTrCode == 't8436':
            self.종목코드테이블 = result[0]
            self.종목코드테이블['컬럼'] = ">> " + self.종목코드테이블['단축코드'] + " : " + self.종목코드테이블['종목명']
            self.종목코드테이블 = self.종목코드테이블.sort_values(['단축코드', '종목명'], ascending=[True, True])
            self.comboBox.addItems(self.종목코드테이블['컬럼'].values)

        if szTrCode == 't1702':
            CTSIDX, CTSDATE, df = result
            df['단축코드'] = self.단축코드[0]
            # print(CTSIDX, CTSDATE)
            with sqlite3.connect(DATABASE) as conn:
                cursor = conn.cursor()
                query = "insert or replace into 종목별투자자(일자, 종가, 전일대비구분, 전일대비, 등락율, 누적거래량, 사모펀드, 증권, 보험, 투신, 은행, 종금, 기금, 기타법인, 개인, 등록외국인, 미등록외국인, 국가외, 기관, 외인계, 기타계, 단축코드) values(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"
                cursor.executemany(query, df.values.tolist())
                conn.commit()

            try:
                if len(df) == int(self.조회건수) and self.radioButton_all.isChecked() == True:
                    QTimer.singleShot(주문지연, lambda: self.Request(result=result))
                else:
                    self.백업한종목수 += 1
                    if len(self.백업할종목코드) > 0:
                        self.단축코드 = self.백업할종목코드.pop(0)
                        self.result = []

                        self.progressBar.setValue(int(self.백업한종목수 / (len(self.종목코드테이블.index) - self.comboBox.currentIndex()) * 100))
                        S = '%s %s' % (self.단축코드[0], self.단축코드[1])
                        self.label_codename.setText(S)

                        QTimer.singleShot(주문지연, lambda : self.Request([]))
                    else:
                        QMessageBox.about(self, "백업완료","백업을 완료하였습니다..")
            except Exception as e:
                pass

    def Request(self, result=[]):
        if len(result) > 0:
            CTSIDX, CTSDATE, df = result
            self.XQ_t1702.Query(종목코드=self.단축코드[0], 종료일자='', 금액수량구분='0', 매수매도구분='0', 누적구분='0', CTSDATE=CTSDATE, CTSIDX=CTSIDX)
        else:
            # print('%s %s' % (self.단축코드[0], self.단축코드[1]))
            self.XQ_t1702.Query(종목코드=self.단축코드[0], 종료일자='', 금액수량구분='0', 매수매도구분='0', 누적구분='0', CTSDATE='', CTSIDX='')

    def Backup_One(self):
        idx = self.comboBox.currentIndex()

        self.백업한종목수 = 1
        self.백업할종목코드 = []
        self.단축코드 = self.종목코드테이블[idx:idx + 1][['단축코드','종목명']].values[0]
        self.기준일자 = self.lineEdit_date.text().strip().replace('-','')
        self.result = []
        self.Request(result=[])

    def Backup_All(self):
        idx = self.comboBox.currentIndex()
        self.백업한종목수 = 1
        self.백업할종목코드 = list(self.종목코드테이블[idx:][['단축코드','종목명']].values)
        self.단축코드 = self.백업할종목코드.pop(0)
        self.기준일자 = self.lineEdit_date.text().strip().replace('-','')

        self.progressBar.setValue(int(self.백업한종목수 / (len(self.종목코드테이블.index) - self.comboBox.currentIndex()) * 100))
        S = '%s %s' % (self.단축코드[0], self.단축코드[1])
        self.label_codename.setText(S)

        self.result = []
        self.Request(result=[])

## ---------------------------------------------------------------------------------------------------------------------
Ui_종목코드, QtBaseClass_종목코드 = uic.loadUiType(UI_DIR+"종목코드조회.ui")
class 화면_종목코드(QDialog, Ui_종목코드):
    def __init__(self, parent=None):
        super(화면_종목코드, self).__init__(parent)
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.setupUi(self)

        self.parent = parent

        self.model = PandasModel()
        self.tableView.setModel(self.model)

        self.df = DataFrame()
        self.XQ_t8436 = t8436(parent=self)
        self.XQ_t8436.Query(구분='0')

    def OnReceiveMessage(self, systemError, messageCode, message):
        # print(systemError, messageCode, message)
        pass

    def OnReceiveData(self, szTrCode, result):
        if szTrCode == 't8436':
            self.df = result[0]
            self.model.update(self.df)
            for i in range(len(self.df.columns)):
                self.tableView.resizeColumnToContents(i)

    def SaveCode(self):
        with sqlite3.connect(DATABASE) as conn:
            cursor = conn.cursor()
            query = "insert or replace into 종목코드(종목명,단축코드,확장코드,ETF구분,상한가,하한가,전일가,주문수량단위,기준가,구분,증권그룹,기업인수목적회사여부) values(?,?,?,?,?,?,?,?,?,?,?,?)"
            cursor.executemany(query, self.df.values.tolist())
            conn.commit()

        QMessageBox.about(self, "종목코드 생성", " %s 항목의 종목코드를 생성하였습니다." % (len(self.df)))


Ui_업종정보, QtBaseClass_업종정보 = uic.loadUiType(UI_DIR+"업종정보조회.ui")
class 화면_업종정보(QDialog, Ui_업종정보):
    def __init__(self, parent=None):
        super(화면_업종정보, self).__init__(parent)
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.setupUi(self)

        self.setWindowTitle('업종정보 조회')

        self.parent = parent

        self.model = PandasModel()
        self.tableView.setModel(self.model)

        self.columns = ['일자', '지수', '전일대비구분', '전일대비', '등락율', '거래량', '거래증가율', '거래대금1', '상승', '보합', '하락', '상승종목비율', '외인순매수',
                   '시가', '고가', '저가', '거래대금2', '상한', '하한', '종목수', '기관순매수', '업종코드', '거래비중', '업종배당수익률']

        self.result = []

        d = datetime.date.today()

        XQ = t8424(parent=self)
        XQ.Query()

    def OnReceiveMessage(self, systemError, messageCode, message):
        # print(systemError, messageCode, message)
        pass

    def OnReceiveData(self, szTrCode, result):
        if szTrCode == 't8424':
            df = result[0]
            df['컬럼'] = df['업종코드'] + " : " + df['업종명']
            df = df.sort_values(['업종코드', '업종명'], ascending=[True, True])
            self.comboBox.addItems(df['컬럼'].values)

        if szTrCode == 't1514':
            CTS일자, df = result
            self.model.update(df)
            for i in range(len(df.columns)):
                self.tableView.resizeColumnToContents(i)

    def inquiry(self):
        업종코드 = self.comboBox.currentText()[:3]
        조회건수 = self.lineEdit_date.text().strip().replace('-', '')

        XQ = t1514(parent=self)
        XQ.Query(업종코드=업종코드,구분1='',구분2='1',CTS일자='',조회건수=조회건수,비중구분='', 연속조회=False)


Ui_테마정보, QtBaseClass_테마정보 = uic.loadUiType(UI_DIR+"테마정보조회.ui")
class 화면_테마정보(QDialog, Ui_테마정보):
    def __init__(self, parent=None):
        super(화면_테마정보, self).__init__(parent)
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.setupUi(self)

        self.setWindowTitle('테마정보 조회')

        self.parent = parent

        self.model = PandasModel()
        self.tableView.setModel(self.model)

        self.columns = ['일자', '지수', '전일대비구분', '전일대비', '등락율', '거래량', '거래증가율', '거래대금1', '상승', '보합', '하락', '상승종목비율', '외인순매수',
                   '시가', '고가', '저가', '거래대금2', '상한', '하한', '종목수', '기관순매수', '업종코드', '거래비중', '업종배당수익률']

        self.result = []

        d = datetime.date.today()

        XQ = t8425(parent=self)
        XQ.Query()

    def OnReceiveMessage(self, systemError, messageCode, message):
        # print(systemError, messageCode, message)
        pass

    def OnReceiveData(self, szTrCode, result):
        if szTrCode == 't8425':
            df = result[0]
            df['컬럼'] = df['테마코드'] + " : " + df['테마명']
            df = df.sort_values(['테마코드', '테마명'], ascending=[True, True])
            self.comboBox.addItems(df['컬럼'].values)

        if szTrCode == 't1537':
            df0, df = result
            self.model.update(df)
            for i in range(len(df.columns)):
                self.tableView.resizeColumnToContents(i)

    def inquiry(self):
        테마코드 = self.comboBox.currentText()[:4]

        XQ = t1537(parent=self)
        XQ.Query(테마코드=테마코드, 연속조회=False)


Ui_분별주가조회, QtBaseClass_분별주가조회 = uic.loadUiType(UI_DIR+"분별주가조회.ui")
class 화면_분별주가(QDialog, Ui_분별주가조회):
    def __init__(self, parent=None):
        super(화면_분별주가, self).__init__(parent)
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.setupUi(self)
        self.setWindowTitle('분별 주가 조회')
        self.parent = parent

        self.model = PandasModel()
        self.tableView.setModel(self.model)

        self.columns = []

        self.result = []

        XQ = t8436(parent=self)
        XQ.Query(구분='0')

        self.XQ_t1302 = t1302(parent=self)

    def OnReceiveMessage(self, systemError, messageCode, message):
        # print(systemError, messageCode, message)
        pass

    def OnReceiveData(self, szTrCode, result):
        if szTrCode == 't8436':
            self.종목코드테이블 = result[0]
            self.종목코드테이블['컬럼'] = ">> " + self.종목코드테이블['단축코드'] + " : " + self.종목코드테이블['종목명']
            self.종목코드테이블 = self.종목코드테이블.sort_values(['단축코드', '종목명'], ascending=[True, True])
            self.comboBox.addItems(self.종목코드테이블['컬럼'].values)

        if szTrCode == 't1302':
            시간CTS, df = result
            self.model.update(df)
            for i in range(len(df.columns)):
                self.tableView.resizeColumnToContents(i)

    def inquiry(self):
        단축코드 = self.comboBox.currentText().strip()[3:9]
        조회건수 = self.lineEdit_cnt.text().strip().replace('-', '')

        self.XQ_t1302.Query(단축코드=단축코드,작업구분='1',시간='',건수=조회건수, 연속조회=False)


Ui_일자별주가조회, QtBaseClass_일자별주가조회 = uic.loadUiType(UI_DIR+"일자별주가조회.ui")
class 화면_일별주가(QDialog, Ui_일자별주가조회):
    def __init__(self, parent=None):
        super(화면_일별주가, self).__init__(parent)
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.setupUi(self)

        self.setWindowTitle('일자별 주가 조회')

        self.parent = parent

        self.model = PandasModel()
        self.tableView.setModel(self.model)

        self.columns = ['날짜', '시가', '고가', '저가', '종가', '전일대비구분', '전일대비', '등락율', '누적거래량', '거래증가율', '체결강도', '소진율', '회전율',
                   '외인순매수', '기관순매수', '종목코드', '누적거래대금', '개인순매수', '시가대비구분', '시가대비', '시가기준등락율', '고가대비구분', '고가대비',
                   '고가기준등락율', '저가대비구분', '저가대비', '저가기준등락율', '시가총액']

        self.result = []

        d = datetime.date.today()

        XQ = t8436(parent=self)
        XQ.Query(구분='0')

    def OnReceiveMessage(self, systemError, messageCode, message):
        # print(systemError, messageCode, message)
        pass

    def OnReceiveData(self, szTrCode, result):
        if szTrCode == 't8436':
            self.종목코드테이블 = result[0]
            self.종목코드테이블['컬럼'] = ">> " + self.종목코드테이블['단축코드'] + " : " + self.종목코드테이블['종목명']
            self.종목코드테이블 = self.종목코드테이블.sort_values(['단축코드', '종목명'], ascending=[True, True])
            self.comboBox.addItems(self.종목코드테이블['컬럼'].values)

        if szTrCode == 't1305':
            CNT, 날짜, IDX, df = result
            # print(CNT, 날짜, IDX)

            self.model.update(df)
            for i in range(len(df.columns)):
                self.tableView.resizeColumnToContents(i)

            if int(CNT) == int(self.조회건수):
                QTimer.singleShot(주문지연, lambda: self.inquiry_repeatly(result=result))
            else:
                # print("===END===")
                pass

    def inquiry_repeatly(self, result):
        CNT, 날짜, IDX, df = result
        self.XQ.Query(단축코드=self.단축코드, 일주월구분='1', 날짜=날짜, IDX=IDX, 건수=self.조회건수, 연속조회=True)

    def inquiry(self):
        self.단축코드 = self.comboBox.currentText()[3:9]
        self.조회건수 = self.lineEdit_date.text().strip().replace('-', '')

        self.XQ = t1305(parent=self)
        self.XQ.Query(단축코드=self.단축코드,일주월구분='1',날짜='',IDX='',건수=self.조회건수, 연속조회=False)


Ui_종목별투자자조회, QtBaseClass_종목별투자자조회 = uic.loadUiType(UI_DIR+"종목별투자자조회.ui")
class 화면_종목별투자자(QDialog, Ui_종목별투자자조회):
    def __init__(self, parent=None):
        super(화면_종목별투자자, self).__init__(parent)
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.setupUi(self)
        self.setWindowTitle('종목별 투자자 조회')
        self.parent = parent

        self.model = PandasModel()
        self.tableView.setModel(self.model)

        self.columns = ['일자', '종가', '전일대비구분', '전일대비', '등락율', '누적거래량', '사모펀드', '증권', '보험', '투신', '은행', '종금', '기금', '기타법인',
                       '개인', '등록외국인', '미등록외국인', '국가외', '기관', '외인계', '기타계']

        self.result = []

        d = datetime.date.today()
        self.lineEdit_date.setText(str(d))

        XQ = t8436(parent=self)
        XQ.Query(구분='0')

    def OnReceiveMessage(self, systemError, messageCode, message):
        # print(systemError, messageCode, message)
        pass

    def OnReceiveData(self, szTrCode, result):
        if szTrCode == 't8436':
            self.종목코드테이블 = result[0]
            self.종목코드테이블['컬럼'] = ">> " + self.종목코드테이블['단축코드'] + " : " + self.종목코드테이블['종목명']
            self.종목코드테이블 = self.종목코드테이블.sort_values(['단축코드', '종목명'], ascending=[True, True])
            self.comboBox.addItems(self.종목코드테이블['컬럼'].values)

        if szTrCode == 't1702':
            CTSIDX, CTSDATE, df = result
            self.model.update(df)
            for i in range(len(df.columns)):
                self.tableView.resizeColumnToContents(i)

    def Request(self, _repeat=0):
        종목코드 = self.lineEdit_code.text().strip()
        기준일자 = self.lineEdit_date.text().strip().replace('-','')

    def inquiry(self):
        단축코드 = self.comboBox.currentText()[3:9]
        조회건수 = self.lineEdit_date.text().strip().replace('-', '')

        XQ = t1702(parent=self)
        XQ.Query(종목코드=단축코드, 종료일자='', 금액수량구분='0', 매수매도구분='0', 누적구분='0', CTSDATE='', CTSIDX='')


class 화면_종목별투자자2(QDialog, Ui_종목별투자자조회):
    def __init__(self, parent=None):
        super(화면_종목별투자자2, self).__init__(parent)
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.setupUi(self)
        self.setWindowTitle('종목별 투자자 조회')
        self.parent = parent

        self.model = PandasModel()
        self.tableView.setModel(self.model)

        self.columns = []

        self.result = []

        d = datetime.date.today()
        self.lineEdit_date.setText(str(d))

        XQ = t8436(parent=self)
        XQ.Query(구분='0')

    def OnReceiveMessage(self, systemError, messageCode, message):
        # print(systemError, messageCode, message)
        pass

    def OnReceiveData(self, szTrCode, result):
        if szTrCode == 't8436':
            self.종목코드테이블 = result[0]
            self.종목코드테이블['컬럼'] = ">> " + self.종목코드테이블['단축코드'] + " : " + self.종목코드테이블['종목명']
            self.종목코드테이블 = self.종목코드테이블.sort_values(['단축코드', '종목명'], ascending=[True, True])
            self.comboBox.addItems(self.종목코드테이블['컬럼'].values)

        if szTrCode == 't1717':
            df = result[0]
            self.model.update(df)
            for i in range(len(df.columns)):
                self.tableView.resizeColumnToContents(i)

    def Request(self, _repeat=0):
        종목코드 = self.lineEdit_code.text().strip()
        기준일자 = self.lineEdit_date.text().strip().replace('-','')

    def inquiry(self):
        단축코드 = self.comboBox.currentText()[3:9]
        조회건수 = self.lineEdit_date.text().strip().replace('-', '')

        XQ = t1717(parent=self)
        XQ.Query(종목코드=단축코드,구분='0',시작일자='20170101',종료일자='20172131')


Ui_차트인덱스, QtBaseClass_차트인덱스 = uic.loadUiType(UI_DIR+"차트인덱스.ui")
class 화면_차트인덱스(QDialog, Ui_차트인덱스):
    def __init__(self, parent=None):
        super(화면_차트인덱스, self).__init__(parent)
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.setupUi(self)

        self.model = PandasModel()
        self.tableView.setModel(self.model)

        self.parent = parent

        self.columns = ['일자', '시간', '시가', '고가', '저가', '종가', '거래량', '지표값1', '지표값2', '지표값3', '지표값4', '지표값5', '위치']

        self.XQ_ChartIndex = ChartIndex(parent=self)
        XQ = t8436(parent=self)
        XQ.Query(구분='0')

    def OnReceiveMessage(self, systemError, messageCode, message):
        # print(systemError, messageCode, message)
        pass

    def OnReceiveData(self, szTrCode, result):
        if szTrCode == 't8436':
            self.종목코드테이블 = result[0]
            self.종목코드테이블['컬럼'] = ">> " + self.종목코드테이블['단축코드'] + " : " + self.종목코드테이블['종목명']
            self.종목코드테이블 = self.종목코드테이블.sort_values(['단축코드', '종목명'], ascending=[True, True])
            self.comboBox.addItems(self.종목코드테이블['컬럼'].values)

        if szTrCode == 'CHARTINDEX':
            식별자, 지표ID, 레코드갯수, 유효데이터컬럼갯수, self.df = result

            self.model.update(self.df)
            for i in range(len(self.df.columns)):
                self.tableView.resizeColumnToContents(i)

    def OnReceiveChartRealData(self, szTrCode, lst):
        if szTrCode == 'CHARTINDEX':
            식별자, result = lst
            지표ID, 레코드갯수, 유효데이터컬럼갯수, d = result
            lst = [[d['일자'],d['시간'],d['시가'],d['고가'],d['저가'],d['종가'],d['거래량'],d['지표값1'],d['지표값2'],d['지표값3'],d['지표값4'],d['지표값5'],d['위치']]]
            self.df = self.df.append(pd.DataFrame(lst, columns=self.columns), ignore_index=True)

            try:
                self.model.update(self.df)
                for i in range(len(self.df.columns)):
                    self.tableView.resizeColumnToContents(i)
            except Exception as e:
                pass

    def inquiry(self):
        지표명 = self.lineEdit_name.text()
        단축코드 =  self.comboBox.currentText()[3:9]
        요청건수 = self.lineEdit_cnt.text()
        실시간 = '1' if self.checkBox.isChecked() == True else '0'

        self.XQ_ChartIndex.Query(지표ID='', 지표명=지표명, 지표조건설정='', 시장구분='1', 주기구분='0', 단축코드=단축코드, 요청건수=요청건수, 단위='3', 시작일자='',
                 종료일자='', 수정주가반영여부='1', 갭보정여부='1', 실시간데이터수신자동등록여부=실시간)


Ui_종목검색, QtBaseClass_종목검색 = uic.loadUiType(UI_DIR+"종목검색.ui")
class 화면_종목검색(QDialog, Ui_종목검색):
    def __init__(self, parent=None):
        super(화면_종목검색, self).__init__(parent)
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.setupUi(self)

        self.model = PandasModel()
        self.tableView.setModel(self.model)

        self.parent = parent

    def OnReceiveData(self, szTrCode, result):
        if szTrCode == 't1833':
            종목검색수, df = result
            self.model.update(df)
            for i in range(len(df.columns)):
                self.tableView.resizeColumnToContents(i)

    def fileselect(self):
        pathname = os.path.dirname(sys.argv[0])
        RESDIR = "%s\\ADF\\" % os.path.abspath(pathname)

        fname = QFileDialog.getOpenFileName(self, 'Open file',RESDIR, "조검검색(*.adf)")
        self.lineEdit.setText(fname[0])

    def inquiry(self):
        filename = self.lineEdit.text()
        XQ = t1833(parent=self)
        XQ.Query(종목검색파일=filename)


Ui_e종목검색, QtBaseClass_e종목검색 = uic.loadUiType(UI_DIR+"e종목검색.ui")
class 화면_e종목검색(QDialog, Ui_e종목검색):
    def __init__(self, parent=None):
        super(화면_e종목검색, self).__init__(parent)
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.setupUi(self)

        self.model = PandasModel()
        self.tableView.setModel(self.model)

        self.parent = parent

    def OnReceiveData(self, szTrCode, result):
        if szTrCode == 't1857':
            검색종목수, 포착시간, 실시간키, df = result
            self.model.update(df)
            for i in range(len(df.columns)):
                self.tableView.resizeColumnToContents(i)

    def OnReceiveSearchRealData(self, szTrCode, result):
        if szTrCode == 't1857':
            print(result)

    def fileselect(self):
        pathname = os.path.dirname(sys.argv[0])
        RESDIR = "%s\\ACF\\" % os.path.abspath(pathname)

        fname = QFileDialog.getOpenFileName(self, 'Open file',RESDIR, "조검검색(*.acf)")
        self.lineEdit.setText(fname[0])

    def inquiry(self):
        filename = self.lineEdit.text()
        XQ = t1857(parent=self)
        XQ.Query(실시간구분='0',종목검색구분='F',종목검색입력값=filename)


Ui_호가창정보, QtBaseClass_호가창정보 = uic.loadUiType(UI_DIR+"실시간호가.ui")
class 화면_호가창정보(QDialog, Ui_호가창정보):
    def __init__(self, parent=None):
        super(화면_호가창정보, self).__init__(parent)
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.setupUi(self)
        self.parent = parent

        self.매도호가컨트롤 = [
            self.label_offerho1, self.label_offerho2, self.label_offerho3, self.label_offerho4, self.label_offerho5,
            self.label_offerho6, self.label_offerho7, self.label_offerho8, self.label_offerho9, self.label_offerho10
        ]

        self.매수호가컨트롤 = [
            self.label_bidho1, self.label_bidho2, self.label_bidho3, self.label_bidho4, self.label_bidho5,
            self.label_bidho6, self.label_bidho7, self.label_bidho8, self.label_bidho9, self.label_bidho10
        ]

        self.매도호가잔량컨트롤 = [
            self.label_offerrem1, self.label_offerrem2, self.label_offerrem3, self.label_offerrem4,
            self.label_offerrem5,
            self.label_offerrem6, self.label_offerrem7, self.label_offerrem8, self.label_offerrem9,
            self.label_offerrem10
        ]

        self.매수호가잔량컨트롤 = [
            self.label_bidrem1, self.label_bidrem2, self.label_bidrem3, self.label_bidrem4, self.label_bidrem5,
            self.label_bidrem6, self.label_bidrem7, self.label_bidrem8, self.label_bidrem9, self.label_bidrem10
        ]

        with sqlite3.connect(DATABASE) as conn:
            query = 'select 단축코드,종목명,ETF구분,구분 from 종목코드'
            df = pdsql.read_sql_query(query, con=conn)

        self.kospi_codes = df.query("구분=='1'")['단축코드'].values.tolist()
        self.kosdaq_codes = df.query("구분=='2'")['단축코드'].values.tolist()

        XQ = t8436(parent=self)
        XQ.Query(구분='0')

        self.kospi_askbid = H1_(parent=self)
        self.kosdaq_askbid = HA_(parent=self)

    def OnReceiveMessage(self, systemError, messageCode, message):
        # print(systemError, messageCode, message)
        pass

    def OnReceiveData(self, szTrCode, result):
        if szTrCode == 't8436':
            self.종목코드테이블 = result[0]
            self.종목코드테이블['컬럼'] = self.종목코드테이블['단축코드'] + " : " + self.종목코드테이블['종목명']
            self.종목코드테이블 = self.종목코드테이블.sort_values(['단축코드', '종목명'], ascending=[True, True])
            self.comboBox.addItems(self.종목코드테이블['컬럼'].values)

    def OnReceiveRealData(self, szTrCode, result):
        try:
            s = "%s:%s:%s" % (result['호가시간'][0:2],result['호가시간'][2:4],result['호가시간'][4:6])
            self.label_hotime.setText(s)

            for i in range(0,10):
                self.매도호가컨트롤[i].setText(result['매도호가'][i])
                self.매수호가컨트롤[i].setText(result['매수호가'][i])
                self.매도호가잔량컨트롤[i].setText(result['매도호가잔량'][i])
                self.매수호가잔량컨트롤[i].setText(result['매수호가잔량'][i])

            self.label_offerremALL.setText(result['총매도호가잔량'])
            self.label_bidremALL.setText(result['총매수호가잔량'])
            self.label_donsigubun.setText(result['동시호가구분'])
            self.label_alloc_gubun.setText(result['배분적용구분'])
        except Exception as e:
            pass

    def AddCode(self):
        종목코드 = self.comboBox.currentText().strip()[0:6]

        self.kospi_askbid.UnadviseRealData()
        self.kosdaq_askbid.UnadviseRealData()

        if 종목코드 in self.kospi_codes:
            self.kospi_askbid.AdviseRealData(종목코드=종목코드)
        if 종목코드 in self.kosdaq_codes:
            self.kosdaq_askbid.AdviseRealData(종목코드=종목코드)


Ui_실시간정보, QtBaseClass_실시간정보 = uic.loadUiType(UI_DIR+"실시간주가.ui")
class 화면_실시간정보(QDialog, Ui_실시간정보):
    def __init__(self, parent=None):
        super(화면_실시간정보, self).__init__(parent)
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.setupUi(self)
        self.parent = parent

        self.kospi_real = S3_(parent=self)

    def OnReceiveRealData(self, szTrCode, result):
        try:
            str = '{}:{} - {}--{}\r'.format(result['체결시간'], result['단축코드'], result['현재가'], result['체결량'])
            self.textBrowser.append(str)
        except Exception as e:
            pass

    def AddCode(self):
        종목코드 = self.comboBox.currentText().strip()
        self.comboBox.addItems([종목코드])
        self.kospi_real.AdviseRealData(종목코드=종목코드)

    def RemoveCode(self):
        종목코드 = self.comboBox.currentText().strip()
        self.kospi_real.UnadviseRealDataWithKey(종목코드=종목코드)


Ui_뉴스, QtBaseClass_뉴스 = uic.loadUiType(UI_DIR+"뉴스.ui")
class 화면_뉴스(QDialog, Ui_뉴스):
    def __init__(self, parent=None):
        super(화면_뉴스, self).__init__(parent)
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.setupUi(self)

        self.parent = parent

        self.news = NWS(parent=self)

    def OnReceiveRealData(self, szTrCode, result):
        str = '{}:{} - {}\r'.format(result['날짜'], result['시간'], result['제목'])
        try:
            self.textBrowser.append(str)
        except Exception as e:
            pass

    def AddCode(self):
        self.news.AdviseRealData()

    def RemoveCode(self):
        self.news.UnadviseRealData()


Ui_주문테스트, QtBaseClass_주문테스트 = uic.loadUiType(UI_DIR+"주문테스트.ui")
class 화면_주문테스트(QDialog, Ui_주문테스트):
    def __init__(self, parent=None):
        super(화면_주문테스트, self).__init__(parent)
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.setupUi(self)
        self.parent = parent

        self.connection = self.parent.connection

        # 계좌정보 불러오기
        nCount = self.connection.ActiveX.GetAccountListCount()
        for i in range(nCount):
            self.comboBox.addItem(self.connection.ActiveX.GetAccountList(i))

        self.QA_CSPAT00600 = CSPAT00600(parent=self)

        self.setup()

    def setup(self):
        self.XR_SC1 = SC1(parent=self)
        self.XR_SC1.AdviseRealData()
        self.주문번호리스트 = []

    def OnReceiveMessage(self, systemError, messageCode, message):
        self.textEdit.insertPlainText("systemError:[%s] messageCode:[%s] message:[%s]\r" % (systemError, messageCode, message))

    def OnReceiveData(self, szTrCode, result):
        if szTrCode == 'CSPAT00600':
            df, df1 = result
            주문번호 = df1['주문번호'].values[0]
            self.textEdit.insertPlainText("주문번호 : %s\r" % 주문번호)
            if 주문번호 != '0':
                # 주문번호처리
                self.주문번호리스트.append(str(주문번호))

    def OnReceiveRealData(self, szTrCode, result):
        try:
            self.textEdit.insertPlainText(szTrCode+'\r')
            self.textEdit.insertPlainText(str(result)+'\r')
        except Exception as e:
            pass

        if szTrCode == 'SC1':
            체결시각 = result['체결시각']
            단축종목번호 = result['단축종목번호'].strip().replace('A','')
            종목명 = result['종목명']
            매매구분 = result['매매구분']
            주문번호 = result['주문번호']
            체결번호 = result['체결번호']
            주문수량 = result['주문수량']
            주문가격 = result['주문가격']
            체결수량 = result['체결수량']
            체결가격 = result['체결가격']
            주문평균체결가격 = result['주문평균체결가격']
            주문계좌번호 = result['주문계좌번호']

            # 내가 주문한 것이 맞을 경우 처리
            if 주문번호 in self.주문번호리스트:
                s = "[%s] %s %s %s %s %s %s %s %s %s %s %s" % (szTrCode,체결시각,단축종목번호,매매구분,주문번호,체결번호,주문수량,주문가격,체결수량,체결가격,주문평균체결가격,주문계좌번호)
                try:
                    self.textEdit.insertPlainText(s + '\r')
                except Exception as e:
                    pass

                일자 = "{:%Y-%m-%d}".format(datetime.datetime.now())
                with sqlite3.connect(DATABASE) as conn:
                    query = 'insert into 거래결과(로봇명, UUID, 일자, 체결시각, 단축종목번호, 종목명, 매매구분, 주문번호, 체결번호, 주문수량, 주문가격, 체결수량, 체결가격, 주문평균체결가격) values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)'
                    data = ['주문테스트', '주문테스트-UUID', 일자, 체결시각, 단축종목번호, 종목명, 매매구분, 주문번호, 체결번호, 주문수량, 주문가격, 체결수량, 체결가격, 주문평균체결가격]
                    cursor = conn.cursor()
                    cursor.execute(query, data)
                    conn.commit()

    def Order(self):
        계좌번호 = self.comboBox.currentText().strip()
        비밀번호 = self.lineEdit_pwd.text().strip()
        종목코드 = self.lineEdit_code.text().strip()
        주문가 = self.lineEdit_price.text().strip()
        주문수량 = self.lineEdit_amt.text().strip()
        매매구분 = self.lineEdit_bs.text().strip()
        호가유형 = self.lineEdit_hoga.text().strip()
        신용거래 = self.lineEdit_sin.text().strip()
        주문조건 = self.lineEdit_jogun.text().strip()

        self.QA_CSPAT00600.Query(계좌번호=계좌번호, 입력비밀번호=비밀번호, 종목번호=종목코드, 주문수량=주문수량, 주문가=주문가, 매매구분=매매구분, 호가유형코드=호가유형, 신용거래코드=신용거래, 주문조건구분=주문조건)


Ui_외부신호2eBEST, QtBaseClass_외부신호2eBEST = uic.loadUiType(UI_DIR+"외부신호2eBEST.ui")
class 화면_외부신호2eBEST(QDialog, Ui_외부신호2eBEST):
    def __init__(self, parent=None):
        super(화면_외부신호2eBEST, self).__init__(parent)
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.setupUi(self)
        self.parent = parent

        self.pathname = os.path.dirname(sys.argv[0])
        self.file = "%s\\" % os.path.abspath(self.pathname)

        self.매도 = 1
        self.매수 = 2
        self.매수방법 = '00'
        self.매도방법 = '00'
        self.조건없음 = 0
        self.조건IOC = 1
        self.조건FOK = 2

        self.신용거래코드 = '000'

        self.주문번호리스트 = []
        self.QA_CSPAT00600 = CSPAT00600(parent=self)
        self.XR_SC1 = SC1(parent=self)
        self.XR_SC1.AdviseRealData()

        self.connection = self.parent.connection

        # 계좌정보 불러오기
        nCount = self.connection.ActiveX.GetAccountListCount()
        for i in range(nCount):
            self.comboBox.addItem(self.connection.ActiveX.GetAccountList(i))

    def OnReceiveMessage(self, systemError, messageCode, message):
        s = "\r%s %s %s\r" % (systemError, messageCode, message)
        try:
            self.plainTextEdit.insertPlainText(s)
        except Exception as e:
            pass

    def OnReceiveData(self, szTrCode, result):
        if szTrCode == 'CSPAT00600':
            df, df1 = result
            주문번호 = df1['주문번호'].values[0]
            if 주문번호 != '0':
                self.주문번호리스트.append(str(주문번호))
                s = "주문번호 : %s\r" % 주문번호
                try:
                    self.plainTextEdit.insertPlainText(s)
                except Exception as e:
                    pass

    def OnReceiveRealData(self, szTrCode, result):
        if szTrCode == 'SC1':
            체결시각 = result['체결시각']
            단축종목번호 = result['단축종목번호'].strip().replace('A','')
            종목명 = result['종목명']
            매매구분 = result['매매구분']
            주문번호 = result['주문번호']
            체결번호 = result['체결번호']
            주문수량 = result['주문수량']
            주문가격 = result['주문가격']
            체결수량 = result['체결수량']
            체결가격 = result['체결가격']
            주문평균체결가격 = result['주문평균체결가격']
            주문계좌번호 = result['주문계좌번호']

            # 내가 주문한 것이 체결된 경우 처리
            if 주문번호 in self.주문번호리스트:
                s = "\r주문체결[%s] : %s %s %s %s %s %s %s %s %s %s %s\r" % (szTrCode,체결시각,단축종목번호,매매구분,주문번호,체결번호,주문수량,주문가격,체결수량,체결가격,주문평균체결가격,주문계좌번호)
                try:
                    self.plainTextEdit.insertPlainText(s)
                except Exception as e:
                    pass

                일자 = "{:%Y-%m-%d}".format(datetime.datetime.now())
                with sqlite3.connect(DATABASE) as conn:
                    query = 'insert into 거래결과(로봇명, UUID, 일자, 체결시각, 단축종목번호, 종목명, 매매구분, 주문번호, 체결번호, 주문수량, 주문가격, 체결수량, 체결가격, 주문평균체결가격) values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)'
                    data = ['툴박스2EBEST', '툴박스2EBEST-UUID', 일자, 체결시각, 단축종목번호, 종목명, 매매구분, 주문번호, 체결번호, 주문수량, 주문가격, 체결수량, 체결가격, 주문평균체결가격]
                    cursor = conn.cursor()
                    cursor.execute(query, data)
                    conn.commit()


    def OnReadFile(self, line):
        try:
            self.plainTextEdit.insertPlainText("\r>> " +line.strip() + '\r')
        except Exception as e:
            pass

        lst = line.strip().split(',')

        try:
            시각, 종류, 단축코드, 가격, 수량 = lst
            가격 = int(가격)
            수량 = int(수량)

            if 종류 == '매수':
                self.QA_CSPAT00600.Query(계좌번호=self.계좌번호, 입력비밀번호=self.비밀번호, 종목번호=단축코드, 주문수량=수량, 주문가=가격, 매매구분=self.매수, 호가유형코드=self.매수방법, 신용거래코드=self.신용거래코드, 주문조건구분=self.조건없음)
            if 종류 == '매도':
                self.QA_CSPAT00600.Query(계좌번호=self.계좌번호, 입력비밀번호=self.비밀번호, 종목번호=단축코드, 주문수량=수량, 주문가=가격, 매매구분=self.매도, 호가유형코드=self.매도방법, 신용거래코드=self.신용거래코드, 주문조건구분=self.조건없음)
        except Exception as e:
            pass

    def fileselect(self):
        ret = QFileDialog.getOpenFileName(self, 'Open file',self.file, "CSV,TXT(*.csv;*.txt)")
        self.file = ret[0]
        self.lineEdit.setText(self.file)

    def StartWatcher(self):
        self.계좌번호 = self.comboBox.currentText().strip()
        self.비밀번호 = self.lineEdit_pwd.text().strip()

        self.fw = FileWatcher(filename=self.file, callback=self.OnReadFile, encoding='utf-8')
        self.fw.start()


Ui_거래결과, QtBaseClass_거래결과 = uic.loadUiType(UI_DIR+"거래결과.ui")
class 화면_거래결과(QDialog, Ui_거래결과):
    def __init__(self, parent=None):
        super(화면_거래결과, self).__init__(parent)
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.setupUi(self)
        self.setWindowTitle('거래결과 조회')
        self.parent = parent

        self.model = PandasModel()
        self.tableView.setModel(self.model)

        self.columns = []

        with sqlite3.connect(DATABASE) as conn:
            query = "select distinct 로봇명 from 거래결과 order by 로봇명"
            df = pdsql.read_sql_query(query, con=conn)
            for name in df['로봇명'].values.tolist():
                self.comboBox.addItem(name)

    def inquiry(self):
        로봇명 = self.comboBox.currentText().strip()
        with sqlite3.connect(DATABASE) as conn:
            query = """
                select 로봇명, UUID, 일자, 체결시각, 단축종목번호, 종목명, 매매구분, 주문번호, 체결번호, 주문수량, 주문가격, 체결수량, 체결가격, 주문평균체결가격 
                from 거래결과
                where  로봇명='%s'
                order by 일자, 체결시각
            """ % 로봇명
            df = pdsql.read_sql_query(query, con=conn)

            self.model.update(df)
            for i in range(len(df.columns)):
                self.tableView.resizeColumnToContents(i)


Ui_버전, QtBaseClass_버전 = uic.loadUiType(UI_DIR+"버전.ui")
class 화면_버전(QDialog, Ui_버전):
    def __init__(self, parent=None):
        super(화면_버전, self).__init__(parent)
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.setupUi(self)
        self.setWindowTitle('버전')
        self.parent = parent

        self.model = PandasModel()
        self.tableView.setModel(self.model)

        df = DataFrame(data=프로그램정보,columns=['A','B'])

        self.model.update(df)
        for i in range(len(df.columns)):
            self.tableView.resizeColumnToContents(i)

########################################################################################################################

########################################################################################################################
class Plot_Worker(QThread):

    finished = pyqtSignal(dict)

    def run(self):

        while True:
            data = {}

            for actval in cm_call_actval:
                data[actval] = self.get_data_infos(actval)

            self.finished.emit(data)
            self.msleep(500)

    def get_data_infos(self, actval):

        try:

            index = cm_call_actval.index(actval)

            call_curve_data = df_plotdata_cm_call.iloc[index].values.tolist()
            put_curve_data = df_plotdata_cm_put.iloc[index].values.tolist()

            if comboindex == 2:

                curve1_data = df_plotdata_kp200.iloc[0].values.tolist()
                curve2_data = df_plotdata_fut.iloc[0].values.tolist()

                return call_curve_data, put_curve_data, curve1_data, curve2_data

            elif comboindex == 1:

                curve1_data = df_plotdata_cm_call_volume.iloc[0].values.tolist()
                curve2_data = df_plotdata_cm_put_volume.iloc[0].values.tolist()
                curve3_data = df_plotdata_cm_volume_cha.iloc[0].values.tolist()

                return call_curve_data, put_curve_data, curve1_data, curve2_data, curve3_data

            else:

                curve1_data = df_plotdata_cm_call_oi.iloc[0].values.tolist()
                curve2_data = df_plotdata_cm_put_oi.iloc[0].values.tolist()
                curve3_data = df_plotdata_cm_oi_cha.iloc[0].values.tolist()

                return call_curve_data, put_curve_data, curve1_data, curve2_data, curve3_data
        except:

            if comboindex == 2:

                return None, None, None, None
            else:
                return None, None, None, None, None

########################################################################################################################

########################################################################################################################
class t8415_Call_Worker(QThread):

    finished = pg.QtCore.Signal(object)

    def run(self):
        while True:

            data = cm_call_t8415_count
            print('t8416 call', data)

            self.finished.emit(data)
            self.msleep(1100)
########################################################################################################################

########################################################################################################################
class t8415_Put_Worker(QThread):

    finished = pg.QtCore.Signal(object)

    def run(self):
        while True:

            data = cm_put_t8415_count
            print('t8416 put', data)

            self.finished.emit(data)
            self.msleep(1100)
########################################################################################################################

########################################################################################################################
class t8416_Call_Worker(QThread):

    finished = pg.QtCore.Signal(object)

    def run(self):
        while True:

            data = cm_call_t8416_count
            print('t8416 call', data)

            self.finished.emit(data)
            self.msleep(1100)
########################################################################################################################

########################################################################################################################
class t8416_Put_Worker(QThread):

    finished = pg.QtCore.Signal(object)

    def run(self):
        while True:

            data = cm_put_t8416_count
            print('t8416 put', data)

            self.finished.emit(data)
            self.msleep(1100)
########################################################################################################################

########################################################################################################################
class t8416_NM_Call_Worker(QThread):

    finished = pg.QtCore.Signal(object)

    def run(self):
        while True:

            data = nm_call_t8416_count
            print('t8416 nm call', data)

            self.finished.emit(data)
            self.msleep(1100)
########################################################################################################################

########################################################################################################################
class t8416_NM_Put_Worker(QThread):

    finished = pg.QtCore.Signal(object)

    def run(self):
        while True:

            data = nm_put_t8416_count
            print('t8416 nm put', data)

            self.finished.emit(data)
            self.msleep(1100)

########################################################################################################################
# 당월물 옵션전광판 class
########################################################################################################################
Ui_당월물옵션전광판, QtBaseClass_당월물옵션전광판 = uic.loadUiType(UI_DIR+"당월물옵션전광판.ui")

class 화면_당월물옵션전광판(QDialog, Ui_당월물옵션전광판):
    def __init__(self, parent=None):
        super(화면_당월물옵션전광판, self).\
            __init__(parent, flags=Qt.WindowMinimizeButtonHint | Qt.WindowMaximizeButtonHint | Qt.WindowCloseButtonHint)
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.setupUi(self)

        global cm_option_title

        cm_option_title = '당월물 선물옵션 전광판 ' + '(' + today_str_title + ')'
        self.setWindowTitle(cm_option_title)

        self.parent = parent

        #self.timer = QTimer(self)
        #self.timer.timeout.connect(self.timeout)
        '''
        self.t8415_callworker = t8415_Call_Worker()
        self.t8415_callworker.finished.connect(self.t8415_call_request)

        self.t8415_putworker = t8415_Put_Worker()
        self.t8415_putworker.finished.connect(self.t8415_put_request)
        '''
        self.t8416_callworker = t8416_Call_Worker()
        self.t8416_callworker.finished.connect(self.t8416_call_request)

        self.t8416_putworker = t8416_Put_Worker()
        self.t8416_putworker.finished.connect(self.t8416_put_request)

        self.plot_worker = Plot_Worker()
        self.plot_worker.finished.connect(self.update_plot)

        # call tablewidget 초기화
        self.tableWidget_call.setRowCount(nRowCount)
        self.tableWidget_call.setColumnCount(Option_column.OID.value + 1)
        self.tableWidget_call.setHorizontalHeaderLabels(['▲', '행사가', '↑/↓', '기준가', '월저', '월고', '전저', '전고', 
        '종가 √', '피봇 √', '시가 √', '시가갭', '저가', '현재가', '고가', '대비', '진폭', '∑(미결or거래량)', 'OIΔ'])
        self.tableWidget_call.verticalHeader().setVisible(False)
        self.tableWidget_call.clearContents()

        global call_ckbox, put_ckbox

        call_ckbox = []

        for i in range(nRowCount):
            call_ckbox.append(QCheckBox())
            self.tableWidget_call.setCellWidget(i, 0, call_ckbox[i])

        self.tableWidget_call.resizeColumnsToContents()
        self.tableWidget_call.setColumnWidth(0, 15)

        # put tablewidget 초기화
        self.tableWidget_put.setRowCount(nRowCount)
        self.tableWidget_put.setColumnCount(Option_column.OID.value + 1)
        self.tableWidget_put.setHorizontalHeaderLabels(['▼', '행사가', '↑/↓', '기준가', '월저', '월고', '전저', '전고', 
        '종가 √', '피봇 √', '시가 √', '시가갭', '저가', '현재가', '고가', '대비', '진폭', '∑(미결or거래량)', 'OIΔ'])
        self.tableWidget_put.verticalHeader().setVisible(False)
        self.tableWidget_put.clearContents()

        put_ckbox = []

        for i in range(nRowCount):
            put_ckbox.append(QCheckBox())
            self.tableWidget_put.setCellWidget(i, 0, put_ckbox[i])

        self.tableWidget_put.resizeColumnsToContents()
        self.tableWidget_put.setColumnWidth(0, 15)

        # Quote tablewidget 초기화
        self.tableWidget_quote.setRowCount(1)
        self.tableWidget_quote.setColumnCount(Quote_column.호가종합.value)
        self.tableWidget_quote.setHorizontalHeaderLabels(['C-MSCC', 'C-MDCC', 'C-MSCR', 'C-MDCR',
                                                          'P-MSCC', 'P-MDCC', 'P-MSCR', 'P-MDCR', '콜건수비', '콜잔량비',
                                                          '풋건수비', '풋잔량비', '호가 ∑(CRΔ/RRΔ)'])
        self.tableWidget_quote.verticalHeader().setVisible(False)
        header = self.tableWidget_quote.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeToContents)
        header.setSectionResizeMode(12, QHeaderView.Stretch)
        self.tableWidget_quote.verticalHeader().setStretchLastSection(True)
        self.tableWidget_quote.clearContents()

        # 선물 tablewidget 초기화
        self.tableWidget_fut.setRowCount(3)
        self.tableWidget_fut.setColumnCount(Futures_column.OID.value + 1)

        self.tableWidget_fut.setVerticalHeaderLabels(['CME', 'FUT', 'KP200'])
        self.tableWidget_fut.setHorizontalHeaderLabels(
            ['↑/↓', 'MSC', 'MDC', 'MSR', 'MDR', 'CR', 'RR', '전저', '전고', '종가', '피봇', '시가', '시가갭', '저가',
             '현재가', '고가', '대비', '진폭', '거래량', 'VR', 'OI', 'OIΔ'])

        # 수급 tablewidget 초기화
        self.tableWidget_supply.setRowCount(1)
        self.tableWidget_supply.setColumnCount(Supply_column.프로그램.value + 1)
        self.tableWidget_supply.setHorizontalHeaderLabels(['외인선물', '프로그램', '외인현물', '개인선물', '기관선물', '∑(선물/현물)'])
        self.tableWidget_supply.verticalHeader().setVisible(False)
        header = self.tableWidget_supply.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeToContents)
        header.setSectionResizeMode(5, QHeaderView.Stretch)
        self.tableWidget_supply.verticalHeader().setStretchLastSection(True)
        self.tableWidget_supply.clearContents()

        self.comboBox1.addItems(['O-Plot', 'V-Plot', 'F-Plot'])
        self.comboBox1.currentIndexChanged.connect(self.selectionChanged)

        self.상태그림 = ['▼', '▬', '▲']
        self.상태문자 = ['매도', '대기', '매수']
        self.특수문자 = ['☆', '★', '※', '○', '●', '◎', '√', '↗', '↘', '↑', '↓', '♣', '♠', '♥', '◆', 'Δ', '【', '】']

        # Enable antialiasing for prettier plots
        pg.setConfigOptions(antialias=True)

        self.Plot_Fut.enableAutoRange('y', True)
        self.Plot_Fut.plotItem.showGrid(True, True, 0.5)
        self.Plot_Fut.setRange(xRange=[0, 395 + 1], padding=0)

        global time_line_fut, fut_curve, kp200_curve
        global fut_jl_line, fut_jh_line, fut_pivot_line, volume_base_line
        global cm_call_volume_curve, cm_put_volume_curve, cm_volume_cha_curve
        global cm_call_oi_curve, cm_put_oi_curve, cm_oi_cha_curve
        #global cm_volume_plus_curve, cm_volume_minus_curve

        time_line_fut = self.Plot_Fut.addLine(x=0, y=None, pen=tpen)

        fut_jl_line = self.Plot_Fut.addLine(x=None, pen=fut_jl_pen)
        fut_jh_line = self.Plot_Fut.addLine(x=None, pen=fut_jh_pen)
        volume_base_line = self.Plot_Fut.addLine(x=None, pen=gpen)
        fut_pivot_line = self.Plot_Fut.addLine(x=None, pen=fut_pvt_pen)

        kp200_curve = self.Plot_Fut.plot(pen=gpen)
        fut_curve = self.Plot_Fut.plot(pen=futpen)

        cm_call_volume_curve = self.Plot_Fut.plot(pen=rpen)
        cm_put_volume_curve = self.Plot_Fut.plot(pen=bpen)
        cm_volume_cha_curve = self.Plot_Fut.plot(pen=gpen)
        #cm_volume_plus_curve = self.Plot_Fut.plot(pen=magenta_pen)
        #cm_volume_minus_curve = self.Plot_Fut.plot(pen=aqua_pen)

        cm_call_oi_curve = self.Plot_Fut.plot(pen=rpen)
        cm_put_oi_curve = self.Plot_Fut.plot(pen=bpen)
        cm_oi_cha_curve = self.Plot_Fut.plot(pen=gpen)

        self.Plot_Opt.enableAutoRange('y', True)
        self.Plot_Opt.plotItem.showGrid(True, True, 0.5)
        self.Plot_Opt.setRange(xRange=[0, 395 + 1], padding=0)

        global time_line, mv_line, call_curve, put_curve

        time_line = self.Plot_Opt.addLine(x=0, y=None, pen=tpen)

        for i in range(9):
            mv_line.append(self.Plot_Opt.addLine(x=None, pen=mvpen))
            call_curve.append(self.Plot_Opt.plot(pen=rpen))
            put_curve.append(self.Plot_Opt.plot(pen=bpen))

        # init value & clear color
        item = QTableWidgetItem("{0:0.2f}".format(0.0))
        item.setTextAlignment(Qt.AlignCenter)
        self.tableWidget_fut.setItem(0, Futures_column.종가.value, item)

        item = QTableWidgetItem("{0:0.2f}".format(0.0))
        item.setTextAlignment(Qt.AlignCenter)
        self.tableWidget_fut.setItem(1, Futures_column.종가.value, item)

        item = QTableWidgetItem("{0:0.2f}".format(0.0))
        item.setTextAlignment(Qt.AlignCenter)
        self.tableWidget_fut.setItem(2, Futures_column.종가.value, item)

        item = QTableWidgetItem("{0:0.2f}".format(0.0))
        item.setTextAlignment(Qt.AlignCenter)
        self.tableWidget_fut.setItem(0, Futures_column.시가.value, item)

        item = QTableWidgetItem("{0:0.2f}".format(0.0))
        item.setTextAlignment(Qt.AlignCenter)
        self.tableWidget_fut.setItem(1, Futures_column.시가.value, item)

        item = QTableWidgetItem("{0:0.2f}".format(0.0))
        item.setTextAlignment(Qt.AlignCenter)
        self.tableWidget_fut.setItem(2, Futures_column.시가.value, item)

        item = QTableWidgetItem("{0:0.2f}".format(0.0))
        item.setTextAlignment(Qt.AlignCenter)
        self.tableWidget_fut.setItem(0, Futures_column.저가.value, item)

        item = QTableWidgetItem("{0:0.2f}".format(0.0))
        item.setTextAlignment(Qt.AlignCenter)
        self.tableWidget_fut.setItem(1, Futures_column.저가.value, item)

        item = QTableWidgetItem("{0:0.2f}".format(0.0))
        item.setTextAlignment(Qt.AlignCenter)
        self.tableWidget_fut.setItem(2, Futures_column.저가.value, item)

        item = QTableWidgetItem("{0:0.2f}".format(0.0))
        item.setTextAlignment(Qt.AlignCenter)
        self.tableWidget_fut.setItem(0, Futures_column.현재가.value, item)
        self.tableWidget_fut.item(0, Futures_column.현재가.value).setBackground(QBrush(옅은회색))

        item = QTableWidgetItem("{0:0.2f}".format(0.0))
        item.setTextAlignment(Qt.AlignCenter)
        self.tableWidget_fut.setItem(1, Futures_column.현재가.value, item)
        self.tableWidget_fut.item(1, Futures_column.현재가.value).setBackground(QBrush(옅은회색))

        item = QTableWidgetItem("{0:0.2f}".format(0.0))
        item.setTextAlignment(Qt.AlignCenter)
        self.tableWidget_fut.setItem(2, Futures_column.현재가.value, item)
        self.tableWidget_fut.item(2, Futures_column.현재가.value).setBackground(QBrush(옅은회색))

        item = QTableWidgetItem("{0:0.2f}".format(0.0))
        item.setTextAlignment(Qt.AlignCenter)
        self.tableWidget_fut.setItem(0, Futures_column.고가.value, item)

        item = QTableWidgetItem("{0:0.2f}".format(2.0))
        item.setTextAlignment(Qt.AlignCenter)
        self.tableWidget_fut.setItem(1, Futures_column.고가.value, item)

        item = QTableWidgetItem("{0:0.2f}".format(0.0))
        item.setTextAlignment(Qt.AlignCenter)
        self.tableWidget_fut.setItem(2, Futures_column.고가.value, item)

        item = QTableWidgetItem("{0}".format(0))
        item.setTextAlignment(Qt.AlignCenter)
        self.tableWidget_fut.setItem(0, Futures_column.거래량.value, item)

        item = QTableWidgetItem("{0}".format(0))
        item.setTextAlignment(Qt.AlignCenter)
        self.tableWidget_fut.setItem(1, Futures_column.거래량.value, item)

        self.tableWidget_fut.resizeColumnsToContents()

        for i in range(nRowCount):
            for j in range(self.tableWidget_call.columnCount() - 1):

                item = QTableWidgetItem("{0}".format(''))
                self.tableWidget_call.setItem(i, j + 1, item)
                self.tableWidget_call.item(i, j + 1).setBackground(QBrush(검정색))

        for i in range(nRowCount):
            for j in range(self.tableWidget_put.columnCount() - 1):

                item = QTableWidgetItem("{0}".format(''))
                self.tableWidget_put.setItem(i, j + 1, item)
                self.tableWidget_put.item(i, j + 1).setBackground(QBrush(검정색))

        self.label_kospi.setText("KOSPI : 0(0.0%)")
        self.label_kospi.setStyleSheet('background-color: yellow ; color: black')
        self.label_kosdaq.setText("KOSDAQ : 0(0.0%)")
        self.label_kosdaq.setStyleSheet('background-color: yellow ; color: black')

        self.label_samsung.setText("SAMSUNG : 0(0.0%)")
        self.label_samsung.setStyleSheet('background-color: yellow ; color: black')
        self.label_mobis.setText("MOBIS : 0(0.0%)")
        self.label_mobis.setStyleSheet('background-color: yellow ; color: black')
        self.label_naver.setText("NAVER : 0(0.0%)")
        self.label_naver.setStyleSheet('background-color: yellow ; color: black')

        self.label_msg.setText("★ 주요 시그날 알림창 ★")
        self.label_msg.setStyleSheet('background-color: lime; color: blue')

        self.label_atm.setText("[Basis] [양합/양차] [∑COI:∑POI]")
        self.label_atm.setStyleSheet('background-color: yellow; color: black')

        self.color_flag = True
        self.alternate_flag = True

        global call_node_state, put_node_state

        call_node_state = {'기준가': False, '월저': False, '월고': False, '전저': False, '전고': False, '종가': True, '피봇': True, '시가': True, '대비': False, '미결': False, '미결증감': False}
        put_node_state = {'기준가': False, '월저': False, '월고': False, '전저': False, '전고': False, '종가': True, '피봇': True, '시가': True, '대비': False, '미결': False, '미결증감': False}

        global coreval

        list_low1 = []
        list_low2 = []
        list_low3 = []
        list_low4 = []
        list_low5 = []

        list_high1 = []
        list_high2 = []
        list_high3 = []
        list_high4 = []
        list_high5 = []

        for i in range(len(의미가)):

            list_low5.append(의미가[i] - 0.05)
            list_low4.append(의미가[i] - 0.04)
            list_low3.append(의미가[i] - 0.03)
            list_low2.append(의미가[i] - 0.02)
            list_low1.append(의미가[i] - 0.01)

            list_high1.append(의미가[i] + 0.01)
            list_high2.append(의미가[i] + 0.02)
            list_high3.append(의미가[i] + 0.03)
            list_high4.append(의미가[i] + 0.04)
            list_high5.append(의미가[i] + 0.05)

        coreval = 의미가 + list_low1 + list_low2 + list_low3 + list_low4 + list_low5 + list_high1 + list_high2 + list_high3 + list_high4 + list_high5
        coreval.sort()

        # 컬럼 헤더 click시 Event 처리용.
        call_h_header = self.tableWidget_call.horizontalHeader()
        call_h_header.sectionClicked.connect(self._call_horizontal_header_clicked)

        put_h_header = self.tableWidget_put.horizontalHeader()
        put_h_header.sectionClicked.connect(self._put_horizontal_header_clicked)

        call_v_header = self.tableWidget_call.verticalHeader()
        call_v_header.sectionClicked.connect(self._call_vertical_header_clicked)

        put_v_header = self.tableWidget_put.verticalHeader()
        put_v_header.sectionClicked.connect(self._put_vertical_header_clicked)

        self.tableWidget_call.cellClicked.connect(self._calltable_cell_clicked)
        self.tableWidget_put.cellClicked.connect(self._puttable_cell_clicked)

        self.tableWidget_call.verticalScrollBar().valueChanged.connect(self._calltable_vertical_scroll_position)
        self.tableWidget_put.verticalScrollBar().valueChanged.connect(self._puttable_vertical_scroll_position)

        # QuoteView 시그날/슬롯
        self.checkBox_quoteview.stateChanged.connect(self.quoteview_state_changed)

        # 지수실시간 요청 시그날/슬롯
        #self.checkBox_vplot.stateChanged.connect(self.vplot_state_changed)

        self.IJ = IJ_(parent=self)
        self.S3 = S3_(parent=self)
        self.BM = BM_(parent=self)
        self.PM = PM_(parent=self)

        self.jif = JIF(parent=self)
        self.jif.AdviseRealData('0')
        print('장운영정보를 요청합니다.')

        dt = datetime.datetime.now()
        current_str = dt.strftime('%H:%M:%S')

        if 4 < int(current_str[0:2]) < 16:
            pass
        else:
            #self.timer.start(1000)
            pass

        if int(current_str[0:2]) < 12:
            str = '[{0:02d}:{1:02d}:{2:02d}] ♣♣♣ Good Morning! Have a Good Day ♣♣♣\r'.format(dt.hour, dt.minute, dt.second)
        else:
            str = '[{0:02d}:{1:02d}:{2:02d}] ♣♣♣ Good Afternoon! Have a Good Day ♣♣♣\r'.format(dt.hour, dt.minute, dt.second)
        self.textBrowser.append(str)

    def selectionChanged(self):

        global comboindex
        global fut_curve, kp200_curve
        global cm_call_volume_curve, cm_put_volume_curve, cm_volume_cha_curve
        global cm_call_oi_curve, cm_put_oi_curve, cm_oi_cha_curve

        txt = self.comboBox1.currentText()
        comboindex = self.comboBox1.currentIndex()

        if comboindex == 2:

            cm_call_volume_curve.clear()
            cm_put_volume_curve.clear()
            cm_volume_cha_curve.clear()

            cm_call_oi_curve.clear()
            cm_put_oi_curve.clear()
            cm_oi_cha_curve.clear()

            for i in range(nCount_cm_option_pairs):
                temp = format(df_cm_call.iloc[i]['미결'], ',')

                item = QTableWidgetItem(temp)
                item.setTextAlignment(Qt.AlignCenter)
                self.tableWidget_call.setItem(i, Option_column.OI.value, item)

                temp = format(df_cm_put.iloc[i]['미결'], ',')

                item = QTableWidgetItem(temp)
                item.setTextAlignment(Qt.AlignCenter)
                self.tableWidget_put.setItem(i, Option_column.OI.value, item)

            call_temp = format(df_cm_call['미결'].sum(), ',')
            put_temp = format(df_cm_put['미결'].sum(), ',')

        elif comboindex == 1:

            kp200_curve.clear()
            fut_curve.clear()

            cm_call_oi_curve.clear()
            cm_put_oi_curve.clear()
            cm_oi_cha_curve.clear()

            for i in range(nCount_cm_option_pairs):
                temp = format(df_cm_call.iloc[i]['수정거래량'], ',')

                item = QTableWidgetItem(temp)
                item.setTextAlignment(Qt.AlignCenter)
                self.tableWidget_call.setItem(i, Option_column.OI.value, item)

                temp = format(df_cm_put.iloc[i]['수정거래량'], ',')

                item = QTableWidgetItem(temp)
                item.setTextAlignment(Qt.AlignCenter)
                self.tableWidget_put.setItem(i, Option_column.OI.value, item)

            call_temp = format(df_cm_call['수정거래량'].sum(), ',')
            put_temp = format(df_cm_put['수정거래량'].sum(), ',')

        else:

            kp200_curve.clear()
            fut_curve.clear()

            cm_call_volume_curve.clear()
            cm_put_volume_curve.clear()
            cm_volume_cha_curve.clear()

            for i in range(nCount_cm_option_pairs):
                temp = format(df_cm_call.iloc[i]['미결'], ',')

                item = QTableWidgetItem(temp)
                item.setTextAlignment(Qt.AlignCenter)
                self.tableWidget_call.setItem(i, Option_column.OI.value, item)

                temp = format(df_cm_put.iloc[i]['미결'], ',')

                item = QTableWidgetItem(temp)
                item.setTextAlignment(Qt.AlignCenter)
                self.tableWidget_put.setItem(i, Option_column.OI.value, item)

            call_temp = format(df_cm_call['미결'].sum(), ',')
            put_temp = format(df_cm_put['미결'].sum(), ',')

        if call_temp != self.tableWidget_call.horizontalHeaderItem(Option_column.OI.value).text():
            item = QTableWidgetItem(call_temp)
            self.tableWidget_call.setHorizontalHeaderItem(Option_column.OI.value, item)
            self.tableWidget_call.resizeColumnsToContents()
            self.tableWidget_call.setColumnWidth(0, 15)
        else:
            pass

        if put_temp != self.tableWidget_put.horizontalHeaderItem(Option_column.OI.value).text():
            item = QTableWidgetItem(put_temp)
            self.tableWidget_put.setHorizontalHeaderItem(Option_column.OI.value, item)
            self.tableWidget_put.resizeColumnsToContents()
            self.tableWidget_put.setColumnWidth(0, 15)
        else:
            pass

    def timeout(self):
        dt = datetime.datetime.now()
        str = '{0:02d}:{1:02d}:{2:02d}'.format(dt.hour, dt.minute, dt.second)
        self.label_msg.setText(str)

    def label_blink(self, widget, color1, color2, blink_set):

        if blink_set:
            if self.color_flag:
                stylesheet = "background-color: {0}; color: {1}".format(color1, color2)
                widget.setStyleSheet(stylesheet)
            else:
                stylesheet = "background-color: {0}; color: {1}".format(color2, color1)
                widget.setStyleSheet(stylesheet)
            self.color_flag = not self.color_flag
        else:
            stylesheet = "background-color: {0}; color: {1}".format(color1, color2)
            widget.setStyleSheet(stylesheet)

    @pyqtSlot(int)
    def quoteview_state_changed(self):

        if self.checkBox_quoteview.isChecked():

            self.tableWidget_quote.setHorizontalHeaderLabels(['C-MSC', 'C-MDC', 'C-MSR',
                                                        'C-MDR', 'P-MSC', 'P-MDC', 'P-MSR', 'P-MDR', '콜건수비',
                                                        '콜잔량비', '풋건수비', '풋잔량비', '호가 ∑(CRΔ/RRΔ)'])

            # 구 호가요청 취소
            for i in range(15):
                self.cm_opt_ho.UnadviseRealDataWithKey(cm_call_code[(old_atm_index - 7) + i])
                self.cm_opt_ho.UnadviseRealDataWithKey(cm_put_code[(old_atm_index - 7) + i])

            # 새 호가요청
            for i in range(15):
                self.cm_opt_ho.AdviseRealData(cm_call_code[(atm_index - 7) + i])
                self.cm_opt_ho.AdviseRealData(cm_put_code[(atm_index - 7) + i])

            '''
            # call tablewidget 부분초기화
            code_col_text = self.tableWidget_call.horizontalHeaderItem(1).text()
            oloh_col_text = self.tableWidget_call.horizontalHeaderItem(2).text()
            jc_col_text = self.tableWidget_call.horizontalHeaderItem(9).text()
            pvt_col_text = self.tableWidget_call.horizontalHeaderItem(10).text()
            do_col_text = self.tableWidget_call.horizontalHeaderItem(11).text()

            if jc_col_text.find(' √') != -1:
                jc_text = '종가 √'
            else:
                jc_text = '종가'

            if pvt_col_text.find(' √') != -1:
                pvt_text = '피봇 √'
            else:
                pvt_text = '피봇'

            if do_col_text.find(' √') != -1:
                do_text = '시가 √'
            else:
                do_text = '시가'

            oi_str = format(df_cm_call['수정거래량'].sum(), ',')

            if oi_str != self.tableWidget_call.horizontalHeaderItem(Option_column.OI.value).text():
                item = QTableWidgetItem(oi_str)
                self.tableWidget_call.setHorizontalHeaderItem(Option_column.OI.value, item)
            else:
                pass

            self.tableWidget_call.resizeColumnsToContents()
            self.tableWidget_call.setColumnWidth(0, 15)

            # put tablewidget 부분초기화
            code_col_text = self.tableWidget_put.horizontalHeaderItem(1).text()
            oloh_col_text = self.tableWidget_put.horizontalHeaderItem(2).text()
            jc_col_text = self.tableWidget_put.horizontalHeaderItem(9).text()
            pvt_col_text = self.tableWidget_put.horizontalHeaderItem(10).text()
            do_col_text = self.tableWidget_put.horizontalHeaderItem(11).text()

            if jc_col_text.find(' √') != -1:
                jc_text = '종가 √'
            else:
                jc_text = '종가'

            if pvt_col_text.find(' √') != -1:
                pvt_text = '피봇 √'
            else:
                pvt_text = '피봇'

            if do_col_text.find(' √') != -1:
                do_text = '시가 √'
            else:
                do_text = '시가'

            oi_str = format(df_cm_put['수정거래량'].sum(), ',')

            if oi_str != self.tableWidget_call.horizontalHeaderItem(Option_column.OI.value).text():
                item = QTableWidgetItem(oi_str)
                self.tableWidget_put.setHorizontalHeaderItem(Option_column.OI.value, item)
            else:
                pass
            '''
        else:
            self.tableWidget_quote.setHorizontalHeaderLabels(['C-MSCC', 'C-MDCC', 'C-MSCR', 'C-MDCR',
                                                              'P-MSCC', 'P-MDCC', 'P-MSCR', 'P-MDCR', '콜건수비',
                                                        '콜잔량비', '풋건수비', '풋잔량비', '호가 ∑(CRΔ/RRΔ)'])

            '''
            # call tablewidget 부분초기화
            code_col_text = self.tableWidget_call.horizontalHeaderItem(1).text()
            oloh_col_text = self.tableWidget_call.horizontalHeaderItem(2).text()
            jc_col_text = self.tableWidget_call.horizontalHeaderItem(9).text()
            pvt_col_text = self.tableWidget_call.horizontalHeaderItem(10).text()
            do_col_text = self.tableWidget_call.horizontalHeaderItem(11).text()

            if call_node_state['기준가']:
                rv_text = '기준가 √'
            else:
                rv_text = '기준가'

            if call_node_state['월저']:
                ml_text = '월저 √'
            else:
                ml_text = '월저'

            if call_node_state['월고']:
                mh_text = '월고 √'
            else:
                mh_text = '월고'

            if call_node_state['전저']:
                jl_text = '전저 √'
            else:
                jl_text = '전저'

            if call_node_state['전고']:
                jh_text = '전고 √'
            else:
                jh_text = '전고'

            if jc_col_text.find(' √') != -1:
                jc_text = '종가 √'
            else:
                jc_text = '종가'

            if pvt_col_text.find(' √') != -1:
                pvt_text = '피봇 √'
            else:
                pvt_text = '피봇'

            if do_col_text.find(' √') != -1:
                do_text = '시가 √'
            else:
                do_text = '시가'

            oi_str = format(df_cm_call['수정거래량'].sum(), ',')

            if oi_str != self.tableWidget_call.horizontalHeaderItem(Option_column.OI.value).text():
                item = QTableWidgetItem(oi_str)
                self.tableWidget_call.setHorizontalHeaderItem(Option_column.OI.value, item)
            else:
                pass

            self.tableWidget_call.resizeColumnsToContents()
            self.tableWidget_call.setColumnWidth(0, 15)

            # put tablewidget 부분초기화
            code_col_text = self.tableWidget_put.horizontalHeaderItem(1).text()
            oloh_col_text = self.tableWidget_put.horizontalHeaderItem(2).text()
            jc_col_text = self.tableWidget_put.horizontalHeaderItem(9).text()
            pvt_col_text = self.tableWidget_put.horizontalHeaderItem(10).text()
            do_col_text = self.tableWidget_put.horizontalHeaderItem(11).text()

            if put_node_state['기준가']:
                rv_text = '기준가 √'
            else:
                rv_text = '기준가'

            if put_node_state['월저']:
                ml_text = '월저 √'
            else:
                ml_text = '월저'

            if put_node_state['월고']:
                mh_text = '월고 √'
            else:
                mh_text = '월고'

            if put_node_state['전저']:
                jl_text = '전저 √'
            else:
                jl_text = '전저'

            if put_node_state['전고']:
                jh_text = '전고 √'
            else:
                jh_text = '전고'

            if jc_col_text.find(' √') != -1:
                jc_text = '종가 √'
            else:
                jc_text = '종가'

            if pvt_col_text.find(' √') != -1:
                pvt_text = '피봇 √'
            else:
                pvt_text = '피봇'

            if do_col_text.find(' √') != -1:
                do_text = '시가 √'
            else:
                do_text = '시가'

            oi_str = format(df_cm_put['수정거래량'].sum(), ',')

            if oi_str != self.tableWidget_call.horizontalHeaderItem(Option_column.OI.value).text():
                item = QTableWidgetItem(oi_str)
                self.tableWidget_put.setHorizontalHeaderItem(Option_column.OI.value, item)
            else:
                pass

            self.tableWidget_put.resizeColumnsToContents()
            self.tableWidget_put.setColumnWidth(0, 15)

            item = QTableWidgetItem("{0}".format('-'))
            item.setTextAlignment(Qt.AlignCenter)
            self.tableWidget_quote.setItem(0, 0, item)

            item = QTableWidgetItem("{0}".format('-'))
            item.setTextAlignment(Qt.AlignCenter)
            self.tableWidget_quote.setItem(0, 1, item)

            item = QTableWidgetItem("{0}".format('-'))
            item.setTextAlignment(Qt.AlignCenter)
            self.tableWidget_quote.setItem(0, 2, item)

            item = QTableWidgetItem("{0}".format('-'))
            item.setTextAlignment(Qt.AlignCenter)
            self.tableWidget_quote.setItem(0, 3, item)

            item = QTableWidgetItem("{0}".format('-'))
            item.setTextAlignment(Qt.AlignCenter)
            self.tableWidget_quote.setItem(0, 4, item)

            item = QTableWidgetItem("{0}".format('-'))
            item.setTextAlignment(Qt.AlignCenter)
            self.tableWidget_quote.setItem(0, 5, item)

            item = QTableWidgetItem("{0}".format('-'))
            item.setTextAlignment(Qt.AlignCenter)
            self.tableWidget_quote.setItem(0, 6, item)

            item = QTableWidgetItem("{0}".format('-'))
            item.setTextAlignment(Qt.AlignCenter)
            self.tableWidget_quote.setItem(0, 7, item)
            '''

    @pyqtSlot(int)
    def _call_horizontal_header_clicked(self, idx):

        global call_node_state
        global cm_call_종가, cm_call_종가_extend, cm_call_피봇, cm_call_피봇_extend, cm_call_시가, cm_call_시가_extend
        global call_background_color1, call_foreground_color1, call_background_color2, call_foreground_color2
        global call_background_color3, call_foreground_color3, call_background_color4, call_foreground_color4
        global call_gap_percent, call_db_percent

        col_text = self.tableWidget_call.horizontalHeaderItem(idx).text()

        if col_text.find(' √') == -1:
            item = QTableWidgetItem(col_text + ' √')
            self.tableWidget_call.setHorizontalHeaderItem(idx, item)
            print("call header column.. ", idx, col_text)

            if idx == 3:
                call_node_state['기준가'] = True
            elif idx == 4:
                call_node_state['월저'] = True
            elif idx == 5:
                call_node_state['월고'] = True
            elif idx == 6:
                call_node_state['전저'] = True
            elif idx == 7:
                call_node_state['전고'] = True
            elif idx == 8:
                call_node_state['종가'] = True
            elif idx == 9:
                call_node_state['피봇'] = True
            elif idx == 10:
                call_node_state['시가'] = True

                #self.call_open_check()
                #self.call_color_check()

            elif idx == 15:
                call_node_state['대비'] = True

                self.call_db_check()

            elif idx == 17:
                call_node_state['미결'] = True

            elif idx == 18:
                call_node_state['미결증감'] = True

                미결증감 = format(round(df_cm_call['미결증감'].mean()), ',') + ' √'

                if 미결증감 != self.tableWidget_call.horizontalHeaderItem(Option_column.OID.value).text():
                    item = QTableWidgetItem(미결증감)
                    self.tableWidget_call.setHorizontalHeaderItem(Option_column.OID.value, item)
                else:
                    pass
            else:
                pass
        else:
            item = QTableWidgetItem(col_text.replace(' √', ''))
            self.tableWidget_call.setHorizontalHeaderItem(idx, item)
            print("call header column.. ", idx, col_text)

            if idx == 3:
                call_node_state['기준가'] = False
            elif idx == 4:
                call_node_state['월저'] = False
            elif idx == 5:
                call_node_state['월고'] = False
            elif idx == 6:
                call_node_state['전저'] = False
            elif idx == 7:
                call_node_state['전고'] = False
            elif idx == 8:
                call_node_state['종가'] = False
            elif idx == 9:
                call_node_state['피봇'] = False
            elif idx == 10:
                call_node_state['시가'] = False

            elif idx == 15:
                call_node_state['대비'] = False
            elif idx == 17:
                call_node_state['미결'] = False

                item = QTableWidgetItem('거래량')
                self.tableWidget_call.setHorizontalHeaderItem(idx, item)
            elif idx == 18:
                call_node_state['미결증감'] = False

                item = QTableWidgetItem('OIΔ')
                self.tableWidget_call.setHorizontalHeaderItem(idx, item)
            else:
                pass

        print(call_node_state)

        self.tableWidget_call.resizeColumnsToContents()
        self.tableWidget_call.setColumnWidth(0, 15)

        for i in range(call_scroll_begin_position, call_scroll_end_position):

            # Clear Color
            self.tableWidget_call.item(i, Option_column.기준가.value).setBackground(QBrush(기본바탕색))
            self.tableWidget_call.item(i, Option_column.기준가.value).setForeground(QBrush(검정색))

            self.tableWidget_call.item(i, Option_column.월저.value).setBackground(QBrush(기본바탕색))
            self.tableWidget_call.item(i, Option_column.월저.value).setForeground(QBrush(검정색))

            self.tableWidget_call.item(i, Option_column.월고.value).setBackground(QBrush(기본바탕색))
            self.tableWidget_call.item(i, Option_column.월고.value).setForeground(QBrush(검정색))

            self.tableWidget_call.item(i, Option_column.전저.value).setBackground(QBrush(기본바탕색))
            self.tableWidget_call.item(i, Option_column.전저.value).setForeground(QBrush(검정색))

            self.tableWidget_call.item(i, Option_column.전고.value).setBackground(QBrush(기본바탕색))
            self.tableWidget_call.item(i, Option_column.전고.value).setForeground(QBrush(검정색))

            self.tableWidget_call.item(i, Option_column.종가.value).setBackground(QBrush(기본바탕색))
            self.tableWidget_call.item(i, Option_column.종가.value).setForeground(QBrush(검정색))

            self.tableWidget_call.item(i, Option_column.피봇.value).setBackground(QBrush(기본바탕색))
            self.tableWidget_call.item(i, Option_column.피봇.value).setForeground(QBrush(검정색))

            self.tableWidget_call.item(i, Option_column.시가.value).setBackground(QBrush(기본바탕색))
            self.tableWidget_call.item(i, Option_column.시가.value).setForeground(QBrush(검정색))

            self.tableWidget_call.item(i, Option_column.저가.value).setBackground(QBrush(기본바탕색))
            self.tableWidget_call.item(i, Option_column.저가.value).setForeground(QBrush(검정색))

            self.tableWidget_call.item(i, Option_column.고가.value).setBackground(QBrush(기본바탕색))
            self.tableWidget_call.item(i, Option_column.고가.value).setForeground(QBrush(검정색))

        self.call_node_color_clear()
        self.put_node_color_clear()

        self.callnode_color_check()
        self.putnode_color_check()

        return

    @pyqtSlot(int)
    def _put_horizontal_header_clicked(self, idx):

        global put_node_state
        global cm_put_종가, cm_put_종가_extend, cm_put_피봇, cm_put_피봇_extend, cm_put_시가, cm_put_시가_extend
        global put_background_color1, put_foreground_color1, put_background_color2, put_foreground_color2
        global put_background_color3, put_foreground_color3, put_background_color4, put_foreground_color4
        global put_gap_percent, put_db_percent

        col_text = self.tableWidget_put.horizontalHeaderItem(idx).text()

        if col_text.find(' √') == -1:
            item = QTableWidgetItem(col_text + ' √')
            self.tableWidget_put.setHorizontalHeaderItem(idx, item)
            print("put header column.. ", idx, col_text)

            if idx == 3:
                put_node_state['기준가'] = True
            elif idx == 4:
                put_node_state['월저'] = True
            elif idx == 5:
                put_node_state['월고'] = True
            elif idx == 6:
                put_node_state['전저'] = True
            elif idx == 7:
                put_node_state['전고'] = True
            elif idx == 8:
                put_node_state['종가'] = True
            elif idx == 9:
                put_node_state['피봇'] = True
            elif idx == 10:
                put_node_state['시가'] = True

                #self.put_open_check()
                #self.put_color_check()

            elif idx == 15:
                put_node_state['대비'] = True

                self.put_db_check()

            elif idx == 17:
                put_node_state['미결'] = True

            elif idx == 18:
                put_node_state['미결증감'] = True

                미결증감 = format(round(df_cm_put['미결증감'].mean()), ',') + ' √'

                if 미결증감 != self.tableWidget_put.horizontalHeaderItem(Option_column.OID.value).text():
                    item = QTableWidgetItem(미결증감)
                    self.tableWidget_put.setHorizontalHeaderItem(Option_column.OID.value, item)
                else:
                    pass
            else:
                pass
        else:
            item = QTableWidgetItem(col_text.replace(' √', ''))
            self.tableWidget_put.setHorizontalHeaderItem(idx, item)
            print("put header column.. ", idx, col_text)

            if idx == 3:
                put_node_state['기준가'] = False
            elif idx == 4:
                put_node_state['월저'] = False
            elif idx == 5:
                put_node_state['월고'] = False
            elif idx == 6:
                put_node_state['전저'] = False
            elif idx == 7:
                put_node_state['전고'] = False
            elif idx == 8:
                put_node_state['종가'] = False
            elif idx == 9:
                put_node_state['피봇'] = False
            elif idx == 10:
                put_node_state['시가'] = False

            elif idx == 15:
                put_node_state['대비'] = False

            elif idx == 17:
                put_node_state['미결'] = False

                item = QTableWidgetItem('거래량')
                self.tableWidget_put.setHorizontalHeaderItem(idx, item)

            elif idx == 18:
                put_node_state['미결증감'] = False

                item = QTableWidgetItem('OIΔ')
                self.tableWidget_put.setHorizontalHeaderItem(idx, item)
            else:
                pass

        self.tableWidget_put.resizeColumnsToContents()
        self.tableWidget_put.setColumnWidth(0, 15)

        for i in range(put_scroll_begin_position, put_scroll_end_position):

            # Clear Color
            self.tableWidget_put.item(i, Option_column.기준가.value).setBackground(QBrush(기본바탕색))
            self.tableWidget_put.item(i, Option_column.기준가.value).setForeground(QBrush(검정색))

            self.tableWidget_put.item(i, Option_column.월저.value).setBackground(QBrush(기본바탕색))
            self.tableWidget_put.item(i, Option_column.월저.value).setForeground(QBrush(검정색))

            self.tableWidget_put.item(i, Option_column.월고.value).setBackground(QBrush(기본바탕색))
            self.tableWidget_put.item(i, Option_column.월고.value).setForeground(QBrush(검정색))

            self.tableWidget_put.item(i, Option_column.전저.value).setBackground(QBrush(기본바탕색))
            self.tableWidget_put.item(i, Option_column.전저.value).setForeground(QBrush(검정색))

            self.tableWidget_put.item(i, Option_column.전고.value).setBackground(QBrush(기본바탕색))
            self.tableWidget_put.item(i, Option_column.전고.value).setForeground(QBrush(검정색))

            self.tableWidget_put.item(i, Option_column.종가.value).setBackground(QBrush(기본바탕색))
            self.tableWidget_put.item(i, Option_column.종가.value).setForeground(QBrush(검정색))

            self.tableWidget_put.item(i, Option_column.피봇.value).setBackground(QBrush(기본바탕색))
            self.tableWidget_put.item(i, Option_column.피봇.value).setForeground(QBrush(검정색))

            self.tableWidget_put.item(i, Option_column.시가.value).setBackground(QBrush(기본바탕색))
            self.tableWidget_put.item(i, Option_column.시가.value).setForeground(QBrush(검정색))

            self.tableWidget_put.item(i, Option_column.저가.value).setBackground(QBrush(기본바탕색))
            self.tableWidget_put.item(i, Option_column.저가.value).setForeground(QBrush(검정색))

            self.tableWidget_put.item(i, Option_column.고가.value).setBackground(QBrush(기본바탕색))
            self.tableWidget_put.item(i, Option_column.고가.value).setForeground(QBrush(검정색))

        self.call_node_color_clear()
        self.put_node_color_clear()

        self.putnode_color_check()
        self.callnode_color_check()

        return

    @pyqtSlot(int)
    def _call_vertical_header_clicked(self, idx):

        row_text = self.tableWidget_call.item(idx, Option_column.행사가.value).text()

        if row_text.find(' √') == -1:
            item = QTableWidgetItem(row_text + ' √')
            item.setTextAlignment(Qt.AlignCenter)
            self.tableWidget_call.setItem(idx, Option_column.행사가.value, item)
        else:
            item = QTableWidgetItem(row_text.replace(' √', ''))
            item.setTextAlignment(Qt.AlignCenter)
            self.tableWidget_call.setItem(idx, Option_column.행사가.value, item)

        self.tableWidget_call.resizeColumnsToContents()
        self.tableWidget_call.setColumnWidth(0, 15)

        return

    @pyqtSlot(int)
    def _put_vertical_header_clicked(self, idx):

        row_text = self.tableWidget_put.item(idx, Option_column.행사가.value).text()

        if row_text.find(' √') == -1:
            item = QTableWidgetItem(row_text + ' √')
            item.setTextAlignment(Qt.AlignCenter)
            self.tableWidget_put.setItem(idx, Option_column.행사가.value, item)
        else:
            item = QTableWidgetItem(row_text.replace(' √', ''))
            item.setTextAlignment(Qt.AlignCenter)
            self.tableWidget_put.setItem(idx, Option_column.행사가.value, item)

        self.tableWidget_put.resizeColumnsToContents()
        self.tableWidget_put.setColumnWidth(0, 15)

        return

    @pyqtSlot(int, int)
    def _calltable_cell_clicked(self, row, col):

        cell = self.tableWidget_call.item(row, col)

        if cell is not None:

            txt = "call table cell clicked = ({0},{1}) ==>{2}<==".format(row, col, cell.text())

            if atm_str != '':

                if row < atm_index:
                    call_positionCell = self.tableWidget_call.item(atm_index + 3, 1)
                else:
                    call_positionCell = self.tableWidget_call.item(atm_index - 4, 1)

                self.tableWidget_call.scrollToItem(call_positionCell)
            else:
                pass

        else:
            txt = "call table cell clicked = ({0},{1}) ==>None type<==".format(row, col)

        print(txt)

        return

    @pyqtSlot(int, int)
    def _puttable_cell_clicked(self, row, col):

        cell = self.tableWidget_put.item(row, col)

        if cell is not None:

            txt = "put table cell clicked = ({0},{1}) ==>{2}<==".format(row, col, cell.text())

            if atm_str != '':

                if row < atm_index:
                    put_positionCell = self.tableWidget_put.item(atm_index + 3, 1)
                else:
                    put_positionCell = self.tableWidget_put.item(atm_index - 4, 1)

                self.tableWidget_put.scrollToItem(put_positionCell)
            else:
                pass

        else:
            txt = "put table cell clicked = ({0},{1}) ==>None type<==".format(row, col)

        print(txt)

        return

    @pyqtSlot(int)
    def _calltable_vertical_scroll_position(self, row):

        global call_scroll_begin_position, call_scroll_end_position
        call_scroll_begin_position = row

        if nCount_cm_option_pairs == 0:

            if nCount_cm_option_pairs - 9 < call_scroll_begin_position < 100:

                call_scroll_end_position = nCount_cm_option_pairs
            else:
                call_scroll_end_position = call_scroll_begin_position + 9
        else:
            if nCount_cm_option_pairs - 9 < call_scroll_begin_position < nCount_cm_option_pairs:

                call_scroll_end_position = nCount_cm_option_pairs
            else:
                call_scroll_end_position = call_scroll_begin_position + 9

            self.tableWidget_call.resizeColumnsToContents()
            self.tableWidget_call.setColumnWidth(0, 15)

            print('call scroll position -----> from %d to %d' % (call_scroll_begin_position, call_scroll_end_position))

            for i in range(call_scroll_begin_position, call_scroll_end_position):

                if df_cm_call.iloc[i]['저가'] < df_cm_call.iloc[i]['고가']:

                    # Clear Color
                    self.tableWidget_call.item(i, Option_column.기준가.value).setBackground(QBrush(기본바탕색))
                    self.tableWidget_call.item(i, Option_column.기준가.value).setForeground(QBrush(검정색))

                    self.tableWidget_call.item(i, Option_column.월저.value).setBackground(QBrush(기본바탕색))
                    self.tableWidget_call.item(i, Option_column.월저.value).setForeground(QBrush(검정색))

                    self.tableWidget_call.item(i, Option_column.월고.value).setBackground(QBrush(기본바탕색))
                    self.tableWidget_call.item(i, Option_column.월고.value).setForeground(QBrush(검정색))

                    self.tableWidget_call.item(i, Option_column.전저.value).setBackground(QBrush(기본바탕색))
                    self.tableWidget_call.item(i, Option_column.전저.value).setForeground(QBrush(검정색))

                    self.tableWidget_call.item(i, Option_column.전고.value).setBackground(QBrush(기본바탕색))
                    self.tableWidget_call.item(i, Option_column.전고.value).setForeground(QBrush(검정색))

                    self.tableWidget_call.item(i, Option_column.종가.value).setBackground(QBrush(기본바탕색))
                    self.tableWidget_call.item(i, Option_column.종가.value).setForeground(QBrush(검정색))

                    self.tableWidget_call.item(i, Option_column.피봇.value).setBackground(QBrush(기본바탕색))
                    self.tableWidget_call.item(i, Option_column.피봇.value).setForeground(QBrush(검정색))

                    self.tableWidget_call.item(i, Option_column.시가.value).setBackground(QBrush(기본바탕색))
                    self.tableWidget_call.item(i, Option_column.시가.value).setForeground(QBrush(검정색))

                    self.tableWidget_call.item(i, Option_column.저가.value).setBackground(QBrush(기본바탕색))
                    self.tableWidget_call.item(i, Option_column.저가.value).setForeground(QBrush(검정색))

                    self.tableWidget_call.item(i, Option_column.고가.value).setBackground(QBrush(기본바탕색))
                    self.tableWidget_call.item(i, Option_column.고가.value).setForeground(QBrush(검정색))

            self.call_node_color_clear()
            self.put_node_color_clear()

            self.callnode_color_check()

        return

    @pyqtSlot(int)
    def _puttable_vertical_scroll_position(self, row):

        global put_scroll_begin_position, put_scroll_end_position
        put_scroll_begin_position = row

        if nCount_cm_option_pairs == 0:

            if nCount_cm_option_pairs - 9 < put_scroll_begin_position < 100:

                put_scroll_end_position = nCount_cm_option_pairs
            else:
                put_scroll_end_position = put_scroll_begin_position + 9
        else:
            if nCount_cm_option_pairs - 9 < put_scroll_begin_position < nCount_cm_option_pairs:

                put_scroll_end_position = nCount_cm_option_pairs
            else:
                put_scroll_end_position = put_scroll_begin_position + 9

            self.tableWidget_put.resizeColumnsToContents()
            self.tableWidget_put.setColumnWidth(0, 15)

            print('put scroll position -----> from %d to %d' % (put_scroll_begin_position, put_scroll_end_position))

            for i in range(put_scroll_begin_position, put_scroll_end_position):

                if df_cm_put.iloc[i]['저가'] < df_cm_put.iloc[i]['고가']:

                    # Clear Color
                    self.tableWidget_put.item(i, Option_column.기준가.value).setBackground(QBrush(기본바탕색))
                    self.tableWidget_put.item(i, Option_column.기준가.value).setForeground(QBrush(검정색))

                    self.tableWidget_put.item(i, Option_column.월저.value).setBackground(QBrush(기본바탕색))
                    self.tableWidget_put.item(i, Option_column.월저.value).setForeground(QBrush(검정색))

                    self.tableWidget_put.item(i, Option_column.월고.value).setBackground(QBrush(기본바탕색))
                    self.tableWidget_put.item(i, Option_column.월고.value).setForeground(QBrush(검정색))

                    self.tableWidget_put.item(i, Option_column.전저.value).setBackground(QBrush(기본바탕색))
                    self.tableWidget_put.item(i, Option_column.전저.value).setForeground(QBrush(검정색))

                    self.tableWidget_put.item(i, Option_column.전고.value).setBackground(QBrush(기본바탕색))
                    self.tableWidget_put.item(i, Option_column.전고.value).setForeground(QBrush(검정색))

                    self.tableWidget_put.item(i, Option_column.종가.value).setBackground(QBrush(기본바탕색))
                    self.tableWidget_put.item(i, Option_column.종가.value).setForeground(QBrush(검정색))

                    self.tableWidget_put.item(i, Option_column.피봇.value).setBackground(QBrush(기본바탕색))
                    self.tableWidget_put.item(i, Option_column.피봇.value).setForeground(QBrush(검정색))

                    self.tableWidget_put.item(i, Option_column.시가.value).setBackground(QBrush(기본바탕색))
                    self.tableWidget_put.item(i, Option_column.시가.value).setForeground(QBrush(검정색))

                    self.tableWidget_put.item(i, Option_column.저가.value).setBackground(QBrush(기본바탕색))
                    self.tableWidget_put.item(i, Option_column.저가.value).setForeground(QBrush(검정색))

                    self.tableWidget_put.item(i, Option_column.고가.value).setBackground(QBrush(기본바탕색))
                    self.tableWidget_put.item(i, Option_column.고가.value).setForeground(QBrush(검정색))

            self.call_node_color_clear()
            self.put_node_color_clear()

            self.putnode_color_check()

        return

    @pyqtSlot(object)
    def t8415_call_request(self, data):
        try:

            XQ = t8415(parent=self)
            XQ.Query(단축코드=cm_call_code[data], 시작일자=month_firstday_str, 종료일자=today_str)

        except:
            pass

    @pyqtSlot(object)
    def t8415_put_request(self, data):
        try:

            XQ = t8415(parent=self)
            XQ.Query(단축코드=cm_put_code[data], 시작일자=month_firstday_str, 종료일자=today_str)

        except:
            pass

    @pyqtSlot(object)
    def t8416_call_request(self, data):
        try:

            print('t8416_call_request', data, cm_call_code[data])
            XQ = t8416(parent=self)
            XQ.Query(단축코드=cm_call_code[data], 시작일자=month_firstday_str, 종료일자=today_str)

        except:
            pass

    @pyqtSlot(object)
    def t8416_put_request(self, data):
        try:

            XQ = t8416(parent=self)
            XQ.Query(단축코드=cm_put_code[data], 시작일자=month_firstday_str, 종료일자=today_str)

        except:
            pass

    @pyqtSlot(dict)
    def update_plot(self, data):
        try:
            start_time = timeit.default_timer()

            dt = datetime.datetime.now()

            global delta_hour, delta_minute, delta_sec

            # 시스템시간이 서버시간보다 빠른 경우
            if time_delta > 0:

                if dt.second - time_delta < 0:

                    delta_sec = 60 + dt.second - time_delta

                    if dt.minute == 0:

                        delta_minute = 59
                        delta_hour = dt.hour - 1
                    else:
                        delta_minute = dt.minute - 1
                        delta_hour = dt.hour
                else:
                    delta_sec = dt.second - time_delta
                    delta_minute = dt.minute
                    delta_hour = dt.hour

            # 시스템시간이 서버시간보다 느린 경우
            elif time_delta < 0:

                delta_sec = (dt.second - time_delta) % 60

                if (dt.second - time_delta) // 60:

                    if dt.minute == 59:

                        delta_minute = 0
                        delta_hour = dt.hour + 1
                    else:
                        delta_minute = dt.minute + (dt.second - time_delta) // 60
                        delta_hour = dt.hour
                else:
                    delta_minute = dt.minute
                    delta_hour = dt.hour

            # 같은 경우
            else:
                delta_sec = dt.second
                delta_minute = dt.minute
                delta_hour = dt.hour

            global call_volume_total, put_volume_total
            global volume_delta, volume_delta_old, oi_delta, oi_delta_old
            global 거래량_직전대비, 미결_직전대비
            #global df_plotdata_cm_call_volume, df_plotdata_cm_put_volume, df_plotdata_cm_volume_cha

            if not pre_start:

                if call_volume_total > put_volume_total and call_volume_total > 0 and put_volume_total < 0:
                    self.label_msg.setStyleSheet('background-color: red; color: white')
                    self.label_msg.setFont(QtGui.QFont("Consolas", 9, QtGui.QFont.Bold))
                elif call_volume_total < put_volume_total and call_volume_total < 0 and put_volume_total > 0:
                    self.label_msg.setStyleSheet('background-color: blue; color: white')
                    self.label_msg.setFont(QtGui.QFont("Consolas", 9, QtGui.QFont.Bold))
                else:
                    self.label_msg.setStyleSheet('background-color: lime; color: blue')
                    self.label_msg.setFont(QtGui.QFont("Consolas", 9, QtGui.QFont.Bold))

                volume_delta_old = volume_delta

                volume_delta = call_volume_total - put_volume_total

                거래량_직전대비.extend([volume_delta - volume_delta_old])
                temp = list(거래량_직전대비)

                if ReceiveRealData:

                    if volume_delta > 0:

                        if min(temp) > 0:

                            str = '{0:02d}:{1:02d}:{2:02d} [{3}] ↗'.format(
                                delta_hour, delta_minute, delta_sec, format(volume_delta, ','))
                            self.label_msg.setText(str)

                        elif max(temp) < 0:

                            str = '{0:02d}:{1:02d}:{2:02d} [{3}] ↘'.format(
                                delta_hour, delta_minute, delta_sec, format(volume_delta, ','))
                            self.label_msg.setText(str)
                        else:
                            str = '{0:02d}:{1:02d}:{2:02d} [{3}]'.format(
                                delta_hour, delta_minute, delta_sec, format(volume_delta, ','))
                            self.label_msg.setText(str)

                    elif volume_delta < 0:

                        if min(temp) > 0:

                            str = '{0:02d}:{1:02d}:{2:02d} [{3}] ↘'.format(
                                delta_hour, delta_minute, delta_sec, format(abs(volume_delta), ','))
                            self.label_msg.setText(str)

                        elif max(temp) < 0:

                            str = '{0:02d}:{1:02d}:{2:02d} [{3}] ↗'.format(
                                delta_hour, delta_minute, delta_sec, format(abs(volume_delta), ','))
                            self.label_msg.setText(str)
                        else:
                            str = '{0:02d}:{1:02d}:{2:02d} [{3}]'.format(
                                delta_hour, delta_minute, delta_sec, format(abs(volume_delta), ','))
                            self.label_msg.setText(str)
                    else:
                        pass

                    if not pre_start:

                        global 콜저가리스트, 콜고가리스트, 풋저가리스트, 풋고가리스트

                        if self.alternate_flag:

                            self.call_color_clear()
                            self.call_post_processing()                            

                            if cm_call_저가 != 콜저가리스트:

                                콜저가리스트 = copy.deepcopy(cm_call_저가)
                                #self.callnode_color_check()
                                self.call_low_update_color_check()
                            else:
                                pass

                            if cm_call_고가 != 콜고가리스트:

                                콜고가리스트 = copy.deepcopy(cm_call_고가)
                                #self.callnode_color_check()
                                self.call_high_update_color_check()                           
                            else:
                                pass
                        else:

                            self.put_color_clear()
                            self.put_post_processing()

                            if cm_put_저가 != 풋저가리스트:

                                풋저가리스트 = copy.deepcopy(cm_put_저가)
                                #self.putnode_color_check()
                                self.put_low_update_color_check()
                            else:
                                pass

                            if cm_put_고가 != 풋고가리스트:

                                풋고가리스트 = copy.deepcopy(cm_put_고가)
                                #self.putnode_color_check()
                                self.put_high_update_color_check()
                            else:
                                pass

                        self.alternate_flag = not self.alternate_flag

                        if not overnight:

                            콜_미결합 = df_cm_call['미결'].sum()
                            풋_미결합 = df_cm_put['미결'].sum()

                            미결합 = 콜_미결합 + 풋_미결합

                            oi_delta_old = oi_delta

                            if 미결합 > 0:
                                콜미결퍼센트 = (콜_미결합 / 미결합) * 100
                                풋미결퍼센트 = 100 - 콜미결퍼센트
                                #call_oi_delta = 콜미결퍼센트 - call_oi_percent_init_value
                                #put_oi_delta = 풋미결퍼센트 - put_oi_percent_init_value
                                call_oi_delta = 콜_미결합 - call_oi_percent_init_value
                                put_oi_delta = 풋_미결합 - put_oi_percent_init_value

                                oi_delta = call_oi_delta - put_oi_delta
                                미결_직전대비.extend([oi_delta - oi_delta_old])
                                temp = list(미결_직전대비)
                            else:
                                pass

                            if oi_delta > 0:

                                self.label_atm.setStyleSheet('background-color: red; color: white')
                                self.label_atm.setFont(QtGui.QFont("Consolas", 9, QtGui.QFont.Bold))

                                if min(temp) > 0:

                                    str = '[{0:0.2f}] [{1:0.2f}/{2:0.2f}] [{3}] ↗'.format(
                                        fut_realdata['현재가'] - fut_realdata['KP200'],
                                        call_atm_value + put_atm_value,
                                        abs(call_atm_value - put_atm_value),
                                        format(abs(oi_delta), ','))
                                elif max(temp) < 0:

                                    str = '[{0:0.2f}] [{1:0.2f}/{2:0.2f}] [{3}] ↘'.format(
                                        fut_realdata['현재가'] - fut_realdata['KP200'],
                                        call_atm_value + put_atm_value,
                                        abs(call_atm_value - put_atm_value),
                                        format(abs(oi_delta), ','))
                                else:

                                    str = '[{0:0.2f}] [{1:0.2f}/{2:0.2f}] [{3}]'.format(
                                        fut_realdata['현재가'] - fut_realdata['KP200'],
                                        call_atm_value + put_atm_value,
                                        abs(call_atm_value - put_atm_value),
                                        format(abs(oi_delta), ','))

                            elif oi_delta < 0:

                                self.label_atm.setStyleSheet('background-color: blue; color: white')
                                self.label_atm.setFont(QtGui.QFont("Consolas", 9, QtGui.QFont.Bold))

                                if min(temp) > 0:

                                    str = '[{0:0.2f}] [{1:0.2f}/{2:0.2f}] [{3}] ↘'.format(
                                        fut_realdata['현재가'] - fut_realdata['KP200'],
                                        call_atm_value + put_atm_value,
                                        abs(call_atm_value - put_atm_value),
                                        format(abs(oi_delta), ','))
                                elif max(temp) < 0:

                                    str = '[{0:0.2f}] [{1:0.2f}/{2:0.2f}] [{3}] ↗'.format(
                                        fut_realdata['현재가'] - fut_realdata['KP200'],
                                        call_atm_value + put_atm_value,
                                        abs(call_atm_value - put_atm_value),
                                        format(abs(oi_delta), ','))
                                else:

                                    str = '[{0:0.2f}] [{1:0.2f}/{2:0.2f}] [{3}]'.format(
                                        fut_realdata['현재가'] - fut_realdata['KP200'],
                                        call_atm_value + put_atm_value,
                                        abs(call_atm_value - put_atm_value),
                                        format(abs(oi_delta), ','))

                            else:
                                self.label_atm.setStyleSheet('background-color: yellow; color: black')
                                self.label_atm.setFont(QtGui.QFont("Consolas", 9, QtGui.QFont.Bold))

                                str = '[{0:0.2f}] [{1:0.2f}/{2:0.2f}] [{3:0.1f}:{4:0.1f}]'.format(
                                    fut_realdata['현재가'] - fut_realdata['KP200'],
                                    call_atm_value + put_atm_value,
                                    abs(call_atm_value - put_atm_value),
                                    콜미결퍼센트, 풋미결퍼센트)

                        else:
                            str = '[{0:0.2f}] [{1:0.2f}/{2:0.2f}] [{3}:{4}]'.format(
                                fut_realdata['현재가'] - fut_realdata['KP200'],
                                call_atm_value + put_atm_value,
                                abs(call_atm_value - put_atm_value),
                                '-', '-')

                        self.label_atm.setText(str)

                        if dt.second in every_0sec and not self.alternate_flag:

                            str = '[{0:02d}:{1:02d}:{2:02d}] 대비 갱신합니다.\r'.format(delta_hour, delta_minute, delta_sec)
                            self.textBrowser.append(str)

                            self.call_db_check()
                            self.put_db_check()
                        else:
                            pass

                        if dt.minute in every_5min and dt.second in only_30sec and self.alternate_flag:

                            str = '[{0:02d}:{1:02d}:{2:02d}] Open Check 갱신합니다.\r'.format(delta_hour, delta_minute,
                                                                                         delta_sec)

                            self.call_open_check()
                            self.put_open_check()
                        else:
                            pass
                    else:
                        pass
                else:
                    str = '{0:02d}:{1:02d}:{2:02d} [{3}]'.format(
                        delta_hour, delta_minute, delta_sec, format(abs(volume_delta), ','))
                    self.label_msg.setText(str)
            else:
                self.label_msg.setStyleSheet('background-color: lime; color: blue')
                self.label_msg.setFont(QtGui.QFont("Consolas", 9, QtGui.QFont.Bold))

                str = '{0:02d}:{1:02d}:{2:02d}'.format(delta_hour, delta_minute, delta_sec)
                self.label_msg.setText(str)

            # 호가갱신
            self.quote_display()

            if self.checkBox_quoteview.isChecked():

                self.call_quote_display()
                self.put_quote_display()
            else:
                self.call_che_display()
                self.put_che_display()

            call_idx = []
            put_idx = []

            for i in range(nRowCount):

                call_ckbox = self.tableWidget_call.cellWidget(i, 0)

                if isinstance(call_ckbox, QCheckBox):
                    if call_ckbox.isChecked():
                        call_idx.append(i)
                    else:
                        pass
                else:
                    pass

                put_ckbox = self.tableWidget_put.cellWidget(i, 0)

                if isinstance(put_ckbox, QCheckBox):
                    if put_ckbox.isChecked():
                        put_idx.append(i)
                    else:
                        pass
                else:
                    pass

            global selected_call, selected_put
            global fut_axY

            selected_call = call_idx
            selected_put = put_idx

            # 옵션 Y축 최대값 구하기
            axY = self.Plot_Opt.getAxis('left')
            #print('옵션 y axis range: {}'.format(axY.range[1]))

            mv_line[0].setValue(1.2)
            mv_line[1].setValue(2.5)
            mv_line[2].setValue(3.5)
            mv_line[3].setValue(4.85)

            if 5.1 < axY.range[1] < 5.5:
                mv_line[4].setValue(5.1)
                mv_line[5].setValue(0)
                mv_line[6].setValue(0)
                mv_line[7].setValue(0)
                mv_line[8].setValue(0)
            elif 5.5 <= axY.range[1] < 6.0:
                mv_line[4].setValue(5.1)
                mv_line[5].setValue(5.5)
                mv_line[6].setValue(0)
                mv_line[7].setValue(0)
                mv_line[8].setValue(0)
            elif 6.0 <= axY.range[1] < 7.1:
                mv_line[4].setValue(5.1)
                mv_line[5].setValue(5.5)
                mv_line[6].setValue(6.85)
                mv_line[7].setValue(0)
                mv_line[8].setValue(0)
            elif 7.1 <= axY.range[1] < 8.1:
                mv_line[4].setValue(5.1)
                mv_line[5].setValue(5.5)
                mv_line[6].setValue(6.85)
                mv_line[7].setValue(7.1)
                mv_line[8].setValue(0)
            elif axY.range[1] >= 8.1:
                mv_line[4].setValue(5.1)
                mv_line[5].setValue(5.5)
                mv_line[6].setValue(6.85)
                mv_line[7].setValue(7.1)
                mv_line[8].setValue(8.1)
            else:
                pass

            if x_idx > 10 and opt_x_idx > 10:

                if comboindex == 2:

                    time_line_fut.setValue(x_idx + 1)
                else:
                    time_line_fut.setValue(opt_x_idx + 1)

                time_line.setValue(opt_x_idx + 1)
            else:
                pass

            if comboindex == 2:

                fut_jl_line.setValue(fut_realdata['전저'])
                fut_jh_line.setValue(fut_realdata['전고'])
                volume_base_line.setValue(fut_realdata['피봇'])
                fut_pivot_line.setValue(fut_realdata['피봇'])
            else:
                fut_jl_line.setValue(0)
                fut_jh_line.setValue(0)
                fut_pivot_line.setValue(0)
                volume_base_line.setValue(0)            

            # clear all view tablewidget curve
            dummy = [np.nan] * (opt_x_idx + 1)
            dummy[0] = 0

            for i in range(9):
                call_curve[i].setData(dummy)
                put_curve[i].setData(dummy)

            # plot data
            for actval, infos in data.items():

                index = cm_call_actval.index(actval)

                for i in range(len(call_idx)):

                    if index == call_idx[i]:

                        call_curve[i].setData(infos[0])
                    else:
                        pass

                for i in range(len(put_idx)):

                    if index == put_idx[i]:

                        put_curve[i].setData(infos[1])
                    else:
                        pass

                curve1_data = infos[2]
                curve2_data = infos[3]

                if comboindex == 2:
                    pass
                else:
                    curve3_data = infos[4]                

            if comboindex == 2:

                kp200_curve.setData(curve1_data)
                fut_curve.setData(curve2_data)

            elif comboindex == 1:
                '''
                c3 = curve3_data[:opt_x_idx + 2]

                if call_volume_total > put_volume_total:
                    cm_volume_cha_curve.setData(c3, fillLevel=0.0, brush='r')
                else:
                    cm_volume_cha_curve.setData(c3, fillLevel=0.0, brush='b')
                '''
                #cm_volume_cha_curve.setData(curve3_data)
                cm_call_volume_curve.setData(curve1_data)
                cm_put_volume_curve.setData(curve2_data)

            else:
                #cm_oi_cha_curve.setData(curve3_data)
                cm_call_oi_curve.setData(curve1_data)
                cm_put_oi_curve.setData(curve2_data)

            str = '[{0:02d}:{1:02d}:{2:02d}] plot update 처리시간 ----------> {3:0.2f} ms...'.format(delta_hour, delta_minute, delta_sec, (timeit.default_timer() - start_time) * 1000)
            print(str)
        except:
            pass

    def set_call_atm_row_color(self, rowIndex, brush):

        for j in range(self.tableWidget_call.columnCount() - 1):
            self.tableWidget_call.item(rowIndex, j + 1).setBackground(brush)

    def set_put_atm_row_color(self, rowIndex, brush):

        for j in range(self.tableWidget_put.columnCount() - 1):
            self.tableWidget_put.item(rowIndex, j + 1).setBackground(brush)

    def within_n_tick(self, source, target, n):

        if round((target - 0.01*n), 2) <= source <= round((target + 0.01*n), 2):
            return True
        else:
            return False

    def calc_pivot(self, jl, jh, jc, do):

        if jl > 0 and jh > 0 and jc > 0 and do > 0:
            tmp = (jl + jh + jc)/3 + (do - jc)
            pivot = round(tmp, 2)

            return pivot
        else:
            return 0

    def make_color_list(self, input_list):

        list_low = []
        list_zero = []
        list_high = []

        temp = list(set(input_list))
        temp.sort()

        index1 = bisect(temp, 0.29)
        index2 = bisect(temp, 10)

        list_singleval = temp[index1:index2]

        for i in range(len(list_singleval)):
            list_low.append(round(list_singleval[i] - 0.01, 2))
            list_zero.append(round(list_singleval[i] + 0.0, 2))
            list_high.append(round(list_singleval[i] + 0.01, 2))

        output_list = list_low + list_zero + list_high
        output_list.sort()

        return output_list

    def find_ATM(self, kp200):

        temp = math.floor(round(kp200 / 2.5, 0) * 2.5)
        str_atm = '{0:0.0f}'.format(temp)

        return str_atm

    def image_grab(self):

        now = time.localtime()
        times = "%04d-%02d-%02d-%02d-%02d-%02d" % (now.tm_year, now.tm_mon, now.tm_mday, now.tm_hour, now.tm_min, now.tm_sec)

        hwnd = win32gui.FindWindow(None, cm_option_title)
        win32gui.SetForegroundWindow(hwnd)
        dimensions = win32gui.GetWindowRect(hwnd)
        img = ImageGrab.grab(dimensions)
        saveas = "Screenshot {}{}".format(times, '.png')
        img.save(saveas)

        str = '[{0:02d}:{1:02d}:{2:02d}] 화면을 캡처했습니다.\r'.format(now.tm_hour, now.tm_min, now.tm_sec)
        self.textBrowser.append(str)

    def call_open_check(self):

        global df_cm_call, call_open, call_ol, call_oh
        global call_gap_percent
        global cm_call_시가_extend, cm_call_피봇_extend

        call_open_count = 0

        for index in range(nCount_cm_option_pairs):

            if df_cm_call.iloc[index]['시가'] > 0.3 and df_cm_call.iloc[index]['저가'] < df_cm_call.iloc[index]['고가']:

                if df_cm_call.iloc[index]['종가'] > 0:

                    df_cm_call.loc[index, '시가갭'] = df_cm_call.iloc[index]['시가'] - df_cm_call.iloc[index]['종가']
                    call_gap_percent[index] = (df_cm_call.iloc[index]['시가'] / df_cm_call.iloc[index]['종가'] - 1) * 100

                    gap_str = "{0:0.2f}({1:0.0f}%)".format(df_cm_call.iloc[index]['시가갭'], call_gap_percent[index])

                    if gap_str != self.tableWidget_call.item(index, Option_column.시가갭.value).text():

                        item = QTableWidgetItem(gap_str)
                        item.setTextAlignment(Qt.AlignCenter)
                        self.tableWidget_call.setItem(index, Option_column.시가갭.value, item)
                    else:
                        pass
                else:
                    pass

                if index > atm_index:
                    call_open_count += 1
                else:
                    pass

                if not call_open[index]:

                    if index != atm_index:
                        self.tableWidget_call.item(index, Option_column.행사가.value).setBackground(QBrush(녹색))
                    else:
                        pass

                    call_open[index] = True

                else:
                    pass

                # call OL/OH count
                if self.within_n_tick(df_cm_call.iloc[index]['시가'], df_cm_call.iloc[index]['저가'], 2) \
                        and not self.within_n_tick(df_cm_call.iloc[index]['시가'], df_cm_call.iloc[index]['고가'], 2):

                    if not call_ol[index]:

                        oloh_str = '↑'

                        if oloh_str != self.tableWidget_call.item(index, Option_column.OLOH.value).text():

                            df_cm_call.loc[index, 'OLOH'] = 'OL'
                            item = QTableWidgetItem("{0}".format(oloh_str))
                            item.setTextAlignment(Qt.AlignCenter)
                            item.setBackground(QBrush(적색))
                            item.setForeground(QBrush(흰색))
                            self.tableWidget_call.setItem(index, Option_column.OLOH.value, item)

                            call_ol[index] = True
                        else:
                            pass
                    else:
                        pass

                elif self.within_n_tick(df_cm_call.iloc[index]['시가'], df_cm_call.iloc[index]['고가'], 2) \
                        and not self.within_n_tick(df_cm_call.iloc[index]['시가'], df_cm_call.iloc[index]['저가'], 2):

                    if not call_oh[index]:

                        oloh_str = '↓'

                        if oloh_str != self.tableWidget_call.item(index, Option_column.OLOH.value).text():

                            df_cm_call.loc[index, 'OLOH'] = 'OH'
                            item = QTableWidgetItem("{0}".format(oloh_str))
                            item.setTextAlignment(Qt.AlignCenter)
                            item.setBackground(QBrush(청색))
                            item.setForeground(QBrush(흰색))
                            self.tableWidget_call.setItem(index, Option_column.OLOH.value, item)

                            call_oh[index] = True
                        else:
                            pass
                    else:
                        pass

                else:
                    oloh_str = ''

                    if oloh_str != self.tableWidget_call.item(index, Option_column.OLOH.value).text():

                        df_cm_call.loc[index, 'OLOH'] = ''
                        item = QTableWidgetItem("{0}".format(oloh_str))
                        item.setBackground(QBrush(기본바탕색))
                        item.setForeground(QBrush(검정색))
                        self.tableWidget_call.setItem(index, Option_column.OLOH.value, item)

                        call_ol[index] = False
                        call_oh[index] = False
                    else:
                        pass
            else:
                pass

        # Call 데이타 표시
        if call_open[nCount_cm_option_pairs - 1]:

            new_actval = repr(call_open_count) + '/' + repr(call_open.count(True)) + '*'
        else:
            new_actval = repr(call_open_count) + '/' + repr(call_open.count(True))

        if new_actval != self.tableWidget_call.horizontalHeaderItem(1).text():
            item = QTableWidgetItem(new_actval)
            self.tableWidget_call.setHorizontalHeaderItem(1, item)
        else:
            pass

        new_oloh = repr(call_ol.count(True)) + '/' + repr(call_oh.count(True))

        if new_oloh != self.tableWidget_call.horizontalHeaderItem(2).text():
            item = QTableWidgetItem(new_oloh)
            self.tableWidget_call.setHorizontalHeaderItem(2, item)
        else:
            pass

        temp = call_gap_percent[:]
        call_gap_percent_local = [value for value in temp if not math.isnan(value)]
        call_gap_percent_local.sort()

        #print('call_gap_percent', call_gap_percent)
        print('call_gap_percent_local', call_gap_percent_local)

        if call_gap_percent_local:
            tmp = np.array(call_gap_percent_local)
            mean = int(round(np.mean(tmp), 1))
            call_str = '시가갭' + '(' + repr(mean) + '%' + ')'

            if call_str != self.tableWidget_call.horizontalHeaderItem(Option_column.시가갭.value).text():
                item = QTableWidgetItem(call_str)
                self.tableWidget_call.setHorizontalHeaderItem(Option_column.시가갭.value, item)

                cm_call_시가 = df_cm_call['시가'].values.tolist()
                cm_call_시가_extend = self.make_color_list(cm_call_시가)

                cm_call_피봇 = df_cm_call['피봇'].values.tolist()
                cm_call_피봇_extend = self.make_color_list(cm_call_피봇)

                self.tableWidget_call.resizeColumnsToContents()
                self.tableWidget_call.setColumnWidth(0, 15)
            else:
                pass
        else:
            print('call_gap_percent_local is empty...')

    def call_db_check(self):

        for index in range(nCount_cm_option_pairs):

            if df_cm_call.iloc[index]['시가'] > 0.3 and df_cm_call.iloc[index]['저가'] < df_cm_call.iloc[index]['고가']:

                df_cm_call.loc[index, '대비'] = \
                    int((round((df_cm_call.iloc[index]['현재가'] - df_cm_call.iloc[index]['시가']), 2)) * 100)
                call_db_percent[index] = (df_cm_call.iloc[index]['현재가'] / df_cm_call.iloc[index]['시가'] - 1) * 100

                gap_str = "{0:0.0f}({1:0.0f}%)".format(df_cm_call.iloc[index]['대비'], call_db_percent[index])

                if gap_str != self.tableWidget_call.item(index, Option_column.대비.value).text():

                    item = QTableWidgetItem(gap_str)
                    item.setTextAlignment(Qt.AlignCenter)
                    self.tableWidget_call.setItem(index, Option_column.대비.value, item)
                else:
                    pass
            else:
                pass

        temp = call_db_percent[:]
        call_db_percent_local = [value for value in temp if not math.isnan(value)]
        call_db_percent_local.sort()

        #print('call_db_percent', call_db_percent)
        #print('call_db_percent_local', call_db_percent_local)

        if call_db_percent_local:
            tmp = np.array(call_db_percent_local)
            mean = int(round(np.mean(tmp), 1))
            call_str = repr(mean) + '%' + ' √'

            if call_str != self.tableWidget_call.horizontalHeaderItem(Option_column.대비.value).text():
                item = QTableWidgetItem(call_str)
                self.tableWidget_call.setHorizontalHeaderItem(Option_column.대비.value, item)
                self.tableWidget_call.resizeColumnsToContents()
                self.tableWidget_call.setColumnWidth(0, 15)
            else:
                pass
        else:
            print('call_db_percent_local is empty...')

    def put_open_check(self):

        global df_cm_put, put_open, put_ol, put_oh
        global put_gap_percent
        global cm_put_시가_extend, cm_put_피봇_extend

        put_open_count = 0

        for index in range(nCount_cm_option_pairs):

            if df_cm_put.iloc[index]['시가'] > 0.3 and df_cm_put.iloc[index]['저가'] < df_cm_put.iloc[index]['고가']:

                if df_cm_put.iloc[index]['종가'] > 0:

                    df_cm_put.loc[index, '시가갭'] = df_cm_put.iloc[index]['시가'] - df_cm_put.iloc[index]['종가']
                    put_gap_percent[index] = (df_cm_put.iloc[index]['시가'] / df_cm_put.iloc[index]['종가'] - 1) * 100

                    gap_str = "{0:0.2f}({1:0.0f}%)".format(df_cm_put.iloc[index]['시가갭'], put_gap_percent[index])

                    if gap_str != self.tableWidget_put.item(index, Option_column.시가갭.value).text():

                        item = QTableWidgetItem(gap_str)
                        item.setTextAlignment(Qt.AlignCenter)
                        self.tableWidget_put.setItem(index, Option_column.시가갭.value, item)
                    else:
                        pass
                else:
                    pass

                if index < atm_index:
                    put_open_count += 1
                else:
                    pass

                if not put_open[index]:

                    if index != atm_index:
                        self.tableWidget_put.item(index, Option_column.행사가.value).setBackground(QBrush(녹색))
                    else:
                        pass

                    put_open[index] = True

                else:
                    pass

                # put OL/OH count
                if self.within_n_tick(df_cm_put.iloc[index]['시가'], df_cm_put.iloc[index]['저가'], 2) \
                        and not self.within_n_tick(df_cm_put.iloc[index]['시가'], df_cm_put.iloc[index]['고가'], 2):

                    if not put_ol[index]:

                        oloh_str = '↑'

                        if oloh_str != self.tableWidget_put.item(index, Option_column.OLOH.value).text():

                            df_cm_put.loc[index, 'OLOH'] = 'OL'
                            item = QTableWidgetItem("{0}".format(oloh_str))
                            item.setTextAlignment(Qt.AlignCenter)
                            item.setBackground(QBrush(청색))
                            item.setForeground(QBrush(흰색))
                            self.tableWidget_put.setItem(index, Option_column.OLOH.value, item)

                            put_ol[index] = True
                        else:
                            pass
                    else:
                        pass

                elif self.within_n_tick(df_cm_put.iloc[index]['시가'], df_cm_put.iloc[index]['고가'], 2) \
                        and not self.within_n_tick(df_cm_put.iloc[index]['시가'], df_cm_put.iloc[index]['저가'], 2):

                    if not put_oh[index]:

                        oloh_str = '↓'

                        if oloh_str != self.tableWidget_put.item(index, Option_column.OLOH.value).text():

                            df_cm_put.loc[index, 'OLOH'] = 'OH'
                            item = QTableWidgetItem("{0}".format(oloh_str))
                            item.setTextAlignment(Qt.AlignCenter)
                            item.setBackground(QBrush(적색))
                            item.setForeground(QBrush(흰색))
                            self.tableWidget_put.setItem(index, Option_column.OLOH.value, item)

                            put_oh[index] = True
                        else:
                            pass
                    else:
                        pass

                else:
                    oloh_str = ''

                    if oloh_str != self.tableWidget_put.item(index, Option_column.OLOH.value).text():

                        df_cm_put.loc[index, 'OLOH'] = ''
                        item = QTableWidgetItem("{0}".format(oloh_str))
                        item.setBackground(QBrush(기본바탕색))
                        item.setForeground(QBrush(검정색))
                        self.tableWidget_put.setItem(index, Option_column.OLOH.value, item)

                        put_ol[index] = False
                        put_oh[index] = False
                    else:
                        pass
            else:
                pass

        # Put 데이타 표시
        if put_open[0]:

            new_actval = repr(put_open_count) + '/' + repr(put_open.count(True)) + '*'
        else:
            new_actval = repr(put_open_count) + '/' + repr(put_open.count(True))

        if new_actval != self.tableWidget_put.horizontalHeaderItem(1).text():
            item = QTableWidgetItem(new_actval)
            self.tableWidget_put.setHorizontalHeaderItem(1, item)
        else:
            pass

        new_oloh = repr(put_ol.count(True)) + '/' + repr(put_oh.count(True))

        if new_oloh != self.tableWidget_put.horizontalHeaderItem(2).text():
            item = QTableWidgetItem(new_oloh)
            self.tableWidget_put.setHorizontalHeaderItem(2, item)
        else:
            pass

        temp = put_gap_percent[:]
        put_gap_percent_local = [value for value in temp if not math.isnan(value)]
        put_gap_percent_local.sort()

        #print('put_gap_percent', put_gap_percent)
        print('put_gap_percent_local', put_gap_percent_local)

        if put_gap_percent_local:
            tmp = np.array(put_gap_percent_local)
            mean = int(round(np.mean(tmp), 1))
            put_str = '시가갭' + '(' + repr(mean) + '%' + ')'

            if put_str != self.tableWidget_put.horizontalHeaderItem(Option_column.시가갭.value).text():
                item = QTableWidgetItem(put_str)
                self.tableWidget_put.setHorizontalHeaderItem(Option_column.시가갭.value, item)

                cm_put_시가 = df_cm_put['시가'].values.tolist()
                cm_put_시가_extend = self.make_color_list(cm_put_시가)

                cm_put_피봇 = df_cm_put['피봇'].values.tolist()
                cm_put_피봇_extend = self.make_color_list(cm_put_피봇)

                self.tableWidget_put.resizeColumnsToContents()
                self.tableWidget_put.setColumnWidth(0, 15)
            else:
                pass
        else:
            print('put_gap_percent_local is empty...')

    def put_db_check(self):

        for index in range(nCount_cm_option_pairs):

            if df_cm_put.iloc[index]['시가'] > 0.3 and df_cm_put.iloc[index]['저가'] < df_cm_put.iloc[index]['고가']:

                df_cm_put.loc[index, '대비'] = \
                    int((round((df_cm_put.iloc[index]['현재가'] - df_cm_put.iloc[index]['시가']), 2)) * 100)
                put_db_percent[index] = (df_cm_put.iloc[index]['현재가'] / df_cm_put.iloc[index]['시가'] - 1) * 100

                gap_str = "{0:0.0f}({1:0.0f}%)".format(df_cm_put.iloc[index]['대비'], put_db_percent[index])

                if gap_str != self.tableWidget_put.item(index, Option_column.대비.value).text():

                    item = QTableWidgetItem(gap_str)
                    item.setTextAlignment(Qt.AlignCenter)
                    self.tableWidget_put.setItem(index, Option_column.대비.value, item)
                else:
                    pass
            else:
                pass

        temp = put_db_percent[:]
        put_db_percent_local = [value for value in temp if not math.isnan(value)]
        put_db_percent_local.sort()

        #print('put_db_percent', put_db_percent)
        #print('put_db_percent_local', put_db_percent_local)

        if put_db_percent_local:
            tmp = np.array(put_db_percent_local)
            mean = int(round(np.mean(tmp), 1))
            put_str = repr(mean) + '%' + ' √'

            if put_str != self.tableWidget_put.horizontalHeaderItem(Option_column.대비.value).text():
                item = QTableWidgetItem(put_str)
                self.tableWidget_put.setHorizontalHeaderItem(Option_column.대비.value, item)
                self.tableWidget_put.resizeColumnsToContents()
                self.tableWidget_put.setColumnWidth(0, 15)
            else:
                pass
        else:
            print('put_db_percent_local is empty...')

    # Call 컬러처리
    def call_color_clear(self):

        if call_scroll_end_position <= nCount_cm_option_pairs:

            for i in range(call_scroll_begin_position, call_scroll_end_position):

                self.tableWidget_call.item(i, Option_column.현재가.value).setBackground(QBrush(옅은회색))
        else:
            pass

    def call_low_color_clear(self):

        if call_scroll_end_position <= nCount_cm_option_pairs:

            for i in range(call_scroll_begin_position, call_scroll_end_position):

                self.tableWidget_call.item(i, Option_column.저가.value).setBackground(QBrush(기본바탕색))
                self.tableWidget_call.item(i, Option_column.저가.value).setForeground(QBrush(검정색))
        else:
            pass

    def call_high_color_clear(self):

        if call_scroll_end_position <= nCount_cm_option_pairs:

            for i in range(call_scroll_begin_position, call_scroll_end_position):

                self.tableWidget_call.item(i, Option_column.고가.value).setBackground(QBrush(기본바탕색))
                self.tableWidget_call.item(i, Option_column.고가.value).setForeground(QBrush(검정색))
        else:
            pass

    def call_node_color_clear(self):

        if call_scroll_end_position <= nCount_cm_option_pairs:

            for i in range(call_scroll_begin_position, call_scroll_end_position):

                if call_node_state['기준가']:
                    self.tableWidget_call.item(i, Option_column.기준가.value).setBackground(QBrush(기본바탕색))
                    self.tableWidget_call.item(i, Option_column.기준가.value).setForeground(QBrush(검정색))
                else:
                    pass

                if call_node_state['월저']:
                    self.tableWidget_call.item(i, Option_column.월저.value).setBackground(QBrush(기본바탕색))
                    self.tableWidget_call.item(i, Option_column.월저.value).setForeground(QBrush(검정색))
                else:
                    pass

                if call_node_state['월고']:
                    self.tableWidget_call.item(i, Option_column.월고.value).setBackground(QBrush(기본바탕색))
                    self.tableWidget_call.item(i, Option_column.월고.value).setForeground(QBrush(검정색))
                else:
                    pass

                if call_node_state['전저']:
                    self.tableWidget_call.item(i, Option_column.전저.value).setBackground(QBrush(기본바탕색))
                    self.tableWidget_call.item(i, Option_column.전저.value).setForeground(QBrush(검정색))
                else:
                    pass

                if call_node_state['전고']:
                    self.tableWidget_call.item(i, Option_column.전고.value).setBackground(QBrush(기본바탕색))
                    self.tableWidget_call.item(i, Option_column.전고.value).setForeground(QBrush(검정색))
                else:
                    pass

                if call_node_state['종가']:
                    self.tableWidget_call.item(i, Option_column.종가.value).setBackground(QBrush(기본바탕색))
                    self.tableWidget_call.item(i, Option_column.종가.value).setForeground(QBrush(검정색))
                else:
                    pass

                if call_node_state['피봇']:
                    self.tableWidget_call.item(i, Option_column.피봇.value).setBackground(QBrush(기본바탕색))
                    self.tableWidget_call.item(i, Option_column.피봇.value).setForeground(QBrush(검정색))
                else:
                    pass

                if call_node_state['시가']:
                    self.tableWidget_call.item(i, Option_column.시가.value).setBackground(QBrush(기본바탕색))

                    if df_cm_call.iloc[i]['시가'] > df_cm_call.iloc[i]['종가']:
                        self.tableWidget_call.item(i, Option_column.시가.value).setForeground(QBrush(적색))
                    elif df_cm_call.iloc[i]['시가'] < df_cm_call.iloc[i]['종가']:
                        self.tableWidget_call.item(i, Option_column.시가.value).setForeground(QBrush(청색))
                    else:
                        self.tableWidget_call.item(i, Option_column.시가.value).setForeground(QBrush(검정색))
                else:
                    pass

                self.tableWidget_call.item(i, Option_column.저가.value).setBackground(QBrush(기본바탕색))
                self.tableWidget_call.item(i, Option_column.저가.value).setForeground(QBrush(검정색))

                self.tableWidget_call.item(i, Option_column.고가.value).setBackground(QBrush(기본바탕색))
                self.tableWidget_call.item(i, Option_column.고가.value).setForeground(QBrush(검정색))
        else:
            pass

    def call_color_check(self):

        for i in range(nCount_cm_option_pairs):

            if df_cm_call.iloc[i]['저가'] in cm_put_종가_extend:

                self.tableWidget_call.item(i, Option_column.저가.value).setBackground(QBrush(Qt.darkCyan))
                self.tableWidget_call.item(i, Option_column.저가.value).setForeground(QBrush(흰색))
            else:
                pass

            if df_cm_call.iloc[i]['저가'] in cm_call_종가_extend:

                self.tableWidget_call.item(i, Option_column.저가.value).setBackground(QBrush(Qt.darkMagenta))
                self.tableWidget_call.item(i, Option_column.저가.value).setForeground(QBrush(흰색))
            else:
                pass

            if df_cm_call.iloc[i]['저가'] in cm_put_피봇_extend:

                self.tableWidget_call.item(i, Option_column.저가.value).setBackground(QBrush(풋피봇색))
                self.tableWidget_call.item(i, Option_column.저가.value).setForeground(QBrush(검정색))
            else:
                pass

            if df_cm_call.iloc[i]['저가'] in cm_call_피봇_extend:

                self.tableWidget_call.item(i, Option_column.저가.value).setBackground(QBrush(콜피봇색))
                self.tableWidget_call.item(i, Option_column.저가.value).setForeground(QBrush(검정색))
            else:
                pass

            if df_cm_call.iloc[i]['저가'] in cm_put_시가_extend:

                self.tableWidget_call.item(i, Option_column.저가.value).setBackground(QBrush(Qt.darkBlue))
                self.tableWidget_call.item(i, Option_column.저가.value).setForeground(QBrush(흰색))
            else:
                pass

            if df_cm_call.iloc[i]['저가'] in cm_call_시가_extend:

                self.tableWidget_call.item(i, Option_column.저가.value).setBackground(QBrush(Qt.darkRed))
                self.tableWidget_call.item(i, Option_column.저가.value).setForeground(QBrush(흰색))
            else:
                pass

            if df_cm_call.iloc[i]['저가'] in coreval:

                self.tableWidget_call.item(i, Option_column.저가.value).setBackground(QBrush(녹색))
                self.tableWidget_call.item(i, Option_column.저가.value).setForeground(QBrush(검정색))
            else:
                pass

            if df_cm_call.iloc[i]['고가'] in cm_put_종가_extend:

                self.tableWidget_call.item(i, Option_column.고가.value).setBackground(QBrush(Qt.darkCyan))
                self.tableWidget_call.item(i, Option_column.고가.value).setForeground(QBrush(흰색))
            else:
                pass

            if df_cm_call.iloc[i]['고가'] in cm_call_종가_extend:

                self.tableWidget_call.item(i, Option_column.고가.value).setBackground(QBrush(Qt.darkMagenta))
                self.tableWidget_call.item(i, Option_column.고가.value).setForeground(QBrush(흰색))
            else:
                pass

            if df_cm_call.iloc[i]['고가'] in cm_put_피봇_extend:

                self.tableWidget_call.item(i, Option_column.고가.value).setBackground(QBrush(풋피봇색))
                self.tableWidget_call.item(i, Option_column.고가.value).setForeground(QBrush(검정색))
            else:
                pass

            if df_cm_call.iloc[i]['고가'] in cm_call_피봇_extend:

                self.tableWidget_call.item(i, Option_column.고가.value).setBackground(QBrush(콜피봇색))
                self.tableWidget_call.item(i, Option_column.고가.value).setForeground(QBrush(검정색))
            else:
                pass

            if df_cm_call.iloc[i]['고가'] in cm_put_시가_extend:

                self.tableWidget_call.item(i, Option_column.고가.value).setBackground(QBrush(Qt.darkBlue))
                self.tableWidget_call.item(i, Option_column.고가.value).setForeground(QBrush(흰색))
            else:
                pass

            if df_cm_call.iloc[i]['고가'] in cm_call_시가_extend:

                self.tableWidget_call.item(i, Option_column.고가.value).setBackground(QBrush(Qt.darkRed))
                self.tableWidget_call.item(i, Option_column.고가.value).setForeground(QBrush(흰색))
            else:
                pass

            if df_cm_call.iloc[i]['고가'] in coreval:

                self.tableWidget_call.item(i, Option_column.고가.value).setBackground(QBrush(녹색))
                self.tableWidget_call.item(i, Option_column.고가.value).setForeground(QBrush(검정색))
            else:
                pass
    
    def callnode_color_check(self):

        start_time = timeit.default_timer()

        if put_scroll_end_position <= nCount_cm_option_pairs:

            for i in range(put_scroll_begin_position, put_scroll_end_position):
                
                # 풋 node 컬러링
                if put_node_state['기준가']:

                    if df_cm_put.iloc[i]['기준가'] in cm_call_저가_extend:

                        self.tableWidget_put.item(i, Option_column.기준가.value).setBackground(QBrush(풋기준가색))
                        self.tableWidget_put.item(i, Option_column.기준가.value).setForeground(QBrush(흰색))
                    else:
                        pass
						
                    if df_cm_put.iloc[i]['기준가'] in cm_call_고가_extend:

                        self.tableWidget_put.item(i, Option_column.기준가.value).setBackground(QBrush(풋기준가색))
                        self.tableWidget_put.item(i, Option_column.기준가.value).setForeground(QBrush(흰색))
                    else:
                        pass
                else:
                    pass

                if put_node_state['월저']:

                    if df_cm_put.iloc[i]['월저'] in cm_call_저가_extend:

                        self.tableWidget_put.item(i, Option_column.월저.value).setBackground(QBrush(풋월저색))
                        self.tableWidget_put.item(i, Option_column.월저.value).setForeground(QBrush(흰색))
                    else:
                        pass
						
                    if df_cm_put.iloc[i]['월저'] in cm_call_고가_extend:

                        self.tableWidget_put.item(i, Option_column.월저.value).setBackground(QBrush(풋월저색))
                        self.tableWidget_put.item(i, Option_column.월저.value).setForeground(QBrush(흰색))
                    else:
                        pass
                else:
                    pass

                if put_node_state['월고']:

                    if df_cm_put.iloc[i]['월고'] in cm_call_저가_extend:

                        self.tableWidget_put.item(i, Option_column.월고.value).setBackground(QBrush(풋월고색))
                        self.tableWidget_put.item(i, Option_column.월고.value).setForeground(QBrush(흰색))
                    else:
                        pass
						
                    if df_cm_put.iloc[i]['월고'] in cm_call_고가_extend:

                        self.tableWidget_put.item(i, Option_column.월고.value).setBackground(QBrush(풋월고색))
                        self.tableWidget_put.item(i, Option_column.월고.value).setForeground(QBrush(흰색))
                    else:
                        pass
                else:
                    pass

                if put_node_state['전저']:

                    if df_cm_put.iloc[i]['전저'] in cm_call_저가_extend:

                        self.tableWidget_put.item(i, Option_column.전저.value).setBackground(QBrush(풋전저색))
                        self.tableWidget_put.item(i, Option_column.전저.value).setForeground(QBrush(흰색))
                    else:
                        pass
						
                    if df_cm_put.iloc[i]['전저'] in cm_call_고가_extend:

                        self.tableWidget_put.item(i, Option_column.전저.value).setBackground(QBrush(풋전저색))
                        self.tableWidget_put.item(i, Option_column.전저.value).setForeground(QBrush(흰색))
                    else:
                        pass
                else:
                    pass

                if put_node_state['전고']:

                    if df_cm_put.iloc[i]['전고'] in cm_call_저가_extend:

                        self.tableWidget_put.item(i, Option_column.전고.value).setBackground(QBrush(풋전고색))
                        self.tableWidget_put.item(i, Option_column.전고.value).setForeground(QBrush(검정색))
                    else:
                        pass
						
                    if df_cm_put.iloc[i]['전고'] in cm_call_고가_extend:

                        self.tableWidget_put.item(i, Option_column.전고.value).setBackground(QBrush(풋전고색))
                        self.tableWidget_put.item(i, Option_column.전고.value).setForeground(QBrush(검정색))
                    else:
                        pass
                else:
                    pass

                if put_node_state['종가']:

                    if df_cm_put.iloc[i]['종가'] in cm_call_저가_extend:

                        self.tableWidget_put.item(i, Option_column.종가.value).setBackground(QBrush(풋종가색))
                        self.tableWidget_put.item(i, Option_column.종가.value).setForeground(QBrush(흰색))
                    else:
                        pass
						
                    if df_cm_put.iloc[i]['종가'] in cm_call_고가_extend:

                        self.tableWidget_put.item(i, Option_column.종가.value).setBackground(QBrush(풋종가색))
                        self.tableWidget_put.item(i, Option_column.종가.value).setForeground(QBrush(흰색))
                    else:
                        pass
                else:
                    pass

                if put_node_state['피봇']:

                    if df_cm_put.iloc[i]['피봇'] in cm_call_저가_extend:

                        self.tableWidget_put.item(i, Option_column.피봇.value).setBackground(QBrush(풋피봇색))
                        self.tableWidget_put.item(i, Option_column.피봇.value).setForeground(QBrush(검정색))
                    else:
                        pass
						
                    if df_cm_put.iloc[i]['피봇'] in cm_call_고가_extend:

                        self.tableWidget_put.item(i, Option_column.피봇.value).setBackground(QBrush(풋피봇색))
                        self.tableWidget_put.item(i, Option_column.피봇.value).setForeground(QBrush(검정색))
                    else:
                        pass
                else:
                    pass

                if put_node_state['시가']:

                    if df_cm_put.iloc[i]['시가'] in cm_call_저가_extend:

                        self.tableWidget_put.item(i, Option_column.시가.value).setBackground(QBrush(풋시가색))
                        self.tableWidget_put.item(i, Option_column.시가.value).setForeground(QBrush(흰색))
                    else:
                        pass
						
                    if df_cm_put.iloc[i]['시가'] in cm_call_고가_extend:

                        self.tableWidget_put.item(i, Option_column.시가.value).setBackground(QBrush(풋시가색))
                        self.tableWidget_put.item(i, Option_column.시가.value).setForeground(QBrush(흰색))
                    else:
                        pass
                else:
                    pass
        else:
            pass

        if call_scroll_end_position <= nCount_cm_option_pairs:            

            for i in range(call_scroll_begin_position, call_scroll_end_position):
                
                # 콜 node 컬러링
                if call_node_state['기준가']:

                    if df_cm_call.iloc[i]['기준가'] in cm_put_저가_extend:

                        self.tableWidget_call.item(i, Option_column.기준가.value).setBackground(QBrush(콜기준가색))
                        self.tableWidget_call.item(i, Option_column.기준가.value).setForeground(QBrush(흰색))
                    else:
                        pass

                    if df_cm_call.iloc[i]['기준가'] in cm_put_고가_extend:

                        self.tableWidget_call.item(i, Option_column.기준가.value).setBackground(QBrush(콜기준가색))
                        self.tableWidget_call.item(i, Option_column.기준가.value).setForeground(QBrush(흰색))
                    else:
                        pass

                    if df_cm_call.iloc[i]['기준가'] in cm_call_저가_extend:

                        self.tableWidget_call.item(i, Option_column.기준가.value).setBackground(QBrush(콜기준가색))
                        self.tableWidget_call.item(i, Option_column.기준가.value).setForeground(QBrush(흰색))
                    else:
                        pass

                    if df_cm_call.iloc[i]['기준가'] in cm_call_고가_extend:

                        self.tableWidget_call.item(i, Option_column.기준가.value).setBackground(QBrush(콜기준가색))
                        self.tableWidget_call.item(i, Option_column.기준가.value).setForeground(QBrush(흰색))
                    else:
                        pass

                    if df_cm_call.iloc[i]['저가'] in cm_call_기준가_extend:

                        self.tableWidget_call.item(i, Option_column.저가.value).setBackground(QBrush(콜기준가색))
                        self.tableWidget_call.item(i, Option_column.저가.value).setForeground(QBrush(흰색))
                    else:
                        pass

                    if df_cm_call.iloc[i]['고가'] in cm_call_기준가_extend:

                        self.tableWidget_call.item(i, Option_column.고가.value).setBackground(QBrush(콜기준가색))
                        self.tableWidget_call.item(i, Option_column.고가.value).setForeground(QBrush(흰색))
                    else:
                        pass
                else:
                    pass

                if call_node_state['월저']:

                    if df_cm_call.iloc[i]['월저'] in cm_put_저가_extend:

                        self.tableWidget_call.item(i, Option_column.월저.value).setBackground(QBrush(콜월저색))
                        self.tableWidget_call.item(i, Option_column.월저.value).setForeground(QBrush(검정색))
                    else:
                        pass

                    if df_cm_call.iloc[i]['월저'] in cm_put_고가_extend:

                        self.tableWidget_call.item(i, Option_column.월저.value).setBackground(QBrush(콜월저색))
                        self.tableWidget_call.item(i, Option_column.월저.value).setForeground(QBrush(검정색))
                    else:
                        pass

                    if df_cm_call.iloc[i]['월저'] in cm_call_저가_extend:

                        self.tableWidget_call.item(i, Option_column.월저.value).setBackground(QBrush(콜월저색))
                        self.tableWidget_call.item(i, Option_column.월저.value).setForeground(QBrush(검정색))
                    else:
                        pass

                    if df_cm_call.iloc[i]['월저'] in cm_call_고가_extend:

                        self.tableWidget_call.item(i, Option_column.월저.value).setBackground(QBrush(콜월저색))
                        self.tableWidget_call.item(i, Option_column.월저.value).setForeground(QBrush(검정색))
                    else:
                        pass

                    if df_cm_call.iloc[i]['저가'] in cm_call_월저_extend:

                        self.tableWidget_call.item(i, Option_column.저가.value).setBackground(QBrush(콜월저색))
                        self.tableWidget_call.item(i, Option_column.저가.value).setForeground(QBrush(검정색))
                    else:
                        pass

                    if df_cm_call.iloc[i]['고가'] in cm_call_월저_extend:

                        self.tableWidget_call.item(i, Option_column.고가.value).setBackground(QBrush(콜월저색))
                        self.tableWidget_call.item(i, Option_column.고가.value).setForeground(QBrush(검정색))
                    else:
                        pass
                else:
                    pass

                if call_node_state['월고']:

                    if df_cm_call.iloc[i]['월고'] in cm_put_저가_extend:

                        self.tableWidget_call.item(i, Option_column.월고.value).setBackground(QBrush(콜월고색))
                        self.tableWidget_call.item(i, Option_column.월고.value).setForeground(QBrush(흰색))
                    else:
                        pass

                    if df_cm_call.iloc[i]['월고'] in cm_put_고가_extend:

                        self.tableWidget_call.item(i, Option_column.월고.value).setBackground(QBrush(콜월고색))
                        self.tableWidget_call.item(i, Option_column.월고.value).setForeground(QBrush(흰색))
                    else:
                        pass

                    if df_cm_call.iloc[i]['월고'] in cm_call_저가_extend:

                        self.tableWidget_call.item(i, Option_column.월고.value).setBackground(QBrush(콜월고색))
                        self.tableWidget_call.item(i, Option_column.월고.value).setForeground(QBrush(흰색))
                    else:
                        pass

                    if df_cm_call.iloc[i]['월고'] in cm_call_고가_extend:

                        self.tableWidget_call.item(i, Option_column.월고.value).setBackground(QBrush(콜월고색))
                        self.tableWidget_call.item(i, Option_column.월고.value).setForeground(QBrush(흰색))
                    else:
                        pass

                    if df_cm_call.iloc[i]['저가'] in cm_call_월고_extend:

                        self.tableWidget_call.item(i, Option_column.저가.value).setBackground(QBrush(콜월고색))
                        self.tableWidget_call.item(i, Option_column.저가.value).setForeground(QBrush(흰색))
                    else:
                        pass

                    if df_cm_call.iloc[i]['고가'] in cm_call_월고_extend:

                        self.tableWidget_call.item(i, Option_column.고가.value).setBackground(QBrush(콜월고색))
                        self.tableWidget_call.item(i, Option_column.고가.value).setForeground(QBrush(흰색))
                    else:
                        pass
                else:
                    pass

                if call_node_state['전저']:

                    if df_cm_call.iloc[i]['전저'] in cm_put_저가_extend:

                        self.tableWidget_call.item(i, Option_column.전저.value).setBackground(QBrush(콜전저색))
                        self.tableWidget_call.item(i, Option_column.전저.value).setForeground(QBrush(검정색))
                    else:
                        pass

                    if df_cm_call.iloc[i]['전저'] in cm_put_고가_extend:

                        self.tableWidget_call.item(i, Option_column.전저.value).setBackground(QBrush(콜전저색))
                        self.tableWidget_call.item(i, Option_column.전저.value).setForeground(QBrush(검정색))
                    else:
                        pass

                    if df_cm_call.iloc[i]['전저'] in cm_call_저가_extend:

                        self.tableWidget_call.item(i, Option_column.전저.value).setBackground(QBrush(콜전저색))
                        self.tableWidget_call.item(i, Option_column.전저.value).setForeground(QBrush(검정색))
                    else:
                        pass

                    if df_cm_call.iloc[i]['전저'] in cm_call_고가_extend:

                        self.tableWidget_call.item(i, Option_column.전저.value).setBackground(QBrush(콜전저색))
                        self.tableWidget_call.item(i, Option_column.전저.value).setForeground(QBrush(검정색))
                    else:
                        pass

                    if df_cm_call.iloc[i]['저가'] in cm_call_전저_extend:

                        self.tableWidget_call.item(i, Option_column.저가.value).setBackground(QBrush(콜전저색))
                        self.tableWidget_call.item(i, Option_column.저가.value).setForeground(QBrush(검정색))
                    else:
                        pass

                    if df_cm_call.iloc[i]['고가'] in cm_call_전저_extend:

                        self.tableWidget_call.item(i, Option_column.고가.value).setBackground(QBrush(콜전저색))
                        self.tableWidget_call.item(i, Option_column.고가.value).setForeground(QBrush(검정색))
                    else:
                        pass
                else:
                    pass

                if call_node_state['전고']:

                    if df_cm_call.iloc[i]['전고'] in cm_put_저가_extend:

                        self.tableWidget_call.item(i, Option_column.전고.value).setBackground(QBrush(콜전고색))
                        self.tableWidget_call.item(i, Option_column.전고.value).setForeground(QBrush(검정색))
                    else:
                        pass

                    if df_cm_call.iloc[i]['전고'] in cm_put_고가_extend:

                        self.tableWidget_call.item(i, Option_column.전고.value).setBackground(QBrush(콜전고색))
                        self.tableWidget_call.item(i, Option_column.전고.value).setForeground(QBrush(검정색))
                    else:
                        pass

                    if df_cm_call.iloc[i]['전고'] in cm_call_저가_extend:

                        self.tableWidget_call.item(i, Option_column.전고.value).setBackground(QBrush(콜전고색))
                        self.tableWidget_call.item(i, Option_column.전고.value).setForeground(QBrush(검정색))
                    else:
                        pass

                    if df_cm_call.iloc[i]['전고'] in cm_call_고가_extend:

                        self.tableWidget_call.item(i, Option_column.전고.value).setBackground(QBrush(콜전고색))
                        self.tableWidget_call.item(i, Option_column.전고.value).setForeground(QBrush(검정색))
                    else:
                        pass

                    if df_cm_call.iloc[i]['저가'] in cm_call_전고_extend:

                        self.tableWidget_call.item(i, Option_column.저가.value).setBackground(QBrush(콜전고색))
                        self.tableWidget_call.item(i, Option_column.저가.value).setForeground(QBrush(검정색))
                    else:
                        pass

                    if df_cm_call.iloc[i]['고가'] in cm_call_전고_extend:

                        self.tableWidget_call.item(i, Option_column.고가.value).setBackground(QBrush(콜전고색))
                        self.tableWidget_call.item(i, Option_column.고가.value).setForeground(QBrush(검정색))
                    else:
                        pass
                else:
                    pass

                if call_node_state['종가']:

                    if df_cm_call.iloc[i]['종가'] in cm_put_저가_extend:

                        self.tableWidget_call.item(i, Option_column.종가.value).setBackground(QBrush(콜종가색))
                        self.tableWidget_call.item(i, Option_column.종가.value).setForeground(QBrush(흰색))
                    else:
                        pass

                    if df_cm_call.iloc[i]['종가'] in cm_put_고가_extend:

                        self.tableWidget_call.item(i, Option_column.종가.value).setBackground(QBrush(콜종가색))
                        self.tableWidget_call.item(i, Option_column.종가.value).setForeground(QBrush(흰색))
                    else:
                        pass

                    if df_cm_call.iloc[i]['종가'] in cm_call_저가_extend:

                        self.tableWidget_call.item(i, Option_column.종가.value).setBackground(QBrush(콜종가색))
                        self.tableWidget_call.item(i, Option_column.종가.value).setForeground(QBrush(흰색))
                    else:
                        pass

                    if df_cm_call.iloc[i]['종가'] in cm_call_고가_extend:

                        self.tableWidget_call.item(i, Option_column.종가.value).setBackground(QBrush(콜종가색))
                        self.tableWidget_call.item(i, Option_column.종가.value).setForeground(QBrush(흰색))
                    else:
                        pass

                    if df_cm_call.iloc[i]['저가'] in cm_call_종가_extend:

                        self.tableWidget_call.item(i, Option_column.저가.value).setBackground(QBrush(콜종가색))
                        self.tableWidget_call.item(i, Option_column.저가.value).setForeground(QBrush(흰색))
                    else:
                        pass

                    if df_cm_call.iloc[i]['고가'] in cm_call_종가_extend:

                        self.tableWidget_call.item(i, Option_column.고가.value).setBackground(QBrush(콜종가색))
                        self.tableWidget_call.item(i, Option_column.고가.value).setForeground(QBrush(흰색))
                    else:
                        pass
                else:
                    pass

                if call_node_state['피봇']:

                    if df_cm_call.iloc[i]['피봇'] in cm_put_저가_extend:

                        self.tableWidget_call.item(i, Option_column.피봇.value).setBackground(QBrush(콜피봇색))
                        self.tableWidget_call.item(i, Option_column.피봇.value).setForeground(QBrush(검정색))
                    else:
                        pass

                    if df_cm_call.iloc[i]['피봇'] in cm_put_고가_extend:

                        self.tableWidget_call.item(i, Option_column.피봇.value).setBackground(QBrush(콜피봇색))
                        self.tableWidget_call.item(i, Option_column.피봇.value).setForeground(QBrush(검정색))
                    else:
                        pass

                    if df_cm_call.iloc[i]['피봇'] in cm_call_저가_extend:

                        self.tableWidget_call.item(i, Option_column.피봇.value).setBackground(QBrush(콜피봇색))
                        self.tableWidget_call.item(i, Option_column.피봇.value).setForeground(QBrush(검정색))
                    else:
                        pass

                    if df_cm_call.iloc[i]['피봇'] in cm_call_고가_extend:

                        self.tableWidget_call.item(i, Option_column.피봇.value).setBackground(QBrush(콜피봇색))
                        self.tableWidget_call.item(i, Option_column.피봇.value).setForeground(QBrush(검정색))
                    else:
                        pass

                    if df_cm_call.iloc[i]['저가'] in cm_call_피봇_extend:

                        self.tableWidget_call.item(i, Option_column.저가.value).setBackground(QBrush(콜피봇색))
                        self.tableWidget_call.item(i, Option_column.저가.value).setForeground(QBrush(검정색))
                    else:
                        pass

                    if df_cm_call.iloc[i]['고가'] in cm_call_피봇_extend:

                        self.tableWidget_call.item(i, Option_column.고가.value).setBackground(QBrush(콜피봇색))
                        self.tableWidget_call.item(i, Option_column.고가.value).setForeground(QBrush(검정색))
                    else:
                        pass
                else:
                    pass

                if call_node_state['시가']:

                    if df_cm_call.iloc[i]['시가'] in cm_put_저가_extend:

                        self.tableWidget_call.item(i, Option_column.시가.value).setBackground(QBrush(콜시가색))
                        self.tableWidget_call.item(i, Option_column.시가.value).setForeground(QBrush(흰색))
                    else:
                        pass

                    if df_cm_call.iloc[i]['시가'] in cm_put_고가_extend:

                        self.tableWidget_call.item(i, Option_column.시가.value).setBackground(QBrush(콜시가색))
                        self.tableWidget_call.item(i, Option_column.시가.value).setForeground(QBrush(흰색))
                    else:
                        pass

                    if df_cm_call.iloc[i]['시가'] in cm_call_저가_extend:

                        self.tableWidget_call.item(i, Option_column.시가.value).setBackground(QBrush(콜시가색))
                        self.tableWidget_call.item(i, Option_column.시가.value).setForeground(QBrush(흰색))
                    else:
                        pass

                    if df_cm_call.iloc[i]['시가'] in cm_call_고가_extend:

                        self.tableWidget_call.item(i, Option_column.시가.value).setBackground(QBrush(콜시가색))
                        self.tableWidget_call.item(i, Option_column.시가.value).setForeground(QBrush(흰색))
                    else:
                        pass

                    if df_cm_call.iloc[i]['저가'] in cm_call_시가_extend:

                        self.tableWidget_call.item(i, Option_column.저가.value).setBackground(QBrush(콜시가색))
                        self.tableWidget_call.item(i, Option_column.저가.value).setForeground(QBrush(흰색))
                    else:
                        pass

                    if df_cm_call.iloc[i]['고가'] in cm_call_시가_extend:

                        self.tableWidget_call.item(i, Option_column.고가.value).setBackground(QBrush(콜시가색))
                        self.tableWidget_call.item(i, Option_column.고가.value).setForeground(QBrush(흰색))
                    else:
                        pass
                else:
                    pass
                
                # 풋 node 컬러링
                if put_node_state['기준가']:

                    if df_cm_call.iloc[i]['저가'] in cm_put_기준가_extend:

                        self.tableWidget_call.item(i, Option_column.저가.value).setBackground(QBrush(풋기준가색))
                        self.tableWidget_call.item(i, Option_column.저가.value).setForeground(QBrush(흰색))
                    else:
                        pass

                    if df_cm_call.iloc[i]['고가'] in cm_put_기준가_extend:

                        self.tableWidget_call.item(i, Option_column.고가.value).setBackground(QBrush(풋기준가색))
                        self.tableWidget_call.item(i, Option_column.고가.value).setForeground(QBrush(흰색))
                    else:
                        pass
                else:
                    pass

                if put_node_state['월저']:

                    if df_cm_call.iloc[i]['저가'] in cm_put_월저_extend:

                        self.tableWidget_call.item(i, Option_column.저가.value).setBackground(QBrush(풋월저색))
                        self.tableWidget_call.item(i, Option_column.저가.value).setForeground(QBrush(흰색))
                    else:
                        pass

                    if df_cm_call.iloc[i]['고가'] in cm_put_월저_extend:

                        self.tableWidget_call.item(i, Option_column.고가.value).setBackground(QBrush(풋월저색))
                        self.tableWidget_call.item(i, Option_column.고가.value).setForeground(QBrush(흰색))
                    else:
                        pass
                else:
                    pass

                if put_node_state['월고']:

                    if df_cm_call.iloc[i]['저가'] in cm_put_월고_extend:

                        self.tableWidget_call.item(i, Option_column.저가.value).setBackground(QBrush(풋월고색))
                        self.tableWidget_call.item(i, Option_column.저가.value).setForeground(QBrush(흰색))
                    else:
                        pass

                    if df_cm_call.iloc[i]['고가'] in cm_put_월고_extend:

                        self.tableWidget_call.item(i, Option_column.고가.value).setBackground(QBrush(풋월고색))
                        self.tableWidget_call.item(i, Option_column.고가.value).setForeground(QBrush(흰색))
                    else:
                        pass
                else:
                    pass

                if put_node_state['전저']:

                    if df_cm_call.iloc[i]['저가'] in cm_put_전저_extend:

                        self.tableWidget_call.item(i, Option_column.저가.value).setBackground(QBrush(풋전저색))
                        self.tableWidget_call.item(i, Option_column.저가.value).setForeground(QBrush(흰색))
                    else:
                        pass

                    if df_cm_call.iloc[i]['고가'] in cm_put_전저_extend:

                        self.tableWidget_call.item(i, Option_column.고가.value).setBackground(QBrush(풋전저색))
                        self.tableWidget_call.item(i, Option_column.고가.value).setForeground(QBrush(흰색))
                    else:
                        pass
                else:
                    pass

                if put_node_state['전고']:

                    if df_cm_call.iloc[i]['저가'] in cm_put_전고_extend:

                        self.tableWidget_call.item(i, Option_column.저가.value).setBackground(QBrush(풋전고색))
                        self.tableWidget_call.item(i, Option_column.저가.value).setForeground(QBrush(검정색))
                    else:
                        pass

                    if df_cm_call.iloc[i]['고가'] in cm_put_전고_extend:

                        self.tableWidget_call.item(i, Option_column.고가.value).setBackground(QBrush(풋전고색))
                        self.tableWidget_call.item(i, Option_column.고가.value).setForeground(QBrush(검정색))
                    else:
                        pass
                else:
                    pass

                if put_node_state['종가']:

                    if df_cm_call.iloc[i]['저가'] in cm_put_종가_extend:

                        self.tableWidget_call.item(i, Option_column.저가.value).setBackground(QBrush(풋종가색))
                        self.tableWidget_call.item(i, Option_column.저가.value).setForeground(QBrush(흰색))
                    else:
                        pass

                    if df_cm_call.iloc[i]['고가'] in cm_put_종가_extend:

                        self.tableWidget_call.item(i, Option_column.고가.value).setBackground(QBrush(풋종가색))
                        self.tableWidget_call.item(i, Option_column.고가.value).setForeground(QBrush(흰색))
                    else:
                        pass
                else:
                    pass

                if put_node_state['피봇']:

                    if df_cm_call.iloc[i]['저가'] in cm_put_피봇_extend:

                        self.tableWidget_call.item(i, Option_column.저가.value).setBackground(QBrush(풋피봇색))
                        self.tableWidget_call.item(i, Option_column.저가.value).setForeground(QBrush(검정색))
                    else:
                        pass

                    if df_cm_call.iloc[i]['고가'] in cm_put_피봇_extend:

                        self.tableWidget_call.item(i, Option_column.고가.value).setBackground(QBrush(풋피봇색))
                        self.tableWidget_call.item(i, Option_column.고가.value).setForeground(QBrush(검정색))
                    else:
                        pass
                else:
                    pass

                if put_node_state['시가']:

                    if df_cm_call.iloc[i]['저가'] in cm_put_시가_extend:

                        self.tableWidget_call.item(i, Option_column.저가.value).setBackground(QBrush(풋시가색))
                        self.tableWidget_call.item(i, Option_column.저가.value).setForeground(QBrush(흰색))
                    else:
                        pass

                    if df_cm_call.iloc[i]['고가'] in cm_put_시가_extend:

                        self.tableWidget_call.item(i, Option_column.고가.value).setBackground(QBrush(풋시가색))
                        self.tableWidget_call.item(i, Option_column.고가.value).setForeground(QBrush(흰색))
                    else:
                        pass
                else:
                    pass

                if df_cm_call.iloc[i]['저가'] in coreval:

                    self.tableWidget_call.item(i, Option_column.저가.value).setBackground(QBrush(대맥점색))
                    self.tableWidget_call.item(i, Option_column.저가.value).setForeground(QBrush(검정색))
                else:
                    pass

                if df_cm_call.iloc[i]['고가'] in coreval:

                    self.tableWidget_call.item(i, Option_column.고가.value).setBackground(QBrush(대맥점색))
                    self.tableWidget_call.item(i, Option_column.고가.value).setForeground(QBrush(검정색))
                else:
                    pass            
        else:
            pass        
			
        process_time = (timeit.default_timer() - start_time) * 1000
        print('call color check process time : %.2f ms' % process_time)

        str = '[{0:02d}:{1:02d}:{2:02d}] Call color check time : {3:0.2f} ms\r'.format(delta_hour, delta_minute, delta_sec, process_time)
        self.textBrowser.append(str)

    def call_low_update_color_check(self):
	
        start_time = timeit.default_timer()

        if put_scroll_end_position <= nCount_cm_option_pairs:

            for i in range(put_scroll_begin_position, put_scroll_end_position):
                
                # 풋 node 컬러링
                if put_node_state['기준가']:

                    if df_cm_put.iloc[i]['기준가'] in cm_call_저가_extend:

                        self.tableWidget_put.item(i, Option_column.기준가.value).setBackground(QBrush(풋기준가색))
                        self.tableWidget_put.item(i, Option_column.기준가.value).setForeground(QBrush(흰색))
                    else:
                        pass
                else:
                    pass

                if put_node_state['월저']:

                    if df_cm_put.iloc[i]['월저'] in cm_call_저가_extend:

                        self.tableWidget_put.item(i, Option_column.월저.value).setBackground(QBrush(풋월저색))
                        self.tableWidget_put.item(i, Option_column.월저.value).setForeground(QBrush(흰색))
                    else:
                        pass
                else:
                    pass

                if put_node_state['월고']:

                    if df_cm_put.iloc[i]['월고'] in cm_call_저가_extend:

                        self.tableWidget_put.item(i, Option_column.월고.value).setBackground(QBrush(풋월고색))
                        self.tableWidget_put.item(i, Option_column.월고.value).setForeground(QBrush(흰색))
                    else:
                        pass
                else:
                    pass

                if put_node_state['전저']:

                    if df_cm_put.iloc[i]['전저'] in cm_call_저가_extend:

                        self.tableWidget_put.item(i, Option_column.전저.value).setBackground(QBrush(풋전저색))
                        self.tableWidget_put.item(i, Option_column.전저.value).setForeground(QBrush(흰색))
                    else:
                        pass
                else:
                    pass

                if put_node_state['전고']:

                    if df_cm_put.iloc[i]['전고'] in cm_call_저가_extend:

                        self.tableWidget_put.item(i, Option_column.전고.value).setBackground(QBrush(풋전고색))
                        self.tableWidget_put.item(i, Option_column.전고.value).setForeground(QBrush(검정색))
                    else:
                        pass
                else:
                    pass

                if put_node_state['종가']:

                    if df_cm_put.iloc[i]['종가'] in cm_call_저가_extend:

                        self.tableWidget_put.item(i, Option_column.종가.value).setBackground(QBrush(풋종가색))
                        self.tableWidget_put.item(i, Option_column.종가.value).setForeground(QBrush(흰색))
                    else:
                        pass
                else:
                    pass

                if put_node_state['피봇']:

                    if df_cm_put.iloc[i]['피봇'] in cm_call_저가_extend:

                        self.tableWidget_put.item(i, Option_column.피봇.value).setBackground(QBrush(풋피봇색))
                        self.tableWidget_put.item(i, Option_column.피봇.value).setForeground(QBrush(검정색))
                    else:
                        pass
                else:
                    pass

                if put_node_state['시가']:

                    if df_cm_put.iloc[i]['시가'] in cm_call_저가_extend:

                        self.tableWidget_put.item(i, Option_column.시가.value).setBackground(QBrush(풋시가색))
                        self.tableWidget_put.item(i, Option_column.시가.value).setForeground(QBrush(흰색))
                    else:
                        pass
                else:
                    pass
        else:
            pass

        if call_scroll_end_position <= nCount_cm_option_pairs:            

            for i in range(call_scroll_begin_position, call_scroll_end_position):
                
                # 콜 node 컬러링
                if call_node_state['기준가']:

                    if df_cm_call.iloc[i]['기준가'] in cm_call_저가_extend:

                        self.tableWidget_call.item(i, Option_column.기준가.value).setBackground(QBrush(콜기준가색))
                        self.tableWidget_call.item(i, Option_column.기준가.value).setForeground(QBrush(흰색))
                    else:
                        pass

                    if df_cm_call.iloc[i]['저가'] in cm_call_기준가_extend:

                        self.tableWidget_call.item(i, Option_column.저가.value).setBackground(QBrush(콜기준가색))
                        self.tableWidget_call.item(i, Option_column.저가.value).setForeground(QBrush(흰색))
                    else:
                        pass
                else:
                    pass

                if call_node_state['월저']:

                    if df_cm_call.iloc[i]['월저'] in cm_call_저가_extend:

                        self.tableWidget_call.item(i, Option_column.월저.value).setBackground(QBrush(콜월저색))
                        self.tableWidget_call.item(i, Option_column.월저.value).setForeground(QBrush(검정색))
                    else:
                        pass

                    if df_cm_call.iloc[i]['저가'] in cm_call_월저_extend:

                        self.tableWidget_call.item(i, Option_column.저가.value).setBackground(QBrush(콜월저색))
                        self.tableWidget_call.item(i, Option_column.저가.value).setForeground(QBrush(검정색))
                    else:
                        pass
                else:
                    pass

                if call_node_state['월고']:

                    if df_cm_call.iloc[i]['월고'] in cm_call_저가_extend:

                        self.tableWidget_call.item(i, Option_column.월고.value).setBackground(QBrush(콜월고색))
                        self.tableWidget_call.item(i, Option_column.월고.value).setForeground(QBrush(흰색))
                    else:
                        pass

                    if df_cm_call.iloc[i]['저가'] in cm_call_월고_extend:

                        self.tableWidget_call.item(i, Option_column.저가.value).setBackground(QBrush(콜월고색))
                        self.tableWidget_call.item(i, Option_column.저가.value).setForeground(QBrush(흰색))
                    else:
                        pass
                else:
                    pass

                if call_node_state['전저']:

                    if df_cm_call.iloc[i]['전저'] in cm_call_저가_extend:

                        self.tableWidget_call.item(i, Option_column.전저.value).setBackground(QBrush(콜전저색))
                        self.tableWidget_call.item(i, Option_column.전저.value).setForeground(QBrush(검정색))
                    else:
                        pass

                    if df_cm_call.iloc[i]['저가'] in cm_call_전저_extend:

                        self.tableWidget_call.item(i, Option_column.저가.value).setBackground(QBrush(콜전저색))
                        self.tableWidget_call.item(i, Option_column.저가.value).setForeground(QBrush(검정색))
                    else:
                        pass
                else:
                    pass

                if call_node_state['전고']:

                    if df_cm_call.iloc[i]['전고'] in cm_call_저가_extend:

                        self.tableWidget_call.item(i, Option_column.전고.value).setBackground(QBrush(콜전고색))
                        self.tableWidget_call.item(i, Option_column.전고.value).setForeground(QBrush(검정색))
                    else:
                        pass

                    if df_cm_call.iloc[i]['저가'] in cm_call_전고_extend:

                        self.tableWidget_call.item(i, Option_column.저가.value).setBackground(QBrush(콜전고색))
                        self.tableWidget_call.item(i, Option_column.저가.value).setForeground(QBrush(검정색))
                    else:
                        pass
                else:
                    pass

                if call_node_state['종가']:

                    if df_cm_call.iloc[i]['종가'] in cm_call_저가_extend:

                        self.tableWidget_call.item(i, Option_column.종가.value).setBackground(QBrush(콜종가색))
                        self.tableWidget_call.item(i, Option_column.종가.value).setForeground(QBrush(흰색))
                    else:
                        pass

                    if df_cm_call.iloc[i]['저가'] in cm_call_종가_extend:

                        self.tableWidget_call.item(i, Option_column.저가.value).setBackground(QBrush(콜종가색))
                        self.tableWidget_call.item(i, Option_column.저가.value).setForeground(QBrush(흰색))
                    else:
                        pass
                else:
                    pass

                if call_node_state['피봇']:

                    if df_cm_call.iloc[i]['피봇'] in cm_call_저가_extend:

                        self.tableWidget_call.item(i, Option_column.피봇.value).setBackground(QBrush(콜피봇색))
                        self.tableWidget_call.item(i, Option_column.피봇.value).setForeground(QBrush(검정색))
                    else:
                        pass

                    if df_cm_call.iloc[i]['저가'] in cm_call_피봇_extend:

                        self.tableWidget_call.item(i, Option_column.저가.value).setBackground(QBrush(콜피봇색))
                        self.tableWidget_call.item(i, Option_column.저가.value).setForeground(QBrush(검정색))
                    else:
                        pass
                else:
                    pass

                if call_node_state['시가']:

                    if df_cm_call.iloc[i]['시가'] in cm_call_저가_extend:

                        self.tableWidget_call.item(i, Option_column.시가.value).setBackground(QBrush(콜시가색))
                        self.tableWidget_call.item(i, Option_column.시가.value).setForeground(QBrush(흰색))
                    else:
                        pass

                    if df_cm_call.iloc[i]['저가'] in cm_call_시가_extend:

                        self.tableWidget_call.item(i, Option_column.저가.value).setBackground(QBrush(콜시가색))
                        self.tableWidget_call.item(i, Option_column.저가.value).setForeground(QBrush(흰색))
                    else:
                        pass
                else:
                    pass
                
                # 풋 node 컬러링
                if put_node_state['기준가']:

                    if df_cm_call.iloc[i]['저가'] in cm_put_기준가_extend:

                        self.tableWidget_call.item(i, Option_column.저가.value).setBackground(QBrush(풋기준가색))
                        self.tableWidget_call.item(i, Option_column.저가.value).setForeground(QBrush(흰색))
                    else:
                        pass
                else:
                    pass

                if put_node_state['월저']:

                    if df_cm_call.iloc[i]['저가'] in cm_put_월저_extend:

                        self.tableWidget_call.item(i, Option_column.저가.value).setBackground(QBrush(풋월저색))
                        self.tableWidget_call.item(i, Option_column.저가.value).setForeground(QBrush(흰색))
                    else:
                        pass
                else:
                    pass

                if put_node_state['월고']:

                    if df_cm_call.iloc[i]['저가'] in cm_put_월고_extend:

                        self.tableWidget_call.item(i, Option_column.저가.value).setBackground(QBrush(풋월고색))
                        self.tableWidget_call.item(i, Option_column.저가.value).setForeground(QBrush(흰색))
                    else:
                        pass
                else:
                    pass

                if put_node_state['전저']:

                    if df_cm_call.iloc[i]['저가'] in cm_put_전저_extend:

                        self.tableWidget_call.item(i, Option_column.저가.value).setBackground(QBrush(풋전저색))
                        self.tableWidget_call.item(i, Option_column.저가.value).setForeground(QBrush(흰색))
                    else:
                        pass
                else:
                    pass

                if put_node_state['전고']:

                    if df_cm_call.iloc[i]['저가'] in cm_put_전고_extend:

                        self.tableWidget_call.item(i, Option_column.저가.value).setBackground(QBrush(풋전고색))
                        self.tableWidget_call.item(i, Option_column.저가.value).setForeground(QBrush(검정색))
                    else:
                        pass
                else:
                    pass

                if put_node_state['종가']:

                    if df_cm_call.iloc[i]['저가'] in cm_put_종가_extend:

                        self.tableWidget_call.item(i, Option_column.저가.value).setBackground(QBrush(풋종가색))
                        self.tableWidget_call.item(i, Option_column.저가.value).setForeground(QBrush(흰색))
                    else:
                        pass
                else:
                    pass

                if put_node_state['피봇']:

                    if df_cm_call.iloc[i]['저가'] in cm_put_피봇_extend:

                        self.tableWidget_call.item(i, Option_column.저가.value).setBackground(QBrush(풋피봇색))
                        self.tableWidget_call.item(i, Option_column.저가.value).setForeground(QBrush(검정색))
                    else:
                        pass
                else:
                    pass

                if put_node_state['시가']:

                    if df_cm_call.iloc[i]['저가'] in cm_put_시가_extend:

                        self.tableWidget_call.item(i, Option_column.저가.value).setBackground(QBrush(풋시가색))
                        self.tableWidget_call.item(i, Option_column.저가.value).setForeground(QBrush(흰색))
                    else:
                        pass
                else:
                    pass

                if df_cm_call.iloc[i]['저가'] in coreval:

                    self.tableWidget_call.item(i, Option_column.저가.value).setBackground(QBrush(대맥점색))
                    self.tableWidget_call.item(i, Option_column.저가.value).setForeground(QBrush(검정색))
                else:
                    pass
        else:
            pass        

        process_time = (timeit.default_timer() - start_time) * 1000
        print('call low color update check process time : %.2f ms' % process_time)

        str = '[{0:02d}:{1:02d}:{2:02d}] Call low color update : {3:0.2f} ms\r'.format(delta_hour, delta_minute, delta_sec, process_time)
        self.textBrowser.append(str)	

    def call_high_update_color_check(self):
	
        start_time = timeit.default_timer()

        if put_scroll_end_position <= nCount_cm_option_pairs:

            for i in range(put_scroll_begin_position, put_scroll_end_position):
                
                # 풋 node 컬러링
                if put_node_state['기준가']:

                    if df_cm_put.iloc[i]['기준가'] in cm_call_고가_extend:

                        self.tableWidget_put.item(i, Option_column.기준가.value).setBackground(QBrush(풋기준가색))
                        self.tableWidget_put.item(i, Option_column.기준가.value).setForeground(QBrush(흰색))
                    else:
                        pass
                else:
                    pass

                if put_node_state['월저']:

                    if df_cm_put.iloc[i]['월저'] in cm_call_고가_extend:

                        self.tableWidget_put.item(i, Option_column.월저.value).setBackground(QBrush(풋월저색))
                        self.tableWidget_put.item(i, Option_column.월저.value).setForeground(QBrush(흰색))
                    else:
                        pass
                else:
                    pass

                if put_node_state['월고']:

                    if df_cm_put.iloc[i]['월고'] in cm_call_고가_extend:

                        self.tableWidget_put.item(i, Option_column.월고.value).setBackground(QBrush(풋월고색))
                        self.tableWidget_put.item(i, Option_column.월고.value).setForeground(QBrush(흰색))
                    else:
                        pass
                else:
                    pass

                if put_node_state['전저']:

                    if df_cm_put.iloc[i]['전저'] in cm_call_고가_extend:

                        self.tableWidget_put.item(i, Option_column.전저.value).setBackground(QBrush(풋전저색))
                        self.tableWidget_put.item(i, Option_column.전저.value).setForeground(QBrush(흰색))
                    else:
                        pass
                else:
                    pass

                if put_node_state['전고']:

                    if df_cm_put.iloc[i]['전고'] in cm_call_고가_extend:

                        self.tableWidget_put.item(i, Option_column.전고.value).setBackground(QBrush(풋전고색))
                        self.tableWidget_put.item(i, Option_column.전고.value).setForeground(QBrush(검정색))
                    else:
                        pass
                else:
                    pass

                if put_node_state['종가']:

                    if df_cm_put.iloc[i]['종가'] in cm_call_고가_extend:

                        self.tableWidget_put.item(i, Option_column.종가.value).setBackground(QBrush(풋종가색))
                        self.tableWidget_put.item(i, Option_column.종가.value).setForeground(QBrush(흰색))
                    else:
                        pass
                else:
                    pass

                if put_node_state['피봇']:

                    if df_cm_put.iloc[i]['피봇'] in cm_call_고가_extend:

                        self.tableWidget_put.item(i, Option_column.피봇.value).setBackground(QBrush(풋피봇색))
                        self.tableWidget_put.item(i, Option_column.피봇.value).setForeground(QBrush(검정색))
                    else:
                        pass
                else:
                    pass

                if put_node_state['시가']:

                    if df_cm_put.iloc[i]['시가'] in cm_call_고가_extend:

                        self.tableWidget_put.item(i, Option_column.시가.value).setBackground(QBrush(풋시가색))
                        self.tableWidget_put.item(i, Option_column.시가.value).setForeground(QBrush(흰색))
                    else:
                        pass
                else:
                    pass
        else:
            pass

        if call_scroll_end_position <= nCount_cm_option_pairs:            

            for i in range(call_scroll_begin_position, call_scroll_end_position):
                
                # 콜 node 컬러링
                if call_node_state['기준가']:

                    if df_cm_call.iloc[i]['기준가'] in cm_call_고가_extend:

                        self.tableWidget_call.item(i, Option_column.기준가.value).setBackground(QBrush(콜기준가색))
                        self.tableWidget_call.item(i, Option_column.기준가.value).setForeground(QBrush(흰색))
                    else:
                        pass

                    if df_cm_call.iloc[i]['고가'] in cm_call_기준가_extend:

                        self.tableWidget_call.item(i, Option_column.고가.value).setBackground(QBrush(콜기준가색))
                        self.tableWidget_call.item(i, Option_column.고가.value).setForeground(QBrush(흰색))
                    else:
                        pass
                else:
                    pass

                if call_node_state['월저']:

                    if df_cm_call.iloc[i]['월저'] in cm_call_고가_extend:

                        self.tableWidget_call.item(i, Option_column.월저.value).setBackground(QBrush(콜월저색))
                        self.tableWidget_call.item(i, Option_column.월저.value).setForeground(QBrush(검정색))
                    else:
                        pass

                    if df_cm_call.iloc[i]['고가'] in cm_call_월저_extend:

                        self.tableWidget_call.item(i, Option_column.고가.value).setBackground(QBrush(콜월저색))
                        self.tableWidget_call.item(i, Option_column.고가.value).setForeground(QBrush(검정색))
                    else:
                        pass
                else:
                    pass

                if call_node_state['월고']:

                    if df_cm_call.iloc[i]['월고'] in cm_call_고가_extend:

                        self.tableWidget_call.item(i, Option_column.월고.value).setBackground(QBrush(콜월고색))
                        self.tableWidget_call.item(i, Option_column.월고.value).setForeground(QBrush(흰색))
                    else:
                        pass

                    if df_cm_call.iloc[i]['고가'] in cm_call_월고_extend:

                        self.tableWidget_call.item(i, Option_column.고가.value).setBackground(QBrush(콜월고색))
                        self.tableWidget_call.item(i, Option_column.고가.value).setForeground(QBrush(흰색))
                    else:
                        pass
                else:
                    pass

                if call_node_state['전저']:

                    if df_cm_call.iloc[i]['전저'] in cm_call_고가_extend:

                        self.tableWidget_call.item(i, Option_column.전저.value).setBackground(QBrush(콜전저색))
                        self.tableWidget_call.item(i, Option_column.전저.value).setForeground(QBrush(검정색))
                    else:
                        pass

                    if df_cm_call.iloc[i]['고가'] in cm_call_전저_extend:

                        self.tableWidget_call.item(i, Option_column.고가.value).setBackground(QBrush(콜전저색))
                        self.tableWidget_call.item(i, Option_column.고가.value).setForeground(QBrush(검정색))
                    else:
                        pass
                else:
                    pass

                if call_node_state['전고']:

                    if df_cm_call.iloc[i]['전고'] in cm_call_고가_extend:

                        self.tableWidget_call.item(i, Option_column.전고.value).setBackground(QBrush(콜전고색))
                        self.tableWidget_call.item(i, Option_column.전고.value).setForeground(QBrush(검정색))
                    else:
                        pass

                    if df_cm_call.iloc[i]['고가'] in cm_call_전고_extend:

                        self.tableWidget_call.item(i, Option_column.고가.value).setBackground(QBrush(콜전고색))
                        self.tableWidget_call.item(i, Option_column.고가.value).setForeground(QBrush(검정색))
                    else:
                        pass
                else:
                    pass

                if call_node_state['종가']:

                    if df_cm_call.iloc[i]['종가'] in cm_call_고가_extend:

                        self.tableWidget_call.item(i, Option_column.종가.value).setBackground(QBrush(콜종가색))
                        self.tableWidget_call.item(i, Option_column.종가.value).setForeground(QBrush(흰색))
                    else:
                        pass

                    if df_cm_call.iloc[i]['고가'] in cm_call_종가_extend:

                        self.tableWidget_call.item(i, Option_column.고가.value).setBackground(QBrush(콜종가색))
                        self.tableWidget_call.item(i, Option_column.고가.value).setForeground(QBrush(흰색))
                    else:
                        pass
                else:
                    pass

                if call_node_state['피봇']:

                    if df_cm_call.iloc[i]['피봇'] in cm_call_고가_extend:

                        self.tableWidget_call.item(i, Option_column.피봇.value).setBackground(QBrush(콜피봇색))
                        self.tableWidget_call.item(i, Option_column.피봇.value).setForeground(QBrush(검정색))
                    else:
                        pass

                    if df_cm_call.iloc[i]['고가'] in cm_call_피봇_extend:

                        self.tableWidget_call.item(i, Option_column.고가.value).setBackground(QBrush(콜피봇색))
                        self.tableWidget_call.item(i, Option_column.고가.value).setForeground(QBrush(검정색))
                    else:
                        pass
                else:
                    pass

                if call_node_state['시가']:

                    if df_cm_call.iloc[i]['시가'] in cm_call_고가_extend:

                        self.tableWidget_call.item(i, Option_column.시가.value).setBackground(QBrush(콜시가색))
                        self.tableWidget_call.item(i, Option_column.시가.value).setForeground(QBrush(흰색))
                    else:
                        pass

                    if df_cm_call.iloc[i]['고가'] in cm_call_시가_extend:

                        self.tableWidget_call.item(i, Option_column.고가.value).setBackground(QBrush(콜시가색))
                        self.tableWidget_call.item(i, Option_column.고가.value).setForeground(QBrush(흰색))
                    else:
                        pass
                else:
                    pass
                
                # 풋 node 컬러링
                if put_node_state['기준가']:

                    if df_cm_call.iloc[i]['고가'] in cm_put_기준가_extend:

                        self.tableWidget_call.item(i, Option_column.고가.value).setBackground(QBrush(풋기준가색))
                        self.tableWidget_call.item(i, Option_column.고가.value).setForeground(QBrush(흰색))
                    else:
                        pass
                else:
                    pass

                if put_node_state['월저']:

                    if df_cm_call.iloc[i]['고가'] in cm_put_월저_extend:

                        self.tableWidget_call.item(i, Option_column.고가.value).setBackground(QBrush(풋월저색))
                        self.tableWidget_call.item(i, Option_column.고가.value).setForeground(QBrush(흰색))
                    else:
                        pass
                else:
                    pass

                if put_node_state['월고']:

                    if df_cm_call.iloc[i]['고가'] in cm_put_월고_extend:

                        self.tableWidget_call.item(i, Option_column.고가.value).setBackground(QBrush(풋월고색))
                        self.tableWidget_call.item(i, Option_column.고가.value).setForeground(QBrush(흰색))
                    else:
                        pass
                else:
                    pass

                if put_node_state['전저']:

                    if df_cm_call.iloc[i]['고가'] in cm_put_전저_extend:

                        self.tableWidget_call.item(i, Option_column.고가.value).setBackground(QBrush(풋전저색))
                        self.tableWidget_call.item(i, Option_column.고가.value).setForeground(QBrush(흰색))
                    else:
                        pass
                else:
                    pass

                if put_node_state['전고']:

                    if df_cm_call.iloc[i]['고가'] in cm_put_전고_extend:

                        self.tableWidget_call.item(i, Option_column.고가.value).setBackground(QBrush(풋전고색))
                        self.tableWidget_call.item(i, Option_column.고가.value).setForeground(QBrush(검정색))
                    else:
                        pass
                else:
                    pass

                if put_node_state['종가']:

                    if df_cm_call.iloc[i]['고가'] in cm_put_종가_extend:

                        self.tableWidget_call.item(i, Option_column.고가.value).setBackground(QBrush(풋종가색))
                        self.tableWidget_call.item(i, Option_column.고가.value).setForeground(QBrush(흰색))
                    else:
                        pass
                else:
                    pass

                if put_node_state['피봇']:

                    if df_cm_call.iloc[i]['고가'] in cm_put_피봇_extend:

                        self.tableWidget_call.item(i, Option_column.고가.value).setBackground(QBrush(풋피봇색))
                        self.tableWidget_call.item(i, Option_column.고가.value).setForeground(QBrush(검정색))
                    else:
                        pass
                else:
                    pass

                if put_node_state['시가']:

                    if df_cm_call.iloc[i]['고가'] in cm_put_시가_extend:

                        self.tableWidget_call.item(i, Option_column.고가.value).setBackground(QBrush(풋시가색))
                        self.tableWidget_call.item(i, Option_column.고가.value).setForeground(QBrush(흰색))
                    else:
                        pass
                else:
                    pass

                if df_cm_call.iloc[i]['고가'] in coreval:

                    self.tableWidget_call.item(i, Option_column.고가.value).setBackground(QBrush(대맥점색))
                    self.tableWidget_call.item(i, Option_column.고가.value).setForeground(QBrush(검정색))
                else:
                    pass
        else:
            pass

        process_time = (timeit.default_timer() - start_time) * 1000
        print('call high color update check process time : %.2f ms' % process_time)

        str = '[{0:02d}:{1:02d}:{2:02d}] Call high color update : {3:0.2f} ms\r'.format(delta_hour, delta_minute, delta_sec, process_time)
        self.textBrowser.append(str)				

    # Put 컬러처리
    def put_color_clear(self):

        if put_scroll_end_position <= nCount_cm_option_pairs:

            for i in range(put_scroll_begin_position, put_scroll_end_position):

                self.tableWidget_put.item(i, Option_column.현재가.value).setBackground(QBrush(옅은회색))
        else:
            pass

    def put_low_color_clear(self):

        if put_scroll_end_position <= nCount_cm_option_pairs:

            for i in range(put_scroll_begin_position, put_scroll_end_position):

                self.tableWidget_put.item(i, Option_column.저가.value).setBackground(QBrush(기본바탕색))
                self.tableWidget_put.item(i, Option_column.저가.value).setForeground(QBrush(검정색))
        else:
            pass

    def put_high_color_clear(self):

        if put_scroll_end_position <= nCount_cm_option_pairs:

            for i in range(put_scroll_begin_position, put_scroll_end_position):

                self.tableWidget_put.item(i, Option_column.고가.value).setBackground(QBrush(기본바탕색))
                self.tableWidget_put.item(i, Option_column.고가.value).setForeground(QBrush(검정색))
        else:
            pass

    def put_node_color_clear(self):

        if put_scroll_end_position <= nCount_cm_option_pairs:

            for i in range(put_scroll_begin_position, put_scroll_end_position):

                # Clear Color
                if put_node_state['기준가']:
                    self.tableWidget_put.item(i, Option_column.기준가.value).setBackground(QBrush(기본바탕색))
                    self.tableWidget_put.item(i, Option_column.기준가.value).setForeground(QBrush(검정색))
                else:
                    pass

                if put_node_state['월저']:
                    self.tableWidget_put.item(i, Option_column.월저.value).setBackground(QBrush(기본바탕색))
                    self.tableWidget_put.item(i, Option_column.월저.value).setForeground(QBrush(검정색))
                else:
                    pass

                if put_node_state['월고']:
                    self.tableWidget_put.item(i, Option_column.월고.value).setBackground(QBrush(기본바탕색))
                    self.tableWidget_put.item(i, Option_column.월고.value).setForeground(QBrush(검정색))
                else:
                    pass

                if put_node_state['전저']:
                    self.tableWidget_put.item(i, Option_column.전저.value).setBackground(QBrush(기본바탕색))
                    self.tableWidget_put.item(i, Option_column.전저.value).setForeground(QBrush(검정색))
                else:
                    pass

                if put_node_state['전고']:
                    self.tableWidget_put.item(i, Option_column.전고.value).setBackground(QBrush(기본바탕색))
                    self.tableWidget_put.item(i, Option_column.전고.value).setForeground(QBrush(검정색))
                else:
                    pass

                if put_node_state['종가']:
                    self.tableWidget_put.item(i, Option_column.종가.value).setBackground(QBrush(기본바탕색))
                    self.tableWidget_put.item(i, Option_column.종가.value).setForeground(QBrush(검정색))
                else:
                    pass

                if put_node_state['피봇']:
                    self.tableWidget_put.item(i, Option_column.피봇.value).setBackground(QBrush(기본바탕색))
                    self.tableWidget_put.item(i, Option_column.피봇.value).setForeground(QBrush(검정색))
                else:
                    pass

                if put_node_state['시가']:
                    self.tableWidget_put.item(i, Option_column.시가.value).setBackground(QBrush(기본바탕색))

                    if df_cm_put.iloc[i]['시가'] > df_cm_put.iloc[i]['종가']:
                        self.tableWidget_put.item(i, Option_column.시가.value).setForeground(QBrush(적색))
                    elif df_cm_put.iloc[i]['시가'] < df_cm_put.iloc[i]['종가']:
                        self.tableWidget_put.item(i, Option_column.시가.value).setForeground(QBrush(청색))
                    else:
                        self.tableWidget_put.item(i, Option_column.시가.value).setForeground(QBrush(검정색))
                else:
                    pass

                self.tableWidget_put.item(i, Option_column.저가.value).setBackground(QBrush(기본바탕색))
                self.tableWidget_put.item(i, Option_column.저가.value).setForeground(QBrush(검정색))

                self.tableWidget_put.item(i, Option_column.고가.value).setBackground(QBrush(기본바탕색))
                self.tableWidget_put.item(i, Option_column.고가.value).setForeground(QBrush(검정색))
        else:
            pass

    def put_color_check(self):

        for i in range(nCount_cm_option_pairs):

            if df_cm_put.iloc[i]['저가'] in cm_call_종가_extend:

                self.tableWidget_put.item(i, Option_column.저가.value).setBackground(QBrush(Qt.darkMagenta))
                self.tableWidget_put.item(i, Option_column.저가.value).setForeground(QBrush(흰색))
            else:
                pass

            if df_cm_put.iloc[i]['저가'] in cm_put_종가_extend:

                self.tableWidget_put.item(i, Option_column.저가.value).setBackground(QBrush(Qt.darkCyan))
                self.tableWidget_put.item(i, Option_column.저가.value).setForeground(QBrush(흰색))
            else:
                pass

            if df_cm_put.iloc[i]['저가'] in cm_call_피봇_extend:

                self.tableWidget_put.item(i, Option_column.저가.value).setBackground(QBrush(콜피봇색))
                self.tableWidget_put.item(i, Option_column.저가.value).setForeground(QBrush(검정색))
            else:
                pass

            if df_cm_put.iloc[i]['저가'] in cm_put_피봇_extend:

                self.tableWidget_put.item(i, Option_column.저가.value).setBackground(QBrush(풋피봇색))
                self.tableWidget_put.item(i, Option_column.저가.value).setForeground(QBrush(검정색))
            else:
                pass

            if df_cm_put.iloc[i]['저가'] in cm_call_시가_extend:

                self.tableWidget_put.item(i, Option_column.저가.value).setBackground(QBrush(Qt.darkRed))
                self.tableWidget_put.item(i, Option_column.저가.value).setForeground(QBrush(흰색))
            else:
                pass

            if df_cm_put.iloc[i]['저가'] in cm_put_시가_extend:

                self.tableWidget_put.item(i, Option_column.저가.value).setBackground(QBrush(Qt.darkBlue))
                self.tableWidget_put.item(i, Option_column.저가.value).setForeground(QBrush(흰색))
            else:
                pass

            if df_cm_put.iloc[i]['저가'] in coreval:

                self.tableWidget_put.item(i, Option_column.저가.value).setBackground(QBrush(녹색))
                self.tableWidget_put.item(i, Option_column.저가.value).setForeground(QBrush(검정색))
            else:
                pass

            if df_cm_put.iloc[i]['고가'] in cm_call_종가_extend:

                self.tableWidget_put.item(i, Option_column.고가.value).setBackground(QBrush(Qt.darkMagenta))
                self.tableWidget_put.item(i, Option_column.고가.value).setForeground(QBrush(흰색))
            else:
                pass

            if df_cm_put.iloc[i]['고가'] in cm_put_종가_extend:

                self.tableWidget_put.item(i, Option_column.고가.value).setBackground(QBrush(Qt.darkCyan))
                self.tableWidget_put.item(i, Option_column.고가.value).setForeground(QBrush(흰색))
            else:
                pass

            if df_cm_put.iloc[i]['고가'] in cm_call_피봇_extend:

                self.tableWidget_put.item(i, Option_column.고가.value).setBackground(QBrush(콜피봇색))
                self.tableWidget_put.item(i, Option_column.고가.value).setForeground(QBrush(검정색))
            else:
                pass

            if df_cm_put.iloc[i]['고가'] in cm_put_피봇_extend:

                self.tableWidget_put.item(i, Option_column.고가.value).setBackground(QBrush(풋피봇색))
                self.tableWidget_put.item(i, Option_column.고가.value).setForeground(QBrush(검정색))
            else:
                pass

            if df_cm_put.iloc[i]['고가'] in cm_call_시가_extend:

                self.tableWidget_put.item(i, Option_column.고가.value).setBackground(QBrush(Qt.darkRed))
                self.tableWidget_put.item(i, Option_column.고가.value).setForeground(QBrush(흰색))
            else:
                pass

            if df_cm_put.iloc[i]['고가'] in cm_put_시가_extend:

                self.tableWidget_put.item(i, Option_column.고가.value).setBackground(QBrush(Qt.darkBlue))
                self.tableWidget_put.item(i, Option_column.고가.value).setForeground(QBrush(흰색))
            else:
                pass

            if df_cm_put.iloc[i]['고가'] in coreval:

                self.tableWidget_put.item(i, Option_column.고가.value).setBackground(QBrush(녹색))
                self.tableWidget_put.item(i, Option_column.고가.value).setForeground(QBrush(검정색))
            else:
                pass

    def putnode_color_check(self):
	
        start_time = timeit.default_timer()

        if call_scroll_end_position <= nCount_cm_option_pairs:

            for i in range(call_scroll_begin_position, call_scroll_end_position):
                
                # 콜 node 컬러링
                if call_node_state['기준가']:

                    if df_cm_call.iloc[i]['기준가'] in cm_put_저가_extend:

                        self.tableWidget_call.item(i, Option_column.기준가.value).setBackground(QBrush(콜기준가색))
                        self.tableWidget_call.item(i, Option_column.기준가.value).setForeground(QBrush(흰색))
                    else:
                        pass
						
                    if df_cm_call.iloc[i]['기준가'] in cm_put_고가_extend:

                        self.tableWidget_call.item(i, Option_column.기준가.value).setBackground(QBrush(콜기준가색))
                        self.tableWidget_call.item(i, Option_column.기준가.value).setForeground(QBrush(흰색))
                    else:
                        pass
                else:
                    pass

                if call_node_state['월저']:

                    if df_cm_call.iloc[i]['월저'] in cm_put_저가_extend:

                        self.tableWidget_call.item(i, Option_column.월저.value).setBackground(QBrush(콜월저색))
                        self.tableWidget_call.item(i, Option_column.월저.value).setForeground(QBrush(검정색))
                    else:
                        pass
						
                    if df_cm_call.iloc[i]['월저'] in cm_put_고가_extend:

                        self.tableWidget_call.item(i, Option_column.월저.value).setBackground(QBrush(콜월저색))
                        self.tableWidget_call.item(i, Option_column.월저.value).setForeground(QBrush(검정색))
                    else:
                        pass
                else:
                    pass

                if call_node_state['월고']:

                    if df_cm_call.iloc[i]['월고'] in cm_put_저가_extend:

                        self.tableWidget_call.item(i, Option_column.월고.value).setBackground(QBrush(콜월고색))
                        self.tableWidget_call.item(i, Option_column.월고.value).setForeground(QBrush(흰색))
                    else:
                        pass
						
                    if df_cm_call.iloc[i]['월고'] in cm_put_고가_extend:

                        self.tableWidget_call.item(i, Option_column.월고.value).setBackground(QBrush(콜월고색))
                        self.tableWidget_call.item(i, Option_column.월고.value).setForeground(QBrush(흰색))
                    else:
                        pass
                else:
                    pass

                if call_node_state['전저']:

                    if df_cm_call.iloc[i]['전저'] in cm_put_저가_extend:

                        self.tableWidget_call.item(i, Option_column.전저.value).setBackground(QBrush(콜전저색))
                        self.tableWidget_call.item(i, Option_column.전저.value).setForeground(QBrush(검정색))
                    else:
                        pass
						
                    if df_cm_call.iloc[i]['전저'] in cm_put_고가_extend:

                        self.tableWidget_call.item(i, Option_column.전저.value).setBackground(QBrush(콜전저색))
                        self.tableWidget_call.item(i, Option_column.전저.value).setForeground(QBrush(검정색))
                    else:
                        pass
                else:
                    pass

                if call_node_state['전고']:

                    if df_cm_call.iloc[i]['전고'] in cm_put_저가_extend:

                        self.tableWidget_call.item(i, Option_column.전고.value).setBackground(QBrush(콜전고색))
                        self.tableWidget_call.item(i, Option_column.전고.value).setForeground(QBrush(검정색))
                    else:
                        pass
						
                    if df_cm_call.iloc[i]['전고'] in cm_put_고가_extend:

                        self.tableWidget_call.item(i, Option_column.전고.value).setBackground(QBrush(콜전고색))
                        self.tableWidget_call.item(i, Option_column.전고.value).setForeground(QBrush(검정색))
                    else:
                        pass
                else:
                    pass

                if call_node_state['종가']:

                    if df_cm_call.iloc[i]['종가'] in cm_put_저가_extend:

                        self.tableWidget_call.item(i, Option_column.종가.value).setBackground(QBrush(콜종가색))
                        self.tableWidget_call.item(i, Option_column.종가.value).setForeground(QBrush(흰색))
                    else:
                        pass
						
                    if df_cm_call.iloc[i]['종가'] in cm_put_고가_extend:

                        self.tableWidget_call.item(i, Option_column.종가.value).setBackground(QBrush(콜종가색))
                        self.tableWidget_call.item(i, Option_column.종가.value).setForeground(QBrush(흰색))
                    else:
                        pass
                else:
                    pass

                if call_node_state['피봇']:

                    if df_cm_call.iloc[i]['피봇'] in cm_put_저가_extend:

                        self.tableWidget_call.item(i, Option_column.피봇.value).setBackground(QBrush(콜피봇색))
                        self.tableWidget_call.item(i, Option_column.피봇.value).setForeground(QBrush(검정색))
                    else:
                        pass
						
                    if df_cm_call.iloc[i]['피봇'] in cm_put_고가_extend:

                        self.tableWidget_call.item(i, Option_column.피봇.value).setBackground(QBrush(콜피봇색))
                        self.tableWidget_call.item(i, Option_column.피봇.value).setForeground(QBrush(검정색))
                    else:
                        pass
                else:
                    pass

                if call_node_state['시가']:

                    if df_cm_call.iloc[i]['시가'] in cm_put_저가_extend:

                        self.tableWidget_call.item(i, Option_column.시가.value).setBackground(QBrush(콜시가색))
                        self.tableWidget_call.item(i, Option_column.시가.value).setForeground(QBrush(흰색))
                    else:
                        pass
						
                    if df_cm_call.iloc[i]['시가'] in cm_put_고가_extend:

                        self.tableWidget_call.item(i, Option_column.시가.value).setBackground(QBrush(콜시가색))
                        self.tableWidget_call.item(i, Option_column.시가.value).setForeground(QBrush(흰색))
                    else:
                        pass
                else:
                    pass 
        else:
            pass

        if put_scroll_end_position <= nCount_cm_option_pairs:            

            for i in range(put_scroll_begin_position, put_scroll_end_position):
                
                # 풋 node 컬러링
                if put_node_state['기준가']:

                    if df_cm_put.iloc[i]['기준가'] in cm_call_저가_extend:

                        self.tableWidget_put.item(i, Option_column.기준가.value).setBackground(QBrush(풋기준가색))
                        self.tableWidget_put.item(i, Option_column.기준가.value).setForeground(QBrush(흰색))
                    else:
                        pass

                    if df_cm_put.iloc[i]['기준가'] in cm_call_고가_extend:

                        self.tableWidget_put.item(i, Option_column.기준가.value).setBackground(QBrush(풋기준가색))
                        self.tableWidget_put.item(i, Option_column.기준가.value).setForeground(QBrush(흰색))
                    else:
                        pass

                    if df_cm_put.iloc[i]['기준가'] in cm_put_저가_extend:

                        self.tableWidget_put.item(i, Option_column.기준가.value).setBackground(QBrush(풋기준가색))
                        self.tableWidget_put.item(i, Option_column.기준가.value).setForeground(QBrush(흰색))
                    else:
                        pass

                    if df_cm_put.iloc[i]['기준가'] in cm_put_고가_extend:

                        self.tableWidget_put.item(i, Option_column.기준가.value).setBackground(QBrush(풋기준가색))
                        self.tableWidget_put.item(i, Option_column.기준가.value).setForeground(QBrush(흰색))
                    else:
                        pass

                    if df_cm_put.iloc[i]['저가'] in cm_put_기준가_extend:

                        self.tableWidget_put.item(i, Option_column.저가.value).setBackground(QBrush(풋기준가색))
                        self.tableWidget_put.item(i, Option_column.저가.value).setForeground(QBrush(흰색))
                    else:
                        pass

                    if df_cm_put.iloc[i]['고가'] in cm_put_기준가_extend:

                        self.tableWidget_put.item(i, Option_column.고가.value).setBackground(QBrush(풋기준가색))
                        self.tableWidget_put.item(i, Option_column.고가.value).setForeground(QBrush(흰색))
                    else:
                        pass
                else:
                    pass

                if put_node_state['월저']:

                    if df_cm_put.iloc[i]['월저'] in cm_call_저가_extend:

                        self.tableWidget_put.item(i, Option_column.월저.value).setBackground(QBrush(풋월저색))
                        self.tableWidget_put.item(i, Option_column.월저.value).setForeground(QBrush(흰색))
                    else:
                        pass

                    if df_cm_put.iloc[i]['월저'] in cm_call_고가_extend:

                        self.tableWidget_put.item(i, Option_column.월저.value).setBackground(QBrush(풋월저색))
                        self.tableWidget_put.item(i, Option_column.월저.value).setForeground(QBrush(흰색))
                    else:
                        pass

                    if df_cm_put.iloc[i]['월저'] in cm_put_저가_extend:

                        self.tableWidget_put.item(i, Option_column.월저.value).setBackground(QBrush(풋월저색))
                        self.tableWidget_put.item(i, Option_column.월저.value).setForeground(QBrush(흰색))
                    else:
                        pass

                    if df_cm_put.iloc[i]['월저'] in cm_put_고가_extend:

                        self.tableWidget_put.item(i, Option_column.월저.value).setBackground(QBrush(풋월저색))
                        self.tableWidget_put.item(i, Option_column.월저.value).setForeground(QBrush(흰색))
                    else:
                        pass

                    if df_cm_put.iloc[i]['저가'] in cm_put_월저_extend:

                        self.tableWidget_put.item(i, Option_column.저가.value).setBackground(QBrush(풋월저색))
                        self.tableWidget_put.item(i, Option_column.저가.value).setForeground(QBrush(흰색))
                    else:
                        pass

                    if df_cm_put.iloc[i]['고가'] in cm_put_월저_extend:

                        self.tableWidget_put.item(i, Option_column.고가.value).setBackground(QBrush(풋월저색))
                        self.tableWidget_put.item(i, Option_column.고가.value).setForeground(QBrush(흰색))
                    else:
                        pass
                else:
                    pass

                if put_node_state['월고']:

                    if df_cm_put.iloc[i]['월고'] in cm_call_저가_extend:

                        self.tableWidget_put.item(i, Option_column.월고.value).setBackground(QBrush(풋월고색))
                        self.tableWidget_put.item(i, Option_column.월고.value).setForeground(QBrush(흰색))
                    else:
                        pass

                    if df_cm_put.iloc[i]['월고'] in cm_call_고가_extend:

                        self.tableWidget_put.item(i, Option_column.월고.value).setBackground(QBrush(풋월고색))
                        self.tableWidget_put.item(i, Option_column.월고.value).setForeground(QBrush(흰색))
                    else:
                        pass

                    if df_cm_put.iloc[i]['월고'] in cm_put_저가_extend:

                        self.tableWidget_put.item(i, Option_column.월고.value).setBackground(QBrush(풋월고색))
                        self.tableWidget_put.item(i, Option_column.월고.value).setForeground(QBrush(흰색))
                    else:
                        pass

                    if df_cm_put.iloc[i]['월고'] in cm_put_고가_extend:

                        self.tableWidget_put.item(i, Option_column.월고.value).setBackground(QBrush(풋월고색))
                        self.tableWidget_put.item(i, Option_column.월고.value).setForeground(QBrush(흰색))
                    else:
                        pass

                    if df_cm_put.iloc[i]['저가'] in cm_put_월고_extend:

                        self.tableWidget_put.item(i, Option_column.저가.value).setBackground(QBrush(풋월고색))
                        self.tableWidget_put.item(i, Option_column.저가.value).setForeground(QBrush(흰색))
                    else:
                        pass

                    if df_cm_put.iloc[i]['고가'] in cm_put_월고_extend:

                        self.tableWidget_put.item(i, Option_column.고가.value).setBackground(QBrush(풋월고색))
                        self.tableWidget_put.item(i, Option_column.고가.value).setForeground(QBrush(흰색))
                    else:
                        pass
                else:
                    pass

                if put_node_state['전저']:

                    if df_cm_put.iloc[i]['전저'] in cm_call_저가_extend:

                        self.tableWidget_put.item(i, Option_column.전저.value).setBackground(QBrush(풋전저색))
                        self.tableWidget_put.item(i, Option_column.전저.value).setForeground(QBrush(흰색))
                    else:
                        pass

                    if df_cm_put.iloc[i]['전저'] in cm_call_고가_extend:

                        self.tableWidget_put.item(i, Option_column.전저.value).setBackground(QBrush(풋전저색))
                        self.tableWidget_put.item(i, Option_column.전저.value).setForeground(QBrush(흰색))
                    else:
                        pass

                    if df_cm_put.iloc[i]['전저'] in cm_put_저가_extend:

                        self.tableWidget_put.item(i, Option_column.전저.value).setBackground(QBrush(풋전저색))
                        self.tableWidget_put.item(i, Option_column.전저.value).setForeground(QBrush(흰색))
                    else:
                        pass

                    if df_cm_put.iloc[i]['전저'] in cm_put_고가_extend:

                        self.tableWidget_put.item(i, Option_column.전저.value).setBackground(QBrush(풋전저색))
                        self.tableWidget_put.item(i, Option_column.전저.value).setForeground(QBrush(흰색))
                    else:
                        pass

                    if df_cm_put.iloc[i]['저가'] in cm_put_전저_extend:

                        self.tableWidget_put.item(i, Option_column.저가.value).setBackground(QBrush(풋전저색))
                        self.tableWidget_put.item(i, Option_column.저가.value).setForeground(QBrush(검정색))
                    else:
                        pass

                    if df_cm_put.iloc[i]['고가'] in cm_put_전저_extend:

                        self.tableWidget_put.item(i, Option_column.고가.value).setBackground(QBrush(풋전저색))
                        self.tableWidget_put.item(i, Option_column.고가.value).setForeground(QBrush(검정색))
                    else:
                        pass
                else:
                    pass

                if put_node_state['전고']:

                    if df_cm_put.iloc[i]['전고'] in cm_call_저가_extend:

                        self.tableWidget_put.item(i, Option_column.전고.value).setBackground(QBrush(풋전고색))
                        self.tableWidget_put.item(i, Option_column.전고.value).setForeground(QBrush(검정색))
                    else:
                        pass

                    if df_cm_put.iloc[i]['전고'] in cm_call_고가_extend:

                        self.tableWidget_put.item(i, Option_column.전고.value).setBackground(QBrush(풋전고색))
                        self.tableWidget_put.item(i, Option_column.전고.value).setForeground(QBrush(검정색))
                    else:
                        pass

                    if df_cm_put.iloc[i]['전고'] in cm_put_저가_extend:

                        self.tableWidget_put.item(i, Option_column.전고.value).setBackground(QBrush(풋전고색))
                        self.tableWidget_put.item(i, Option_column.전고.value).setForeground(QBrush(검정색))
                    else:
                        pass

                    if df_cm_put.iloc[i]['전고'] in cm_put_고가_extend:

                        self.tableWidget_put.item(i, Option_column.전고.value).setBackground(QBrush(풋전고색))
                        self.tableWidget_put.item(i, Option_column.전고.value).setForeground(QBrush(검정색))
                    else:
                        pass

                    if df_cm_put.iloc[i]['저가'] in cm_put_전고_extend:

                        self.tableWidget_put.item(i, Option_column.저가.value).setBackground(QBrush(풋전고색))
                        self.tableWidget_put.item(i, Option_column.저가.value).setForeground(QBrush(검정색))
                    else:
                        pass

                    if df_cm_put.iloc[i]['고가'] in cm_put_전고_extend:

                        self.tableWidget_put.item(i, Option_column.고가.value).setBackground(QBrush(풋전고색))
                        self.tableWidget_put.item(i, Option_column.고가.value).setForeground(QBrush(검정색))
                    else:
                        pass
                else:
                    pass

                if put_node_state['종가']:

                    if df_cm_put.iloc[i]['종가'] in cm_call_저가_extend:

                        self.tableWidget_put.item(i, Option_column.종가.value).setBackground(QBrush(풋종가색))
                        self.tableWidget_put.item(i, Option_column.종가.value).setForeground(QBrush(흰색))
                    else:
                        pass

                    if df_cm_put.iloc[i]['종가'] in cm_call_고가_extend:

                        self.tableWidget_put.item(i, Option_column.종가.value).setBackground(QBrush(풋종가색))
                        self.tableWidget_put.item(i, Option_column.종가.value).setForeground(QBrush(흰색))
                    else:
                        pass

                    if df_cm_put.iloc[i]['종가'] in cm_put_저가_extend:

                        self.tableWidget_put.item(i, Option_column.종가.value).setBackground(QBrush(풋종가색))
                        self.tableWidget_put.item(i, Option_column.종가.value).setForeground(QBrush(흰색))
                    else:
                        pass

                    if df_cm_put.iloc[i]['종가'] in cm_put_고가_extend:

                        self.tableWidget_put.item(i, Option_column.종가.value).setBackground(QBrush(풋종가색))
                        self.tableWidget_put.item(i, Option_column.종가.value).setForeground(QBrush(흰색))
                    else:
                        pass

                    if df_cm_put.iloc[i]['저가'] in cm_put_종가_extend:

                        self.tableWidget_put.item(i, Option_column.저가.value).setBackground(QBrush(풋종가색))
                        self.tableWidget_put.item(i, Option_column.저가.value).setForeground(QBrush(흰색))
                    else:
                        pass

                    if df_cm_put.iloc[i]['고가'] in cm_put_종가_extend:

                        self.tableWidget_put.item(i, Option_column.고가.value).setBackground(QBrush(풋종가색))
                        self.tableWidget_put.item(i, Option_column.고가.value).setForeground(QBrush(흰색))
                    else:
                        pass
                else:
                    pass

                if put_node_state['피봇']:

                    if df_cm_put.iloc[i]['피봇'] in cm_call_저가_extend:

                        self.tableWidget_put.item(i, Option_column.피봇.value).setBackground(QBrush(풋피봇색))
                        self.tableWidget_put.item(i, Option_column.피봇.value).setForeground(QBrush(검정색))
                    else:
                        pass

                    if df_cm_put.iloc[i]['피봇'] in cm_call_고가_extend:

                        self.tableWidget_put.item(i, Option_column.피봇.value).setBackground(QBrush(풋피봇색))
                        self.tableWidget_put.item(i, Option_column.피봇.value).setForeground(QBrush(검정색))
                    else:
                        pass

                    if df_cm_put.iloc[i]['피봇'] in cm_put_저가_extend:

                        self.tableWidget_put.item(i, Option_column.피봇.value).setBackground(QBrush(풋피봇색))
                        self.tableWidget_put.item(i, Option_column.피봇.value).setForeground(QBrush(검정색))
                    else:
                        pass

                    if df_cm_put.iloc[i]['피봇'] in cm_put_고가_extend:

                        self.tableWidget_put.item(i, Option_column.피봇.value).setBackground(QBrush(풋피봇색))
                        self.tableWidget_put.item(i, Option_column.피봇.value).setForeground(QBrush(검정색))
                    else:
                        pass

                    if df_cm_put.iloc[i]['저가'] in cm_put_피봇_extend:

                        self.tableWidget_put.item(i, Option_column.저가.value).setBackground(QBrush(풋피봇색))
                        self.tableWidget_put.item(i, Option_column.저가.value).setForeground(QBrush(검정색))
                    else:
                        pass

                    if df_cm_put.iloc[i]['고가'] in cm_put_피봇_extend:

                        self.tableWidget_put.item(i, Option_column.고가.value).setBackground(QBrush(풋피봇색))
                        self.tableWidget_put.item(i, Option_column.고가.value).setForeground(QBrush(검정색))
                    else:
                        pass
                else:
                    pass

                if put_node_state['시가']:

                    if df_cm_put.iloc[i]['시가'] in cm_call_저가_extend:

                        self.tableWidget_put.item(i, Option_column.시가.value).setBackground(QBrush(풋시가색))
                        self.tableWidget_put.item(i, Option_column.시가.value).setForeground(QBrush(흰색))
                    else:
                        pass

                    if df_cm_put.iloc[i]['시가'] in cm_call_고가_extend:

                        self.tableWidget_put.item(i, Option_column.시가.value).setBackground(QBrush(풋시가색))
                        self.tableWidget_put.item(i, Option_column.시가.value).setForeground(QBrush(흰색))
                    else:
                        pass

                    if df_cm_put.iloc[i]['시가'] in cm_put_저가_extend:

                        self.tableWidget_put.item(i, Option_column.시가.value).setBackground(QBrush(풋시가색))
                        self.tableWidget_put.item(i, Option_column.시가.value).setForeground(QBrush(흰색))
                    else:
                        pass

                    if df_cm_put.iloc[i]['시가'] in cm_put_고가_extend:

                        self.tableWidget_put.item(i, Option_column.시가.value).setBackground(QBrush(풋시가색))
                        self.tableWidget_put.item(i, Option_column.시가.value).setForeground(QBrush(흰색))
                    else:
                        pass

                    if df_cm_put.iloc[i]['저가'] in cm_put_시가_extend:

                        self.tableWidget_put.item(i, Option_column.저가.value).setBackground(QBrush(풋시가색))
                        self.tableWidget_put.item(i, Option_column.저가.value).setForeground(QBrush(흰색))
                    else:
                        pass

                    if df_cm_put.iloc[i]['고가'] in cm_put_시가_extend:

                        self.tableWidget_put.item(i, Option_column.고가.value).setBackground(QBrush(풋시가색))
                        self.tableWidget_put.item(i, Option_column.고가.value).setForeground(QBrush(흰색))
                    else:
                        pass
                else:
                    pass

                # 콜 node 컬러링                
                if call_node_state['기준가']:

                    if df_cm_put.iloc[i]['저가'] in cm_call_기준가_extend:

                        self.tableWidget_put.item(i, Option_column.저가.value).setBackground(QBrush(콜기준가색))
                        self.tableWidget_put.item(i, Option_column.저가.value).setForeground(QBrush(흰색))
                    else:
                        pass

                    if df_cm_put.iloc[i]['고가'] in cm_call_기준가_extend:

                        self.tableWidget_put.item(i, Option_column.고가.value).setBackground(QBrush(콜기준가색))
                        self.tableWidget_put.item(i, Option_column.고가.value).setForeground(QBrush(흰색))
                    else:
                        pass
                else:
                    pass

                if call_node_state['월저']:

                    if df_cm_put.iloc[i]['저가'] in cm_call_월저_extend:

                        self.tableWidget_put.item(i, Option_column.저가.value).setBackground(QBrush(콜월저색))
                        self.tableWidget_put.item(i, Option_column.저가.value).setForeground(QBrush(검정색))
                    else:
                        pass

                    if df_cm_put.iloc[i]['고가'] in cm_call_월저_extend:

                        self.tableWidget_put.item(i, Option_column.고가.value).setBackground(QBrush(콜월저색))
                        self.tableWidget_put.item(i, Option_column.고가.value).setForeground(QBrush(검정색))
                    else:
                        pass
                else:
                    pass

                if call_node_state['월고']:

                    if df_cm_put.iloc[i]['저가'] in cm_call_월고_extend:

                        self.tableWidget_put.item(i, Option_column.저가.value).setBackground(QBrush(콜월고색))
                        self.tableWidget_put.item(i, Option_column.저가.value).setForeground(QBrush(흰색))
                    else:
                        pass

                    if df_cm_put.iloc[i]['고가'] in cm_call_월고_extend:

                        self.tableWidget_put.item(i, Option_column.고가.value).setBackground(QBrush(콜월고색))
                        self.tableWidget_put.item(i, Option_column.고가.value).setForeground(QBrush(흰색))
                    else:
                        pass
                else:
                    pass

                if call_node_state['전저']:

                    if df_cm_put.iloc[i]['저가'] in cm_call_전저_extend:

                        self.tableWidget_put.item(i, Option_column.저가.value).setBackground(QBrush(콜전저색))
                        self.tableWidget_put.item(i, Option_column.저가.value).setForeground(QBrush(검정색))
                    else:
                        pass

                    if df_cm_put.iloc[i]['고가'] in cm_call_전저_extend:

                        self.tableWidget_put.item(i, Option_column.고가.value).setBackground(QBrush(콜전저색))
                        self.tableWidget_put.item(i, Option_column.고가.value).setForeground(QBrush(검정색))
                    else:
                        pass
                else:
                    pass

                if call_node_state['전고']:

                    if df_cm_put.iloc[i]['저가'] in cm_call_전고_extend:

                        self.tableWidget_put.item(i, Option_column.저가.value).setBackground(QBrush(콜전고색))
                        self.tableWidget_put.item(i, Option_column.저가.value).setForeground(QBrush(검정색))
                    else:
                        pass

                    if df_cm_put.iloc[i]['고가'] in cm_call_전고_extend:

                        self.tableWidget_put.item(i, Option_column.고가.value).setBackground(QBrush(콜전고색))
                        self.tableWidget_put.item(i, Option_column.고가.value).setForeground(QBrush(검정색))
                    else:
                        pass
                else:
                    pass

                if call_node_state['종가']:

                    if df_cm_put.iloc[i]['저가'] in cm_call_종가_extend:

                        self.tableWidget_put.item(i, Option_column.저가.value).setBackground(QBrush(콜종가색))
                        self.tableWidget_put.item(i, Option_column.저가.value).setForeground(QBrush(흰색))
                    else:
                        pass

                    if df_cm_put.iloc[i]['고가'] in cm_call_종가_extend:

                        self.tableWidget_put.item(i, Option_column.고가.value).setBackground(QBrush(콜종가색))
                        self.tableWidget_put.item(i, Option_column.고가.value).setForeground(QBrush(흰색))
                    else:
                        pass
                else:
                    pass

                if call_node_state['피봇']:

                    if df_cm_put.iloc[i]['저가'] in cm_call_피봇_extend:

                        self.tableWidget_put.item(i, Option_column.저가.value).setBackground(QBrush(콜피봇색))
                        self.tableWidget_put.item(i, Option_column.저가.value).setForeground(QBrush(검정색))
                    else:
                        pass

                    if df_cm_put.iloc[i]['고가'] in cm_call_피봇_extend:

                        self.tableWidget_put.item(i, Option_column.고가.value).setBackground(QBrush(콜피봇색))
                        self.tableWidget_put.item(i, Option_column.고가.value).setForeground(QBrush(검정색))
                    else:
                        pass
                else:
                    pass

                if call_node_state['시가']:

                    if df_cm_put.iloc[i]['저가'] in cm_call_시가_extend:

                        self.tableWidget_put.item(i, Option_column.저가.value).setBackground(QBrush(콜시가색))
                        self.tableWidget_put.item(i, Option_column.저가.value).setForeground(QBrush(흰색))
                    else:
                        pass

                    if df_cm_put.iloc[i]['고가'] in cm_call_시가_extend:

                        self.tableWidget_put.item(i, Option_column.고가.value).setBackground(QBrush(콜시가색))
                        self.tableWidget_put.item(i, Option_column.고가.value).setForeground(QBrush(흰색))
                    else:
                        pass
                else:
                    pass                
                
                if df_cm_put.iloc[i]['저가'] in coreval:

                    self.tableWidget_put.item(i, Option_column.저가.value).setBackground(QBrush(대맥점색))
                    self.tableWidget_put.item(i, Option_column.저가.value).setForeground(QBrush(검정색))
                else:
                    pass

                if df_cm_put.iloc[i]['고가'] in coreval:

                    self.tableWidget_put.item(i, Option_column.고가.value).setBackground(QBrush(대맥점색))
                    self.tableWidget_put.item(i, Option_column.고가.value).setForeground(QBrush(검정색))
                else:
                    pass
        else:
            pass
			
        process_time = (timeit.default_timer() - start_time) * 1000
        print('put color check process time : %.2f ms' % process_time)

        str = '[{0:02d}:{1:02d}:{2:02d}] Put color check time : {3:0.2f} ms\r'.format(delta_hour, delta_minute, delta_sec, process_time)
        self.textBrowser.append(str)

    def put_low_update_color_check(self):
	
        start_time = timeit.default_timer()

        if call_scroll_end_position <= nCount_cm_option_pairs:

            for i in range(call_scroll_begin_position, call_scroll_end_position):
                
                # 콜 node 컬러링
                if call_node_state['기준가']:

                    if df_cm_call.iloc[i]['기준가'] in cm_put_저가_extend:

                        self.tableWidget_call.item(i, Option_column.기준가.value).setBackground(QBrush(콜기준가색))
                        self.tableWidget_call.item(i, Option_column.기준가.value).setForeground(QBrush(흰색))
                    else:
                        pass
                else:
                    pass

                if call_node_state['월저']:

                    if df_cm_call.iloc[i]['월저'] in cm_put_저가_extend:

                        self.tableWidget_call.item(i, Option_column.월저.value).setBackground(QBrush(콜월저색))
                        self.tableWidget_call.item(i, Option_column.월저.value).setForeground(QBrush(검정색))
                    else:
                        pass
                else:
                    pass

                if call_node_state['월고']:

                    if df_cm_call.iloc[i]['월고'] in cm_put_저가_extend:

                        self.tableWidget_call.item(i, Option_column.월고.value).setBackground(QBrush(콜월고색))
                        self.tableWidget_call.item(i, Option_column.월고.value).setForeground(QBrush(흰색))
                    else:
                        pass
                else:
                    pass

                if call_node_state['전저']:

                    if df_cm_call.iloc[i]['전저'] in cm_put_저가_extend:

                        self.tableWidget_call.item(i, Option_column.전저.value).setBackground(QBrush(콜전저색))
                        self.tableWidget_call.item(i, Option_column.전저.value).setForeground(QBrush(검정색))
                    else:
                        pass
                else:
                    pass

                if call_node_state['전고']:

                    if df_cm_call.iloc[i]['전고'] in cm_put_저가_extend:

                        self.tableWidget_call.item(i, Option_column.전고.value).setBackground(QBrush(콜전고색))
                        self.tableWidget_call.item(i, Option_column.전고.value).setForeground(QBrush(검정색))
                    else:
                        pass
                else:
                    pass

                if call_node_state['종가']:

                    if df_cm_call.iloc[i]['종가'] in cm_put_저가_extend:

                        self.tableWidget_call.item(i, Option_column.종가.value).setBackground(QBrush(콜종가색))
                        self.tableWidget_call.item(i, Option_column.종가.value).setForeground(QBrush(흰색))
                    else:
                        pass
                else:
                    pass

                if call_node_state['피봇']:

                    if df_cm_call.iloc[i]['피봇'] in cm_put_저가_extend:

                        self.tableWidget_call.item(i, Option_column.피봇.value).setBackground(QBrush(콜피봇색))
                        self.tableWidget_call.item(i, Option_column.피봇.value).setForeground(QBrush(검정색))
                    else:
                        pass
                else:
                    pass

                if call_node_state['시가']:

                    if df_cm_call.iloc[i]['시가'] in cm_put_저가_extend:

                        self.tableWidget_call.item(i, Option_column.시가.value).setBackground(QBrush(콜시가색))
                        self.tableWidget_call.item(i, Option_column.시가.value).setForeground(QBrush(흰색))
                    else:
                        pass
                else:
                    pass 
        else:
            pass

        if put_scroll_end_position <= nCount_cm_option_pairs:            

            for i in range(put_scroll_begin_position, put_scroll_end_position):
                
                # 풋 node 컬러링
                if put_node_state['기준가']:

                    if df_cm_put.iloc[i]['기준가'] in cm_put_저가_extend:

                        self.tableWidget_put.item(i, Option_column.기준가.value).setBackground(QBrush(풋기준가색))
                        self.tableWidget_put.item(i, Option_column.기준가.value).setForeground(QBrush(흰색))
                    else:
                        pass

                    if df_cm_put.iloc[i]['저가'] in cm_put_기준가_extend:

                        self.tableWidget_put.item(i, Option_column.저가.value).setBackground(QBrush(풋기준가색))
                        self.tableWidget_put.item(i, Option_column.저가.value).setForeground(QBrush(흰색))
                    else:
                        pass
                else:
                    pass

                if put_node_state['월저']:

                    if df_cm_put.iloc[i]['월저'] in cm_put_저가_extend:

                        self.tableWidget_put.item(i, Option_column.월저.value).setBackground(QBrush(풋월저색))
                        self.tableWidget_put.item(i, Option_column.월저.value).setForeground(QBrush(흰색))
                    else:
                        pass

                    if df_cm_put.iloc[i]['저가'] in cm_put_월저_extend:

                        self.tableWidget_put.item(i, Option_column.저가.value).setBackground(QBrush(풋월저색))
                        self.tableWidget_put.item(i, Option_column.저가.value).setForeground(QBrush(흰색))
                    else:
                        pass
                else:
                    pass

                if put_node_state['월고']:

                    if df_cm_put.iloc[i]['월고'] in cm_put_저가_extend:

                        self.tableWidget_put.item(i, Option_column.월고.value).setBackground(QBrush(풋월고색))
                        self.tableWidget_put.item(i, Option_column.월고.value).setForeground(QBrush(흰색))
                    else:
                        pass

                    if df_cm_put.iloc[i]['저가'] in cm_put_월고_extend:

                        self.tableWidget_put.item(i, Option_column.저가.value).setBackground(QBrush(풋월고색))
                        self.tableWidget_put.item(i, Option_column.저가.value).setForeground(QBrush(흰색))
                    else:
                        pass
                else:
                    pass

                if put_node_state['전저']:

                    if df_cm_put.iloc[i]['전저'] in cm_put_저가_extend:

                        self.tableWidget_put.item(i, Option_column.전저.value).setBackground(QBrush(풋전저색))
                        self.tableWidget_put.item(i, Option_column.전저.value).setForeground(QBrush(흰색))
                    else:
                        pass

                    if df_cm_put.iloc[i]['저가'] in cm_put_전저_extend:

                        self.tableWidget_put.item(i, Option_column.저가.value).setBackground(QBrush(풋전저색))
                        self.tableWidget_put.item(i, Option_column.저가.value).setForeground(QBrush(검정색))
                    else:
                        pass
                else:
                    pass

                if put_node_state['전고']:

                    if df_cm_put.iloc[i]['전고'] in cm_put_저가_extend:

                        self.tableWidget_put.item(i, Option_column.전고.value).setBackground(QBrush(풋전고색))
                        self.tableWidget_put.item(i, Option_column.전고.value).setForeground(QBrush(검정색))
                    else:
                        pass

                    if df_cm_put.iloc[i]['저가'] in cm_put_전고_extend:

                        self.tableWidget_put.item(i, Option_column.저가.value).setBackground(QBrush(풋전고색))
                        self.tableWidget_put.item(i, Option_column.저가.value).setForeground(QBrush(검정색))
                    else:
                        pass
                else:
                    pass

                if put_node_state['종가']:

                    if df_cm_put.iloc[i]['종가'] in cm_put_저가_extend:

                        self.tableWidget_put.item(i, Option_column.종가.value).setBackground(QBrush(풋종가색))
                        self.tableWidget_put.item(i, Option_column.종가.value).setForeground(QBrush(흰색))
                    else:
                        pass

                    if df_cm_put.iloc[i]['저가'] in cm_put_종가_extend:

                        self.tableWidget_put.item(i, Option_column.저가.value).setBackground(QBrush(풋종가색))
                        self.tableWidget_put.item(i, Option_column.저가.value).setForeground(QBrush(흰색))
                    else:
                        pass
                else:
                    pass

                if put_node_state['피봇']:

                    if df_cm_put.iloc[i]['피봇'] in cm_put_저가_extend:

                        self.tableWidget_put.item(i, Option_column.피봇.value).setBackground(QBrush(풋피봇색))
                        self.tableWidget_put.item(i, Option_column.피봇.value).setForeground(QBrush(검정색))
                    else:
                        pass

                    if df_cm_put.iloc[i]['저가'] in cm_put_피봇_extend:

                        self.tableWidget_put.item(i, Option_column.저가.value).setBackground(QBrush(풋피봇색))
                        self.tableWidget_put.item(i, Option_column.저가.value).setForeground(QBrush(검정색))
                    else:
                        pass
                else:
                    pass

                if put_node_state['시가']:

                    if df_cm_put.iloc[i]['시가'] in cm_put_저가_extend:

                        self.tableWidget_put.item(i, Option_column.시가.value).setBackground(QBrush(풋시가색))
                        self.tableWidget_put.item(i, Option_column.시가.value).setForeground(QBrush(흰색))
                    else:
                        pass

                    if df_cm_put.iloc[i]['저가'] in cm_put_시가_extend:

                        self.tableWidget_put.item(i, Option_column.저가.value).setBackground(QBrush(풋시가색))
                        self.tableWidget_put.item(i, Option_column.저가.value).setForeground(QBrush(흰색))
                    else:
                        pass
                else:
                    pass

                # 콜 node 컬러링                
                if call_node_state['기준가']:

                    if df_cm_put.iloc[i]['저가'] in cm_call_기준가_extend:

                        self.tableWidget_put.item(i, Option_column.저가.value).setBackground(QBrush(콜기준가색))
                        self.tableWidget_put.item(i, Option_column.저가.value).setForeground(QBrush(흰색))
                    else:
                        pass
                else:
                    pass

                if call_node_state['월저']:

                    if df_cm_put.iloc[i]['저가'] in cm_call_월저_extend:

                        self.tableWidget_put.item(i, Option_column.저가.value).setBackground(QBrush(콜월저색))
                        self.tableWidget_put.item(i, Option_column.저가.value).setForeground(QBrush(검정색))
                    else:
                        pass
                else:
                    pass

                if call_node_state['월고']:

                    if df_cm_put.iloc[i]['저가'] in cm_call_월고_extend:

                        self.tableWidget_put.item(i, Option_column.저가.value).setBackground(QBrush(콜월고색))
                        self.tableWidget_put.item(i, Option_column.저가.value).setForeground(QBrush(흰색))
                    else:
                        pass
                else:
                    pass

                if call_node_state['전저']:

                    if df_cm_put.iloc[i]['저가'] in cm_call_전저_extend:

                        self.tableWidget_put.item(i, Option_column.저가.value).setBackground(QBrush(콜전저색))
                        self.tableWidget_put.item(i, Option_column.저가.value).setForeground(QBrush(검정색))
                    else:
                        pass
                else:
                    pass

                if call_node_state['전고']:

                    if df_cm_put.iloc[i]['저가'] in cm_call_전고_extend:

                        self.tableWidget_put.item(i, Option_column.저가.value).setBackground(QBrush(콜전고색))
                        self.tableWidget_put.item(i, Option_column.저가.value).setForeground(QBrush(검정색))
                    else:
                        pass
                else:
                    pass

                if call_node_state['종가']:

                    if df_cm_put.iloc[i]['저가'] in cm_call_종가_extend:

                        self.tableWidget_put.item(i, Option_column.저가.value).setBackground(QBrush(콜종가색))
                        self.tableWidget_put.item(i, Option_column.저가.value).setForeground(QBrush(흰색))
                    else:
                        pass
                else:
                    pass

                if call_node_state['피봇']:

                    if df_cm_put.iloc[i]['저가'] in cm_call_피봇_extend:

                        self.tableWidget_put.item(i, Option_column.저가.value).setBackground(QBrush(콜피봇색))
                        self.tableWidget_put.item(i, Option_column.저가.value).setForeground(QBrush(검정색))
                    else:
                        pass
                else:
                    pass

                if call_node_state['시가']:

                    if df_cm_put.iloc[i]['저가'] in cm_call_시가_extend:

                        self.tableWidget_put.item(i, Option_column.저가.value).setBackground(QBrush(콜시가색))
                        self.tableWidget_put.item(i, Option_column.저가.value).setForeground(QBrush(흰색))
                    else:
                        pass
                else:
                    pass                
                
                if df_cm_put.iloc[i]['저가'] in coreval:

                    self.tableWidget_put.item(i, Option_column.저가.value).setBackground(QBrush(대맥점색))
                    self.tableWidget_put.item(i, Option_column.저가.value).setForeground(QBrush(검정색))
                else:
                    pass
        else:
            pass

        process_time = (timeit.default_timer() - start_time) * 1000
        print('put low color update check process time : %.2f ms' % process_time)

        str = '[{0:02d}:{1:02d}:{2:02d}] Put low color update : {3:0.2f} ms\r'.format(delta_hour, delta_minute, delta_sec, process_time)
        self.textBrowser.append(str)

    def put_high_update_color_check(self):
	
        start_time = timeit.default_timer()

        if call_scroll_end_position <= nCount_cm_option_pairs:

            for i in range(call_scroll_begin_position, call_scroll_end_position):
                
                # 콜 node 컬러링
                if call_node_state['기준가']:

                    if df_cm_call.iloc[i]['기준가'] in cm_put_고가_extend:

                        self.tableWidget_call.item(i, Option_column.기준가.value).setBackground(QBrush(콜기준가색))
                        self.tableWidget_call.item(i, Option_column.기준가.value).setForeground(QBrush(흰색))
                    else:
                        pass
                else:
                    pass

                if call_node_state['월저']:

                    if df_cm_call.iloc[i]['월저'] in cm_put_고가_extend:

                        self.tableWidget_call.item(i, Option_column.월저.value).setBackground(QBrush(콜월저색))
                        self.tableWidget_call.item(i, Option_column.월저.value).setForeground(QBrush(검정색))
                    else:
                        pass
                else:
                    pass

                if call_node_state['월고']:

                    if df_cm_call.iloc[i]['월고'] in cm_put_고가_extend:

                        self.tableWidget_call.item(i, Option_column.월고.value).setBackground(QBrush(콜월고색))
                        self.tableWidget_call.item(i, Option_column.월고.value).setForeground(QBrush(흰색))
                    else:
                        pass
                else:
                    pass

                if call_node_state['전저']:

                    if df_cm_call.iloc[i]['전저'] in cm_put_고가_extend:

                        self.tableWidget_call.item(i, Option_column.전저.value).setBackground(QBrush(콜전저색))
                        self.tableWidget_call.item(i, Option_column.전저.value).setForeground(QBrush(검정색))
                    else:
                        pass
                else:
                    pass

                if call_node_state['전고']:

                    if df_cm_call.iloc[i]['전고'] in cm_put_고가_extend:

                        self.tableWidget_call.item(i, Option_column.전고.value).setBackground(QBrush(콜전고색))
                        self.tableWidget_call.item(i, Option_column.전고.value).setForeground(QBrush(검정색))
                    else:
                        pass
                else:
                    pass

                if call_node_state['종가']:

                    if df_cm_call.iloc[i]['종가'] in cm_put_고가_extend:

                        self.tableWidget_call.item(i, Option_column.종가.value).setBackground(QBrush(콜종가색))
                        self.tableWidget_call.item(i, Option_column.종가.value).setForeground(QBrush(흰색))
                    else:
                        pass
                else:
                    pass

                if call_node_state['피봇']:

                    if df_cm_call.iloc[i]['피봇'] in cm_put_고가_extend:

                        self.tableWidget_call.item(i, Option_column.피봇.value).setBackground(QBrush(콜피봇색))
                        self.tableWidget_call.item(i, Option_column.피봇.value).setForeground(QBrush(검정색))
                    else:
                        pass
                else:
                    pass

                if call_node_state['시가']:

                    if df_cm_call.iloc[i]['시가'] in cm_put_고가_extend:

                        self.tableWidget_call.item(i, Option_column.시가.value).setBackground(QBrush(콜시가색))
                        self.tableWidget_call.item(i, Option_column.시가.value).setForeground(QBrush(흰색))
                    else:
                        pass
                else:
                    pass 
        else:
            pass

        if put_scroll_end_position <= nCount_cm_option_pairs:            

            for i in range(put_scroll_begin_position, put_scroll_end_position):
                
                # 풋 node 컬러링
                if put_node_state['기준가']:

                    if df_cm_put.iloc[i]['기준가'] in cm_put_고가_extend:

                        self.tableWidget_put.item(i, Option_column.기준가.value).setBackground(QBrush(풋기준가색))
                        self.tableWidget_put.item(i, Option_column.기준가.value).setForeground(QBrush(흰색))
                    else:
                        pass

                    if df_cm_put.iloc[i]['고가'] in cm_put_기준가_extend:

                        self.tableWidget_put.item(i, Option_column.고가.value).setBackground(QBrush(풋기준가색))
                        self.tableWidget_put.item(i, Option_column.고가.value).setForeground(QBrush(흰색))
                    else:
                        pass
                else:
                    pass

                if put_node_state['월저']:

                    if df_cm_put.iloc[i]['월저'] in cm_put_고가_extend:

                        self.tableWidget_put.item(i, Option_column.월저.value).setBackground(QBrush(풋월저색))
                        self.tableWidget_put.item(i, Option_column.월저.value).setForeground(QBrush(흰색))
                    else:
                        pass

                    if df_cm_put.iloc[i]['고가'] in cm_put_월저_extend:

                        self.tableWidget_put.item(i, Option_column.고가.value).setBackground(QBrush(풋월저색))
                        self.tableWidget_put.item(i, Option_column.고가.value).setForeground(QBrush(흰색))
                    else:
                        pass
                else:
                    pass

                if put_node_state['월고']:

                    if df_cm_put.iloc[i]['월고'] in cm_put_고가_extend:

                        self.tableWidget_put.item(i, Option_column.월고.value).setBackground(QBrush(풋월고색))
                        self.tableWidget_put.item(i, Option_column.월고.value).setForeground(QBrush(흰색))
                    else:
                        pass

                    if df_cm_put.iloc[i]['고가'] in cm_put_월고_extend:

                        self.tableWidget_put.item(i, Option_column.고가.value).setBackground(QBrush(풋월고색))
                        self.tableWidget_put.item(i, Option_column.고가.value).setForeground(QBrush(흰색))
                    else:
                        pass
                else:
                    pass

                if put_node_state['전저']:

                    if df_cm_put.iloc[i]['전저'] in cm_put_고가_extend:

                        self.tableWidget_put.item(i, Option_column.전저.value).setBackground(QBrush(풋전저색))
                        self.tableWidget_put.item(i, Option_column.전저.value).setForeground(QBrush(흰색))
                    else:
                        pass

                    if df_cm_put.iloc[i]['고가'] in cm_put_전저_extend:

                        self.tableWidget_put.item(i, Option_column.고가.value).setBackground(QBrush(풋전저색))
                        self.tableWidget_put.item(i, Option_column.고가.value).setForeground(QBrush(검정색))
                    else:
                        pass
                else:
                    pass

                if put_node_state['전고']:

                    if df_cm_put.iloc[i]['전고'] in cm_put_고가_extend:

                        self.tableWidget_put.item(i, Option_column.전고.value).setBackground(QBrush(풋전고색))
                        self.tableWidget_put.item(i, Option_column.전고.value).setForeground(QBrush(검정색))
                    else:
                        pass

                    if df_cm_put.iloc[i]['고가'] in cm_put_전고_extend:

                        self.tableWidget_put.item(i, Option_column.고가.value).setBackground(QBrush(풋전고색))
                        self.tableWidget_put.item(i, Option_column.고가.value).setForeground(QBrush(검정색))
                    else:
                        pass
                else:
                    pass

                if put_node_state['종가']:

                    if df_cm_put.iloc[i]['종가'] in cm_put_고가_extend:

                        self.tableWidget_put.item(i, Option_column.종가.value).setBackground(QBrush(풋종가색))
                        self.tableWidget_put.item(i, Option_column.종가.value).setForeground(QBrush(흰색))
                    else:
                        pass

                    if df_cm_put.iloc[i]['고가'] in cm_put_종가_extend:

                        self.tableWidget_put.item(i, Option_column.고가.value).setBackground(QBrush(풋종가색))
                        self.tableWidget_put.item(i, Option_column.고가.value).setForeground(QBrush(흰색))
                    else:
                        pass
                else:
                    pass

                if put_node_state['피봇']:

                    if df_cm_put.iloc[i]['피봇'] in cm_put_고가_extend:

                        self.tableWidget_put.item(i, Option_column.피봇.value).setBackground(QBrush(풋피봇색))
                        self.tableWidget_put.item(i, Option_column.피봇.value).setForeground(QBrush(검정색))
                    else:
                        pass

                    if df_cm_put.iloc[i]['고가'] in cm_put_피봇_extend:

                        self.tableWidget_put.item(i, Option_column.고가.value).setBackground(QBrush(풋피봇색))
                        self.tableWidget_put.item(i, Option_column.고가.value).setForeground(QBrush(검정색))
                    else:
                        pass
                else:
                    pass

                if put_node_state['시가']:

                    if df_cm_put.iloc[i]['시가'] in cm_put_고가_extend:

                        self.tableWidget_put.item(i, Option_column.시가.value).setBackground(QBrush(풋시가색))
                        self.tableWidget_put.item(i, Option_column.시가.value).setForeground(QBrush(흰색))
                    else:
                        pass

                    if df_cm_put.iloc[i]['고가'] in cm_put_시가_extend:

                        self.tableWidget_put.item(i, Option_column.고가.value).setBackground(QBrush(풋시가색))
                        self.tableWidget_put.item(i, Option_column.고가.value).setForeground(QBrush(흰색))
                    else:
                        pass
                else:
                    pass

                # 콜 node 컬러링                
                if call_node_state['기준가']:

                    if df_cm_put.iloc[i]['고가'] in cm_call_기준가_extend:

                        self.tableWidget_put.item(i, Option_column.고가.value).setBackground(QBrush(콜기준가색))
                        self.tableWidget_put.item(i, Option_column.고가.value).setForeground(QBrush(흰색))
                    else:
                        pass
                else:
                    pass

                if call_node_state['월저']:

                    if df_cm_put.iloc[i]['고가'] in cm_call_월저_extend:

                        self.tableWidget_put.item(i, Option_column.고가.value).setBackground(QBrush(콜월저색))
                        self.tableWidget_put.item(i, Option_column.고가.value).setForeground(QBrush(검정색))
                    else:
                        pass
                else:
                    pass

                if call_node_state['월고']:

                    if df_cm_put.iloc[i]['고가'] in cm_call_월고_extend:

                        self.tableWidget_put.item(i, Option_column.고가.value).setBackground(QBrush(콜월고색))
                        self.tableWidget_put.item(i, Option_column.고가.value).setForeground(QBrush(흰색))
                    else:
                        pass
                else:
                    pass

                if call_node_state['전저']:

                    if df_cm_put.iloc[i]['고가'] in cm_call_전저_extend:

                        self.tableWidget_put.item(i, Option_column.고가.value).setBackground(QBrush(콜전저색))
                        self.tableWidget_put.item(i, Option_column.고가.value).setForeground(QBrush(검정색))
                    else:
                        pass
                else:
                    pass

                if call_node_state['전고']:

                    if df_cm_put.iloc[i]['고가'] in cm_call_전고_extend:

                        self.tableWidget_put.item(i, Option_column.고가.value).setBackground(QBrush(콜전고색))
                        self.tableWidget_put.item(i, Option_column.고가.value).setForeground(QBrush(검정색))
                    else:
                        pass
                else:
                    pass

                if call_node_state['종가']:

                    if df_cm_put.iloc[i]['고가'] in cm_call_종가_extend:

                        self.tableWidget_put.item(i, Option_column.고가.value).setBackground(QBrush(콜종가색))
                        self.tableWidget_put.item(i, Option_column.고가.value).setForeground(QBrush(흰색))
                    else:
                        pass
                else:
                    pass

                if call_node_state['피봇']:

                    if df_cm_put.iloc[i]['고가'] in cm_call_피봇_extend:

                        self.tableWidget_put.item(i, Option_column.고가.value).setBackground(QBrush(콜피봇색))
                        self.tableWidget_put.item(i, Option_column.고가.value).setForeground(QBrush(검정색))
                    else:
                        pass
                else:
                    pass

                if call_node_state['시가']:

                    if df_cm_put.iloc[i]['고가'] in cm_call_시가_extend:

                        self.tableWidget_put.item(i, Option_column.고가.value).setBackground(QBrush(콜시가색))
                        self.tableWidget_put.item(i, Option_column.고가.value).setForeground(QBrush(흰색))
                    else:
                        pass
                else:
                    pass 

                if df_cm_put.iloc[i]['고가'] in coreval:

                    self.tableWidget_put.item(i, Option_column.고가.value).setBackground(QBrush(대맥점색))
                    self.tableWidget_put.item(i, Option_column.고가.value).setForeground(QBrush(검정색))
                else:
                    pass
        else:
            pass        

        process_time = (timeit.default_timer() - start_time) * 1000
        print('put high color update check process time : %.2f ms' % process_time)

        str = '[{0:02d}:{1:02d}:{2:02d}] Put high color update : {3:0.2f} ms\r'.format(delta_hour, delta_minute, delta_sec, process_time)
        self.textBrowser.append(str)

    def OnReceiveData(self, szTrCode, result):

        global gmshcode
        global cm_call_code, cm_put_code
        global cm_call_actval, cm_put_actval
        global df_plotdata_fut
        global atm_index, old_atm_index
        global df_plotdata_cm_call, df_plotdata_cm_put
        global df_plotdata_cm_call_volume, df_plotdata_cm_put_volume, df_plotdata_cm_volume_cha
        global df_plotdata_cm_call_oi, df_plotdata_cm_put_oi, df_plotdata_cm_oi_cha
        global atm_str

        global fut_realdata

        global call_ckbox
        global selected_call
        global df_cm_call, df_cm_call_ho

        global put_ckbox
        global selected_put
        global df_cm_put, df_cm_put_ho

        global df_cm_call_che, df_cm_put_che

        global cm_call_행사가, cm_put_행사가

        global cm_call_기준가, cm_call_월저, cm_call_월고, cm_call_전저, cm_call_전고, cm_call_종가, cm_call_피봇, \
            cm_call_시가, cm_call_저가, cm_call_고가
        global cm_call_기준가_extend, cm_call_월저_extend, cm_call_월고_extend, cm_call_전저_extend, cm_call_전고_extend, \
            cm_call_종가_extend, cm_call_피봇_extend, cm_call_시가_extend, cm_call_저가_extend, cm_call_고가_extend

        global cm_put_기준가, cm_put_월저, cm_put_월고, cm_put_전저, cm_put_전고, cm_put_종가, cm_put_피봇, \
            cm_put_시가, cm_put_저가, cm_put_고가
        global cm_put_기준가_extend, cm_put_월저_extend, cm_put_월고_extend, cm_put_전저_extend, cm_put_전고_extend, \
            cm_put_종가_extend, cm_put_피봇_extend, cm_put_시가_extend, cm_put_저가_extend, cm_put_고가_extend

        global nCount_cm_option_pairs

        global df_plotdata_fut, df_plotdata_kp200
        global 콜_미결합, 풋_미결합, 콜미결퍼센트, 풋미결퍼센트
        global call_atm_value, put_atm_value

        global df_cme, df_futures
        global kp200_realdata

        global refresh_flag

        global call_oi_percent_init_value, put_oi_percent_init_value
        global call_gap_percent, call_db_percent, put_gap_percent, put_db_percent
        global volume_cha_sign

        global call_open
        global call_ol
        global call_oh

        global put_open
        global put_ol
        global put_oh

        global call_volume_total, put_volume_total

        dt = datetime.datetime.now()

        if szTrCode == 't2101':

            df = result[0]

            fut_realdata['KP200'] = df['KOSPI200지수']

            fut_realdata['시가'] = df['시가']

            item = QTableWidgetItem("{0:0.2f}".format(df['시가']))
            item.setTextAlignment(Qt.AlignCenter)
            item.setBackground(QBrush(기본바탕색))

            if fut_realdata['시가'] > fut_realdata['종가']:
                item.setForeground(QBrush(적색))
            elif fut_realdata['시가'] < fut_realdata['종가']:
                item.setForeground(QBrush(청색))
            else:
                item.setForeground(QBrush(검정색))

            self.tableWidget_fut.setItem(1, Futures_column.시가.value, item)

            if not overnight:

                df_plotdata_kp200.iloc[0][0] = fut_realdata['KP200']
                df_plotdata_fut.iloc[0][0] = fut_realdata['종가']

                if fut_realdata['시가'] > 0:

                    df_plotdata_fut.iloc[0][1] = fut_realdata['시가']
                    fut_realdata['시가갭'] = fut_realdata['시가'] - fut_realdata['종가']
                    fut_realdata['피봇'] = self.calc_pivot(fut_realdata['전저'], fut_realdata['전고'],
                                                         fut_realdata['종가'], fut_realdata['시가'])
                else:
                    fut_realdata['시가갭'] = 0.0
                    fut_realdata['피봇'] = 0.0
            else:
                pass

            item = QTableWidgetItem("{0:0.2f}".format(fut_realdata['시가갭']))
            item.setTextAlignment(Qt.AlignCenter)
            self.tableWidget_fut.setItem(1, Futures_column.시가갭.value, item)

            item = QTableWidgetItem("{0:0.2f}".format(fut_realdata['피봇']))
            item.setTextAlignment(Qt.AlignCenter)
            self.tableWidget_fut.setItem(1, Futures_column.피봇.value, item)

            if pre_start:

                kp200_realdata['종가'] = df['KOSPI200지수']

            else:
                if df['KOSPI200전일대비구분'] == '2':

                    kp200_realdata['종가'] = df['KOSPI200지수'] - df['KOSPI200전일대비']

                elif df['KOSPI200전일대비구분'] == '5':

                    kp200_realdata['종가'] = df['KOSPI200지수'] + df['KOSPI200전일대비']

                else:
                    kp200_realdata['종가'] = df['KOSPI200지수']

            item = QTableWidgetItem("{0:0.2f}".format(kp200_realdata['종가']))
            item.setTextAlignment(Qt.AlignCenter)
            self.tableWidget_fut.setItem(2, Futures_column.종가.value, item)

            fut_realdata['저가'] = df['저가']

            item = QTableWidgetItem("{0:0.2f}".format(fut_realdata['저가']))
            item.setTextAlignment(Qt.AlignCenter)
            self.tableWidget_fut.setItem(1, Futures_column.저가.value, item)

            fut_realdata['현재가'] = df['현재가']

            item = QTableWidgetItem("{0:0.2f}".format(fut_realdata['현재가']))
            item.setTextAlignment(Qt.AlignCenter)
            item.setBackground(QBrush(옅은회색))
            self.tableWidget_fut.setItem(1, Futures_column.현재가.value, item)

            fut_realdata['고가'] = df['고가']

            item = QTableWidgetItem("{0:0.2f}".format(fut_realdata['고가']))
            item.setTextAlignment(Qt.AlignCenter)
            self.tableWidget_fut.setItem(1, Futures_column.고가.value, item)

            if fut_realdata['시가'] > 0:

                fut_realdata['대비'] = int((round((df['현재가'] - df['시가']), 2)) * 100)
            else:
                fut_realdata['대비'] = 0

            item = QTableWidgetItem("{0:0.0f}".format(fut_realdata['대비']))
            item.setTextAlignment(Qt.AlignCenter)
            self.tableWidget_fut.setItem(1, Futures_column.대비.value, item)

            fut_realdata['진폭'] = df['고가'] - df['저가']

            item = QTableWidgetItem("{0:0.2f}".format(fut_realdata['진폭']))
            item.setTextAlignment(Qt.AlignCenter)
            self.tableWidget_fut.setItem(1, Futures_column.진폭.value, item)

            fut_realdata['거래량'] = df['거래량']

            item = QTableWidgetItem("{0}".format(df['거래량']))
            item.setTextAlignment(Qt.AlignCenter)
            self.tableWidget_fut.setItem(1, Futures_column.거래량.value, item)

            fut_realdata['미결'] = df['미결제량']

            item = QTableWidgetItem("{0}".format(df['미결제량']))
            item.setTextAlignment(Qt.AlignCenter)
            self.tableWidget_fut.setItem(1, Futures_column.OI.value, item)

            fut_realdata['미결증감'] = df['미결제증감']

            item = QTableWidgetItem("{0}".format(fut_realdata['미결증감']))
            item.setTextAlignment(Qt.AlignCenter)

            if fut_realdata['미결증감'] < 0:
                item.setBackground(QBrush(녹색))
            else:
                item.setBackground(QBrush(기본바탕색))

            self.tableWidget_fut.setItem(1, Futures_column.OID.value, item)

            self.tableWidget_fut.resizeColumnsToContents()

            fut_realdata['선물코드'] = 'FUT'

            columns = ['선물코드', 'KP200', '전저', '전고', '종가', '피봇', '시가', '시가갭', '저가',
                       '현재가', '고가', '대비', '진폭', '거래량', '미결', '미결증감']

            df_futures = DataFrame(data=[fut_realdata], columns=columns)

        elif szTrCode == 't2301':

            block, df, df1 = result

            if not refresh_flag:

                # 옵션 행사가 갯수
                nCount_cm_option_pairs = len(df)

                call_result = []
                callho_result = []
                put_result = []
                putho_result = []

                callche_result = []
                putche_result = []

                if not overnight:

                    self.Plot_Opt.setRange(xRange=[0, 395 + 10], padding=0)
                    time_line.setValue(404)

                    self.Plot_Fut.setRange(xRange=[0, 395 + 10], padding=0)
                    time_line_fut.setValue(404)

                    df_plotdata_cm_call = DataFrame(index=range(0, nCount_cm_option_pairs), columns=range(0, 395 + 10))
                    df_plotdata_cm_put = DataFrame(index=range(0, nCount_cm_option_pairs), columns=range(0, 395 + 10))

                    df_plotdata_cm_call_volume = DataFrame(index=range(0, 1), columns=range(0, 395 + 10))
                    df_plotdata_cm_put_volume = DataFrame(index=range(0, 1), columns=range(0, 395 + 10))
                    df_plotdata_cm_volume_cha = DataFrame(index=range(0, 1), columns=range(0, 395 + 10))

                    df_plotdata_cm_call_oi = DataFrame(index=range(0, 1), columns=range(0, 395 + 10))
                    df_plotdata_cm_put_oi = DataFrame(index=range(0, 1), columns=range(0, 395 + 10))
                    df_plotdata_cm_oi_cha = DataFrame(index=range(0, 1), columns=range(0, 395 + 10))

                    df_plotdata_fut = DataFrame(index=range(0, 1), columns=range(0, 395 + 10))
                    df_plotdata_kp200 = DataFrame(index=range(0, 1), columns=range(0, 395 + 10))

                    volume_cha_sign = [False] * 406
                else:
                    self.Plot_Opt.setRange(xRange=[0, 660 + 10], padding=0)
                    time_line.setValue(669)

                    self.Plot_Fut.setRange(xRange=[0, 660 + 10], padding=0)
                    time_line_fut.setValue(669)

                    df_plotdata_cm_call = DataFrame(index=range(0, nCount_cm_option_pairs), columns=range(0, 660 + 10))
                    df_plotdata_cm_put = DataFrame(index=range(0, nCount_cm_option_pairs), columns=range(0, 660 + 10))

                    df_plotdata_cm_call_volume = DataFrame(index=range(0, 1), columns=range(0, 660 + 10))
                    df_plotdata_cm_put_volume = DataFrame(index=range(0, 1), columns=range(0, 660 + 10))
                    df_plotdata_cm_volume_cha = DataFrame(index=range(0, 1), columns=range(0, 660 + 10))

                    df_plotdata_cm_call_oi = DataFrame(index=range(0, 1), columns=range(0, 660 + 10))
                    df_plotdata_cm_put_oi = DataFrame(index=range(0, 1), columns=range(0, 660 + 10))
                    df_plotdata_cm_oi_cha = DataFrame(index=range(0, 1), columns=range(0, 660 + 10))

                    df_plotdata_fut = DataFrame(index=range(0, 1), columns=range(0, 660 + 10))
                    df_plotdata_kp200 = DataFrame(index=range(0, 1), columns=range(0, 660 + 10))

                    volume_cha_sign = [False] * 671

                # 콜처리
                for i in range(nCount_cm_option_pairs):

                    행사가 = df['행사가'][i]
                    item = QTableWidgetItem("{0:0.2f}".format(df['float_행사가'][i]))
                    item.setTextAlignment(Qt.AlignCenter)
                    self.tableWidget_call.setItem(i, Option_column.행사가.value, item)

                    cm_call_code.append(df['콜옵션코드'][i])
                    cm_call_actval.append(df['콜옵션코드'][i][5:8])

                    OLOH = ''
                    item = QTableWidgetItem("{0}".format(OLOH))
                    item.setTextAlignment(Qt.AlignCenter)
                    self.tableWidget_call.setItem(i, Option_column.OLOH.value, item)

                    시가 = round(df['시가'][i], 2)

                    현재가 = df['현재가'][i]
                    item = QTableWidgetItem("{0:0.2f}".format(현재가))
                    item.setTextAlignment(Qt.AlignCenter)
                    item.setBackground(QBrush(옅은회색))

                    if pre_start:

                        item.setForeground(QBrush(검정색))
                    else:
                        if 시가 > 0:

                            if 현재가 > 시가:
                                item.setForeground(QBrush(적색))
                            elif 현재가 < 시가:
                                item.setForeground(QBrush(청색))
                            else:
                                item.setForeground(QBrush(검정색))
                        else:
                            pass

                    self.tableWidget_call.setItem(i, Option_column.현재가.value, item)

                    if df['전일대비구분'][i] == '2':

                        종가 = round((현재가 - df['전일대비'][i]), 2)

                    elif df['전일대비구분'][i] == '5':

                        종가 = round((현재가 + df['전일대비'][i]), 2)

                    else:
                        종가 = round(현재가, 2)

                    item = QTableWidgetItem("{0:0.2f}".format(종가))
                    item.setTextAlignment(Qt.AlignCenter)
                    self.tableWidget_call.setItem(i, Option_column.종가.value, item)

                    df_plotdata_cm_call.iloc[i][0] = 종가

                    저가 = df['저가'][i]
                    item = QTableWidgetItem("{0:0.2f}".format(저가))
                    item.setTextAlignment(Qt.AlignCenter)
                    self.tableWidget_call.setItem(i, Option_column.저가.value, item)

                    고가 = df['고가'][i]
                    item = QTableWidgetItem("{0:0.2f}".format(고가))
                    item.setTextAlignment(Qt.AlignCenter)
                    self.tableWidget_call.setItem(i, Option_column.고가.value, item)

                    진폭 = 고가 - 저가
                    item = QTableWidgetItem("{0:0.2f}".format(진폭))
                    item.setTextAlignment(Qt.AlignCenter)
                    self.tableWidget_call.setItem(i, Option_column.진폭.value, item)

                    if 시가 > 0:

                        item = QTableWidgetItem("{0:0.2f}".format(시가))
                        item.setTextAlignment(Qt.AlignCenter)

                        if 시가 > 종가:
                            item.setForeground(QBrush(적색))
                        elif 시가 < 종가:
                            item.setForeground(QBrush(청색))
                        else:
                            item.setForeground(QBrush(검정색))

                        self.tableWidget_call.setItem(i, Option_column.시가.value, item)

                        if not overnight:
                            df_plotdata_cm_call.iloc[i][1] = 시가
                        else:
                            pass

                        시가갭 = 시가 - 종가
                        대비 = int(round((현재가 - 시가) * 100, 2))

                        if 시가 > 0.3 and 저가 < 고가:

                            call_gap_percent[i] = (시가 / 종가 - 1) * 100

                            gap_str = "{0:0.2f}({1:0.0f}%)".format(시가갭, call_gap_percent[i])

                            item = QTableWidgetItem(gap_str)
                            item.setTextAlignment(Qt.AlignCenter)
                            self.tableWidget_call.setItem(i, Option_column.시가갭.value, item)

                            call_db_percent[i] = (현재가 / 시가 - 1) * 100

                            gap_str = "{0:0.0f}({1:0.0f}%)".format(대비, call_db_percent[i])

                            item = QTableWidgetItem(gap_str)
                            item.setTextAlignment(Qt.AlignCenter)
                            self.tableWidget_call.setItem(i, Option_column.대비.value, item)
                        else:
                            gap_str = "{0:0.2f}".format(시가갭)

                            item = QTableWidgetItem(gap_str)
                            item.setTextAlignment(Qt.AlignCenter)
                            self.tableWidget_call.setItem(i, Option_column.시가갭.value, item)

                            gap_str = "{0:0.0f}".format(대비)

                            item = QTableWidgetItem(gap_str)
                            item.setTextAlignment(Qt.AlignCenter)
                            self.tableWidget_call.setItem(i, Option_column.대비.value, item)
                    else:
                        시가 = 0.0
                        시가갭 = 0.0
                        대비 = 0

                        item = QTableWidgetItem("{0:0.2f}".format(시가))
                        item.setTextAlignment(Qt.AlignCenter)
                        self.tableWidget_call.setItem(i, Option_column.시가.value, item)

                        item = QTableWidgetItem("{0:0.2f}".format(시가갭))
                        item.setTextAlignment(Qt.AlignCenter)
                        self.tableWidget_call.setItem(i, Option_column.시가갭.value, item)

                        item = QTableWidgetItem("{0}".format(대비))
                        item.setTextAlignment(Qt.AlignCenter)
                        self.tableWidget_call.setItem(i, Option_column.대비.value, item)

                    피봇 = 0.0
                    item = QTableWidgetItem("{0:0.2f}".format(피봇))
                    item.setTextAlignment(Qt.AlignCenter)
                    self.tableWidget_call.setItem(i, Option_column.피봇.value, item)

                    if overnight:
                        전저 = 저가
                        종가 = 현재가
                        전고 = 고가
                    else:
                        전저 = 0.0
                        전고 = 0.0

                        if 시가 > 0 and round(저가, 2) < round(고가, 2):
                            self.tableWidget_call.item(i, Option_column.행사가.value).setBackground(QBrush(녹색))
                            self.tableWidget_call.item(i, Option_column.행사가.value).setForeground(QBrush(검정색))
                            pass
                        else:
                            pass

                    미결 = int(df['미결제약정'][i] * (df['현재가'][i] - 시가갭))
                    거래량 = df['거래량'][i]
                    수정거래량 = int(df['거래량'][i] * (df['현재가'][i] - 시가갭))

                    if pre_start:

                        temp = format(미결, ',')
                    else:
                        if comboindex == 1:

                            temp = format(수정거래량, ',')
                        else:
                            temp = format(미결, ',')

                    item = QTableWidgetItem(temp)
                    item.setTextAlignment(Qt.AlignCenter)
                    self.tableWidget_call.setItem(i, Option_column.OI.value, item)

                    미결증감 = int(round(df['미결제약정증감'][i] * df['현재가'][i]))
                    temp = format(미결증감, ',')

                    item = QTableWidgetItem(temp)
                    item.setTextAlignment(Qt.AlignCenter)
                    self.tableWidget_call.setItem(i, Option_column.OID.value, item)

                    if df['ATM구분'][i] == '1':

                        atm_index = i
                        old_atm_index = i

                        if not overnight:

                            call_ckbox[atm_index - 1].setCheckState(Qt.Checked)
                            call_ckbox[atm_index].setCheckState(Qt.Checked)
                            call_ckbox[atm_index + 1].setCheckState(Qt.Checked)

                            selected_call = [atm_index - 1, atm_index, atm_index + 1]
                        else:
                            pass
                    else:
                        pass

                    단축코드 = 0
                    체결시간 = 0
                    기준가 = 0.0
                    월저 = 0.0
                    월고 = 0.0

                    lst = [단축코드, 체결시간, 행사가, OLOH, 기준가, 월저, 월고, 전저, 전고, 종가, 피봇, 시가, 시가갭, 저가, 현재가,
                           고가, 대비, 진폭, 거래량, 수정거래량, 미결, 미결증감]
                    call_result.append(lst)

                    매도누적체결량 = 0
                    매도누적체결건수 = 0
                    매수누적체결량 = 0
                    매수누적체결건수 = 0

                    lst = [매도누적체결량, 매도누적체결건수, 매수누적체결량, 매수누적체결건수]
                    callche_result.append(lst)

                    매수건수 = 0
                    매도건수 = 0
                    매수잔량 = 0
                    매도잔량 = 0

                    lstho = [매수건수, 매도건수, 매수잔량, 매도잔량]
                    callho_result.append(lstho)

                columns = ['단축코드', '체결시간', '행사가', 'OLOH', '기준가', '월저', '월고', '전저', '전고', '종가', '피봇', '시가', '시가갭', '저가',
                           '현재가', '고가', '대비', '진폭', '거래량', '수정거래량', '미결', '미결증감']

                df_cm_call = DataFrame(data=call_result, columns=columns)

                columns = ['매도누적체결량', '매도누적체결건수', '매수누적체결량', '매수누적체결건수']
                df_cm_call_che = DataFrame(data=callche_result, columns=columns)

                columns = ['매수건수', '매도건수', '매수잔량', '매도잔량']
                df_cm_call_ho = DataFrame(data=callho_result, columns=columns)

                if pre_start:

                    미결 = format(df_cm_call['미결'].sum(), ',')

                    if 미결 != self.tableWidget_call.horizontalHeaderItem(Option_column.OI.value).text():
                        item = QTableWidgetItem(미결)
                        self.tableWidget_call.setHorizontalHeaderItem(Option_column.OI.value, item)
                    else:
                        pass
                else:
                    if comboindex == 1:

                        temp = format(df_cm_call['수정거래량'].sum(), ',')
                    else:
                        temp = format(df_cm_call['미결'].sum(), ',')
                    
                    if temp != self.tableWidget_call.horizontalHeaderItem(Option_column.OI.value).text():
                        item = QTableWidgetItem(temp)
                        self.tableWidget_call.setHorizontalHeaderItem(Option_column.OI.value, item)
                    else:
                        pass

                cm_call_행사가 = df_cm_call['행사가'].values.tolist()

                print(df_cm_call)

                self.tableWidget_call.resizeColumnsToContents()
                self.tableWidget_call.setColumnWidth(0, 15)

                # 풋처리
                for i in range(nCount_cm_option_pairs):

                    행사가 = df1['행사가'][i]
                    item = QTableWidgetItem("{0:0.2f}".format(df1['float_행사가'][i]))
                    item.setTextAlignment(Qt.AlignCenter)
                    self.tableWidget_put.setItem(i, Option_column.행사가.value, item)

                    cm_put_code.append(df1['풋옵션코드'][i])
                    cm_put_actval.append(df1['풋옵션코드'][i][5:8])

                    OLOH = ''
                    item = QTableWidgetItem("{0}".format(OLOH))
                    item.setTextAlignment(Qt.AlignCenter)
                    self.tableWidget_put.setItem(i, Option_column.OLOH.value, item)

                    시가 = round(df1['시가'][i], 2)

                    현재가 = df1['현재가'][i]
                    item = QTableWidgetItem("{0:0.2f}".format(현재가))
                    item.setTextAlignment(Qt.AlignCenter)
                    item.setBackground(QBrush(옅은회색))

                    if pre_start:

                        item.setForeground(QBrush(검정색))
                    else:
                        if 시가 > 0:

                            if 현재가 > 시가:
                                item.setForeground(QBrush(적색))
                            elif 현재가 < 시가:
                                item.setForeground(QBrush(청색))
                            else:
                                item.setForeground(QBrush(검정색))
                        else:
                            pass

                    self.tableWidget_put.setItem(i, Option_column.현재가.value, item)

                    if df1['전일대비구분'][i] == '2':

                        종가 = round((현재가 - df1['전일대비'][i]), 2)

                    elif df['전일대비구분'][i] == '5':

                        종가 = round((현재가 + df1['전일대비'][i]), 2)

                    else:
                        종가 = round(현재가, 2)

                    item = QTableWidgetItem("{0:0.2f}".format(종가))
                    item.setTextAlignment(Qt.AlignCenter)
                    self.tableWidget_put.setItem(i, Option_column.종가.value, item)

                    df_plotdata_cm_put.iloc[i][0] = 종가

                    저가 = df1['저가'][i]
                    item = QTableWidgetItem("{0:0.2f}".format(저가))
                    item.setTextAlignment(Qt.AlignCenter)
                    self.tableWidget_put.setItem(i, Option_column.저가.value, item)

                    고가 = df1['고가'][i]
                    item = QTableWidgetItem("{0:0.2f}".format(고가))
                    item.setTextAlignment(Qt.AlignCenter)
                    self.tableWidget_put.setItem(i, Option_column.고가.value, item)

                    진폭 = 고가 - 저가
                    item = QTableWidgetItem("{0:0.2f}".format(진폭))
                    item.setTextAlignment(Qt.AlignCenter)
                    self.tableWidget_put.setItem(i, Option_column.진폭.value, item)

                    if 시가 > 0:

                        item = QTableWidgetItem("{0:0.2f}".format(시가))
                        item.setTextAlignment(Qt.AlignCenter)

                        if 시가 > 종가:
                            item.setForeground(QBrush(적색))
                        elif 시가 < 종가:
                            item.setForeground(QBrush(청색))
                        else:
                            item.setForeground(QBrush(검정색))

                        self.tableWidget_put.setItem(i, Option_column.시가.value, item)

                        if not overnight:
                            df_plotdata_cm_put.iloc[i][1] = 시가
                        else:
                            pass

                        시가갭 = 시가 - 종가
                        대비 = int(round((현재가 - 시가) * 100, 2))

                        if 시가 > 0.3 and 저가 < 고가:

                            put_gap_percent[i] = (시가 / 종가 - 1) * 100

                            gap_str = "{0:0.2f}({1:0.0f}%)".format(시가갭, put_gap_percent[i])

                            item = QTableWidgetItem(gap_str)
                            item.setTextAlignment(Qt.AlignCenter)
                            self.tableWidget_put.setItem(i, Option_column.시가갭.value, item)

                            put_db_percent[i] = (현재가 / 시가 - 1) * 100

                            gap_str = "{0:0.0f}({1:0.0f}%)".format(대비, put_db_percent[i])

                            item = QTableWidgetItem(gap_str)
                            item.setTextAlignment(Qt.AlignCenter)
                            self.tableWidget_put.setItem(i, Option_column.대비.value, item)
                        else:
                            gap_str = "{0:0.2f}".format(시가갭)

                            item = QTableWidgetItem(gap_str)
                            item.setTextAlignment(Qt.AlignCenter)
                            self.tableWidget_put.setItem(i, Option_column.시가갭.value, item)

                            gap_str = "{0:0.0f}".format(대비)

                            item = QTableWidgetItem(gap_str)
                            item.setTextAlignment(Qt.AlignCenter)
                            self.tableWidget_put.setItem(i, Option_column.대비.value, item)
                    else:
                        시가 = 0.0
                        시가갭 = 0.0
                        대비 = 0

                        item = QTableWidgetItem("{0:0.2f}".format(시가))
                        item.setTextAlignment(Qt.AlignCenter)
                        self.tableWidget_put.setItem(i, Option_column.시가.value, item)

                        item = QTableWidgetItem("{0:0.2f}".format(시가갭))
                        item.setTextAlignment(Qt.AlignCenter)
                        self.tableWidget_put.setItem(i, Option_column.시가갭.value, item)

                        item = QTableWidgetItem("{0}".format(대비))
                        item.setTextAlignment(Qt.AlignCenter)
                        self.tableWidget_put.setItem(i, Option_column.대비.value, item)

                    피봇 = 0.0
                    item = QTableWidgetItem("{0:0.2f}".format(피봇))
                    item.setTextAlignment(Qt.AlignCenter)
                    self.tableWidget_put.setItem(i, Option_column.피봇.value, item)

                    if overnight:
                        전저 = 저가
                        종가 = 현재가
                        전고 = 고가
                    else:
                        전저 = 0.0
                        전고 = 0.0

                    if not overnight:

                        if 시가 > 0 and round(저가, 2) < round(고가, 2):
                            self.tableWidget_put.item(i, Option_column.행사가.value).setBackground(QBrush(녹색))
                            self.tableWidget_put.item(i, Option_column.행사가.value).setForeground(QBrush(검정색))
                            pass
                        else:
                            pass
                    else:
                        pass

                    미결 = int(df1['미결제약정'][i] * (df1['현재가'][i] - 시가갭))
                    거래량 = df1['거래량'][i]
                    수정거래량 = int(df1['거래량'][i] * (df1['현재가'][i] - 시가갭))

                    if pre_start:

                        temp = format(미결, ',')
                    else:
                        if comboindex == 1:

                            temp = format(수정거래량, ',')
                        else:
                            temp = format(미결, ',')                        

                    item = QTableWidgetItem(temp)
                    item.setTextAlignment(Qt.AlignCenter)
                    self.tableWidget_put.setItem(i, Option_column.OI.value, item)

                    미결증감 = int(round(df1['미결제약정증감'][i] * df1['현재가'][i]))
                    temp = format(미결증감, ',')

                    item = QTableWidgetItem(temp)
                    item.setTextAlignment(Qt.AlignCenter)
                    self.tableWidget_put.setItem(i, Option_column.OID.value, item)

                    if df1['ATM구분'][i] == '1':

                        # atm_str = 행사가
                        atm_index = i
                        old_atm_index = i

                        if not overnight:

                            put_ckbox[atm_index - 1].setCheckState(Qt.Checked)
                            put_ckbox[atm_index].setCheckState(Qt.Checked)
                            put_ckbox[atm_index + 1].setCheckState(Qt.Checked)

                            selected_put = [atm_index - 1, atm_index, atm_index + 1]
                        else:
                            pass
                    else:
                        pass

                    단축코드 = 0
                    체결시간 = 0
                    기준가 = 0.0
                    월저 = 0.0
                    월고 = 0.0

                    lst = [단축코드, 체결시간, 행사가, OLOH, 기준가, 월저, 월고, 전저, 전고, 종가, 피봇, 시가, 시가갭, 저가, 현재가,
                           고가, 대비, 진폭, 거래량, 수정거래량, 미결, 미결증감]
                    put_result.append(lst)

                    매도누적체결량 = 0
                    매도누적체결건수 = 0
                    매수누적체결량 = 0
                    매수누적체결건수 = 0

                    lst = [매도누적체결량, 매도누적체결건수, 매수누적체결량, 매수누적체결건수]
                    putche_result.append(lst)

                    매수건수 = 0
                    매도건수 = 0
                    매수잔량 = 0
                    매도잔량 = 0

                    lstho = [매수건수, 매도건수, 매수잔량, 매도잔량]
                    putho_result.append(lstho)

                columns = ['단축코드', '체결시간', '행사가', 'OLOH', '기준가', '월저', '월고', '전저', '전고', '종가', '피봇', '시가', '시가갭', '저가',
                           '현재가', '고가', '대비', '진폭', '거래량', '수정거래량', '미결', '미결증감']

                df_cm_put = DataFrame(data=put_result, columns=columns)

                columns = ['매도누적체결량', '매도누적체결건수', '매수누적체결량', '매수누적체결건수']
                df_cm_put_che = DataFrame(data=putche_result, columns=columns)

                columns = ['매수건수', '매도건수', '매수잔량', '매도잔량']
                df_cm_put_ho = DataFrame(data=putho_result, columns=columns)

                if pre_start:

                    미결 = format(df_cm_put['미결'].sum(), ',')

                    if 미결 != self.tableWidget_put.horizontalHeaderItem(Option_column.OI.value).text():
                        item = QTableWidgetItem(미결)
                        self.tableWidget_put.setHorizontalHeaderItem(Option_column.OI.value, item)
                    else:
                        pass
                else:
                    if comboindex == 1:

                        temp = format(df_cm_put['수정거래량'].sum(), ',')
                    else:
                        temp = format(df_cm_put['미결'].sum(), ',')                    

                    if temp != self.tableWidget_put.horizontalHeaderItem(Option_column.OI.value).text():
                        item = QTableWidgetItem(temp)
                        self.tableWidget_put.setHorizontalHeaderItem(Option_column.OI.value, item)
                    else:
                        pass

                cm_put_행사가 = df_cm_put['행사가'].values.tolist()
                
                print(df_cm_put)

                self.tableWidget_put.resizeColumnsToContents()
                self.tableWidget_put.setColumnWidth(0, 15)

                cm_call_종가 = df_cm_call['종가'].values.tolist()
                cm_call_종가_extend = self.make_color_list(cm_call_종가)

                cm_put_종가 = df_cm_put['종가'].values.tolist()
                cm_put_종가_extend = self.make_color_list(cm_put_종가)

                if not pre_start:

                    # 콜 컬러링 리스트 작성
                    cm_call_시가 = df_cm_call['시가'].values.tolist()
                    cm_call_시가_extend = self.make_color_list(cm_call_시가)

                    cm_call_피봇 = df_cm_call['피봇'].values.tolist()
                    cm_call_피봇_extend = self.make_color_list(cm_call_피봇)

                    cm_call_저가 = df_cm_call['저가'].values.tolist()
                    cm_call_저가_extend = self.make_color_list(cm_call_저가)

                    cm_call_고가 = df_cm_call['고가'].values.tolist()
                    cm_call_고가_extend = self.make_color_list(cm_call_고가)

                    # 풋 컬러링 리스트 작성
                    cm_put_시가 = df_cm_put['시가'].values.tolist()
                    cm_put_시가_extend = self.make_color_list(cm_put_시가)

                    cm_put_피봇 = df_cm_put['피봇'].values.tolist()
                    cm_put_피봇_extend = self.make_color_list(cm_put_피봇)

                    cm_put_저가 = df_cm_put['저가'].values.tolist()
                    cm_put_저가_extend = self.make_color_list(cm_put_저가)

                    cm_put_고가 = df_cm_put['고가'].values.tolist()
                    cm_put_고가_extend = self.make_color_list(cm_put_고가)
                else:
                    pass

                # 수정거래량 차 구하기
                '''
                temp = call_volume_total - put_volume_total

                item = QTableWidgetItem("{0}".format(temp))
                item.setTextAlignment(Qt.AlignCenter)

                if temp > 0:

                    item.setBackground(QBrush(적색))
                    item.setForeground(QBrush(흰색))
                elif temp < 0:

                    item.setBackground(QBrush(청색))
                    item.setForeground(QBrush(흰색))
                else:
                    item.setBackground(QBrush(기본바탕색))
                    item.setForeground(QBrush(검정색))

                self.tableWidget_fut.setItem(2, Futures_column.거래량.value, item)
                self.tableWidget_fut.resizeColumnsToContents()
                '''

                df_plotdata_cm_call_volume.iloc[0][0] = 0                
                df_plotdata_cm_put_volume.iloc[0][0] = 0
                df_plotdata_cm_volume_cha.iloc[0][0] = 0

                콜_미결합 = df_cm_call['미결'].sum()
                풋_미결합 = df_cm_put['미결'].sum()

                미결합 = 콜_미결합 + 풋_미결합

                if 미결합 > 0:
                    콜미결퍼센트 = (콜_미결합 / 미결합) * 100
                    풋미결퍼센트 = 100 - 콜미결퍼센트

                    #call_oi_percent_init_value = 콜미결퍼센트
                    #put_oi_percent_init_value = 풋미결퍼센트
                    call_oi_percent_init_value = 콜_미결합
                    put_oi_percent_init_value = 풋_미결합

                    df_plotdata_cm_call_oi[0][0] = 0
                    df_plotdata_cm_put_oi[0][0] = 0
                    df_plotdata_cm_oi_cha.iloc[0][0] = 0

                    str = '[{0:02d}:{1:02d}:{2:02d}] Call OI 시작값 : {3}, Put OI 시작값 : {4}\r'.format(dt.hour,
                                            dt.minute, dt.second, format(call_oi_percent_init_value, ','),
                                            format(put_oi_percent_init_value, ','))
                    self.textBrowser.append(str)

                    temp = 'OIIV({0}/{1}) ∑(CRΔ/RRΔ)'.format(format(call_oi_percent_init_value, ','), format(put_oi_percent_init_value, ','))

                    item = QTableWidgetItem(temp)
                    self.tableWidget_quote.setHorizontalHeaderItem(Quote_column.호가종합.value - 1, item)
                else:
                    pass

                if not overnight:

                    XQ = t2101(parent=self)
                    XQ.Query(종목코드=gmshcode)
                    print('t2101 요청')

                    time.sleep(0.1)

                    XQ = t2801(parent=self)
                    XQ.Query(종목코드=gmshcode)
                    print('t2801 요청')

                    if pre_start:

                        # FUTURES/KOSPI200 예상지수 요청
                        self.YJ = YJ_(parent=self)
                        self.YJ.AdviseRealData(FUTURES)
                        self.YJ.AdviseRealData(KOSPI200)

                        # 지수선물예상체결 요청
                        self.YFC = YFC(parent=self)
                        self.YFC.AdviseRealData(gmshcode)

                        # KOSPI예상체결 요청
                        self.YS3 = YS3(parent=self)
                        self.YS3.AdviseRealData(SAMSUNG)
                        self.YS3.AdviseRealData(MOBIS)
                        self.YS3.AdviseRealData(NAVER)

                        # 지수옵션예상체결 요청
                        self.YOC = YOC(parent=self)

                        for i in range(nCount_cm_option_pairs):
                            self.YOC.AdviseRealData(df['콜옵션코드'][i])
                            self.YOC.AdviseRealData(df1['풋옵션코드'][i])
                    else:
                        pass

                    # 옵션 실시간테이타 요청
                    self.cm_opt_real = OC0(parent=self)

                    for i in range(nCount_cm_option_pairs):
                        self.cm_opt_real.AdviseRealData(df['콜옵션코드'][i])
                        self.cm_opt_real.AdviseRealData(df1['풋옵션코드'][i])

                    # 전일등가 중심 9개 행사가 호가요청
                    self.cm_opt_ho = OH0(parent=self)

                    for i in range(15):
                        self.cm_opt_ho.AdviseRealData(cm_call_code[(old_atm_index - 7) + i])
                        self.cm_opt_ho.AdviseRealData(cm_put_code[(old_atm_index - 7) + i])

                    # 선물 실시간테이타 요청
                    self.fut_real = FC0(parent=self)
                    self.fut_ho = FH0(parent=self)

                    self.fut_real.AdviseRealData(gmshcode)
                    self.fut_ho.AdviseRealData(gmshcode)

                    # KOSPI/KOSPI200/KOSDAQ 지수요청
                    self.IJ.AdviseRealData(KOSPI)
                    self.IJ.AdviseRealData(KOSPI200)
                    self.IJ.AdviseRealData(KOSDAQ)

                    # KOSPI체결 요청
                    self.S3.AdviseRealData(SAMSUNG)
                    self.S3.AdviseRealData(MOBIS)
                    self.S3.AdviseRealData(NAVER)

                    # 업종별 투자자별 매매현황 요청
                    self.BM.AdviseRealData(FUTURES)
                    self.BM.AdviseRealData(KOSPI)

                    # 프로그램 매매현황 요청
                    self.PM.AdviseRealData()

                    # t8416 요청
                    if today_str != month_firstday_str:
                        self.t8416_callworker.start()
                        self.t8416_callworker.daemon = True
                    else:
                        call_positionCell = self.tableWidget_call.item(atm_index + 3, 1)
                        self.tableWidget_call.scrollToItem(call_positionCell)

                        put_positionCell = self.tableWidget_put.item(atm_index + 3, 1)
                        self.tableWidget_put.scrollToItem(put_positionCell)

                        self.call_open_check()
                        self.call_db_check()

                        self.put_open_check()
                        self.put_db_check()

                        self.call_node_color_clear()
                        self.put_node_color_clear()

                        self.callnode_color_check()
                        self.putnode_color_check()

                        self.plot_worker.start()
                        self.plot_worker.daemon = True
                        print('Plot 쓰레드가 시작됩니다...')
                        print('\r')

                        str = '[{0:02d}:{1:02d}:{2:02d}] Plot 쓰레드가 시작됩니다.\r'.format(dt.hour, dt.minute, dt.second)
                        self.textBrowser.append(str)
                else:

                    XQ = t2101(parent=self)
                    XQ.Query(종목코드=gmshcode)

                    time.sleep(0.1)

                    XQ = t2801(parent=self)
                    XQ.Query(종목코드=gmshcode)

                    # t8416 요청
                    if today_str != month_firstday_str:
                        self.t8416_callworker.start()
                        self.t8416_callworker.daemon = True
                    else:
                        # EUREX 야간옵션 시세전광판
                        XQ = t2835(parent=self)
                        XQ.Query(월물=month_str)
            else:

                if not overnight:

                    for i in range(nCount_cm_option_pairs):

                        if df_cm_call.iloc[i]['시가'] > 0:

                            df_cm_call.loc[i, '피봇'] = self.calc_pivot(df_cm_call.iloc[i]['전저'],
                                                                      df_cm_call.iloc[i]['전고'],
                                                                      df_cm_call.iloc[i]['종가'],
                                                                      df_cm_call.iloc[i]['시가'])

                            item = QTableWidgetItem("{0:0.2f}".format(df_cm_call.iloc[i]['피봇']))
                            item.setTextAlignment(Qt.AlignCenter)
                            self.tableWidget_call.setItem(i, Option_column.피봇.value, item)
                        else:
                            pass

                        저가 = df['저가'][i]
                        df_cm_call.loc[i, '저가'] = 저가

                        item = QTableWidgetItem("{0:0.2f}".format(저가))
                        item.setTextAlignment(Qt.AlignCenter)
                        self.tableWidget_call.setItem(i, Option_column.저가.value, item)

                        고가 = df['고가'][i]
                        df_cm_call.loc[i, '고가'] = 고가

                        item = QTableWidgetItem("{0:0.2f}".format(고가))
                        item.setTextAlignment(Qt.AlignCenter)
                        self.tableWidget_call.setItem(i, Option_column.고가.value, item)

                        진폭 = 고가 - 저가
                        item = QTableWidgetItem("{0:0.2f}".format(진폭))
                        item.setTextAlignment(Qt.AlignCenter)
                        self.tableWidget_call.setItem(i, Option_column.진폭.value, item)

                        if df_cm_put.iloc[i]['시가'] > 0:

                            df_cm_put.loc[i, '피봇'] = self.calc_pivot(df_cm_put.iloc[i]['전저'],
                                                                     df_cm_put.iloc[i]['전고'],
                                                                     df_cm_put.iloc[i]['종가'],
                                                                     df_cm_put.iloc[i]['시가'])

                            item = QTableWidgetItem("{0:0.2f}".format(df_cm_put.iloc[i]['피봇']))
                            item.setTextAlignment(Qt.AlignCenter)
                            self.tableWidget_put.setItem(i, Option_column.피봇.value, item)
                        else:
                            pass

                        저가 = df1['저가'][i]
                        df_cm_put.loc[i, '저가'] = 저가

                        item = QTableWidgetItem("{0:0.2f}".format(저가))
                        item.setTextAlignment(Qt.AlignCenter)
                        self.tableWidget_put.setItem(i, Option_column.저가.value, item)

                        고가 = df1['고가'][i]
                        df_cm_put.loc[i, '고가'] = 고가

                        item = QTableWidgetItem("{0:0.2f}".format(고가))
                        item.setTextAlignment(Qt.AlignCenter)
                        self.tableWidget_put.setItem(i, Option_column.고가.value, item)

                        진폭 = 고가 - 저가
                        item = QTableWidgetItem("{0:0.2f}".format(진폭))
                        item.setTextAlignment(Qt.AlignCenter)
                        self.tableWidget_put.setItem(i, Option_column.진폭.value, item)

                    cm_call_피봇 = df_cm_call['피봇'].values.tolist()
                    cm_call_피봇_extend = self.make_color_list(cm_call_피봇)

                    cm_call_저가 = df_cm_call['저가'].values.tolist()
                    cm_call_저가_extend = self.make_color_list(cm_call_저가)

                    cm_call_고가 = df_cm_call['고가'].values.tolist()
                    cm_call_고가_extend = self.make_color_list(cm_call_고가)

                    cm_put_피봇 = df_cm_put['피봇'].values.tolist()
                    cm_put_피봇_extend = self.make_color_list(cm_put_피봇)

                    cm_put_저가 = df_cm_put['저가'].values.tolist()
                    cm_put_저가_extend = self.make_color_list(cm_put_저가)

                    cm_put_고가 = df_cm_put['고가'].values.tolist()
                    cm_put_고가_extend = self.make_color_list(cm_put_고가)

                    self.call_open_check()
                    self.call_db_check()

                    self.put_open_check()
                    self.put_db_check()

                    self.call_node_color_clear()
                    self.put_node_color_clear()

                    self.callnode_color_check()
                    self.putnode_color_check()

                    str = '[{0:02d}:{1:02d}:{2:02d}] 주간옵션 전광판을 갱신합니다.\r'.format(dt.hour, dt.minute, dt.second)
                    self.textBrowser.append(str)
                else:
                    # EUREX 야간옵션 시세전광판
                    XQ = t2835(parent=self)
                    XQ.Query(월물=month_str)

        elif szTrCode == 't2801':

            df = result[0]

            fut_realdata['KP200'] = df['KOSPI200지수']
            kp200_realdata['종가'] = df['KOSPI200지수']

            # 주간 데이타를 가져옴
            if overnight:

                df_plotdata_kp200.iloc[0][0] = kp200_realdata['종가']
                df_plotdata_fut.iloc[0][0] = fut_realdata['현재가']

                if df['시가'] > 0:
                    df_plotdata_fut.iloc[0][1] = df['시가']
                else:
                    pass
            else:
                pass

            item = QTableWidgetItem("{0:0.2f}".format(df['KOSPI200지수']))
            item.setTextAlignment(Qt.AlignCenter)
            item.setBackground(QBrush(옅은회색))
            self.tableWidget_fut.setItem(2, Futures_column.현재가.value, item)

            if overnight:

                fut_realdata['전저'] = fut_realdata['저가']
                item = QTableWidgetItem("{0:0.2f}".format(fut_realdata['전저']))
                item.setTextAlignment(Qt.AlignCenter)
                self.tableWidget_fut.setItem(0, Futures_column.전저.value, item)

                fut_realdata['전고'] = fut_realdata['고가']
                item = QTableWidgetItem("{0:0.2f}".format(fut_realdata['전고']))
                item.setTextAlignment(Qt.AlignCenter)
                self.tableWidget_fut.setItem(0, Futures_column.전고.value, item)

                fut_realdata['종가'] = fut_realdata['현재가']
                item = QTableWidgetItem("{0:0.2f}".format(fut_realdata['종가']))
                item.setTextAlignment(Qt.AlignCenter)
                self.tableWidget_fut.setItem(0, Futures_column.종가.value, item)
            else:
                atm_str = self.find_ATM(fut_realdata['KP200'])

                if atm_str in cm_call_actval:

                    atm_index = cm_call_actval.index(atm_str)
                    self.tableWidget_call.item(atm_index, Option_column.행사가.value).setBackground(QBrush(노란색))
                    self.tableWidget_call.item(atm_index, Option_column.행사가.value).setForeground(QBrush(검정색))
                    self.tableWidget_put.item(atm_index, Option_column.행사가.value).setBackground(QBrush(노란색))
                    self.tableWidget_put.item(atm_index, Option_column.행사가.value).setForeground(QBrush(검정색))

                    call_atm_value = df_cm_call.iloc[atm_index]['현재가']
                    put_atm_value = df_cm_put.iloc[atm_index]['현재가']

                    str = '[{0:0.2f}] [{1:0.2f}/{2:0.2f}] [{3:0.1f}:{4:0.1f}]'.format(
                        fut_realdata['현재가'] - fut_realdata['KP200'],
                        call_atm_value + put_atm_value,
                        abs(call_atm_value - put_atm_value),
                        콜미결퍼센트, 풋미결퍼센트)
                    self.label_atm.setText(str)
                else:
                    print("atm_str이 리스트에 없습니다.", atm_str)

            fut_realdata['시가'] = df['시가']

            item = QTableWidgetItem("{0:0.2f}".format(fut_realdata['시가']))
            item.setTextAlignment(Qt.AlignCenter)

            item.setBackground(QBrush(기본바탕색))

            if overnight:

                if fut_realdata['시가'] > fut_realdata['종가']:
                    item.setForeground(QBrush(적색))
                elif fut_realdata['시가'] < fut_realdata['종가']:
                    item.setForeground(QBrush(청색))
                else:
                    item.setForeground(QBrush(검정색))
            else:
                pass

            self.tableWidget_fut.setItem(0, Futures_column.시가.value, item)

            if fut_realdata['시가'] > 0 and fut_realdata['종가'] > 0:

                fut_realdata['시가갭'] = fut_realdata['시가'] - fut_realdata['종가']
                item = QTableWidgetItem("{0:0.2f}".format(fut_realdata['시가갭']))
                item.setTextAlignment(Qt.AlignCenter)
                self.tableWidget_fut.setItem(0, Futures_column.시가갭.value, item)

                if overnight:

                    fut_realdata['피봇'] = self.calc_pivot(fut_realdata['전저'], fut_realdata['전고'], fut_realdata['종가'],
                                                         fut_realdata['시가'])

                    item = QTableWidgetItem("{0:0.2f}".format(fut_realdata['피봇']))
                    item.setTextAlignment(Qt.AlignCenter)
                    self.tableWidget_fut.setItem(0, Futures_column.피봇.value, item)
                else:
                    pass
            else:
                pass

            fut_realdata['저가'] = df['저가']
            item = QTableWidgetItem("{0:0.2f}".format(df['저가']))
            item.setTextAlignment(Qt.AlignCenter)
            self.tableWidget_fut.setItem(0, Futures_column.저가.value, item)

            fut_realdata['현재가'] = df['현재가']

            item = QTableWidgetItem("{0:0.2f}".format(df['현재가']))
            item.setTextAlignment(Qt.AlignCenter)
            item.setBackground(QBrush(옅은회색))
            self.tableWidget_fut.setItem(0, Futures_column.현재가.value, item)

            fut_realdata['고가'] = df['고가']
            item = QTableWidgetItem("{0:0.2f}".format(df['고가']))
            item.setTextAlignment(Qt.AlignCenter)
            self.tableWidget_fut.setItem(0, Futures_column.고가.value, item)

            if df['시가'] > 0:

                fut_realdata['대비'] = int((round((df['현재가'] - df['시가']), 2)) * 100)

                item = QTableWidgetItem("{0:0.0f}".format(fut_realdata['대비']))
                item.setTextAlignment(Qt.AlignCenter)
                self.tableWidget_fut.setItem(0, Futures_column.대비.value, item)
            else:
                pass

            fut_realdata['진폭'] = df['고가'] - df['저가']
            item = QTableWidgetItem("{0:0.2f}".format(fut_realdata['진폭']))
            item.setTextAlignment(Qt.AlignCenter)
            self.tableWidget_fut.setItem(0, Futures_column.진폭.value, item)

            fut_realdata['거래량'] = df['거래량']
            item = QTableWidgetItem("{0}".format(fut_realdata['거래량']))
            item.setTextAlignment(Qt.AlignCenter)
            self.tableWidget_fut.setItem(0, Futures_column.거래량.value, item)

            fut_realdata['미결'] = df['미결제량']
            item = QTableWidgetItem("{0}".format(fut_realdata['미결']))
            item.setTextAlignment(Qt.AlignCenter)
            self.tableWidget_fut.setItem(0, Futures_column.OI.value, item)

            fut_realdata['미결증감'] = df['미결제증감']
            item = QTableWidgetItem("{0}".format(fut_realdata['미결증감']))
            item.setTextAlignment(Qt.AlignCenter)

            if fut_realdata['미결증감'] < 0:
                item.setBackground(QBrush(녹색))
            else:
                item.setBackground(QBrush(기본바탕색))

            self.tableWidget_fut.setItem(0, Futures_column.OID.value, item)

            self.tableWidget_fut.resizeColumnsToContents()

            fut_realdata['선물코드'] = 'CME'

            columns = ['선물코드', 'KP200', '전저', '전고', '종가', '피봇', '시가', '시가갭', '저가',
                       '현재가', '고가', '대비', '진폭', '거래량', '미결', '미결증감']

            df_cme = DataFrame(data=[fut_realdata], columns=columns)

        elif szTrCode == 't2830':

            pass

        elif szTrCode == 't2835':

            block, df, df1 = result

            if not refresh_flag:

                call_open = [False] * nRowCount
                call_ol = [False] * nRowCount
                call_oh = [False] * nRowCount

                put_open = [False] * nRowCount
                put_ol = [False] * nRowCount
                put_oh = [False] * nRowCount

                # gap percent 초기화
                call_gap_percent = [NaN] * nRowCount
                put_gap_percent = [NaN] * nRowCount

                # db percent 초기화
                call_db_percent = [NaN] * nRowCount
                put_db_percent = [NaN] * nRowCount

                item = QTableWidgetItem('시가갭')
                self.tableWidget_call.setHorizontalHeaderItem(Option_column.시가갭.value, item)

                item = QTableWidgetItem('대비')
                self.tableWidget_call.setHorizontalHeaderItem(Option_column.대비.value, item)

                item = QTableWidgetItem('시가갭')
                self.tableWidget_put.setHorizontalHeaderItem(Option_column.시가갭.value, item)

                item = QTableWidgetItem('대비')
                self.tableWidget_put.setHorizontalHeaderItem(Option_column.대비.value, item)

                for i in range(nCount_cm_option_pairs):

                    # 수정거래량 초기화
                    df_cm_call.loc[i, '수정거래량'] = 0
                    df_cm_put.loc[i, '수정거래량'] = 0

                    # Call 처리
                    item = QTableWidgetItem("{0}".format(''))
                    item.setBackground(QBrush(기본바탕색))
                    item.setForeground(QBrush(검정색))
                    self.tableWidget_call.setItem(i, Option_column.OLOH.value, item)

                    전저 = df_cm_call.iloc[i]['저가']
                    df_cm_call.loc[i, '전저'] = 전저
                    item = QTableWidgetItem("{0:0.2f}".format(전저))
                    item.setTextAlignment(Qt.AlignCenter)
                    self.tableWidget_call.setItem(i, Option_column.전저.value, item)

                    전고 = df_cm_call.iloc[i]['고가']
                    df_cm_call.loc[i, '전고'] = 전고
                    item = QTableWidgetItem("{0:0.2f}".format(전고))
                    item.setTextAlignment(Qt.AlignCenter)
                    self.tableWidget_call.setItem(i, Option_column.전고.value, item)

                    if 18 <= dt.hour < 24 or 0 <= dt.hour < 4:
                        
                        시가 = df['시가'][i]
                    else:
                        시가 = 0.0

                    df_cm_call.loc[i, '시가'] = 시가

                    item = QTableWidgetItem("{0:0.2f}".format(시가))
                    item.setTextAlignment(Qt.AlignCenter)
                    self.tableWidget_call.setItem(i, Option_column.시가.value, item)

                    종가 = df_cm_call.iloc[i]['현재가']
                    df_cm_call.loc[i, '종가'] = 종가
                    item = QTableWidgetItem("{0:0.2f}".format(종가))
                    item.setTextAlignment(Qt.AlignCenter)
                    self.tableWidget_call.setItem(i, Option_column.종가.value, item)

                    df_plotdata_cm_call.iloc[i][0] = 종가

                    현재가 = df['현재가'][i]
                    df_cm_call.loc[i, '현재가'] = 현재가

                    item = QTableWidgetItem("{0:0.2f}".format(현재가))
                    item.setTextAlignment(Qt.AlignCenter)

                    if 시가 > 0:

                        if 시가 < 현재가:
                            item.setForeground(QBrush(적색))
                        elif 시가 > 현재가:
                            item.setForeground(QBrush(청색))
                        else:
                            item.setForeground(QBrush(검정색))
                    else:
                        item.setForeground(QBrush(검정색))

                    item.setBackground(QBrush(옅은회색))
                    self.tableWidget_call.setItem(i, Option_column.현재가.value, item)

                    저가 = df['저가'][i]
                    df_cm_call.loc[i, '저가'] = df['저가'][i]

                    item = QTableWidgetItem("{0:0.2f}".format(저가))
                    item.setTextAlignment(Qt.AlignCenter)
                    self.tableWidget_call.setItem(i, Option_column.저가.value, item)

                    고가 = df['고가'][i]
                    df_cm_call.loc[i, '고가'] = df['고가'][i]

                    item = QTableWidgetItem("{0:0.2f}".format(고가))
                    item.setTextAlignment(Qt.AlignCenter)
                    self.tableWidget_call.setItem(i, Option_column.고가.value, item)

                    진폭 = 고가 - 저가
                    item = QTableWidgetItem("{0:0.2f}".format(진폭))
                    item.setTextAlignment(Qt.AlignCenter)
                    self.tableWidget_call.setItem(i, Option_column.진폭.value, item)

                    if 시가 > 0:

                        item = QTableWidgetItem("{0:0.2f}".format(시가))
                        item.setTextAlignment(Qt.AlignCenter)

                        if 시가 > 종가:
                            item.setForeground(QBrush(적색))
                        elif 시가 < 종가:
                            item.setForeground(QBrush(청색))
                        else:
                            item.setForeground(QBrush(검정색))

                        self.tableWidget_call.setItem(i, Option_column.시가.value, item)

                        df_plotdata_cm_call.iloc[i][1] = 시가

                        시가갭 = 시가 - 종가
                        대비 = int(round((현재가 - 시가) * 100, 2))

                        if 시가 > 0.3 and 저가 < 고가:

                            call_gap_percent[i] = (시가 / 종가 - 1) * 100

                            gap_str = "{0:0.2f}({1:0.0f}%)".format(시가갭, call_gap_percent[i])

                            item = QTableWidgetItem(gap_str)
                            item.setTextAlignment(Qt.AlignCenter)
                            self.tableWidget_call.setItem(i, Option_column.시가갭.value, item)

                            call_db_percent[i] = (현재가 / 시가 - 1) * 100

                            gap_str = "{0:0.0f}({1:0.0f}%)".format(대비, call_db_percent[i])

                            item = QTableWidgetItem(gap_str)
                            item.setTextAlignment(Qt.AlignCenter)
                            self.tableWidget_call.setItem(i, Option_column.대비.value, item)
                        else:
                            gap_str = "{0:0.2f}".format(시가갭)

                            item = QTableWidgetItem(gap_str)
                            item.setTextAlignment(Qt.AlignCenter)
                            self.tableWidget_call.setItem(i, Option_column.시가갭.value, item)

                            gap_str = "{0:0.0f}".format(대비)

                            item = QTableWidgetItem(gap_str)
                            item.setTextAlignment(Qt.AlignCenter)
                            self.tableWidget_call.setItem(i, Option_column.대비.value, item)

                        if 전저 > 0 and 전고 > 0 and 종가 > 0 and 시가 > 0:

                            피봇 = self.calc_pivot(전저, 전고, 종가, 시가)
                            df_cm_call.loc[i, '피봇'] = 피봇

                            item = QTableWidgetItem("{0:0.2f}".format(df_cm_call.iloc[i]['피봇']))
                            item.setTextAlignment(Qt.AlignCenter)
                            self.tableWidget_call.setItem(i, Option_column.피봇.value, item)
                        else:
                            pass
                    else:
                        시가 = 0.0
                        피봇 = 0.0
                        시가갭 = 0.0
                        대비 = 0

                        item = QTableWidgetItem("{0:0.2f}".format(시가))
                        item.setTextAlignment(Qt.AlignCenter)
                        self.tableWidget_call.setItem(i, Option_column.시가.value, item)

                        item = QTableWidgetItem("{0:0.2f}".format(피봇))
                        item.setTextAlignment(Qt.AlignCenter)
                        self.tableWidget_call.setItem(i, Option_column.피봇.value, item)

                        item = QTableWidgetItem("{0:0.2f}".format(시가갭))
                        item.setTextAlignment(Qt.AlignCenter)
                        self.tableWidget_call.setItem(i, Option_column.시가갭.value, item)

                        item = QTableWidgetItem("{0}".format(대비))
                        item.setTextAlignment(Qt.AlignCenter)
                        self.tableWidget_call.setItem(i, Option_column.대비.value, item)

                        self.tableWidget_call.item(i, Option_column.행사가.value).setBackground(QBrush(기본바탕색))
                        self.tableWidget_call.item(i, Option_column.행사가.value).setForeground(QBrush(검정색))

                    if 시가 > 0 and 저가 < 고가:
                        self.tableWidget_call.item(i, Option_column.행사가.value).setBackground(QBrush(녹색))
                        self.tableWidget_call.item(i, Option_column.행사가.value).setForeground(QBrush(검정색))
                    else:
                        pass

                    수정거래량 = int(df['거래량'][i] * (df['현재가'][i] - 시가갭))
                    df_cm_call.loc[i, '수정거래량'] = 수정거래량
                    # t2835에 미결항목이 없음
                    df_cm_call.loc[i, '미결'] = 0

                    temp = format(수정거래량, ',')

                    item = QTableWidgetItem(temp)
                    item.setTextAlignment(Qt.AlignCenter)
                    self.tableWidget_call.setItem(i, Option_column.OI.value, item)

                    df_cm_call.loc[i, '미결증감'] = 0
                    temp = format(0, ',')

                    item = QTableWidgetItem(temp)
                    item.setTextAlignment(Qt.AlignCenter)
                    self.tableWidget_call.setItem(i, Option_column.OID.value, item)

                    df_plotdata_cm_call_volume.iloc[0][0] = 0

                    # Put 처리
                    item = QTableWidgetItem("{0}".format(''))
                    item.setBackground(QBrush(기본바탕색))
                    item.setForeground(QBrush(검정색))
                    self.tableWidget_put.setItem(i, Option_column.OLOH.value, item)

                    전저 = df_cm_put.iloc[i]['저가']
                    df_cm_put.loc[i, '전저'] = 전저
                    item = QTableWidgetItem("{0:0.2f}".format(전저))
                    item.setTextAlignment(Qt.AlignCenter)
                    self.tableWidget_put.setItem(i, Option_column.전저.value, item)

                    전고 = df_cm_put.iloc[i]['고가']
                    df_cm_put.loc[i, '전고'] = 전고
                    item = QTableWidgetItem("{0:0.2f}".format(전고))
                    item.setTextAlignment(Qt.AlignCenter)
                    self.tableWidget_put.setItem(i, Option_column.전고.value, item)

                    if 18 <= dt.hour < 24 or 0 <= dt.hour < 4:
                        
                        시가 = df1['시가'][i]
                    else:
                        시가 = 0.0

                    df_cm_put.loc[i, '시가'] = 시가

                    item = QTableWidgetItem("{0:0.2f}".format(시가))
                    item.setTextAlignment(Qt.AlignCenter)
                    self.tableWidget_put.setItem(i, Option_column.시가.value, item)

                    종가 = df_cm_put.iloc[i]['현재가']
                    df_cm_put.loc[i, '종가'] = 종가
                    item = QTableWidgetItem("{0:0.2f}".format(종가))
                    item.setTextAlignment(Qt.AlignCenter)
                    self.tableWidget_put.setItem(i, Option_column.종가.value, item)

                    df_plotdata_cm_put.iloc[i][0] = 종가

                    현재가 = df1['현재가'][i]
                    df_cm_put.loc[i, '현재가'] = 현재가

                    item = QTableWidgetItem("{0:0.2f}".format(현재가))
                    item.setTextAlignment(Qt.AlignCenter)

                    if 시가 > 0:

                        if 시가 < 현재가:
                            item.setForeground(QBrush(적색))
                        elif 시가 > 현재가:
                            item.setForeground(QBrush(청색))
                        else:
                            item.setForeground(QBrush(검정색))
                    else:
                        item.setForeground(QBrush(검정색))

                    item.setBackground(QBrush(옅은회색))
                    self.tableWidget_put.setItem(i, Option_column.현재가.value, item)

                    저가 = df1['저가'][i]
                    df_cm_put.loc[i, '저가'] = df1['저가'][i]

                    item = QTableWidgetItem("{0:0.2f}".format(저가))
                    item.setTextAlignment(Qt.AlignCenter)
                    self.tableWidget_put.setItem(i, Option_column.저가.value, item)

                    고가 = df1['고가'][i]
                    df_cm_put.loc[i, '고가'] = df1['고가'][i]

                    item = QTableWidgetItem("{0:0.2f}".format(고가))
                    item.setTextAlignment(Qt.AlignCenter)
                    self.tableWidget_put.setItem(i, Option_column.고가.value, item)

                    진폭 = 고가 - 저가
                    item = QTableWidgetItem("{0:0.2f}".format(진폭))
                    item.setTextAlignment(Qt.AlignCenter)
                    self.tableWidget_put.setItem(i, Option_column.진폭.value, item)

                    if 시가 > 0:

                        item = QTableWidgetItem("{0:0.2f}".format(시가))
                        item.setTextAlignment(Qt.AlignCenter)

                        if 시가 > 종가:
                            item.setForeground(QBrush(적색))
                        elif 시가 < 종가:
                            item.setForeground(QBrush(청색))
                        else:
                            item.setForeground(QBrush(검정색))

                        self.tableWidget_put.setItem(i, Option_column.시가.value, item)

                        df_plotdata_cm_put.iloc[i][1] = 시가

                        시가갭 = 시가 - 종가
                        대비 = int(round((현재가 - 시가) * 100, 2))

                        if 시가 > 0.3 and 저가 < 고가:

                            put_gap_percent[i] = (시가 / 종가 - 1) * 100

                            gap_str = "{0:0.2f}({1:0.0f}%)".format(시가갭, put_gap_percent[i])

                            item = QTableWidgetItem(gap_str)
                            item.setTextAlignment(Qt.AlignCenter)
                            self.tableWidget_put.setItem(i, Option_column.시가갭.value, item)

                            put_db_percent[i] = (현재가 / 시가 - 1) * 100

                            gap_str = "{0:0.0f}({1:0.0f}%)".format(대비, put_db_percent[i])

                            item = QTableWidgetItem(gap_str)
                            item.setTextAlignment(Qt.AlignCenter)
                            self.tableWidget_put.setItem(i, Option_column.대비.value, item)
                        else:
                            gap_str = "{0:0.2f}".format(시가갭)

                            item = QTableWidgetItem(gap_str)
                            item.setTextAlignment(Qt.AlignCenter)
                            self.tableWidget_put.setItem(i, Option_column.시가갭.value, item)

                            gap_str = "{0:0.0f}".format(대비)

                            item = QTableWidgetItem(gap_str)
                            item.setTextAlignment(Qt.AlignCenter)
                            self.tableWidget_put.setItem(i, Option_column.대비.value, item)

                        if 전저 > 0 and 전고 > 0 and 종가 > 0 and 시가 > 0:

                            피봇 = self.calc_pivot(전저, 전고, 종가, 시가)
                            df_cm_put.loc[i, '피봇'] = 피봇

                            item = QTableWidgetItem("{0:0.2f}".format(df_cm_put.iloc[i]['피봇']))
                            item.setTextAlignment(Qt.AlignCenter)
                            self.tableWidget_put.setItem(i, Option_column.피봇.value, item)
                        else:
                            pass
                    else:
                        시가 = 0.0
                        피봇 = 0.0
                        시가갭 = 0.0
                        대비 = 0

                        item = QTableWidgetItem("{0:0.2f}".format(시가))
                        item.setTextAlignment(Qt.AlignCenter)
                        self.tableWidget_put.setItem(i, Option_column.시가.value, item)

                        item = QTableWidgetItem("{0:0.2f}".format(피봇))
                        item.setTextAlignment(Qt.AlignCenter)
                        self.tableWidget_put.setItem(i, Option_column.피봇.value, item)

                        item = QTableWidgetItem("{0:0.2f}".format(시가갭))
                        item.setTextAlignment(Qt.AlignCenter)
                        self.tableWidget_put.setItem(i, Option_column.시가갭.value, item)

                        item = QTableWidgetItem("{0}".format(대비))
                        item.setTextAlignment(Qt.AlignCenter)
                        self.tableWidget_put.setItem(i, Option_column.대비.value, item)

                        self.tableWidget_put.item(i, Option_column.행사가.value).setBackground(QBrush(기본바탕색))
                        self.tableWidget_put.item(i, Option_column.행사가.value).setForeground(QBrush(검정색))

                    if 시가 > 0 and 저가 < 고가:
                        self.tableWidget_put.item(i, Option_column.행사가.value).setBackground(QBrush(녹색))
                        self.tableWidget_put.item(i, Option_column.행사가.value).setForeground(QBrush(검정색))
                    else:
                        pass

                    수정거래량 = int(df1['거래량'][i] * (df1['현재가'][i] - 시가갭))
                    df_cm_put.loc[i, '수정거래량'] = 수정거래량
                    # t2835에 미결항목이 없음
                    df_cm_put.loc[i, '미결'] = 0

                    temp = format(수정거래량, ',')

                    item = QTableWidgetItem(temp)
                    item.setTextAlignment(Qt.AlignCenter)
                    self.tableWidget_put.setItem(i, Option_column.OI.value, item)

                    df_cm_put.loc[i, '미결증감'] = 0
                    temp = format(0, ',')

                    item = QTableWidgetItem(temp)
                    item.setTextAlignment(Qt.AlignCenter)
                    self.tableWidget_put.setItem(i, Option_column.OID.value, item)

                    df_plotdata_cm_put_volume.iloc[0][0] = 0
                    df_plotdata_cm_volume_cha.iloc[0][0] = 0
                
                print('\r')
                print('t2835 call', df_cm_call)
                print('\r')
                print('t2835 put', df_cm_put)

                cm_call_전저 = df_cm_call['전저'].values.tolist()
                cm_call_전저_extend = self.make_color_list(cm_call_전저)

                cm_call_전고 = df_cm_call['전고'].values.tolist()
                cm_call_전고_extend = self.make_color_list(cm_call_전고)

                cm_call_종가 = df_cm_call['종가'].values.tolist()
                cm_call_종가_extend = self.make_color_list(cm_call_종가)
                
                cm_call_피봇 = df_cm_call['피봇'].values.tolist()
                cm_call_피봇_extend = self.make_color_list(cm_call_피봇)

                cm_call_시가 = df_cm_call['시가'].values.tolist()
                cm_call_시가_extend = self.make_color_list(cm_call_시가)

                cm_call_저가 = df_cm_call['저가'].values.tolist()
                cm_call_저가_extend = self.make_color_list(cm_call_저가)

                cm_call_고가 = df_cm_call['고가'].values.tolist()
                cm_call_고가_extend = self.make_color_list(cm_call_고가)

                cm_put_전저 = df_cm_put['전저'].values.tolist()
                cm_put_전저_extend = self.make_color_list(cm_put_전저)

                cm_put_전고 = df_cm_put['전고'].values.tolist()
                cm_put_전고_extend = self.make_color_list(cm_put_전고)

                cm_put_종가 = df_cm_put['종가'].values.tolist()
                cm_put_종가_extend = self.make_color_list(cm_put_종가)
                
                cm_put_피봇 = df_cm_put['피봇'].values.tolist()
                cm_put_피봇_extend = self.make_color_list(cm_put_피봇)

                cm_put_시가 = df_cm_put['시가'].values.tolist()
                cm_put_시가_extend = self.make_color_list(cm_put_시가)

                cm_put_저가 = df_cm_put['저가'].values.tolist()
                cm_put_저가_extend = self.make_color_list(cm_put_저가)

                cm_put_고가 = df_cm_put['고가'].values.tolist()
                cm_put_고가_extend = self.make_color_list(cm_put_고가)
                '''
                # 실시간테이타 요청
                self.cm_opt_real = EC0(parent=self)
                self.cm_opt_ho = EH0(parent=self)
                self.fut_real = NC0(parent=self)
                self.fut_ho = NH0(parent=self)

                self.fut_real.AdviseRealData(gmshcode)
                self.fut_ho.AdviseRealData(gmshcode)

                # 업종별 투자자별 매매현황 요청
                self.BM.AdviseRealData(CME)

                for i in range(15):
                    self.cm_opt_ho.AdviseRealData(cm_call_code[(old_atm_index - 7) + i])
                    self.cm_opt_ho.AdviseRealData(cm_put_code[(old_atm_index - 7) + i])

                for i in range(nCount_cm_option_pairs):
                    self.cm_opt_real.AdviseRealData(df['콜옵션코드'][i])
                    self.cm_opt_real.AdviseRealData(df1['풋옵션코드'][i])
                '''
            else:

                for i in range(nCount_cm_option_pairs):

                    시가 = df['시가'][i]
                    df_cm_call.loc[i, '시가'] = df['시가'][i]

                    item = QTableWidgetItem("{0:0.2f}".format(시가))
                    item.setTextAlignment(Qt.AlignCenter)
                    self.tableWidget_call.setItem(i, Option_column.시가.value, item)

                    if 시가 > 0:

                        피봇 = self.calc_pivot(df_cm_call.iloc[i]['전저'], df_cm_call.iloc[i]['전고'], df_cm_call.iloc[i]['종가'], 시가)
                        df_cm_call.loc[i, '피봇'] = 피봇

                        item = QTableWidgetItem("{0:0.2f}".format(df_cm_call.iloc[i]['피봇']))
                        item.setTextAlignment(Qt.AlignCenter)
                        self.tableWidget_call.setItem(i, Option_column.피봇.value, item)
                    else:
                        pass                    

                    저가 = df['저가'][i]
                    df_cm_call.loc[i, '저가'] = df['저가'][i]

                    item = QTableWidgetItem("{0:0.2f}".format(저가))
                    item.setTextAlignment(Qt.AlignCenter)
                    self.tableWidget_call.setItem(i, Option_column.저가.value, item)

                    고가 = df['고가'][i]
                    df_cm_call.loc[i, '고가'] = df['고가'][i]

                    item = QTableWidgetItem("{0:0.2f}".format(고가))
                    item.setTextAlignment(Qt.AlignCenter)
                    self.tableWidget_call.setItem(i, Option_column.고가.value, item)

                    진폭 = 고가 - 저가
                    item = QTableWidgetItem("{0:0.2f}".format(진폭))
                    item.setTextAlignment(Qt.AlignCenter)
                    self.tableWidget_call.setItem(i, Option_column.진폭.value, item)

                    시가 = df1['시가'][i]
                    df_cm_put.loc[i, '시가'] = df1['시가'][i]

                    item = QTableWidgetItem("{0:0.2f}".format(시가))
                    item.setTextAlignment(Qt.AlignCenter)
                    self.tableWidget_put.setItem(i, Option_column.시가.value, item)

                    if 시가 > 0:

                        피봇 = self.calc_pivot(df_cm_put.iloc[i]['전저'], df_cm_put.iloc[i]['전고'], df_cm_put.iloc[i]['종가'], 시가)
                        df_cm_put.loc[i, '피봇'] = 피봇

                        item = QTableWidgetItem("{0:0.2f}".format(df_cm_put.iloc[i]['피봇']))
                        item.setTextAlignment(Qt.AlignCenter)
                        self.tableWidget_put.setItem(i, Option_column.피봇.value, item)
                    else:
                        pass                    

                    저가 = df1['저가'][i]
                    df_cm_put.loc[i, '저가'] = df1['저가'][i]

                    item = QTableWidgetItem("{0:0.2f}".format(저가))
                    item.setTextAlignment(Qt.AlignCenter)
                    self.tableWidget_put.setItem(i, Option_column.저가.value, item)

                    고가 = df1['고가'][i]
                    df_cm_put.loc[i, '고가'] = df1['고가'][i]

                    item = QTableWidgetItem("{0:0.2f}".format(고가))
                    item.setTextAlignment(Qt.AlignCenter)
                    self.tableWidget_put.setItem(i, Option_column.고가.value, item)

                    진폭 = 고가 - 저가
                    item = QTableWidgetItem("{0:0.2f}".format(진폭))
                    item.setTextAlignment(Qt.AlignCenter)
                    self.tableWidget_put.setItem(i, Option_column.진폭.value, item)

                cm_call_시가 = df_cm_call['시가'].values.tolist()
                cm_call_시가_extend = self.make_color_list(cm_call_시가)

                cm_call_피봇 = df_cm_call['피봇'].values.tolist()
                cm_call_피봇_extend = self.make_color_list(cm_call_피봇)

                cm_call_저가 = df_cm_call['저가'].values.tolist()
                cm_call_저가_extend = self.make_color_list(cm_call_저가)

                cm_call_고가 = df_cm_call['고가'].values.tolist()
                cm_call_고가_extend = self.make_color_list(cm_call_고가)

                cm_put_시가 = df_cm_put['시가'].values.tolist()
                cm_put_시가_extend = self.make_color_list(cm_put_시가)

                cm_put_피봇 = df_cm_put['피봇'].values.tolist()
                cm_put_피봇_extend = self.make_color_list(cm_put_피봇)

                cm_put_저가 = df_cm_put['저가'].values.tolist()
                cm_put_저가_extend = self.make_color_list(cm_put_저가)

                cm_put_고가 = df_cm_put['고가'].values.tolist()
                cm_put_고가_extend = self.make_color_list(cm_put_고가)

                str = '[{0:02d}:{1:02d}:{2:02d}] 야간옵션 전광판을 갱신합니다.\r'.format(dt.hour, dt.minute, dt.second)
                self.textBrowser.append(str)

            atm_str = self.find_ATM(fut_realdata['KP200'])

            if atm_str in cm_call_actval:

                atm_index = cm_call_actval.index(atm_str)

                self.tableWidget_call.item(atm_index, Option_column.행사가.value).setBackground(QBrush(노란색))
                self.tableWidget_call.item(atm_index, Option_column.행사가.value).setForeground(QBrush(검정색))

                call_atm_value = df_cm_call.iloc[atm_index]['현재가']
                put_atm_value = df_cm_put.iloc[atm_index]['현재가']

                str = '[{0:0.2f}] [{1:0.2f}/{2:0.2f}] [{3:0.1f}:{4:0.1f}]'.format(
                    fut_realdata['현재가'] - fut_realdata['KP200'],
                    call_atm_value + put_atm_value,
                    abs(call_atm_value - put_atm_value),
                    콜미결퍼센트, 풋미결퍼센트)
                self.label_atm.setText(str)

                call_ckbox[atm_index - 1].setCheckState(Qt.Checked)
                call_ckbox[atm_index].setCheckState(Qt.Checked)
                call_ckbox[atm_index + 1].setCheckState(Qt.Checked)

                selected_call = [atm_index - 1, atm_index, atm_index + 1]

                call_positionCell = self.tableWidget_call.item(atm_index + 3, 1)
                self.tableWidget_call.scrollToItem(call_positionCell)

                self.tableWidget_put.item(atm_index, Option_column.행사가.value).setBackground(QBrush(노란색))
                self.tableWidget_put.item(atm_index, Option_column.행사가.value).setForeground(QBrush(검정색))

                put_ckbox[atm_index - 1].setCheckState(Qt.Checked)
                put_ckbox[atm_index].setCheckState(Qt.Checked)
                put_ckbox[atm_index + 1].setCheckState(Qt.Checked)

                selected_put = [atm_index - 1, atm_index, atm_index + 1]

                put_positionCell = self.tableWidget_put.item(atm_index + 3, 1)
                self.tableWidget_put.scrollToItem(put_positionCell)
            else:
                print("atm_str이 리스트에 없습니다.", atm_str)

            self.tableWidget_call.resizeColumnsToContents()
            self.tableWidget_call.setColumnWidth(0, 15)

            self.tableWidget_put.resizeColumnsToContents()
            self.tableWidget_put.setColumnWidth(0, 15)

            call_volume_total = df_cm_call['수정거래량'].sum()
            put_volume_total = df_cm_put['수정거래량'].sum()

            self.call_open_check()
            self.call_db_check()

            self.put_open_check()
            self.put_db_check()

            self.call_node_color_clear()
            self.put_node_color_clear()

            self.callnode_color_check()
            self.putnode_color_check()

            if not refresh_flag:

                # 실시간테이타 요청
                self.cm_opt_real = EC0(parent=self)
                self.cm_opt_ho = EH0(parent=self)
                self.fut_real = NC0(parent=self)
                self.fut_ho = NH0(parent=self)

                self.fut_real.AdviseRealData(gmshcode)
                self.fut_ho.AdviseRealData(gmshcode)

                # 업종별 투자자별 매매현황 요청
                self.BM.AdviseRealData(CME)

                for i in range(15):
                    self.cm_opt_ho.AdviseRealData(cm_call_code[(old_atm_index - 7) + i])
                    self.cm_opt_ho.AdviseRealData(cm_put_code[(old_atm_index - 7) + i])

                for i in range(nCount_cm_option_pairs):
                    self.cm_opt_real.AdviseRealData(df['콜옵션코드'][i])
                    self.cm_opt_real.AdviseRealData(df1['풋옵션코드'][i])

                str = '[{0:02d}:{1:02d}:{2:02d}] 야간 실시간데이타를 요청합니다.\r'.format(dt.hour, dt.minute,
                                                                             dt.second)
                self.textBrowser.append(str)

                self.plot_worker.start()
                self.plot_worker.daemon = True
                print('Plot 쓰레드가 시작됩니다...')
                print('\r')

                str = '[{0:02d}:{1:02d}:{2:02d}] Plot 쓰레드가 시작됩니다.\r'.format(dt.hour, dt.minute,
                                                                            dt.second)
                self.textBrowser.append(str)

                refresh_flag = True
                self.pushButton_add.setText('Refresh')
            else:
                pass

        elif szTrCode == 't8415':

            block, df = result

            if block['단축코드'][0:3] == '201':

                for i in range(len(selected_call)):

                    if result['단축코드'][5:8] == df_cm_call.iloc[selected_call[i]]['행사가']:

                        pass
                    else:
                        pass

            elif block['단축코드'][0:3] == '301':

                for i in range(len(selected_put)):

                    if result['단축코드'][5:8] == df_cm_put.iloc[selected_put[i]]['행사가']:

                        pass
                    else:
                        pass
            else:
                pass

        elif szTrCode == 't8416':

            block, df = result

            global cm_call_t8416_count, cm_put_t8416_count
            global actval_increased

            if block['단축코드'] == '':

                if self.t8416_callworker.isRunning():

                    cm_call_기준가 = df_cm_call['기준가'].values.tolist()
                    cm_call_월저 = df_cm_call['월저'].values.tolist()
                    cm_call_월고 = df_cm_call['월고'].values.tolist()
                    cm_call_전저 = df_cm_call['전저'].values.tolist()
                    cm_call_전고 = df_cm_call['전고'].values.tolist()

                    cm_call_기준가_extend = self.make_color_list(cm_call_기준가)
                    cm_call_월저_extend = self.make_color_list(cm_call_월저)
                    cm_call_월고_extend = self.make_color_list(cm_call_월고)
                    cm_call_전저_extend = self.make_color_list(cm_call_전저)
                    cm_call_전고_extend = self.make_color_list(cm_call_전고)

                    self.t8416_callworker.terminate()
                    str = '[{0:02d}:{1:02d}:{2:02d}] Call 과거데이타 수신완료 !!!\r'.format(dt.hour, dt.minute,
                                                                    dt.second)
                    self.textBrowser.append(str)

                    call_positionCell = self.tableWidget_call.item(atm_index + 3, 1)
                    self.tableWidget_call.scrollToItem(call_positionCell)

                    time.sleep(1.1)

                    self.t8416_putworker.start()
                    self.t8416_putworker.daemon = True
                else:
                    pass

                actval_increased = True

                print('새로운 행사가 추가됨 !!!')
                print('\r')
                str = '[{0:02d}:{1:02d}:{2:02d}] 새로운 행사가 추가됨 !!!\r'.format(dt.hour, dt.minute, dt.second)
                self.textBrowser.append(str)

            else:
                pass

            if block['단축코드'][0:3] == '101':

                if not overnight:

                    item = QTableWidgetItem("{0:0.2f}".format(block['전일저가']))
                    item.setTextAlignment(Qt.AlignCenter)
                    self.tableWidget_fut.setItem(1, Futures_column.전저.value, item)

                    item = QTableWidgetItem("{0:0.2f}".format(block['전일고가']))
                    item.setTextAlignment(Qt.AlignCenter)
                    self.tableWidget_fut.setItem(1, Futures_column.전고.value, item)

                    item = QTableWidgetItem("{0:0.2f}".format(block['전일종가']))
                    item.setTextAlignment(Qt.AlignCenter)
                    self.tableWidget_fut.setItem(1, Futures_column.종가.value, item)

                    self.tableWidget_fut.resizeColumnsToContents()
                else:
                    pass

            elif block['단축코드'][0:3] == '201':

                df_cm_call.loc[cm_call_t8416_count, '기준가'] = round(df['저가'][0], 2)
                item = QTableWidgetItem("{0:0.2f}".format(df['저가'][0]))
                item.setTextAlignment(Qt.AlignCenter)
                self.tableWidget_call.setItem(cm_call_t8416_count, Option_column.기준가.value, item)

                df_cm_call.loc[cm_call_t8416_count, '월저'] = round(min(df['저가']), 2)
                item = QTableWidgetItem("{0:0.2f}".format(min(df['저가'])))
                item.setTextAlignment(Qt.AlignCenter)
                self.tableWidget_call.setItem(cm_call_t8416_count, Option_column.월저.value, item)

                df_cm_call.loc[cm_call_t8416_count, '월고'] = round(max(df['고가']), 2)
                item = QTableWidgetItem("{0:0.2f}".format(max(df['고가'])))
                item.setTextAlignment(Qt.AlignCenter)
                self.tableWidget_call.setItem(cm_call_t8416_count, Option_column.월고.value, item)

                df_cm_call.loc[cm_call_t8416_count, '전저'] = round(block['전일저가'], 2)
                item = QTableWidgetItem("{0:0.2f}".format(df_cm_call.iloc[cm_call_t8416_count]['전저']))
                item.setTextAlignment(Qt.AlignCenter)
                self.tableWidget_call.setItem(cm_call_t8416_count, Option_column.전저.value, item)

                df_cm_call.loc[cm_call_t8416_count, '전고'] = round(block['전일고가'], 2)
                item = QTableWidgetItem("{0:0.2f}".format(df_cm_call.iloc[cm_call_t8416_count]['전고']))
                item.setTextAlignment(Qt.AlignCenter)
                self.tableWidget_call.setItem(cm_call_t8416_count, Option_column.전고.value, item)

                df_cm_call.loc[cm_call_t8416_count, '종가'] = round(block['전일종가'], 2)
                item = QTableWidgetItem("{0:0.2f}".format(df_cm_call.iloc[cm_call_t8416_count]['종가']))
                item.setTextAlignment(Qt.AlignCenter)
                self.tableWidget_call.setItem(cm_call_t8416_count, Option_column.종가.value, item)

                if not pre_start:

                    if df_cm_call.iloc[cm_call_t8416_count]['시가'] > 0 and \
                            df_cm_call.iloc[cm_call_t8416_count]['저가'] < df_cm_call.iloc[cm_call_t8416_count]['고가']:

                        temp = self.calc_pivot(df_cm_call.iloc[cm_call_t8416_count]['전저'],
                            df_cm_call.iloc[cm_call_t8416_count]['전고'],
                            df_cm_call.iloc[cm_call_t8416_count]['종가'],
                            df_cm_call.iloc[cm_call_t8416_count]['시가'])

                        df_cm_call.loc[cm_call_t8416_count, '피봇'] = round(temp, 2)

                        item = QTableWidgetItem("{0:0.2f}".format(df_cm_call.iloc[cm_call_t8416_count]['피봇']))
                        item.setTextAlignment(Qt.AlignCenter)
                        self.tableWidget_call.setItem(cm_call_t8416_count, Option_column.피봇.value, item)

                        if df_cm_call.iloc[cm_call_t8416_count]['시가'] > 0.3:

                            temp = df_cm_call.iloc[cm_call_t8416_count]['시가'] - df_cm_call.iloc[cm_call_t8416_count]['종가']

                            if temp != 0:

                                df_cm_call.loc[cm_call_t8416_count, '시가갭'] = round(temp, 2)

                                if df_cm_call.iloc[cm_call_t8416_count]['종가'] > 0:

                                    gap_percent = int((df_cm_call.iloc[cm_call_t8416_count]['시가'] /
                                                       df_cm_call.iloc[cm_call_t8416_count]['종가'] - 1) * 100)

                                    item = QTableWidgetItem(
                                        "{0:0.2f}({1}%)".format(df_cm_call.iloc[cm_call_t8416_count]['시가갭'], gap_percent))
                                    item.setTextAlignment(Qt.AlignCenter)
                                    self.tableWidget_call.setItem(cm_call_t8416_count, Option_column.시가갭.value, item)
                                else:
                                    pass

                            temp = round((df_cm_call.iloc[cm_call_t8416_count]['현재가'] -
                                          df_cm_call.iloc[cm_call_t8416_count]['시가']), 2) * 100

                            df_cm_call.loc[cm_call_t8416_count, '대비'] = int(temp)

                            item = QTableWidgetItem("{0}".format(df_cm_call.iloc[cm_call_t8416_count]['대비']))
                            item.setTextAlignment(Qt.AlignCenter)
                            self.tableWidget_call.setItem(cm_call_t8416_count, Option_column.대비.value, item)

                            df_cm_call.loc[cm_call_t8416_count, '진폭'] = df_cm_call.iloc[cm_call_t8416_count]['고가'] - \
                                                                        df_cm_call.iloc[cm_call_t8416_count]['저가']

                            item = QTableWidgetItem("{0:0.2f}".format(df_cm_call.iloc[cm_call_t8416_count]['진폭']))
                            item.setTextAlignment(Qt.AlignCenter)
                            self.tableWidget_call.setItem(cm_call_t8416_count, Option_column.진폭.value, item)
                        else:
                            pass
                    else:
                        pass
                else:
                    pass

                str = '[{0:02d}:{1:02d}:{2:02d}] Call 과거데이타({3}/{4}) 수신중...\r'.\
                    format(dt.hour, dt.minute, dt.second, cm_call_t8416_count + 1, nCount_cm_option_pairs)

                self.textBrowser.append(str)

                cm_call_t8416_count += 1

                if cm_call_t8416_count == nCount_cm_option_pairs:

                    cm_call_기준가 = df_cm_call['기준가'].values.tolist()
                    cm_call_월저 = df_cm_call['월저'].values.tolist()
                    cm_call_월고 = df_cm_call['월고'].values.tolist()

                    cm_call_기준가_extend = self.make_color_list(cm_call_기준가)
                    cm_call_월저_extend = self.make_color_list(cm_call_월저)
                    cm_call_월고_extend = self.make_color_list(cm_call_월고)                    

                    if not overnight:

                        cm_call_전저 = df_cm_call['전저'].values.tolist()
                        cm_call_전고 = df_cm_call['전고'].values.tolist()
                        cm_call_전저_extend = self.make_color_list(cm_call_전저)
                        cm_call_전고_extend = self.make_color_list(cm_call_전고)
                    else:
                        pass

                    if self.t8416_callworker.isRunning():

                        self.t8416_callworker.terminate()
                        str = '[{0:02d}:{1:02d}:{2:02d}] Call 과거데이타 수신완료 !!!\r'.format(dt.hour, dt.minute,
                                                                       dt.second)
                        self.textBrowser.append(str)

                        self.tableWidget_call.resizeColumnsToContents()
                        self.tableWidget_call.setColumnWidth(0, 15)

                        call_positionCell = self.tableWidget_call.item(atm_index + 3, 1)
                        self.tableWidget_call.scrollToItem(call_positionCell)

                        time.sleep(1.1)

                        self.t8416_putworker.start()
                        self.t8416_putworker.daemon = True
                    else:
                        pass
                else:
                    pass

            elif block['단축코드'][0:3] == '301':

                df_cm_put.loc[cm_put_t8416_count, '기준가'] = round(df['저가'][0], 2)
                item = QTableWidgetItem("{0:0.2f}".format(df['저가'][0]))
                item.setTextAlignment(Qt.AlignCenter)
                self.tableWidget_put.setItem(cm_put_t8416_count, Option_column.기준가.value, item)

                df_cm_put.loc[cm_put_t8416_count, '월저'] = round(min(df['저가']), 2)
                item = QTableWidgetItem("{0:0.2f}".format(min(df['저가'])))
                item.setTextAlignment(Qt.AlignCenter)
                self.tableWidget_put.setItem(cm_put_t8416_count, Option_column.월저.value, item)

                df_cm_put.loc[cm_put_t8416_count, '월고'] = round(max(df['고가']), 2)
                item = QTableWidgetItem("{0:0.2f}".format(max(df['고가'])))
                item.setTextAlignment(Qt.AlignCenter)
                self.tableWidget_put.setItem(cm_put_t8416_count, Option_column.월고.value, item)

                df_cm_put.loc[cm_put_t8416_count, '전저'] = round(block['전일저가'], 2)
                item = QTableWidgetItem("{0:0.2f}".format(df_cm_put.iloc[cm_put_t8416_count]['전저']))
                item.setTextAlignment(Qt.AlignCenter)
                self.tableWidget_put.setItem(cm_put_t8416_count, Option_column.전저.value, item)

                df_cm_put.loc[cm_put_t8416_count, '전고'] = round(block['전일고가'], 2)
                item = QTableWidgetItem("{0:0.2f}".format(df_cm_put.iloc[cm_put_t8416_count]['전고']))
                item.setTextAlignment(Qt.AlignCenter)
                self.tableWidget_put.setItem(cm_put_t8416_count, Option_column.전고.value, item)

                df_cm_put.loc[cm_put_t8416_count, '종가'] = round(block['전일종가'], 2)
                item = QTableWidgetItem("{0:0.2f}".format(df_cm_put.iloc[cm_put_t8416_count]['종가']))
                item.setTextAlignment(Qt.AlignCenter)
                self.tableWidget_put.setItem(cm_put_t8416_count, Option_column.종가.value, item)

                if not pre_start:

                    if df_cm_put.iloc[cm_put_t8416_count]['시가'] > 0 and \
                            df_cm_put.iloc[cm_put_t8416_count]['저가'] < df_cm_put.iloc[cm_put_t8416_count]['고가']:

                        temp = self.calc_pivot(df_cm_put.iloc[cm_put_t8416_count]['전저'],
                            df_cm_put.iloc[cm_put_t8416_count]['전고'],
                            df_cm_put.iloc[cm_put_t8416_count]['종가'],
                            df_cm_put.iloc[cm_put_t8416_count]['시가'])

                        df_cm_put.loc[cm_put_t8416_count, '피봇'] = round(temp, 2)

                        item = QTableWidgetItem("{0:0.2f}".format(df_cm_put.iloc[cm_put_t8416_count]['피봇']))
                        item.setTextAlignment(Qt.AlignCenter)
                        self.tableWidget_put.setItem(cm_put_t8416_count, Option_column.피봇.value, item)

                        if df_cm_put.iloc[cm_put_t8416_count]['시가'] > 0.3:

                            temp = df_cm_put.iloc[cm_put_t8416_count]['시가'] - df_cm_put.iloc[cm_put_t8416_count]['종가']

                            if temp != 0:

                                df_cm_put.loc[cm_put_t8416_count, '시가갭'] = round(temp, 2)

                                if df_cm_put.iloc[cm_put_t8416_count]['종가'] > 0:

                                    gap_percent = int((df_cm_put.iloc[cm_put_t8416_count]['시가'] /
                                                       df_cm_put.iloc[cm_put_t8416_count]['종가'] - 1) * 100)

                                    item = QTableWidgetItem(
                                        "{0:0.2f}({1}%)".format(df_cm_put.iloc[cm_put_t8416_count]['시가갭'], gap_percent))
                                    item.setTextAlignment(Qt.AlignCenter)
                                    self.tableWidget_put.setItem(cm_put_t8416_count, Option_column.시가갭.value, item)
                                else:
                                    pass

                            temp = round((df_cm_put.iloc[cm_put_t8416_count]['현재가'] -
                                          df_cm_put.iloc[cm_put_t8416_count]['시가']), 2) * 100

                            df_cm_put.loc[cm_put_t8416_count, '대비'] = int(temp)

                            item = QTableWidgetItem("{0}".format(df_cm_put.iloc[cm_put_t8416_count]['대비']))
                            item.setTextAlignment(Qt.AlignCenter)
                            self.tableWidget_put.setItem(cm_put_t8416_count, Option_column.대비.value, item)

                            df_cm_put.loc[cm_put_t8416_count, '진폭'] = df_cm_put.iloc[cm_put_t8416_count]['고가'] - \
                                                                      df_cm_put.iloc[cm_put_t8416_count]['저가']

                            item = QTableWidgetItem("{0:0.2f}".format(df_cm_put.iloc[cm_put_t8416_count]['진폭']))
                            item.setTextAlignment(Qt.AlignCenter)
                            self.tableWidget_put.setItem(cm_put_t8416_count, Option_column.진폭.value, item)
                        else:
                            pass
                    else:
                        pass
                else:
                    pass

                str = '[{0:02d}:{1:02d}:{2:02d}] Put 과거데이타({3}/{4}) 수신중...\r'.format(dt.hour, dt.minute, dt.second, cm_put_t8416_count + 1, nCount_cm_option_pairs)
                self.textBrowser.append(str)

                cm_put_t8416_count += 1
            else:
                pass

            if actval_increased:
                new_count = nCount_cm_option_pairs - 1
            else:
                new_count = nCount_cm_option_pairs

            if cm_put_t8416_count == new_count:

                cm_put_기준가 = df_cm_put['기준가'].values.tolist()
                cm_put_월저 = df_cm_put['월저'].values.tolist()
                cm_put_월고 = df_cm_put['월고'].values.tolist()

                cm_put_기준가_extend = self.make_color_list(cm_put_기준가)
                cm_put_월저_extend = self.make_color_list(cm_put_월저)
                cm_put_월고_extend = self.make_color_list(cm_put_월고)

                if not overnight:

                    cm_put_전저 = df_cm_put['전저'].values.tolist()
                    cm_put_전고 = df_cm_put['전고'].values.tolist()                    
                    cm_put_전저_extend = self.make_color_list(cm_put_전저)
                    cm_put_전고_extend = self.make_color_list(cm_put_전고)
                else:
                    pass

                print('\r')
                print('t8416 Call 전광판\r')
                print(df_cm_call)
                print('\r')
                print('t8416 Put 전광판\r')
                print(df_cm_put)
                print('\r')

                self.tableWidget_put.resizeColumnsToContents()
                self.tableWidget_put.setColumnWidth(0, 15)

                put_positionCell = self.tableWidget_put.item(atm_index + 3, 1)
                self.tableWidget_put.scrollToItem(put_positionCell)

                if self.t8416_putworker.isRunning():

                    self.t8416_putworker.terminate()
                    str = '[{0:02d}:{1:02d}:{2:02d}] Put 과거데이타 수신완료 !!!\r'.format(dt.hour, dt.minute,
                                                                  dt.second)
                    self.textBrowser.append(str)
                else:
                    pass

                print('옵션 과거데이타 수신완료 !!!')
                print('\r')

                if overnight:

                    # EUREX 야간옵션 시세전광판
                    XQ = t2835(parent=self)
                    XQ.Query(월물=month_str)

                    str = '[{0:02d}:{1:02d}:{2:02d}] EUREX 야간옵션 데이타를 요청합니다.\r'.format(dt.hour, dt.minute,
                                                                 dt.second)
                    self.textBrowser.append(str)
                else:

                    if pre_start:

                        for i in range(nCount_cm_option_pairs):
                            수정거래량 = 0

                            df_cm_call.loc[i, '수정거래량'] = 수정거래량
                            df_cm_put.loc[i, '수정거래량'] = 수정거래량

                            temp = format(수정거래량, ',')

                            item = QTableWidgetItem(temp)
                            item.setTextAlignment(Qt.AlignCenter)
                            self.tableWidget_call.setItem(i, Option_column.OI.value, item)

                            item = QTableWidgetItem(temp)
                            item.setTextAlignment(Qt.AlignCenter)
                            self.tableWidget_put.setItem(i, Option_column.OI.value, item)

                        str = '[{0:02d}:{1:02d}:{2:02d}] 수정거래량을 초기화합니다.\r'.format(dt.hour, dt.minute,
                                                                                  dt.second)
                        self.textBrowser.append(str)
                    else:
                        pass

                    self.call_open_check()
                    self.call_db_check()

                    self.put_open_check()
                    self.put_db_check()

                    self.call_node_color_clear()
                    self.put_node_color_clear()

                    self.callnode_color_check()
                    self.putnode_color_check()
                    
                    if not refresh_flag:

                        self.plot_worker.start()
                        self.plot_worker.daemon = True
                        print('Plot 쓰레드가 시작됩니다...')
                        print('\r')

                        str = '[{0:02d}:{1:02d}:{2:02d}] Plot 쓰레드가 시작됩니다.\r'.format(dt.hour, dt.minute,
                                                                                    dt.second)
                        self.textBrowser.append(str)

                        refresh_flag = True
                        self.pushButton_add.setText('Refresh')
                    else:
                        pass

        elif szTrCode == 't8432':

            df = result[0]

            근월물선물코드 = df.iloc[0]['단축코드']
            차월물선물코드 = df.iloc[1]['단축코드']

            gmshcode = 근월물선물코드

            print('근월물선물코드', 근월물선물코드)
            print('차월물선물코드', 차월물선물코드)

            if not overnight:
                fut_realdata['전저'] = df.iloc[0]['전일저가']
                item = QTableWidgetItem("{0:0.2f}".format(df.iloc[0]['전일저가']))
                item.setTextAlignment(Qt.AlignCenter)
                self.tableWidget_fut.setItem(1, Futures_column.전저.value, item)

                fut_realdata['전고'] = df.iloc[0]['전일고가']
                item = QTableWidgetItem("{0:0.2f}".format(df.iloc[0]['전일고가']))
                item.setTextAlignment(Qt.AlignCenter)
                self.tableWidget_fut.setItem(1, Futures_column.전고.value, item)

                fut_realdata['종가'] = df.iloc[0]['전일종가']
                item = QTableWidgetItem("{0:0.2f}".format(df.iloc[0]['전일종가']))
                item.setTextAlignment(Qt.AlignCenter)
                self.tableWidget_fut.setItem(1, Futures_column.종가.value, item)
            else:
                pass

            self.tableWidget_fut.resizeColumnsToContents()

        elif szTrCode == 't8433':

            pass
        else:
            pass

    def call_display(self, result):

        global opt_callreal_update_counter
        global df_cm_call, df_plotdata_cm_call, df_plotdata_cm_call_volume, df_plotdata_cm_call_oi
        global call_atm_value, call_db_percent
        global cm_call_피봇, cm_call_피봇_extend, cm_call_시가, cm_call_시가_extend
        global df_cm_call_che
        global call_volume_total
        global cm_call_저가, cm_call_저가_extend, cm_call_고가, cm_call_고가_extend

        dt = datetime.datetime.now()

        opt_callreal_update_counter += 1

        index = cm_call_행사가.index(result['단축코드'][5:8])

        if call_scroll_begin_position <= index < call_scroll_end_position:

            # Data Update
            if result['저가'] != self.tableWidget_call.item(index, Option_column.저가.value).text():

                df_cm_call.loc[index, '저가'] = round(float(result['저가']), 2)

                item = QTableWidgetItem(result['저가'])
                item.setTextAlignment(Qt.AlignCenter)
                #item.setBackground(QBrush(옅은회색))                
                self.tableWidget_call.setItem(index, Option_column.저가.value, item)

                str = '[{0:02d}:{1:02d}:{2:02d}] Call {3} 저가갱신됨 !!!\r'.format(delta_hour, delta_minute, delta_sec,
                                                                              result['저가'])
                self.textBrowser.append(str)

                cm_call_저가 = df_cm_call['저가'].values.tolist()
                cm_call_저가_extend = self.make_color_list(cm_call_저가)

                item = QTableWidgetItem("{0:0.2f}".format(float(result['고가']) - float(result['저가'])))
                item.setTextAlignment(Qt.AlignCenter)
                self.tableWidget_call.setItem(index, Option_column.진폭.value, item)
            else:
                pass

            if result['고가'] != self.tableWidget_call.item(index, Option_column.고가.value).text():

                df_cm_call.loc[index, '고가'] = round(float(result['고가']), 2)

                item = QTableWidgetItem(result['고가'])
                item.setTextAlignment(Qt.AlignCenter)
                #item.setBackground(QBrush(옅은회색))
                self.tableWidget_call.setItem(index, Option_column.고가.value, item)

                str = '[{0:02d}:{1:02d}:{2:02d}] Call {3} 고가갱신됨 !!!\r'.format(delta_hour, delta_minute, delta_sec,
                                                                              result['고가'])
                self.textBrowser.append(str)

                cm_call_고가 = df_cm_call['고가'].values.tolist()
                cm_call_고가_extend = self.make_color_list(cm_call_고가)

                item = QTableWidgetItem("{0:0.2f}".format(float(result['고가']) - float(result['저가'])))
                item.setTextAlignment(Qt.AlignCenter)
                self.tableWidget_call.setItem(index, Option_column.진폭.value, item)
            else:
                pass

            if result['현재가'] != self.tableWidget_call.item(index, Option_column.현재가.value).text():

                df_cm_call.loc[index, '현재가'] = round(float(result['현재가']), 2)
                df_plotdata_cm_call.iloc[index][opt_x_idx + 1] = float(result['현재가'])

                item = QTableWidgetItem(result['현재가'])
                item.setTextAlignment(Qt.AlignCenter)
                item.setBackground(QBrush(기본바탕색))

                if float(result['시가']) < float(result['현재가']):
                    item.setForeground(QBrush(적색))
                elif float(result['시가']) > float(result['현재가']):
                    item.setForeground(QBrush(청색))
                else:
                    item.setForeground(QBrush(검정색))
                self.tableWidget_call.setItem(index, Option_column.현재가.value, item)

                if float(result['현재가']) <= df_cm_call.iloc[index]['시가갭']:

                    수정거래량 = result['누적거래량'] * float(result['현재가'])
                    매도누적체결량 = result['매도누적체결량'] * float(result['현재가'])
                    매수누적체결량 = result['매수누적체결량'] * float(result['현재가'])
                    미결 = result['미결제약정수량'] * float(result['현재가'])
                    미결증감 = result['미결제약정증감'] * float(result['현재가'])

                    if not overnight:

                        매도누적체결건수 = result['매도누적체결건수'] * float(result['현재가'])
                        매수누적체결건수 = result['매수누적체결건수'] * float(result['현재가'])
                    else:
                        pass
                else:
                    수정거래량 = result['누적거래량'] * (float(result['현재가']) - df_cm_call.iloc[index]['시가갭'])
                    매도누적체결량 = result['매도누적체결량'] * (float(result['현재가']) - df_cm_call.iloc[index]['시가갭'])
                    매수누적체결량 = result['매수누적체결량'] * (float(result['현재가']) - df_cm_call.iloc[index]['시가갭'])
                    미결 = result['미결제약정수량'] * (float(result['현재가']) - df_cm_call.iloc[index]['시가갭'])
                    미결증감 = result['미결제약정증감'] * (float(result['현재가']) - df_cm_call.iloc[index]['시가갭'])

                    if not overnight:

                        매도누적체결건수 = result['매도누적체결건수'] * (float(result['현재가']) - df_cm_call.iloc[index]['시가갭'])
                        매수누적체결건수 = result['매수누적체결건수'] * (float(result['현재가']) - df_cm_call.iloc[index]['시가갭'])
                    else:
                        pass

                df_cm_call.loc[index, '수정거래량'] = int(수정거래량)
                #df_plotdata_cm_call_volume.iloc[0][opt_x_idx + 1] = df_cm_call['수정거래량'].sum()
                #call_volume_total = df_cm_call['수정거래량'].sum()

                df_cm_call.loc[index, '미결'] = int(미결)
                df_cm_call.loc[index, '미결증감'] = int(미결증감)

                df_plotdata_cm_call_oi.iloc[0][opt_x_idx + 1] = df_cm_call['미결'].sum() - call_oi_percent_init_value

                df_cm_call_che.loc[index, '매도누적체결량'] = int(매도누적체결량)
                df_cm_call_che.loc[index, '매수누적체결량'] = int(매수누적체결량)

                if not overnight:

                    df_cm_call_che.loc[index, '매도누적체결건수'] = int(매도누적체결건수)
                    df_cm_call_che.loc[index, '매수누적체결건수'] = int(매수누적체결건수)
                else:
                    pass

                call_volume_total = df_cm_call_che['매수누적체결량'].sum() - df_cm_call_che['매도누적체결량'].sum()

                df_plotdata_cm_call_volume.iloc[0][opt_x_idx + 1] = call_volume_total

                if index == atm_index:

                    call_atm_value = float(result['현재가'])
                else:
                    pass

                if float(result['시가']) > 0.3 and float(result['저가']) < float(result['고가']):

                    call_db_percent[index] = (float(result['현재가']) / float(result['시가']) - 1) * 100

                    gap_str = "{0:0.0f}({1:0.0f}%)".format(
                        (float(result['현재가']) - float(result['시가'])) * 100, call_db_percent[index])

                    if gap_str != self.tableWidget_call.setItem(index, Option_column.대비.value, item).text():

                        item = QTableWidgetItem(gap_str)
                        item.setTextAlignment(Qt.AlignCenter)
                        self.tableWidget_call.setItem(index, Option_column.대비.value, item)
                    else:
                        pass
                else:
                    pass
            else:
                pass

            # 현재가가 시가임
            if result['현재가'] == result['저가'] and result['현재가'] == result['고가']:

                if result['시가'] != self.tableWidget_call.item(index, Option_column.시가.value).text():

                    str = '[{0:02d}:{1:02d}:{2:02d}] Call in Window 시가 {3} Open...\r'. \
                        format(dt.hour, dt.minute, dt.second, result['시가'])

                    self.textBrowser.append(str)

                    if df_cm_call.iloc[index]['종가'] > 0:

                        df_cm_call.loc[index, '시가'] = round(float(result['시가']), 2)
                        df_cm_call.loc[index, '시가갭'] = float(result['시가']) - df_cm_call.iloc[index]['종가']
                        df_plotdata_cm_call.iloc[index][1] = float(result['시가'])

                        item = QTableWidgetItem(result['시가'])
                        item.setTextAlignment(Qt.AlignCenter)

                        if float(result['시가']) > df_cm_call.iloc[index]['종가']:
                            item.setForeground(QBrush(적색))
                        elif float(result['시가']) < df_cm_call.iloc[index]['종가']:
                            item.setForeground(QBrush(청색))
                        else:
                            item.setForeground(QBrush(검정색))

                        self.tableWidget_call.setItem(index, Option_column.시가.value, item)

                        cm_call_시가 = df_cm_call['시가'].values.tolist()
                        cm_call_시가_extend = self.make_color_list(cm_call_시가)
                    else:
                        pass

                    if df_cm_call.iloc[index]['시가'] > 0:

                        temp = self.calc_pivot(df_cm_call.iloc[index]['전저'],
                                                                      df_cm_call.iloc[index]['전고'],
                                                                      df_cm_call.iloc[index]['종가'],
                                                                      df_cm_call.iloc[index]['시가'])

                        df_cm_call.loc[index, '피봇'] = round(temp, 2)

                        item = QTableWidgetItem("{0:0.2f}".format(df_cm_call.iloc[index]['피봇']))
                        item.setTextAlignment(Qt.AlignCenter)
                        self.tableWidget_call.setItem(index, Option_column.피봇.value, item)

                        cm_call_피봇 = df_cm_call['피봇'].values.tolist()
                        cm_call_피봇_extend = self.make_color_list(cm_call_피봇)
                    else:
                        pass
                else:
                    pass
            else:
                pass
        else:

            if float(result['시가']) > 0.3:

                if result['저가'] != self.tableWidget_call.item(index, Option_column.저가.value).text():

                    df_cm_call.loc[index, '저가'] = round(float(result['저가']), 2)

                    item = QTableWidgetItem(result['저가'])
                    item.setTextAlignment(Qt.AlignCenter)
                    item.setBackground(QBrush(옅은회색))
                    self.tableWidget_call.setItem(index, Option_column.저가.value, item)

                    item = QTableWidgetItem("{0:0.2f}".format(float(result['고가']) - float(result['저가'])))
                    item.setTextAlignment(Qt.AlignCenter)
                    self.tableWidget_call.setItem(index, Option_column.진폭.value, item)
                else:
                    pass

                if result['고가'] != self.tableWidget_call.item(index, Option_column.고가.value).text():

                    df_cm_call.loc[index, '고가'] = round(float(result['고가']), 2)

                    item = QTableWidgetItem(result['고가'])
                    item.setTextAlignment(Qt.AlignCenter)
                    item.setBackground(QBrush(옅은회색))
                    self.tableWidget_call.setItem(index, Option_column.고가.value, item)

                    item = QTableWidgetItem("{0:0.2f}".format(float(result['고가']) - float(result['저가'])))
                    item.setTextAlignment(Qt.AlignCenter)
                    self.tableWidget_call.setItem(index, Option_column.진폭.value, item)
                else:
                    pass

                if result['현재가'] != self.tableWidget_call.item(index, Option_column.현재가.value).text():

                    df_cm_call.loc[index, '현재가'] = round(float(result['현재가']), 2)
                    df_plotdata_cm_call.iloc[index][opt_x_idx + 1] = float(result['현재가'])

                    item = QTableWidgetItem(result['현재가'])
                    item.setTextAlignment(Qt.AlignCenter)
                    item.setBackground(QBrush(기본바탕색))
                    self.tableWidget_call.setItem(index, Option_column.현재가.value, item)

                    if float(result['저가']) < float(result['고가']):

                        call_db_percent[index] = (float(result['현재가']) / float(result['시가']) - 1) * 100

                        gap_str = "{0:0.0f}({1:0.0f}%)".format(
                            (float(result['현재가']) - float(result['시가'])) * 100, call_db_percent[index])

                        if gap_str != self.tableWidget_call.setItem(index, Option_column.대비.value, item).text():

                            item = QTableWidgetItem(gap_str)
                            item.setTextAlignment(Qt.AlignCenter)
                            self.tableWidget_call.setItem(index, Option_column.대비.value, item)
                        else:
                            pass
                    else:
                        pass
                else:
                    pass

                # 현재가가 시가임
                if result['현재가'] == result['저가'] and result['현재가'] == result['고가']:

                    if result['시가'] != self.tableWidget_call.item(index, Option_column.시가.value).text():

                        str = '[{0:02d}:{1:02d}:{2:02d}] Call out Window 시가 {3} Open...\r'. \
                            format(dt.hour, dt.minute, dt.second, result['시가'])

                        self.textBrowser.append(str)

                        if df_cm_call.iloc[index]['종가'] > 0:

                            df_cm_call.loc[index, '시가'] = round(float(result['시가']), 2)
                            df_cm_call.loc[index, '시가갭'] = float(result['시가']) - df_cm_call.iloc[index]['종가']
                            df_plotdata_cm_call.iloc[index][1] = float(result['시가'])

                            item = QTableWidgetItem(result['시가'])
                            item.setTextAlignment(Qt.AlignCenter)

                            if float(result['시가']) > df_cm_call.iloc[index]['종가']:
                                item.setForeground(QBrush(적색))
                            elif float(result['시가']) < df_cm_call.iloc[index]['종가']:
                                item.setForeground(QBrush(청색))
                            else:
                                item.setForeground(QBrush(검정색))

                            self.tableWidget_call.setItem(index, Option_column.시가.value, item)

                            cm_call_시가 = df_cm_call['시가'].values.tolist()
                            cm_call_시가_extend = self.make_color_list(cm_call_시가)
                        else:
                            pass

                        if df_cm_call.iloc[index]['시가'] > 0:

                            temp = self.calc_pivot(df_cm_call.iloc[index]['전저'],
                                                                          df_cm_call.iloc[index]['전고'],
                                                                          df_cm_call.iloc[index]['종가'],
                                                                          df_cm_call.iloc[index]['시가'])

                            df_cm_call.loc[index, '피봇'] = round(temp, 2)

                            item = QTableWidgetItem("{0:0.2f}".format(df_cm_call.iloc[index]['피봇']))
                            item.setTextAlignment(Qt.AlignCenter)
                            self.tableWidget_call.setItem(index, Option_column.피봇.value, item)

                            cm_call_피봇 = df_cm_call['피봇'].values.tolist()
                            cm_call_피봇_extend = self.make_color_list(cm_call_피봇)
                        else:
                            pass
                    else:
                        pass
                else:
                    pass
            else:
                pass

    def call_post_processing(self):

        global call_below_atm_count

        global call_open, call_ol, call_oh
        global call_gap_percent
        global df_plotdata_cm_call
        global cm_call_시가, cm_call_시가_extend, cm_call_피봇, cm_call_피봇_extend

        index = cm_call_행사가.index(call_result['단축코드'][5:8])

        if call_result['시가'] != self.tableWidget_call.item(index, Option_column.시가.value).text():

            if float(call_result['시가']) > 0 and df_cm_call.iloc[index]['종가'] > 0:

                df_cm_call.loc[index, '시가'] = round(float(call_result['시가']), 2)
                df_cm_call.loc[index, '시가갭'] = float(call_result['시가']) - df_cm_call.iloc[index]['종가']
                df_plotdata_cm_call.iloc[index][1] = float(call_result['시가'])

                item = QTableWidgetItem(call_result['시가'])
                item.setTextAlignment(Qt.AlignCenter)

                if float(call_result['시가']) > df_cm_call.iloc[index]['종가']:
                    item.setForeground(QBrush(적색))
                elif float(call_result['시가']) < df_cm_call.iloc[index]['종가']:
                    item.setForeground(QBrush(청색))
                else:
                    item.setForeground(QBrush(검정색))

                self.tableWidget_call.setItem(index, Option_column.시가.value, item)

                if float(call_result['시가']) > 0.3:

                    call_gap_percent[index] = (float(call_result['시가']) / df_cm_call.iloc[index]['종가'] - 1) * 100
                    gap_str = "{0:0.2f}({1:0.0f}%)".format(df_cm_call.iloc[index]['시가갭'], call_gap_percent[index])
                else:
                    gap_str = "{0:0.2f}".format(df_cm_call.iloc[index]['시가갭'])

                if gap_str != self.tableWidget_call.item(index, Option_column.시가갭.value).text():

                    item = QTableWidgetItem(gap_str)
                    item.setTextAlignment(Qt.AlignCenter)
                    self.tableWidget_call.setItem(index, Option_column.시가갭.value, item)
                else:
                    pass

                temp = self.calc_pivot(df_cm_call.iloc[index]['전저'],
                                                              df_cm_call.iloc[index]['전고'],
                                                              df_cm_call.iloc[index]['종가'],
                                                              df_cm_call.iloc[index]['시가'])

                df_cm_call.loc[index, '피봇'] = round(temp, 2)

                item = QTableWidgetItem("{0:0.2f}".format(df_cm_call.iloc[index]['피봇']))
                item.setTextAlignment(Qt.AlignCenter)
                self.tableWidget_call.setItem(index, Option_column.피봇.value, item)

                cm_call_시가 = df_cm_call['시가'].values.tolist()
                cm_call_시가_extend = self.make_color_list(cm_call_시가)

                cm_call_피봇 = df_cm_call['피봇'].values.tolist()
                cm_call_피봇_extend = self.make_color_list(cm_call_피봇)
            else:
                pass
        else:
            pass

        df_cm_call.loc[index, '거래량'] = call_result['누적거래량']

        if comboindex == 1:

            temp = format(df_cm_call.iloc[index]['수정거래량'], ',')

            if temp != self.tableWidget_call.item(index, Option_column.OI.value).text():

                item = QTableWidgetItem(temp)
                item.setTextAlignment(Qt.AlignCenter)

                if index == df_cm_call['수정거래량'].idxmax():
                    item.setBackground(QBrush(녹색))
                else:
                    item.setBackground(QBrush(기본바탕색))

                self.tableWidget_call.setItem(index, Option_column.OI.value, item)
            else:
                pass

            temp = format(call_volume_total, ',')

            if temp != self.tableWidget_call.horizontalHeaderItem(Option_column.OI.value).text():
                item = QTableWidgetItem(temp)
                self.tableWidget_call.setHorizontalHeaderItem(Option_column.OI.value, item)
            else:
                pass
        else:

            temp = format(df_cm_call.iloc[index]['미결'], ',')

            if temp != self.tableWidget_call.item(index, Option_column.OI.value).text():

                item = QTableWidgetItem(temp)
                item.setTextAlignment(Qt.AlignCenter)
                self.tableWidget_call.setItem(index, Option_column.OI.value, item)
            else:
                pass

            temp = format(df_cm_call['미결'].sum(), ',')

            if temp != self.tableWidget_call.horizontalHeaderItem(Option_column.OI.value).text():
                item = QTableWidgetItem(temp)
                self.tableWidget_call.setHorizontalHeaderItem(Option_column.OI.value, item)
            else:
                pass        

        미결증감 = format(df_cm_call.iloc[index]['미결증감'], ',')

        if 미결증감 != self.tableWidget_call.item(index, Option_column.OID.value).text():

            item = QTableWidgetItem(미결증감)
            item.setTextAlignment(Qt.AlignCenter)

            if call_result['미결제약정증감'] < 0:
                item.setBackground(QBrush(녹색))
            else:
                item.setBackground(QBrush(기본바탕색))

            self.tableWidget_call.setItem(index, Option_column.OID.value, item)
        else:
            pass

        if df_cm_call.iloc[index]['시가'] > 0.3 and df_cm_call.iloc[index]['저가'] < df_cm_call.iloc[index]['고가']:

            if self.tableWidget_call.item(index, Option_column.시가갭.value).text() == '0.00':

                df_cm_call.loc[index, '시가갭'] = float(call_result['시가']) - df_cm_call.iloc[index]['종가']
                call_gap_percent[index] = (float(call_result['시가']) / df_cm_call.iloc[index]['종가'] - 1) * 100

                gap_str = "{0:0.2f}({1:0.0f}%)".format(df_cm_call.iloc[index]['시가갭'], call_gap_percent[index])

                item = QTableWidgetItem(gap_str)
                item.setTextAlignment(Qt.AlignCenter)
                self.tableWidget_call.setItem(index, Option_column.시가갭.value, item)
            else:
                pass

            if not call_open[index]:

                if index != atm_index:
                    self.tableWidget_call.item(index, Option_column.행사가.value).setBackground(QBrush(녹색))
                else:
                    pass

                if index > atm_index:
                    call_below_atm_count += 1
                else:
                    pass

                call_open[index] = True

                new_actval = repr(call_below_atm_count) + '/' + repr(call_open.count(True))

                if new_actval != self.tableWidget_call.horizontalHeaderItem(1).text():
                    item = QTableWidgetItem(new_actval)
                    self.tableWidget_call.setHorizontalHeaderItem(1, item)
                else:
                    pass

                if call_open.count(True) >= 1:

                    temp = call_gap_percent[:]
                    call_gap_percent_local = [value for value in temp if not math.isnan(value)]
                    call_gap_percent_local.sort()

                    print('call_gap_percent_local', call_gap_percent_local)

                    if call_gap_percent_local:
                        tmp = np.array(call_gap_percent_local)
                        mean = int(round(np.mean(tmp), 1))
                        call_str = '시가갭' + '(' + repr(mean) + '%' + ')'

                        if call_str != self.tableWidget_call.horizontalHeaderItem(Option_column.시가갭.value).text():
                            item = QTableWidgetItem(call_str)
                            self.tableWidget_call.setHorizontalHeaderItem(Option_column.시가갭.value, item)
                        else:
                            pass
                    else:
                        print('call_gap_percent_local is empty...')
                else:
                    pass
            else:
                pass

            # call OL/OH count
            if self.within_n_tick(df_cm_call.iloc[index]['시가'], df_cm_call.iloc[index]['저가'], 2) \
                    and not self.within_n_tick(df_cm_call.iloc[index]['시가'], df_cm_call.iloc[index]['고가'], 2):

                if not call_ol[index]:

                    oloh_str = '↑'

                    if oloh_str != self.tableWidget_call.item(index, Option_column.OLOH.value).text():
                        item = QTableWidgetItem("{0}".format(oloh_str))
                        item.setTextAlignment(Qt.AlignCenter)
                        item.setBackground(QBrush(적색))
                        item.setForeground(QBrush(흰색))
                        self.tableWidget_call.setItem(index, Option_column.OLOH.value, item)

                        call_ol[index] = True
                    else:
                        pass
                else:
                    pass

            elif self.within_n_tick(df_cm_call.iloc[index]['시가'], df_cm_call.iloc[index]['고가'], 2) \
                    and not self.within_n_tick(df_cm_call.iloc[index]['시가'], df_cm_call.iloc[index]['저가'], 2):

                if not call_oh[index]:

                    oloh_str = '↓'

                    if oloh_str != self.tableWidget_call.item(index, Option_column.OLOH.value).text():
                        item = QTableWidgetItem("{0}".format(oloh_str))
                        item.setTextAlignment(Qt.AlignCenter)
                        item.setBackground(QBrush(청색))
                        item.setForeground(QBrush(흰색))
                        self.tableWidget_call.setItem(index, Option_column.OLOH.value, item)

                        call_oh[index] = True
                    else:
                        pass
                else:
                    pass
            else:
                oloh_str = ''

                if oloh_str != self.tableWidget_call.item(index, Option_column.OLOH.value).text():
                    item = QTableWidgetItem("{0}".format(oloh_str))
                    item.setBackground(QBrush(기본바탕색))
                    item.setForeground(QBrush(검정색))
                    self.tableWidget_call.setItem(index, Option_column.OLOH.value, item)

                    call_ol[index] = False
                    call_oh[index] = False
                else:
                    pass

            new_oloh = repr(call_ol.count(True)) + '/' + repr(call_oh.count(True))

            if new_oloh != self.tableWidget_call.horizontalHeaderItem(2).text():
                item = QTableWidgetItem(new_oloh)
                self.tableWidget_call.setHorizontalHeaderItem(2, item)
            else:
                pass
        else:
            pass

        self.tableWidget_call.resizeColumnsToContents()
        self.tableWidget_call.setColumnWidth(0, 15)

    def put_display(self, result):

        global opt_putreal_update_counter
        global df_cm_put, df_plotdata_cm_put, df_plotdata_cm_put_volume, df_plotdata_cm_volume_cha
        global put_atm_value, put_db_percent
        global cm_put_피봇, cm_put_피봇_extend, cm_put_시가, cm_put_시가_extend
        global df_cm_put_che
        global put_volume_total
        global df_plotdata_cm_put_oi, df_plotdata_cm_oi_cha
        global cm_put_저가, cm_put_저가_extend, cm_put_고가, cm_put_고가_extend

        dt = datetime.datetime.now()

        opt_putreal_update_counter += 1

        index = cm_put_행사가.index(result['단축코드'][5:8])

        if put_scroll_begin_position <= index < put_scroll_end_position:

            # Data Update
            if result['저가'] != self.tableWidget_put.item(index, Option_column.저가.value).text():

                df_cm_put.loc[index, '저가'] = round(float(result['저가']), 2)

                item = QTableWidgetItem(result['저가'])
                item.setTextAlignment(Qt.AlignCenter)
                #item.setBackground(QBrush(옅은회색))
                self.tableWidget_put.setItem(index, Option_column.저가.value, item)

                str = '[{0:02d}:{1:02d}:{2:02d}] Put {3} 저가갱신됨 !!!\r'.format(delta_hour, delta_minute, delta_sec,
                                                                              result['저가'])
                self.textBrowser.append(str)

                cm_put_저가 = df_cm_put['저가'].values.tolist()
                cm_put_저가_extend = self.make_color_list(cm_put_저가)

                item = QTableWidgetItem("{0:0.2f}".format(float(result['고가']) - float(result['저가'])))
                item.setTextAlignment(Qt.AlignCenter)
                self.tableWidget_put.setItem(index, Option_column.진폭.value, item)
            else:
                pass

            if result['고가'] != self.tableWidget_put.item(index, Option_column.고가.value).text():

                df_cm_put.loc[index, '고가'] = round(float(result['고가']), 2)

                item = QTableWidgetItem(result['고가'])
                item.setTextAlignment(Qt.AlignCenter)
                #item.setBackground(QBrush(옅은회색))
                self.tableWidget_put.setItem(index, Option_column.고가.value, item)

                str = '[{0:02d}:{1:02d}:{2:02d}] Put {3} 고가갱신됨 !!!\r'.format(delta_hour, delta_minute, delta_sec,
                                                                             result['고가'])
                self.textBrowser.append(str)

                cm_put_고가 = df_cm_put['고가'].values.tolist()
                cm_put_고가_extend = self.make_color_list(cm_put_고가)

                item = QTableWidgetItem("{0:0.2f}".format(float(result['고가']) - float(result['저가'])))
                item.setTextAlignment(Qt.AlignCenter)
                self.tableWidget_put.setItem(index, Option_column.진폭.value, item)
            else:
                pass

            if result['현재가'] != self.tableWidget_put.item(index, Option_column.현재가.value).text():

                df_cm_put.loc[index, '현재가'] = round(float(result['현재가']), 2)
                df_plotdata_cm_put.iloc[index][opt_x_idx + 1] = float(result['현재가'])

                item = QTableWidgetItem(result['현재가'])
                item.setTextAlignment(Qt.AlignCenter)
                item.setBackground(QBrush(기본바탕색))

                if float(result['시가']) < float(result['현재가']):
                    item.setForeground(QBrush(적색))
                elif float(result['시가']) > float(result['현재가']):
                    item.setForeground(QBrush(청색))
                else:
                    item.setForeground(QBrush(검정색))

                self.tableWidget_put.setItem(index, Option_column.현재가.value, item)

                if float(result['현재가']) <= df_cm_put.iloc[index]['시가갭']:

                    수정거래량 = result['누적거래량'] * float(result['현재가'])
                    매도누적체결량 = result['매도누적체결량'] * float(result['현재가'])
                    매수누적체결량 = result['매수누적체결량'] * float(result['현재가'])
                    미결 = result['미결제약정수량'] * float(result['현재가'])
                    미결증감 = result['미결제약정증감'] * float(result['현재가'])

                    if not overnight:

                        매도누적체결건수 = result['매도누적체결건수'] * float(result['현재가'])
                        매수누적체결건수 = result['매수누적체결건수'] * float(result['현재가'])
                    else:
                        pass
                else:
                    수정거래량 = result['누적거래량'] * (float(result['현재가']) - df_cm_put.iloc[index]['시가갭'])
                    매도누적체결량 = result['매도누적체결량'] * (float(result['현재가']) - df_cm_put.iloc[index]['시가갭'])
                    매수누적체결량 = result['매수누적체결량'] * (float(result['현재가']) - df_cm_put.iloc[index]['시가갭'])
                    미결 = result['미결제약정수량'] * (float(result['현재가']) - df_cm_put.iloc[index]['시가갭'])
                    미결증감 = result['미결제약정증감'] * (float(result['현재가']) - df_cm_put.iloc[index]['시가갭'])

                    if not overnight:

                        매도누적체결건수 = result['매도누적체결건수'] * (float(result['현재가']) - df_cm_put.iloc[index]['시가갭'])
                        매수누적체결건수 = result['매수누적체결건수'] * (float(result['현재가']) - df_cm_put.iloc[index]['시가갭'])
                    else:
                        pass

                df_cm_put.loc[index, '수정거래량'] = int(수정거래량)

                #df_plotdata_cm_put_volume.iloc[0][opt_x_idx + 1] = df_cm_put['수정거래량'].sum()
                #df_plotdata_cm_volume_cha.iloc[0][opt_x_idx + 1] = df_cm_call['수정거래량'].sum() - df_cm_put['수정거래량'].sum()
                #put_volume_total = df_cm_put['수정거래량'].sum()

                df_cm_put.loc[index, '미결'] = int(미결)
                df_cm_put.loc[index, '미결증감'] = int(미결증감)

                df_plotdata_cm_put_oi.iloc[0][opt_x_idx + 1] = df_cm_put['미결'].sum() - put_oi_percent_init_value
                df_plotdata_cm_oi_cha.iloc[0][opt_x_idx + 1] = (df_cm_call['미결'].sum() - call_oi_percent_init_value) - (df_cm_put['미결'].sum() - put_oi_percent_init_value)

                df_cm_put_che.loc[index, '매도누적체결량'] = int(매도누적체결량)
                df_cm_put_che.loc[index, '매수누적체결량'] = int(매수누적체결량)

                if not overnight:

                    df_cm_put_che.loc[index, '매도누적체결건수'] = int(매도누적체결건수)
                    df_cm_put_che.loc[index, '매수누적체결건수'] = int(매수누적체결건수)
                else:
                    pass

                put_volume_total = df_cm_put_che['매수누적체결량'].sum() - df_cm_put_che['매도누적체결량'].sum()

                df_plotdata_cm_put_volume.iloc[0][opt_x_idx + 1] = put_volume_total

                df_plotdata_cm_volume_cha.iloc[0][opt_x_idx + 1] = abs(call_volume_total) + abs(put_volume_total)

                if index == atm_index:

                    put_atm_value = float(result['현재가'])
                else:
                    pass

                if float(result['시가']) > 0.3 and float(result['저가']) < float(result['고가']):

                    put_db_percent[index] = (float(result['현재가']) / float(result['시가']) - 1) * 100

                    gap_str = "{0:0.0f}({1:0.0f}%)".format(
                        (float(result['현재가']) - float(result['시가'])) * 100, put_db_percent[index])

                    if gap_str != self.tableWidget_put.setItem(index, Option_column.대비.value, item).text():

                        item = QTableWidgetItem(gap_str)
                        item.setTextAlignment(Qt.AlignCenter)
                        self.tableWidget_put.setItem(index, Option_column.대비.value, item)
                    else:
                        pass
                else:
                    pass
            else:
                pass

            # 현재가가 시가임
            if result['현재가'] == result['저가'] and result['현재가'] == result['고가']:

                if result['시가'] != self.tableWidget_put.item(index, Option_column.시가.value).text():

                    str = '[{0:02d}:{1:02d}:{2:02d}] Put in Window 시가 {3} Open...\r'. \
                        format(dt.hour, dt.minute, dt.second, result['시가'])

                    self.textBrowser.append(str)

                    if df_cm_put.iloc[index]['종가'] > 0:

                        df_cm_put.loc[index, '시가'] = round(float(result['시가']), 2)
                        df_cm_put.loc[index, '시가갭'] = float(result['시가']) - df_cm_put.iloc[index]['종가']
                        df_plotdata_cm_put.iloc[index][1] = float(result['시가'])

                        item = QTableWidgetItem(result['시가'])
                        item.setTextAlignment(Qt.AlignCenter)

                        if float(result['시가']) > df_cm_put.iloc[index]['종가']:
                            item.setForeground(QBrush(적색))
                        elif float(result['시가']) < df_cm_put.iloc[index]['종가']:
                            item.setForeground(QBrush(청색))
                        else:
                            item.setForeground(QBrush(검정색))

                        self.tableWidget_put.setItem(index, Option_column.시가.value, item)

                        cm_put_시가 = df_cm_put['시가'].values.tolist()
                        cm_put_시가_extend = self.make_color_list(cm_put_시가)
                    else:
                        pass

                    if df_cm_put.iloc[index]['시가'] > 0:

                        temp = self.calc_pivot(df_cm_put.iloc[index]['전저'],
                                                                     df_cm_put.iloc[index]['전고'],
                                                                     df_cm_put.iloc[index]['종가'],
                                                                     df_cm_put.iloc[index]['시가'])

                        df_cm_put.loc[index, '피봇'] = round(temp, 2)

                        item = QTableWidgetItem("{0:0.2f}".format(df_cm_put.iloc[index]['피봇']))
                        item.setTextAlignment(Qt.AlignCenter)
                        self.tableWidget_put.setItem(index, Option_column.피봇.value, item)

                        cm_put_피봇 = df_cm_put['피봇'].values.tolist()
                        cm_put_피봇_extend = self.make_color_list(cm_put_피봇)
                    else:
                        pass
                else:
                    pass
            else:
                pass
        else:

            if float(result['시가']) > 0.3:

                if result['저가'] != self.tableWidget_put.item(index, Option_column.저가.value).text():

                    df_cm_put.loc[index, '저가'] = round(float(result['저가']), 2)

                    item = QTableWidgetItem(result['저가'])
                    item.setTextAlignment(Qt.AlignCenter)
                    item.setBackground(QBrush(옅은회색))
                    self.tableWidget_put.setItem(index, Option_column.저가.value, item)

                    item = QTableWidgetItem("{0:0.2f}".format(float(result['고가']) - float(result['저가'])))
                    item.setTextAlignment(Qt.AlignCenter)
                    self.tableWidget_put.setItem(index, Option_column.진폭.value, item)
                else:
                    pass

                if result['고가'] != self.tableWidget_put.item(index, Option_column.고가.value).text():

                    df_cm_put.loc[index, '고가'] = round(float(result['고가']), 2)

                    item = QTableWidgetItem(result['고가'])
                    item.setTextAlignment(Qt.AlignCenter)
                    item.setBackground(QBrush(옅은회색))
                    self.tableWidget_put.setItem(index, Option_column.고가.value, item)

                    item = QTableWidgetItem("{0:0.2f}".format(float(result['고가']) - float(result['저가'])))
                    item.setTextAlignment(Qt.AlignCenter)
                    self.tableWidget_put.setItem(index, Option_column.진폭.value, item)
                else:
                    pass

                if result['현재가'] != self.tableWidget_put.item(index, Option_column.현재가.value).text():

                    df_cm_put.loc[index, '현재가'] = round(float(result['현재가']), 2)
                    df_plotdata_cm_put.iloc[index][opt_x_idx + 1] = float(result['현재가'])

                    item = QTableWidgetItem(result['현재가'])
                    item.setTextAlignment(Qt.AlignCenter)
                    item.setBackground(QBrush(기본바탕색))
                    self.tableWidget_put.setItem(index, Option_column.현재가.value, item)

                    if float(result['저가']) < float(result['고가']):

                        put_db_percent[index] = (float(result['현재가']) / float(result['시가']) - 1) * 100

                        gap_str = "{0:0.0f}({1:0.0f}%)".format(
                            (float(result['현재가']) - float(result['시가'])) * 100, put_db_percent[index])

                        if gap_str != self.tableWidget_put.setItem(index, Option_column.대비.value, item).text():

                            item = QTableWidgetItem(gap_str)
                            item.setTextAlignment(Qt.AlignCenter)
                            self.tableWidget_put.setItem(index, Option_column.대비.value, item)
                        else:
                            pass
                    else:
                        pass
                else:
                    pass

                # 현재가가 시가임
                if result['현재가'] == result['저가'] and result['현재가'] == result['고가']:

                    if result['시가'] != self.tableWidget_put.item(index, Option_column.시가.value).text():

                        str = '[{0:02d}:{1:02d}:{2:02d}] Put out Window 시가 {3} Open...\r'. \
                            format(dt.hour, dt.minute, dt.second, result['시가'])

                        self.textBrowser.append(str)

                        if df_cm_put.iloc[index]['종가'] > 0:

                            df_cm_put.loc[index, '시가'] = round(float(result['시가']), 2)
                            df_cm_put.loc[index, '시가갭'] = float(result['시가']) - df_cm_put.iloc[index]['종가']
                            df_plotdata_cm_put.iloc[index][1] = float(result['시가'])

                            item = QTableWidgetItem(result['시가'])
                            item.setTextAlignment(Qt.AlignCenter)

                            if float(result['시가']) > df_cm_put.iloc[index]['종가']:
                                item.setForeground(QBrush(적색))
                            elif float(result['시가']) < df_cm_put.iloc[index]['종가']:
                                item.setForeground(QBrush(청색))
                            else:
                                item.setForeground(QBrush(검정색))

                            self.tableWidget_put.setItem(index, Option_column.시가.value, item)

                            cm_put_시가 = df_cm_put['시가'].values.tolist()
                            cm_put_시가_extend = self.make_color_list(cm_put_시가)
                        else:
                            pass

                        if df_cm_put.iloc[index]['시가'] > 0:

                            temp = self.calc_pivot(df_cm_put.iloc[index]['전저'],
                                                                         df_cm_put.iloc[index]['전고'],
                                                                         df_cm_put.iloc[index]['종가'],
                                                                         df_cm_put.iloc[index]['시가'])

                            df_cm_put.loc[index, '피봇'] = round(temp, 2)

                            item = QTableWidgetItem("{0:0.2f}".format(df_cm_put.iloc[index]['피봇']))
                            item.setTextAlignment(Qt.AlignCenter)
                            self.tableWidget_put.setItem(index, Option_column.피봇.value, item)

                            cm_put_피봇 = df_cm_put['피봇'].values.tolist()
                            cm_put_피봇_extend = self.make_color_list(cm_put_피봇)
                        else:
                            pass
                    else:
                        pass
                else:
                    pass
            else:
                pass

    def put_post_processing(self):

        global put_above_atm_count

        global put_open, put_ol, put_oh
        global put_gap_percent
        global df_plotdata_cm_put
        global cm_put_시가, cm_put_시가_extend, cm_put_피봇, cm_put_피봇_extend

        index = cm_put_행사가.index(put_result['단축코드'][5:8])

        if put_result['시가'] != self.tableWidget_put.item(index, Option_column.시가.value).text():

            if float(put_result['시가']) > 0 and df_cm_put.iloc[index]['종가'] > 0:

                df_cm_put.loc[index, '시가'] = round(float(put_result['시가']), 2)
                df_cm_put.loc[index, '시가갭'] = float(put_result['시가']) - df_cm_put.iloc[index]['종가']
                df_plotdata_cm_put.iloc[index][1] = float(put_result['시가'])

                item = QTableWidgetItem(put_result['시가'])
                item.setTextAlignment(Qt.AlignCenter)

                if float(put_result['시가']) > df_cm_put.iloc[index]['종가']:
                    item.setForeground(QBrush(적색))
                elif float(put_result['시가']) < df_cm_put.iloc[index]['종가']:
                    item.setForeground(QBrush(청색))
                else:
                    item.setForeground(QBrush(검정색))

                self.tableWidget_put.setItem(index, Option_column.시가.value, item)

                df_cm_put.loc[index, '시가갭'] = float(put_result['시가']) - df_cm_put.iloc[index]['종가']

                if float(put_result['시가']) > 0.3:

                    put_gap_percent[index] = (float(put_result['시가']) / df_cm_put.iloc[index]['종가'] - 1) * 100
                    gap_str = "{0:0.2f}({1:0.0f}%)".format(df_cm_put.iloc[index]['시가갭'], put_gap_percent[index])
                else:
                    gap_str = "{0:0.2f}".format(df_cm_put.iloc[index]['시가갭'])

                if gap_str != self.tableWidget_put.item(index, Option_column.시가갭.value).text():

                    item = QTableWidgetItem(gap_str)
                    item.setTextAlignment(Qt.AlignCenter)
                    self.tableWidget_put.setItem(index, Option_column.시가갭.value, item)
                else:
                    pass

                temp = self.calc_pivot(df_cm_put.iloc[index]['전저'],
                                                             df_cm_put.iloc[index]['전고'],
                                                             df_cm_put.iloc[index]['종가'],
                                                             df_cm_put.iloc[index]['시가'])

                df_cm_put.loc[index, '피봇'] = round(temp, 2)

                item = QTableWidgetItem("{0:0.2f}".format(df_cm_put.iloc[index]['피봇']))
                item.setTextAlignment(Qt.AlignCenter)
                self.tableWidget_put.setItem(index, Option_column.피봇.value, item)

                cm_put_시가 = df_cm_put['시가'].values.tolist()
                cm_put_시가_extend = self.make_color_list(cm_put_시가)

                cm_put_피봇 = df_cm_put['피봇'].values.tolist()
                cm_put_피봇_extend = self.make_color_list(cm_put_피봇)
            else:
                pass
        else:
            pass

        df_cm_put.loc[index, '거래량'] = put_result['누적거래량']

        if comboindex == 1:

            temp = format(df_cm_put.iloc[index]['수정거래량'], ',')

            if temp != self.tableWidget_put.item(index, Option_column.OI.value).text():

                item = QTableWidgetItem(temp)
                item.setTextAlignment(Qt.AlignCenter)

                if index == df_cm_put['수정거래량'].idxmax():
                    item.setBackground(QBrush(녹색))
                else:
                    item.setBackground(QBrush(기본바탕색))

                self.tableWidget_put.setItem(index, Option_column.OI.value, item)
            else:
                pass

            temp = format(put_volume_total, ',')

            if temp != self.tableWidget_put.horizontalHeaderItem(Option_column.OI.value).text():
                item = QTableWidgetItem(temp)
                self.tableWidget_put.setHorizontalHeaderItem(Option_column.OI.value, item)
            else:
                pass
        else:

            temp = format(df_cm_put.iloc[index]['미결'], ',')

            if temp != self.tableWidget_put.item(index, Option_column.OI.value).text():

                item = QTableWidgetItem(temp)
                item.setTextAlignment(Qt.AlignCenter)
                self.tableWidget_put.setItem(index, Option_column.OI.value, item)
            else:
                pass

            temp = format(df_cm_put['미결'].sum(), ',')

            if temp != self.tableWidget_put.horizontalHeaderItem(Option_column.OI.value).text():
                item = QTableWidgetItem(temp)
                self.tableWidget_put.setHorizontalHeaderItem(Option_column.OI.value, item)
            else:
                pass        

        미결증감 = format(df_cm_put.iloc[index]['미결증감'], ',')

        if 미결증감 != self.tableWidget_put.item(index, Option_column.OID.value).text():

            item = QTableWidgetItem(미결증감)
            item.setTextAlignment(Qt.AlignCenter)

            if put_result['미결제약정증감'] < 0:
                item.setBackground(QBrush(녹색))
            else:
                item.setBackground(QBrush(기본바탕색))

            self.tableWidget_put.setItem(index, Option_column.OID.value, item)
        else:
            pass

        if df_cm_put.iloc[index]['시가'] > 0.3 and df_cm_put.iloc[index]['저가'] < df_cm_put.iloc[index]['고가']:

            if self.tableWidget_put.item(index, Option_column.시가갭.value).text() == '0.00':

                df_cm_put.loc[index, '시가갭'] = float(put_result['시가']) - df_cm_put.iloc[index]['종가']
                put_gap_percent[index] = (float(put_result['시가']) / df_cm_put.iloc[index]['종가'] - 1) * 100

                gap_str = "{0:0.2f}({1:0.0f}%)".format(df_cm_put.iloc[index]['시가갭'], put_gap_percent[index])

                item = QTableWidgetItem(gap_str)
                item.setTextAlignment(Qt.AlignCenter)
                self.tableWidget_put.setItem(index, Option_column.시가갭.value, item)
            else:
                pass

            if not put_open[index]:

                if index != atm_index:
                    self.tableWidget_put.item(index, Option_column.행사가.value).setBackground(QBrush(녹색))
                else:
                    pass

                if index < atm_index:
                    put_above_atm_count += 1
                else:
                    pass

                put_open[index] = True

                new_actval = repr(put_above_atm_count) + '/' + repr(put_open.count(True))

                if new_actval != self.tableWidget_put.horizontalHeaderItem(1).text():
                    item = QTableWidgetItem(new_actval)
                    self.tableWidget_put.setHorizontalHeaderItem(1, item)
                else:
                    pass

                if put_open.count(True) >= 1:

                    temp = put_gap_percent[:]
                    put_gap_percent_local = [value for value in temp if not math.isnan(value)]
                    put_gap_percent_local.sort()

                    if put_gap_percent_local:
                        tmp = np.array(put_gap_percent_local)
                        mean = int(round(np.mean(tmp), 1))
                        put_str = '시가갭' + '(' + repr(mean) + '%' + ')'

                        if put_str != self.tableWidget_put.horizontalHeaderItem(Option_column.시가갭.value).text():
                            item = QTableWidgetItem(put_str)
                            self.tableWidget_put.setHorizontalHeaderItem(Option_column.시가갭.value, item)
                        else:
                            pass
                    else:
                        print('put_gap_percent_local is empty...')
                else:
                    pass
            else:
                pass

            # put OL/OH count
            if self.within_n_tick(df_cm_put.iloc[index]['시가'], df_cm_put.iloc[index]['저가'], 2) \
                    and not self.within_n_tick(df_cm_put.iloc[index]['시가'], df_cm_put.iloc[index]['고가'], 2):

                if not put_ol[index]:

                    oloh_str = '↑'

                    if oloh_str != self.tableWidget_put.item(index, Option_column.OLOH.value).text():
                        item = QTableWidgetItem("{0}".format(oloh_str))
                        item.setTextAlignment(Qt.AlignCenter)
                        item.setBackground(QBrush(청색))
                        item.setForeground(QBrush(흰색))
                        self.tableWidget_put.setItem(index, Option_column.OLOH.value, item)

                        put_ol[index] = True
                    else:
                        pass
                else:
                    pass

            elif self.within_n_tick(df_cm_put.iloc[index]['시가'], df_cm_put.iloc[index]['고가'], 2) \
                    and not self.within_n_tick(df_cm_put.iloc[index]['시가'], df_cm_put.iloc[index]['저가'], 2):

                if not put_oh[index]:

                    oloh_str = '↓'

                    if oloh_str != self.tableWidget_put.item(index, Option_column.OLOH.value).text():
                        item = QTableWidgetItem("{0}".format(oloh_str))
                        item.setTextAlignment(Qt.AlignCenter)
                        item.setBackground(QBrush(적색))
                        item.setForeground(QBrush(흰색))
                        self.tableWidget_put.setItem(index, Option_column.OLOH.value, item)

                        put_oh[index] = True
                    else:
                        pass
                else:
                    pass
            else:
                oloh_str = ''

                if oloh_str != self.tableWidget_put.item(index, Option_column.OLOH.value).text():
                    item = QTableWidgetItem("{0}".format(oloh_str))
                    item.setBackground(QBrush(기본바탕색))
                    item.setForeground(QBrush(검정색))
                    self.tableWidget_put.setItem(index, Option_column.OLOH.value, item)

                    put_ol[index] = False
                    put_oh[index] = False
                else:
                    pass

            new_oloh = repr(put_ol.count(True)) + '/' + repr(put_oh.count(True))

            if new_oloh != self.tableWidget_put.horizontalHeaderItem(2).text():
                item = QTableWidgetItem(new_oloh)
                self.tableWidget_put.setHorizontalHeaderItem(2, item)
            else:
                pass
        else:
            pass

        self.tableWidget_put.resizeColumnsToContents()
        self.tableWidget_put.setColumnWidth(0, 15)

    def quote_display(self):

        global call_quote, put_quote

        call_quote = df_cm_call_ho.sum()
        put_quote = df_cm_put_ho.sum()

        if call_quote['매도건수'] > 0:
            call_count_ratio = call_quote['매수건수'] / call_quote['매도건수']
        else:
            call_count_ratio = 0

        if call_quote['매도잔량'] > 0:
            call_remainder_ratio = call_quote['매수잔량'] / call_quote['매도잔량']
        else:
            call_remainder_ratio = 0

        if put_quote['매도건수'] > 0:
            put_count_ratio = put_quote['매수건수'] / put_quote['매도건수']
        else:
            put_count_ratio = 0

        if put_quote['매도잔량'] > 0:
            put_remainder_ratio = put_quote['매수잔량'] / put_quote['매도잔량']
        else:
            put_remainder_ratio = 0

        temp = (call_quote['매수건수'] + call_quote['매도건수']) - (put_quote['매수건수'] + put_quote['매도건수'])
        건수차 = format(temp, ',')

        temp = (call_quote['매수잔량'] + call_quote['매도잔량']) - (put_quote['매수잔량'] + put_quote['매도잔량'])
        잔량차 = format(temp, ',')

        item_str = "{0:0.2f}/{1:0.2f}\n({2}/{3})".format(abs(call_count_ratio - put_count_ratio),
                                                         abs(call_remainder_ratio - put_remainder_ratio),
                                                         건수차, 잔량차)

        if item_str != self.tableWidget_quote.item(0, 12).text():

            item = QTableWidgetItem(item_str)
            item.setTextAlignment(Qt.AlignCenter)

            if call_count_ratio > put_count_ratio and call_remainder_ratio > put_remainder_ratio:
                item.setBackground(QBrush(적색))
                item.setForeground(QBrush(흰색))
            elif call_count_ratio < put_count_ratio and call_remainder_ratio < put_remainder_ratio:
                item.setBackground(QBrush(청색))
                item.setForeground(QBrush(흰색))
            else:
                item.setBackground(QBrush(기본바탕색))
                item.setForeground(QBrush(검정색))

            self.tableWidget_quote.setItem(0, 12, item)
        else:
            pass

        temp = call_quote['매수건수'] + call_quote['매도건수']
        건수합 = format(temp, ',')

        item_str = "{0:0.2f}\n({1})".format(call_count_ratio, 건수합)

        if item_str != self.tableWidget_quote.item(0, 8).text():

            item = QTableWidgetItem(item_str)
            item.setTextAlignment(Qt.AlignCenter)
            self.tableWidget_quote.setItem(0, 8, item)
        else:
            pass

        temp = call_quote['매수잔량'] + call_quote['매도잔량']
        잔량합 = format(temp, ',')

        item_str = "{0:0.2f}\n({1})".format(call_remainder_ratio, 잔량합)

        if item_str != self.tableWidget_quote.item(0, 9).text():

            item = QTableWidgetItem(item_str)
            item.setTextAlignment(Qt.AlignCenter)
            self.tableWidget_quote.setItem(0, 9, item)
        else:
            pass

        temp = put_quote['매수건수'] + put_quote['매도건수']
        건수합 = format(temp, ',')

        item_str = "{0:0.2f}\n({1})".format(put_count_ratio, 건수합)

        if item_str != self.tableWidget_quote.item(0, 10).text():

            item = QTableWidgetItem(item_str)
            item.setTextAlignment(Qt.AlignCenter)
            self.tableWidget_quote.setItem(0, 10, item)
        else:
            pass

        temp = put_quote['매수잔량'] + put_quote['매도잔량']
        잔량합 = format(temp, ',')

        item_str = "{0:0.2f}\n({1})".format(put_remainder_ratio, 잔량합)

        if item_str != self.tableWidget_quote.item(0, 11).text():

            item = QTableWidgetItem(item_str)
            item.setTextAlignment(Qt.AlignCenter)
            self.tableWidget_quote.setItem(0, 11, item)
        else:
            pass

    def call_quote_display(self):

        global call_quote

        call_quote = df_cm_call_ho.sum()

        매수건수 = format(call_quote['매수건수'], ',')

        if 매수건수 != self.tableWidget_quote.item(0, 0).text():
            item = QTableWidgetItem(매수건수)
            item.setTextAlignment(Qt.AlignCenter)
            self.tableWidget_quote.setItem(0, 0, item)
        else:
            pass

        매도건수 = format(call_quote['매도건수'], ',')

        if 매도건수 != self.tableWidget_quote.item(0, 1).text():
            item = QTableWidgetItem(매도건수)
            item.setTextAlignment(Qt.AlignCenter)
            self.tableWidget_quote.setItem(0, 1, item)
        else:
            pass

        매수잔량 = format(call_quote['매수잔량'], ',')

        if 매수잔량 != self.tableWidget_quote.item(0, 2).text():
            item = QTableWidgetItem(매수잔량)
            item.setTextAlignment(Qt.AlignCenter)
            self.tableWidget_quote.setItem(0, 2, item)
        else:
            pass

        매도잔량 = format(call_quote['매도잔량'], ',')

        if 매도잔량 != self.tableWidget_quote.item(0, 3).text():
            item = QTableWidgetItem(매도잔량)
            item.setTextAlignment(Qt.AlignCenter)
            self.tableWidget_quote.setItem(0, 3, item)
        else:
            pass

    def call_che_display(self):

        global call_che

        call_che = df_cm_call_che.sum()

        매수잔량 = format(call_che['매수누적체결량'], ',')
        매도잔량 = format(call_che['매도누적체결량'], ',')

        if 매수잔량 != self.tableWidget_quote.item(0, 2).text():
            item = QTableWidgetItem(매수잔량)
            item.setTextAlignment(Qt.AlignCenter)

            if call_che['매수누적체결량'] > call_che['매도누적체결량']:

                item.setBackground(QBrush(적색))
                item.setForeground(QBrush(흰색))
            elif call_che['매수누적체결량'] < call_che['매도누적체결량']:

                item.setBackground(QBrush(청색))
                item.setForeground(QBrush(흰색))
            else:
                item.setBackground(QBrush(기본바탕색))
                item.setForeground(QBrush(검정색))

            self.tableWidget_quote.setItem(0, 2, item)
        else:
            pass

        '''
        if call_che['매도누적체결량'] > 0:

            temp = (call_che['매수누적체결량'] / call_che['매도누적체결량']) * 100
        else:
            temp = 0
        '''

        temp = format(call_che['매수누적체결량'] - call_che['매도누적체결량'], ',')
        item_str = "{0}\n({1})".format(매도잔량, temp)

        if item_str != self.tableWidget_quote.item(0, 3).text():
            item = QTableWidgetItem(item_str)
            item.setTextAlignment(Qt.AlignCenter)

            if call_che['매수누적체결량'] > call_che['매도누적체결량']:

                item.setBackground(QBrush(적색))
                item.setForeground(QBrush(흰색))
            elif call_che['매수누적체결량'] < call_che['매도누적체결량']:

                item.setBackground(QBrush(청색))
                item.setForeground(QBrush(흰색))
            else:
                item.setBackground(QBrush(기본바탕색))
                item.setForeground(QBrush(검정색))

            self.tableWidget_quote.setItem(0, 3, item)
        else:
            pass

        if not overnight:

            매수건수 = format(call_che['매수누적체결건수'], ',')

            if 매수건수 != self.tableWidget_quote.item(0, 0).text():
                item = QTableWidgetItem(매수건수)
                item.setTextAlignment(Qt.AlignCenter)
                self.tableWidget_quote.setItem(0, 0, item)
            else:
                pass

            매도건수 = format(call_che['매도누적체결건수'], ',')

            if 매도건수 != self.tableWidget_quote.item(0, 1).text():
                item = QTableWidgetItem(매도건수)
                item.setTextAlignment(Qt.AlignCenter)
                self.tableWidget_quote.setItem(0, 1, item)
            else:
                pass
        else:
            pass

    def put_quote_display(self):

        global put_quote

        put_quote = df_cm_put_ho.sum()

        매수건수 = format(put_quote['매수건수'], ',')

        if 매수건수 != self.tableWidget_quote.item(0, 4).text():
            item = QTableWidgetItem(매수건수)
            item.setTextAlignment(Qt.AlignCenter)
            self.tableWidget_quote.setItem(0, 4, item)
        else:
            pass

        매도건수 = format(put_quote['매도건수'], ',')

        if 매도건수 != self.tableWidget_quote.item(0, 5).text():
            item = QTableWidgetItem(매도건수)
            item.setTextAlignment(Qt.AlignCenter)
            self.tableWidget_quote.setItem(0, 5, item)
        else:
            pass

        매수잔량 = format(put_quote['매수잔량'], ',')

        if 매수잔량 != self.tableWidget_quote.item(0, 6).text():
            item = QTableWidgetItem(매수잔량)
            item.setTextAlignment(Qt.AlignCenter)
            self.tableWidget_quote.setItem(0, 6, item)
        else:
            pass

        매도잔량 = format(put_quote['매도잔량'], ',')

        if 매도잔량 != self.tableWidget_quote.item(0, 7).text():
            item = QTableWidgetItem(매도잔량)
            item.setTextAlignment(Qt.AlignCenter)
            self.tableWidget_quote.setItem(0, 7, item)
        else:
            pass

    def put_che_display(self):

        global put_che

        put_che = df_cm_put_che.sum()

        매수잔량 = format(put_che['매수누적체결량'], ',')
        매도잔량 = format(put_che['매도누적체결량'], ',')

        if 매수잔량 != self.tableWidget_quote.item(0, 6).text():
            item = QTableWidgetItem(매수잔량)
            item.setTextAlignment(Qt.AlignCenter)

            if put_che['매수누적체결량'] > put_che['매도누적체결량']:

                item.setBackground(QBrush(청색))
                item.setForeground(QBrush(흰색))
            elif put_che['매수누적체결량'] < put_che['매도누적체결량']:

                item.setBackground(QBrush(적색))
                item.setForeground(QBrush(흰색))
            else:
                item.setBackground(QBrush(기본바탕색))
                item.setForeground(QBrush(검정색))

            self.tableWidget_quote.setItem(0, 6, item)
        else:
            pass

        '''
        if put_che['매도누적체결량'] > 0:

            temp = (put_che['매수누적체결량'] / put_che['매도누적체결량']) * 100
        else:
            temp = 0
        '''

        temp = format(put_che['매수누적체결량'] - put_che['매도누적체결량'], ',')
        item_str = "{0}\n({1})".format(매도잔량, temp)

        if item_str != self.tableWidget_quote.item(0, 7).text():
            item = QTableWidgetItem(item_str)
            item.setTextAlignment(Qt.AlignCenter)

            if put_che['매수누적체결량'] > put_che['매도누적체결량']:

                item.setBackground(QBrush(청색))
                item.setForeground(QBrush(흰색))
            elif put_che['매수누적체결량'] < put_che['매도누적체결량']:

                item.setBackground(QBrush(적색))
                item.setForeground(QBrush(흰색))
            else:
                item.setBackground(QBrush(기본바탕색))
                item.setForeground(QBrush(검정색))

            self.tableWidget_quote.setItem(0, 7, item)
        else:
            pass

        if not overnight:

            매수건수 = format(put_che['매수누적체결건수'], ',')

            if 매수건수 != self.tableWidget_quote.item(0, 4).text():
                item = QTableWidgetItem(매수건수)
                item.setTextAlignment(Qt.AlignCenter)
                self.tableWidget_quote.setItem(0, 4, item)
            else:
                pass

            매도건수 = format(put_che['매도누적체결건수'], ',')

            if 매도건수 != self.tableWidget_quote.item(0, 5).text():
                item = QTableWidgetItem(매도건수)
                item.setTextAlignment(Qt.AlignCenter)
                self.tableWidget_quote.setItem(0, 5, item)
            else:
                pass
        else:
            pass

    def OnReceiveRealData(self, szTrCode, result):
        try:
            global pre_start
            global atm_str, atm_index
            global atm_index_yj

            global fut_realdata

            global df_cm_call, df_cm_put
            global df_cm_call_ho, df_cm_put_ho

            global x_idx
            global df_plotdata_fut, df_plotdata_kp200
            global df_plotdata_cm_call, df_plotdata_cm_put

            global opt_callreal_update_counter, opt_putreal_update_counter
            global opt_call_ho_update_counter, opt_put_ho_update_counter
            global call_atm_value, put_atm_value
            global old_atm_index
            global ReceiveRealData

            global FUT_FOREIGNER_거래대금순매수, FUT_RETAIL_거래대금순매수, FUT_INSTITUTIONAL_거래대금순매수, FUT_STOCK_거래대금순매수, \
                FUT_BOHEOM_거래대금순매수, FUT_TOOSIN_거래대금순매수, FUT_BANK_거래대금순매수, FUT_JONGGEUM_거래대금순매수, \
                FUT_GIGEUM_거래대금순매수, FUT_GITA_거래대금순매수

            global FUT_FOREIGNER_거래대금순매수_직전대비, FUT_RETAIL_거래대금순매수_직전대비, FUT_INSTITUTIONAL_거래대금순매수_직전대비, \
                FUT_STOCK_거래대금순매수_직전대비, FUT_BOHEOM_거래대금순매수_직전대비, FUT_TOOSIN_거래대금순매수_직전대비, \
                FUT_BANK_거래대금순매수_직전대비, FUT_JONGGEUM_거래대금순매수_직전대비, FUT_GIGEUM_거래대금순매수_직전대비, \
                FUT_GITA_거래대금순매수_직전대비

            global KOSPI_FOREIGNER_거래대금순매수, KOSPI_RETAIL_거래대금순매수, KOSPI_INSTITUTIONAL_거래대금순매수, KOSPI_STOCK_거래대금순매수, \
                KOSPI_BOHEOM_거래대금순매수, KOSPI_TOOSIN_거래대금순매수, KOSPI_BANK_거래대금순매수, KOSPI_JONGGEUM_거래대금순매수, \
                KOSPI_GIGEUM_거래대금순매수, KOSPI_GITA_거래대금순매수

            global KOSPI_FOREIGNER_거래대금순매수_직전대비, KOSPI_RETAIL_거래대금순매수_직전대비, KOSPI_INSTITUTIONAL_거래대금순매수_직전대비, \
                KOSPI_STOCK_거래대금순매수_직전대비, KOSPI_BOHEOM_거래대금순매수_직전대비, KOSPI_TOOSIN_거래대금순매수_직전대비, \
                KOSPI_BANK_거래대금순매수_직전대비, KOSPI_JONGGEUM_거래대금순매수_직전대비, KOSPI_GIGEUM_거래대금순매수_직전대비, \
                KOSPI_GITA_거래대금순매수_직전대비

            global FUT_FOREIGNER_직전대비, FUT_RETAIL_직전대비, FUT_INSTITUTIONAL_직전대비, \
                KOSPI_FOREIGNER_직전대비, PROGRAM_직전대비

            global opt_x_idx

            global kp200_realdata
            global call_result, put_result
            global yoc_call_gap_percent, yoc_put_gap_percent

            global time_delta

            start_time = timeit.default_timer()

            dt = datetime.datetime.now()

            if szTrCode == 'JIF':

                str = '[{0:02d}:{1:02d}:{2:02d}] 장구분[{3}], 장상태[{4}]\r'.format(dt.hour, dt.minute, dt.second, result['장구분'], result['장상태'])
                self.textBrowser.append(str)

                # 장시작 10분전
                if result['장구분'] == '5' and result['장상태'] == '25':

                    if dt.minute == 50:
                        time_delta = dt.second - 0
                    elif dt.minute == 49:
                        time_delta = dt.second - 60
                    else:
                        pass

                    if time_delta > 0:
                        str = '[{0:02d}:{1:02d}:{2:02d}] 시스템시간이 서버시간보다 {3}초 빠릅니다.\r'.format(dt.hour, dt.minute,
                                                                    dt.second, time_delta)
                        self.textBrowser.append(str)
                    elif time_delta < 0:
                        str = '[{0:02d}:{1:02d}:{2:02d}] 시스템시간이 서버시간보다 {3}초 느립니다.\r'.format(dt.hour, dt.minute,
                                                                                dt.second, time_delta)
                        self.textBrowser.append(str)
                    else:
                        str = '[{0:02d}:{1:02d}:{2:02d}] 시스템시간과 서버시간이 같습니다.\r'.format(dt.hour, dt.minute,
                                                                                dt.second)
                        self.textBrowser.append(str)

                    str = '[{0:02d}:{1:02d}:{2:02d}] 장시작 10분전입니다.\r'.format(dt.hour, dt.minute, dt.second)
                    self.textBrowser.append(str)

                    if not START_ON:
                        self.AddCode()
                        str = '[{0:02d}:{1:02d}:{2:02d}] Auto Start...\r'.format(dt.hour, dt.minute, dt.second)
                        self.textBrowser.append(str)

                        pre_start = True
                    else:
                        pass

                # 현물장 시작 10초전
                elif result['장구분'] == '1' and result['장상태'] == '22':

                    # 지수옵션 예상체결 요청취소(안하면 시작시 지연발생함)
                    self.YOC.UnadviseRealData()

                    str = '[{0:02d}:{1:02d}:{2:02d}] 지수옵션 예상체결 요청을 취소합니다.\r'.format(dt.hour, dt.minute, dt.second)
                    self.textBrowser.append(str)

                    str = '[{0:02d}:{1:02d}:{2:02d}] 현물장 시작 10초전입니다.\r'.format(dt.hour, dt.minute, dt.second)
                    self.textBrowser.append(str)

                # 선물장 시작 10초전
                elif result['장구분'] == '5' and result['장상태'] == '22':

                    # 지수옵션 예상체결 요청취소(안하면 시작시 지연발생함)
                    self.YOC.UnadviseRealData()

                    str = '[{0:02d}:{1:02d}:{2:02d}] 지수옵션 예상체결 요청을 취소합니다.\r'.format(dt.hour, dt.minute, dt.second)
                    self.textBrowser.append(str)

                    # 지수선물 예상체결 요청취소
                    self.YFC.UnadviseRealData()

                    str = '[{0:02d}:{1:02d}:{2:02d}] 지수선물 예상체결 요청을 취소합니다.\r'.format(dt.hour, dt.minute, dt.second)
                    self.textBrowser.append(str)

                    # KOSPI 예상체결 요청취소
                    self.YS3.UnadviseRealData()

                    str = '[{0:02d}:{1:02d}:{2:02d}] KOSPI 예상체결 요청을 취소합니다.\r'.format(dt.hour, dt.minute, dt.second)
                    self.textBrowser.append(str)
                    '''
                    # FUTURES/KOSPI200 예상지수 요청취소
                    self.YJ.UnadviseRealData()

                    str = '[{0:02d}:{1:02d}:{2:02d}] FUTURES/KOSPI200 예상지수 요청을 취소합니다.\r'.format(dt.hour, 
                                                                            dt.minute, dt.second)
                    self.textBrowser.append(str)
                    '''
                    str = '[{0:02d}:{1:02d}:{2:02d}] 선물장 시작 10초전입니다.\r'.format(dt.hour, dt.minute, dt.second)
                    self.textBrowser.append(str)

                # 주간 선물/옵션장 시작
                elif result['장구분'] == '5' and result['장상태'] == '21':

                    if dt.minute == 0:
                        time_delta = dt.second - 0
                    elif dt.minute == 59:
                        time_delta = dt.second - 60
                    else:
                        pass

                    pre_start = False

                    str = '[{0:02d}:{1:02d}:{2:02d}] Time Delta = {3}초\r'.format(dt.hour, dt.minute, dt.second, time_delta)
                    self.textBrowser.append(str)

                    str = '[{0:02d}:{1:02d}:{2:02d}] 주간장이 시작됩니다.\r'.format(dt.hour, dt.minute, dt.second)
                    self.textBrowser.append(str)

                    # 9시 1분 KP200 시가갱신을 위해 값을 클리어
                    '''
                    temp = 0.0

                    item = QTableWidgetItem("{0:0.2f}".format(temp))
                    item.setTextAlignment(Qt.AlignCenter)
                    self.tableWidget_fut.setItem(2, Futures_column.시가.value, item)
                    '''

                # 야간 선물장 시작
                elif result['장구분'] == '7' and result['장상태'] == '21':

                    if dt.minute == 0:
                        time_delta = dt.second - 0
                    elif dt.minute == 59:
                        time_delta = dt.second - 60
                    else:
                        pass

                    if time_delta > 0:
                        str = '[{0:02d}:{1:02d}:{2:02d}] 시스템시간이 서버시간보다 {3}초 빠릅니다.\r'.format(dt.hour, dt.minute,
                                                                    dt.second, time_delta)
                        self.textBrowser.append(str)
                    elif time_delta < 0:
                        str = '[{0:02d}:{1:02d}:{2:02d}] 시스템시간이 서버시간보다 {3}초 느립니다.\r'.format(dt.hour, dt.minute,
                                                                                dt.second, time_delta)
                        self.textBrowser.append(str)
                    else:
                        str = '[{0:02d}:{1:02d}:{2:02d}] 시스템시간과 서버시간이 같습니다.\r'.format(dt.hour, dt.minute,
                                                                                dt.second)
                        self.textBrowser.append(str)

                    str = '[{0:02d}:{1:02d}:{2:02d}] 야간 선물장이 시작됩니다.\r'.format(dt.hour, dt.minute, dt.second)
                    self.textBrowser.append(str)

                    if not ReceiveRealData:
                        #self.timer.stop()
                        ReceiveRealData = True
                        print('All Timer is stopped !!!')
                    else:
                        pass

                # 야간 옵션장 시작
                elif result['장구분'] == '8' and result['장상태'] == '21':

                    if dt.minute == 0:
                        time_delta = dt.second - 0
                    elif dt.minute == 59:
                        time_delta = dt.second - 60
                    else:
                        pass

                    if time_delta > 0:
                        str = '[{0:02d}:{1:02d}:{2:02d}] 시스템시간이 서버시간보다 {3}초 빠릅니다.\r'.format(dt.hour, dt.minute,
                                                                    dt.second, time_delta)
                        self.textBrowser.append(str)
                    elif time_delta < 0:
                        str = '[{0:02d}:{1:02d}:{2:02d}] 시스템시간이 서버시간보다 {3}초 느립니다.\r'.format(dt.hour, dt.minute,
                                                                                dt.second, time_delta)
                        self.textBrowser.append(str)
                    else:
                        str = '[{0:02d}:{1:02d}:{2:02d}] 시스템시간과 서버시간이 같습니다.\r'.format(dt.hour, dt.minute,
                                                                                dt.second)
                        self.textBrowser.append(str)

                    str = '[{0:02d}:{1:02d}:{2:02d}] 야간 옵션장이 시작됩니다.\r'.format(dt.hour, dt.minute, dt.second)
                    self.textBrowser.append(str)

                    if not ReceiveRealData:
                        #self.timer.stop()
                        ReceiveRealData = True
                        print('All Timer is stopped !!!')
                    else:
                        pass

                # 현물 장마감 5분전
                elif result['장구분'] == '1' and result['장상태'] == '44':

                    print('현물 장마감 5분전입니다.')
                    str = '[{0:02d}:{1:02d}:{2:02d}] 현물 장마감 5분전입니다.\r'.format(dt.hour, dt.minute, dt.second)
                    self.textBrowser.append(str)

                # 현물 장마감 1분전
                elif result['장구분'] == '1' and result['장상태'] == '43':

                    print('현물 장마감 1분전입니다.')
                    str = '[{0:02d}:{1:02d}:{2:02d}] 현물 장마감 1분전입니다.\r'.format(dt.hour, dt.minute, dt.second)
                    self.textBrowser.append(str)

                    # FUTURES/KOSPI200 예상지수 요청취소
                    self.YJ.UnadviseRealData()

                    str = '[{0:02d}:{1:02d}:{2:02d}] FUTURES/KOSPI200 예상지수 요청을 취소합니다.\r'.format(dt.hour, dt.minute, dt.second)
                    self.textBrowser.append(str)

                    # 지수선물예상체결 요청취소
                    self.YFC.UnadviseRealData()

                    str = '[{0:02d}:{1:02d}:{2:02d}] 지수선물 예상체결 요청을 취소합니다.\r'.format(dt.hour, dt.minute, dt.second)
                    self.textBrowser.append(str)

                    # KOSPI예상체결 요청취소
                    self.YS3.UnadviseRealData()

                    str = '[{0:02d}:{1:02d}:{2:02d}] KOSPI 예상체결 요청을 취소합니다.\r'.format(dt.hour, dt.minute, dt.second)
                    self.textBrowser.append(str)

                    # 지수옵션예상체결 요청취소
                    self.YOC.UnadviseRealData()

                    str = '[{0:02d}:{1:02d}:{2:02d}] 지수옵션 예상체결 요청을 취소합니다.\r'.format(dt.hour, dt.minute, dt.second)
                    self.textBrowser.append(str)

                # 장후 동시호가 시작
                elif result['장구분'] == '5' and result['장상태'] == '31':

                    print('장후 동시호가가 시작되었습니다.')
                    str = '[{0:02d}:{1:02d}:{2:02d}] 장후 동시호가가 시작되었습니다.\r'.format(dt.hour, dt.minute, dt.second)
                    self.textBrowser.append(str)

                # 주간 선물/옵션장 종료
                elif result['장구분'] == '5' and result['장상태'] == '41':

                    print('주간 선물/옵션장이 종료되었습니다.')
                    str = '[{0:02d}:{1:02d}:{2:02d}] 주간 선물/옵션장이 종료되었습니다.\r'.format(dt.hour, dt.minute, dt.second)
                    self.textBrowser.append(str)

                    self.SaveResult()

                # 야간 선물장 종료
                elif result['장구분'] == '7' and result['장상태'] == '41':

                    print('야간 선물장이 종료되었습니다.')
                    str = '[{0:02d}:{1:02d}:{2:02d}] 야간 선물장이 종료되었습니다.\r'.format(dt.hour, dt.minute, dt.second)
                    self.textBrowser.append(str)

                    self.SaveResult()

                # 야간 옵션장 종료
                elif result['장구분'] == '8' and result['장상태'] == '41':

                    print('야간 옵션장이 종료되었습니다...')
                    str = '[{0:02d}:{1:02d}:{2:02d}] 야간 옵션장이 종료되었습니다.\r'.format(dt.hour, dt.minute, dt.second)
                    self.textBrowser.append(str)

                    self.SaveResult()
                else:
                    pass

            elif szTrCode == 'YJ_':

                if pre_start:

                    if result['업종코드'] == KOSPI200:

                        if result['예상지수'] != float(self.tableWidget_fut.item(2, Futures_column.시가.value).text()):

                            kp200_realdata['시가'] = result['예상지수']
                            fut_realdata['KP200'] = result['예상지수']
                            df_plotdata_kp200.iloc[0][1] = result['예상지수']

                            item = QTableWidgetItem("{0:0.2f}".format(result['예상지수']))
                            item.setTextAlignment(Qt.AlignCenter)

                            if kp200_realdata['시가'] > kp200_realdata['종가']:

                                item.setForeground(QBrush(적색))
                            elif kp200_realdata['시가'] < kp200_realdata['종가']:

                                item.setForeground(QBrush(청색))
                            else:
                                item.setForeground(QBrush(검정색))

                            self.tableWidget_fut.setItem(2, Futures_column.시가.value, item)
                        else:
                            pass

                        atm_str = self.find_ATM(result['예상지수'])

                        str = '[{0:02d}:{1:02d}:{2:02d}] 예상 등가지수 : {3}, 예상 Basis : {4:0.2f}\r'.format(
                                        int(result['시간'][0:2]),
                                        int(result['시간'][2:4]),
                                        int(result['시간'][4:6]),
                                        atm_str,
                                        fut_realdata['시가'] - fut_realdata['KP200'])
                        self.textBrowser.append(str)

                        if atm_str in cm_call_actval:
                            atm_index_yj = cm_call_actval.index(atm_str)
                            #print('예상 등가지수 index : ', atm_index_yj)
                        else:
                            print("atm_str이 리스트에 없습니다.", atm_str)

                    elif result['업종코드'] == FUTURES:

                        print('선물 예상지수 : ', result['예상지수'])

                    else:
                        pass
                else:
                    pass

            elif szTrCode == 'YS3':

                if pre_start:

                    현재가 = format(result['예상체결가격'], ',')

                    if result['단축코드'] == SAMSUNG:

                        if result['예상체결가전일종가대비구분'] == '5':

                            jisu_str = "SS : {0}({1}, {2:0.1f}%)".format(현재가, -result['예상체결가전일종가대비'],
                                                                                result['예상체결가전일종가등락율'])
                            self.label_samsung.setText(jisu_str)
                            self.label_samsung.setStyleSheet('background-color: blue ; color: white')

                        elif result['예상체결가전일종가대비구분'] == '2':

                            jisu_str = "SS : {0}({1}, {2:0.1f}%)".format(현재가, result['예상체결가전일종가대비'],
                                                                                result['예상체결가전일종가등락율'])
                            self.label_samsung.setText(jisu_str)
                            self.label_samsung.setStyleSheet('background-color: red ; color: white')

                        else:
                            jisu_str = "SS : {0}({1})".format(현재가, result['예상체결가전일종가대비'])
                            self.label_samsung.setText(jisu_str)
                            self.label_samsung.setStyleSheet('background-color: yellow ; color: black')

                    elif result['단축코드'] == MOBIS:

                        if result['예상체결가전일종가대비구분'] == '5':

                            jisu_str = "MOBIS : {0}({1}, {2:0.1f}%)".format(현재가, -result['예상체결가전일종가대비'],
                                                                              result['예상체결가전일종가등락율'])
                            self.label_mobis.setText(jisu_str)
                            self.label_mobis.setStyleSheet('background-color: blue ; color: white')

                        elif result['예상체결가전일종가대비구분'] == '2':

                            jisu_str = "MOBIS : {0}({1}, {2:0.1f}%)".format(현재가, result['예상체결가전일종가대비'],
                                                                              result['예상체결가전일종가등락율'])
                            self.label_mobis.setText(jisu_str)
                            self.label_mobis.setStyleSheet('background-color: red ; color: white')

                        else:
                            jisu_str = "MOBIS : {0}({1})".format(현재가, result['예상체결가전일종가대비'])
                            self.label_mobis.setText(jisu_str)
                            self.label_mobis.setStyleSheet('background-color: yellow ; color: black')

                    elif result['단축코드'] == NAVER:

                        if result['예상체결가전일종가대비구분'] == '5':

                            jisu_str = "NAVER : {0}({1}, {2:0.1f}%)".format(현재가, -result['예상체결가전일종가대비'],
                                                                              result['예상체결가전일종가등락율'])
                            self.label_naver.setText(jisu_str)
                            self.label_naver.setStyleSheet('background-color: blue ; color: white')

                        elif result['예상체결가전일종가대비구분'] == '2':

                            jisu_str = "NAVER : {0}({1}, {2:0.1f}%)".format(현재가, result['예상체결가전일종가대비'],
                                                                              result['예상체결가전일종가등락율'])
                            self.label_naver.setText(jisu_str)
                            self.label_naver.setStyleSheet('background-color: red ; color: white')

                        else:
                            jisu_str = "NAVER : {0}({1})".format(현재가, result['예상체결가전일종가대비'])
                            self.label_naver.setText(jisu_str)
                            self.label_naver.setStyleSheet('background-color: yellow ; color: black')
                    else:
                        print('단축코드', result['단축코드'])
                else:
                    pass

            elif szTrCode == 'YOC':

                if pre_start:

                    if result['단축코드'][0:3] == '201':

                        index = cm_call_행사가.index(result['단축코드'][5:8])

                        if result['예상체결가격'] != float(self.tableWidget_call.item(index, Option_column.시가.value).text()):

                            if result['예상체결가격'] > 0:

                                df_plotdata_cm_call.iloc[index][1] = result['예상체결가격']

                                df_cm_call.loc[index, '시가'] = round(result['예상체결가격'], 2)
                                item = QTableWidgetItem("{0:0.2f}".format(result['예상체결가격']))
                                item.setTextAlignment(Qt.AlignCenter)

                                if result['예상체결가격'] > df_cm_call.iloc[index]['종가']:
                                    item.setForeground(QBrush(적색))
                                elif result['예상체결가격'] < df_cm_call.iloc[index]['종가']:
                                    item.setForeground(QBrush(청색))
                                else:
                                    item.setForeground(QBrush(검정색))

                                self.tableWidget_call.setItem(index, Option_column.시가.value, item)

                                temp = self.calc_pivot(df_cm_call.iloc[index]['전저'],
                                                                              df_cm_call.iloc[index]['전고'],
                                                                              df_cm_call.iloc[index]['종가'],
                                                                              df_cm_call.iloc[index]['시가'])

                                df_cm_call.loc[index, '피봇'] = round(temp, 2)

                                item = QTableWidgetItem("{0:0.2f}".format(df_cm_call.iloc[index]['피봇']))
                                item.setTextAlignment(Qt.AlignCenter)
                                self.tableWidget_call.setItem(index, Option_column.피봇.value, item)

                                if result['예상체결가격'] > 0.3 and df_cm_call.iloc[index]['종가'] > 0:

                                    시가갭 = result['예상체결가격'] - df_cm_call.iloc[index]['종가']
                                    yoc_call_gap_percent[index] = (result['예상체결가격'] / df_cm_call.iloc[index][
                                        '종가'] - 1) * 100

                                    gap_str = "{0:0.2f}({1:0.0f}%)".format(시가갭, yoc_call_gap_percent[index])

                                    if gap_str != self.tableWidget_call.item(index, Option_column.시가갭.value).text():

                                        item = QTableWidgetItem(gap_str)
                                        item.setTextAlignment(Qt.AlignCenter)
                                        self.tableWidget_call.setItem(index, Option_column.시가갭.value, item)

                                        self.tableWidget_call.resizeColumnsToContents()
                                        self.tableWidget_call.setColumnWidth(0, 15)
                                    else:
                                        pass
                                else:
                                    pass

                                str = '[{0:02d}:{1:02d}:{2:02d}] [{3}] Call {4} 시작예상가 수신... \r'.format(
                                    int(result['예상체결시간'][0:2]),
                                    int(result['예상체결시간'][2:4]),
                                    int(result['예상체결시간'][4:6]),
                                    szTrCode,
                                    result['예상체결가격'])
                                self.textBrowser.append(str)
                            else:
                                pass
                        else:
                            pass

                        temp = yoc_call_gap_percent[:]
                        call_gap_percent_local = [value for value in temp if not math.isnan(value)]
                        call_gap_percent_local.sort()

                        if call_gap_percent_local:
                            tmp = np.array(call_gap_percent_local)
                            mean = int(round(np.mean(tmp), 1))
                            call_str = '시가갭' + '(' + repr(mean) + '%' + ')'

                            if call_str != self.tableWidget_call.horizontalHeaderItem(Option_column.시가갭.value).text():
                                item = QTableWidgetItem(call_str)
                                self.tableWidget_call.setHorizontalHeaderItem(Option_column.시가갭.value, item)
                                self.tableWidget_call.resizeColumnsToContents()
                                self.tableWidget_call.setColumnWidth(0, 15)
                            else:
                                pass
                        else:
                            pass

                    elif result['단축코드'][0:3] == '301':

                        index = cm_put_행사가.index(result['단축코드'][5:8])

                        if result['예상체결가격'] != float(self.tableWidget_put.item(index, Option_column.시가.value).text()):

                            if result['예상체결가격'] > 0:

                                df_plotdata_cm_put.iloc[index][1] = result['예상체결가격']

                                df_cm_put.loc[index, '시가'] = round(result['예상체결가격'], 2)
                                item = QTableWidgetItem("{0:0.2f}".format(result['예상체결가격']))
                                item.setTextAlignment(Qt.AlignCenter)

                                if result['예상체결가격'] > df_cm_put.iloc[index]['종가']:
                                    item.setForeground(QBrush(적색))
                                elif result['예상체결가격'] < df_cm_put.iloc[index]['종가']:
                                    item.setForeground(QBrush(청색))
                                else:
                                    item.setForeground(QBrush(검정색))

                                self.tableWidget_put.setItem(index, Option_column.시가.value, item)

                                temp = self.calc_pivot(df_cm_put.iloc[index]['전저'],
                                                                              df_cm_put.iloc[index]['전고'],
                                                                              df_cm_put.iloc[index]['종가'],
                                                                              df_cm_put.iloc[index]['시가'])

                                df_cm_put.loc[index, '피봇'] = round(temp, 2)

                                item = QTableWidgetItem("{0:0.2f}".format(df_cm_put.iloc[index]['피봇']))
                                item.setTextAlignment(Qt.AlignCenter)
                                self.tableWidget_put.setItem(index, Option_column.피봇.value, item)

                                if result['예상체결가격'] > 0.3 and df_cm_put.iloc[index]['종가'] > 0:

                                    시가갭 = result['예상체결가격'] - df_cm_put.iloc[index]['종가']
                                    yoc_put_gap_percent[index] = (result['예상체결가격'] / df_cm_put.iloc[index][
                                        '종가'] - 1) * 100

                                    gap_str = "{0:0.2f}({1:0.0f}%)".format(시가갭, yoc_put_gap_percent[index])

                                    if gap_str != self.tableWidget_put.item(index, Option_column.시가갭.value).text():

                                        item = QTableWidgetItem(gap_str)
                                        item.setTextAlignment(Qt.AlignCenter)
                                        self.tableWidget_put.setItem(index, Option_column.시가갭.value, item)

                                        self.tableWidget_put.resizeColumnsToContents()
                                        self.tableWidget_put.setColumnWidth(0, 15)
                                    else:
                                        pass
                                else:
                                    pass

                                str = '[{0:02d}:{1:02d}:{2:02d}] [{3}] Put {4} 시작예상가 수신... \r'.format(
                                    int(result['예상체결시간'][0:2]),
                                    int(result['예상체결시간'][2:4]),
                                    int(result['예상체결시간'][4:6]),
                                    szTrCode,
                                    result['예상체결가격'])
                                self.textBrowser.append(str)
                            else:
                                pass
                        else:
                            pass

                        temp = yoc_put_gap_percent[:]
                        put_gap_percent_local = [value for value in temp if not math.isnan(value)]
                        put_gap_percent_local.sort()

                        if put_gap_percent_local:
                            tmp = np.array(put_gap_percent_local)
                            mean = int(round(np.mean(tmp), 1))
                            put_str = '시가갭' + '(' + repr(mean) + '%' + ')'

                            if put_str != self.tableWidget_put.horizontalHeaderItem(Option_column.시가갭.value).text():
                                item = QTableWidgetItem(put_str)
                                self.tableWidget_put.setHorizontalHeaderItem(Option_column.시가갭.value, item)
                                self.tableWidget_put.resizeColumnsToContents()
                                self.tableWidget_put.setColumnWidth(0, 15)
                            else:
                                pass
                        else:
                            pass
                    else:
                        pass
                else:
                    str = '[{0:02d}:{1:02d}:{2:02d}] Wrong [{3}] 수신... \r'.format(
                        int(result['예상체결시간'][0:2]),
                        int(result['예상체결시간'][2:4]),
                        int(result['예상체결시간'][4:6]),
                        szTrCode)
                    self.textBrowser.append(str)

            elif szTrCode == 'YFC':

                if pre_start:

                    if result['단축코드'] == gmshcode:

                        if result['예상체결가격'] != float(self.tableWidget_fut.item(1, Futures_column.시가.value).text()):

                            fut_realdata['시가'] = result['예상체결가격']
                            df_plotdata_fut.iloc[0][1] = result['예상체결가격']

                            item = QTableWidgetItem("{0:0.2f}".format(result['예상체결가격']))
                            item.setTextAlignment(Qt.AlignCenter)

                            if result['예상체결가격'] > fut_realdata['종가']:
                                item.setForeground(QBrush(적색))
                            elif result['예상체결가격'] < fut_realdata['종가']:
                                item.setForeground(QBrush(청색))
                            else:
                                item.setForeground(QBrush(검정색))

                            self.tableWidget_fut.setItem(1, Futures_column.시가.value, item)

                            fut_realdata['피봇'] = self.calc_pivot(fut_realdata['전저'], fut_realdata['전고'],
                                                                 fut_realdata['종가'],
                                                                 fut_realdata['시가'])

                            item = QTableWidgetItem("{0:0.2f}".format(fut_realdata['피봇']))
                            item.setTextAlignment(Qt.AlignCenter)
                            self.tableWidget_fut.setItem(1, Futures_column.피봇.value, item)

                            self.tableWidget_fut.resizeColumnsToContents()
                        else:
                            pass
                    else:
                        pass
                else:
                    pass

            elif szTrCode == 'S3_':

                현재가 = format(result['현재가'], ',')

                # S3 데이타표시
                if result['단축코드'] == SAMSUNG:

                    if result['전일대비구분'] == '5':

                        jisu_str = "SS : {0}({1}, {2:0.1f}%)".format(현재가, -result['전일대비'], result['등락율'])
                        self.label_samsung.setText(jisu_str)
                        self.label_samsung.setStyleSheet('background-color: blue ; color: white')

                    elif result['전일대비구분'] == '2':

                        jisu_str = "SS : {0}({1}, {2:0.1f}%)".format(현재가, result['전일대비'], result['등락율'])
                        self.label_samsung.setText(jisu_str)
                        self.label_samsung.setStyleSheet('background-color: red ; color: white')

                    else:
                        jisu_str = "SS : {0}({1})".format(현재가, result['전일대비'])
                        self.label_samsung.setText(jisu_str)
                        self.label_samsung.setStyleSheet('background-color: yellow ; color: black')

                elif result['단축코드'] == MOBIS:

                    if result['전일대비구분'] == '5':

                        jisu_str = "MOBIS : {0}({1}, {2:0.1f}%)".format(현재가, -result['전일대비'], result['등락율'])
                        self.label_mobis.setText(jisu_str)
                        self.label_mobis.setStyleSheet('background-color: blue ; color: white')

                    elif result['전일대비구분'] == '2':

                        jisu_str = "MOBIS : {0}({1}, {2:0.1f}%)".format(현재가, result['전일대비'], result['등락율'])
                        self.label_mobis.setText(jisu_str)
                        self.label_mobis.setStyleSheet('background-color: red ; color: white')

                    else:
                        jisu_str = "MOBIS : {0}({1})".format(현재가, result['전일대비'])
                        self.label_mobis.setText(jisu_str)
                        self.label_mobis.setStyleSheet('background-color: yellow ; color: black')

                elif result['단축코드'] == NAVER:

                    if result['전일대비구분'] == '5':

                        jisu_str = "NAVER : {0}({1}, {2:0.1f}%)".format(현재가, -result['전일대비'], result['등락율'])
                        self.label_naver.setText(jisu_str)
                        self.label_naver.setStyleSheet('background-color: blue ; color: white')

                    elif result['전일대비구분'] == '2':

                        jisu_str = "NAVER : {0}({1}, {2:0.1f}%)".format(현재가, result['전일대비'], result['등락율'])
                        self.label_naver.setText(jisu_str)
                        self.label_naver.setStyleSheet('background-color: red ; color: white')

                    else:
                        jisu_str = "NAVER : {0}({1})".format(현재가, result['전일대비'])
                        self.label_naver.setText(jisu_str)
                        self.label_naver.setStyleSheet('background-color: yellow ; color: black')
                else:
                    pass

            elif szTrCode == 'IJ_':

                # IJ 데이타표시
                if result['업종코드'] == KOSPI200:

                    if result['시가지수'] != float(self.tableWidget_fut.item(2, Futures_column.시가.value).text()):

                        kp200_realdata['시가'] = result['시가지수']
                        df_plotdata_kp200.iloc[0][1] = result['시가지수']

                        item = QTableWidgetItem("{0:0.2f}".format(result['시가지수']))
                        item.setTextAlignment(Qt.AlignCenter)

                        if kp200_realdata['시가'] > kp200_realdata['종가']:

                            item.setForeground(QBrush(적색))
                        elif kp200_realdata['시가'] < kp200_realdata['종가']:

                            item.setForeground(QBrush(청색))
                        else:
                            item.setForeground(QBrush(검정색))

                        self.tableWidget_fut.setItem(2, Futures_column.시가.value, item)

                        str = '[{0:02d}:{1:02d}:{2:02d}] KP200 시작가 {3:0.2f)를 수신했습니다.\r'.format(
                            int(result['시간'][0:2]),
                            int(result['시간'][2:4]),
                            int(result['시간'][4:6]),
                            kp200_realdata['시가'])
                        self.textBrowser.append(str)

                        # 전일 등가중심 호가요청 취소
                        for i in range(15):
                            self.cm_opt_ho.UnadviseRealDataWithKey(cm_call_code[(old_atm_index - 7) + i])
                            self.cm_opt_ho.UnadviseRealDataWithKey(cm_put_code[(old_atm_index - 7) + i])

                        atm_str = self.find_ATM(kp200_realdata['시가'])
                        atm_index = cm_call_actval.index(atm_str)

                        str = '[{0:02d}:{1:02d}:{2:02d}] 전일호가 취소 및 당일호가(등가:{3})를 요청합니다.\r'.format(
                            dt.hour, dt.minute, dt.second, atm_str)
                        self.textBrowser.append(str)

                        # 당일 호가요청
                        for i in range(15):
                            self.cm_opt_ho.AdviseRealData(cm_call_code[(atm_index - 7) + i])
                            self.cm_opt_ho.AdviseRealData(cm_put_code[(atm_index - 7) + i])
                    else:
                        pass

                    if result['저가지수'] != float(self.tableWidget_fut.item(2, Futures_column.저가.value).text()):

                        kp200_realdata['저가'] = result['저가지수']

                        item = QTableWidgetItem("{0:0.2f}".format(result['저가지수']))
                        item.setTextAlignment(Qt.AlignCenter)
                        self.tableWidget_fut.setItem(2, Futures_column.저가.value, item)
                    else:
                        pass

                    if result['고가지수'] != float(self.tableWidget_fut.item(2, Futures_column.고가.value).text()):

                        kp200_realdata['고가'] = result['고가지수']

                        item = QTableWidgetItem("{0:0.2f}".format(result['고가지수']))
                        item.setTextAlignment(Qt.AlignCenter)
                        self.tableWidget_fut.setItem(2, Futures_column.고가.value, item)
                    else:
                        pass

                elif result['업종코드'] == KOSPI:

                    temp_str = format(result['지수'], ',')

                    if result['전일대비구분'] == '5':

                        jisu_str = "KOSPI : {0}({1:0.2f}, {2:0.1f}%)".format(temp_str,
                                                                                    -result['전일비'],
                                                                                    result['등락율'])
                        self.label_kospi.setText(jisu_str)
                        self.label_kospi.setStyleSheet('background-color: blue ; color: white')

                    elif result['전일대비구분'] == '2':

                        jisu_str = "KOSPI : {0}({1:0.2f}, {2:0.1f}%)".format(temp_str,
                                                                                    result['전일비'],
                                                                                    result['등락율'])
                        self.label_kospi.setText(jisu_str)
                        self.label_kospi.setStyleSheet('background-color: red ; color: white')

                    else:

                        jisu_str = "KOSPI : {0}({1:0.2f})".format(temp_str, result['전일비'])
                        self.label_kospi.setText(jisu_str)
                        self.label_kospi.setStyleSheet('background-color: yellow ; color: black')

                elif result['업종코드'] == KOSDAQ:

                    temp_str = format(result['지수'], ',')

                    if result['전일대비구분'] == '5':

                        jisu_str = "KOSDAQ : {0}({1:0.2f}, {2:0.1f}%)".format(temp_str,
                                                                                     -result['전일비'],
                                                                                     result['등락율'])
                        self.label_kosdaq.setText(jisu_str)
                        self.label_kosdaq.setStyleSheet('background-color: blue ; color: white')

                    elif result['전일대비구분'] == '2':

                        jisu_str = "KOSDAQ : {0}({1:0.2f}, {2:0.1f}%)".format(temp_str,
                                                                                     result['전일비'],
                                                                                     result['등락율'])
                        self.label_kosdaq.setText(jisu_str)
                        self.label_kosdaq.setStyleSheet('background-color: red ; color: white')

                    else:

                        jisu_str = "KOSDAQ : {0}({1:0.2f})".format(temp_str, result['전일비'])
                        self.label_kosdaq.setText(jisu_str)
                        self.label_kosdaq.setStyleSheet('background-color: yellow ; color: black')
                else:
                    pass

            elif szTrCode == 'BM_':

                if result['업종코드'] == FUTURES and result['투자자코드'] == FOREIGNER or result['업종코드'] == CME and result['투자자코드'] == FOREIGNER:

                    FUT_FOREIGNER_거래대금순매수 = int(result['거래대금순매수'])
                    FUT_FOREIGNER_거래대금순매수_직전대비 = int(result['거래대금순매수직전대비'])

                    FUT_FOREIGNER_직전대비.extend([int(result['거래대금순매수직전대비'])])
                    temp = list(FUT_FOREIGNER_직전대비)

                    순매수 = format(FUT_FOREIGNER_거래대금순매수, ',')

                    if min(temp) > 0:

                        item_str = "{0}({1})\n↗".format(순매수, result['거래대금순매수직전대비'])

                        if item_str != self.tableWidget_supply.item(0, 0).text():
                            item = QTableWidgetItem(item_str)
                            item.setTextAlignment(Qt.AlignCenter)
                            item.setBackground(QBrush(적색))
                            item.setForeground(QBrush(흰색))
                            self.tableWidget_supply.setItem(0, 0, item)
                        else:
                            pass

                    elif max(temp) < 0:

                        item_str = "{0}({1})\n↘".format(순매수, result['거래대금순매수직전대비'])

                        if item_str != self.tableWidget_supply.item(0, 0).text():
                            item = QTableWidgetItem(item_str)
                            item.setTextAlignment(Qt.AlignCenter)
                            item.setBackground(QBrush(청색))
                            item.setForeground(QBrush(흰색))
                            self.tableWidget_supply.setItem(0, 0, item)
                        else:
                            pass

                    else:

                        item_str = "{0}({1})".format(순매수, result['거래대금순매수직전대비'])

                        if item_str != self.tableWidget_supply.item(0, 0).text():
                            item = QTableWidgetItem(item_str)
                            item.setTextAlignment(Qt.AlignCenter)
                            item.setBackground(QBrush(기본바탕색))
                            item.setForeground(QBrush(검정색))
                            self.tableWidget_supply.setItem(0, 0, item)
                        else:
                            pass

                elif result['업종코드'] == FUTURES and result['투자자코드'] == RETAIL or result['업종코드'] == CME and result['투자자코드'] == RETAIL:

                    FUT_RETAIL_거래대금순매수 = int(result['거래대금순매수'])
                    FUT_RETAIL_거래대금순매수_직전대비 = int(result['거래대금순매수직전대비'])

                    FUT_RETAIL_직전대비.extend([int(result['거래대금순매수직전대비'])])
                    temp = list(FUT_RETAIL_직전대비)

                    순매수 = format(FUT_RETAIL_거래대금순매수, ',')

                    if min(temp) > 0:

                        item_str = "{0}({1})\n↗".format(순매수, result['거래대금순매수직전대비'])

                    elif max(temp) < 0:

                        item_str = "{0}({1})\n↘".format(순매수, result['거래대금순매수직전대비'])

                    else:
                        item_str = "{0}({1})".format(순매수, result['거래대금순매수직전대비'])

                    if item_str != self.tableWidget_supply.item(0, 3).text():
                        item = QTableWidgetItem(item_str)
                        item.setTextAlignment(Qt.AlignCenter)
                        self.tableWidget_supply.setItem(0, 3, item)
                    else:
                        pass

                elif result['업종코드'] == FUTURES and result['투자자코드'] == INSTITUTIONAL or result['업종코드'] == CME and result['투자자코드'] == INSTITUTIONAL:

                    FUT_INSTITUTIONAL_거래대금순매수 = int(result['거래대금순매수'])
                    FUT_INSTITUTIONAL_거래대금순매수_직전대비 = int(result['거래대금순매수직전대비'])

                    기관_거래대금순매수 = FUT_INSTITUTIONAL_거래대금순매수 + FUT_STOCK_거래대금순매수 + FUT_BOHEOM_거래대금순매수 + \
                                 FUT_TOOSIN_거래대금순매수 + FUT_BANK_거래대금순매수 + FUT_JONGGEUM_거래대금순매수 + \
                                 FUT_GIGEUM_거래대금순매수 + FUT_GITA_거래대금순매수

                    기관_거래대금순매수_직전대비 = FUT_INSTITUTIONAL_거래대금순매수_직전대비 + FUT_STOCK_거래대금순매수_직전대비 + \
                                      FUT_BOHEOM_거래대금순매수_직전대비 + FUT_TOOSIN_거래대금순매수_직전대비 + FUT_BANK_거래대금순매수_직전대비 + \
                                      FUT_JONGGEUM_거래대금순매수_직전대비 + FUT_GIGEUM_거래대금순매수_직전대비 + FUT_GITA_거래대금순매수_직전대비

                    FUT_INSTITUTIONAL_직전대비.extend([기관_거래대금순매수_직전대비])
                    temp = list(FUT_INSTITUTIONAL_직전대비)

                    순매수 = format(기관_거래대금순매수, ',')

                    if min(temp) > 0:

                        item_str = "{0}({1})\n↗".format(순매수, 기관_거래대금순매수_직전대비)

                    elif max(temp) < 0:

                        item_str = "{0}({1})\n↘".format(순매수, 기관_거래대금순매수_직전대비)

                    else:
                        item_str = "{0}({1})".format(순매수, 기관_거래대금순매수_직전대비)

                    if item_str != self.tableWidget_supply.item(0, 4).text():
                        item = QTableWidgetItem(item_str)
                        item.setTextAlignment(Qt.AlignCenter)
                        self.tableWidget_supply.setItem(0, 4, item)
                    else:
                        pass

                elif result['업종코드'] == FUTURES and result['투자자코드'] == STOCK or result['업종코드'] == CME and result['투자자코드'] == STOCK:

                    FUT_STOCK_거래대금순매수 = int(result['거래대금순매수'])
                    FUT_STOCK_거래대금순매수_직전대비 = int(result['거래대금순매수직전대비'])

                elif result['업종코드'] == FUTURES and result['투자자코드'] == BOHEOM or result['업종코드'] == CME and result['투자자코드'] == BOHEOM:

                    FUT_BOHEOM_거래대금순매수 = int(result['거래대금순매수'])
                    FUT_BOHEOM_거래대금순매수_직전대비 = int(result['거래대금순매수직전대비'])

                elif result['업종코드'] == FUTURES and result['투자자코드'] == TOOSIN or result['업종코드'] == CME and result['투자자코드'] == TOOSIN:

                    FUT_TOOSIN_거래대금순매수 = int(result['거래대금순매수'])
                    FUT_TOOSIN_거래대금순매수_직전대비 = int(result['거래대금순매수직전대비'])

                elif result['업종코드'] == FUTURES and result['투자자코드'] == BANK or result['업종코드'] == CME and result['투자자코드'] == BANK:

                    FUT_BANK_거래대금순매수 = int(result['거래대금순매수'])
                    FUT_BANK_거래대금순매수_직전대비 = int(result['거래대금순매수직전대비'])

                elif result['업종코드'] == FUTURES and result['투자자코드'] == JONGGEUM or result['업종코드'] == CME and result['투자자코드'] == JONGGEUM:

                    FUT_JONGGEUM_거래대금순매수 = int(result['거래대금순매수'])
                    FUT_JONGGEUM_거래대금순매수_직전대비 = int(result['거래대금순매수직전대비'])

                elif result['업종코드'] == FUTURES and result['투자자코드'] == GIGEUM or result['업종코드'] == CME and result['투자자코드'] == GIGEUM:

                    FUT_GIGEUM_거래대금순매수 = int(result['거래대금순매수'])
                    FUT_GIGEUM_거래대금순매수_직전대비 = int(result['거래대금순매수직전대비'])

                elif result['업종코드'] == FUTURES and result['투자자코드'] == GITA or result['업종코드'] == CME and result['투자자코드'] == GITA:

                    FUT_GITA_거래대금순매수 = int(result['거래대금순매수'])
                    FUT_GITA_거래대금순매수_직전대비 = int(result['거래대금순매수직전대비'])

                elif result['업종코드'] == KOSPI and result['투자자코드'] == FOREIGNER:

                    KOSPI_FOREIGNER_거래대금순매수 = int(result['거래대금순매수'])
                    KOSPI_FOREIGNER_거래대금순매수_직전대비 = int(result['거래대금순매수직전대비'])

                    KOSPI_FOREIGNER_직전대비.extend([int(result['거래대금순매수직전대비'])])
                    temp = list(KOSPI_FOREIGNER_직전대비)

                    순매수 = format(KOSPI_FOREIGNER_거래대금순매수, ',')

                    if min(temp) > 0:

                        item_str = "{0}({1})\n↗".format(순매수, result['거래대금순매수직전대비'])

                        if item_str != self.tableWidget_supply.item(0, 2).text():
                            item = QTableWidgetItem(item_str)
                            item.setTextAlignment(Qt.AlignCenter)
                            item.setBackground(QBrush(적색))
                            item.setForeground(QBrush(흰색))
                            self.tableWidget_supply.setItem(0, 2, item)
                        else:
                            pass

                    elif max(temp) < 0:

                        item_str = "{0}({1})\n↘".format(순매수, result['거래대금순매수직전대비'])

                        if item_str != self.tableWidget_supply.item(0, 2).text():
                            item = QTableWidgetItem(item_str)
                            item.setTextAlignment(Qt.AlignCenter)
                            item.setBackground(QBrush(청색))
                            item.setForeground(QBrush(흰색))
                            self.tableWidget_supply.setItem(0, 2, item)
                        else:
                            pass

                    else:
                        item_str = "{0}({1})".format(순매수, result['거래대금순매수직전대비'])

                        if item_str != self.tableWidget_supply.item(0, 2).text():
                            item = QTableWidgetItem(item_str)
                            item.setTextAlignment(Qt.AlignCenter)
                            item.setBackground(QBrush(기본바탕색))
                            item.setForeground(QBrush(검정색))
                            self.tableWidget_supply.setItem(0, 2, item)
                        else:
                            pass

                elif result['업종코드'] == KOSPI and result['투자자코드'] == RETAIL:

                    KOSPI_RETAIL_거래대금순매수 = int(result['거래대금순매수'])
                    KOSPI_RETAIL_거래대금순매수_직전대비 = int(result['거래대금순매수직전대비'])

                elif result['업종코드'] == KOSPI and result['투자자코드'] == INSTITUTIONAL:

                    KOSPI_INSTITUTIONAL_거래대금순매수 = int(result['거래대금순매수'])
                    KOSPI_INSTITUTIONAL_거래대금순매수_직전대비 = int(result['거래대금순매수직전대비'])

                elif result['업종코드'] == KOSPI and result['투자자코드'] == STOCK:

                    KOSPI_STOCK_거래대금순매수 = int(result['거래대금순매수'])
                    KOSPI_STOCK_거래대금순매수_직전대비 = int(result['거래대금순매수직전대비'])

                elif result['업종코드'] == KOSPI and result['투자자코드'] == BOHEOM:

                    KOSPI_BOHEOM_거래대금순매수 = int(result['거래대금순매수'])
                    KOSPI_BOHEOM_거래대금순매수_직전대비 = int(result['거래대금순매수직전대비'])

                elif result['업종코드'] == KOSPI and result['투자자코드'] == TOOSIN:

                    KOSPI_TOOSIN_거래대금순매수 = int(result['거래대금순매수'])
                    KOSPI_TOOSIN_거래대금순매수_직전대비 = int(result['거래대금순매수직전대비'])

                elif result['업종코드'] == KOSPI and result['투자자코드'] == BANK:

                    KOSPI_BANK_거래대금순매수 = int(result['거래대금순매수'])
                    KOSPI_BANK_거래대금순매수_직전대비 = int(result['거래대금순매수직전대비'])

                elif result['업종코드'] == KOSPI and result['투자자코드'] == JONGGEUM:

                    KOSPI_JONGGEUM_거래대금순매수 = int(result['거래대금순매수'])
                    KOSPI_JONGGEUM_거래대금순매수_직전대비 = int(result['거래대금순매수직전대비'])

                elif result['업종코드'] == KOSPI and result['투자자코드'] == GIGEUM:

                    KOSPI_GIGEUM_거래대금순매수 = int(result['거래대금순매수'])
                    KOSPI_GIGEUM_거래대금순매수_직전대비 = int(result['거래대금순매수직전대비'])

                elif result['업종코드'] == KOSPI and result['투자자코드'] == GITA:

                    KOSPI_GITA_거래대금순매수 = int(result['거래대금순매수'])
                    KOSPI_GITA_거래대금순매수_직전대비 = int(result['거래대금순매수직전대비'])
                else:
                    pass

                if overnight:

                    선물_거래대금순매수 = FUT_FOREIGNER_거래대금순매수 + FUT_RETAIL_거래대금순매수 + \
                                 FUT_INSTITUTIONAL_거래대금순매수 + FUT_STOCK_거래대금순매수 + FUT_BOHEOM_거래대금순매수 + \
                                 FUT_TOOSIN_거래대금순매수 + FUT_BANK_거래대금순매수 + FUT_JONGGEUM_거래대금순매수 + \
                                 FUT_GIGEUM_거래대금순매수 + FUT_GITA_거래대금순매수

                    선물_거래대금순매수_직전대비 = FUT_FOREIGNER_거래대금순매수_직전대비 + FUT_RETAIL_거래대금순매수_직전대비 + \
                                      FUT_INSTITUTIONAL_거래대금순매수_직전대비 + FUT_STOCK_거래대금순매수_직전대비 + \
                                      FUT_BOHEOM_거래대금순매수_직전대비 + FUT_TOOSIN_거래대금순매수_직전대비 + FUT_BANK_거래대금순매수_직전대비 + \
                                      FUT_JONGGEUM_거래대금순매수_직전대비 + FUT_GIGEUM_거래대금순매수_직전대비 + \
                                      FUT_GITA_거래대금순매수_직전대비

                    현물_거래대금순매수 = 0
                    현물_거래대금순매수_직전대비 = 0

                    temp1 = format(선물_거래대금순매수, ',')
                    temp2 = format(현물_거래대금순매수, ',')

                    item_str = "{0}({1})\n{2}({3})".format(temp1, 선물_거래대금순매수_직전대비, temp2, 현물_거래대금순매수_직전대비)

                    if item_str != self.tableWidget_supply.item(0, 5).text():
                        item = QTableWidgetItem(item_str)
                        item.setTextAlignment(Qt.AlignCenter)
                        self.tableWidget_supply.setItem(0, 5, item)
                    else:
                        pass
                else:
                    pass

            elif szTrCode == 'PM_':

                프로그램_전체순매수금액 = int(result['전체순매수금액합계'] / 100)
                프로그램_전체순매수금액직전대비 = int(result['전체순매수금액직전대비'] / 100)

                선물_거래대금순매수 = FUT_FOREIGNER_거래대금순매수 + FUT_RETAIL_거래대금순매수 + \
                             FUT_INSTITUTIONAL_거래대금순매수 + FUT_STOCK_거래대금순매수 + FUT_BOHEOM_거래대금순매수 + \
                             FUT_TOOSIN_거래대금순매수 + FUT_BANK_거래대금순매수 + FUT_JONGGEUM_거래대금순매수 + \
                             FUT_GIGEUM_거래대금순매수 + FUT_GITA_거래대금순매수

                선물_거래대금순매수_직전대비 = FUT_FOREIGNER_거래대금순매수_직전대비 + FUT_RETAIL_거래대금순매수_직전대비 + \
                                  FUT_INSTITUTIONAL_거래대금순매수_직전대비 + FUT_STOCK_거래대금순매수_직전대비 + \
                                  FUT_BOHEOM_거래대금순매수_직전대비 + FUT_TOOSIN_거래대금순매수_직전대비 + FUT_BANK_거래대금순매수_직전대비 + \
                                  FUT_JONGGEUM_거래대금순매수_직전대비 + FUT_GIGEUM_거래대금순매수_직전대비 + \
                                  FUT_GITA_거래대금순매수_직전대비

                현물_거래대금순매수 = KOSPI_FOREIGNER_거래대금순매수 + KOSPI_RETAIL_거래대금순매수 + \
                             KOSPI_INSTITUTIONAL_거래대금순매수 + KOSPI_STOCK_거래대금순매수 + KOSPI_BOHEOM_거래대금순매수 + \
                             KOSPI_TOOSIN_거래대금순매수 + KOSPI_BANK_거래대금순매수 + KOSPI_JONGGEUM_거래대금순매수 + \
                             KOSPI_GIGEUM_거래대금순매수 + KOSPI_GITA_거래대금순매수 + 프로그램_전체순매수금액

                현물_거래대금순매수_직전대비 = KOSPI_FOREIGNER_거래대금순매수_직전대비 + KOSPI_RETAIL_거래대금순매수_직전대비 + \
                                  KOSPI_INSTITUTIONAL_거래대금순매수_직전대비 + KOSPI_STOCK_거래대금순매수_직전대비 + \
                                  KOSPI_BOHEOM_거래대금순매수_직전대비 + KOSPI_TOOSIN_거래대금순매수_직전대비 + KOSPI_BANK_거래대금순매수_직전대비 + \
                                  KOSPI_JONGGEUM_거래대금순매수_직전대비 + KOSPI_GIGEUM_거래대금순매수_직전대비 + \
                                  KOSPI_GITA_거래대금순매수_직전대비 + 프로그램_전체순매수금액직전대비

                PROGRAM_직전대비.extend([프로그램_전체순매수금액직전대비])
                temp = list(PROGRAM_직전대비)

                순매수 = format(프로그램_전체순매수금액, ',')

                if min(temp) > 0:

                    item_str = "{0}({1})\n↗".format(순매수, 프로그램_전체순매수금액직전대비)

                    if item_str != self.tableWidget_supply.item(0, 1).text():
                        item = QTableWidgetItem(item_str)
                        item.setTextAlignment(Qt.AlignCenter)
                        item.setBackground(QBrush(적색))
                        item.setForeground(QBrush(흰색))
                        self.tableWidget_supply.setItem(0, 1, item)
                    else:
                        pass

                elif max(temp) < 0:

                    item_str = "{0}({1})\n↘".format(순매수, 프로그램_전체순매수금액직전대비)

                    if item_str != self.tableWidget_supply.item(0, 1).text():
                        item = QTableWidgetItem(item_str)
                        item.setTextAlignment(Qt.AlignCenter)
                        item.setBackground(QBrush(청색))
                        item.setForeground(QBrush(흰색))
                        self.tableWidget_supply.setItem(0, 1, item)
                    else:
                        pass

                else:
                    item_str = "{0}({1})".format(순매수, 프로그램_전체순매수금액직전대비)

                    if item_str != self.tableWidget_supply.item(0, 1).text():
                        item = QTableWidgetItem(item_str)
                        item.setTextAlignment(Qt.AlignCenter)
                        item.setBackground(QBrush(기본바탕색))
                        item.setForeground(QBrush(검정색))
                        self.tableWidget_supply.setItem(0, 1, item)
                    else:
                        pass

                temp1 = format(선물_거래대금순매수, ',')
                temp2 = format(현물_거래대금순매수, ',')

                item_str = "{0}({1})\n{2}({3})".format(temp1, 선물_거래대금순매수_직전대비, temp2, 현물_거래대금순매수_직전대비)

                if item_str != self.tableWidget_supply.item(0, 5).text():
                    item = QTableWidgetItem(item_str)
                    item.setTextAlignment(Qt.AlignCenter)
                    self.tableWidget_supply.setItem(0, 5, item)
                else:
                    pass

            elif szTrCode == 'FC0' or szTrCode == 'NC0':

                global 선물현재가

                if result['현재가'] != 선물현재가:

                    # FC0/NC0 표시
                    if overnight:

                        if result['체결시간'] != '':
                            nighttime = int(result['체결시간'][0:2])

                            if 0 <= nighttime <= 5:
                                nighttime = nighttime + 24
                            else:
                                pass

                            x_idx = (nighttime - start_hour) * 60 + int(result['체결시간'][2:4]) + 1
                        else:
                            x_idx = 1
                    else:

                        if result['체결시간'] != '':
                            x_idx = (int(result['체결시간'][0:2]) - start_hour) * 60 + int(result['체결시간'][2:4]) + 1
                        else:
                            x_idx = 1

                    df_plotdata_fut.iloc[0][x_idx + 1] = result['현재가']

                    if x_idx == 1:

                        df_plotdata_kp200.iloc[0][x_idx + 1] = df_plotdata_kp200.iloc[0][1]
                    else:
                        df_plotdata_kp200.iloc[0][x_idx + 1] = result['KOSPI200지수']

                    # FUT OL/OH
                    if self.within_n_tick(result['시가'], result['저가'], 10) and \
                            not self.within_n_tick(result['시가'], result['고가'], 10):

                        item = QTableWidgetItem("{0}".format('↑'))
                        item.setTextAlignment(Qt.AlignCenter)
                        item.setBackground(QBrush(적색))
                        item.setForeground(QBrush(흰색))

                        if overnight:
                            self.tableWidget_fut.setItem(0, 0, item)
                        else:
                            self.tableWidget_fut.setItem(1, 0, item)

                    elif not self.within_n_tick(result['시가'], result['저가'], 10) and \
                            self.within_n_tick(result['시가'], result['고가'], 10):

                        item = QTableWidgetItem("{0}".format('↓'))
                        item.setTextAlignment(Qt.AlignCenter)
                        item.setBackground(QBrush(청색))
                        item.setForeground(QBrush(흰색))

                        if overnight:
                            self.tableWidget_fut.setItem(0, 0, item)
                        else:
                            self.tableWidget_fut.setItem(1, 0, item)

                    else:
                        item = QTableWidgetItem("{0}".format(''))

                        if overnight:
                            self.tableWidget_fut.setItem(0, 0, item)
                        else:
                            self.tableWidget_fut.setItem(1, 0, item)

                    if overnight:
                        self.tableWidget_fut.item(0, Futures_column.현재가.value).setBackground(QBrush(옅은회색))
                    else:
                        self.tableWidget_fut.item(1, Futures_column.현재가.value).setBackground(QBrush(옅은회색))
                        self.tableWidget_fut.item(2, Futures_column.현재가.value).setBackground(QBrush(옅은회색))

                    if overnight:
                        fut_price = float(self.tableWidget_fut.item(0, Futures_column.현재가.value).text())
                    else:
                        fut_price = float(self.tableWidget_fut.item(1, Futures_column.현재가.value).text())

                    if result['현재가'] != fut_price:

                        fut_realdata['현재가'] = result['현재가']

                        item = QTableWidgetItem("{0:0.2f}".format(result['현재가']))
                        item.setTextAlignment(Qt.AlignCenter)
                        item.setBackground(QBrush(기본바탕색))

                        if overnight:
                            self.tableWidget_fut.setItem(0, Futures_column.현재가.value, item)
                        else:
                            self.tableWidget_fut.setItem(1, Futures_column.현재가.value, item)

                        if result['시가'] < result['현재가']:

                            if overnight:
                                self.tableWidget_fut.item(0, Futures_column.현재가.value).setForeground(QBrush(적색))
                            else:
                                self.tableWidget_fut.item(1, Futures_column.현재가.value).setForeground(QBrush(적색))

                        elif result['시가'] > result['현재가']:

                            if overnight:
                                self.tableWidget_fut.item(0, Futures_column.현재가.value).setForeground(QBrush(청색))
                            else:
                                self.tableWidget_fut.item(1, Futures_column.현재가.value).setForeground(QBrush(청색))

                        else:
                            if overnight:
                                self.tableWidget_fut.item(0, Futures_column.현재가.value).setForeground(QBrush(검정색))
                            else:
                                self.tableWidget_fut.item(1, Futures_column.현재가.value).setForeground(QBrush(검정색))

                        대비 = int((round((result['현재가'] - result['시가']), 2)) * 100)
                        item = QTableWidgetItem("{0}".format(대비))
                        item.setTextAlignment(Qt.AlignCenter)

                        if overnight:
                            self.tableWidget_fut.setItem(0, Futures_column.대비.value, item)
                        else:
                            self.tableWidget_fut.setItem(1, Futures_column.대비.value, item)
                    else:
                        pass

                    if overnight:
                        fut_open = float(self.tableWidget_fut.item(0, Futures_column.시가.value).text())
                    else:
                        fut_open = float(self.tableWidget_fut.item(1, Futures_column.시가.value).text())

                    if result['시가'] != fut_open:

                        fut_realdata['시가'] = result['시가']
                        df_plotdata_fut.iloc[0][1] = result['시가']

                        item = QTableWidgetItem("{0:0.2f}".format(result['시가']))
                        item.setTextAlignment(Qt.AlignCenter)
                        item.setBackground(QBrush(기본바탕색))

                        if fut_realdata['시가'] > fut_realdata['종가']:
                            item.setForeground(QBrush(적색))
                        elif fut_realdata['시가'] < fut_realdata['종가']:
                            item.setForeground(QBrush(청색))
                        else:
                            item.setForeground(QBrush(검정색))

                        if overnight:
                            self.tableWidget_fut.setItem(0, Futures_column.시가.value, item)
                        else:
                            self.tableWidget_fut.setItem(1, Futures_column.시가.value, item)

                        fut_realdata['피봇'] = self.calc_pivot(fut_realdata['전저'], fut_realdata['전고'], fut_realdata['종가'],
                                                             fut_realdata['시가'])

                        item = QTableWidgetItem("{0:0.2f}".format(fut_realdata['피봇']))
                        item.setTextAlignment(Qt.AlignCenter)

                        if overnight:
                            self.tableWidget_fut.setItem(0, Futures_column.피봇.value, item)
                        else:
                            self.tableWidget_fut.setItem(1, Futures_column.피봇.value, item)

                        if fut_realdata['종가'] > 0 and fut_realdata['시가'] > 0:

                            fut_realdata['시가갭'] = fut_realdata['시가'] - fut_realdata['종가']
                            # gap_percent = int((fut_realdata['시가'] / fut_realdata['종가'] - 1) * 100)
                            item = QTableWidgetItem("{0:0.2f}".format(fut_realdata['시가갭']))
                            item.setTextAlignment(Qt.AlignCenter)

                            if overnight:
                                self.tableWidget_fut.setItem(0, Futures_column.시가갭.value, item)
                            else:
                                self.tableWidget_fut.setItem(1, Futures_column.시가갭.value, item)
                        else:
                            pass
                    else:
                        if overnight:
                            fut_pivot = float(self.tableWidget_fut.item(0, Futures_column.피봇.value).text())
                        else:
                            fut_pivot = float(self.tableWidget_fut.item(1, Futures_column.피봇.value).text())

                        if fut_pivot == 0:

                            fut_realdata['시가'] = result['시가']

                            fut_realdata['피봇'] = self.calc_pivot(fut_realdata['전저'], fut_realdata['전고'],
                                                                 fut_realdata['종가'],
                                                                 fut_realdata['시가'])

                            item = QTableWidgetItem("{0:0.2f}".format(fut_realdata['피봇']))
                            item.setTextAlignment(Qt.AlignCenter)

                            if overnight:
                                self.tableWidget_fut.setItem(0, Futures_column.피봇.value, item)
                            else:
                                self.tableWidget_fut.setItem(1, Futures_column.피봇.value, item)
                        else:
                            pass

                    if result['KOSPI200지수'] != float(self.tableWidget_fut.item(2, Futures_column.현재가.value).text()):

                        fut_realdata['KP200'] = result['KOSPI200지수']
                        kp200_realdata['현재가'] = result['KOSPI200지수']

                        item = QTableWidgetItem("{0:0.2f}".format(result['KOSPI200지수']))
                        item.setTextAlignment(Qt.AlignCenter)
                        item.setBackground(QBrush(옅은회색))
                        self.tableWidget_fut.setItem(2, Futures_column.현재가.value, item)

                        # 등가 check & coloring
                        atm_str = self.find_ATM(result['KOSPI200지수'])
                        atm_index = cm_call_actval.index(atm_str)

                        if atm_index != old_atm_index:

                            self.tableWidget_call.item(atm_index, Option_column.행사가.value).setBackground(
                                QBrush(노란색))
                            self.tableWidget_call.item(old_atm_index, Option_column.행사가.value).setBackground(
                                QBrush(녹색))

                            self.tableWidget_put.item(atm_index, Option_column.행사가.value).setBackground(
                                QBrush(노란색))
                            self.tableWidget_put.item(old_atm_index, Option_column.행사가.value).setBackground(
                                QBrush(녹색))

                            old_atm_index = atm_index
                        else:
                            pass
                    else:
                        pass

                    if overnight:
                        fut_low = float(self.tableWidget_fut.item(0, Futures_column.저가.value).text())
                    else:
                        fut_low = float(self.tableWidget_fut.item(1, Futures_column.저가.value).text())

                    if result['저가'] != fut_low:

                        fut_realdata['저가'] = result['저가']

                        item = QTableWidgetItem("{0:0.2f}".format(result['저가']))
                        item.setTextAlignment(Qt.AlignCenter)
                        item.setBackground(QBrush(옅은회색))

                        if overnight:
                            self.tableWidget_fut.setItem(0, Futures_column.저가.value, item)
                        else:
                            self.tableWidget_fut.setItem(1, Futures_column.저가.value, item)

                        fut_realdata['진폭'] = result['고가'] - result['저가']
                        item = QTableWidgetItem("{0:0.2f}".format(fut_realdata['진폭']))
                        item.setTextAlignment(Qt.AlignCenter)

                        if overnight:
                            self.tableWidget_fut.setItem(0, Futures_column.진폭.value, item)
                        else:
                            self.tableWidget_fut.setItem(1, Futures_column.진폭.value, item)
                    else:
                        pass

                    if overnight:
                        fut_high = float(self.tableWidget_fut.item(0, Futures_column.고가.value).text())
                    else:
                        fut_high = float(self.tableWidget_fut.item(1, Futures_column.고가.value).text())

                    if result['고가'] != fut_high:

                        fut_realdata['고가'] = result['고가']

                        item = QTableWidgetItem("{0:0.2f}".format(result['고가']))
                        item.setTextAlignment(Qt.AlignCenter)
                        item.setBackground(QBrush(옅은회색))

                        if overnight:
                            self.tableWidget_fut.setItem(0, Futures_column.고가.value, item)
                        else:
                            self.tableWidget_fut.setItem(1, Futures_column.고가.value, item)

                        fut_realdata['진폭'] = result['고가'] - result['저가']
                        item = QTableWidgetItem("{0:0.2f}".format(fut_realdata['진폭']))
                        item.setTextAlignment(Qt.AlignCenter)

                        if overnight:
                            self.tableWidget_fut.setItem(0, Futures_column.진폭.value, item)
                        else:
                            self.tableWidget_fut.setItem(1, Futures_column.진폭.value, item)
                    else:
                        pass

                    if overnight:
                        fut_volume = int(self.tableWidget_fut.item(0, Futures_column.거래량.value).text())
                    else:
                        fut_volume = int(self.tableWidget_fut.item(1, Futures_column.거래량.value).text())

                    if result['누적거래량'] != fut_volume:

                        fut_realdata['거래량'] = result['누적거래량']

                        item = QTableWidgetItem("{0}".format(result['누적거래량']))
                        item.setTextAlignment(Qt.AlignCenter)

                        if overnight:
                            self.tableWidget_fut.setItem(0, Futures_column.거래량.value, item)
                        else:
                            self.tableWidget_fut.setItem(1, Futures_column.거래량.value, item)
                    else:
                        pass

                    if overnight:
                        fut_oid = float(self.tableWidget_fut.item(0, Futures_column.OID.value).text())
                    else:
                        fut_oid = float(self.tableWidget_fut.item(1, Futures_column.OID.value).text())

                    if result['미결제약정증감'] != fut_oid:

                        fut_realdata['미결'] = result['미결제약정수량']
                        fut_realdata['미결증감'] = result['미결제약정증감']

                        item = QTableWidgetItem("{0}".format(result['미결제약정수량']))
                        item.setTextAlignment(Qt.AlignCenter)

                        if overnight:
                            self.tableWidget_fut.setItem(0, Futures_column.OI.value, item)
                        else:
                            self.tableWidget_fut.setItem(1, Futures_column.OI.value, item)

                        item = QTableWidgetItem("{0}".format(result['미결제약정증감']))
                        item.setTextAlignment(Qt.AlignCenter)

                        if result['미결제약정증감'] < 0:
                            item.setBackground(QBrush(녹색))
                        else:
                            item.setBackground(QBrush(기본바탕색))

                        if overnight:
                            self.tableWidget_fut.setItem(0, Futures_column.OID.value, item)
                        else:
                            self.tableWidget_fut.setItem(1, Futures_column.OID.value, item)

                        self.tableWidget_fut.resizeColumnsToContents()
                    else:
                        pass

                    if szTrCode == 'FC0':

                        if result['전일동시간대거래량'] > 0:

                            if overnight:
                                fut_vr = float(self.tableWidget_fut.item(0, Futures_column.VR.value).text())
                            else:
                                fut_vr = float(self.tableWidget_fut.item(1, Futures_column.VR.value).text())

                            vr = result['누적거래량'] / result['전일동시간대거래량']

                            if vr != fut_vr:
                                item = QTableWidgetItem("{0:0.1f}".format(vr))
                                item.setTextAlignment(Qt.AlignCenter)

                                if overnight:
                                    self.tableWidget_fut.setItem(0, Futures_column.VR.value, item)
                                else:
                                    self.tableWidget_fut.setItem(1, Futures_column.VR.value, item)
                            else:
                                pass
                        else:
                            pass
                    else:
                        pass

                    선물현재가 = copy.deepcopy(result['현재가'])
                else:
                    pass

            elif szTrCode == 'OC0' or szTrCode == 'EC0':

                if pre_start:
                    pre_start = False
                else:
                    pass

                global 콜현재가, 풋현재가

                # X축 시간좌표 계산
                if overnight:

                    if result['체결시간'] != '':

                        nighttime = int(result['체결시간'][0:2])

                        if 0 <= nighttime <= 5:
                            nighttime = nighttime + 24
                        else:
                            pass

                        opt_x_idx = (nighttime - start_hour) * 60 + int(result['체결시간'][2:4]) + 1
                    else:
                        opt_x_idx = 1
                else:

                    if result['체결시간'] != '':
                        opt_x_idx = (int(result['체결시간'][0:2]) - start_hour) * 60 + int(result['체결시간'][2:4]) + 1
                    else:
                        opt_x_idx = 1

                if result['단축코드'][0:3] == '201':

                    if result['현재가'] != 콜현재가:
                        call_result = copy.deepcopy(result)
                        self.call_display(result)
                        콜현재가 = copy.deepcopy(result['현재가'])
                    else:
                        pass

                    if opt_callreal_update_counter >= 500:

                        opt_callreal_update_counter = 0
                        opt_putreal_update_counter = 0
                    else:
                        pass

                    process_time = (timeit.default_timer() - start_time) * 1000

                    if process_time > 0:

                        if opt_callreal_update_counter >= opt_putreal_update_counter:

                            str = '[{0:02d}:{1:02d}:{2:02d}] Call {3} 수신 C({4}/{5}) : {6:0.2f} ms... \r'.format(
                                int(result['체결시간'][0:2]),
                                int(result['체결시간'][2:4]),
                                int(result['체결시간'][4:6]),
                                result['현재가'],
                                opt_callreal_update_counter,
                                opt_putreal_update_counter,
                                process_time)
                            self.textBrowser.append(str)
                        else:

                            str = '[{0:02d}:{1:02d}:{2:02d}] Call {3} 수신 P({4}/{5}) : {6:0.2f} ms... \r'.format(
                                int(result['체결시간'][0:2]),
                                int(result['체결시간'][2:4]),
                                int(result['체결시간'][4:6]),
                                result['현재가'],
                                opt_callreal_update_counter,
                                opt_putreal_update_counter,
                                process_time)
                            self.textBrowser.append(str)
                    else:
                        pass

                elif result['단축코드'][0:3] == '301':

                    if result['현재가'] != 풋현재가:
                        put_result = copy.deepcopy(result)
                        self.put_display(result)
                        풋현재가 = copy.deepcopy(result['현재가'])
                    else:
                        pass

                    if opt_putreal_update_counter >= 500:

                        opt_callreal_update_counter = 0
                        opt_putreal_update_counter = 0
                    else:
                        pass

                    process_time = (timeit.default_timer() - start_time) * 1000

                    if process_time > 0:

                        if opt_callreal_update_counter >= opt_putreal_update_counter:

                            str = '[{0:02d}:{1:02d}:{2:02d}] Put {3} 수신 C({4}/{5}) : {6:0.2f} ms... \r'.format(
                                int(result['체결시간'][0:2]),
                                int(result['체결시간'][2:4]),
                                int(result['체결시간'][4:6]),
                                result['현재가'],
                                opt_callreal_update_counter,
                                opt_putreal_update_counter,
                                process_time)
                            self.textBrowser.append(str)
                        else:

                            str = '[{0:02d}:{1:02d}:{2:02d}] Put {3} 수신 P({4}/{5}) : {6:0.2f} ms... \r'.format(
                                int(result['체결시간'][0:2]),
                                int(result['체결시간'][2:4]),
                                int(result['체결시간'][4:6]),
                                result['현재가'],
                                opt_callreal_update_counter,
                                opt_putreal_update_counter,
                                process_time)
                            self.textBrowser.append(str)
                    else:
                        pass
                else:
                    pass

            elif szTrCode == 'OH0' or szTrCode == 'EH0':

                if not ReceiveRealData:
                    ReceiveRealData = True
                else:
                    pass

                if result['단축코드'][0:3] == '201':

                    index = cm_call_행사가.index(result['단축코드'][5:8])

                    df_cm_call_ho.loc[index, '매수건수'] = result['매수호가총건수']
                    df_cm_call_ho.loc[index, '매도건수'] = result['매도호가총건수']
                    df_cm_call_ho.loc[index, '매수잔량'] = result['매수호가총수량']
                    df_cm_call_ho.loc[index, '매도잔량'] = result['매도호가총수량']

                    opt_call_ho_update_counter += 1

                elif result['단축코드'][0:3] == '301':

                    index = cm_put_행사가.index(result['단축코드'][5:8])

                    df_cm_put_ho.loc[index, '매수건수'] = result['매수호가총건수']
                    df_cm_put_ho.loc[index, '매도건수'] = result['매도호가총건수']
                    df_cm_put_ho.loc[index, '매수잔량'] = result['매수호가총수량']
                    df_cm_put_ho.loc[index, '매도잔량'] = result['매도호가총수량']

                    opt_put_ho_update_counter += 1

                else:
                    pass

                if opt_call_ho_update_counter == 1000 or opt_put_ho_update_counter == 1000:

                    opt_call_ho_update_counter = 0
                    opt_put_ho_update_counter = 0
                else:
                    pass

                '''
                process_time = (timeit.default_timer() - start_time) * 1000

                if process_time > 0:

                    if opt_call_ho_update_counter >= opt_put_ho_update_counter:

                        str = '[{0:02d}:{1:02d}:{2:02d}] RealData Call {3}=[{4}/{5}] --> {6:0.2f} ms... \r'.format(
                            dt.hour,
                            dt.minute,
                            dt.second,
                            szTrCode,
                            opt_call_ho_update_counter,
                            opt_put_ho_update_counter,
                            process_time)
                        # self.textBrowser.append(str)
                        print(str)
                    else:
                        str = '[{0:02d}:{1:02d}:{2:02d}] RealData Put {3}=[{4}/{5}] --> {6:0.2f} ms... \r'.format(
                            dt.hour,
                            dt.minute,
                            dt.second,
                            szTrCode,
                            opt_call_ho_update_counter,
                            opt_put_ho_update_counter,
                            process_time)
                        # self.textBrowser.append(str)
                        print(str)
                else:
                    pass
                '''

            elif szTrCode == 'FH0' or szTrCode == 'NH0':

                # 선물호가 갱신
                if overnight:
                    fut_매수건수 = int(self.tableWidget_fut.item(0, Futures_column.매수건수.value).text())
                else:
                    fut_매수건수 = int(self.tableWidget_fut.item(1, Futures_column.매수건수.value).text())

                if result['매수호가총건수'] != fut_매수건수:

                    item = QTableWidgetItem("{0}".format(result['매수호가총건수']))
                    item.setTextAlignment(Qt.AlignCenter)

                    if overnight:
                        self.tableWidget_fut.setItem(0, Futures_column.매수건수.value, item)
                    else:
                        self.tableWidget_fut.setItem(1, Futures_column.매수건수.value, item)
                else:
                    pass

                if overnight:
                    fut_매도건수 = int(self.tableWidget_fut.item(0, Futures_column.매도건수.value).text())
                else:
                    fut_매도건수 = int(self.tableWidget_fut.item(1, Futures_column.매도건수.value).text())

                if result['매도호가총건수'] != fut_매도건수:

                    item = QTableWidgetItem("{0}".format(result['매도호가총건수']))
                    item.setTextAlignment(Qt.AlignCenter)

                    if overnight:
                        self.tableWidget_fut.setItem(0, Futures_column.매도건수.value, item)
                    else:
                        self.tableWidget_fut.setItem(1, Futures_column.매도건수.value, item)
                else:
                    pass

                if overnight:
                    fut_매수잔량 = int(self.tableWidget_fut.item(0, Futures_column.매수잔량.value).text())
                else:
                    fut_매수잔량 = int(self.tableWidget_fut.item(1, Futures_column.매수잔량.value).text())

                if result['매수호가총수량'] != fut_매수잔량:

                    item = QTableWidgetItem("{0}".format(result['매수호가총수량']))
                    item.setTextAlignment(Qt.AlignCenter)

                    if overnight:
                        self.tableWidget_fut.setItem(0, Futures_column.매수잔량.value, item)
                    else:
                        self.tableWidget_fut.setItem(1, Futures_column.매수잔량.value, item)
                else:
                    pass

                if overnight:
                    fut_매도잔량 = int(self.tableWidget_fut.item(0, Futures_column.매도잔량.value).text())
                else:
                    fut_매도잔량 = int(self.tableWidget_fut.item(1, Futures_column.매도잔량.value).text())

                if result['매도호가총수량'] != fut_매도잔량:

                    item = QTableWidgetItem("{0}".format(result['매도호가총수량']))
                    item.setTextAlignment(Qt.AlignCenter)

                    if overnight:
                        self.tableWidget_fut.setItem(0, Futures_column.매도잔량.value, item)
                    else:
                        self.tableWidget_fut.setItem(1, Futures_column.매도잔량.value, item)
                else:
                    pass

                if result['매도호가총건수'] > 0:

                    fut_cr = result['매수호가총건수'] / result['매도호가총건수']

                    item = QTableWidgetItem("{0:0.2f}".format(fut_cr))
                    item.setTextAlignment(Qt.AlignCenter)

                    if overnight:
                        self.tableWidget_fut.setItem(0, Futures_column.건수비.value, item)
                    else:
                        self.tableWidget_fut.setItem(1, Futures_column.건수비.value, item)
                else:
                    pass

                if result['매도호가총수량'] > 0:

                    fut_rr = result['매수호가총수량'] / result['매도호가총수량']

                    item = QTableWidgetItem("{0:0.2f}".format(fut_rr))
                    item.setTextAlignment(Qt.AlignCenter)

                    if overnight:
                        self.tableWidget_fut.setItem(0, Futures_column.잔량비.value, item)
                    else:
                        self.tableWidget_fut.setItem(1, Futures_column.잔량비.value, item)
                else:
                    pass

                if not overnight:

                    if fut_cr > 1 and fut_cr > fut_rr:

                        self.tableWidget_fut.item(1, Futures_column.건수비.value).setBackground(QBrush(적색))
                        self.tableWidget_fut.item(1, Futures_column.건수비.value).setForeground(QBrush(흰색))
                        self.tableWidget_fut.item(1, Futures_column.잔량비.value).setBackground(QBrush(적색))
                        self.tableWidget_fut.item(1, Futures_column.잔량비.value).setForeground(QBrush(흰색))

                    elif fut_cr < 1 and fut_cr < fut_rr:

                        self.tableWidget_fut.item(1, Futures_column.건수비.value).setBackground(QBrush(청색))
                        self.tableWidget_fut.item(1, Futures_column.건수비.value).setForeground(QBrush(흰색))
                        self.tableWidget_fut.item(1, Futures_column.잔량비.value).setBackground(QBrush(청색))
                        self.tableWidget_fut.item(1, Futures_column.잔량비.value).setForeground(QBrush(흰색))
                    else:
                        self.tableWidget_fut.item(1, Futures_column.건수비.value).setBackground(QBrush(기본바탕색))
                        self.tableWidget_fut.item(1, Futures_column.건수비.value).setForeground(QBrush(검정색))
                        self.tableWidget_fut.item(1, Futures_column.잔량비.value).setBackground(QBrush(기본바탕색))
                        self.tableWidget_fut.item(1, Futures_column.잔량비.value).setForeground(QBrush(검정색))
                else:
                    pass

                '''
                process_time = (timeit.default_timer() - start_time) * 1000

                if process_time > 0:
                    str = '[{0:02d}:{1:02d}:{2:02d}] RealData 처리시간 {3} --> {4:0.2f} ms... \r'.format(
                        dt.hour,
                        dt.minute,
                        dt.second,
                        szTrCode,
                        process_time)
                    # self.textBrowser.append(str)
                    #print(str)
                else:
                    pass
                '''
            else:
                print('요청하지 않은 TR 코드 : ', szTrCode)

            process_time = (timeit.default_timer() - start_time) * 1000

            if process_time > 0:
                str = '[{0:02d}:{1:02d}:{2:02d}] OnReceiveRealData[{3}] 처리시간 --> {4:0.2f} ms...\r'.format(dt.hour,
                                                                        dt.minute, dt.second, szTrCode, process_time)
                #self.textBrowser.append(str)
                #print(str)
            else:
                pass

        except Exception as e:
            pass

    def AddCode(self):

        global overnight, start_hour

        global START_ON
        global pre_start

        global kp200_realdata, fut_realdata

        current = datetime.datetime.now()
        current_str = current.strftime('%H:%M:%S')

        print('서비스요청 시간 :', current_str)

        if not refresh_flag:

            START_ON = True

            kp200_realdata['전저'] = 0.0
            kp200_realdata['전고'] = 0.0
            kp200_realdata['종가'] = 0.0
            kp200_realdata['피봇'] = 0.0
            kp200_realdata['시가'] = 0.0
            kp200_realdata['시가갭'] = 0.0
            kp200_realdata['저가'] = 0.0
            kp200_realdata['현재가'] = 0.0
            kp200_realdata['고가'] = 0.0
            kp200_realdata['대비'] = 0
            kp200_realdata['진폭'] = 0.0

            fut_realdata['선물코드'] = ''
            fut_realdata['KP200'] = 0.0
            fut_realdata['전저'] = 0.0
            fut_realdata['전고'] = 0.0
            fut_realdata['종가'] = 0.0
            fut_realdata['피봇'] = 0.0
            fut_realdata['시가'] = 0.0
            fut_realdata['시가갭'] = 0.0
            fut_realdata['저가'] = 0.0
            fut_realdata['현재가'] = 0.0
            fut_realdata['고가'] = 0.0
            fut_realdata['대비'] = 0
            fut_realdata['진폭'] = 0.0
            fut_realdata['거래량'] = 0
            fut_realdata['미결'] = 0
            fut_realdata['미결증감'] = 0

            item = QTableWidgetItem("{0}".format('0'))
            item.setTextAlignment(Qt.AlignCenter)
            self.tableWidget_fut.setItem(1, Futures_column.매수건수.value, item)

            item = QTableWidgetItem("{0}".format('0'))
            item.setTextAlignment(Qt.AlignCenter)
            self.tableWidget_fut.setItem(0, Futures_column.매수건수.value, item)

            item = QTableWidgetItem("{0}".format('0'))
            item.setTextAlignment(Qt.AlignCenter)
            self.tableWidget_fut.setItem(1, Futures_column.매도건수.value, item)

            item = QTableWidgetItem("{0}".format('0'))
            item.setTextAlignment(Qt.AlignCenter)
            self.tableWidget_fut.setItem(0, Futures_column.매도건수.value, item)

            item = QTableWidgetItem("{0}".format('0'))
            item.setTextAlignment(Qt.AlignCenter)
            self.tableWidget_fut.setItem(1, Futures_column.매수잔량.value, item)

            item = QTableWidgetItem("{0}".format('0'))
            item.setTextAlignment(Qt.AlignCenter)
            self.tableWidget_fut.setItem(0, Futures_column.매수잔량.value, item)

            item = QTableWidgetItem("{0}".format('0'))
            item.setTextAlignment(Qt.AlignCenter)
            self.tableWidget_fut.setItem(1, Futures_column.매도잔량.value, item)

            item = QTableWidgetItem("{0}".format('0'))
            item.setTextAlignment(Qt.AlignCenter)
            self.tableWidget_fut.setItem(0, Futures_column.매도잔량.value, item)

            item = QTableWidgetItem("{0:0.2f}".format(0.0))
            item.setTextAlignment(Qt.AlignCenter)
            self.tableWidget_fut.setItem(1, Futures_column.건수비.value, item)

            item = QTableWidgetItem("{0:0.2f}".format(0.0))
            item.setTextAlignment(Qt.AlignCenter)
            self.tableWidget_fut.setItem(0, Futures_column.건수비.value, item)

            item = QTableWidgetItem("{0:0.2f}".format(0.0))
            item.setTextAlignment(Qt.AlignCenter)
            self.tableWidget_fut.setItem(1, Futures_column.잔량비.value, item)

            item = QTableWidgetItem("{0:0.2f}".format(0.0))
            item.setTextAlignment(Qt.AlignCenter)
            self.tableWidget_fut.setItem(0, Futures_column.잔량비.value, item)

            item = QTableWidgetItem("{0:0.1f}".format(0.0))
            item.setTextAlignment(Qt.AlignCenter)
            self.tableWidget_fut.setItem(0, Futures_column.VR.value, item)

            item = QTableWidgetItem("{0:0.1f}".format(0.0))
            item.setTextAlignment(Qt.AlignCenter)
            self.tableWidget_fut.setItem(1, Futures_column.VR.value, item)

            item = QTableWidgetItem("{0}".format('0'))
            item.setTextAlignment(Qt.AlignCenter)
            self.tableWidget_quote.setItem(0, 0, item)

            item = QTableWidgetItem("{0}".format('0'))
            item.setTextAlignment(Qt.AlignCenter)
            self.tableWidget_quote.setItem(0, 1, item)

            item = QTableWidgetItem("{0}".format('0'))
            item.setTextAlignment(Qt.AlignCenter)
            self.tableWidget_quote.setItem(0, 2, item)

            item = QTableWidgetItem("{0}".format('0'))
            item.setTextAlignment(Qt.AlignCenter)
            self.tableWidget_quote.setItem(0, 3, item)

            item = QTableWidgetItem("{0}".format('0'))
            item.setTextAlignment(Qt.AlignCenter)
            self.tableWidget_quote.setItem(0, 4, item)

            item = QTableWidgetItem("{0}".format('0'))
            item.setTextAlignment(Qt.AlignCenter)
            self.tableWidget_quote.setItem(0, 5, item)

            item = QTableWidgetItem("{0}".format('0'))
            item.setTextAlignment(Qt.AlignCenter)
            self.tableWidget_quote.setItem(0, 6, item)

            item = QTableWidgetItem("{0}".format('0'))
            item.setTextAlignment(Qt.AlignCenter)
            self.tableWidget_quote.setItem(0, 7, item)

            item = QTableWidgetItem("{0}".format('0'))
            item.setTextAlignment(Qt.AlignCenter)
            self.tableWidget_quote.setItem(0, 8, item)

            item = QTableWidgetItem("{0}".format('0'))
            item.setTextAlignment(Qt.AlignCenter)
            self.tableWidget_quote.setItem(0, 9, item)

            item = QTableWidgetItem("{0}".format('0'))
            item.setTextAlignment(Qt.AlignCenter)
            self.tableWidget_quote.setItem(0, 10, item)

            item = QTableWidgetItem("{0}".format('0'))
            item.setTextAlignment(Qt.AlignCenter)
            self.tableWidget_quote.setItem(0, 11, item)

            item = QTableWidgetItem("{0}".format('0'))
            item.setTextAlignment(Qt.AlignCenter)
            self.tableWidget_quote.setItem(0, 12, item)

            item = QTableWidgetItem("{0}".format('0'))
            item.setTextAlignment(Qt.AlignCenter)
            self.tableWidget_supply.setItem(0, Supply_column.외인선옵.value - 1, item)

            item = QTableWidgetItem("{0}".format('0'))
            item.setTextAlignment(Qt.AlignCenter)
            self.tableWidget_supply.setItem(0, Supply_column.개인선옵.value - 1, item)

            item = QTableWidgetItem("{0}".format('0'))
            item.setTextAlignment(Qt.AlignCenter)
            self.tableWidget_supply.setItem(0, Supply_column.기관선옵.value - 1, item)

            item = QTableWidgetItem("{0}".format('0'))
            item.setTextAlignment(Qt.AlignCenter)
            self.tableWidget_supply.setItem(0, Supply_column.외인현물.value - 1, item)

            item = QTableWidgetItem("{0}".format('0'))
            item.setTextAlignment(Qt.AlignCenter)
            self.tableWidget_supply.setItem(0, Supply_column.프로그램.value - 1, item)

            item = QTableWidgetItem("{0}".format('0'))
            item.setTextAlignment(Qt.AlignCenter)
            self.tableWidget_supply.setItem(0, Supply_column.프로그램.value, item)
        else:
            pass

        # 지수선물 마스터조회 API용
        XQ = t8432(parent=self)
        XQ.Query(구분='F')

        if self.checkBox_realtime.isChecked():

            # 주야간 선물/옵션요청 선택(주간=FC0/OC0, 야간=NC0/EC0)
            if 4 < int(current_str[0:2]) < 17:

                if int(current_str[0:2]) == 8 and int(current_str[3:5]) <= 59:
                    pre_start = True
                else:
                    pass

                # 옵션 전광판
                XQ = t2301(parent=self)
                XQ.Query(월물=month_str, 미니구분='G')

                start_hour = 9

                print('주간 선물/옵션 실시간요청...')

            else:
                overnight = True

                # 옵션 전광판
                XQ = t2301(parent=self)
                XQ.Query(월물=month_str, 미니구분='G')

                start_hour = 18

                print('야간 선물/옵션 실시간요청...')
        else:

            # 옵션 전광판
            XQ = t2301(parent=self)
            XQ.Query(월물=month_str, 미니구분='G')

            print('주간 선물/옵션 로그요청...')

    def SaveResult(self):

        now = time.localtime()
        times = "%04d-%02d-%02d-%02d-%02d-%02d" % \
                (now.tm_year, now.tm_mon, now.tm_mday, now.tm_hour, now.tm_min, now.tm_sec)

        file = open('skybot.log', 'w')
        text = self.textBrowser.toPlainText()
        file.write(text)
        file.close()

        if df_cme.empty:

            pass
        else:
            fut_csv = "Futures 전광판 {}{}".format(times, '.csv')
            temp = df_cme.append(df_futures, ignore_index=True)
            # temp = pd.concat([df_cme, df_futures], ignore_index=True)
            temp.to_csv(fut_csv, encoding='ms949')

            kp200_graph_csv = "KP200 Graph {}{}".format(times, '.csv')
            df_plotdata_kp200.to_csv(kp200_graph_csv, encoding='ms949')

            fut_graph_csv = "Fut Graph {}{}".format(times, '.csv')
            df_plotdata_fut.to_csv(fut_graph_csv, encoding='ms949')

        if df_cm_call.empty:

            pass
        else:
            self.call_open_check()

            call_csv = "Call 전광판 {}{}".format(times, '.csv')
            df_cm_call.loc[0:, '행사가':].to_csv(call_csv, encoding='ms949')

            call_graph_csv = "Call Graph {}{}".format(times, '.csv')
            df_plotdata_cm_call.to_csv(call_graph_csv, encoding='ms949')

            self.put_open_check()

            put_csv = "Put 전광판 {}{}".format(times, '.csv')
            df_cm_put.loc[0:, '행사가':].to_csv(put_csv, encoding='ms949')

            put_graph_csv = "Put Graph {}{}".format(times, '.csv')
            df_plotdata_cm_put.to_csv(put_graph_csv, encoding='ms949')

            call_volume_csv = "Call Volume {}{}".format(times, '.csv')
            df_plotdata_cm_call_volume.to_csv(call_volume_csv, encoding='ms949')

            put_volume_csv = "Put Volume {}{}".format(times, '.csv')
            df_plotdata_cm_put_volume.to_csv(put_volume_csv, encoding='ms949')

            self.image_grab()

        if overnight:

            #self.timer.stop()
            print('All Timer is stopped !!!')
            '''
            if self.plot_worker.isRunning():
                self.plot_worker.terminate()
                print('Plot Thread is terminated...')
            '''
            print('서버연결을 Release 합니다.')
            self.parent.connection.logout()
            self.parent.connection.disconnect()
            self.parent.statusbar.showMessage("서버연결을 Release 합니다.")
        else:
            self.parent.connection.logout()
            self.parent.statusbar.showMessage("로그아웃 합니다.")

    def RemoveCode(self):

        self.image_grab()

        file = open('skybot.log', 'w')
        text = self.textBrowser.toPlainText()
        file.write(text)
        file.close()        

########################################################################################################################

########################################################################################################################
Ui_차월물옵션전광판, QtBaseClass_차월물옵션전광판 = uic.loadUiType(UI_DIR + "차월물옵션전광판.ui")
class 화면_차월물옵션전광판(QDialog, Ui_차월물옵션전광판):
    def __init__(self, parent=None):
        super(화면_차월물옵션전광판, self).__init__(parent,
                                          flags=Qt.WindowMinimizeButtonHint | Qt.WindowMaximizeButtonHint | Qt.WindowCloseButtonHint)
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.setupUi(self)

        title = '차월물 옵션전광판 ' + '(' + today_str_title + ')'
        self.setWindowTitle(title)

        self.parent = parent

        self.t8416_callworker = t8416_NM_Call_Worker()
        self.t8416_callworker.finished.connect(self.t8416_call_request)

        self.t8416_putworker = t8416_NM_Put_Worker()
        self.t8416_putworker.finished.connect(self.t8416_put_request)

        # call tablewidget 초기화
        self.tableWidget_call.setRowCount(nRowCount)
        self.tableWidget_call.setColumnCount(Option_column.OID.value + 1)
        self.tableWidget_call.setHorizontalHeaderLabels(
            ['▲', '행사가', '↑/↓', '기준가', '월저', '월고', '전저', '전고', '종가', '피봇', '시가', '시가갭', '저가', '현재가', '고가',
             '대비', '진폭', '거래량', 'OIΔ'])
        self.tableWidget_call.clearContents()

        global nm_call_ckbox, nm_put_ckbox

        nm_call_ckbox = []

        for i in range(nRowCount):
            nm_call_ckbox.append(QCheckBox())
            self.tableWidget_call.setCellWidget(i, 0, nm_call_ckbox[i])

        self.tableWidget_call.resizeColumnsToContents()
        self.tableWidget_call.setColumnWidth(0, 15)

        # put tablewidget 초기화
        self.tableWidget_put.setRowCount(nRowCount)
        self.tableWidget_put.setColumnCount(Option_column.OID.value + 1)
        self.tableWidget_put.setHorizontalHeaderLabels(
            ['▼', '행사가', '↑/↓', '기준가', '월저', '월고', '전저', '전고', '종가', '피봇', '시가', '시가갭', '저가', '현재가', '고가',
             '대비', '진폭', '거래량', 'OIΔ'])
        self.tableWidget_put.clearContents()

        nm_put_ckbox = []

        for i in range(nRowCount):
            nm_put_ckbox.append(QCheckBox())
            self.tableWidget_put.setCellWidget(i, 0, nm_put_ckbox[i])

        self.tableWidget_put.resizeColumnsToContents()
        self.tableWidget_put.setColumnWidth(0, 15)

        # Quote tablewidget 초기화
        self.tableWidget_quote.setRowCount(1)
        self.tableWidget_quote.setColumnCount(Quote_column.호가종합.value)
        self.tableWidget_quote.setHorizontalHeaderLabels(['C-MSCC', 'C-MDCC', 'C-MSCR', 'C-MDCR',
                                                          'P-MSCC', 'P-MDCC', 'P-MSCR', 'P-MDCR', '콜건수비', '콜잔량비',
                                                          '풋건수비', '풋잔량비', '호가 ∑(CRΔ/RRΔ)'])
        self.tableWidget_quote.verticalHeader().setVisible(False)
        header = self.tableWidget_quote.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeToContents)
        header.setSectionResizeMode(12, QHeaderView.Stretch)
        self.tableWidget_quote.verticalHeader().setStretchLastSection(True)
        self.tableWidget_quote.clearContents()

        for i in range(nRowCount):
            for j in range(self.tableWidget_call.columnCount() - 1):
                item = QTableWidgetItem("{0}".format(''))
                self.tableWidget_call.setItem(i, j + 1, item)
                self.tableWidget_call.item(i, j + 1).setBackground(QBrush(검정색))

        for i in range(nRowCount):
            for j in range(self.tableWidget_put.columnCount() - 1):
                item = QTableWidgetItem("{0}".format(''))
                self.tableWidget_put.setItem(i, j + 1, item)
                self.tableWidget_put.item(i, j + 1).setBackground(QBrush(검정색))

        # 컬럼 헤더 click시 Event 처리용.
        call_h_header = self.tableWidget_call.horizontalHeader()
        call_h_header.sectionClicked.connect(self._call_horizontal_header_clicked)

        put_h_header = self.tableWidget_put.horizontalHeader()
        put_h_header.sectionClicked.connect(self._put_horizontal_header_clicked)

        call_v_header = self.tableWidget_call.verticalHeader()
        call_v_header.sectionClicked.connect(self._call_vertical_header_clicked)

        put_v_header = self.tableWidget_put.verticalHeader()
        put_v_header.sectionClicked.connect(self._put_vertical_header_clicked)

        self.tableWidget_call.cellClicked.connect(self._calltable_cell_clicked)
        self.tableWidget_put.cellClicked.connect(self._puttable_cell_clicked)

        self.tableWidget_call.verticalScrollBar().valueChanged.connect(self._calltable_vertical_scroll_position)
        self.tableWidget_put.verticalScrollBar().valueChanged.connect(self._puttable_vertical_scroll_position)

        # QuoteView 시그날/슬롯
        self.checkBox_quoteview.stateChanged.connect(self.quoteview_state_changed)

        current = datetime.datetime.now()
        current_str = current.strftime('%H:%M:%S')

        # 주야간 선물/옵션요청 선택(주간=FC0/OC0, 야간=NC0/EC0)
        if 4 < int(current_str[0:2]) < 16:

            df_plotdata_nm_call = DataFrame(index=range(0, nRowCount), columns=range(0, 396))
            df_plotdata_nm_put = DataFrame(index=range(0, nRowCount), columns=range(0, 396))

        else:

            df_plotdata_nm_call = DataFrame(index=range(0, nRowCount), columns=range(0, 661))
            df_plotdata_nm_put = DataFrame(index=range(0, nRowCount), columns=range(0, 661))

        self.jif = JIF(parent=self)
        self.jif.AdviseRealData('0')
        print('장운영정보를 요청합니다.')

        # 옵션 전광판
        XQ = t2301(parent=self)
        XQ.Query(월물=nm_month_str, 미니구분='G')
        print('차월물 옵션전광판 데이타를 요청합니다.')
    '''
    @pyqtSlot(int)
    def quoteview_state_changed(self, int):

        pass
    '''
    @pyqtSlot(int)
    def _call_horizontal_header_clicked(self, idx):

        col_text = self.tableWidget_call.horizontalHeaderItem(idx).text()

        if col_text.find('*') == -1:
            item = QTableWidgetItem(col_text + '*')
            self.tableWidget_call.setHorizontalHeaderItem(idx, item)
            print("call header column.. ", idx, col_text)
        else:
            item = QTableWidgetItem(col_text.replace('*', ''))
            self.tableWidget_call.setHorizontalHeaderItem(idx, item)
            print("call header column.. ", idx, col_text)

        self.tableWidget_call.resizeColumnsToContents()
        self.tableWidget_call.setColumnWidth(0, 15)

        return

    @pyqtSlot(int)
    def _put_horizontal_header_clicked(self, idx):

        col_text = self.tableWidget_put.horizontalHeaderItem(idx).text()

        if col_text.find('*') == -1:
            item = QTableWidgetItem(col_text + '*')
            self.tableWidget_put.setHorizontalHeaderItem(idx, item)
            print("call header column.. ", idx, col_text)
        else:
            item = QTableWidgetItem(col_text.replace('*', ''))
            self.tableWidget_put.setHorizontalHeaderItem(idx, item)
            print("call header column.. ", idx, col_text)

        self.tableWidget_put.resizeColumnsToContents()
        self.tableWidget_put.setColumnWidth(0, 15)

        return

    @pyqtSlot(int)
    def _call_vertical_header_clicked(self, idx):

        print(idx)

        return

    @pyqtSlot(int)
    def _put_vertical_header_clicked(self, idx):

        print(idx)

        return

    @pyqtSlot(int, int)
    def _calltable_cell_clicked(self, row, col):

        cell = self.tableWidget_call.item(row, col)

        if cell is not None:

            txt = "call table cell clicked = ({0},{1}) ==>{2}<==".format(row, col, cell.text())

            if atm_str != '':

                if row < atm_index:
                    call_positionCell = self.tableWidget_call.item(atm_index + 4, 1)
                else:
                    call_positionCell = self.tableWidget_call.item(atm_index - 4, 1)

                self.tableWidget_call.scrollToItem(call_positionCell)
            else:
                pass

        else:
            txt = "call table cell clicked = ({0},{1}) ==>None type<==".format(row, col)

        print(txt)

        return

    @pyqtSlot(int, int)
    def _puttable_cell_clicked(self, row, col):

        cell = self.tableWidget_put.item(row, col)

        if cell is not None:

            txt = "put table cell clicked = ({0},{1}) ==>{2}<==".format(row, col, cell.text())

            if atm_str != '':

                if row < atm_index:
                    put_positionCell = self.tableWidget_put.item(atm_index + 3, 1)
                else:
                    put_positionCell = self.tableWidget_put.item(atm_index - 4, 1)

                self.tableWidget_put.scrollToItem(put_positionCell)
            else:
                pass

        else:
            txt = "put table cell clicked = ({0},{1}) ==>None type<==".format(row, col)

        print(txt)

        return

    @pyqtSlot(int)
    def _calltable_vertical_scroll_position(self, row):

        global nm_call_scroll_position
        nm_call_scroll_position = row

        self.tableWidget_call.resizeColumnsToContents()
        self.tableWidget_call.setColumnWidth(0, 15)

        print('call scroll position -----> ', nm_call_scroll_position)

        return

    @pyqtSlot(int)
    def _puttable_vertical_scroll_position(self, row):

        global nm_put_scroll_position
        nm_put_scroll_position = row

        self.tableWidget_put.resizeColumnsToContents()
        self.tableWidget_put.setColumnWidth(0, 15)

        print('put scroll position -----> ', nm_put_scroll_position)

        return

    @pyqtSlot(object)
    def t8415_call_request(self, data):
        try:

            XQ = t8415(parent=self)
            XQ.Query(단축코드=nm_call_code[data], 시작일자=month_firstday_str, 종료일자=today_str)

        except:
            pass

    @pyqtSlot(object)
    def t8415_put_request(self, data):
        try:

            XQ = t8415(parent=self)
            XQ.Query(단축코드=nm_put_code[data], 시작일자=month_firstday_str, 종료일자=today_str)

        except:
            pass

    @pyqtSlot(object)
    def t8416_call_request(self, data):
        try:

            XQ = t8416(parent=self)
            XQ.Query(단축코드=nm_call_code[data], 시작일자=month_firstday_str, 종료일자=today_str)

        except:
            pass

    @pyqtSlot(object)
    def t8416_put_request(self, data):
        try:

            XQ = t8416(parent=self)
            XQ.Query(단축코드=nm_put_code[data], 시작일자=month_firstday_str, 종료일자=today_str)

        except:
            pass

    @pyqtSlot(dict)
    def update_data(self, data):
        try:
            start_time = timeit.default_timer()

            global nm_call_ol, nm_call_oh, nm_put_ol, nm_put_oh

            nm_call_open_count = 0
            nm_put_open_count = 0

            nm_call_ol_count = 0
            nm_call_oh_count = 0
            nm_put_ol_count = 0
            nm_put_oh_count = 0

            actval_length = len(data.keys())

            call_gap_percent_local = [0] * actval_length
            put_gap_percent_local = [0] * actval_length

            # 데이타 처리
            for actval, infos in data.items():

                index = nm_call_actval.index(actval)

                if infos[0]:
                    nm_call_open_count += 1
                else:
                    pass

                if infos[1]:
                    nm_call_ol_count += 1
                    nm_call_ol[index] = True
                else:
                    pass

                if infos[2]:
                    nm_call_oh_count += 1
                    nm_call_oh[index] = True
                else:
                    pass

                if infos[3]:
                    call_gap_percent_local[index] = infos[3]
                    item = QTableWidgetItem("{0:0.2f}({1:0.0f}%)".format(df_nm_call.iloc[index]['시가'] - df_nm_call.iloc[index]['종가'], infos[3]))
                    item.setTextAlignment(Qt.AlignCenter)
                    self.tableWidget_call.setItem(index, Option_column.시가갭.value, item)
                else:
                    call_gap_percent_local[index] = 0.0

                if infos[4]:
                    nm_put_open_count += 1
                else:
                    pass

                if infos[5]:
                    nm_put_ol_count += 1
                    nm_put_ol[index] = True
                else:
                    pass

                if infos[6]:
                    nm_put_oh_count += 1
                    nm_put_oh[index] = True
                else:
                    pass

                if infos[7]:
                    put_gap_percent_local[index] = infos[7]
                    item = QTableWidgetItem("{0:0.2f}({1:0.0f}%)".format(df_nm_put.iloc[index]['시가'] - df_nm_put.iloc[index]['종가'], infos[7]))
                    item.setTextAlignment(Qt.AlignCenter)
                    self.tableWidget_put.setItem(index, Option_column.시가갭.value, item)
                else:
                    put_gap_percent_local[index] = 0.0

            # 종합데이타 표시
            new_actval = '행사가' + '(' + repr(nm_call_open_count) + ')'

            if new_actval != self.tableWidget_call.horizontalHeaderItem(1).text():
                item = QTableWidgetItem(new_actval)
                self.tableWidget_call.setHorizontalHeaderItem(1, item)
            else:
                pass

            new_oloh = repr(nm_call_ol_count) + '/' + repr(nm_call_oh_count)

            if new_oloh != self.tableWidget_call.horizontalHeaderItem(2).text():
                item = QTableWidgetItem(new_oloh)
                self.tableWidget_call.setHorizontalHeaderItem(2, item)
            else:
                pass

            new_actval = '행사가' + '(' + repr(nm_put_open_count) + ')'

            if new_actval != self.tableWidget_put.horizontalHeaderItem(1).text():
                item = QTableWidgetItem(new_actval)
                self.tableWidget_put.setHorizontalHeaderItem(1, item)
            else:
                pass

            new_oloh = repr(nm_put_ol_count) + '/' + repr(nm_put_oh_count)

            if new_oloh != self.tableWidget_put.horizontalHeaderItem(2).text():
                item = QTableWidgetItem(new_oloh)
                self.tableWidget_put.setHorizontalHeaderItem(2, item)
            else:
                pass

            while call_gap_percent_local.count(0) > 0:
                call_gap_percent_local.remove(0)

            if not call_gap_percent_local:
                pass
            else:
                tmp = np.array(call_gap_percent_local)
                mean = int(round(np.mean(tmp), 1))
                call_str = '시가갭' + '(' + repr(mean) + '%' + ')'

            if call_str != self.tableWidget_call.horizontalHeaderItem(Option_column.시가갭.value).text():
                item = QTableWidgetItem(call_str)
                self.tableWidget_call.setHorizontalHeaderItem(Option_column.시가갭.value, item)
                self.tableWidget_call.resizeColumnsToContents()
                self.tableWidget_call.setColumnWidth(0, 15)
            else:
                pass

            while put_gap_percent_local.count(0) > 0:
                put_gap_percent_local.remove(0)

            if not put_gap_percent_local:
                pass
            else:
                tmp = np.array(put_gap_percent_local)
                mean = int(round(np.mean(tmp), 1))
                put_str = '시가갭' + '(' + repr(mean) + '%' + ')'

            if put_str != self.tableWidget_put.horizontalHeaderItem(Option_column.시가갭.value).text():
                item = QTableWidgetItem(put_str)
                self.tableWidget_put.setHorizontalHeaderItem(Option_column.시가갭.value, item)
                self.tableWidget_put.resizeColumnsToContents()
                self.tableWidget_put.setColumnWidth(0, 15)
            else:
                pass

            # 데이타 Coloring 처리 및 표시
            if nm_call_scroll_position < nCount_nm_option_pairs:

                if nCount_nm_option_pairs - 9 < nm_call_scroll_position < nCount_nm_option_pairs:

                    call_scroll_end_position = nCount_nm_option_pairs
                else:
                    call_scroll_end_position = nm_call_scroll_position + 9

                for index in range(nm_call_scroll_position, call_scroll_end_position):

                    # clear call color
                    self.tableWidget_call.item(index, Option_column.OLOH.value).setBackground(QBrush(기본바탕색))
                    self.tableWidget_call.item(index, Option_column.OLOH.value).setForeground(QBrush(검정색))

                    self.tableWidget_call.item(index, Option_column.기준가.value).setBackground(QBrush(기본바탕색))
                    self.tableWidget_call.item(index, Option_column.기준가.value).setForeground(QBrush(검정색))

                    self.tableWidget_call.item(index, Option_column.월저.value).setBackground(QBrush(기본바탕색))
                    self.tableWidget_call.item(index, Option_column.월저.value).setForeground(QBrush(검정색))

                    self.tableWidget_call.item(index, Option_column.월고.value).setBackground(QBrush(기본바탕색))
                    self.tableWidget_call.item(index, Option_column.월고.value).setForeground(QBrush(검정색))

                    self.tableWidget_call.item(index, Option_column.전저.value).setBackground(QBrush(기본바탕색))
                    self.tableWidget_call.item(index, Option_column.전저.value).setForeground(QBrush(검정색))

                    self.tableWidget_call.item(index, Option_column.전고.value).setBackground(QBrush(기본바탕색))
                    self.tableWidget_call.item(index, Option_column.전고.value).setForeground(QBrush(검정색))

                    self.tableWidget_call.item(index, Option_column.종가.value).setBackground(QBrush(기본바탕색))
                    self.tableWidget_call.item(index, Option_column.종가.value).setForeground(QBrush(검정색))

                    self.tableWidget_call.item(index, Option_column.피봇.value).setBackground(QBrush(기본바탕색))
                    self.tableWidget_call.item(index, Option_column.피봇.value).setForeground(QBrush(검정색))

                    self.tableWidget_call.item(index, Option_column.시가.value).setBackground(QBrush(기본바탕색))
                    self.tableWidget_call.item(index, Option_column.시가.value).setForeground(QBrush(검정색))

                    self.tableWidget_call.item(index, Option_column.저가.value).setBackground(QBrush(기본바탕색))
                    self.tableWidget_call.item(index, Option_column.저가.value).setForeground(QBrush(검정색))

                    self.tableWidget_call.item(index, Option_column.고가.value).setBackground(QBrush(기본바탕색))
                    self.tableWidget_call.item(index, Option_column.고가.value).setForeground(QBrush(검정색))

                    self.tableWidget_call.item(index, Option_column.대비.value).setBackground(QBrush(기본바탕색))
                    self.tableWidget_call.item(index, Option_column.대비.value).setForeground(QBrush(검정색))

                    self.tableWidget_call.item(index, Option_column.현재가.value).setBackground(QBrush(옅은회색))

                    # 등가 coloring
                    if index == atm_index:
                        self.tableWidget_call.item(index, Option_column.행사가.value).setBackground(QBrush(노란색))
                    else:
                        if df_nm_call.iloc[index]['저가'] < df_nm_call.iloc[index]['고가']:
                            self.tableWidget_call.item(index, Option_column.행사가.value).setBackground(QBrush(녹색))
                        else:
                            self.tableWidget_call.item(index, Option_column.행사가.value).setBackground(QBrush(기본바탕색))

                    if df_nm_call.iloc[index]['시가'] > 0:
                        if df_nm_call.iloc[index]['시가'] < df_nm_call.iloc[index]['현재가']:
                            self.tableWidget_call.item(index, Option_column.현재가.value).setForeground(QBrush(적색))
                        elif df_nm_call.iloc[index]['시가'] > df_nm_call.iloc[index]['현재가']:
                            self.tableWidget_call.item(index, Option_column.현재가.value).setForeground(QBrush(청색))
                        else:
                            self.tableWidget_call.item(index, Option_column.현재가.value).setForeground(QBrush(검정색))
                    else:
                        self.tableWidget_call.item(index, Option_column.현재가.value).setForeground(QBrush(검정색))

                    # call OL/OH
                    if nm_call_ol[index] and not nm_call_oh[index]:

                        df_nm_call.loc[index, 'OLOH'] = '↑'
                        item = QTableWidgetItem("{0}".format(df_nm_call.iloc[index]['OLOH']))
                        item.setTextAlignment(Qt.AlignCenter)
                        item.setBackground(QBrush(적색))
                        item.setForeground(QBrush(흰색))
                        self.tableWidget_call.setItem(index, Option_column.OLOH.value, item)

                    elif not nm_call_ol[index] and nm_call_oh[index]:

                        df_nm_call.loc[index, 'OLOH'] = '↓'
                        item = QTableWidgetItem("{0}".format(df_nm_call.iloc[index]['OLOH']))
                        item.setTextAlignment(Qt.AlignCenter)
                        item.setBackground(QBrush(청색))
                        item.setForeground(QBrush(흰색))
                        self.tableWidget_call.setItem(index, Option_column.OLOH.value, item)

                    else:

                        df_nm_call.loc[index, 'OLOH'] = ''
                        item = QTableWidgetItem("{0}".format(df_nm_call.iloc[index]['OLOH']))
                        item.setTextAlignment(Qt.AlignCenter)
                        self.tableWidget_call.setItem(index, Option_column.OLOH.value, item)

                    # call coloring job

            else:
                pass

            if nm_put_scroll_position < nCount_nm_option_pairs:

                if nCount_nm_option_pairs - 9 < nm_put_scroll_position < nCount_nm_option_pairs:

                    put_scroll_end_position = nCount_nm_option_pairs
                else:
                    put_scroll_end_position = nm_put_scroll_position + 9

                for index in range(nm_put_scroll_position, put_scroll_end_position):

                    # clear put color
                    self.tableWidget_put.item(index, Option_column.OLOH.value).setBackground(QBrush(기본바탕색))
                    self.tableWidget_put.item(index, Option_column.OLOH.value).setForeground(QBrush(검정색))

                    self.tableWidget_put.item(index, Option_column.기준가.value).setBackground(QBrush(기본바탕색))
                    self.tableWidget_put.item(index, Option_column.기준가.value).setForeground(QBrush(검정색))

                    self.tableWidget_put.item(index, Option_column.월저.value).setBackground(QBrush(기본바탕색))
                    self.tableWidget_put.item(index, Option_column.월저.value).setForeground(QBrush(검정색))

                    self.tableWidget_put.item(index, Option_column.월고.value).setBackground(QBrush(기본바탕색))
                    self.tableWidget_put.item(index, Option_column.월고.value).setForeground(QBrush(검정색))

                    self.tableWidget_put.item(index, Option_column.전저.value).setBackground(QBrush(기본바탕색))
                    self.tableWidget_put.item(index, Option_column.전저.value).setForeground(QBrush(검정색))

                    self.tableWidget_put.item(index, Option_column.전고.value).setBackground(QBrush(기본바탕색))
                    self.tableWidget_put.item(index, Option_column.전고.value).setForeground(QBrush(검정색))

                    self.tableWidget_put.item(index, Option_column.종가.value).setBackground(QBrush(기본바탕색))
                    self.tableWidget_put.item(index, Option_column.종가.value).setForeground(QBrush(검정색))

                    self.tableWidget_put.item(index, Option_column.피봇.value).setBackground(QBrush(기본바탕색))
                    self.tableWidget_put.item(index, Option_column.피봇.value).setForeground(QBrush(검정색))

                    self.tableWidget_put.item(index, Option_column.시가.value).setBackground(QBrush(기본바탕색))
                    self.tableWidget_put.item(index, Option_column.시가.value).setForeground(QBrush(검정색))

                    self.tableWidget_put.item(index, Option_column.저가.value).setBackground(QBrush(기본바탕색))
                    self.tableWidget_put.item(index, Option_column.저가.value).setForeground(QBrush(검정색))

                    self.tableWidget_put.item(index, Option_column.고가.value).setBackground(QBrush(기본바탕색))
                    self.tableWidget_put.item(index, Option_column.고가.value).setForeground(QBrush(검정색))

                    self.tableWidget_put.item(index, Option_column.대비.value).setBackground(QBrush(기본바탕색))
                    self.tableWidget_put.item(index, Option_column.대비.value).setForeground(QBrush(검정색))

                    self.tableWidget_put.item(index, Option_column.현재가.value).setBackground(QBrush(옅은회색))

                    # 등가 coloring
                    if index == atm_index:
                        self.tableWidget_put.item(index, Option_column.행사가.value).setBackground(QBrush(노란색))
                    else:
                        if df_nm_put.iloc[index]['저가'] < df_nm_put.iloc[index]['고가']:
                            self.tableWidget_put.item(index, Option_column.행사가.value).setBackground(QBrush(녹색))
                        else:
                            self.tableWidget_put.item(index, Option_column.행사가.value).setBackground(QBrush(기본바탕색))

                    if df_nm_put.iloc[index]['시가'] > 0:
                        if df_nm_put.iloc[index]['시가'] < df_nm_put.iloc[index]['현재가']:
                            self.tableWidget_put.item(index, Option_column.현재가.value).setForeground(QBrush(적색))
                        elif df_nm_put.iloc[index]['시가'] > df_nm_put.iloc[index]['현재가']:
                            self.tableWidget_put.item(index, Option_column.현재가.value).setForeground(QBrush(청색))
                        else:
                            self.tableWidget_put.item(index, Option_column.현재가.value).setForeground(QBrush(검정색))
                    else:
                        self.tableWidget_put.item(index, Option_column.현재가.value).setForeground(QBrush(검정색))

                    # put OL/OH
                    if nm_put_ol[index] and not nm_put_oh[index]:

                        df_nm_put.loc[index, 'OLOH'] = '↑'
                        item = QTableWidgetItem("{0}".format(df_nm_put.iloc[index]['OLOH']))
                        item.setTextAlignment(Qt.AlignCenter)
                        item.setBackground(QBrush(청색))
                        item.setForeground(QBrush(흰색))
                        self.tableWidget_put.setItem(index, Option_column.OLOH.value, item)

                    elif not nm_put_ol[index] and nm_put_oh[index]:

                        df_nm_put.loc[index, 'OLOH'] = '↓'
                        item = QTableWidgetItem("{0}".format(df_nm_put.iloc[index]['OLOH']))
                        item.setTextAlignment(Qt.AlignCenter)
                        item.setBackground(QBrush(적색))
                        item.setForeground(QBrush(흰색))
                        self.tableWidget_put.setItem(index, Option_column.OLOH.value, item)

                    else:

                        df_nm_put.loc[index, 'OLOH'] = ''
                        item = QTableWidgetItem("{0}".format(df_nm_put.iloc[index]['OLOH']))
                        item.setTextAlignment(Qt.AlignCenter)
                        self.tableWidget_put.setItem(index, Option_column.OLOH.value, item)

                    # put coloring job
            else:
                pass

            dt = datetime.datetime.now()
            str = '[{0:02d}:{1:02d}:{2:02d}] NM data update 처리시간 --> {3:0.2f} ms...\r'.\
                format(dt.hour, dt.minute, (dt.second - time_delta) % 60, (timeit.default_timer() - start_time) * 1000)
            self.textBrowser.append(str)

        except:
            pass

    def set_call_atm_row_color(self, rowIndex, brush):

        for j in range(self.tableWidget_call.columnCount() - 1):
            self.tableWidget_call.item(rowIndex, j + 1).setBackground(brush)

    def set_put_atm_row_color(self, rowIndex, brush):

        for j in range(self.tableWidget_put.columnCount() - 1):
            self.tableWidget_put.item(rowIndex, j + 1).setBackground(brush)

    def within_n_tick(self, source, target, n):

        if round((target - 0.01 * n), 2) <= source <= round((target + 0.01 * n), 2):
            return True
        else:
            return False

    def calc_pivot(self, jl, jh, jc, do):

        tmp = (jl + jh + jc) / 3 + (do - jc)
        pivot = round(tmp, 2)

        return pivot

    def find_ATM(self, kp200):

        # temp = round(kp200 / 2.5, 0) * 2.5
        temp = math.floor(round(kp200 / 2.5, 0) * 2.5)
        str_atm = '{0:0.0f}'.format(temp)

        return str_atm

    def OnReceiveData(self, szTrCode, result):

        global gmshcode

        if szTrCode == 't2301':

            block, df, df1 = result
            call_result = []

            global atm_index
            global df_plotdata_nm_call, df_plotdata_nm_put

            for i in range(len(df)):

                행사가 = df['행사가'][i]
                item = QTableWidgetItem("{0:^5}".format(df['행사가'][i]))
                item.setTextAlignment(Qt.AlignCenter)
                self.tableWidget_call.setItem(i, Option_column.행사가.value, item)

                OLOH = ''
                item = QTableWidgetItem("{0}".format(OLOH))
                item.setTextAlignment(Qt.AlignCenter)
                self.tableWidget_call.setItem(i, Option_column.OLOH.value, item)

                피봇 = 0.0
                item = QTableWidgetItem("{0:0.2f}".format(피봇))
                item.setTextAlignment(Qt.AlignCenter)
                self.tableWidget_call.setItem(i, Option_column.피봇.value, item)

                시가 = df['시가'][i]
                item = QTableWidgetItem("{0:0.2f}".format(df['시가'][i]))
                item.setTextAlignment(Qt.AlignCenter)
                self.tableWidget_call.setItem(i, Option_column.시가.value, item)

                #df_plotdata_nm_call.iloc[i][0] = 시가

                시가갭 = 0
                item = QTableWidgetItem("{0}".format(시가갭))
                item.setTextAlignment(Qt.AlignCenter)
                self.tableWidget_call.setItem(i, Option_column.시가갭.value, item)

                저가 = df['저가'][i]
                item = QTableWidgetItem("{0:0.2f}".format(df['저가'][i]))
                item.setTextAlignment(Qt.AlignCenter)
                self.tableWidget_call.setItem(i, Option_column.저가.value, item)

                현재가 = df['현재가'][i]
                item = QTableWidgetItem("{0:0.2f}".format(df['현재가'][i]))
                item.setTextAlignment(Qt.AlignCenter)
                item.setBackground(QBrush(옅은회색))
                item.setForeground(QBrush(검정색))
                self.tableWidget_call.setItem(i, Option_column.현재가.value, item)

                고가 = df['고가'][i]
                item = QTableWidgetItem("{0:0.2f}".format(df['고가'][i]))
                item.setTextAlignment(Qt.AlignCenter)
                self.tableWidget_call.setItem(i, Option_column.고가.value, item)

                if round(저가, 2) < round(고가, 2):
                    item = QTableWidgetItem("{0:^5}".format(행사가))
                    item.setTextAlignment(Qt.AlignCenter)
                    item.setBackground(QBrush(녹색))
                    item.setForeground(QBrush(검정색))
                    self.tableWidget_call.setItem(i, Option_column.행사가.value, item)
                    nm_call_code_on.append('ON')
                else:
                    nm_call_code_on.append('OFF')

                대비 = 0
                item = QTableWidgetItem("{0}".format(대비))
                item.setTextAlignment(Qt.AlignCenter)
                self.tableWidget_call.setItem(i, Option_column.대비.value, item)

                진폭 = 0.0
                item = QTableWidgetItem("{0:0.2f}".format(진폭))
                item.setTextAlignment(Qt.AlignCenter)
                self.tableWidget_call.setItem(i, Option_column.진폭.value, item)

                미결 = df['미결제약정'][i]
                item = QTableWidgetItem("{0:0.0f}".format(df['미결제약정'][i] * df['현재가'][i]))
                item.setTextAlignment(Qt.AlignCenter)
                self.tableWidget_call.setItem(i, Option_column.OI.value, item)

                미결증감 = df['미결제약정증감'][i]
                item = QTableWidgetItem("{0:0.0f}".format(df['미결제약정증감'][i] * df['현재가'][i]))
                item.setTextAlignment(Qt.AlignCenter)
                self.tableWidget_call.setItem(i, Option_column.OID.value, item)

                if df['ATM구분'][i] == '1':

                    global atm_str

                    atm_str = 행사가
                    atm_index = i

                    global nm_call_ckbox

                    nm_call_ckbox[atm_index - 1].setCheckState(Qt.Checked)
                    nm_call_ckbox[atm_index].setCheckState(Qt.Checked)
                    nm_call_ckbox[atm_index + 1].setCheckState(Qt.Checked)

                    global selected_call

                    selected_call = [atm_index - 1, atm_index, atm_index + 1]

                    self.set_call_atm_row_color(atm_index, QBrush(옅은회색))

                    item = QTableWidgetItem("{0:^5}".format(행사가))
                    item.setTextAlignment(Qt.AlignCenter)
                    item.setBackground(QBrush(노란색))
                    item.setForeground(QBrush(검정색))
                    self.tableWidget_call.setItem(i, Option_column.행사가.value, item)
                else:
                    pass

                기준가 = 0.0
                월저 = 0.0
                월고 = 0.0
                전저 = 0.0
                전고 = 0.0
                종가 = 0.0

                lst = [행사가, OLOH, 기준가, 월저, 월고, 전저, 전고, 종가, 피봇, 시가, 시가갭, 저가, 현재가, 고가, 대비, 진폭, 미결, 미결증감]
                call_result.append(lst)

            global df_nm_call
            columns = ['행사가', 'OLOH', '기준가', '월저', '월고', '전저', '전고', '종가', '피봇', '시가', '시가갭', '저가', '현재가', '고가', '대비',
                       '진폭', '미결', '미결증감']
            df_nm_call = DataFrame(data=call_result, columns=columns)

            print(df_nm_call)

            global nm_call_행사가

            nm_call_행사가 = df_nm_call['행사가'].values.tolist()

            global nm_call_시가

            nm_call_시가 = df_nm_call['시가'].values.tolist()

            self.tableWidget_call.resizeColumnsToContents()
            self.tableWidget_call.setColumnWidth(0, 15)

            put_result = []

            for i in range(len(df1)):

                행사가 = df1['행사가'][i]
                item = QTableWidgetItem("{0:^5}".format(df1['행사가'][i]))
                item.setTextAlignment(Qt.AlignCenter)
                self.tableWidget_put.setItem(i, Option_column.행사가.value, item)

                OLOH = ''
                item = QTableWidgetItem("{0}".format(OLOH))
                item.setTextAlignment(Qt.AlignCenter)
                self.tableWidget_put.setItem(i, Option_column.OLOH.value, item)

                피봇 = 0.0
                item = QTableWidgetItem("{0:0.2f}".format(피봇))
                item.setTextAlignment(Qt.AlignCenter)
                self.tableWidget_put.setItem(i, Option_column.피봇.value, item)

                시가 = df1['시가'][i]
                item = QTableWidgetItem("{0:0.2f}".format(df1['시가'][i]))
                item.setTextAlignment(Qt.AlignCenter)
                self.tableWidget_put.setItem(i, Option_column.시가.value, item)

                #df_plotdata_nm_put.iloc[i][0] = 시가

                시가갭 = 0
                item = QTableWidgetItem("{0}".format(시가갭))
                item.setTextAlignment(Qt.AlignCenter)
                self.tableWidget_put.setItem(i, Option_column.시가갭.value, item)

                저가 = df1['저가'][i]
                item = QTableWidgetItem("{0:0.2f}".format(df1['저가'][i]))
                item.setTextAlignment(Qt.AlignCenter)
                self.tableWidget_put.setItem(i, Option_column.저가.value, item)

                현재가 = df1['현재가'][i]
                item = QTableWidgetItem("{0:0.2f}".format(df1['현재가'][i]))
                item.setTextAlignment(Qt.AlignCenter)
                item.setBackground(QBrush(옅은회색))
                item.setForeground(QBrush(검정색))
                self.tableWidget_put.setItem(i, Option_column.현재가.value, item)

                고가 = df1['고가'][i]
                item = QTableWidgetItem("{0:0.2f}".format(df1['고가'][i]))
                item.setTextAlignment(Qt.AlignCenter)
                self.tableWidget_put.setItem(i, Option_column.고가.value, item)

                if round(저가, 2) < round(고가, 2):
                    item = QTableWidgetItem("{0:^5}".format(행사가))
                    item.setTextAlignment(Qt.AlignCenter)
                    item.setBackground(QBrush(녹색))
                    item.setForeground(QBrush(검정색))
                    self.tableWidget_put.setItem(i, Option_column.행사가.value, item)
                    nm_put_code_on.append('ON')
                else:
                    nm_put_code_on.append('OFF')

                대비 = 0
                item = QTableWidgetItem("{0}".format(대비))
                item.setTextAlignment(Qt.AlignCenter)
                self.tableWidget_put.setItem(i, Option_column.대비.value, item)

                진폭 = 0.0
                item = QTableWidgetItem("{0:0.2f}".format(진폭))
                item.setTextAlignment(Qt.AlignCenter)
                self.tableWidget_put.setItem(i, Option_column.진폭.value, item)

                미결 = df1['미결제약정'][i]
                item = QTableWidgetItem("{0:0.0f}".format(df1['미결제약정'][i] * df1['현재가'][i]))
                item.setTextAlignment(Qt.AlignCenter)
                self.tableWidget_put.setItem(i, Option_column.OI.value, item)

                미결증감 = df1['미결제약정증감'][i]
                item = QTableWidgetItem("{0:0.0f}".format(df1['미결제약정증감'][i] * df1['현재가'][i]))
                item.setTextAlignment(Qt.AlignCenter)
                self.tableWidget_put.setItem(i, Option_column.OID.value, item)

                if df1['ATM구분'][i] == '1':

                    atm_str = 행사가
                    atm_index = i

                    global nm_put_ckbox

                    nm_put_ckbox[atm_index - 1].setCheckState(Qt.Checked)
                    nm_put_ckbox[atm_index].setCheckState(Qt.Checked)
                    nm_put_ckbox[atm_index + 1].setCheckState(Qt.Checked)

                    global selected_put

                    selected_put = [atm_index - 1, atm_index, atm_index + 1]

                    self.set_put_atm_row_color(atm_index, QBrush(옅은회색))

                    item = QTableWidgetItem("{0:^5}".format(행사가))
                    item.setTextAlignment(Qt.AlignCenter)
                    item.setBackground(QBrush(노란색))
                    item.setForeground(QBrush(검정색))
                    self.tableWidget_put.setItem(i, Option_column.행사가.value, item)
                else:
                    pass

                기준가 = 0.0
                월저 = 0.0
                월고 = 0.0
                전저 = 0.0
                전고 = 0.0
                종가 = 0.0

                lst = [행사가, OLOH, 기준가, 월저, 월고, 전저, 전고, 종가, 피봇, 시가, 시가갭, 저가, 현재가, 고가, 대비, 진폭, 미결, 미결증감]
                put_result.append(lst)

            global df_nm_put
            columns = ['행사가', 'OLOH', '기준가', '월저', '월고', '전저', '전고', '종가', '피봇', '시가', '시가갭', '저가', '현재가', '고가', '대비',
                       '진폭', '미결', '미결증감']
            df_nm_put = DataFrame(data=put_result, columns=columns)

            print(df_nm_put)

            global nm_put_행사가

            nm_put_행사가 = df_nm_put['행사가'].values.tolist()

            global nm_put_시가

            nm_put_시가 = df_nm_put['시가'].values.tolist()

            self.tableWidget_put.resizeColumnsToContents()
            self.tableWidget_put.setColumnWidth(0, 15)

            global nCount_nm_option_pairs
            nCount_nm_option_pairs = len(df1)

            # 실시간테이타 요청
            for i in range(nCount_nm_option_pairs):
                nm_call_code.append(df['콜옵션코드'][i])
                nm_put_code.append(df1['풋옵션코드'][i])
                nm_call_actval.append(df['콜옵션코드'][i][5:8])
                nm_put_actval.append(df1['풋옵션코드'][i][5:8])
                #self.nm_opt_real.AdviseRealData(df['콜옵션코드'][i])
                #self.nm_opt_real.AdviseRealData(df1['풋옵션코드'][i])

            # t8416 요청
            if today_str != month_firstday_str:
                self.t8416_callworker.start()
                self.t8416_callworker.daemon = True
            else:
                pass

                #self.color_worker.start()
                #self.color_worker.daemon = True

                #self.plot_worker.start()
                #self.plot_worker.daemon = True

        elif szTrCode == 't8415':

            block, df = result

            if block['단축코드'][0:3] == '201':

                for i in range(len(selected_call)):

                    if result['단축코드'][5:8] == df_nm_call.iloc[selected_call[i]]['행사가']:

                        pass
                    else:
                        pass

            elif block['단축코드'][0:3] == '301':

                for i in range(len(selected_put)):

                    if result['단축코드'][5:8] == df_nm_put.iloc[selected_put[i]]['행사가']:

                        pass
                    else:
                        pass
            else:
                pass

        elif szTrCode == 't8416':

            block, df = result

            global nm_call_t8416_count, nm_put_t8416_count
            global nm_call_gap_percent, nm_put_gap_percent

            global nm_call_기준가, nm_call_월저, nm_call_월고, nm_call_전저, nm_call_전고, nm_call_종가, nm_call_피봇
            global nm_put_기준가, nm_put_월저, nm_put_월고, nm_put_전저, nm_put_전고, nm_put_종가, nm_put_피봇

            global nm_actval_increased

            dt = datetime.datetime.now()

            if block['단축코드'] == '':

                if self.t8416_callworker.isRunning():

                    nm_call_기준가 = df_nm_call['기준가'].values.tolist()
                    nm_call_월저 = df_nm_call['월저'].values.tolist()
                    nm_call_월고 = df_nm_call['월고'].values.tolist()
                    nm_call_전저 = df_nm_call['전저'].values.tolist()
                    nm_call_전고 = df_nm_call['전고'].values.tolist()
                    nm_call_종가 = df_nm_call['종가'].values.tolist()
                    nm_call_피봇 = df_nm_call['피봇'].values.tolist()

                    self.t8416_callworker.terminate()
                    self.textBrowser.append('t8416 callworker terminated...\r')

                    call_positionCell = self.tableWidget_call.item(atm_index + 4, 1)
                    self.tableWidget_call.scrollToItem(call_positionCell)

                    time.sleep(1.1)

                    self.t8416_putworker.start()
                    self.t8416_putworker.daemon = True
                else:
                    pass

                nm_actval_increased = True

                print('t8416 Call 데이타수신 완료 !!!')
                print('\r')
                str = '[{0:02d}:{1:02d}:{2:02d}] t8416 TR Call 데이타수신 완료 !!!\r'.format(dt.hour, dt.minute, dt.second)
                self.textBrowser.append(str)

            else:
                pass

            if block['단축코드'][0:3] == '101':

                item = QTableWidgetItem("{0:0.2f}".format(block['전일저가']))
                item.setTextAlignment(Qt.AlignCenter)
                self.tableWidget_fut.setItem(1, Futures_column.전저.value, item)

                item = QTableWidgetItem("{0:0.2f}".format(block['전일고가']))
                item.setTextAlignment(Qt.AlignCenter)
                self.tableWidget_fut.setItem(1, Futures_column.전고.value, item)

                df_plotdata_fut.iloc[0][0] = block['전일종가']

                item = QTableWidgetItem("{0:0.2f}".format(block['전일종가']))
                item.setTextAlignment(Qt.AlignCenter)
                self.tableWidget_fut.setItem(1, Futures_column.종가.value, item)

                self.tableWidget_fut.resizeColumnsToContents()

            elif block['단축코드'][0:3] == '201':

                df_nm_call.loc[nm_call_t8416_count, '기준가'] = df['저가'][0]
                item = QTableWidgetItem("{0:0.2f}".format(df['저가'][0]))
                item.setTextAlignment(Qt.AlignCenter)
                self.tableWidget_call.setItem(nm_call_t8416_count, Option_column.기준가.value, item)

                df_nm_call.loc[nm_call_t8416_count, '월저'] = min(df['저가'])
                item = QTableWidgetItem("{0:0.2f}".format(min(df['저가'])))
                item.setTextAlignment(Qt.AlignCenter)
                self.tableWidget_call.setItem(nm_call_t8416_count, Option_column.월저.value, item)

                df_nm_call.loc[nm_call_t8416_count, '월고'] = max(df['고가'])
                item = QTableWidgetItem("{0:0.2f}".format(max(df['고가'])))
                item.setTextAlignment(Qt.AlignCenter)
                self.tableWidget_call.setItem(nm_call_t8416_count, Option_column.월고.value, item)

                df_nm_call.loc[nm_call_t8416_count, '전저'] = block['전일저가']
                item = QTableWidgetItem("{0:0.2f}".format(block['전일저가']))
                item.setTextAlignment(Qt.AlignCenter)
                self.tableWidget_call.setItem(nm_call_t8416_count, Option_column.전저.value, item)

                df_nm_call.loc[nm_call_t8416_count, '전고'] = block['전일고가']
                item = QTableWidgetItem("{0:0.2f}".format(block['전일고가']))
                item.setTextAlignment(Qt.AlignCenter)
                self.tableWidget_call.setItem(nm_call_t8416_count, Option_column.전고.value, item)

                df_nm_call.loc[nm_call_t8416_count, '종가'] = block['전일종가']
                item = QTableWidgetItem("{0:0.2f}".format(block['전일종가']))
                item.setTextAlignment(Qt.AlignCenter)
                self.tableWidget_call.setItem(nm_call_t8416_count, Option_column.종가.value, item)

                if df_nm_call.iloc[nm_call_t8416_count]['시가'] > 0:

                    df_nm_call.loc[nm_call_t8416_count, '피봇'] = self.calc_pivot(
                        df_nm_call.iloc[nm_call_t8416_count]['전저'],
                        df_nm_call.iloc[nm_call_t8416_count]['전고'],
                        df_nm_call.iloc[nm_call_t8416_count]['종가'],
                        df_nm_call.iloc[nm_call_t8416_count]['시가'])

                    item = QTableWidgetItem("{0:0.2f}".format(df_nm_call.iloc[nm_call_t8416_count]['피봇']))
                    item.setTextAlignment(Qt.AlignCenter)
                    self.tableWidget_call.setItem(nm_call_t8416_count, Option_column.피봇.value, item)

                    temp = df_nm_call.iloc[nm_call_t8416_count]['시가'] - df_nm_call.iloc[nm_call_t8416_count]['종가']

                    if temp != 0:
                        df_nm_call.loc[nm_call_t8416_count, '시가갭'] = round(temp, 2)
                        gap_percent = int((df_nm_call.iloc[nm_call_t8416_count]['시가'] /
                                           df_nm_call.iloc[nm_call_t8416_count]['종가'] - 1) * 100)

                        if 0.3 < df_nm_call.iloc[nm_call_t8416_count]['시가'] < 10.0:
                            nm_call_gap_percent[nm_call_t8416_count] = gap_percent
                        else:
                            pass

                        item = QTableWidgetItem(
                            "{0}({1}%)".format(df_nm_call.iloc[nm_call_t8416_count]['시가갭'], gap_percent))
                        item.setTextAlignment(Qt.AlignCenter)
                        self.tableWidget_call.setItem(nm_call_t8416_count, Option_column.시가갭.value, item)

                    temp = round(
                        (df_nm_call.iloc[nm_call_t8416_count]['현재가'] - df_nm_call.iloc[nm_call_t8416_count]['시가']),
                        2) * 100

                    df_nm_call.loc[nm_call_t8416_count, '대비'] = int(temp)

                    item = QTableWidgetItem("{0}".format(df_nm_call.iloc[nm_call_t8416_count]['대비']))
                    item.setTextAlignment(Qt.AlignCenter)
                    self.tableWidget_call.setItem(nm_call_t8416_count, Option_column.대비.value, item)

                    df_nm_call.loc[nm_call_t8416_count, '진폭'] = df_nm_call.iloc[nm_call_t8416_count]['고가'] - \
                                                                df_nm_call.iloc[nm_call_t8416_count]['저가']

                    item = QTableWidgetItem("{0:0.2f}".format(df_nm_call.iloc[nm_call_t8416_count]['진폭']))
                    item.setTextAlignment(Qt.AlignCenter)
                    self.tableWidget_call.setItem(nm_call_t8416_count, Option_column.진폭.value, item)

                else:
                    pass

                str = '[{0:02d}:{1:02d}:{2:02d}] Call 과거데이타({3}/{4}) 수신중...\r'.format(dt.hour, dt.minute,
                                                                        dt.second, nm_call_t8416_count + 1,
                                                                        nCount_nm_option_pairs)
                self.textBrowser.append(str)

                nm_call_t8416_count += 1

                if nm_call_t8416_count == nCount_nm_option_pairs:

                    nm_call_기준가 = df_nm_call['기준가'].values.tolist()
                    nm_call_월저 = df_nm_call['월저'].values.tolist()
                    nm_call_월고 = df_nm_call['월고'].values.tolist()
                    nm_call_전저 = df_nm_call['전저'].values.tolist()
                    nm_call_전고 = df_nm_call['전고'].values.tolist()
                    nm_call_종가 = df_nm_call['종가'].values.tolist()
                    nm_call_피봇 = df_nm_call['피봇'].values.tolist()

                    if self.t8416_callworker.isRunning():

                        self.t8416_callworker.terminate()
                        self.textBrowser.append('t8416 callworker terminated...\r')

                        call_positionCell = self.tableWidget_call.item(atm_index + 4, 1)
                        self.tableWidget_call.scrollToItem(call_positionCell)

                        time.sleep(1.1)

                        self.t8416_putworker.start()
                        self.t8416_putworker.daemon = True
                    else:
                        pass
                else:
                    pass

            elif block['단축코드'][0:3] == '301':

                df_nm_put.loc[nm_put_t8416_count, '기준가'] = df['저가'][0]
                item = QTableWidgetItem("{0:0.2f}".format(df['저가'][0]))
                item.setTextAlignment(Qt.AlignCenter)
                self.tableWidget_put.setItem(nm_put_t8416_count, Option_column.기준가.value, item)

                df_nm_put.loc[nm_put_t8416_count, '월저'] = min(df['저가'])
                item = QTableWidgetItem("{0:0.2f}".format(min(df['저가'])))
                item.setTextAlignment(Qt.AlignCenter)
                self.tableWidget_put.setItem(nm_put_t8416_count, Option_column.월저.value, item)

                df_nm_put.loc[nm_put_t8416_count, '월고'] = max(df['고가'])
                item = QTableWidgetItem("{0:0.2f}".format(max(df['고가'])))
                item.setTextAlignment(Qt.AlignCenter)
                self.tableWidget_put.setItem(nm_put_t8416_count, Option_column.월고.value, item)

                df_nm_put.loc[nm_put_t8416_count, '전저'] = block['전일저가']
                item = QTableWidgetItem("{0:0.2f}".format(block['전일저가']))
                item.setTextAlignment(Qt.AlignCenter)
                self.tableWidget_put.setItem(nm_put_t8416_count, Option_column.전저.value, item)

                df_nm_put.loc[nm_put_t8416_count, '전고'] = block['전일고가']
                item = QTableWidgetItem("{0:0.2f}".format(block['전일고가']))
                item.setTextAlignment(Qt.AlignCenter)
                self.tableWidget_put.setItem(nm_put_t8416_count, Option_column.전고.value, item)

                df_nm_put.loc[nm_put_t8416_count, '종가'] = block['전일종가']
                item = QTableWidgetItem("{0:0.2f}".format(block['전일종가']))
                item.setTextAlignment(Qt.AlignCenter)
                self.tableWidget_put.setItem(nm_put_t8416_count, Option_column.종가.value, item)

                if df_nm_put.iloc[nm_put_t8416_count]['시가'] > 0:

                    df_nm_put.loc[nm_put_t8416_count, '피봇'] = self.calc_pivot(df_nm_put.iloc[nm_put_t8416_count]['전저'],
                                                                              df_nm_put.iloc[nm_put_t8416_count]['전고'],
                                                                              df_nm_put.iloc[nm_put_t8416_count]['종가'],
                                                                              df_nm_put.iloc[nm_put_t8416_count]['시가'])

                    item = QTableWidgetItem("{0:0.2f}".format(df_nm_put.iloc[nm_put_t8416_count]['피봇']))
                    item.setTextAlignment(Qt.AlignCenter)
                    self.tableWidget_put.setItem(nm_put_t8416_count, Option_column.피봇.value, item)

                    temp = df_nm_put.iloc[nm_put_t8416_count]['시가'] - df_nm_put.iloc[nm_put_t8416_count]['종가']

                    if temp != 0:
                        df_nm_put.loc[nm_put_t8416_count, '시가갭'] = round(temp, 2)
                        gap_percent = int((df_nm_put.iloc[nm_put_t8416_count]['시가'] /
                                           df_nm_put.iloc[nm_put_t8416_count]['종가'] - 1) * 100)

                        if 0.3 < df_nm_put.iloc[nm_put_t8416_count]['시가'] < 10.0:
                            nm_put_gap_percent[nm_put_t8416_count] = gap_percent
                        else:
                            pass

                        item = QTableWidgetItem(
                            "{0}({1}%)".format(df_nm_put.iloc[nm_put_t8416_count]['시가갭'], gap_percent))
                        item.setTextAlignment(Qt.AlignCenter)
                        self.tableWidget_put.setItem(nm_put_t8416_count, Option_column.시가갭.value, item)

                    temp = round((df_nm_put.iloc[nm_put_t8416_count]['현재가'] - df_nm_put.iloc[nm_put_t8416_count]['시가']),
                                 2) * 100

                    df_nm_put.loc[nm_put_t8416_count, '대비'] = int(temp)

                    item = QTableWidgetItem("{0}".format(df_nm_put.iloc[nm_put_t8416_count]['대비']))
                    item.setTextAlignment(Qt.AlignCenter)
                    self.tableWidget_put.setItem(nm_put_t8416_count, Option_column.대비.value, item)

                    df_nm_put.loc[nm_put_t8416_count, '진폭'] = df_nm_put.iloc[nm_put_t8416_count]['고가'] - \
                                                              df_nm_put.iloc[nm_put_t8416_count]['저가']

                    item = QTableWidgetItem("{0:0.2f}".format(df_nm_put.iloc[nm_put_t8416_count]['진폭']))
                    item.setTextAlignment(Qt.AlignCenter)
                    self.tableWidget_put.setItem(nm_put_t8416_count, Option_column.진폭.value, item)

                else:
                    pass

                str = '[{0:02d}:{1:02d}:{2:02d}] Put 과거데이타({3}/{4}) 수신중...\r'.format(dt.hour, dt.minute,
                                                                       dt.second, nm_put_t8416_count + 1,
                                                                       nCount_nm_option_pairs)
                self.textBrowser.append(str)

                nm_put_t8416_count += 1
            else:
                pass

            if nm_actval_increased:
                new_count = nCount_nm_option_pairs - 1
            else:
                new_count = nCount_nm_option_pairs

            if nm_put_t8416_count == new_count:

                nm_put_기준가 = df_nm_put['기준가'].values.tolist()
                nm_put_월저 = df_nm_put['월저'].values.tolist()
                nm_put_월고 = df_nm_put['월고'].values.tolist()
                nm_put_전저 = df_nm_put['전저'].values.tolist()
                nm_put_전고 = df_nm_put['전고'].values.tolist()
                nm_put_종가 = df_nm_put['종가'].values.tolist()
                nm_put_피봇 = df_nm_put['피봇'].values.tolist()

                print('\r')
                print('Call 전광판\r')
                print(df_nm_call)
                print('\r')
                print('Put 전광판\r')
                print(df_nm_put)
                print('\r')

                put_positionCell = self.tableWidget_put.item(atm_index + 3, 1)
                self.tableWidget_put.scrollToItem(put_positionCell)

                if self.t8416_putworker.isRunning():

                    self.t8416_putworker.terminate()
                    self.textBrowser.append('t8416 putworker terminated...\r')
                else:
                    pass

                print('t8416 Put 데이타수신 완료 !!!')
                print('\r')
                str = '[{0:02d}:{1:02d}:{2:02d}] t8416 TR Put 데이타수신 완료 !!!\r'.format(dt.hour, dt.minute,
                                                                  dt.second)
                self.textBrowser.append(str)

        elif szTrCode == 't2101':
            pass
        elif szTrCode == 't2801':
            pass
        elif szTrCode == 't8432':
            pass
        else:
            pass

    def OnReceiveRealData(self, szTrCode, result):
        try:

            global x_idx

            if szTrCode == 'JIF':
                pass

            elif szTrCode == 'YOC':
                pass

            elif szTrCode == 'FC0' or szTrCode == 'NC0':

                pass
            elif szTrCode == 'FH0' or szTrCode == 'NH0':

                pass
            elif szTrCode == 'OC0' or szTrCode == 'EC0':

                print('NM Data', szTrCode)
            elif szTrCode == 'OH0' or szTrCode == 'EH0':

                pass
            else:
                pass

        except Exception as e:
            pass

    def AddCode(self):

        global overnight, start_hour
        global df_plotdata_nm_call, df_plotdata_nm_put
        global pre_start

        current = datetime.datetime.now()
        current_str = current.strftime('%H:%M:%S')

        print('시작시간 :', current_str)

        # 주야간 선물/옵션요청 선택(주간=FC0/OC0, 야간=NC0/EC0)
        if 4 < int(current_str[0:2]) < 16:

            if int(current_str[0:2]) == 8 and int(current_str[3:5]) < 50:

                pre_start = True
            else:
                pass

            self.nm_opt_real = OC0(parent=self)
            start_hour = 9

            print('주간 선물/옵션 실시간요청...')

        else:

            self.nm_opt_real = EC0(parent=self)
            start_hour = 18

            overnight = True
            print('야간 선물/옵션 실시간요청...')

        # 실시간테이타 요청
        for i in range(nCount_nm_option_pairs):
            self.nm_opt_real.AdviseRealData(nm_call_code[i])
            self.nm_opt_real.AdviseRealData(nm_put_code[i])
            print('nm_call_code, nm_put_code', nm_call_code[i], nm_put_code[i])

        self.data_display_worker.start()
        self.data_display_worker.daemon = True
        print('Data Display 쓰레드가 시작됩니다...')

    def RemoveCode(self):

        if self.data_display_worker.isRunning():
            self.data_display_worker.terminate()

        print('Terminate All Thread !!!')

        # 실시간테이타 요청취소
        for i in range(nCount_nm_option_pairs):
            self.nm_opt_real.UnadviseRealDataWithKey(nm_call_code[i])
            self.nm_opt_real.UnadviseRealDataWithKey(nm_put_code[i])

        print('실시간테이타 요청취소 !!!')

########################################################################################################################

########################################################################################################################
# 메인
########################################################################################################################

Ui_MainWindow, QtBaseClass_MainWindow = uic.loadUiType(UI_DIR+"mymoneybot.ui")

class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        QMainWindow.__init__(self)
        Ui_MainWindow.__init__(self)
        self.setupUi(self)
        self.setWindowTitle("SkyBot")

        self.plugins = CPluginManager.plugin_loader()
        menuitems = self.plugins.keys()
        menu = self.menubar.addMenu('&플러그인로봇')
        for item in menuitems:
            icon = QIcon()
            icon.addPixmap(QtGui.QPixmap("PNG/approval.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
            entry = menu.addAction(icon, item)
            entry.setObjectName(item)

        self.시작시각 = datetime.datetime.now()

        self.robots = []

        self.dialog = dict()

        self.portfolio_columns = ['종목코드', '종목명', 'TAG', '매수가', '수량', '매수일']
        self.robot_columns = ['Robot타입', 'Robot명', 'RobotID', '실행상태', '포트수', '포트폴리오']

        self.model = PandasModel()
        self.tableView_robot.setModel(self.model)
        self.tableView_robot.setSelectionBehavior(QTableView.SelectRows)
        self.tableView_robot.setSelectionMode(QTableView.SingleSelection)

        self.tableView_robot.pressed.connect(self.RobotCurrentIndex)
        self.tableView_robot_current_index = None

        self.portfolio_model = PandasModel()
        self.tableView_portfolio.setModel(self.portfolio_model)
        self.tableView_portfolio.setSelectionBehavior(QTableView.SelectRows)
        self.tableView_portfolio.setSelectionMode(QTableView.SingleSelection)
        self.tableView_portfolio.pressed.connect(self.PortfolioCurrentIndex)
        self.tableView_portfolio_current_index = None

        self.portfolio_model.update((DataFrame(columns=self.portfolio_columns)))

        self.주문제한 = 0
        self.조회제한 = 0
        self.금일백업작업중 = False
        self.종목선정작업중 = False

        self.계좌번호 = None
        self.거래비밀번호 = None

        # AxtiveX 설정
        # self.connection = XASession(parent=self)
        self.connection = None
        self.XQ_t0167 = t0167(parent=self)

    def OnQApplicationStarted(self):
        self.clock = QtCore.QTimer()
        self.clock.timeout.connect(self.OnClockTick)
        self.clock.start(1000)

        try:
            with open('mymoneybot.robot', 'rb') as handle:
                self.robots = pickle.load(handle)
        except Exception as e:
            pass

        self.RobotView()


        #TODO:자동로그인
        self.MyLogin()

    def OnClockTick(self):
        current = datetime.datetime.now()
        current_str = current.strftime('%H:%M:%S')

        if current.second == 0: # 매 0초
            try:
                if self.connection is not None:
                    msg = '오프라인'
                    if self.connection.IsConnected():
                        msg = "온라인"

                        # 현재시간 조회
                        self.XQ_t0167.Query()
                    else:
                        msg = "오프라인"
                    self.statusbar.showMessage(msg)
            except Exception as e:
                pass

            _temp = []
            for r in self.robots:
                if r.running == True:
                    _temp.append(r.Name)

            if current_str in ['09:01:00']:
                self.RobotRun()
                self.RobotView()

            if current_str in ['15:31:00']:
                self.SaveRobots()
                self.RobotView()

            if current_str[3:] in ['00:00', '30:00']:
                ToTelegram("%s : 로봇 %s개가 실행중입니다. ([%s])" % (current_str, len(_temp), ','.join(_temp)))

            if current.minute % 10 == 0: # 매 10 분
                pass

    def closeEvent(self,event):
        result = QMessageBox.question(self,"프로그램 종료","정말 종료하시겠습니까 ?", QMessageBox.Yes| QMessageBox.No)

        if result == QMessageBox.Yes:
            event.accept()
            self.clock.stop()
            self.SaveRobots()
        else:
            event.ignore()

    def SaveRobots(self):
        for r in self.robots:
            r.Run(flag=False, parent=None)

        try:
            with open('mymoneybot.robot', 'wb') as handle:
                pickle.dump(self.robots, handle, protocol=pickle.HIGHEST_PROTOCOL)
        except Exception as e:
            print(e)
        finally:
            for r in self.robots:
                r.Run(flag=False, parent=self)

    def LoadRobots(self):
        with open('mymoneybot.robot', 'rb') as handle:
            try:
                self.robots = pickle.load(handle)
            except Exception as e:
                print(e)
            finally:
                pass

    def robot_selected(self, QModelIndex):
        Robot타입 = self.model._data[QModelIndex.row():QModelIndex.row()+1]['Robot타입'].values[0]

        uuid = self.model._data[QModelIndex.row():QModelIndex.row()+1]['RobotID'].values[0]
        portfolio = None
        for r in self.robots:
            if r.UUID == uuid:
                portfolio = r.portfolio
                model = PandasModel()
                result = []
                for p, v in portfolio.items():
                    result.append((v.종목코드, v.종목명.strip(), p, v.매수가, v.수량, v.매수일))
                self.portfolio_model.update((DataFrame(data=result, columns=['종목코드','종목명','TAG','매수가','수량','매수일'])))

                break

    def robot_double_clicked(self, QModelIndex):
        self.RobotEdit(QModelIndex)
        self.RobotView()

    def portfolio_selected(self, QModelIndex):
        pass

    def portfolio_double_clicked(self, QModelIndex):
        RobotUUID = self.model._data[self.tableView_robot_current_index.row():self.tableView_robot_current_index.row() + 1]['RobotID'].values[0]
        Portfolio라벨 = self.portfolio_model._data[self.tableView_portfolio_current_index.row():self.tableView_portfolio_current_index.row() + 1]['TAG'].values[0]

        for r in self.robots:
            if r.UUID == RobotUUID:
                portfolio_keys = list(r.portfolio.keys())
                for k in portfolio_keys:
                    if k == Portfolio라벨:
                        v = r.portfolio[k]
                        result = QMessageBox.question(self, "포트폴리오 종목 삭제", "[%s-%s] 을/를 삭제 하시겠습니까 ?" %(v.종목코드, v.종목명), QMessageBox.Yes | QMessageBox.No)
                        if result == QMessageBox.Yes:
                            r.portfolio.pop(Portfolio라벨)

                        self.PortfolioView()

    def RobotCurrentIndex(self, index):
        self.tableView_robot_current_index = index

    def RobotRun(self):
        for r in self.robots:
            r.초기조건()
            # logger.debug('%s %s %s %s' % (r.sName, r.UUID, len(r.portfolio), r.GetStatus()))
            r.Run(flag=True, parent=self)

    def RobotView(self):
        result = []
        for r in self.robots:
            result.append(r.getstatus())

        self.model.update(DataFrame(data=result, columns=self.robot_columns))

        # RobotID 숨김
        self.tableView_robot.setColumnHidden(2, True)

        for i in range(len(self.robot_columns)):
            self.tableView_robot.resizeColumnToContents(i)

    def RobotEdit(self, QModelIndex):
        Robot타입 = self.model._data[QModelIndex.row():QModelIndex.row()+1]['Robot타입'].values[0]
        RobotUUID = self.model._data[QModelIndex.row():QModelIndex.row()+1]['RobotID'].values[0]

        for r in self.robots:
            if r.UUID == RobotUUID:
                r.modal(parent=self)

    def PortfolioView(self):
        RobotUUID = self.model._data[self.tableView_robot_current_index.row():self.tableView_robot_current_index.row() + 1]['RobotID'].values[0]
        portfolio = None
        for r in self.robots:
            if r.UUID == RobotUUID:
                portfolio = r.portfolio
                # model = PandasModel()
                result = []
                for p, v in portfolio.items():
                    매수일 = "%s" % v.매수일
                    result.append((v.종목코드, v.종목명.strip(), p, v.매수가, v.수량, 매수일[:19]))

                df = DataFrame(data=result, columns=self.portfolio_columns)
                df = df.sort_values(['종목명'], ascending=True)
                self.portfolio_model.update(df)

                for i in range(len(self.portfolio_columns)):
                    self.tableView_portfolio.resizeColumnToContents(i)

    def PortfolioCurrentIndex(self, index):
        self.tableView_portfolio_current_index = index

    # ------------------------------------------------------------------------------------------------------------------
    def MyLogin(self):
        계좌정보 = pd.read_csv("secret/passwords.csv", converters={'계좌번호': str, '거래비밀번호': str})
        주식계좌정보 = 계좌정보.query("구분 == '거래'")

        if len(주식계좌정보) > 0:
            if self.connection is None:
                self.connection = XASession(parent=self)

            self.계좌번호 = 주식계좌정보['계좌번호'].values[0].strip()
            self.id = 주식계좌정보['사용자ID'].values[0].strip()
            self.pwd = 주식계좌정보['비밀번호'].values[0].strip()
            self.cert = 주식계좌정보['공인인증비밀번호'].values[0].strip()
            self.거래비밀번호 = 주식계좌정보['거래비밀번호'].values[0].strip()
            self.url = 주식계좌정보['url'].values[0].strip()
            self.connection.login(url=self.url, id=self.id, pwd=self.pwd, cert=self.cert)
        else:
            print("secret디렉토리의 passwords.csv 파일에서 거래 계좌를 지정해 주세요")

    def OnLogin(self, code, msg):
        if code == '0000':
            self.statusbar.showMessage("로그인 되었습니다.")
        else:
            self.statusbar.showMessage("%s %s" % (code, msg))

    def OnLogout(self):
        self.statusbar.showMessage("로그아웃 되었습니다.")

    def OnDisconnect(self):
        # 로봇 상태 저장
        self.SaveRobots()

        self.statusbar.showMessage("연결이 끊겼습니다.")

        self.connection.login(url='demo.ebestsec.co.kr', id=self.id, pwd=self.pwd, cert=self.cert)

    def OnReceiveMessage(self, systemError, messageCode, message):
        # 클래스이름 = self.__class__.__name__
        # 함수이름 = inspect.currentframe().f_code.co_name
        # print("%s-%s " % (클래스이름, 함수이름), systemError, messageCode, message)
        pass

    def OnReceiveData(self, szTrCode, result):
        # print(szTrCode, result)
        pass

    def OnReceiveRealData(self, szTrCode, result):
        # print(szTrCode, result)
        pass

    # ------------------------------------------------------------------------------------------------------------------
    def MENU_Action(self, qaction):
        logger.debug("Action Slot %s %s " % (qaction.objectName(), qaction.text()))
        _action = qaction.objectName()

        if _action == "actionExit":
            self.connection.disconnect()
            self.close()

        if _action == "actionLogin":
            self.MyLogin()

        if _action == "actionLogout":
            self.connection.logout()
            self.statusbar.showMessage("로그아웃 되었습니다.")

        # 일별가격정보 백업
        if _action == "actionPriceBackupDay":
            if self.dialog.get('일별가격정보백업') is not None:
                try:
                    self.dialog['일별가격정보백업'].show()
                except Exception as e:
                    self.dialog['일별가격정보백업'] = 화면_일별가격정보백업(parent=self)
                    self.dialog['일별가격정보백업'].show()
            else:
                self.dialog['일별가격정보백업'] = 화면_일별가격정보백업(parent=self)
                self.dialog['일별가격정보백업'].show()

        # 분별가격정보 백업
        if _action == "actionPriceBackupMin":
            if self.dialog.get('분별가격정보백업') is not None:
                try:
                    self.dialog['분별가격정보백업'].show()
                except Exception as e:
                    self.dialog['분별가격정보백업'] = 화면_분별가격정보백업(parent=self)
                    self.dialog['분별가격정보백업'].show()
            else:
                self.dialog['분별가격정보백업'] = 화면_분별가격정보백업(parent=self)
                self.dialog['분별가격정보백업'].show()

        # 일별업종정보 백업
        if _action == "actionSectorBackupDay":
            if self.dialog.get('일별업종정보백업') is not None:
                try:
                    self.dialog['일별업종정보백업'].show()
                except Exception as e:
                    self.dialog['일별업종정보백업'] = 화면_일별업종정보백업(parent=self)
                    self.dialog['일별업종정보백업'].show()
            else:
                self.dialog['일별업종정보백업'] = 화면_일별업종정보백업(parent=self)
                self.dialog['일별업종정보백업'].show()

        # 종목별 투자자정보 백업
        if _action == "actionInvestorBackup":
            if self.dialog.get('종목별투자자정보백업') is not None:
                try:
                    self.dialog['종목별투자자정보백업'].show()
                except Exception as e:
                    self.dialog['종목별투자자정보백업'] = 화면_종목별투자자정보백업(parent=self)
                    self.dialog['종목별투자자정보백업'].show()
            else:
                self.dialog['종목별투자자정보백업'] = 화면_종목별투자자정보백업(parent=self)
                self.dialog['종목별투자자정보백업'].show()

        # 종목코드 조회/저장
        if _action == "actionStockcode":
            if self.dialog.get('종목코드조회') is not None:
                try:
                    self.dialog['종목코드조회'].show()
                except Exception as e:
                    self.dialog['종목코드조회'] = 화면_종목코드(parent=self)
                    self.dialog['종목코드조회'].show()
            else:
                self.dialog['종목코드조회'] = 화면_종목코드(parent=self)
                self.dialog['종목코드조회'].show()

        # 거래결과
        if _action == "actionTool2ebest":
            if self.dialog.get('외부신호2eBEST') is not None:
                try:
                    self.dialog['외부신호2eBEST'].show()
                except Exception as e:
                    self.dialog['외부신호2eBEST'] = 화면_외부신호2eBEST(parent=self)
                    self.dialog['외부신호2eBEST'].show()
            else:
                self.dialog['외부신호2eBEST'] = 화면_외부신호2eBEST(parent=self)
                self.dialog['외부신호2eBEST'].show()

        if _action == "actionTradeResult":
            if self.dialog.get('거래결과') is not None:
                try:
                    self.dialog['거래결과'].show()
                except Exception as e:
                    self.dialog['거래결과'] = 화면_거래결과(parent=self)
                    self.dialog['거래결과'].show()
            else:
                self.dialog['거래결과'] = 화면_거래결과(parent=self)
                self.dialog['거래결과'].show()

        # 일자별 주가
        if _action == "actionDailyPrice":
            if self.dialog.get('일자별주가') is not None:
                try:
                    self.dialog['일자별주가'].show()
                except Exception as e:
                    self.dialog['일자별주가'] = 화면_일별주가(parent=self)
                    self.dialog['일자별주가'].show()
            else:
                self.dialog['일자별주가'] = 화면_일별주가(parent=self)
                self.dialog['일자별주가'].show()

        # 분별 주가
        if _action == "actionMinuitePrice":
            if self.dialog.get('분별주가') is not None:
                try:
                    self.dialog['분별주가'].show()
                except Exception as e:
                    self.dialog['분별주가'] = 화면_분별주가(parent=self)
                    self.dialog['분별주가'].show()
            else:
                self.dialog['분별주가'] = 화면_분별주가(parent=self)
                self.dialog['분별주가'].show()

        # 업종정보
        if _action == "actionSectorView":
            if self.dialog.get('업종정보조회') is not None:
                try:
                    self.dialog['업종정보조회'].show()
                except Exception as e:
                    self.dialog['업종정보조회'] = 화면_업종정보(parent=self)
                    self.dialog['업종정보조회'].show()
            else:
                self.dialog['업종정보조회'] = 화면_업종정보(parent=self)
                self.dialog['업종정보조회'].show()

        # 테마정보
        if _action == "actionTheme":
            if self.dialog.get('테마정보조회') is not None:
                try:
                    self.dialog['테마정보조회'].show()
                except Exception as e:
                    self.dialog['테마정보조회'] = 화면_테마정보(parent=self)
                    self.dialog['테마정보조회'].show()
            else:
                self.dialog['테마정보조회'] = 화면_테마정보(parent=self)
                self.dialog['테마정보조회'].show()

        # 종목별 투자자
        if _action == "actionInvestors":
            if self.dialog.get('종목별투자자') is not None:
                try:
                    self.dialog['종목별투자자'].show()
                except Exception as e:
                    self.dialog['종목별투자자'] = 화면_종목별투자자(parent=self)
                    self.dialog['종목별투자자'].show()
            else:
                self.dialog['종목별투자자'] = 화면_종목별투자자(parent=self)
                self.dialog['종목별투자자'].show()

        # 종목별 투자자2
        if _action == "actionInvestors2":
            if self.dialog.get('종목별투자자2') is not None:
                try:
                    self.dialog['종목별투자자2'].show()
                except Exception as e:
                    self.dialog['종목별투자자2'] = 화면_종목별투자자2(parent=self)
                    self.dialog['종목별투자자2'].show()
            else:
                self.dialog['종목별투자자2'] = 화면_종목별투자자2(parent=self)
                self.dialog['종목별투자자2'].show()

        # 호가창정보
        if _action == "actionAskBid":
            if self.dialog.get('호가창정보') is not None:
                try:
                    self.dialog['호가창정보'].show()
                except Exception as e:
                    self.dialog['호가창정보'] = 화면_호가창정보(parent=self)
                    self.dialog['호가창정보'].show()
            else:
                self.dialog['호가창정보'] = 화면_호가창정보(parent=self)
                self.dialog['호가창정보'].show()

        # 실시간정보
        if _action == "actionRealDataDialog":
            if self.dialog.get('실시간정보') is not None:
                try:
                    self.dialog['실시간정보'].show()
                except Exception as e:
                    self.dialog['실시간정보'] = 화면_실시간정보(parent=self)
                    self.dialog['실시간정보'].show()
            else:
                self.dialog['실시간정보'] = 화면_실시간정보(parent=self)
                self.dialog['실시간정보'].show()

        # 뉴스
        if _action == "actionNews":
            if self.dialog.get('뉴스') is not None:
                try:
                    self.dialog['뉴스'].show()
                except Exception as e:
                    self.dialog['뉴스'] = 화면_뉴스(parent=self)
                    self.dialog['뉴스'].show()
            else:
                self.dialog['뉴스'] = 화면_뉴스(parent=self)
                self.dialog['뉴스'].show()

        # 계좌정보 조회
        if _action == "actionAccountDialog":
            if self.dialog.get('계좌정보조회') is not None:
                try:
                    self.dialog['계좌정보조회'].show()
                except Exception as e:
                    self.dialog['계좌정보조회'] = 화면_계좌정보(parent=self)
                    self.dialog['계좌정보조회'].show()
            else:
                self.dialog['계좌정보조회'] = 화면_계좌정보(parent=self)
                self.dialog['계좌정보조회'].show()

        # 차트인덱스
        if _action == "actionChartIndex":
            if self.dialog.get('차트인덱스') is not None:
                try:
                    self.dialog['차트인덱스'].show()
                except Exception as e:
                    self.dialog['차트인덱스'] = 화면_차트인덱스(parent=self)
                    self.dialog['차트인덱스'].show()
            else:
                self.dialog['차트인덱스'] = 화면_차트인덱스(parent=self)
                self.dialog['차트인덱스'].show()

        # 종목검색
        if _action == "actionSearchItems":
            if self.dialog.get('종목검색') is not None:
                try:
                    self.dialog['종목검색'].show()
                except Exception as e:
                    self.dialog['종목검색'] = 화면_종목검색(parent=self)
                    self.dialog['종목검색'].show()
            else:
                self.dialog['종목검색'] = 화면_종목검색(parent=self)
                self.dialog['종목검색'].show()

        # e종목검색
        if _action == "actionESearchItems":
            if self.dialog.get('e종목검색') is not None:
                try:
                    self.dialog['e종목검색'].show()
                except Exception as e:
                    self.dialog['e종목검색'] = 화면_e종목검색(parent=self)
                    self.dialog['e종목검색'].show()
            else:
                self.dialog['e종목검색'] = 화면_e종목검색(parent=self)
                self.dialog['e종목검색'].show()

        if _action == "actionOpenScreen":
            XQ = t8430(parent=self)
            XQ.Query(구분='0')

            res = XQ.RequestLinkToHTS("&STOCK_CODE", "069500", "")

        # 주문테스트
        if _action == "actionOrder":
            if self.dialog.get('주문테스트') is not None:
                try:
                    self.dialog['주문테스트'].show()
                except Exception as e:
                    self.dialog['주문테스트'] = 화면_주문테스트(parent=self)
                    self.dialog['주문테스트'].show()
            else:
                self.dialog['주문테스트'] = 화면_주문테스트(parent=self)
                self.dialog['주문테스트'].show()

        # 사용법
        if _action == "actionMustRead":
            webbrowser.open('https://thinkpoolost.wixsite.com/moneybot')

        if _action == "actionUsage":
            webbrowser.open('https://docs.google.com/document/d/1BGENxWqJyZdihQFuWcmTNy3_4J0kHolCc-qcW3RULzs/edit')

        if _action == "actionVersion":
            if self.dialog.get('Version') is not None:
                try:
                    self.dialog['Version'].show()
                except Exception as e:
                    self.dialog['Version'] = 화면_버전(parent=self)
                    self.dialog['Version'].show()
            else:
                self.dialog['Version'] = 화면_버전(parent=self)
                self.dialog['Version'].show()

        if _action == "actionRobotLoad":
            reply = QMessageBox.question(self, "로봇 탑제", "저장된 로봇을 읽어올까요?", QMessageBox.Yes | QMessageBox.Cancel)
            if reply == QMessageBox.Cancel:
                pass
            elif reply == QMessageBox.Yes:
                self.LoadRobots()

            self.RobotView()

        elif _action == "actionRobotSave":
            reply = QMessageBox.question(self, "로봇 저장", "현재 로봇을 저장할까요?",
                                         QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel)
            if reply == QMessageBox.Cancel:
                pass
            elif reply == QMessageBox.No:
                pass
            elif reply == QMessageBox.Yes:
                self.SaveRobots()

            self.RobotView()

        elif _action == "actionRobotOneRun":
            try:
                RobotUUID = self.model._data[self.tableView_robot_current_index.row():self.tableView_robot_current_index.row() + 1]['RobotID'].values[0]
            except Exception as e:
                RobotUUID = ''

            robot_found = None
            for r in self.robots:
                if r.UUID == RobotUUID:
                    robot_found = r
                    break

            if robot_found == None:
                return

            robot_found.Run(flag=True, parent=self)

            self.RobotView()

        elif _action == "actionRobotOneStop":
            try:
                RobotUUID = self.model._data[self.tableView_robot_current_index.row():self.tableView_robot_current_index.row() + 1]['RobotID'].values[0]
            except Exception as e:
                RobotUUID = ''

            robot_found = None
            for r in self.robots:
                if r.UUID == RobotUUID:
                    robot_found = r
                    break

            if robot_found == None:
                return

            reply = QMessageBox.question(self,"로봇 실행 중지", "로봇 실행을 중지할까요?\n%s" % robot_found.getstatus(),QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel)
            if reply == QMessageBox.Cancel:
                pass
            elif reply == QMessageBox.No:
                pass
            elif reply == QMessageBox.Yes:
                robot_found.Run(flag=False, parent=None)

            self.RobotView()

        elif _action == "actionRobotRun":
            self.RobotRun()
            self.RobotView()

        elif _action == "actionRobotStop":
            reply = QMessageBox.question(self,"전체 로봇 실행 중지", "전체 로봇 실행을 중지할까요?",QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel)
            if reply == QMessageBox.Cancel:
                pass
            elif reply == QMessageBox.No:
                pass
            elif reply == QMessageBox.Yes:
                for r in self.robots:
                    r.Run(flag=False, parent=None)

            self.RobotView()

        elif _action == "actionRobotRemove":
            try:
                RobotUUID = self.model._data[self.tableView_robot_current_index.row():self.tableView_robot_current_index.row() + 1]['RobotID'].values[0]

                robot_found = None
                for r in self.robots:
                    if r.UUID == RobotUUID:
                        robot_found = r
                        break

                if robot_found == None:
                    return

                reply = QMessageBox.question(self, "로봇 삭제", "로봇을 삭제할까요?\n%s" % robot_found.getstatus()[0:4], QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel)
                if reply == QMessageBox.Cancel:
                    pass
                elif reply == QMessageBox.No:
                    pass
                elif reply == QMessageBox.Yes:
                    self.robots.remove(robot_found)

                self.RobotView()
            except Exception as e:
                pass

        elif _action == "actionRobotClear":
            reply = QMessageBox.question(self, "로봇 전체 삭제", "로봇 전체를 삭제할까요?",
                                         QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel)
            if reply == QMessageBox.Cancel:
                pass
            elif reply == QMessageBox.No:
                pass
            elif reply == QMessageBox.Yes:
                self.robots = []

            self.RobotView()

        elif _action == "actionRobotView":
            self.RobotView()
            for r in self.robots:
                logger.debug('%s %s %s %s' % (r.Name, r.UUID, len(r.portfolio), r.getstatus()))

        if _action in self.plugins.keys():
            robot = self.plugins[_action].instance()
            robot.set_database(database=DATABASE)
            robot.set_secret(계좌번호=self.계좌번호, 비밀번호=self.거래비밀번호)
            ret = robot.modal(parent=self)
            if ret == 1:
                self.robots.append(robot)
            self.RobotView()

        # 당월물 옵션전광판
        if _action == "actionCMOptionPrice":
            if self.dialog.get('당월물옵션전광판') is not None:
                try:
                    self.dialog['당월물옵션전광판'].show()
                except Exception as e:
                    self.dialog['당월물옵션전광판'] = 화면_당월물옵션전광판(parent=self)
                    self.dialog['당월물옵션전광판'].show()
            else:
                self.dialog['당월물옵션전광판'] = 화면_당월물옵션전광판(parent=self)
                self.dialog['당월물옵션전광판'].show()

        # 차월물 옵션전광판
        if _action == "actionNMOptionPrice":
            if self.dialog.get('차월물옵션전광판') is not None:
                try:
                    self.dialog['차월물옵션전광판'].show()
                except Exception as e:
                    self.dialog['차월물옵션전광판'] = 화면_차월물옵션전광판(parent=self)
                    self.dialog['차월물옵션전광판'].show()
            else:
                self.dialog['차월물옵션전광판'] = 화면_차월물옵션전광판(parent=self)
                self.dialog['차월물옵션전광판'].show()


    # ------------------------------------------------------------

if __name__ == "__main__":
    # Window 8, 10
    # Window 7은 한글을 못읽음
    # Speak("스카이봇이 시작됩니다.")

    XingAdminCheck()

    ToTelegram("SkyBot이 실행되었습니다.")

    # 1.로그 인스턴스를 만든다.
    logger = logging.getLogger('mymoneybot')
    # 2.formatter를 만든다.
    formatter = logging.Formatter('[%(levelname)s|%(filename)s:%(lineno)s]%(asctime)s>%(message)s')

    loggerLevel = logging.DEBUG
    filename = "LOG/mymoneybot.log"

    # 스트림과 파일로 로그를 출력하는 핸들러를 각각 만든다.
    filehandler = logging.FileHandler(filename)
    streamhandler = logging.StreamHandler()

    # 각 핸들러에 formatter를 지정한다.
    filehandler.setFormatter(formatter)
    streamhandler.setFormatter(formatter)

    # 로그 인스턴스에 스트림 핸들러와 파일 핸들러를 붙인다.
    logger.addHandler(filehandler)
    logger.addHandler(streamhandler)
    logger.setLevel(loggerLevel)
    logger.debug("=============================================================================")
    logger.info("LOG START")

    app = QApplication(sys.argv)
    #app.setStyle(QStyleFactory.create('Fusion'))
    app.setQuitOnLastWindowClosed(True)

    window = MainWindow()
    window.show()

    QTimer().singleShot(1, window.OnQApplicationStarted)

    sys.exit(app.exec_())

