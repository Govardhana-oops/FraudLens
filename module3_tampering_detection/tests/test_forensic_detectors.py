"""Unit Tests for Individual Forensic Detectors in Module 3."""

import pytest
import numpy as np
from src.forensics.ela_detector import ELADetector
from src.forensics.noise_inconsistency_detector import NoiseInconsistencyDetector
from src.forensics.edge_gradient_detector import EdgeGradientDetector
from src.forensics.font_texture_detector import FontTextureDetector
from src.forensics.frequency_fft_detector import FrequencyFFTDetector

@pytest.fixture
def base_config():
    return {
        "ela_params": {"quality": 90, "scale": 15},
        "noise_params": {"patch_size": 32},
        "spectral_params": {"notch_filter_radius": 15}
    }

def test_ela_detector_uniform_image(base_config):
    detector = ELADetector(base_config)
    arr = np.ones((512, 512, 3), dtype=np.uint8) * 200
    res = detector.detect(arr)
    assert res.name == "error_level_analysis"
    assert res.anomaly_score < 0.40

def test_noise_detector_uniform_noise(base_config):
    detector = NoiseInconsistencyDetector(base_config)
    # Uniform Gaussian noise across the whole image
    np.random.seed(42)
    noise = np.random.normal(128, 10, (512, 512, 3)).astype(np.uint8)
    res = detector.detect(noise)
    assert res.name == "noise_inconsistency"
    assert res.anomaly_score < 0.45

def test_edge_gradient_detector_smooth_image(base_config):
    detector = EdgeGradientDetector(base_config)
    arr = np.ones((512, 512, 3), dtype=np.uint8) * 220
    res = detector.detect(arr)
    assert res.name == "edge_gradient_discontinuity"
    assert res.anomaly_score == 0.0

def test_frequency_fft_detector_smooth_image(base_config):
    detector = FrequencyFFTDetector(base_config)
    arr = np.ones((512, 512, 3), dtype=np.uint8) * 220
    res = detector.detect(arr)
    assert res.name == "frequency_fft_spectral"
    assert res.anomaly_score < 0.35
