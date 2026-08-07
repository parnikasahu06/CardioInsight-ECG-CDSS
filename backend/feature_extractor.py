"""
feature_extractor.py

Production-ready ECG clinical feature engineering module.

This module contains ONLY the reusable feature-engineering logic extracted
from the ECG_Clinical_Analyzer.ipynb notebook. Every calculation, feature
name, feature order, threshold and algorithm has been preserved exactly as
implemented in the notebook. No logic has been redesigned, optimized or
simplified.

Notebook-specific code (plotting, model training, evaluation, SHAP, CSV
export, dataset loops, print statements) has been intentionally removed.
"""

import numpy as np

import neurokit2 as nk

from scipy.fft import rfft, rfftfreq
from scipy.signal import welch
from scipy.stats import entropy


# =====================================================
# Project Configuration
# =====================================================

SAMPLING_RATE = 500
NUM_LEADS = 12


# =====================================================
# Manually Identified Duplicate Features
# =====================================================
# These features were manually reviewed and removed after correlation
# analysis in the notebook to eliminate duplicate representations while
# preserving clinically interpretable variables.

DUPLICATE_FEATURES = [

    # ---------- HRV duplicates ----------
    "HRV_MeanNN",
    "HRV_SDNN",
    "HRV_RMSSD",
    "HRV_SDSD",
    "HRV_CVNN",
    "HRV_CVSD",
    "HRV_MedianNN",
    "HRV_IQRNN",
    "HRV_MinNN",
    "HRV_MaxNN",
    "HRV_pNN20",
    "HRV_pNN50",

    # ---------- Duplicate Lead-II Features ----------
    "II_energy",
    "II_rms",
    "II_peak_to_peak",

    # ---------- Duplicate Signal Features ----------
    "signal_range",

    # ---------- NeuroKit Internal Duplicates ----------
    "HRV_C1a",
    "HRV_C2a",
    "HRV_Ca",
    "HRV_AI",
    "HRV_SD1"

]


# ==========================================
# Beat Matching Utility
# ==========================================

def nearest_previous(reference, candidates):
    """
    Returns the nearest candidate occurring before the reference point.
    """

    candidates = np.array(candidates)
    candidates = candidates[candidates < reference]

    if len(candidates) == 0:
        return np.nan

    return candidates[-1]


def nearest_next(reference, candidates):
    """
    Returns the nearest candidate occurring after the reference point.
    """

    candidates = np.array(candidates)
    candidates = candidates[candidates > reference]

    if len(candidates) == 0:
        return np.nan

    return candidates[0]


# ===========================================
# Beat Morphology Helper
# ===========================================

def valid_points(points):
    """
    Remove NaN values and convert to integer indices.
    """
    points = np.asarray(points)

    return points[~np.isnan(points)].astype(int)


class FeatureExtractor:
    """
    Extracts clinically meaningful ECG features from a single 12-lead
    ECG recording, exactly reproducing the feature engineering pipeline
    developed in the ECG_Clinical_Analyzer notebook.
    """

    def __init__(self, sampling_rate=SAMPLING_RATE):
        self.sampling_rate = sampling_rate

    # =====================================================
    # Rhythm Feature Extraction
    # =====================================================

    def extract_rhythm_features(self, r_peaks, sampling_rate=100):
        """
        Extract Heart Rate Variability (HRV) features
        from detected R peaks.
        """

        if len(r_peaks) < 2:
            return {
                "heart_rate": np.nan,
                "mean_rr": np.nan,
                "median_rr": np.nan,
                "min_rr": np.nan,
                "max_rr": np.nan,
                "std_rr": np.nan,
                "rmssd": np.nan,
                "sdsd": np.nan,
                "nn20": np.nan,
                "nn50": np.nan,
                "pnn20": np.nan,
                "pnn50": np.nan,
                "rr_range": np.nan,
                "rr_iqr": np.nan,
                "cvnn": np.nan,
                "cvsd": np.nan
            }

        rr = np.diff(r_peaks) / sampling_rate

        diff_rr = np.diff(rr)

        nn20 = np.sum(np.abs(diff_rr) > 0.02)
        nn50 = np.sum(np.abs(diff_rr) > 0.05)

        rmssd = np.sqrt(np.mean(diff_rr**2))

        features = {

            "heart_rate": 60 / np.mean(rr),

            "mean_rr": np.mean(rr),

            "median_rr": np.median(rr),

            "min_rr": np.min(rr),

            "max_rr": np.max(rr),

            "std_rr": np.std(rr),

            "rmssd": rmssd,

            "sdsd": np.std(diff_rr),

            "nn20": nn20,

            "nn50": nn50,

            "pnn20": nn20 / len(diff_rr)*100,

            "pnn50": nn50 / len(diff_rr)*100,

            "rr_range": np.max(rr) - np.min(rr),

            "rr_iqr": np.percentile(rr,75)-np.percentile(rr,25),

            "cvnn": np.std(rr)/np.mean(rr),

            "cvsd": rmssd/np.mean(rr)

        }

        return features

    # =====================================================
    # Advanced HRV Features (NeuroKit2)
    # =====================================================

    def extract_advanced_hrv_features(self, r_peaks, sampling_rate=500):
        """
        Extract advanced HRV features using NeuroKit2.
        """

        if len(r_peaks) < 4:
            return {}

        try:

            peaks = {
                "ECG_R_Peaks": np.array(r_peaks, dtype=int)
            }

            hrv = nk.hrv(
                peaks,
                sampling_rate=sampling_rate,
                show=False
            )

            features = {}

            for col in hrv.columns:

                value = hrv.iloc[0][col]

                if np.isscalar(value):
                    
                    features[col] = float(value)

            for key, value in features.items():

              if isinstance(value, (int, float, np.floating)):
                if np.isinf(value):
                    features[key] = np.nan

            return features

        except Exception:

            return {}

    # ==========================================
    # Clinical Interval Feature Extraction
    # ==========================================

    def extract_interval_features(self, waves, r_peaks, sampling_rate=500):
        """
        Extract clinically important ECG interval features.
        """

        pr_intervals = []
        qrs_durations = []
        qt_intervals = []
        qtcs = []
        st_segments = []
        pr_segments = []

        rr = np.diff(r_peaks) / sampling_rate

        for r in r_peaks:

            # ---------- Previous Waves ----------
            p_onset = nearest_previous(r, waves["ECG_P_Onsets"])
            p_offset = nearest_previous(r, waves["ECG_P_Offsets"])
            q_peak = nearest_previous(r, waves["ECG_Q_Peaks"])

            # ---------- Next Waves ----------
            s_peak = nearest_next(r, waves["ECG_S_Peaks"])
            t_offset = nearest_next(r, waves["ECG_T_Offsets"])

            # ---------- PR Interval ----------
            if not np.isnan(p_onset) and not np.isnan(q_peak):
                pr = (q_peak - p_onset) / sampling_rate * 1000
                pr_intervals.append(pr)

            # ---------- PR Segment ----------
            if not np.isnan(p_offset) and not np.isnan(q_peak):
                pr_seg = (q_peak - p_offset) / sampling_rate * 1000
                pr_segments.append(pr_seg)

            # ---------- QRS Duration ----------
            if not np.isnan(q_peak) and not np.isnan(s_peak):
                qrs = (s_peak - q_peak) / sampling_rate * 1000
                qrs_durations.append(qrs)

            # ---------- QT Interval ----------
            if not np.isnan(q_peak) and not np.isnan(t_offset):
                qt = (t_offset - q_peak) / sampling_rate * 1000
                qt_intervals.append(qt)

                if len(rr) > 0:
                    qtc = qt / np.sqrt(np.mean(rr))
                    qtcs.append(qtc)

            # ---------- ST Segment ----------
            if not np.isnan(s_peak) and not np.isnan(t_offset):
                st = (t_offset - s_peak) / sampling_rate * 1000
                st_segments.append(st)

        features = {

            "pr_interval": np.nanmean(pr_intervals),

            "pr_segment": np.nanmean(pr_segments),

            "qrs_duration": np.nanmean(qrs_durations),

            "qt_interval": np.nanmean(qt_intervals),

            "qtc": np.nanmean(qtcs),

            "st_segment": np.nanmean(st_segments),

            "mean_rr_interval": np.mean(rr) * 1000 if len(rr) else np.nan,

            "qt_rr_ratio":
                np.nanmean(qt_intervals) /
                (np.mean(rr) * 1000)
                if len(rr) else np.nan
        }

        return features

    # ==========================================
    # ECG Wave Amplitude Extraction
    # ==========================================

    def extract_wave_amplitudes(self, signal, waves, r_peaks):
        """
        Extract amplitudes of P, Q, R, S and T waves
        from Lead II.
        """

        lead = signal[:, 1]

        amplitudes = {}

        wave_map = {
            "p": waves.get("ECG_P_Peaks", []),
            "q": waves.get("ECG_Q_Peaks", []),
            "r": r_peaks,
            "s": waves.get("ECG_S_Peaks", []),
            "t": waves.get("ECG_T_Peaks", [])
        }

        for wave, indices in wave_map.items():

            indices = np.array(indices)

            indices = indices[~np.isnan(indices)].astype(int)

            indices = indices[
                (indices >= 0) &
                (indices < len(lead))
            ]

            amplitudes[wave] = lead[indices]

        return amplitudes

    # ==========================================
    # Morphological Feature Extraction
    # ==========================================

    def extract_morphology_features(self, signal, wave_amplitudes):
        """
        Extract morphology features from Lead II ECG.
        """

        lead = signal[:, 1]

        features = {}

        # =====================================================
        # Mean Wave Amplitudes
        # =====================================================

        for wave in ["p", "q", "r", "s", "t"]:

            values = np.array(wave_amplitudes[wave])

            if len(values):

                features[f"{wave}_amp_mean"] = np.mean(values)
                features[f"{wave}_amp_std"] = np.std(values)
                features[f"{wave}_amp_max"] = np.max(values)
                features[f"{wave}_amp_min"] = np.min(values)

            else:

                features[f"{wave}_amp_mean"] = np.nan
                features[f"{wave}_amp_std"] = np.nan
                features[f"{wave}_amp_max"] = np.nan
                features[f"{wave}_amp_min"] = np.nan

        # =====================================================
        # Clinical Ratios
        # =====================================================

        r = features["r_amp_mean"]
        s = abs(features["s_amp_mean"])
        q = abs(features["q_amp_mean"])

        features["r_s_ratio"] = r / s if s else np.nan
        features["r_q_ratio"] = r / q if q else np.nan

        # =====================================================
        # Global Signal Statistics
        # =====================================================

        features["peak_to_peak"] = np.ptp(lead)
        features["signal_energy"] = np.sum(lead ** 2)
        features["signal_rms"] = np.sqrt(np.mean(lead ** 2))
        features["mean_abs_amplitude"] = np.mean(np.abs(lead))
        features["signal_range"] = np.max(lead) - np.min(lead)

        # =====================================================
        # Signal Complexity Features
        # =====================================================

        diff_signal = np.diff(lead)

        # Crest Factor
        rms = features["signal_rms"]

        features["crest_factor"] = (
            np.max(np.abs(lead)) / rms
            if rms > 0 else np.nan
        )

        # Waveform Length
        features["waveform_length"] = np.sum(np.abs(diff_signal))

        # Mean Absolute Difference
        features["mean_abs_diff"] = np.mean(np.abs(diff_signal))

        # Hjorth Activity
        features["hjorth_activity"] = np.var(lead)

        # Hjorth Mobility
        variance = np.var(lead)
        diff_variance = np.var(diff_signal)

        features["hjorth_mobility"] = (
            np.sqrt(diff_variance / variance)
            if variance > 0 else np.nan
        )

        return features

    # ==========================================
    # Frequency Domain Feature Extraction
    # ==========================================

    def extract_frequency_features(self, signal, sampling_rate=500):
        """
        Extract frequency-domain features from Lead II ECG.
        """

        lead = signal[:, 1]

        # ------------------------------------
        # FFT
        # ------------------------------------

        fft_values = np.abs(rfft(lead))
        frequencies = rfftfreq(len(lead), d=1/sampling_rate)

        # Remove DC component
        fft_values = fft_values[1:]
        frequencies = frequencies[1:]

        # ------------------------------------
        # Dominant Frequency
        # ------------------------------------

        dominant_frequency = frequencies[np.argmax(fft_values)]

        # ------------------------------------
        # Spectral Centroid
        # ------------------------------------

        spectral_centroid = (
            np.sum(frequencies * fft_values)
            / np.sum(fft_values)
        )

        # ------------------------------------
        # Spectral Bandwidth
        # ------------------------------------

        spectral_bandwidth = np.sqrt(
            np.sum(
                ((frequencies - spectral_centroid) ** 2)
                * fft_values
            )
            / np.sum(fft_values)
        )

        # ------------------------------------
        # Spectral Entropy
        # ------------------------------------

        power = fft_values ** 2
        power = power / np.sum(power)

        spectral_entropy = entropy(power)

        # ------------------------------------
        # Welch Power Spectrum
        # ------------------------------------

        freqs, psd = welch(
            lead,
            fs=sampling_rate,
            nperseg=1024
        )

        # Better estimation of total spectral power
        total_power = np.trapezoid(psd, freqs)

        # ------------------------------------
        # Final Features
        # ------------------------------------

        features = {

            "dominant_frequency": dominant_frequency,

            "spectral_centroid": spectral_centroid,

            "spectral_bandwidth": spectral_bandwidth,

            "spectral_entropy": spectral_entropy,

            "total_power": total_power

        }

        return features

    # ===========================================
    # Beat Morphology Feature Extraction
    # ===========================================

    def extract_beat_morphology_features(self, signal, waves, r_peaks):
        """
        Extract clinically meaningful beat morphology features
        from Lead II.

        Parameters
        ----------
        signal : ndarray (5000,12)
        waves : dict
        r_peaks : array

        Returns
        -------
        dict
        """

        lead = signal[:, 1]

        def valid(arr):
            arr = np.asarray(arr)
            return arr[~np.isnan(arr)].astype(int)

        # -----------------------------
        # Wave Locations
        # -----------------------------
        p = valid(waves["ECG_P_Peaks"])
        q = valid(waves["ECG_Q_Peaks"])
        s = valid(waves["ECG_S_Peaks"])
        t = valid(waves["ECG_T_Peaks"])

        r = valid(r_peaks)

        r_on = valid(waves["ECG_R_Onsets"])
        r_off = valid(waves["ECG_R_Offsets"])

        t_on = valid(waves["ECG_T_Onsets"])
        t_off = valid(waves["ECG_T_Offsets"])

        features = {}

        # ====================================================
        # QRS Width
        # ====================================================

        n = min(len(r_on), len(r_off))

        if n > 0:

            qrs_width = (r_off[:n] - r_on[:n]) / SAMPLING_RATE * 1000

            features["qrs_width_mean"] = np.mean(qrs_width)
            features["qrs_width_std"] = np.std(qrs_width)

        else:

            features["qrs_width_mean"] = np.nan
            features["qrs_width_std"] = np.nan

        # ====================================================
        # T Width
        # ====================================================

        n = min(len(t_on), len(t_off))

        if n > 0:

            t_width = (t_off[:n] - t_on[:n]) / SAMPLING_RATE * 1000

            features["t_width_mean"] = np.mean(t_width)
            features["t_width_std"] = np.std(t_width)

        else:

            features["t_width_mean"] = np.nan
            features["t_width_std"] = np.nan

        # ====================================================
        # Upstroke / Downstroke Slopes
        # ====================================================

        up_slopes = []
        down_slopes = []

        n = min(len(q), len(r), len(s))

        for i in range(n):

            rise = lead[r[i]] - lead[q[i]]
            fall = lead[r[i]] - lead[s[i]]

            rise_time = max(r[i] - q[i], 1)
            fall_time = max(s[i] - r[i], 1)

            up_slopes.append(rise / rise_time)
            down_slopes.append(fall / fall_time)

        if len(up_slopes):

            features["upstroke_mean"] = np.mean(up_slopes)
            features["upstroke_std"] = np.std(up_slopes)

            features["downstroke_mean"] = np.mean(down_slopes)
            features["downstroke_std"] = np.std(down_slopes)

        else:

            features["upstroke_mean"] = np.nan
            features["upstroke_std"] = np.nan

            features["downstroke_mean"] = np.nan
            features["downstroke_std"] = np.nan

        # ====================================================
        # Beat Area
        # ====================================================

        beat_area = []

        n = min(len(r_on), len(r_off))

        for i in range(n):

            beat = lead[r_on[i]:r_off[i]]

            beat_area.append(np.sum(np.abs(beat)))

        if len(beat_area):

            features["beat_area_mean"] = np.mean(beat_area)
            features["beat_area_std"] = np.std(beat_area)

        else:

            features["beat_area_mean"] = np.nan
            features["beat_area_std"] = np.nan

        return features

    # ===========================================
    # Per-Lead Signal Feature Extraction
    # ===========================================

    def extract_per_lead_features(self, signal):
        """
        Extract robust statistical descriptors
        from each of the 12 ECG leads.
        """

        features = {}

        lead_names = [
            "I","II","III",
            "aVR","aVL","aVF",
            "V1","V2","V3","V4","V5","V6"
        ]

        for i, lead_name in enumerate(lead_names):

            lead = signal[:, i]

            features[f"{lead_name}_mean"] = np.mean(lead)

            features[f"{lead_name}_std"] = np.std(lead)

            features[f"{lead_name}_median"] = np.median(lead)

            features[f"{lead_name}_max"] = np.max(lead)

            features[f"{lead_name}_min"] = np.min(lead)

            features[f"{lead_name}_rms"] = np.sqrt(np.mean(lead**2))

            features[f"{lead_name}_energy"] = np.sum(lead**2)

            features[f"{lead_name}_peak_to_peak"] = np.ptp(lead)

        return features

    # =====================================================
    # Complete Feature Extraction Pipeline
    # =====================================================

    def extract_complete_features(self, signal, sampling_rate=500):
        """
        Extract all clinically meaningful ECG features
        from a single 12-lead ECG.
        """

        features = {}

        # -------------------------------------------------
        # Lead II Preprocessing
        # -------------------------------------------------

        lead_ii = signal[:, 1]

        cleaned_signal = nk.ecg_clean(
            lead_ii,
            sampling_rate=sampling_rate
        )

        info = nk.ecg_peaks(
            cleaned_signal,
            sampling_rate=sampling_rate
        )[1]

        _, waves = nk.ecg_delineate(
            cleaned_signal,
            info["ECG_R_Peaks"],
            sampling_rate=sampling_rate,
            method="dwt"
        )

        # -------------------------------------------------
        # Rhythm Features
        # -------------------------------------------------

        rhythm = self.extract_rhythm_features(
            info["ECG_R_Peaks"],
            sampling_rate
        )

        features.update(rhythm)

        # -------------------------------------------------
        # Advanced HRV Features
        # -------------------------------------------------

        advanced_hrv = self.extract_advanced_hrv_features(
            info["ECG_R_Peaks"],
            sampling_rate
        )

        features.update(advanced_hrv)

        # -------------------------------------------------
        # Clinical Interval Features
        # -------------------------------------------------

        interval = self.extract_interval_features(
            waves,
            info["ECG_R_Peaks"],
            sampling_rate
        )

        features.update(interval)

        # -------------------------------------------------
        # Wave Amplitudes
        # -------------------------------------------------

        wave_amplitudes = self.extract_wave_amplitudes(
            signal,
            waves,
            info["ECG_R_Peaks"]
        )

        # -------------------------------------------------
        # Morphological Features
        # -------------------------------------------------

        morphology = self.extract_morphology_features(
            signal,
            wave_amplitudes
        )

        features.update(morphology)

        # -------------------------------------------------
        # Frequency Domain Features
        # -------------------------------------------------

        frequency = self.extract_frequency_features(
            signal,
            sampling_rate
        )

        features.update(frequency)

        # -------------------------------------------------
        # Beat Morphology Features
        # -------------------------------------------------

        beat = self.extract_beat_morphology_features(
            signal,
            waves,
            info["ECG_R_Peaks"]
        )

        features.update(beat)

        # -------------------------------------------------
        # Per-Lead Features
        # -------------------------------------------------

        perlead = self.extract_per_lead_features(
            signal
        )

        features.update(perlead)

        return features

    # =====================================================
    # Public Entry Point
    # =====================================================

    def extract_features(self, signal, sampling_rate=None, drop_duplicates=True):
        """
        Extract the full clinical ECG feature vector for a single
        12-lead ECG recording, matching the feature set used to train
        the final XGBoost model.

        Parameters
        ----------
        signal : ndarray of shape (n_samples, 12)
            Raw 12-lead ECG signal (as loaded, e.g. via wfdb.rdsamp).
        sampling_rate : int, optional
            Sampling rate of the signal in Hz. Defaults to the
            extractor's configured sampling_rate (500 Hz).
        drop_duplicates : bool, default True
            If True, removes the manually identified duplicate features
            (DUPLICATE_FEATURES) exactly as done in the notebook prior
            to model training.

        Returns
        -------
        dict
            Dictionary of feature_name -> value, in the exact order
            produced by the notebook's feature engineering pipeline.
        """

        if sampling_rate is None:
            sampling_rate = self.sampling_rate

        features = self.extract_complete_features(
            signal,
            sampling_rate=sampling_rate
        )

        if drop_duplicates:
            for feature in DUPLICATE_FEATURES:
                features.pop(feature, None)

        return features
