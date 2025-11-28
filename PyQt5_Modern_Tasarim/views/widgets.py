# views/widgets.py
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QComboBox
from PyQt5.QtCore import pyqtSignal
from datetime import datetime

class MonthYearWidget(QWidget):
    dateChanged = pyqtSignal(str) 

    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(5)
        
        # Bu flag, dışarıdan (örneğin PDF sayfasındaki checkbox ile) 
        # ay seçiminin zorla kapatılıp kapatılmadığını takip eder.
        self._year_only_forced = False 
        
        # Yıl Seçimi
        self.combo_year = QComboBox()
        current_year = datetime.now().year
        
        self.combo_year.addItem("Tüm Yıllar") 
        self.combo_year.addItems([str(y) for y in range(2020, current_year + 2)])
        self.combo_year.setCurrentText(str(current_year))
        
        # Ay Seçimi
        self.combo_month = QComboBox()
        self.combo_month.addItem("Tüm Aylar") 
        self.combo_month.addItems([f"{m:02d}" for m in range(1, 13)])
        
        self.layout.addWidget(self.combo_year)
        self.layout.addWidget(self.combo_month)

        # Sinyal Bağlantıları
        self.combo_year.currentIndexChanged.connect(self.on_year_changed)
        self.combo_month.currentIndexChanged.connect(self.emit_signal)

    def on_year_changed(self):
        """Yıl değiştiğinde ay kutusunun durumunu güncelle."""
        is_all_years = (self.combo_year.currentIndex() == 0) # "Tüm Yıllar" seçili mi?
        
        # Eğer dışarıdan "Sadece Yıl" modu zorlanmadıysa,
        # "Tüm Yıllar" seçimine göre ay kutusunu aç/kapat.
        if not self._year_only_forced:
            self.combo_month.setEnabled(not is_all_years)
        
        if is_all_years:
            self.combo_month.setCurrentIndex(0) # Ayı sıfırla
            
        self.emit_signal()

    def emit_signal(self):
        self.dateChanged.emit(self.get_date_str())

    def get_date_str(self):
        year = self.combo_year.currentText()
        month_idx = self.combo_month.currentIndex()
        month_text = self.combo_month.currentText()
        
        if self.combo_year.currentIndex() == 0: # "Tüm Yıllar"
            return ""
            
        if month_idx == 0: # "Tüm Aylar"
            return year
        else:
            return f"{year}-{month_text}"

    def clear_filters(self):
        current_year = datetime.now().year
        self.combo_year.blockSignals(True)
        self.combo_month.blockSignals(True)
        
        self.combo_year.setCurrentText(str(current_year))
        self.combo_month.setCurrentIndex(0)
        
        # Dış zorlamayı kaldır
        self._year_only_forced = False
        self.combo_month.setEnabled(True)
        
        self.combo_year.blockSignals(False)
        self.combo_month.blockSignals(False)
        self.emit_signal()
    
    def set_enabled(self, enabled):
        self.combo_year.setEnabled(enabled)
        is_all_years = (self.combo_year.currentIndex() == 0)
        # Eğer dışarıdan zorlanmadıysa durumu koru
        if not self._year_only_forced:
            self.combo_month.setEnabled(enabled and not is_all_years)
        else:
            self.combo_month.setEnabled(False)

    # --- EKSİK OLAN METOD BURAYA EKLENDİ ---
    def set_year_only_mode(self, enabled: bool):
        """Dışarıdan (örn: Checkbox) sadece yıl modunu zorlamak için."""
        self._year_only_forced = enabled
        
        if enabled:
            self.combo_month.setCurrentIndex(0) # Tüm Aylar'a getir
            self.combo_month.setEnabled(False)  # Kutuyu kilitle
        else:
            # Kilidi aç, ama "Tüm Yıllar" seçiliyse hala kapalı kalsın
            is_all_years = (self.combo_year.currentIndex() == 0)
            self.combo_month.setEnabled(not is_all_years)