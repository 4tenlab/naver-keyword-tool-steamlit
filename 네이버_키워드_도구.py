from PySide6.QtWidgets import (QApplication, QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem, QMessageBox, QFileDialog, QHeaderView, QAbstractItemView, QSplitter)
from PySide6.QtCore import Qt, QTimer
import json
import requests
import hmac, hashlib, base64, time
import os
import datetime
import traceback

try:
    from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
    import matplotlib.pyplot as plt
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False

CONFIG_FILE = 'naver_keyword_config.json'

def save_config(config):
    with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
        json.dump(config, f, ensure_ascii=False, indent=2)

def load_config():
    try:
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return {}

def generate_signature(timestamp, method, uri, secret_key):
    msg = f"{timestamp}.{method}.{uri}"
    hash = hmac.new(secret_key.encode(), msg.encode(), hashlib.sha256)
    return base64.b64encode(hash.digest()).decode()

def search_keywords(keyword, customer_id, api_key, secret_key):
    BASE_URL = 'https://api.searchad.naver.com'
    uri = '/keywordstool'
    url = BASE_URL + uri
    method = 'GET'
    keyword_param = keyword.replace(' ', '')
    params = {'hintKeywords': keyword_param, 'showDetail': 1}
    timestamp = str(round(time.time() * 1000))
    signature = generate_signature(timestamp, method, uri, secret_key)
    headers = {
        'Content-Type': 'application/json; charset=UTF-8',
        'X-Timestamp': timestamp,
        'X-API-KEY': api_key,
        'X-Customer': str(customer_id),
        'X-Signature': signature
    }
    r = requests.get(url, params=params, headers=headers)
    r.raise_for_status()
    return r.json().get('keywordList', [])

class NaverKeywordApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("네이버 키워드 도구 v0.0.4")
        self.config_path = None
        self.selected_col = None
        self.sort_reverse = False
        self.current_search_keyword = ""  # 검색한 키워드 저장 변수 추가
        self.columns = ['키워드', '총 검색량', 'PC', 'MOBILE', '경쟁정도', '월평균 노출 광고수']
        self.init_ui()
        self.setStyleSheet("background-color: white;")

    def init_ui(self):
        splitter = QSplitter()
        splitter.setOrientation(Qt.Horizontal)
        splitter.setStyleSheet('''
            QSplitter::handle {
                background: #d1d1d6;
                width: 1px;
                min-width: 1px;
                margin: 0px;
            }
            QSplitter::handle:hover {
                background: #a0a0a0;
            }
        ''')

        # Apple 스타일 좌측 입력 영역
        left_widget = QWidget()
        left_layout = QVBoxLayout()
        left_layout.setContentsMargins(32, 32, 32, 32)
        left_layout.setSpacing(18)
        left_widget.setLayout(left_layout)
        left_widget.setStyleSheet("background-color: white;")
        
        # 상단에 설명 텍스트 추가
        desc_label = QLabel("네이버 키워드 도구를 사용하여 입력한 키워드와 관련된 모든 연관키워드의 검색량과 경쟁정도를 분석할 수 있습니다.")
        desc_label.setWordWrap(True)
        desc_label.setStyleSheet("color: #555; font-size: 13px; margin-bottom: 15px; line-height: 1.4;")
        left_layout.addWidget(desc_label)
        
        self.entries = {}
        default_values = {
            "customer_id": "1606492",
            "api_key": "0100000000dc897c13f61383de5adb2ed865838918b6260db6710f1949dc74795da1b2e53e",
            "secret_key": "AQAAAADciXwT9hOD3lrbLthlg4kYTPfLKERBgDLqGB3VN4N08g=="
        }
        # 스타일시트 정의 - 포커스 색상을 파스텔톤 하늘색으로 변경
        lineedit_style = """
            QLineEdit {
                background: #fff;
                color: #222;
                border: 1.5px solid #d1d1d6;
                border-radius: 8px;
                padding: 8px 12px;
                font-size: 15px;
                font-family: 'SF Pro', '맑은 고딕', Arial, sans-serif;
                box-shadow: 0 1px 4px rgba(0,0,0,0.03);
            }
            QLineEdit:focus {
                border: 1.5px solid #a6dcef;
                background: #f8faff;
            }
        """
        label_style = "color: #222; font-size: 14px; font-family: 'SF Pro', '맑은 고딕', Arial, sans-serif; margin-bottom: 2px;"
        # 첫 줄: Keyword [ 키워드 검색 예) 비타민, 뇌과학, 러닝화 ]
        keyword_row = QHBoxLayout()
        keyword_row.setSpacing(10)
        lbl = QLabel("검색 키워드")  # 레이블 텍스트 변경
        lbl.setStyleSheet(label_style)
        ent = QLineEdit()
        ent.setStyleSheet(lineedit_style)
        ent.setPlaceholderText("분석하려는 메인 키워드를 입력하세요 (예: 비타민, 뇌과학, 러닝화)")  # 플레이스홀더 텍스트 수정
        self.entries["keyword"] = ent
        ent.returnPressed.connect(self.on_search)
        keyword_row.addWidget(lbl)
        keyword_row.addWidget(ent, 10)
        left_layout.addLayout(keyword_row)

        # 나머지 입력란
        for label, key in [
            ("CUSTOMER_ID", "customer_id"),
            ("API_KEY", "api_key"),
            ("SECRET_KEY", "secret_key")
        ]:
            row = QHBoxLayout()
            row.setSpacing(8)
            lbl = QLabel(label)
            lbl.setStyleSheet(label_style)
            ent = QLineEdit()
            ent.setStyleSheet(lineedit_style)
            ent.setEchoMode(QLineEdit.Password)
            if key in default_values:
                ent.setText(default_values[key])
            self.entries[key] = ent
            row.addWidget(lbl)
            row.addWidget(ent, 10)
            left_layout.addLayout(row)
            
        # 하단 버튼: 설정 저장, 설정 불러오기, 실행(오른쪽 끝)
        left_layout.addSpacing(10)
        btn_save = QPushButton("설정 저장")
        btn_load = QPushButton("설정 불러오기")
        btn_search = QPushButton("분석 실행")  # 버튼 텍스트 변경
        btn_excel = QPushButton("엑셀 다운로드")
        
        # 버튼 스타일 정의
        btn_common_style = """
            QPushButton {
                color: white;
                border: none;
                border-radius: 8px;
                padding: 8px 20px;
                font-size: 15px;
                font-family: 'SF Pro', '맑은 고딕', Arial, sans-serif;
                font-weight: 600;
                min-width: 120px;
            }
        """
        
        # 파란색 버튼을 파스텔톤 하늘색으로 변경 (설정 저장, 설정 불러오기)
        btn_blue_style = btn_common_style + """
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #a6dcef, stop:1 #7fbfe0);
            }
            QPushButton:hover {
                background: #7fbfe0;
            }
            QPushButton:pressed {
                background: #5aafdb;
            }
        """
        
        # 엑셀 녹색 버튼 (엑셀 다운로드) - 파스텔톤 초록색
        btn_excel_style = btn_common_style + """
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #a8e6cf, stop:1 #88d8b0);
            }
            QPushButton:hover {
                background: #88d8b0;
            }
            QPushButton:pressed {
                background: #6dc9a0;
            }
        """
        
        # 실행 버튼 - 파스텔톤 하늘색
        btn_search_style = btn_common_style + """
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #a6dcef, stop:1 #7fbfe0);
            }
            QPushButton:hover {
                background: #7fbfe0;
            }
            QPushButton:pressed {
                background: #5aafdb;
            }
        """
        
        btn_save.setStyleSheet(btn_blue_style)
        btn_load.setStyleSheet(btn_blue_style)
        btn_excel.setStyleSheet(btn_excel_style)
        btn_search.setStyleSheet(btn_search_style)
        
        btn_save.clicked.connect(self.save_settings)
        btn_load.clicked.connect(self.load_settings)
        btn_search.clicked.connect(self.on_search)
        btn_excel.clicked.connect(self.export_to_excel)
        
        btns = QHBoxLayout()
        btns.setSpacing(10)
        btns.addWidget(btn_save, 2)
        btns.addWidget(btn_load, 2)
        btns.addStretch(6)
        btns.addWidget(btn_excel, 2)  # 위치 변경: 엑셀 다운로드 버튼을 먼저 배치
        btns.addWidget(btn_search, 2)  # 위치 변경: 실행 버튼을 마지막에 배치
        left_layout.addLayout(btns)
        
        # 흰 공간 제거 - 여기서 addStretch 제거하고 간격만 추가
        left_layout.addSpacing(10)

        # 좌측 하단 그래프 영역 - 테두리 색상 회색으로 변경
        self.graph_widget = QWidget()
        self.graph_layout = QVBoxLayout()
        self.graph_widget.setLayout(self.graph_layout)
        self.graph_widget.setStyleSheet("border: 2px solid #d1d1d6; border-radius: 6px; background: white;")
        self.graph_widget.setMinimumHeight(300)  # 그래프 최소 높이 설정
        self.graph_canvas = None
        left_layout.addWidget(self.graph_widget, 1)  # 그래프에 stretch factor 1 추가하여 남은 공간 모두 사용

        # 우측 결과 테이블 영역 (Apple 스타일)
        right_widget = QWidget()
        right_layout = QVBoxLayout()
        right_layout.setContentsMargins(24, 32, 24, 32)
        right_widget.setLayout(right_layout)
        right_widget.setStyleSheet("background-color: white;")
        
        # 연관 키워드 안내 라벨 추가
        related_label = QLabel("연관 키워드 분석 결과")
        related_label.setStyleSheet("color: #333; font-size: 16px; font-weight: bold; margin-bottom: 5px;")
        right_layout.addWidget(related_label)
        
        # 조회 기준 기간 라벨
        info_layout = QHBoxLayout()
        self.period_label = QLabel()
        self.period_label.setStyleSheet("color: #666; font-size: 13px;")
        info_layout.addWidget(self.period_label)
        
        # 우측 정렬된 도움말 라벨 추가
        help_label = QLabel("컬럼 헤더를 클릭하여 정렬할 수 있습니다")
        help_label.setStyleSheet("color: #666; font-size: 13px; font-style: italic;")
        help_label.setAlignment(Qt.AlignRight)
        info_layout.addWidget(help_label)
        
        right_layout.addLayout(info_layout)
        right_layout.addSpacing(5)
        
        self.table = QTableWidget(0, len(self.columns))
        self.table.setHorizontalHeaderLabels(self.columns)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        
        # 헤더 클릭 이벤트를 더 명확하게 연결
        self.table.horizontalHeader().sectionClicked.disconnect() if self.table.horizontalHeader().signalsBlocked() == False else None
        self.table.horizontalHeader().sectionClicked.connect(self.on_header_click)
        
        table_style = """
            QTableWidget {
                background: #fff;
                color: #222;
                border: 1.5px solid #e5e5ea;
                border-radius: 10px;
                font-size: 15px;
                font-family: 'SF Pro', '맑은 고딕', Arial, sans-serif;
                gridline-color: #e5e5ea;
            }
            QHeaderView::section {
                background: #f5f5f7;
                color: #222;
                border: 1px solid #e5e5ea;
                font-weight: 600;
                font-size: 15px;
                padding: 6px 0;
            }
            QHeaderView::section:hover {
                background: #e8e8ed;
            }
            QTableWidget::item:selected {
                background: #eaf1fb;
                color: #222;
            }
            QTableWidget::item:hover {
                background: #f0f4fa;
            }
        """
        self.table.setStyleSheet(table_style)
        right_layout.addWidget(self.table)

        splitter.addWidget(left_widget)
        splitter.addWidget(right_widget)
        QTimer.singleShot(0, lambda: splitter.setSizes([360, 840]))

        main_layout = QHBoxLayout()
        main_layout.addWidget(splitter)
        self.setLayout(main_layout)

    def on_search(self):
        kw = self.entries['keyword'].text().strip()
        cid = self.entries['customer_id'].text().strip()
        api = self.entries['api_key'].text().strip()
        sec = self.entries['secret_key'].text().strip()
        if not all([kw, cid, api, sec]):
            QMessageBox.critical(self, "입력 오류", "모든 값을 입력하세요.")
            return
        # 조회 기준 기간 계산 (최근 30일)
        end_date = datetime.date.today()
        start_date = end_date - datetime.timedelta(days=29)
        self.period_label.setText(f"조회 기준: {start_date.strftime('%Y-%m-%d')} ~ {end_date.strftime('%Y-%m-%d')}")
        
        # 검색 키워드 저장 (클래스 변수)
        self.current_search_keyword = kw.lower()
        
        try:
            data = search_keywords(kw, cid, api, sec)
            self.table.setRowCount(0)
            keyword_graph_data = []
            
            for k in data:
                pc = int(k['monthlyPcQcCnt']) if k['monthlyPcQcCnt'] != '< 10' else 0
                mo = int(k['monthlyMobileQcCnt']) if k['monthlyMobileQcCnt'] != '< 10' else 0
                total = pc + mo
                comp = k.get('compIdx', '-')
                ad_cnt = k.get('monthlyAvePcCtr', '-')
                row = [k['relKeyword'], total, pc, mo, comp, ad_cnt]
                row_idx = self.table.rowCount()
                self.table.insertRow(row_idx)
                
                # 현재 키워드가 검색한 키워드와 일치하는지 확인
                is_searched_keyword = k['relKeyword'].lower() == self.current_search_keyword
                
                for col_idx, val in enumerate(row):
                    item = QTableWidgetItem(str(val))
                    
                    # 검색한 키워드와 일치하면 텍스트 색상을 붉은색으로 변경
                    if is_searched_keyword:
                        from PySide6.QtGui import QColor, QBrush
                        item.setForeground(QBrush(QColor('#FF5555')))  # 붉은색으로 설정
                        # 첫 번째 열(키워드)만 굵게 표시
                        if col_idx == 0:
                            font = item.font()
                            font.setBold(True)
                            item.setFont(font)
                    
                    self.table.setItem(row_idx, col_idx, item)
                
                keyword_graph_data.append((k['relKeyword'], total))
            
            self.draw_keyword_graph(keyword_graph_data)
        except Exception as e:
            QMessageBox.critical(self, "API 오류", str(e))

    def save_settings(self):
        config = {k: v.text() for k, v in self.entries.items()}
        file_path, _ = QFileDialog.getSaveFileName(self, "설정 저장", "naver_keyword_config.json", "JSON files (*.json)")
        if file_path:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=2)
            self.config_path = file_path
            
            # 메시지 박스 개선
            msg_box = QMessageBox(self)
            msg_box.setWindowTitle("설정 저장 완료")
            msg_box.setIcon(QMessageBox.Information)
            
            # 메인 메시지와 상세 설명을 함께 표시
            main_text = "API 설정이 성공적으로 저장되었습니다."
            info_text = f"저장 위치: {file_path}"
            detail_text = "저장된 설정 파일은 다음에 프로그램을 실행할 때 불러와서 API 정보를 다시 입력하지 않아도 됩니다."
            
            # 모든 정보를 한 번에 표시
            msg_box.setText(f"{main_text}\n\n{info_text}\n\n{detail_text}")
            
            # 버튼 스타일 적용
            msg_box.setStandardButtons(QMessageBox.Ok)
            ok_button = msg_box.button(QMessageBox.Ok)
            ok_button.setText("확인")
            ok_button.setStyleSheet("""
                QPushButton {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #a6dcef, stop:1 #7fbfe0);
                    color: white;
                    border: none;
                    border-radius: 4px;
                    padding: 6px 16px;
                    font-size: 14px;
                    font-weight: 600;
                    min-width: 80px;
                }
                QPushButton:hover {
                    background: #7fbfe0;
                }
            """)
            
            # 전체 다이얼로그 스타일 설정
            msg_box.setStyleSheet("""
                QMessageBox {
                    background-color: white;
                }
                QLabel {
                    font-size: 14px;
                    color: #333;
                    font-family: 'SF Pro', '맑은 고딕', Arial, sans-serif;
                }
            """)
            
            # 다이얼로그 크기 조정을 위한 너비 설정
            msg_box.setMinimumWidth(400)
            
            msg_box.exec()

    def load_settings(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "설정 불러오기", "naver_keyword_config.json", "JSON files (*.json)")
        if file_path and os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            for k, v in self.entries.items():
                v.setText(config.get(k, ""))
            self.config_path = file_path
            
            # 메시지 박스 개선
            msg_box = QMessageBox(self)
            msg_box.setWindowTitle("설정 불러오기 완료")
            msg_box.setIcon(QMessageBox.Information)
            
            # 메인 메시지와 상세 설명을 함께 표시
            main_text = "API 설정이 성공적으로 불러와졌습니다."
            info_text = f"불러온 파일: {file_path}"
            
            # 불러온 키워드 정보 추가 (있는 경우)
            keyword = config.get("keyword", "")
            keyword_text = f"검색 키워드: {keyword}" if keyword else ""
            
            detail_text = "모든 API 정보가 입력란에 적용되었습니다. 이제 '분석 실행' 버튼을 클릭하여 검색을 시작하세요."
            
            # 모든 정보를 한 번에 표시
            full_text = f"{main_text}\n\n{info_text}"
            if keyword_text:
                full_text += f"\n{keyword_text}"
            full_text += f"\n\n{detail_text}"
            
            msg_box.setText(full_text)
            
            # 버튼 스타일 적용
            msg_box.setStandardButtons(QMessageBox.Ok)
            ok_button = msg_box.button(QMessageBox.Ok)
            ok_button.setText("확인")
            ok_button.setStyleSheet("""
                QPushButton {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #a6dcef, stop:1 #7fbfe0);
                    color: white;
                    border: none;
                    border-radius: 4px;
                    padding: 6px 16px;
                    font-size: 14px;
                    font-weight: 600;
                    min-width: 80px;
                }
                QPushButton:hover {
                    background: #7fbfe0;
                }
            """)
            
            # 전체 다이얼로그 스타일 설정
            msg_box.setStyleSheet("""
                QMessageBox {
                    background-color: white;
                }
                QLabel {
                    font-size: 14px;
                    color: #333;
                    font-family: 'SF Pro', '맑은 고딕', Arial, sans-serif;
                }
            """)
            
            # 다이얼로그 크기 조정을 위한 너비 설정
            msg_box.setMinimumWidth(400)
            
            msg_box.exec()

    def on_header_click(self, idx):
        """테이블 헤더 클릭 시 호출되는 함수"""
        print(f"헤더 클릭 이벤트 발생: {self.columns[idx]} (인덱스: {idx})")
        col = self.columns[idx]
        if self.selected_col == col:
            self.sort_reverse = not self.sort_reverse
        else:
            self.sort_reverse = False
        self.selected_col = col
        
        # 정렬 수행
        self.sort_column(idx, self.sort_reverse)
        
        # 헤더 텍스트 업데이트
        self.update_header_texts()
        
        # 그래프를 직접 업데이트 - 타이머를 사용하여 UI 업데이트 후 실행
        QTimer.singleShot(100, self.update_graph_from_table)
    
    def update_header_texts(self):
        for i, col in enumerate(self.columns):
            if col == self.selected_col:
                arrow = "↓" if self.sort_reverse else "↑"
                self.table.horizontalHeaderItem(i).setText(f"{arrow} {col}")
            else:
                self.table.horizontalHeaderItem(i).setText(col)

    def sort_column(self, idx, reverse):
        def try_float(val):
            try:
                return float(str(val).replace(',', ''))
            except:
                return str(val)
        col = self.columns[idx]
        data = []
        for row in range(self.table.rowCount()):
            row_data = [self.table.item(row, c).text() for c in range(self.table.columnCount())]
            data.append(row_data)
        if col in ('총 검색량', 'PC', 'MOBILE', '월평균 노출 광고수'):
            data.sort(key=lambda x: try_float(x[idx]), reverse=reverse)
        elif col == '경쟁정도':
            order = {'높음': 3, '중간': 2, '낮음': 1}
            data.sort(key=lambda x: order.get(x[idx], 0), reverse=reverse)
        else:
            data.sort(key=lambda x: x[idx], reverse=reverse)
        self.table.setRowCount(0)
        
        # PySide6 GUI 관련 클래스 임포트 (지역에서 필요할 때만 로드)
        from PySide6.QtGui import QColor, QBrush, QFont
        
        for row in data:
            row_idx = self.table.rowCount()
            self.table.insertRow(row_idx)
            # 현재 행의 키워드가 검색한 키워드와 일치하는지 확인
            is_searched_keyword = row[0].lower() == self.current_search_keyword if self.current_search_keyword else False
            
            for col_idx, val in enumerate(row):
                item = QTableWidgetItem(str(val))
                
                # 검색한 키워드와 일치하면 텍스트 색상을 붉은색으로 변경
                if is_searched_keyword:
                    item.setForeground(QBrush(QColor('#FF5555')))  # 붉은색으로 설정
                    # 첫 번째 열(키워드)만 굵게 표시
                    if col_idx == 0:
                        font = item.font()
                        font.setBold(True)
                        item.setFont(font)
                
                self.table.setItem(row_idx, col_idx, item)
        
        # 정렬 후 이 함수에서도 직접 업데이트 (중복 호출되어도 상관없음)
        # self.update_graph_from_table() - on_header_click에서 호출하므로 여기서는 제거

    def update_graph_from_table(self):
        """현재 테이블 데이터를 기반으로 그래프 업데이트"""
        try:
            if self.table.rowCount() == 0:
                print("테이블에 데이터가 없어 그래프를 업데이트하지 않습니다.")
                return
                
            # 테이블에서 키워드와 총 검색량 데이터 추출
            keyword_graph_data = []
            row_limit = min(15, self.table.rowCount())  # 상위 15개만 사용
            print(f"그래프 업데이트 시작: 테이블 행 수 = {self.table.rowCount()}, 사용할 행 수 = {row_limit}")
            
            for row in range(row_limit):
                try:
                    keyword_item = self.table.item(row, 0)  # 키워드는 첫 번째 열
                    total_item = self.table.item(row, 1)    # 총 검색량은 두 번째 열
                    
                    if keyword_item and total_item:
                        keyword = keyword_item.text()
                        total_text = str(total_item.text()).replace(',', '')
                        if total_text.strip():  # 빈 문자열이 아닌지 확인
                            total = int(total_text)
                            keyword_graph_data.append((keyword, total))
                            print(f"  행 {row}: 키워드 '{keyword}', 검색량 {total}")
                except (ValueError, AttributeError, Exception) as e:
                    print(f"  행 {row} 처리 오류: {e}")
                    continue
            
            # 디버깅 메시지 출력
            print(f"그래프 업데이트: {len(keyword_graph_data)}개 항목 추출 완료")
            
            # 그래프 업데이트
            if keyword_graph_data:
                # 그래프 데이터를 검색량 기준 내림차순으로 정렬 (그래프 시각화 용도)
                sorted_data = sorted(keyword_graph_data, key=lambda x: x[1], reverse=True)
                self.draw_keyword_graph(sorted_data)
            else:
                print("  추출된 데이터가 없어 그래프를 업데이트하지 않습니다.")
                # 그래프 영역에 메시지 표시
                for i in reversed(range(self.graph_layout.count())):
                    self.graph_layout.itemAt(i).widget().setParent(None)
                no_data_label = QLabel("정렬된 데이터를 그래프로 표시할 수 없습니다.")
                no_data_label.setAlignment(Qt.AlignCenter)
                no_data_label.setStyleSheet("color: #666; font-size: 14px;")
                self.graph_layout.addWidget(no_data_label)
        except Exception as e:
            print(f"그래프 업데이트 중 오류 발생: {e}")
            # 오류 발생 시 그래프 영역에 메시지 표시
            for i in reversed(range(self.graph_layout.count())):
                self.graph_layout.itemAt(i).widget().setParent(None)
            error_label = QLabel(f"그래프 업데이트 오류: {str(e)}")
            error_label.setAlignment(Qt.AlignCenter)
            error_label.setStyleSheet("color: red; font-size: 12px;")
            self.graph_layout.addWidget(error_label)

    def export_to_excel(self):
        try:
            import pandas as pd
        except ImportError:
            QMessageBox.critical(self, "엑셀 저장 오류", "pandas 패키지가 필요합니다.\n명령프롬프트에서 'pip install pandas openpyxl' 실행 후 다시 시도하세요.")
            return
        # 테이블 데이터 추출
        data = []
        for row in range(self.table.rowCount()):
            row_data = []
            for col in range(self.table.columnCount()):
                item = self.table.item(row, col)
                row_data.append(item.text() if item else "")
            data.append(row_data)
        if not data:
            QMessageBox.warning(self, "엑셀 저장", "저장할 데이터가 없습니다.")
            return
        df = pd.DataFrame(data, columns=self.columns)
        from PySide6.QtWidgets import QFileDialog
        file_path, _ = QFileDialog.getSaveFileName(self, "엑셀로 저장", "keyword_result.xlsx", "Excel Files (*.xlsx)")
        if not file_path:
            return
        try:
            df.to_excel(file_path, index=False)
            # 메시지 박스 개선
            msg_box = QMessageBox(self)
            msg_box.setWindowTitle("엑셀 다운로드 완료")
            msg_box.setIcon(QMessageBox.Information)
            keyword = self.entries["keyword"].text().strip()
            
            # 메인 메시지와 상세 설명을 함께 표시
            main_text = f"'{keyword}' 키워드 검색 결과가 엑셀 파일로 저장되었습니다."
            info_text = f"저장 위치: {file_path}"
            detail_text = "엑셀 파일이 성공적으로 저장되었습니다.\n이 파일은 Microsoft Excel 또는 다른 스프레드시트 프로그램에서 열 수 있습니다."
            
            # 모든 정보를 한 번에 표시
            msg_box.setText(f"{main_text}\n\n{info_text}\n\n{detail_text}")
            
            # 버튼 스타일 적용
            msg_box.setStandardButtons(QMessageBox.Ok)
            ok_button = msg_box.button(QMessageBox.Ok)
            ok_button.setText("확인 완료")
            ok_button.setStyleSheet("""
                QPushButton {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #4f8cff, stop:1 #357ae8);
                    color: white;
                    border: none;
                    border-radius: 4px;
                    padding: 6px 16px;
                    font-size: 14px;
                    font-weight: 600;
                    min-width: 80px;
                }
                QPushButton:hover {
                    background: #357ae8;
                }
            """)
            
            # 전체 다이얼로그 스타일 설정
            msg_box.setStyleSheet("""
                QMessageBox {
                    background-color: white;
                }
                QLabel {
                    font-size: 14px;
                    color: #333;
                    font-family: 'SF Pro', '맑은 고딕', Arial, sans-serif;
                }
            """)
            
            # 다이얼로그 크기 조정을 위한 너비 설정
            msg_box.setMinimumWidth(400)
            
            msg_box.exec()
        except Exception as e:
            QMessageBox.critical(self, "엑셀 저장 오류", f"엑셀 저장 중 오류 발생:\n{str(e)}\n{traceback.format_exc()}")

    def draw_keyword_graph(self, keywords):
        if not MATPLOTLIB_AVAILABLE:
            no_matplotlib_label = QLabel("matplotlib 패키지가 필요합니다.\n'pip install matplotlib' 후 다시 실행하세요.")
            no_matplotlib_label.setAlignment(Qt.AlignCenter)
            no_matplotlib_label.setStyleSheet("color: #666; font-size: 14px;")
            
            # 기존 위젯 제거
            for i in reversed(range(self.graph_layout.count())): 
                self.graph_layout.itemAt(i).widget().setParent(None)
                
            self.graph_layout.addWidget(no_matplotlib_label)
            return
            
        # 기존 그래프 제거
        for i in reversed(range(self.graph_layout.count())):
            self.graph_layout.itemAt(i).widget().setParent(None)
        if self.graph_canvas:
            self.graph_canvas.setParent(None)
            self.graph_canvas = None
            
        # 상위 15개만
        top_keywords = sorted(keywords, key=lambda x: x[1], reverse=True)[:15]
        if not top_keywords:
            no_data_label = QLabel("데이터가 없습니다.")
            no_data_label.setAlignment(Qt.AlignCenter)
            no_data_label.setStyleSheet("color: #666; font-size: 14px;")
            self.graph_layout.addWidget(no_data_label)
            return
            
        try:
            # 저장된 검색 키워드 사용 (클래스 변수)
            original_keyword = self.current_search_keyword
            
            # 한글 폰트 설정 (에러 처리 추가)
            try:
                plt.rcParams['font.family'] = 'Malgun Gothic'
            except:
                try:
                    # 대체 폰트 시도
                    plt.rcParams['font.family'] = 'AppleGothic, Malgun Gothic, Gulim, Arial'
                except:
                    pass  # 폰트 설정 실패해도 계속 진행
            
            # 그래프 크기를 더 크게 설정 (가로, 세로 비율 모두 증가)
            fig, ax = plt.subplots(figsize=(8, 5), dpi=100)
            
            # 데이터 준비
            keywords_labels = [k[0] for k in top_keywords]
            values = [k[1] for k in top_keywords]
            
            # 막대 색상 설정 (검색한 키워드만 붉은색으로)
            bar_colors = []
            for keyword in keywords_labels:
                if original_keyword and keyword.lower() == original_keyword:
                    bar_colors.append('#FF5555')  # 붉은색 (사용자 검색 키워드)
                else:
                    bar_colors.append('#a6dcef')  # 파스텔톤 하늘색 (기타 키워드)
            
            # 막대 그래프 생성
            bars = ax.bar(range(len(top_keywords)), values, color=bar_colors, width=0.6)
            
            # Y축 라벨에 천 단위 콤마 추가
            ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, loc: "{:,}".format(int(x))))
            
            # X축 레이블 설정 - 가독성 향상
            plt.xticks(range(len(top_keywords)), keywords_labels, rotation=45, ha='right', fontsize=10)
            
            # 막대 위에 값 표시
            for bar in bars:
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height + 0.1,
                        '{:,}'.format(int(height)),
                        ha='center', va='bottom', fontsize=9)
            
            ax.set_ylabel('총 검색량', fontsize=12)
            ax.set_title('상위 키워드별 총 검색량', fontsize=14, pad=15)
            
            # 그래프 레이아웃 여백 조정
            fig.tight_layout()
            
            self.graph_canvas = FigureCanvas(fig)
            self.graph_layout.addWidget(self.graph_canvas)
            
        except Exception as e:
            error_label = QLabel(f"그래프 생성 오류: {str(e)}")
            error_label.setAlignment(Qt.AlignCenter)
            error_label.setStyleSheet("color: red; font-size: 12px;")
            self.graph_layout.addWidget(error_label)

if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    win = NaverKeywordApp()
    win.resize(1200, 700)
    win.show()
    sys.exit(app.exec())