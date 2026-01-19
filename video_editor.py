"""
Interface graphique principale pour VidEdit
Application de montage vidéo avec PyQt5
"""

import sys
import os
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                             QHBoxLayout, QPushButton, QLabel, QFileDialog,
                             QTabWidget, QLineEdit, QSpinBox, QDoubleSpinBox,
                             QMessageBox, QListWidget, QCheckBox, QProgressBar)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from video_processor import VideoProcessor


class ProcessingThread(QThread):
    """Thread pour traiter les vidéos sans bloquer l'interface"""
    finished = pyqtSignal(bool, str)

    def __init__(self, func, *args, **kwargs):
        super().__init__()
        self.func = func
        self.args = args
        self.kwargs = kwargs

    def run(self):
        success, message = self.func(*self.args, **self.kwargs)
        self.finished.emit(success, message)


class VideoEditorApp(QMainWindow):
    """Fenêtre principale de l'application VidEdit"""

    def __init__(self):
        super().__init__()
        self.processor = VideoProcessor()
        self.current_video_path = None
        self.processing_thread = None
        self.init_ui()

    def init_ui(self):
        """Initialise l'interface utilisateur"""
        self.setWindowTitle("VidEdit - Éditeur Vidéo")
        self.setGeometry(100, 100, 800, 600)

        # Widget central
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Layout principal
        main_layout = QVBoxLayout()
        central_widget.setLayout(main_layout)

        # Zone de chargement de vidéo
        load_layout = QHBoxLayout()
        self.load_button = QPushButton("📁 Charger une vidéo")
        self.load_button.clicked.connect(self.load_video)
        self.video_label = QLabel("Aucune vidéo chargée")
        load_layout.addWidget(self.load_button)
        load_layout.addWidget(self.video_label)
        load_layout.addStretch()
        main_layout.addLayout(load_layout)

        # Informations vidéo
        self.info_label = QLabel("")
        main_layout.addWidget(self.info_label)

        # Barre de progression
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        main_layout.addWidget(self.progress_bar)

        # Onglets pour les différentes opérations
        self.tabs = QTabWidget()
        self.tabs.addTab(self.create_cut_tab(), "✂️ Découper")
        self.tabs.addTab(self.create_resize_tab(), "🔄 Redimensionner")
        self.tabs.addTab(self.create_audio_tab(), "🎵 Ajouter Audio")
        self.tabs.addTab(self.create_merge_tab(), "🔗 Fusionner")
        main_layout.addWidget(self.tabs)

        self.show()

    def create_cut_tab(self):
        """Crée l'onglet de découpage vidéo"""
        tab = QWidget()
        layout = QVBoxLayout()

        # Instructions
        layout.addWidget(QLabel("Découpez une portion de votre vidéo"))

        # Temps de début
        start_layout = QHBoxLayout()
        start_layout.addWidget(QLabel("Temps de début (secondes):"))
        self.start_time_spin = QDoubleSpinBox()
        self.start_time_spin.setMaximum(99999)
        self.start_time_spin.setValue(0)
        start_layout.addWidget(self.start_time_spin)
        start_layout.addStretch()
        layout.addLayout(start_layout)

        # Temps de fin
        end_layout = QHBoxLayout()
        end_layout.addWidget(QLabel("Temps de fin (secondes):"))
        self.end_time_spin = QDoubleSpinBox()
        self.end_time_spin.setMaximum(99999)
        self.end_time_spin.setValue(10)
        end_layout.addWidget(self.end_time_spin)
        end_layout.addStretch()
        layout.addLayout(end_layout)

        # Bouton de découpage
        cut_button = QPushButton("✂️ Découper la vidéo")
        cut_button.clicked.connect(self.cut_video)
        layout.addWidget(cut_button)

        layout.addStretch()
        tab.setLayout(layout)
        return tab

    def create_resize_tab(self):
        """Crée l'onglet de redimensionnement"""
        tab = QWidget()
        layout = QVBoxLayout()

        # Instructions
        layout.addWidget(QLabel("Redimensionnez votre vidéo"))

        # Scale X
        scale_x_layout = QHBoxLayout()
        scale_x_layout.addWidget(QLabel("Scale X (%):"))
        self.scale_x_spin = QSpinBox()
        self.scale_x_spin.setMinimum(1)
        self.scale_x_spin.setMaximum(500)
        self.scale_x_spin.setValue(100)
        scale_x_layout.addWidget(self.scale_x_spin)
        scale_x_layout.addStretch()
        layout.addLayout(scale_x_layout)

        # Scale Y
        scale_y_layout = QHBoxLayout()
        scale_y_layout.addWidget(QLabel("Scale Y (%):"))
        self.scale_y_spin = QSpinBox()
        self.scale_y_spin.setMinimum(1)
        self.scale_y_spin.setMaximum(500)
        self.scale_y_spin.setValue(100)
        scale_y_layout.addWidget(self.scale_y_spin)
        scale_y_layout.addStretch()
        layout.addLayout(scale_y_layout)

        # Presets communs
        layout.addWidget(QLabel("Presets:"))
        preset_layout = QHBoxLayout()

        preset_50 = QPushButton("50%")
        preset_50.clicked.connect(lambda: self.set_scale_preset(50, 50))
        preset_layout.addWidget(preset_50)

        preset_200 = QPushButton("200%")
        preset_200.clicked.connect(lambda: self.set_scale_preset(200, 200))
        preset_layout.addWidget(preset_200)

        preset_layout.addStretch()
        layout.addLayout(preset_layout)

        # Bouton de redimensionnement
        resize_button = QPushButton("🔄 Redimensionner la vidéo")
        resize_button.clicked.connect(self.resize_video)
        layout.addWidget(resize_button)

        layout.addStretch()
        tab.setLayout(layout)
        return tab

    def create_audio_tab(self):
        """Crée l'onglet d'ajout audio"""
        tab = QWidget()
        layout = QVBoxLayout()

        # Instructions
        layout.addWidget(QLabel("Ajoutez une piste audio à votre vidéo"))

        # Sélection fichier audio
        audio_layout = QHBoxLayout()
        self.audio_button = QPushButton("📁 Choisir un fichier audio")
        self.audio_button.clicked.connect(self.select_audio)
        self.audio_label = QLabel("Aucun fichier audio sélectionné")
        audio_layout.addWidget(self.audio_button)
        audio_layout.addWidget(self.audio_label)
        audio_layout.addStretch()
        layout.addLayout(audio_layout)

        # Option remplacer/mixer
        self.replace_audio_check = QCheckBox("Remplacer l'audio existant (sinon mixer)")
        layout.addWidget(self.replace_audio_check)

        # Bouton d'ajout audio
        add_audio_button = QPushButton("🎵 Ajouter l'audio")
        add_audio_button.clicked.connect(self.add_audio)
        layout.addWidget(add_audio_button)

        layout.addStretch()
        tab.setLayout(layout)
        return tab

    def create_merge_tab(self):
        """Crée l'onglet de fusion de vidéos"""
        tab = QWidget()
        layout = QVBoxLayout()

        # Instructions
        layout.addWidget(QLabel("Fusionnez plusieurs vidéos en une seule"))

        # Liste des vidéos
        layout.addWidget(QLabel("Vidéos à fusionner (dans l'ordre):"))
        self.merge_list = QListWidget()
        layout.addWidget(self.merge_list)

        # Boutons de gestion de liste
        button_layout = QHBoxLayout()

        add_video_button = QPushButton("➕ Ajouter vidéo")
        add_video_button.clicked.connect(self.add_video_to_merge)
        button_layout.addWidget(add_video_button)

        remove_video_button = QPushButton("➖ Retirer")
        remove_video_button.clicked.connect(self.remove_video_from_merge)
        button_layout.addWidget(remove_video_button)

        clear_button = QPushButton("🗑️ Tout effacer")
        clear_button.clicked.connect(self.clear_merge_list)
        button_layout.addWidget(clear_button)

        button_layout.addStretch()
        layout.addLayout(button_layout)

        # Bouton de fusion
        merge_button = QPushButton("🔗 Fusionner les vidéos")
        merge_button.clicked.connect(self.merge_videos)
        layout.addWidget(merge_button)

        tab.setLayout(layout)
        return tab

    def load_video(self):
        """Charge une vidéo"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Choisir une vidéo", "",
            "Fichiers vidéo (*.mp4 *.avi *.mov *.mkv);;Tous les fichiers (*.*)"
        )

        if file_path:
            success, message = self.processor.load_video(file_path)
            if success:
                self.current_video_path = file_path
                self.video_label.setText(os.path.basename(file_path))
                self.update_video_info()
                QMessageBox.information(self, "Succès", message)
            else:
                QMessageBox.critical(self, "Erreur", message)

    def update_video_info(self):
        """Met à jour l'affichage des informations vidéo"""
        info = self.processor.get_video_info()
        if info:
            self.info_label.setText(
                f"Durée: {info['duration']:.2f}s | "
                f"FPS: {info['fps']:.2f} | "
                f"Résolution: {info['width']}x{info['height']}"
            )
            self.end_time_spin.setValue(info['duration'])

    def get_output_path(self, suffix):
        """Génère un chemin de sortie pour la vidéo traitée"""
        if not self.current_video_path:
            return None

        directory = os.path.dirname(self.current_video_path)
        base_name = os.path.splitext(os.path.basename(self.current_video_path))[0]
        extension = os.path.splitext(self.current_video_path)[1]

        output_path, _ = QFileDialog.getSaveFileName(
            self, "Enregistrer la vidéo",
            os.path.join(directory, f"{base_name}_{suffix}{extension}"),
            "Fichiers vidéo (*.mp4 *.avi *.mov *.mkv)"
        )

        return output_path

    def start_processing(self, func, *args, **kwargs):
        """Démarre le traitement dans un thread séparé"""
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)
        self.setEnabled(False)

        self.processing_thread = ProcessingThread(func, *args, **kwargs)
        self.processing_thread.finished.connect(self.on_processing_finished)
        self.processing_thread.start()

    def on_processing_finished(self, success, message):
        """Appelé quand le traitement est terminé"""
        self.progress_bar.setVisible(False)
        self.setEnabled(True)

        if success:
            QMessageBox.information(self, "Succès", message)
        else:
            QMessageBox.critical(self, "Erreur", message)

    def cut_video(self):
        """Découpe la vidéo"""
        if not self.current_video_path:
            QMessageBox.warning(self, "Attention", "Veuillez d'abord charger une vidéo")
            return

        output_path = self.get_output_path("cut")
        if not output_path:
            return

        start_time = self.start_time_spin.value()
        end_time = self.end_time_spin.value()

        self.start_processing(self.processor.cut_video, start_time, end_time, output_path)

    def resize_video(self):
        """Redimensionne la vidéo"""
        if not self.current_video_path:
            QMessageBox.warning(self, "Attention", "Veuillez d'abord charger une vidéo")
            return

        output_path = self.get_output_path("resized")
        if not output_path:
            return

        scale_x = self.scale_x_spin.value()
        scale_y = self.scale_y_spin.value()

        self.start_processing(self.processor.resize_video, scale_x, scale_y, output_path)

    def set_scale_preset(self, x, y):
        """Définit les valeurs de scale X et Y"""
        self.scale_x_spin.setValue(x)
        self.scale_y_spin.setValue(y)

    def select_audio(self):
        """Sélectionne un fichier audio"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Choisir un fichier audio", "",
            "Fichiers audio (*.mp3 *.wav *.aac *.m4a);;Tous les fichiers (*.*)"
        )

        if file_path:
            self.audio_path = file_path
            self.audio_label.setText(os.path.basename(file_path))

    def add_audio(self):
        """Ajoute une piste audio à la vidéo"""
        if not self.current_video_path:
            QMessageBox.warning(self, "Attention", "Veuillez d'abord charger une vidéo")
            return

        if not hasattr(self, 'audio_path') or not self.audio_path:
            QMessageBox.warning(self, "Attention", "Veuillez d'abord sélectionner un fichier audio")
            return

        output_path = self.get_output_path("audio")
        if not output_path:
            return

        replace = self.replace_audio_check.isChecked()

        self.start_processing(self.processor.add_audio, self.audio_path, output_path, replace)

    def add_video_to_merge(self):
        """Ajoute une vidéo à la liste de fusion"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Choisir une vidéo", "",
            "Fichiers vidéo (*.mp4 *.avi *.mov *.mkv);;Tous les fichiers (*.*)"
        )

        if file_path:
            self.merge_list.addItem(file_path)

    def remove_video_from_merge(self):
        """Retire une vidéo de la liste de fusion"""
        current_row = self.merge_list.currentRow()
        if current_row >= 0:
            self.merge_list.takeItem(current_row)

    def clear_merge_list(self):
        """Efface toute la liste de fusion"""
        self.merge_list.clear()

    def merge_videos(self):
        """Fusionne les vidéos de la liste"""
        if self.merge_list.count() < 2:
            QMessageBox.warning(self, "Attention",
                              "Ajoutez au moins 2 vidéos à fusionner")
            return

        video_paths = [self.merge_list.item(i).text()
                      for i in range(self.merge_list.count())]

        output_path, _ = QFileDialog.getSaveFileName(
            self, "Enregistrer la vidéo fusionnée",
            "merged_video.mp4",
            "Fichiers vidéo (*.mp4 *.avi *.mov *.mkv)"
        )

        if not output_path:
            return

        self.start_processing(self.processor.merge_videos, video_paths, output_path)

    def closeEvent(self, event):
        """Appelé lors de la fermeture de l'application"""
        self.processor.close()
        event.accept()


def main():
    app = QApplication(sys.argv)
    editor = VideoEditorApp()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
