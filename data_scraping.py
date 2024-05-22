import sys
import requests
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox, QTabWidget, QTextEdit, QHBoxLayout
)
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from bs4 import BeautifulSoup


def scrape(url):
    """
    Scrape the content of a webpage.

    This function takes a URL as input, sends a GET request to the URL, and parses the HTML content
    of the webpage using BeautifulSoup. It extracts the title, content, links, authors of comments,
    and the post link from the webpage.

    :param url: The URL of the webpage to scrape.
    :type url: str
    :return: A dictionary containing the scraped content, including the title, content, links,
             authors of comments, and the post link. If the webpage cannot be accessed, returns
             a string indicating the error.
    :rtype: Union[dict, str]
    """
    response = requests.get(url)
    if response.status_code == 200:
        html_content = response.content
        soup = BeautifulSoup(html_content, 'html.parser')

        baslik_etiketi = soup.find("h1", class_="entry-title")
        baslik = baslik_etiketi.text.strip() if baslik_etiketi else "Başlık bulunamadı"

        icerik_etiketleri = soup.find("div", class_="post-content entry-content")
        icerik_paragraflar = icerik_etiketleri.find_all("p") if icerik_etiketleri else []
        icerik = "\n".join([paragraf.text.strip() for paragraf in icerik_paragraflar])

        links = soup.find_all('a')
        link_listesi = [(link.get_text(strip=True), link.get('href')) for link in links]

        yorum_yazarlari = soup.find_all("cite", class_="fn")
        yazar_listesi = [yazar.text.strip() for yazar in yorum_yazarlari]

        post_title_div = soup.find("div", class_="post-title")
        if post_title_div:
            a_tag = post_title_div.find("a")
            if a_tag and 'href' in a_tag.attrs:
                post_link = a_tag['href']
            else:
                post_link = "Link bulunamadı"
        else:
            post_link = "Div bulunamadı"

        return {
            "baslik": baslik,
            "icerik": icerik,
            "linkler": link_listesi,
            "yorum_yazarlari": yazar_listesi,
            "post_link": post_link
        }
    else:
        return "Web sayfasına erişilemiyor."

class ScrapeThread(QThread):
    finished = pyqtSignal(dict)
    error = pyqtSignal(str)

    def __init__(self, url):
        super().__init__()
        self.url = url

    def run(self):
        result = scrape(self.url)
        if isinstance(result, str):
            self.error.emit(result)
        else:
            self.finished.emit(result)

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Web Scraper')

        self.layout = QVBoxLayout()

        self.url_label = QLabel('Please enter the requested website:')
        self.url_label.setFont(QFont('Arial', 14, QFont.Bold))
        self.layout.addWidget(self.url_label)

        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText('Enter the URL here...')
        self.url_input.setFont(QFont('Arial', 12))
        self.url_input.setStyleSheet("padding: 10px;")
        self.layout.addWidget(self.url_input)

        self.scrape_button = QPushButton('Scrape')
        self.scrape_button.setFont(QFont('Arial', 12, QFont.Bold))
        self.scrape_button.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                padding: 10px;
                border-radius: 5px;
                border: none;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:pressed {
                background-color: #4CAF50;
            }
        """)        
        self.scrape_button.clicked.connect(self.scrape_and_show)
        self.layout.addWidget(self.scrape_button)

        self.setLayout(self.layout)

        self.setStyleSheet("""
            QWidget {
                background-color: #f0f0f0;
            }
            QLabel {
                color: #333;
            }
            QLineEdit {
                border: 1px solid #ccc;
                border-radius: 5px;
            }
        """)

    def scrape_and_show(self):
        url = self.url_input.text()
        if url:
            self.thread = ScrapeThread(url)
            self.thread.finished.connect(self.show_content_window)
            self.thread.error.connect(self.show_error)
            self.thread.start()
        else:
            QMessageBox.warning(self, 'Uyarı', 'Lütfen geçerli bir URL girin.')

    
    def show_content_window(self, content):
        self.content_window = QWidget()
        self.content_window.setWindowTitle('Scraped Content')
        self.content_layout = QVBoxLayout()

        self.tabs = QTabWidget()

        # Başlık Sekmesi
        self.baslik_tab = QWidget()
        self.baslik_layout = QVBoxLayout()
        self.baslik_text = QTextEdit()
        self.baslik_text.setFont(QFont('Arial', 16, QFont.Bold))
        self.baslik_text.setStyleSheet("background-color: #fff; padding: 10px;")
        self.baslik_text.setPlainText(content["baslik"])
        self.baslik_text.setReadOnly(True)
        self.baslik_layout.addWidget(self.baslik_text)
        self.baslik_tab.setLayout(self.baslik_layout)
        self.tabs.addTab(self.baslik_tab, "Başlık")

        # İçerik Sekmesi
        self.icerik_tab = QWidget()
        self.icerik_layout = QVBoxLayout()
        self.icerik_text = QTextEdit()
        self.icerik_text.setFont(QFont('Arial', 12))
        self.icerik_text.setStyleSheet("background-color: #fff; padding: 10px;")
        self.icerik_text.setPlainText(content["icerik"])
        self.icerik_text.setReadOnly(True)
        self.icerik_layout.addWidget(self.icerik_text)
        self.icerik_tab.setLayout(self.icerik_layout)
        self.tabs.addTab(self.icerik_tab, "İçerik")

        # Linkler Sekmesi
        self.linkler_tab = QWidget()
        self.linkler_layout = QVBoxLayout()
        self.linkler_text = QTextEdit()
        self.linkler_text.setFont(QFont('Arial', 12))
        self.linkler_text.setStyleSheet("background-color: #fff; padding: 10px;")
        linkler_content = "\n".join([f"Link Başlığı: {link_text}\nURL: {link_url}" for link_text, link_url in content["linkler"]])
        self.linkler_text.setPlainText(linkler_content)
        self.linkler_text.setReadOnly(True)
        self.linkler_layout.addWidget(self.linkler_text)
        self.linkler_tab.setLayout(self.linkler_layout)
        self.tabs.addTab(self.linkler_tab, "Linkler")

        # Yorum Yazarları Sekmesi
        self.yazarlar_tab = QWidget()
        self.yazarlar_layout = QVBoxLayout()
        self.yazarlar_text = QTextEdit()
        self.yazarlar_text.setFont(QFont('Arial', 12))
        self.yazarlar_text.setStyleSheet("background-color: #fff; padding: 10px;")
        yazarlar_content = "\n".join([f"Yazar: {yazar}" for yazar in content["yorum_yazarlari"]])
        self.yazarlar_text.setPlainText(yazarlar_content)
        self.yazarlar_text.setReadOnly(True)
        self.yazarlar_layout.addWidget(self.yazarlar_text)
        self.yazarlar_tab.setLayout(self.yazarlar_layout)
        self.tabs.addTab(self.yazarlar_tab, "Yorum Yazarları")

        # Post Link Sekmesi
        self.post_link_tab = QWidget()
        self.post_link_layout = QVBoxLayout()
        self.post_link_text = QTextEdit()
        self.post_link_text.setFont(QFont('Arial', 12))
        self.post_link_text.setStyleSheet("background-color: #fff; padding: 10px;")
        self.post_link_text.setPlainText(content["post_link"])
        self.post_link_text.setReadOnly(True)
        self.post_link_layout.addWidget(self.post_link_text)
        self.post_link_tab.setLayout(self.post_link_layout)
        self.tabs.addTab(self.post_link_tab, "Post Link")

        self.content_layout.addWidget(self.tabs)
        self.content_window.setLayout(self.content_layout)
        self.content_window.resize(800, 600)
        self.content_window.show()


        self.tabs.setStyleSheet("""
            QTabWidget::pane { /* The tab widget frame */
                border: none;
                position: absolute;
                top: -0.5em;
                color: #333;
                background: #f0f0f0;
            }

            QTabWidget::tab-bar {
                alignment: center;
            }

            QTabBar::tab {
                background: #E0E0E0;
                border: 1px solid #C4C4C3;
                border-bottom-color: #C2C7CB; /* same as pane color */
                min-width: 8ex;
                padding: 10px;
                margin-right: 2px;
            }

            QTabBar::tab:first {
                border-top-left-radius: 10px;
            }

            QTabBar::tab:last {
                border-top-right-radius: 10px;
            }

            QTabBar::tab:selected, QTabBar::tab:hover {
                background: #45a049;
            }

            QTextEdit {
                border: 1px solid #ccc;
                border-radius: 5px;
                background-color: #fff;
                padding: 10px;
            }

            QScrollBar:vertical {
                background: #f0f0f0;
                width: 10px;
                margin: 0px 0px 0px 0px;
            }

            QScrollBar::handle:vertical {
                background: #45a049;
                min-height: 20px;
                border-radius: 5px;
            }

            QScrollBar::add-line:vertical {
                background: none;
                height: 0px;
                subcontrol-position: bottom;
                subcontrol-origin: margin;
            }

            QScrollBar::sub-line:vertical {
                background: none;
                height: 0px;
                subcontrol-position: top;
                subcontrol-origin: margin;
            }
        """)
        self.linkler_text.setStyleSheet("""
            QTextEdit {
                border: 1px solid #ccc;
                border-radius: 5px;
                background-color: #fff;
                padding: 10px;
            }
            QTextEdit::-webkit-scrollbar {
                width: 10px;
            }
            QTextEdit::-webkit-scrollbar-thumb {
                background-color: #4CAF50;
                border-radius: 5px;
            }
            QTextEdit::-webkit-scrollbar-track {
                background-color: #f0f0f0;
                border-radius: 5px;
            }
        """)

        self.icerik_text.setStyleSheet("""
            QTextEdit {
                border: 1px solid #ccc;
                border-radius: 5px;
                background-color: #fff;
                padding: 10px;
            }
            QTextEdit::-webkit-scrollbar {
                width: 10px;
            }
            QTextEdit::-webkit-scrollbar-thumb {
                background-color: #4CAF50;
                border-radius: 5px;
            }
            QTextEdit::-webkit-scrollbar-track {
                background-color: #f0f0f0;
                border-radius: 5px;
            }
        """)

    def show_error(self, message):
        QMessageBox.warning(self, 'Uyarı', message)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    mainWin = MainWindow()
    mainWin.resize(400, 200)
    mainWin.show()
    sys.exit(app.exec_())

