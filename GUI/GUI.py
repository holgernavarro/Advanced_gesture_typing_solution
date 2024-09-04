import sys
import asyncio
import pyautogui
import webbrowser
from bleak import BleakScanner, BleakClient
from PySide6.QtGui import QPixmap
from PySide6.QtCore import Qt, QThread, Signal
from PySide6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QListWidget, QLabel, QTextEdit, QProgressBar, QMainWindow, QMessageBox, QComboBox, QStyledItemDelegate)

# UUID del servicio y característica a leer
SERVICE_UUID = "12345678-1234-5678-1234-56789abcdef0"
CHARACTERISTIC_UUID = "abcdef01-1234-5678-1234-56789abcdef0"

class ScanThread(QThread):
    
    devices_discovered = Signal(list)

    def run(self):
        devices = asyncio.run(BleakScanner.discover())
        self.devices_discovered.emit(devices)

class ConnectThread(QThread):
    connection_status = Signal(str)
    notification_received = Signal(bytes)

    def __init__(self, device_address):
        super().__init__()
        self.device_address = device_address

    async def check_uuids(self, client):
        try:
            services = await client.get_services()
            for service in services:
                if service.uuid == SERVICE_UUID:
                    characteristics = [char.uuid for char in service.characteristics]
                    return CHARACTERISTIC_UUID in characteristics
        except Exception as e:
            print(f"Error checking UUIDs: {e}")
        return False

    def run(self):
        async def try_connect():
            async with BleakClient(self.device_address) as client:
                if client.is_connected:
                    if await self.check_uuids(client):
                        self.connection_status.emit(f"Connect to {self.device_address}")
                        await self.start_notification(client)
                    else:
                        self.connection_status.emit(f"Unsupported device")
                else:
                    self.connection_status.emit(f"Unable to connect to {self.device_address}")

        asyncio.run(try_connect())

    async def start_notification(self, client):
        def notification_handler(sender, data):
            self.notification_received.emit(data)

        await client.start_notify(CHARACTERISTIC_UUID, notification_handler)
        # Esperar por datos y mantener la conexión
        while client.is_connected:
            await asyncio.sleep(1)
        await client.stop_notify(CHARACTERISTIC_UUID)

class RoundedButton(QPushButton):
    def __init__(self, text, color, parent=None):
        super().__init__(text, parent)
        self.setFixedSize(260, 50)
        self.setStyleSheet(f"""
            QPushButton {{
                background-color: {color};
                color: white;
                border-radius: 10px;
                font-weight: bold;
                font-size: 14px;
                padding: 0;
            }}
            QPushButton:hover {{
                background-color: #0056b3;
            }}
        """)

class CenteredItemDelegate(QStyledItemDelegate):
    def initStyleOption(self, option, index):
        super().initStyleOption(option, index)
        option.displayAlignment = Qt.AlignCenter

class BLEInterface(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Advanced Gesture Typing Solution V1.0")
        self.setFixedSize(1280, 720)

        # Inicializa el modo en "teclado"
        self.mouse_mode = False

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        self.layout = QHBoxLayout(self.central_widget)

        # Marco izquierdo
        self.left_frame = QVBoxLayout()
        self.left_frame.setContentsMargins(20, 20, 20, 20)

        # Widget contenedor para aplicar el estilo
        self.left_widget = QWidget()
        self.left_widget.setLayout(self.left_frame)
        self.left_widget.setStyleSheet("background-color: #407BF6;")
        self.layout.addWidget(self.left_widget)

        self.info_label = QLabel("Advanced Gesture \n Typing Solution ")
        self.info_label.setStyleSheet("color: white; font-size: 24px;")
        self.info_label.setAlignment(Qt.AlignCenter)
        self.left_frame.addWidget(self.info_label)

        self.image_label1 = QLabel()
        pixmap1 = QPixmap("ecg-4.png")  # Actualiza la ruta a tu archivo de imagen
        self.image_label1.setPixmap(pixmap1)
        self.left_frame.addWidget(self.image_label1)

        self.image_label2 = QLabel()
        pixmap2 = QPixmap("teclado.png")  # Actualiza la ruta a tu segunda imagen
        self.image_label2.setPixmap(pixmap2)
        self.left_frame.addWidget(self.image_label2)

        # Centrar imágenes
        self.left_frame.setAlignment(self.image_label1, Qt.AlignCenter)
        self.left_frame.setAlignment(self.image_label2, Qt.AlignCenter)

        # Marco derecho
        self.right_frame = QVBoxLayout()
        self.layout.addLayout(self.right_frame)

        self.info_label = QLabel("📡 Bluetooth Devices:")
        self.info_label.setStyleSheet("color: black; font-size: 36px;")
        self.info_label.setAlignment(Qt.AlignCenter)
        self.right_frame.addWidget(self.info_label)

        # Lista de dispositivos centrada
        self.devices_listbox = QListWidget()
        self.devices_listbox.setFixedSize(550, 200)
        self.devices_listbox.setStyleSheet("color: black; font-size: 15px;")
        self.devices_listbox.setItemDelegate(CenteredItemDelegate())
        listbox_layout = QHBoxLayout()
        listbox_layout.addWidget(self.devices_listbox)
        listbox_layout.setAlignment(Qt.AlignCenter)  # Centrar horizontalmente
        self.right_frame.addLayout(listbox_layout)

        # Barra de progreso centrada
        self.progress = QProgressBar()
        self.progress.setRange(0, 0)
        self.progress.setTextVisible(False)
        self.progress.setVisible(False)  # Inicialmente oculta
        progress_layout = QHBoxLayout()
        progress_layout.addWidget(self.progress)
        progress_layout.setAlignment(Qt.AlignCenter)  # Centrar horizontalmente
        self.right_frame.addLayout(progress_layout)
        

        # Botón para cambiar el modo, centrado en la parte superior
        self.toggle_mode_button = RoundedButton("Mode: Keyboard", "#407BF6")
        self.toggle_mode_button.clicked.connect(self.toggle_mode)
        self.toggle_mode_button.setFixedSize(550, 50)
        toggle_mode_layout = QHBoxLayout()
        toggle_mode_layout.addWidget(self.toggle_mode_button)
        toggle_mode_layout.setAlignment(Qt.AlignCenter)  # Centrar horizontalmente
        self.right_frame.addLayout(toggle_mode_layout)

        # Agrupación de botones de escanear y conectar
        # Agrupación de botones de escanear y conectar
        self.button_group1 = QHBoxLayout()
        self.scan_button = RoundedButton("Scan", "#407BF6")
        self.scan_button.clicked.connect(self.scan_devices)
        self.button_group1.addWidget(self.scan_button)

        self.connect_button = RoundedButton("Connect", "#407BF6")
        self.connect_button.clicked.connect(self.connect_device)
        self.button_group1.addWidget(self.connect_button)

        self.right_frame.addLayout(self.button_group1)


        # Agrupación de botones de manual de usuario y créditos
        self.button_group2 = QHBoxLayout()
        self.manual_button = RoundedButton("User Manual", "#407BF6")
        self.manual_button.clicked.connect(self.open_manual)
        self.button_group2.addWidget(self.manual_button)

        self.credits_button = RoundedButton("Credits", "#407BF6")
        self.credits_button.clicked.connect(self.show_credits)
        self.button_group2.addWidget(self.credits_button)

        self.right_frame.addLayout(self.button_group2)

        # Widget para visualizar los datos recibidos, centrado
        self.data_text = QTextEdit()
        self.data_text.setFixedHeight(60)
        self.data_text.setStyleSheet("font-size: 48px;")
        self.data_text.setAlignment(Qt.AlignCenter)
        self.data_text.setFixedSize(550, 100)

        data_text_layout = QHBoxLayout()
        data_text_layout.addWidget(self.data_text)
        data_text_layout.setAlignment(Qt.AlignCenter)  # Centrar horizontalmente
        self.right_frame.addLayout(data_text_layout)

        self.scan_thread = ScanThread()
        self.scan_thread.devices_discovered.connect(self.update_device_list)

        self.connect_thread = None
        
        # Botón de salir centrado
        self.exit_button = RoundedButton("Exit", "#407BF6")
        self.exit_button.clicked.connect(self.close)
        exit_button_layout = QHBoxLayout()
        exit_button_layout.addWidget(self.exit_button)
        exit_button_layout.setAlignment(Qt.AlignCenter)
        self.exit_button.setFixedSize(550, 50)
        self.right_frame.addLayout(exit_button_layout)

        # Nuevo Frame ---------------------------------------------------
        self.new_frame = QVBoxLayout()
        self.layout.addLayout(self.new_frame)
        alfabeto = [
                            "a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k", "l", "m",
                            "n", "o", "p", "q", "r", "s", "t", "u", "v", "w", "x", "y", "z",
                            "0","1", "2", "3", "4", "5", "6", "7", "8", "9", " ", "!", "@", "#", 
                            "$", "%", "^", "&", "*", "(", ")", "-", "_", "=", "+", "[", "]", 
                            "{", "}", ";", ":"
                            ]
        
        self.info_label = QLabel("⚙️ Gesture Configuration")
        self.info_label.setStyleSheet("color: black; font-size: 25px;")
        self.info_label.setAlignment(Qt.AlignCenter)
        self.new_frame.addWidget(self.info_label)

        self.info_label = QLabel("Gesture 1 ")
        self.info_label.setStyleSheet("color: black; font-size: 15px;")
        self.new_frame.addWidget(self.info_label)

        self.combo_box_1 = QComboBox()
        self.combo_box_1.addItems(alfabeto)
        self.new_frame.addWidget(self.combo_box_1)

        self.info_label = QLabel("Gesture 2 ")
        self.info_label.setStyleSheet("color: black; font-size: 15px;")
        self.new_frame.addWidget(self.info_label)

        self.combo_box_2 = QComboBox()
        self.combo_box_2.addItems(alfabeto)
        self.new_frame.addWidget(self.combo_box_2)

        self.info_label = QLabel("Gesture 3 ")
        self.info_label.setStyleSheet("color: black; font-size: 15px;")
        self.new_frame.addWidget(self.info_label)

        self.combo_box_3 = QComboBox()
        self.combo_box_3.addItems(alfabeto)
        self.new_frame.addWidget(self.combo_box_3)

        self.info_label = QLabel("Gesture 4 ")
        self.info_label.setStyleSheet("color: black; font-size: 15px;")
        self.new_frame.addWidget(self.info_label)

        self.combo_box_4 = QComboBox()
        self.combo_box_4.addItems(alfabeto)
        self.new_frame.addWidget(self.combo_box_4)

        self.info_label = QLabel("Gesture 5 ")
        self.info_label.setStyleSheet("color: black; font-size: 15px;")
        self.new_frame.addWidget(self.info_label)

        self.combo_box_5 = QComboBox()
        self.combo_box_5.addItems(alfabeto)
        self.new_frame.addWidget(self.combo_box_5)

        self.info_label = QLabel("Gesture 6 ")
        self.info_label.setStyleSheet("color: black; font-size: 15px;")
        self.new_frame.addWidget(self.info_label)

        self.combo_box_6 = QComboBox()
        self.combo_box_6.addItems(alfabeto)
        self.new_frame.addWidget(self.combo_box_6)

        # Botón de salir centrado
        self.exit_button = RoundedButton("Save changes", "#407BF6")
        exit_button_layout = QHBoxLayout()
        exit_button_layout.addWidget(self.exit_button)
        exit_button_layout.setAlignment(Qt.AlignCenter)
        self.exit_button.setFixedSize(350, 50)
        self.new_frame.addLayout(exit_button_layout)


    def toggle_mode(self):
        # Cambia el modo entre "mouse" y "teclado"
        self.mouse_mode = not self.mouse_mode
        mode = "Mouse" if self.mouse_mode else "Keyboard"
        self.toggle_mode_button.setText(f"Mode: ({mode})")

        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("Modo Cambiado")
        msg_box.setText(f"Mode: {mode}")
        
        # Establece el icono personalizado
        icon_path = "mouse.png" if self.mouse_mode else "keyboard.png"
        pixmap = QPixmap(icon_path)
        msg_box.setIconPixmap(pixmap)
        
        msg_box.exec()


    def scan_devices(self):
        self.progress.setVisible(True)  # Mostrar barra de progreso
        self.scan_thread.start()

    def update_device_list(self, devices):
        self.progress.setVisible(False)  # Ocultar barra de progreso
        self.devices_listbox.clear()
        self.devices = devices
        for device in devices:
            self.devices_listbox.addItem(f"{device.name} ({device.address})")

    def connect_device(self):
        selected = self.devices_listbox.currentRow()
        if selected == -1:
            msg_box = QMessageBox(self)
            msg_box.setWindowTitle("Error")
            msg_box.setText("You have not selected a device")
            msg_box.setIconPixmap(QPixmap("bluetooth.png"))  # Actualiza la ruta a tu archivo de ícono de error
            msg_box.exec()
            return

        device_address = self.devices[selected].address
        self.progress.setVisible(True)  # Mostrar barra de progreso
        self.connect_thread = ConnectThread(device_address)
        self.connect_thread.connection_status.connect(self.show_connection_status)
        self.connect_thread.notification_received.connect(self.handle_notification)
        self.connect_thread.start()

    def show_connection_status(self, status):
        self.progress.setVisible(False)
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("Conection status")
        msg_box.setText(status)
        if "Connect to" in status:
            msg_box.setIcon(QMessageBox.Information)
            msg_box.setIconPixmap(QPixmap("comprobado.png"))  # Ruta al icono de conexión exitosa
        else:
            msg_box.setIcon(QMessageBox.Warning)
            msg_box.setIconPixmap(QPixmap("cerrar.png"))  # Ruta al icono de error
        msg_box.exec()
        

    def handle_notification(self, data):
        if len(data) > 0:
            int_value = int.from_bytes(data, byteorder='little')

            if 0 <= int_value <= 5:
                if self.mouse_mode:
                    # Acciones en modo "mouse"
                    if int_value == 0:
                        # Acción para el valor 0
                        pyautogui.moveRel(0, -20)  # Mover el cursor hacia arriba
                    elif int_value == 1:
                        # Acción para el valor 1
                        pyautogui.moveRel(0, 20)   # Mover el cursor hacia abajo
                    elif int_value == 2:
                        # Acción para el valor 2
                        pyautogui.moveRel(-20, 0)  # Mover el cursor a la izquierda
                    elif int_value == 3:
                        # Acción para el valor 3
                        pyautogui.moveRel(20, 0)   # Mover el cursor a la derecha
                    elif int_value == 4:
                        # Acción para el valor 4
                        pyautogui.click(button='left')  # Clic izquierdo
                    elif int_value == 5:
                        # Acción para el valor 5
                        pyautogui.click(button='right')  # Clic derecho
                else:
                    # Acciones en modo "teclado"
                    if int_value == 1:
                        # Acción para el valor 0
                        self.data_text.setPlainText('Gesture 1')
                        ctext = self.combo_box_1.currentText()
                        pyautogui.write(ctext)
                    elif int_value == 2:
                        # Acción para el valor 1
                        self.data_text.setPlainText('Gesture 2')
                        ctext_2 = self.combo_box_2.currentText()
                        pyautogui.write(ctext_2)
                    elif int_value == 3:
                        # Acción para el valor 2
                        self.data_text.setPlainText('Gesture 3')
                        ctext_3 = self.combo_box_3.currentText()
                        pyautogui.write(ctext_3)
                    elif int_value == 4:
                        # Acción para el valor 3
                        self.data_text.setPlainText('Gesture 4')
                        ctext_4 = self.combo_box_4.currentText()
                        pyautogui.write(ctext_4)
                    elif int_value == 5:
                        # Acción para el valor 4
                        self.data_text.setPlainText('Gesture 5')
                        ctext_5 = self.combo_box_5.currentText()
                        pyautogui.write(ctext_5)
                    elif int_value == 6:
                        # Acción para el valor 5
                        self.data_text.setPlainText('Gesture 6')
                        ctext_6 = self.combo_box_6.currentText()
                        pyautogui.write(ctext_6)
            else:
                print(f"Valor de datos inesperado recibido: {int_value}")

    def open_manual(self):
        webbrowser.open("http://example.com")  # Actualiza con la URL de tu manual

    def show_credits(self):
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("Créditos")
        msg_box.setIconPixmap(QPixmap("photo.png"))
        msg_box.setText("Developed by: \n Holger Navarro \n Electronic Engineer \n Made in colombia")
        msg_box.exec()
if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_window = BLEInterface()
    main_window.show()
    sys.exit(app.exec())

