import logging
import os
import os.path
import sys

from PyQt5.QtGui import QStandardItemModel, QStandardItem, QFontDatabase
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QLabel, QListView, QPushButton, QTextEdit, \
    QComboBox, QAbstractItemView, QHBoxLayout, QFileDialog, QLineEdit
from qt_material import apply_stylesheet

from thread_merge import AudioMergeThread

# Set logging level to info
logging.getLogger().setLevel(logging.INFO)

# Define a dictionary to map formats to FFmpeg codecs and extensions
format_mapping = {
    "mp3": {"codec": "libmp3lame", "extension": "mp3"},
    "aac": {"codec": "aac", "extension": "aac"},
    "m4a": {"codec": "aac", "extension": "m4a"},
    "wav": {"codec": "pcm_s16le", "extension": "wav"},
    "flac": {"codec": "flac", "extension": "flac"},
    "ogg": {"codec": "libvorbis", "extension": "ogg"},
    "ac3": {"codec": "ac3", "extension": "ac3"},
    "wma": {"codec": "wmav2", "extension": "wma"},
    "aiff": {"codec": "pcm_s16le", "extension": "aiff"},
    "mka": {"codec": "aac", "extension": "mka"},
    "mp2": {"codec": "mp2", "extension": "mp2"},
}

extensions = ["mp3", "aac", "m4a", "wav", "flac", "ogg", "ac3", "wma", "aiff",
              "mka", "mp2"]


# Check and remove extension
def remove_extension(input_string):
    for ext in extensions:
        if input_string.endswith("." + ext):
            return input_string[:-len(ext) - 1]  # Remove the extension and the dot
    return input_string  # No valid extension found


class AudioFileDropWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.label = QLabel('Drag & Drop audio files here or add them manually:')
        self.list_view = QListView()
        self.remove_button = QPushButton("Remove Selected")
        self.remove_all_button = QPushButton("Remove All")
        self.add_files_button = QPushButton("Add Files")
        self.label_format = QLabel('Select audio output format:')
        self.format_combo_box = QComboBox()
        self.output_filename_input = QLineEdit(self)
        self.merge_button = QPushButton("Merge Audio")
        self.debug_label = QLabel("FFmpeg debug Information:")
        self.ffmpeg_output = QTextEdit(self)
        self.model = QStandardItemModel()
        self.audio_files = {}  # Dictionary to store title-filepath pairs
        self.output_file = "output"
        self.merge_thread = None
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        layout.addWidget(self.label)

        # Create a QHBoxLayout for the QListView and Remove button
        list_view_layout = QHBoxLayout()

        self.list_view.setFixedHeight(200)
        self.list_view.setSpacing(0)
        self.list_view.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.list_view.setSelectionMode(QAbstractItemView.MultiSelection)
        list_view_layout.addWidget(self.list_view)

        # Create a QVBoxLayout for the "Remove Selected" and "Add Files" buttons
        buttons_layout = QVBoxLayout()

        # Add a "Remove" button
        self.remove_button.clicked.connect(self.remove_selected_items)
        buttons_layout.addWidget(self.remove_button)

        # Add a "Remove All" button to open a file dialog
        self.remove_all_button.clicked.connect(self.remove_all_items)
        buttons_layout.addWidget(self.remove_all_button)

        # Add a "Add Files" button to open a file dialog
        self.add_files_button.clicked.connect(self.add_files_dialog)
        buttons_layout.addWidget(self.add_files_button)

        list_view_layout.addLayout(buttons_layout)
        buttons_layout.setSpacing(0)

        layout.addLayout(list_view_layout)  # Add the QHBoxLayout to the main layout

        layout.addWidget(self.label_format)

        # Create a dropdown (combo box) for selecting audio file format
        self.format_combo_box.setView(QListView())
        self.format_combo_box.setFixedWidth(100)
        self.format_combo_box.addItems(extensions)
        layout.addWidget(self.format_combo_box)

        # Create a QLineEdit widget for entering the output filename
        self.output_filename_input.setMaxLength(80)
        # self.output_filename_input.setStyleSheet("color: white;")
        self.output_filename_input.setPlaceholderText("Enter output filename (default name: output.*)")
        layout.addWidget(self.output_filename_input)
        self.format_combo_box.currentTextChanged.connect(self.update_line_edit)
        self.update_line_edit()

        # Add a "Merge" button
        self.merge_button.clicked.connect(self.merge_selected_items)
        layout.addWidget(self.merge_button)

        layout.addWidget(self.debug_label)

        # Create a QTextEdit widget to display FFmpeg output
        self.ffmpeg_output.setFixedHeight(200)
        font = "Cascadia Mono"
        self.ffmpeg_output.setStyleSheet("QTextEdit{"
                                         "font: Cascadia Mono;"
                                         "color: green;"
                                         "background-color: black}")
        if font not in QFontDatabase().families():
            self.ffmpeg_output.setStyleSheet("QTextEdit{"
                                             "font: Monospace;"
                                             "color: green;"
                                             "background-color: black}")
        self.ffmpeg_output.setReadOnly(True)
        layout.addWidget(self.ffmpeg_output)

        self.setLayout(layout)
        self.setAcceptDrops(True)

        self.list_view.setModel(self.model)
        # Connect a signal to update button state
        self.list_view.model().rowsInserted.connect(self.update_button_state)
        self.list_view.model().rowsRemoved.connect(self.update_button_state)
        self.list_view.model().modelReset.connect(self.update_button_state)
        self.update_button_state()
        print(self.model.rowCount())
        self.check_ffmpeg()

    # Check for FFmpeg
    def check_ffmpeg(self):
        if not os.path.exists('ffmpeg.exe'):
            self.merge_button.setEnabled(False)
            self.add_files_button.setEnabled(False)
            self.remove_button.setEnabled(False)
            self.remove_all_button.setEnabled(False)
            self.format_combo_box.setEnabled(False)
            self.output_filename_input.setEnabled(False)
            self.ffmpeg_output.setText("FFmpeg was not found in the current folder")
            self.ffmpeg_output.setStyleSheet('QTextEdit{color: red;}')

    def update_line_edit(self):
        self.output_filename_input.setPlaceholderText(
            f'Enter output filename (default name: output.{self.format_combo_box.currentText()})')

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls() and all(self.is_audio_file(url.toLocalFile()) for url in event.mimeData().urls()):
            event.acceptProposedAction()

    def dropEvent(self, event):
        audio_files = [url.toLocalFile() for url in event.mimeData().urls() if self.is_audio_file(url.toLocalFile())]
        if audio_files:
            self.label.setText("Dropped audio files:")
            # Sort the files alphabetically
            self.update_audio_list(audio_files)

    @staticmethod
    def is_audio_file(file_path):
        allowed_extensions = extensions
        return any(file_path.lower().endswith(ext) for ext in allowed_extensions)

    def remove_selected_items(self):
        selected_indexes = self.list_view.selectedIndexes()
        rows_to_remove = sorted(set(index.row() for index in selected_indexes), reverse=True)
        for row in rows_to_remove:
            item = self.model.item(row)
            if item is not None:
                title = item.text()
                if title in self.audio_files:
                    self.model.removeRow(row)
                    del self.audio_files[title]

    def remove_all_items(self):
        self.model.clear()
        self.audio_files.clear()

    def add_files_dialog(self):
        options = QFileDialog.Options()
        options |= QFileDialog.ReadOnly
        file_dialog = QFileDialog()
        file_dialog.setFileMode(QFileDialog.ExistingFiles)
        file_dialog.setNameFilter("Audio Files (*.mp3 *.aac *.m4a *.wav *.flac *.ogg *.ac3 *.wma *.aiff "
                                  "*.mka *.mp2);;All Files (*)")
        audio_files, _ = file_dialog.getOpenFileNames(self, "Select Audio Files", "",
                                                      "Audio Files (*.mp3 *.aac *.m4a *.wav *.flac *.ogg *.ac3 *.wma "
                                                      "*.aiff *.mka *.mp2);",
                                                      options=options)

        if audio_files:
            self.update_audio_list(audio_files)

    def update_audio_list(self, audio_files):
        for file_path in audio_files:
            title = os.path.basename(file_path)
            if title in self.audio_files:
                # Remove the existing item from the list view
                item = self.model.findItems(title)
                if item:
                    self.model.removeRow(item[0].row())
            # Add the selected file to the list view and dictionary
            item = QStandardItem(title)
            self.model.appendRow(item)
            self.audio_files[title] = file_path

    def merge_selected_items(self):
        self.add_files_button.setEnabled(False)
        self.remove_button.setEnabled(False)
        self.remove_all_button.setEnabled(False)
        self.output_filename_input.setEnabled(False)
        self.ffmpeg_output.setEnabled(False)
        self.merge_button.setEnabled(False)
        self.format_combo_box.setEnabled(False)
        self.ffmpeg_output.clear()
        self.ffmpeg_output.setText("Audio file encoding in progress..")
        model = self.list_view.model()
        all_items = []
        for row in range(model.rowCount()):
            index = model.index(row, 0)  # Assuming a single-column list view
            item = model.data(index)
            all_items.append(item)

        # Now, the all_items list contains all items in the QListView
        print(all_items)
        output_format = self.format_combo_box.currentText()
        if output_format not in format_mapping:
            raise ValueError("Invalid output format")
        output_codec = format_mapping[output_format]["codec"]

        print("f"+self.output_file)
        if self.output_filename_input.text():
            self.output_file = remove_extension(self.output_filename_input.text())
        print("ff"+self.output_file)

        # Create input streams for selected files
        for file_path in self.audio_files.values():
            print(file_path)

        # Check for running thread
        if self.merge_thread:
            self.ffmpeg_output.setText('Merging already in progress!')
            return
        self.merge_thread = AudioMergeThread(
            self.audio_files.values(),
            self.output_file,
            output_format,
            output_codec
        )

        # Connect the thread's finished signal to append out or err when they are not None
        self.merge_thread.finished.connect(self.thread_merge_finished)
        self.merge_thread.start()
        # logging.info('ffmpeg stdout: %s', out.decode())
        # logging.info('ffmpeg stderr: %s', err.decode())

    def thread_merge_finished(self, out, err):
        self.ffmpeg_output.append(err) if err else self.ffmpeg_output.append(out) if out else self.ffmpeg_output.append(
            "An error occured")
        self.ffmpeg_output.append("Audio files successfully encoded!")
        print(self.output_file + '.' + self.format_combo_box.currentText())
        self.ffmpeg_output.append(
            f"File {self.output_file + '.' + self.format_combo_box.currentText() if not self.output_filename_input.text() else self.output_filename_input.text() + '.' + self.format_combo_box.currentText()} saved to disk.")
        self.merge_button.setEnabled(True)
        self.add_files_button.setEnabled(True)
        self.remove_button.setEnabled(True)
        self.remove_all_button.setEnabled(True)
        self.output_filename_input.setEnabled(True)
        self.ffmpeg_output.setEnabled(True)
        self.format_combo_box.setEnabled(True)
        self.merge_thread = None

    def update_button_state(self):
        # Get the number of items in the QListView
        item_count = self.model.rowCount()

        # Enable the button if there are at least 2 items, otherwise disable it
        if item_count >= 2:
            self.merge_button.setEnabled(True)
        else:
            self.merge_button.setEnabled(False)


class AudioFileDropApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.setGeometry(100, 100, 400, 400)  # Increased the height to accommodate the QTextEdit
        self.setWindowTitle('FastAudioMerge')
        central_widget = AudioFileDropWidget()
        self.setCentralWidget(central_widget)


def main():
    app = QApplication(sys.argv)
    extra = {

        # Density Scale
        'density_scale': '-1',
    }
    # setup stylesheet
    apply_stylesheet(app, theme='dark_blue.xml', invert_secondary=False, extra=extra, css_file='style.css')
    window = AudioFileDropApp()
    window.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
