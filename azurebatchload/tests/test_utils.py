from azurebatchload.utils import convert_windows_path_to_unix


def test_convert_windows_path_to_unix():
    paths_to_check = {
        r"C:\Documents\Newsletters\Summer2018.pdf": r"C:/Documents/Newsletters/Summer2018.pdf",
        r"C:\\Documents\\Newsletters\\Summer2018.pdf": r"C:/Documents/Newsletters/Summer2018.pdf",
    }

    for p1, p2 in paths_to_check.items():
        assert convert_windows_path_to_unix(p1) == p2
