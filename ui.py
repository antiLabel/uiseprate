
from PySide6.QtWidgets import (QMainWindow, QApplication,QTableView, QDialog, QVBoxLayout,
                                QFormLayout, QLabel, QLineEdit, QDoubleSpinBox,
                                QComboBox, QDateEdit, QFileDialog, QDialogButtonBox, QMessageBox)
from PySide6.QtGui import QStandardItemModel, QStandardItem, QAction
from PySide6.QtCore import Qt, QDate
from logic import ExpenseLogic
from qt_material import apply_stylesheet


class AddExpenseDialog(QDialog):
    def __init__(self, categories, parent=None):
        super().__init__(parent)
        self.setWindowTitle('添加新账目')
        self.setModal(True)

        self.date_edit = QDateEdit(QDate.currentDate(), self)
        self.date_edit.setCalendarPopup(True)

        self.desc_edit = QLineEdit(self)
        self.amount_spin = QDoubleSpinBox(self)
        self.amount_spin.setRange(0, 1e9)
        self.amount_spin.setDecimals(2)

        self.category_combo = QComboBox(self)
        self.category_combo.addItems(categories)

        form_layout = QFormLayout()
        form_layout.addRow('日期：', self.date_edit)
        form_layout.addRow('描述：', self.desc_edit)
        form_layout.addRow('金额：', self.amount_spin)
        form_layout.addRow('类别：', self.category_combo)

        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)

        main_layout = QVBoxLayout()
        main_layout.addLayout(form_layout)
        main_layout.addWidget(button_box)
        self.setLayout(main_layout)

    def get_data(self):
        return {
            'date': self.date_edit.date().toString(Qt.ISODate),
            'description': self.desc_edit.text(),
            'amount': self.amount_spin.value(),
            'category': self.category_combo.currentText()
        }


class ExpenseTrackerApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Expense Tracker")
        self.setGeometry(500, 100, 800, 600)

        # 1. 创建逻辑处理器实例
        self.logic = ExpenseLogic(self) 
        
        self.logic.add_record_to_model.connect(self.model_add_record)  
        self.logic.remove_records_from_model.connect(self.model_remove_records)
        self.logic.load_records_to_model.connect(self.model_load_records)
        self.logic.error_occurred.connect(self.show_error)

        self.categories = ["食品", "交通", "娱乐", "医疗", "其他"]  # 示例类别
        self.add_action()
        self.init_ui()
        self._setup_model()

    
    def add_action(self): 
        self.add_expense_action = QAction("添加账目", self)
        self.add_expense_action.setStatusTip("添加新的费用记录")
        self.add_expense_action.triggered.connect(self.add_expense)

        self.delete_expense_action = QAction("删除账目", self)
        self.delete_expense_action.setStatusTip("删除选中的费用记录")
        self.delete_expense_action.triggered.connect(self.delete_expense)

        self.save_data_action = QAction("保存数据", self)
        self.save_data_action.setStatusTip("保存当前数据到文件")
        self.save_data_action.triggered.connect(self.save_data)

        self.load_data_action = QAction("加载数据", self)
        self.load_data_action.setStatusTip("从文件加载数据")
        self.load_data_action.triggered.connect(self.load_data)


    def init_ui(self):
        self.table_view = QTableView(self)
        self.setCentralWidget(self.table_view)
        self.statusBar().showMessage("欢迎使用费用追踪器", 3000)
        data_menu = self.menuBar().addMenu("数据")
        data_menu.addAction(self.save_data_action)
        data_menu.addAction(self.load_data_action)
        expense_menu = self.menuBar().addMenu("账目")
        expense_menu.addAction(self.add_expense_action)
        expense_menu.addAction(self.delete_expense_action)

        self.toolBar = self.addToolBar("工具栏")
        self.toolBar.addAction(self.add_expense_action)
        self.toolBar.addAction(self.delete_expense_action)

        
    def _setup_model(self):
        self.model = QStandardItemModel(0, 4, self)
        self.model.setHorizontalHeaderLabels(["日期", "描述", "金额", "类别"])
        self.table_view.setModel(self.model)


    def add_expense(self):
        dialog = AddExpenseDialog(self.categories, self)
        if dialog.exec():
            new_record = dialog.get_data()
            if new_record:
                self.logic.add_record(new_record)

    def delete_expense(self):
        selected_row_qindexs = self.table_view.selectionModel().selectedRows()
        selected_row_indexs = [index.row() for index in selected_row_qindexs]
        self.logic.remove_records(selected_row_indexs)

    def save_data(self):
        default_dir = self.logic.get_last_save_dir()
        path, _ = QFileDialog.getSaveFileName(
            self, '保存文件', default_dir, 'JSON 文件 (*.json)'
        )
        if not path:
            return
        self.logic.save_records(path)
        self.statusBar().showMessage("数据已保存", 3000)

    def load_data(self):
        default_dir = self.logic.get_last_save_dir()
        path, _ = QFileDialog.getOpenFileName(
            self, '加载文件', default_dir, 'JSON 文件 (*.json)'
        )
        if not path:
            return
        self.logic.load_records(path)
        self.statusBar().showMessage("数据已加载", 3000)
    
    def model_load_records(self, records):
        self.model.setRowCount(0)
        for record in records:
            self.model_add_record(record)

    def model_add_record(self,  record):
        items = [
            QStandardItem(record.get('date', '')),
            QStandardItem(record.get('description', '')),
            QStandardItem(f"{record.get('amount', 0):.2f}"),
            QStandardItem(record.get('category', ''))
        ]
        for item in items:
            item.setEditable(False)
        self.model.appendRow(items)

    def model_remove_records(self, indexes):
        for index in sorted(indexes, reverse=True):
            self.model.removeRow(index)
    
    def show_error(self, error_message):
        QMessageBox.critical(self, '错误', error_message)

if __name__ == "__main__":
    app = QApplication([])
    apply_stylesheet(app, theme='dark_blue.xml')  # 使用qt-material主题
    window = ExpenseTrackerApp()
    window.show()
    app.exec()