import os
import ffmpeg
from PyQt5.QtCore import QThread, pyqtSignal


class AudioMergeThread(QThread):
    finished = pyqtSignal(str, str, str)

    def __init__(self, input_files, output_file, output_format, output_codec, script_dir, timestamp):
        super().__init__()
        self.input_files = input_files
        self.output_file = output_file
        self.output_format = output_format
        self.output_codec = output_codec
        self.script_dir = script_dir
        self.timestamp = timestamp

    def run(self):
        try:
            # Define output directory relative to script location
            output_dir = os.path.join(self.script_dir, "audio")
            os.makedirs(output_dir, exist_ok=True)

            if self.timestamp:
                output_filename = f"{self.output_file}_{self.timestamp}.{self.output_format}"
            else:
                output_filename = f"{self.output_file}.{self.output_format}"
            output_file_path = os.path.join(output_dir, output_filename)

            # Create input streams for selected files
            input_streams = [ffmpeg.input(str(file_path)) for file_path in self.input_files]

            # Merge the audio files using FFmpeg
            out, err = ffmpeg.concat(*input_streams, v=0, a=1).output(
                output_file_path, codec=self.output_codec, ac=2, q="2"
            ).overwrite_output().run(capture_stdout=True, capture_stderr=True)

            # Emit the result when finished
            self.finished.emit(out.decode('utf-8'), err.decode('utf-8'), output_file_path)

        except Exception as e:
            self.finished.emit(str(e), '', '')
