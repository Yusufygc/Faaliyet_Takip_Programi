# views/pages/pdf_page.py
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QLabel, QPushButton, 
                             QFileDialog, QMessageBox, QCheckBox, QFrame)
from PyQt5.QtCore import Qt
from views.widgets import MonthYearWidget
from services.pdf_service import PDFService
from datetime import datetime
import os

class PdfPage(QWidget):
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.pdf_service = PDFService()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)

        # --- Kart Tasarımı ---
        card = QFrame()
        card.setObjectName("card")
        card.setFixedSize(450, 400)
        
        card_layout = QVBoxLayout(card)
        card_layout.setSpacing(20)
        card_layout.setContentsMargins(30, 30, 30, 30)

        # Başlık
        title = QLabel("PDF Raporu Oluştur")
        title.setStyleSheet("font-size: 20px; font-weight: bold; color: #2C3E50; border: none;")
        title.setAlignment(Qt.AlignCenter)
        card_layout.addWidget(title)

        # Açıklama
        desc = QLabel("Rapor almak istediğiniz dönemi seçiniz.\n(Tüm yıl için 'Tüm Aylar'ı seçin)")
        desc.setStyleSheet("color: #7F8C8D; font-size: 13px; border: none;")
        desc.setAlignment(Qt.AlignCenter)
        card_layout.addWidget(desc)

        # Tarih Seçimi
        self.date_picker = MonthYearWidget()
        # Varsayılan olarak yıllık modda başlasın
        # self.date_picker.set_year_only_mode(True) # İsteğe bağlı
        card_layout.addWidget(self.date_picker)

        # İsteğe Bağlı: Sadece Yıl Seçimi Kutucuğu
        self.chk_year_only = QCheckBox("Sadece Yıllık Rapor")
        self.chk_year_only.setStyleSheet("color: #2C3E50; font-weight: bold;")
        self.chk_year_only.toggled.connect(self.toggle_year_mode)
        card_layout.addWidget(self.chk_year_only)

        # Oluştur Butonu
        btn_create = QPushButton("📄 Raporu Kaydet")
        btn_create.setObjectName("btn_success")
        btn_create.setCursor(Qt.PointingHandCursor)
        btn_create.setMinimumHeight(50)
        btn_create.clicked.connect(self.generate_pdf)
        card_layout.addWidget(btn_create)

        layout.addWidget(card)

    def toggle_year_mode(self, checked):
        """Sadece yıl seçilecekse ay kutusunu pasif yap."""
        self.date_picker.set_year_only_mode(checked)

    def generate_pdf(self):
        # 1. Tarihi Al
        date_prefix = self.date_picker.get_date_str()
        
        # 2. Dosya Kayıt Yeri
        default_name = f"Rapor_{date_prefix if date_prefix else 'TumZamanlar'}.pdf"
        file_path, _ = QFileDialog.getSaveFileName(self, "PDF Kaydet", default_name, "PDF Files (*.pdf)")
        
        if not file_path:
            return # İptal edildi

        # Buton durumu
        sender = self.sender()
        if sender: sender.setEnabled(False)
        
        # Safe StatusBar Access
        window = self.window()
        if window and hasattr(window, 'statusBar') and window.statusBar():
            window.statusBar().showMessage("PDF hazırlanıyor...", 1000)

        # 3. Verileri Çek (Asenkron)
        self.controller.get_pdf_data(
            lambda data: self.on_pdf_data_loaded(data, file_path, date_prefix, sender),
            date_prefix
        )

    def on_pdf_data_loaded(self, raw_data, file_path, date_prefix, btn_sender):
        if btn_sender: btn_sender.setEnabled(True)

        if not raw_data:
            QMessageBox.warning(self, "Uyarı", "Seçilen dönem için kayıtlı veri bulunamadı.")
            return

        # 4. Özet Bilgi Hazırla
        summary = {
            "Rapor Dönemi": date_prefix if date_prefix else "Tüm Zamanlar",
            "Toplam Faaliyet Sayısı": len(raw_data),
            "Rapor Türü": "Yıllık" if len(date_prefix) == 4 else "Aylık"
        }

        # 5. Servisi Çağır
        try:
             success, message = self.pdf_service.create_report(
                file_path, 
                f"{date_prefix} Dönemi Faaliyet Raporu", 
                summary, 
                raw_data
            )
             if success:
                QMessageBox.information(self, "Başarılı", message)
                try:
                    os.startfile(file_path) # Windows'ta dosyayı aç
                except:
                    pass
             else:
                QMessageBox.critical(self, "Hata", message)

        except Exception as e:
            QMessageBox.critical(self, "Hata", f"PDF oluşturulamadı: {e}")
            
        # Safe StatusBar Access
        window = self.window()
        if window and hasattr(window, 'statusBar') and window.statusBar():
            window.statusBar().showMessage("İşlem tamamlandı.", 2000)