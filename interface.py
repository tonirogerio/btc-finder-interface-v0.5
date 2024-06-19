from PyQt6.QtGui import QFont, QIcon, QPixmap
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QRadioButton, QLabel, QInputDialog, \
    QMessageBox, QTextEdit, QButtonGroup, QHBoxLayout
from PyQt6.QtCore import QProcess, Qt, QSize
import sys


class BitcoinFinderUI(QWidget):
    def __init__(self):
        super().__init__()

        self.status = 0
        self.initUI()
        self.process = None
        self.wallet = None

    def initUI(self):
        layout = QVBoxLayout()

        self.title_label = QLabel("Bitcoin Finder - v0.5")
        self.title_label.setFont(QFont("Arial Black", 14))
        self.setMinimumSize(550, 800)
        layout.addWidget(self.title_label, alignment=Qt.AlignmentFlag.AlignCenter)

        self.choose_wallet_button = QPushButton('Escolha uma Carteira Puzzle (1 - 160)')
        self.choose_wallet_button.setMinimumWidth(250)
        self.choose_wallet_button.setMinimumHeight(30)
        self.choose_wallet_button.setFont(QFont("Georgia", 10))
        self.choose_wallet_button.setIcon(QIcon('icon/wallet.ico'))
        self.choose_wallet_button.setIconSize(QSize(30, 30))
        self.choose_wallet_button.clicked.connect(self.choose_wallet)

        layout.addWidget(self.choose_wallet_button, alignment=Qt.AlignmentFlag.AlignCenter)

        self.option_label = QLabel('Escolha uma opção:')
        self.option_label.setFont(QFont("Arial Black", 12))
        layout.addWidget(self.option_label, alignment=Qt.AlignmentFlag.AlignCenter)

        self.radio_layout = QHBoxLayout()
        self.option_group = QButtonGroup(self)
        self.option1_radio = QRadioButton("1 - Comecar do inicio")
        self.option1_radio.setFont(QFont("Georgia", 10))
        self.option_group.addButton(self.option1_radio, 1)

        self.option2_radio = QRadioButton("2 - Escolher uma porcentagem")
        self.option2_radio.setFont(QFont("Georgia", 10))
        self.option_group.addButton(self.option2_radio, 2)

        self.option3_radio = QRadioButton("3 - Escolher minimo")
        self.option3_radio.setFont(QFont("Georgia", 10))
        self.option_group.addButton(self.option3_radio, 3)

        self.radio_layout.addWidget(self.option1_radio)
        self.radio_layout.addWidget(self.option2_radio)
        self.radio_layout.addWidget(self.option3_radio)

        layout.addLayout(self.radio_layout)

        self.start_stop_layout = QHBoxLayout()

        self.start_button = QPushButton('Start')
        self.start_button.setMaximumWidth(100)
        self.start_button.setMinimumHeight(30)
        self.start_button.setFont(QFont("Georgia", 10))
        self.start_button.setIcon(QIcon('icon/play_start.ico'))
        self.start_button.setIconSize(QSize(24, 24))
        self.start_button.clicked.connect(self.start_process)

        self.stop_button = QPushButton('Stop')
        self.stop_button.setMaximumWidth(100)
        self.stop_button.setMinimumHeight(30)
        self.stop_button.setFont(QFont("Georgia", 10))
        self.stop_button.setIcon(QIcon('icon/cube_stop.ico'))
        self.stop_button.setIconSize(QSize(24, 24))
        self.stop_button.clicked.connect(self.stop_process)

        self.clear_button = QPushButton('Clear')
        self.clear_button.setMaximumWidth(100)
        self.clear_button.setMinimumHeight(30)
        self.clear_button.setFont(QFont("Georgia", 10))
        self.clear_button.setIcon(QIcon('icon/brush.ico'))
        self.clear_button.setIconSize(QSize(24, 24))
        self.clear_button.clicked.connect(self.clear_output)

        self.start_stop_layout.addWidget(self.start_button)
        self.start_stop_layout.addWidget(self.stop_button)
        self.start_stop_layout.addWidget(self.clear_button)
        layout.addLayout(self.start_stop_layout)

        self.output_area = QTextEdit()
        self.output_area.setReadOnly(True)
        layout.addWidget(self.output_area)

        self.layout_status = QHBoxLayout()

        self.worker_icon = QLabel('')
        self.worker_icon.setPixmap(QIcon('icon/worker.ico').pixmap(QSize(30, 30)))

        self.status_label = QLabel('Worker Não Iniciado')
        self.status_label.setFont(QFont("Georgia", 12))
        self.status_label.setMinimumWidth(50)
        self.status_label.setMinimumHeight(30)

        self.status_icon = QLabel('')
        self.status_icon.setPixmap(QIcon('icon/blank_blue.ico').pixmap(QSize(30, 30)))

        self.layout_status.addWidget(self.worker_icon, alignment=Qt.AlignmentFlag.AlignCenter)
        self.layout_status.addWidget(self.status_label, alignment=Qt.AlignmentFlag.AlignCenter)
        self.layout_status.addWidget(self.status_icon, alignment=Qt.AlignmentFlag.AlignCenter)

        layout.addLayout(self.layout_status)

        self.setLayout(layout)
        self.setWindowTitle('Bitcoin Finder')
        self.setWindowIcon(QIcon('icon/bitcoin.ico'))

    def choose_wallet(self):
        wallet, ok = QInputDialog.getInt(self, 'Escolha uma carteira', 'Escolha uma carteira puzzle (1 - 160):', min=1, max=160)
        if ok:
            self.wallet = wallet
            QMessageBox.information(self, 'Carteira Escolhida', f'Carteira escolhida: {wallet}')

    def start_process(self):
        selected_id = self.option_group.checkedId()
        if selected_id not in [1, 2, 3]:
            QMessageBox.warning(self, 'Erro', 'Você precisa escolher uma opção válida (1, 2 ou 3).')
            return

        if self.wallet is None:
            QMessageBox.warning(self, 'Erro', 'Você precisa escolher uma carteira.')
            return

        self.process = QProcess(self)
        self.process.readyReadStandardOutput.connect(self.handle_stdout)
        self.process.readyReadStandardError.connect(self.handle_stderr)

        command = ["node", "main.js"]
        self.process.start(command[0], command[1:])

        if selected_id == 2:
            percentage_str, ok = QInputDialog.getText(self, 'Escolha a porcentagem', 'Escolha um número entre 0 e 1:')

            if ok:
                percentage_str = percentage_str.replace(',', '.')

                try:
                    percentage = float(percentage_str)

                    if 0 <= percentage <= 1:
                        formatted_percentage = f"{percentage:.16f}"
                        self.process.write(f'{self.wallet}\n2\n{formatted_percentage}\n'.encode())
                    else:
                        QMessageBox.warning(self, 'Erro', 'Você precisa escolher um número entre 0 e 1.')

                except ValueError:
                    QMessageBox.warning(self, 'Erro',
                                        'Entrada inválida. Certifique-se de usar um formato numérico correto.')

        elif selected_id == 3:
            min_value, ok = QInputDialog.getText(self, 'Escolha o mínimo', 'Entre o mínimo:')
            if ok:
                min_value = min_value.strip()
                # Remover '0x' do início se estiver presente e converter para número
                if min_value.startswith('0x'):
                    min_value = min_value[2:]
                try:
                    min_value = int(min_value, 16)
                    self.process.write(f'{self.wallet}\n3\n{min_value}\n'.encode())
                except ValueError:
                    QMessageBox.warning(self, 'Erro', 'Você precisa inserir um valor hexadecimal válido.')
        else:
            self.process.write(f'{self.wallet}\n1\n'.encode())

        self.status = 1
        self.get_status()

    def get_status(self):
        if self.status == 1:
            self.status_icon.setPixmap(QIcon('icon/blank_green.ico').pixmap(QSize(30, 30)))
            self.status_label.setText('Executando...')
        else:
            self.status_icon.setPixmap(QIcon('icon/blank_red.ico').pixmap(QSize(30, 30)))
            self.status_label.setText('Worker Parado')

    def stop_process(self):
        if self.process and self.process.state() == QProcess.ProcessState.Running:
            self.status = 0
            self.get_status()
            self.process.kill()
            self.output_area.append("Processo parado.")

    def handle_stdout(self):
        data = self.process.readAllStandardOutput().data().decode()
        lines = data.splitlines()
        for line in lines:
            if not line.strip().isdigit():
                self.output_area.append(line)
                if "Ultima chave tentada:" in line:
                    self.output_area.append("")

    def handle_stderr(self):
        data = self.process.readAllStandardError().data().decode()
        self.output_area.append(data)

    def clear_output(self):
        self.output_area.clear()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = BitcoinFinderUI()
    ex.show()
    sys.exit(app.exec())
