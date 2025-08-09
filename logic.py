import json
import os
import sys
from PySide6.QtCore import QObject, Signal, QSettings

class ExpenseLogic(QObject):
    load_records_to_model = Signal(list)
    add_record_to_model = Signal(dict)
    remove_records_from_model = Signal(list)
    error_occurred = Signal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # 获取exe或py文件所在目录
        if hasattr(sys, 'frozen'):
            app_dir = os.path.dirname(sys.executable)
        else:
            app_dir = os.path.dirname(os.path.abspath(__file__))
        
        config_path = os.path.join(app_dir, 'config.ini')
        self.settings = QSettings(config_path, QSettings.IniFormat)
        self.records = []

    def load_records(self, filepath):
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                self.records = json.load(f)
            self.settings.setValue('last_save_dir', os.path.dirname(filepath))
        except (json.JSONDecodeError, IOError) as e:
            self.error_occurred.emit(f"加载数据失败: {e}")
            self.records = []
        self.load_records_to_model.emit(self.records)   

    def save_records(self, filepath):
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(self.records, f, ensure_ascii=False, indent=4)
            # 保存目录到配置文件
            self.settings.setValue('last_save_dir', os.path.dirname(filepath))
        except IOError as e:
            self.error_occurred.emit(f"保存数据失败: {e}")

    def add_record(self, record):
        self.records.append(record)
        self.add_record_to_model.emit(record)
    
    def remove_records(self, indexes):
        for index in sorted(indexes, reverse=True):
            del self.records[index]
        self.remove_records_from_model.emit(indexes)

    

    def get_all_records(self):
        return self.records
    
    def get_last_save_dir(self):
        return self.settings.value('last_save_dir', os.path.expanduser('~'))