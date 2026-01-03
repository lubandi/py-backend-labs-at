import sys

import pytest

from importer_cli.cli import main


def test_no_args(monkeypatch, capsys):
    monkeypatch.setattr(sys, "argv", ["cli.py"])
    with pytest.raises(SystemExit):
        main()
    captured = capsys.readouterr()
    # Check the usage message appears
    assert "usage: cli.py" in captured.err
    assert "the following arguments are required: csv_file" in captured.err


def test_import_csv_success(tmp_path, monkeypatch, capsys):
    # Create a fake CSV file
    csv_file = tmp_path / "users.csv"
    csv_file.write_text("user_id,name,email\n1,John,john@example.com\n")

    monkeypatch.setattr(sys, "argv", ["cli.py", str(csv_file)])
    main()
    captured = capsys.readouterr()
    assert "Successfully imported" in captured.out


def test_import_csv_errors(tmp_path, monkeypatch, capsys):
    # CSV with missing columns
    csv_file = tmp_path / "bad_users.csv"
    csv_file.write_text("user_id,name\n1,John\n")  # missing email

    monkeypatch.setattr(sys, "argv", ["cli.py", str(csv_file)])
    main()
    captured = capsys.readouterr()
    assert "Errors encountered" in captured.out


def test_verbose_flag(tmp_path, monkeypatch, capsys):
    csv_file = tmp_path / "users.csv"
    csv_file.write_text("user_id,name,email\n1,John,john@example.com\n")

    monkeypatch.setattr(sys, "argv", ["cli.py", str(csv_file), "-v"])
    main()
    captured = capsys.readouterr()
    assert "✅ Successfully imported" in captured.out
