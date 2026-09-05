"""CLI Commands Functional Verification for Module 13."""

import io
import pytest
import numpy as np
import cv2
from PIL import Image
from module13_final_validation.src.cli import build_parser

@pytest.fixture
def sample_image_path(tmp_path):
    img = Image.new("RGB", (100, 100), color=(240, 240, 240))
    p = tmp_path / "test_doc.jpg"
    img.save(p)
    return str(p)

def test_cli_system_check(capsys):
    parser = build_parser()
    args = parser.parse_args(["check"])
    code = args.func(args)
    assert code == 0
    captured = capsys.readouterr()
    assert "Module 1" in captured.out
    assert "All 12 Subsystems Fully Operational" in captured.out

def test_cli_lookup(capsys):
    parser = build_parser()
    args = parser.parse_args(["lookup", "NONEXISTENT123", "--country", "USA"])
    code = args.func(args)
    assert code == 0
    captured = capsys.readouterr()
    assert "is_flagged" in captured.out

def test_cli_sync(capsys):
    parser = build_parser()
    args = parser.parse_args(["sync"])
    code = args.func(args)
    assert code == 0
    captured = capsys.readouterr()
    assert "sync_status" in captured.out

def test_cli_audit_verify(capsys):
    parser = build_parser()
    args = parser.parse_args(["audit-verify"])
    code = args.func(args)
    assert code == 0
    captured = capsys.readouterr()
    assert "CRYPTOGRAPHICALLY VALID" in captured.out

def test_cli_screen(capsys, sample_image_path):
    parser = build_parser()
    args = parser.parse_args(["screen", "--image", sample_image_path, "--json"])
    code = args.func(args)
    assert code == 0
    captured = capsys.readouterr()
    assert "screening_id" in captured.out
    assert "recommended_action" in captured.out
