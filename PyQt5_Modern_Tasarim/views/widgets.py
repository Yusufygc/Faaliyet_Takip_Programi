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
        self.layout.setSpacing(5) # Elemanlar arası boşluk
        
        # Yıl Seçimi
        self.combo_year = QComboBox()
        current_year = datetime.now().year
        
        # YENİ: Tüm Yıllar seçeneği en başa eklendi
        self.combo_year.addItem("Tüm Yıllar") 
        self.combo_year.addItems([str(y) for y in range(2020, current_year + 2)])
        
        # Varsayılan olarak "Tüm Yıllar" mı yoksa "Mevcut Yıl" mı gelsin?
        # Kullanıcı genelde günceli görmek ister, o yüzden mevcut yılı seçelim.
        self.combo_year.setCurrentText(str(current_year))
        
        # Ay Seçimi
        self.combo_month = QComboBox()
        self.combo_month.addItem("Tüm Aylar") 
        self.combo_month.addItems([f"{m:02d}" for m in range(1, 13)])
        
        self.layout.addWidget(self.combo_year)
        self.layout.addWidget(self.combo_month)

        # Sinyal Bağlantıları
        self.combo_year.currentIndexChanged.connect(self.on_year_changed) # Özel slot
        self.combo_month.currentIndexChanged.connect(self.emit_signal)

    def on_year_changed(self):
        """Yıl değiştiğinde ay kutusunun durumunu güncelle."""
        is_all_years = (self.combo_year.currentIndex() == 0) # "Tüm Yıllar" seçili mi?
        
        # Eğer Tüm Yıllar seçiliyse, Ay seçimi mantıksız olur, pasif yapalım
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
        
        # "Tüm Yıllar" seçiliyse (index 0) boş döndür -> Filtre Yok
        if self.combo_year.currentIndex() == 0:
            return ""
            
        if month_idx == 0: # "Tüm Aylar" seçili
            return year
        else:
            return f"{year}-{month_text}"

    def clear_filters(self):
        """Seçimleri varsayılan değerlere döndürür."""
        current_year = datetime.now().year
        self.combo_year.blockSignals(True)
        self.combo_month.blockSignals(True)
        
        self.combo_year.setCurrentText(str(current_year))
        self.combo_month.setCurrentIndex(0)
        self.combo_month.setEnabled(True)
        
        self.combo_year.blockSignals(False)
        self.combo_month.blockSignals(False)
        self.emit_signal()
    
    def set_enabled(self, enabled):
        self.combo_year.setEnabled(enabled)
        # Ay kutusu sadece yıl seçiliyse aktif olmalı
        is_all_years = (self.combo_year.currentIndex() == 0)
        self.combo_month.setEnabled(enabled and not is_all_years)