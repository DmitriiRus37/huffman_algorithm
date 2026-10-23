import pytest

QtWidgets = pytest.importorskip('PyQt6.QtWidgets')

import app_window  # noqa: E402
from app_window import Ui_main_window, remove_input_file_suffix  # noqa: E402


@pytest.fixture(scope='module')
def qapp():
    return QtWidgets.QApplication.instance() or QtWidgets.QApplication([])


@pytest.fixture
def ui(qapp):
    window = QtWidgets.QWidget()
    ui = Ui_main_window()
    ui.setupUi(window)
    yield ui
    window.deleteLater()


def fake_dialog(monkeypatch, path):
    calls = []

    def get_open_file_name(parent, title, directory):
        calls.append((parent, title, directory))
        return path, ''
    monkeypatch.setattr(app_window.QFileDialog, 'getOpenFileName', get_open_file_name)
    return calls


@pytest.mark.parametrize('path,expected', [
    ('/a/b.txt.huff', '/a/b.txt'), ('/a/b.lzw', '/a/b'), ('/a/b.h_ad', '/a/b'), ('/a/b.txt', '/a/b.txt'),
])
def test_remove_input_file_suffix(path, expected):
    assert remove_input_file_suffix(path) == expected


def test_setup_ui(ui):
    assert ui.main_window.windowTitle() == 'File Compressor'
    assert ui.btn_huffman.isChecked()
    assert ui.tabWidget.count() == 2
    assert ui.tabWidget.tabText(1) == 'Decompress'
    assert ui.check_clicked_button_to_compress_method() is ui.btn_huffman


@pytest.mark.parametrize('button,suffix', [('btn_huffman', '.huff'), ('btn_lzw', '.lzw'),
                                           ('btn_huffman_adaptive', '.h_ad')])
def test_choose_file_to_compress(ui, monkeypatch, button, suffix):
    getattr(ui, button).click()
    calls = fake_dialog(monkeypatch, '/data/file.txt')
    ui.btn_choose_input_file_to_compress.click()
    assert calls[0][0] is ui.main_window
    assert ui.input_file_to_compress_field.toPlainText() == '/data/file.txt'
    assert ui.output_file_compressed_field.toPlainText() == '/data/file.txt' + suffix
    assert ui.check_clicked_button_to_compress_method() is getattr(ui, button)


def test_cancelled_dialogs_leave_fields_empty(ui, monkeypatch):
    fake_dialog(monkeypatch, '')
    ui.open_input_file_to_compress_dialog()
    ui.open_input_file_to_decompress_dialog()
    assert ui.input_file_to_compress_field.toPlainText() == ''
    assert ui.input_file_to_decompress_field.toPlainText() == ''


def test_choose_file_to_decompress(ui, monkeypatch):
    fake_dialog(monkeypatch, '/data/file.txt.huff')
    ui.btn_choose_input_file_to_decompress.click()
    assert ui.input_file_to_decompress_field.toPlainText() == '/data/file.txt.huff'
    assert ui.output_file_decompressed_field.toPlainText() == '/data/file.txt.txt'


def uncheck_all(ui):
    for b in (ui.btn_huffman, ui.btn_lzw, ui.btn_huffman_adaptive):
        b.setAutoExclusive(False)
        b.setChecked(False)


def test_no_method_selected_raises(ui):
    uncheck_all(ui)
    with pytest.raises(RuntimeError, match='None button'):
        ui.check_clicked_button_to_compress_method()
    with pytest.raises(RuntimeError, match='None button'):
        ui.open_input_file_to_compress_dialog()


def test_compress_and_decompress_buttons_round_trip(ui, tmp_path):
    src = tmp_path / 'src.txt'
    src.write_bytes(b'gui round trip ' * 50)
    ui.input_file_to_compress_field.setPlainText(str(src))
    ui.output_file_compressed_field.setPlainText(str(tmp_path / 'src.txt.huff'))
    ui.btn_compress.click()
    ui.input_file_to_decompress_field.setPlainText(str(tmp_path / 'src.txt.huff'))
    ui.output_file_decompressed_field.setPlainText(str(tmp_path / 'out.txt'))
    ui.btn_decompress.click()
    assert (tmp_path / 'out.txt').read_bytes() == src.read_bytes()


@pytest.mark.parametrize('button', ['btn_lzw', 'btn_huffman_adaptive'])
def test_unimplemented_methods_write_nothing(ui, tmp_path, button):
    src = tmp_path / 'src.txt'
    src.write_bytes(b'data')
    getattr(ui, button).click()
    ui.input_file_to_compress_field.setPlainText(str(src))
    ui.output_file_compressed_field.setPlainText(str(tmp_path / 'out'))
    ui.compress_button_action()
    assert not (tmp_path / 'out').exists()


def test_buttons_ignore_empty_paths(ui, tmp_path):
    ui.compress_button_action()
    ui.decompress_button_action()
    assert list(tmp_path.iterdir()) == []
