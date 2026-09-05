"""Unit Tests for Evaluation Metrics (CER, WER, Field F1)."""

import pytest
from src.evaluation.metrics import compute_cer, compute_wer, evaluate_field_extraction

def test_cer_identical():
    ref = "PASSPORT"
    hyp = "PASSPORT"
    cer, acc = compute_cer(ref, hyp)
    assert cer == 0.0
    assert acc == 1.0

def test_cer_single_substitution():
    ref = "PASSPORT"
    hyp = "PASSPO8T"
    cer, acc = compute_cer(ref, hyp)
    assert cer == 1 / 8
    assert acc == 7 / 8

def test_wer():
    ref = "STATE OF UTOPIA DRIVER LICENSE"
    hyp = "STATE OF UTOPIA DRIVER LICENCE"
    wer, acc = compute_wer(ref, hyp)
    assert wer > 0.0
    assert acc < 1.0

def test_field_extraction_evaluation():
    gt = {
        "passport_number": {"text": "P12345678"},
        "full_name": {"text": "JOHN SMITH"}
    }
    ext = {
        "passport_number": type("Field", (), {"value": "P12345678"})(),
        "full_name": type("Field", (), {"value": "JOHN SMITH"})()
    }
    eval_res = evaluate_field_extraction(gt, ext)
    assert eval_res["precision"] == 1.0
    assert eval_res["recall"] == 1.0
    assert eval_res["f1"] == 1.0
    assert eval_res["exact_match_ratio"] == 1.0
