import json
import subprocess

import ffmpeg
from PyQt5.QtCore import QThread, pyqtSignal


class AudioMergeThread(QThread):
    finished = pyqtSignal(str, str)  # Signal to emit when the audio merge is finished

    def __init__(self, input_files, output_file, output_format, output_codec):
        super().__init__()
        self.input_files = input_files
        self.output_file = output_file
        self.output_format = output_format
        self.output_codec = output_codec

    @staticmethod
    def get_total_frames(files):
        total_frames = 0
        for file in files:
            ffprobe_command = [
                'ffprobe',
                '-v', 'error',
                '-select_streams', 'a:0', '-count_packets',
                '-show_entries', 'stream=nb_read_packets',
                '-of', 'csv=p=0', '-of', 'json',
                file
            ]

            try:
                ffprobe_output = subprocess.check_output(ffprobe_command, universal_newlines=True)
                data = json.loads(ffprobe_output)
                total_frames += int(data['streams'][0]['nb_read_packets'])
            except subprocess.CalledProcessError as e:
                print(f"Error running ffprobe: {e}")
                return None
        return total_frames

    def run(self):
        try:
            # Create input streams for selected files
            input_streams = [ffmpeg.input(str(file_path)) for file_path in self.input_files]

            # Merge the audio files using FFmpeg
            output_file_path = f"{self.output_file}.{self.output_format}"
            out, err = ffmpeg.concat(*input_streams, v=0, a=1).output(
                output_file_path, codec=self.output_codec, ac=2, q="2"
            ).overwrite_output().run(capture_stdout=True, capture_stderr=True)
            # Emit the result when finished
            self.finished.emit(out.decode('utf-8'), err.decode('utf-8'))

        except Exception as e:
            self.finished.emit(str(e), '')
