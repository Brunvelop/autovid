import sys
import threading
import uvicorn
import requests
from time import sleep
from PyQt6.QtCore import Qt, QUrl, QTimer
from PyQt6.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QWidget, QProgressBar
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebEngineCore import QWebEngineProfile

class FastAPIWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("FastAPI App")
        
        # Configurar el tamaño y posición de la ventana
        self.setGeometry(100, 100, 800, 600)
        
        # Crear el widget central
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)
        
        # Crear la pantalla de carga
        self.loading_widget = QWidget()
        loading_layout = QVBoxLayout(self.loading_widget)
        
        # Añadir mensaje de carga
        loading_label = QLabel("Iniciando servidor...")
        loading_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        loading_layout.addWidget(loading_label)
        
        # Añadir barra de progreso
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 0)  # Modo indeterminado
        loading_layout.addWidget(self.progress_bar)
        
        # Mostrar la pantalla de carga
        self.layout.addWidget(self.loading_widget)
        
        # Crear el widget del navegador (oculto inicialmente)
        self.browser = QWebEngineView()
        self.browser.hide()
        
        # Deshabilitar caché del navegador
        profile = QWebEngineProfile.defaultProfile()
        profile.setHttpCacheType(QWebEngineProfile.HttpCacheType.NoCache)
        
        # Configurar la URL de FastAPI
        self.api_url = "http://127.0.0.1:8000"
        self.browser.setUrl(QUrl(self.api_url))
        
        # Añadir el navegador al layout
        self.layout.addWidget(self.browser)
        
        # Iniciar el temporizador para verificar el servidor
        self.check_timer = QTimer()
        self.check_timer.timeout.connect(self.check_server)
        self.check_timer.start(100)  # Verificar cada 100ms
    
    def check_server(self):
        """Verifica si el servidor FastAPI está listo"""
        try:
            response = requests.get(self.api_url)
            if response.status_code == 200:
                # Servidor listo, mostrar el navegador
                self.loading_widget.hide()
                self.browser.show()
                self.check_timer.stop()
        except requests.exceptions.ConnectionError:
            # Servidor aún no está listo
            pass

def run_fastapi():
    """Función para ejecutar el servidor FastAPI"""
    uvicorn.run("UI_api:app", host="127.0.0.1", port=8000)

def main():
    # Iniciar el servidor FastAPI en un hilo separado
    fastapi_thread = threading.Thread(target=run_fastapi, daemon=True)
    fastapi_thread.start()
    
    # Crear la aplicación Qt
    app = QApplication(sys.argv)
    
    # Crear y mostrar la ventana principal
    window = FastAPIWindow()
    window.show()
    
    # Ejecutar el bucle de eventos
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
