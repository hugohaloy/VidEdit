"""
Module de traitement vidéo pour VidEdit
Utilise MoviePy pour les opérations de montage vidéo
"""

from moviepy.editor import VideoFileClip, AudioFileClip, concatenate_videoclips, CompositeAudioClip
import os


class VideoProcessor:
    """Classe pour effectuer des opérations de traitement vidéo"""

    def __init__(self):
        self.current_video = None
        self.video_path = None

    def load_video(self, file_path):
        """Charge une vidéo depuis un fichier"""
        try:
            self.current_video = VideoFileClip(file_path)
            self.video_path = file_path
            return True, f"Vidéo chargée: {os.path.basename(file_path)}"
        except Exception as e:
            return False, f"Erreur lors du chargement: {str(e)}"

    def get_video_info(self):
        """Retourne les informations de la vidéo actuelle"""
        if self.current_video is None:
            return None

        return {
            'duration': self.current_video.duration,
            'fps': self.current_video.fps,
            'size': self.current_video.size,
            'width': self.current_video.w,
            'height': self.current_video.h
        }

    def cut_video(self, start_time, end_time, output_path):
        """
        Découpe une vidéo entre start_time et end_time (en secondes)
        """
        try:
            if self.current_video is None:
                return False, "Aucune vidéo chargée"

            if start_time < 0 or end_time > self.current_video.duration:
                return False, "Temps invalide"

            if start_time >= end_time:
                return False, "Le temps de début doit être inférieur au temps de fin"

            cut_clip = self.current_video.subclip(start_time, end_time)
            cut_clip.write_videofile(output_path, codec='libx264', audio_codec='aac')
            cut_clip.close()

            return True, f"Vidéo découpée sauvegardée: {output_path}"
        except Exception as e:
            return False, f"Erreur lors du découpage: {str(e)}"

    def resize_video(self, scale_x, scale_y, output_path):
        """
        Redimensionne une vidéo avec les facteurs scale_x et scale_y
        scale_x et scale_y sont des pourcentages (100 = taille originale)
        """
        try:
            if self.current_video is None:
                return False, "Aucune vidéo chargée"

            if scale_x <= 0 or scale_y <= 0:
                return False, "Les facteurs de redimensionnement doivent être positifs"

            new_width = int(self.current_video.w * scale_x / 100)
            new_height = int(self.current_video.h * scale_y / 100)

            resized_clip = self.current_video.resize(newsize=(new_width, new_height))
            resized_clip.write_videofile(output_path, codec='libx264', audio_codec='aac')
            resized_clip.close()

            return True, f"Vidéo redimensionnée sauvegardée: {output_path}"
        except Exception as e:
            return False, f"Erreur lors du redimensionnement: {str(e)}"

    def add_audio(self, audio_path, output_path, replace=False):
        """
        Ajoute une piste audio à la vidéo
        Si replace=True, remplace l'audio existant, sinon le mixe
        """
        try:
            if self.current_video is None:
                return False, "Aucune vidéo chargée"

            audio_clip = AudioFileClip(audio_path)

            if replace:
                # Remplace l'audio
                final_clip = self.current_video.set_audio(audio_clip)
            else:
                # Mixe avec l'audio existant
                if self.current_video.audio is not None:
                    mixed_audio = CompositeAudioClip([self.current_video.audio, audio_clip])
                    final_clip = self.current_video.set_audio(mixed_audio)
                else:
                    final_clip = self.current_video.set_audio(audio_clip)

            final_clip.write_videofile(output_path, codec='libx264', audio_codec='aac')
            final_clip.close()
            audio_clip.close()

            return True, f"Audio ajouté, vidéo sauvegardée: {output_path}"
        except Exception as e:
            return False, f"Erreur lors de l'ajout audio: {str(e)}"

    def merge_videos(self, video_paths, output_path):
        """
        Fusionne plusieurs vidéos en une seule
        video_paths: liste des chemins des vidéos à fusionner
        """
        try:
            if not video_paths or len(video_paths) < 2:
                return False, "Au moins 2 vidéos sont nécessaires pour la fusion"

            clips = []
            for path in video_paths:
                try:
                    clip = VideoFileClip(path)
                    clips.append(clip)
                except Exception as e:
                    for c in clips:
                        c.close()
                    return False, f"Erreur lors du chargement de {path}: {str(e)}"

            final_clip = concatenate_videoclips(clips, method="compose")
            final_clip.write_videofile(output_path, codec='libx264', audio_codec='aac')

            # Fermeture des clips
            final_clip.close()
            for clip in clips:
                clip.close()

            return True, f"Vidéos fusionnées sauvegardées: {output_path}"
        except Exception as e:
            return False, f"Erreur lors de la fusion: {str(e)}"

    def close(self):
        """Ferme la vidéo actuelle et libère les ressources"""
        if self.current_video is not None:
            self.current_video.close()
            self.current_video = None
            self.video_path = None
