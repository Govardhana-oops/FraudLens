"""Calibrated 2D FFT Frequency & Spectral Anomaly Forensic Detector."""

from typing import Dict, Any, Optional, List
import numpy as np
import cv2
from .base_detector import BaseForensicDetector
from ..schemas.output_schema import ForensicIndicatorResult

class FrequencyFFTDetector(BaseForensicDetector):
    """Detects periodic resampling grids, screen replay moiré lattices, and spectral anomalies using 2D FFT."""

    def detect(self, image: np.ndarray, regions: Optional[Dict[str, Any]] = None) -> ForensicIndicatorResult:
        if image is None or image.size == 0:
            return ForensicIndicatorResult(
                name="frequency_fft_spectral",
                anomaly_score=0.0,
                confidence=0.0,
                details={"error": "Empty image buffer"}
            )

        try:
            # 1. Convert to grayscale
            if len(image.shape) == 3:
                gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY if image.shape[2] == 3 else cv2.COLOR_RGB2GRAY)
            else:
                gray = image.copy()

            # Resize to standardized dimension for FFT
            target_size = 256
            resized = cv2.resize(gray, (target_size, target_size), interpolation=cv2.INTER_AREA)

            # 2. Compute 2D Fast Fourier Transform
            dft = np.fft.fft2(resized.astype(np.float32))
            dft_shift = np.fft.fftshift(dft)
            magnitude_spectrum = 20 * np.log(np.abs(dft_shift) + 1.0)

            # 3. Mask out DC center component and natural horizontal/vertical axes
            center_y, center_x = target_size // 2, target_size // 2
            r = self.config.get("spectral_params", {}).get("notch_filter_radius", 15)
            y, x = np.ogrid[:target_size, :target_size]
            mask = (x - center_x)**2 + (y - center_y)**2 <= r*r

            # Also mask 3-pixel wide cross-hair on center axes (natural text/line orientations)
            axis_width = 3
            mask |= (np.abs(x - center_x) <= axis_width) | (np.abs(y - center_y) <= axis_width)

            magnitude_spectrum[mask] = 0.0

            # 4. Search for anomalous off-axis spectral peaks (indicative of screen pixel moiré lattices)
            high_freq_mean = float(np.mean(magnitude_spectrum[~mask]))
            high_freq_std = float(np.std(magnitude_spectrum[~mask]))
            high_freq_max = float(np.max(magnitude_spectrum[~mask]))

            peak_prominence = (high_freq_max - high_freq_mean) / (high_freq_std + 1e-4)

            # Anomaly score: prominence > 3.5 indicates sharp isolated off-axis spectral spike
            anomaly_score = float(np.clip((peak_prominence - 3.5) / 2.5, 0.0, 1.0))

            return ForensicIndicatorResult(
                name="frequency_fft_spectral",
                anomaly_score=round(anomaly_score, 4),
                confidence=0.91,
                details={
                    "high_freq_mean": round(high_freq_mean, 2),
                    "high_freq_std": round(high_freq_std, 2),
                    "high_freq_max": round(high_freq_max, 2),
                    "peak_prominence": round(peak_prominence, 2)
                }
            )
        except Exception as e:
            return ForensicIndicatorResult(
                name="frequency_fft_spectral",
                anomaly_score=0.0,
                confidence=0.5,
                details={"exception": str(e)}
            )
