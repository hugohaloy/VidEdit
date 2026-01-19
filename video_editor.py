"""
Interface graphique principale pour VidEdit
Application de montage vidéo avec PyQt5 - Interface professionnelle
"""

import sys
import os
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                             QHBoxLayout, QPushButton, QLabel, QFileDialog,
                             QSpinBox, QDoubleSpinBox, QSlider, QGroupBox,
                             QMessageBox, QListWidget, QCheckBox, QProgressBar,
                             QSplitter, QScrollArea, QFrame, QListWidgetItem)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QTimer, QSize
from PyQt5.QtGui import QPixmap, QImage, QPalette, QColor
from video_processor import VideoProcessor
import cv2
import numpy as np


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


class VideoClipWidget(QWidget):
    """Widget représentant un clip vidéo dans la timeline"""

    def __init__(self, file_path, duration, parent=None):
        super().__init__(parent)
        self.file_path = file_path
        self.duration = duration
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(5, 5, 5, 5)

        # Nom du fichier
        name_label = QLabel(os.path.basename(self.file_path))
        name_label.setStyleSheet("color: white; font-size: 10px;")
        layout.addWidget(name_label)

        # Durée
        duration_label = QLabel(f"{self.duration:.2f}s")
        duration_label.setStyleSheet("color: #aaa; font-size: 9px;")
        layout.addWidget(duration_label)

        self.setLayout(layout)
        self.setMinimumWidth(100)
        self.setMaximumHeight(60)
        self.setStyleSheet("""
            VideoClipWidget {
                background-color: #3a4a5a;
                border: 1px solid #5a6a7a;
                border-radius: 3px;
            }
            VideoClipWidget:hover {
                background-color: #4a5a6a;
            }
        """)


class TimelineWidget(QWidget):
    """Widget de timeline pour gérer les clips vidéo"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.clips = []
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        # Titre
        title_label = QLabel("Timeline")
        title_label.setStyleSheet("color: white; font-size: 12px; font-weight: bold;")
        layout.addWidget(title_label)

        # Liste des clips
        self.clips_list = QListWidget()
        self.clips_list.setFlow(QListWidget.LeftToRight)
        self.clips_list.setViewMode(QListWidget.IconMode)
        self.clips_list.setResizeMode(QListWidget.Adjust)
        self.clips_list.setSpacing(5)
        self.clips_list.setStyleSheet("""
            QListWidget {
                background-color: #2a3a4a;
                border: 1px solid #4a5a6a;
                border-radius: 3px;
            }
        """)
        layout.addWidget(self.clips_list)

        # Boutons d'action
        button_layout = QHBoxLayout()

        add_btn = QPushButton("➕ Ajouter clip")
        add_btn.clicked.connect(self.add_clip)
        button_layout.addWidget(add_btn)

        remove_btn = QPushButton("➖ Retirer")
        remove_btn.clicked.connect(self.remove_clip)
        button_layout.addWidget(remove_btn)

        clear_btn = QPushButton("🗑️ Tout effacer")
        clear_btn.clicked.connect(self.clear_clips)
        button_layout.addWidget(clear_btn)

        button_layout.addStretch()
        layout.addLayout(button_layout)

        self.setLayout(layout)

    def add_clip(self):
        """Ajoute un clip à la timeline"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Choisir une vidéo", "",
            "Fichiers vidéo (*.mp4 *.avi *.mov *.mkv);;Tous les fichiers (*.*)"
        )
        if file_path:
            # Obtenir la durée de la vidéo
            cap = cv2.VideoCapture(file_path)
            fps = cap.get(cv2.CAP_PROP_FPS)
            frame_count = cap.get(cv2.CAP_PROP_FRAME_COUNT)
            duration = frame_count / fps if fps > 0 else 0
            cap.release()

            self.clips.append(file_path)

            # Créer un item pour la liste
            item = QListWidgetItem()
            clip_widget = VideoClipWidget(file_path, duration)
            item.setSizeHint(clip_widget.sizeHint())
            self.clips_list.addItem(item)
            self.clips_list.setItemWidget(item, clip_widget)

    def remove_clip(self):
        """Retire le clip sélectionné"""
        current_row = self.clips_list.currentRow()
        if current_row >= 0:
            self.clips_list.takeItem(current_row)
            del self.clips[current_row]

    def clear_clips(self):
        """Efface tous les clips"""
        self.clips_list.clear()
        self.clips = []

    def get_clips(self):
        """Retourne la liste des chemins de clips"""
        return self.clips


class VideoPreviewWidget(QWidget):
    """Widget de preview vidéo"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_video_path = None
        self.cap = None
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)
        self.is_playing = False
        self.current_frame = 0
        self.total_frames = 0
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        # Zone d'affichage vidéo
        self.video_label = QLabel()
        self.video_label.setAlignment(Qt.AlignCenter)
        self.video_label.setMinimumSize(640, 360)
        self.video_label.setStyleSheet("""
            QLabel {
                background-color: #1a1a1a;
                border: 2px solid #3a4a5a;
                border-radius: 5px;
            }
        """)
        self.video_label.setText("Aucune vidéo chargée\n\nCliquez sur 'Charger une vidéo' pour commencer")
        self.video_label.setStyleSheet(self.video_label.styleSheet() + "color: #888;")
        layout.addWidget(self.video_label)

        # Contrôles de lecture
        controls_layout = QHBoxLayout()

        self.play_button = QPushButton("▶️ Lecture")
        self.play_button.clicked.connect(self.toggle_play)
        self.play_button.setEnabled(False)
        controls_layout.addWidget(self.play_button)

        self.stop_button = QPushButton("⏹️ Stop")
        self.stop_button.clicked.connect(self.stop_video)
        self.stop_button.setEnabled(False)
        controls_layout.addWidget(self.stop_button)

        # Timeline slider
        self.timeline_slider = QSlider(Qt.Horizontal)
        self.timeline_slider.setEnabled(False)
        self.timeline_slider.valueChanged.connect(self.seek_video)
        controls_layout.addWidget(self.timeline_slider)

        # Time label
        self.time_label = QLabel("00:00 / 00:00")
        self.time_label.setStyleSheet("color: white;")
        controls_layout.addWidget(self.time_label)

        layout.addLayout(controls_layout)

        # Info vidéo
        self.info_label = QLabel("")
        self.info_label.setStyleSheet("color: #aaa; font-size: 10px;")
        layout.addWidget(self.info_label)

        self.setLayout(layout)

    def load_video(self, file_path):
        """Charge une vidéo pour la preview"""
        self.current_video_path = file_path

        if self.cap:
            self.cap.release()

        self.cap = cv2.VideoCapture(file_path)
        self.total_frames = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))
        fps = self.cap.get(cv2.CAP_PROP_FPS)
        width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        duration = self.total_frames / fps if fps > 0 else 0

        self.timeline_slider.setMaximum(self.total_frames - 1)
        self.timeline_slider.setEnabled(True)
        self.play_button.setEnabled(True)
        self.stop_button.setEnabled(True)

        # Afficher les infos
        self.info_label.setText(f"Résolution: {width}x{height} | FPS: {fps:.2f} | Durée: {duration:.2f}s")

        # Afficher la première frame
        self.current_frame = 0
        self.show_frame(0)

    def show_frame(self, frame_number):
        """Affiche une frame spécifique"""
        if not self.cap:
            return

        self.cap.set(cv2.CAP_PROP_POS_FRAMES, frame_number)
        ret, frame = self.cap.read()

        if ret:
            # Convertir BGR vers RGB
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            # Redimensionner pour s'adapter au label
            h, w, ch = frame.shape
            label_w = self.video_label.width()
            label_h = self.video_label.height()

            # Calculer le ratio pour garder les proportions
            ratio = min(label_w / w, label_h / h)
            new_w = int(w * ratio)
            new_h = int(h * ratio)

            frame = cv2.resize(frame, (new_w, new_h))

            # Convertir en QImage
            bytes_per_line = ch * new_w
            q_image = QImage(frame.data, new_w, new_h, bytes_per_line, QImage.Format_RGB888)

            # Afficher
            self.video_label.setPixmap(QPixmap.fromImage(q_image))

            # Mettre à jour le time label
            fps = self.cap.get(cv2.CAP_PROP_FPS)
            current_time = frame_number / fps if fps > 0 else 0
            total_time = self.total_frames / fps if fps > 0 else 0
            self.time_label.setText(f"{self.format_time(current_time)} / {self.format_time(total_time)}")

    def format_time(self, seconds):
        """Formate le temps en MM:SS"""
        mins = int(seconds // 60)
        secs = int(seconds % 60)
        return f"{mins:02d}:{secs:02d}"

    def toggle_play(self):
        """Basculer lecture/pause"""
        if not self.is_playing:
            self.is_playing = True
            self.play_button.setText("⏸️ Pause")
            fps = self.cap.get(cv2.CAP_PROP_FPS)
            self.timer.start(int(1000 / fps) if fps > 0 else 30)
        else:
            self.is_playing = False
            self.play_button.setText("▶️ Lecture")
            self.timer.stop()

    def stop_video(self):
        """Arrête la lecture"""
        self.is_playing = False
        self.play_button.setText("▶️ Lecture")
        self.timer.stop()
        self.current_frame = 0
        self.timeline_slider.setValue(0)
        self.show_frame(0)

    def update_frame(self):
        """Met à jour la frame pendant la lecture"""
        if self.current_frame < self.total_frames - 1:
            self.current_frame += 1
            self.timeline_slider.setValue(self.current_frame)
            self.show_frame(self.current_frame)
        else:
            self.stop_video()

    def seek_video(self, value):
        """Déplace la lecture à une position spécifique"""
        if not self.is_playing:
            self.current_frame = value
            self.show_frame(value)

    def close_video(self):
        """Ferme la vidéo"""
        if self.cap:
            self.cap.release()
            self.cap = None


class OptionsPanel(QWidget):
    """Panneau d'options à droite"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(5, 5, 5, 5)

        # Scroll area pour les options
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        # Widget contenant toutes les options
        options_widget = QWidget()
        options_layout = QVBoxLayout()

        # Panneau: Fichier
        file_group = self.create_file_panel()
        options_layout.addWidget(file_group)

        # Panneau: Découpage
        cut_group = self.create_cut_panel()
        options_layout.addWidget(cut_group)

        # Panneau: Transformation
        transform_group = self.create_transform_panel()
        options_layout.addWidget(transform_group)

        # Panneau: Audio
        audio_group = self.create_audio_panel()
        options_layout.addWidget(audio_group)

        # Panneau: Export
        export_group = self.create_export_panel()
        options_layout.addWidget(export_group)

        options_layout.addStretch()
        options_widget.setLayout(options_layout)
        scroll.setWidget(options_widget)

        main_layout.addWidget(scroll)
        self.setLayout(main_layout)

    def create_file_panel(self):
        """Crée le panneau de gestion des fichiers"""
        group = QGroupBox("📁 Fichier")
        layout = QVBoxLayout()

        self.load_button = QPushButton("Charger une vidéo")
        layout.addWidget(self.load_button)

        self.current_file_label = QLabel("Aucun fichier")
        self.current_file_label.setWordWrap(True)
        self.current_file_label.setStyleSheet("color: #aaa; font-size: 10px;")
        layout.addWidget(self.current_file_label)

        group.setLayout(layout)
        return group

    def create_cut_panel(self):
        """Crée le panneau de découpage"""
        group = QGroupBox("✂️ Découpage")
        layout = QVBoxLayout()

        # Temps de début
        layout.addWidget(QLabel("Temps de début (s):"))
        self.start_time_spin = QDoubleSpinBox()
        self.start_time_spin.setMaximum(99999)
        self.start_time_spin.setValue(0)
        layout.addWidget(self.start_time_spin)

        # Temps de fin
        layout.addWidget(QLabel("Temps de fin (s):"))
        self.end_time_spin = QDoubleSpinBox()
        self.end_time_spin.setMaximum(99999)
        self.end_time_spin.setValue(10)
        layout.addWidget(self.end_time_spin)

        # Bouton
        self.cut_button = QPushButton("Découper")
        layout.addWidget(self.cut_button)

        group.setLayout(layout)
        return group

    def create_transform_panel(self):
        """Crée le panneau de transformation"""
        group = QGroupBox("🔄 Transformation")
        layout = QVBoxLayout()

        # Scale X
        layout.addWidget(QLabel("Scale X (%):"))
        self.scale_x_spin = QSpinBox()
        self.scale_x_spin.setMinimum(1)
        self.scale_x_spin.setMaximum(500)
        self.scale_x_spin.setValue(100)
        layout.addWidget(self.scale_x_spin)

        # Scale Y
        layout.addWidget(QLabel("Scale Y (%):"))
        self.scale_y_spin = QSpinBox()
        self.scale_y_spin.setMinimum(1)
        self.scale_y_spin.setMaximum(500)
        self.scale_y_spin.setValue(100)
        layout.addWidget(self.scale_y_spin)

        # Presets
        preset_layout = QHBoxLayout()
        preset_50 = QPushButton("50%")
        preset_50.clicked.connect(lambda: self.set_scale_preset(50, 50))
        preset_layout.addWidget(preset_50)

        preset_200 = QPushButton("200%")
        preset_200.clicked.connect(lambda: self.set_scale_preset(200, 200))
        preset_layout.addWidget(preset_200)
        layout.addLayout(preset_layout)

        # Bouton
        self.resize_button = QPushButton("Redimensionner")
        layout.addWidget(self.resize_button)

        group.setLayout(layout)
        return group

    def create_audio_panel(self):
        """Crée le panneau audio"""
        group = QGroupBox("🎵 Audio")
        layout = QVBoxLayout()

        self.audio_button = QPushButton("Choisir fichier audio")
        layout.addWidget(self.audio_button)

        self.audio_label = QLabel("Aucun fichier")
        self.audio_label.setWordWrap(True)
        self.audio_label.setStyleSheet("color: #aaa; font-size: 10px;")
        layout.addWidget(self.audio_label)

        self.replace_audio_check = QCheckBox("Remplacer l'audio existant")
        layout.addWidget(self.replace_audio_check)

        self.add_audio_button = QPushButton("Ajouter l'audio")
        layout.addWidget(self.add_audio_button)

        group.setLayout(layout)
        return group

    def create_export_panel(self):
        """Crée le panneau d'export"""
        group = QGroupBox("💾 Export")
        layout = QVBoxLayout()

        self.merge_button = QPushButton("Fusionner les clips de la timeline")
        layout.addWidget(self.merge_button)

        group.setLayout(layout)
        return group

    def set_scale_preset(self, x, y):
        """Définit un preset de scale"""
        self.scale_x_spin.setValue(x)
        self.scale_y_spin.setValue(y)


class VideoEditorApp(QMainWindow):
    """Fenêtre principale de l'application VidEdit"""

    def __init__(self):
        super().__init__()
        self.processor = VideoProcessor()
        self.current_video_path = None
        self.processing_thread = None
        self.audio_path = None
        self.init_ui()

    def init_ui(self):
        """Initialise l'interface utilisateur"""
        self.setWindowTitle("VidEdit - Éditeur Vidéo Professionnel")
        self.setGeometry(100, 100, 1400, 800)

        # Thème sombre
        self.setStyleSheet("""
            QMainWindow {
                background-color: #2b2b2b;
            }
            QWidget {
                background-color: #2b2b2b;
                color: white;
            }
            QGroupBox {
                border: 1px solid #3a4a5a;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
                font-weight: bold;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
            QPushButton {
                background-color: #3a4a5a;
                border: 1px solid #4a5a6a;
                border-radius: 3px;
                padding: 5px;
                color: white;
            }
            QPushButton:hover {
                background-color: #4a5a6a;
            }
            QPushButton:pressed {
                background-color: #2a3a4a;
            }
            QSpinBox, QDoubleSpinBox {
                background-color: #3a4a5a;
                border: 1px solid #4a5a6a;
                border-radius: 3px;
                padding: 3px;
                color: white;
            }
            QSlider::groove:horizontal {
                height: 8px;
                background: #3a4a5a;
                border-radius: 4px;
            }
            QSlider::handle:horizontal {
                background: #5a7a9a;
                width: 16px;
                margin: -4px 0;
                border-radius: 8px;
            }
            QProgressBar {
                background-color: #3a4a5a;
                border: 1px solid #4a5a6a;
                border-radius: 3px;
                text-align: center;
                color: white;
            }
            QProgressBar::chunk {
                background-color: #5a7a9a;
            }
        """)

        # Widget central
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Layout principal avec splitters
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(5, 5, 5, 5)

        # Barre de progression (cachée par défaut)
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        main_layout.addWidget(self.progress_bar)

        # Splitter horizontal: Preview + Options
        h_splitter = QSplitter(Qt.Horizontal)

        # Zone centrale: Preview + Timeline
        center_widget = QWidget()
        center_layout = QVBoxLayout()
        center_layout.setContentsMargins(0, 0, 0, 0)

        # Preview
        self.preview_widget = VideoPreviewWidget()
        center_layout.addWidget(self.preview_widget, stretch=3)

        # Timeline
        self.timeline_widget = TimelineWidget()
        center_layout.addWidget(self.timeline_widget, stretch=1)

        center_widget.setLayout(center_layout)
        h_splitter.addWidget(center_widget)

        # Panneau d'options à droite
        self.options_panel = OptionsPanel()
        self.options_panel.setMaximumWidth(300)
        h_splitter.addWidget(self.options_panel)

        # Proportions du splitter
        h_splitter.setStretchFactor(0, 3)
        h_splitter.setStretchFactor(1, 1)

        main_layout.addWidget(h_splitter)
        central_widget.setLayout(main_layout)

        # Connecter les signaux
        self.connect_signals()

        self.show()

    def connect_signals(self):
        """Connecte tous les signaux aux slots"""
        self.options_panel.load_button.clicked.connect(self.load_video)
        self.options_panel.cut_button.clicked.connect(self.cut_video)
        self.options_panel.resize_button.clicked.connect(self.resize_video)
        self.options_panel.audio_button.clicked.connect(self.select_audio)
        self.options_panel.add_audio_button.clicked.connect(self.add_audio)
        self.options_panel.merge_button.clicked.connect(self.merge_videos)

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
                self.options_panel.current_file_label.setText(os.path.basename(file_path))

                # Charger dans la preview
                self.preview_widget.load_video(file_path)

                # Mettre à jour les limites de temps
                info = self.processor.get_video_info()
                if info:
                    self.options_panel.end_time_spin.setValue(info['duration'])

                QMessageBox.information(self, "Succès", message)
            else:
                QMessageBox.critical(self, "Erreur", message)

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

        start_time = self.options_panel.start_time_spin.value()
        end_time = self.options_panel.end_time_spin.value()

        self.start_processing(self.processor.cut_video, start_time, end_time, output_path)

    def resize_video(self):
        """Redimensionne la vidéo"""
        if not self.current_video_path:
            QMessageBox.warning(self, "Attention", "Veuillez d'abord charger une vidéo")
            return

        output_path = self.get_output_path("resized")
        if not output_path:
            return

        scale_x = self.options_panel.scale_x_spin.value()
        scale_y = self.options_panel.scale_y_spin.value()

        self.start_processing(self.processor.resize_video, scale_x, scale_y, output_path)

    def select_audio(self):
        """Sélectionne un fichier audio"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Choisir un fichier audio", "",
            "Fichiers audio (*.mp3 *.wav *.aac *.m4a);;Tous les fichiers (*.*)"
        )

        if file_path:
            self.audio_path = file_path
            self.options_panel.audio_label.setText(os.path.basename(file_path))

    def add_audio(self):
        """Ajoute une piste audio à la vidéo"""
        if not self.current_video_path:
            QMessageBox.warning(self, "Attention", "Veuillez d'abord charger une vidéo")
            return

        if not self.audio_path:
            QMessageBox.warning(self, "Attention", "Veuillez d'abord sélectionner un fichier audio")
            return

        output_path = self.get_output_path("audio")
        if not output_path:
            return

        replace = self.options_panel.replace_audio_check.isChecked()

        self.start_processing(self.processor.add_audio, self.audio_path, output_path, replace)

    def merge_videos(self):
        """Fusionne les vidéos de la timeline"""
        clips = self.timeline_widget.get_clips()

        if len(clips) < 2:
            QMessageBox.warning(self, "Attention",
                              "Ajoutez au moins 2 vidéos à la timeline")
            return

        output_path, _ = QFileDialog.getSaveFileName(
            self, "Enregistrer la vidéo fusionnée",
            "merged_video.mp4",
            "Fichiers vidéo (*.mp4 *.avi *.mov *.mkv)"
        )

        if not output_path:
            return

        self.start_processing(self.processor.merge_videos, clips, output_path)

    def closeEvent(self, event):
        """Appelé lors de la fermeture de l'application"""
        self.processor.close()
        self.preview_widget.close_video()
        event.accept()


def main():
    app = QApplication(sys.argv)
    editor = VideoEditorApp()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
