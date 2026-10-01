"""
=========================================================
ECG Clinical Decision Support System - v5 Feature Pipeline
=========================================================
Extracted directly from notebook/ECG_Clinical_Analyzer_final3.ipynb.
Contains feature extraction logic (322 raw features) and custom
transformer / estimator classes for XGBoost multi-label model loading.
=========================================================
"""

import sys
import numpy as np
import pandas as pd
import neurokit2 as nk
from scipy.signal import butter, sosfiltfilt
from scipy.fft import rfft, rfftfreq
from scipy.signal import welch
from scipy.stats import entropy
from scipy.integrate import trapezoid
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.feature_selection import VarianceThreshold
from sklearn.preprocessing import StandardScaler
from xgboost import XGBClassifier

# ----------------------------------------------------------------
# Constants & Configuration
# ----------------------------------------------------------------
SAMPLING_RATE = 500
LEAD_NAMES = ["I", "II", "III", "aVR", "aVL", "aVF", "V1", "V2", "V3", "V4", "V5", "V6"]
LEAD_IDX = {n: i for i, n in enumerate(LEAD_NAMES)}
DETECTION_LEADS = ["II", "I", "V5"]

PRECORD = ["V1", "V2", "V3", "V4", "V5", "V6"]
ANTERIOR = ["V1", "V2", "V3", "V4"]
INFERIOR = ["II", "III", "aVF"]
LATERAL = ["I", "aVL", "V5", "V6"]

QRS_VEL_FRAC = 0.12
QRS_HOLD_MS = 10

RANGE = {
    "pr": (60, 400),
    "qrs": (40, 250),
    "qt": (200, 700),
    "st": (0, 300),
    "pr_seg": (0, 250),
    "jt": (100, 600),
}

PWAVE_KEYS = [
    "pwave_dur",
    "pwave_dur_sd",
    "pwave_II_pos",
    "pwave_II_neg",
    "pwave_V1_pos",
    "pwave_V1_neg",
    "pwave_V1_ptf",
    "pwave_n_valid",
]

RHYTHM_KEYS = [
    "heart_rate",
    "mean_rr",
    "median_rr",
    "min_rr",
    "max_rr",
    "sdnn",
    "rmssd",
    "pnn50",
    "cvnn",
    "rr_range",
    "rr_iqr",
    "rr_skew",
]


# ----------------------------------------------------------------
# Custom Transformers & Estimator Classes (Pickle Compatibility)
# ----------------------------------------------------------------
class MissingFilter(BaseEstimator, TransformerMixin):
    def __init__(self, max_frac=0.5):
        self.max_frac = max_frac

    def fit(self, X, y=None):
        X = np.asarray(X, dtype=float)
        self.keep_idx_ = np.flatnonzero(np.isnan(X).mean(axis=0) <= self.max_frac)
        return self

    def transform(self, X):
        return np.asarray(X, dtype=float)[:, self.keep_idx_]


class QuantileClipper(BaseEstimator, TransformerMixin):
    def __init__(self, lower=0.005, upper=0.995):
        self.lower, self.upper = lower, upper

    def fit(self, X, y=None):
        X = np.asarray(X, dtype=float)
        self.lo_ = np.nanquantile(X, self.lower, axis=0)
        self.hi_ = np.nanquantile(X, self.upper, axis=0)
        return self

    def transform(self, X):
        return np.clip(np.asarray(X, dtype=float), self.lo_, self.hi_)


class CorrelationPruner(BaseEstimator, TransformerMixin):
    def __init__(self, threshold=0.95):
        self.threshold = threshold

    def fit(self, X, y=None):
        X = np.asarray(X, dtype=float)
        corr = np.abs(np.corrcoef(X, rowvar=False))
        corr = np.nan_to_num(corr, nan=0.0)
        n, drop = corr.shape[0], set()
        for i in range(n):
            if i in drop:
                continue
            for j in range(i + 1, n):
                if j not in drop and corr[i, j] > self.threshold:
                    drop.add(j)
        self.keep_idx_ = np.array([i for i in range(n) if i not in drop], dtype=int)
        return self

    def transform(self, X):
        return np.asarray(X, dtype=float)[:, self.keep_idx_]


class XGBMultiLabel(BaseEstimator):
    def __init__(
        self,
        n_estimators=400,
        learning_rate=0.05,
        max_depth=6,
        subsample=0.8,
        colsample_bytree=0.8,
        min_child_weight=2,
        reg_lambda=1.0,
        use_pos_weight=True,
        random_state=42,
        n_jobs=-1,
    ):
        self.n_estimators = n_estimators
        self.learning_rate = learning_rate
        self.max_depth = max_depth
        self.subsample = subsample
        self.colsample_bytree = colsample_bytree
        self.min_child_weight = min_child_weight
        self.reg_lambda = reg_lambda
        self.use_pos_weight = use_pos_weight
        self.random_state = random_state
        self.n_jobs = n_jobs

    def fit(self, X, Y):
        Y = np.asarray(Y)
        self.estimators_, self.pos_weight_ = [], []
        for j in range(Y.shape[1]):
            pos = float(Y[:, j].sum())
            neg = float(len(Y) - pos)
            spw = neg / max(pos, 1.0) if self.use_pos_weight else 1.0
            clf = XGBClassifier(
                n_estimators=self.n_estimators,
                learning_rate=self.learning_rate,
                max_depth=self.max_depth,
                subsample=self.subsample,
                colsample_bytree=self.colsample_bytree,
                min_child_weight=self.min_child_weight,
                reg_lambda=self.reg_lambda,
                scale_pos_weight=spw,
                objective="binary:logistic",
                eval_metric="logloss",
                random_state=self.random_state,
                n_jobs=self.n_jobs,
            )
            clf.fit(X, Y[:, j])
            self.estimators_.append(clf)
            self.pos_weight_.append(spw)
        return self

    def predict_proba(self, X):
        return np.column_stack([e.predict_proba(X)[:, 1] for e in self.estimators_])


def _make_xgb(
    spw,
    n_estimators,
    learning_rate,
    max_depth,
    subsample,
    colsample_bytree,
    min_child_weight,
    reg_lambda,
    random_state,
    n_jobs,
):
    return XGBClassifier(
        n_estimators=n_estimators,
        learning_rate=learning_rate,
        max_depth=max_depth,
        subsample=subsample,
        colsample_bytree=colsample_bytree,
        min_child_weight=min_child_weight,
        reg_lambda=reg_lambda,
        scale_pos_weight=spw,
        objective="binary:logistic",
        eval_metric="logloss",
        random_state=random_state,
        n_jobs=n_jobs,
    )


class XGBClassifierChain(BaseEstimator):
    def __init__(
        self,
        order=None,
        n_splits=5,
        n_estimators=400,
        learning_rate=0.05,
        max_depth=6,
        subsample=0.8,
        colsample_bytree=0.8,
        min_child_weight=2,
        reg_lambda=1.0,
        random_state=42,
        n_jobs=-1,
    ):
        self.order = order
        self.n_splits = n_splits
        self.n_estimators = n_estimators
        self.learning_rate = learning_rate
        self.max_depth = max_depth
        self.subsample = subsample
        self.colsample_bytree = colsample_bytree
        self.min_child_weight = min_child_weight
        self.reg_lambda = reg_lambda
        self.random_state = random_state
        self.n_jobs = n_jobs

    def fit(self, X, Y, groups=None):
        X = np.asarray(X, dtype=float)
        Y = np.asarray(Y, dtype=int)
        n, k = Y.shape
        groups = np.arange(n) if groups is None else np.asarray(groups)
        self.order_ = list(np.argsort(Y.sum(axis=0))) if self.order is None else list(self.order)

        oof = np.zeros((n, k), dtype=float)
        self.estimators_ = [None] * k
        self.pos_weight_ = [None] * k

        for pos, j in enumerate(self.order_):
            extra_cols = self.order_[:pos]
            Xj = np.hstack([X] + [oof[:, [c]] for c in extra_cols]) if extra_cols else X
            y = Y[:, j]
            pos_n, neg_n = float(y.sum()), float(len(y) - y.sum())
            spw = neg_n / max(pos_n, 1.0)

            clf = _make_xgb(
                spw,
                self.n_estimators,
                self.learning_rate,
                self.max_depth,
                self.subsample,
                self.colsample_bytree,
                self.min_child_weight,
                self.reg_lambda,
                self.random_state,
                self.n_jobs,
            )
            clf.fit(Xj, y)
            self.estimators_[j] = clf
            self.pos_weight_[j] = spw
        return self

    def predict_proba(self, X):
        X = np.asarray(X, dtype=float)
        n, k = X.shape[0], len(self.order_)
        probs = np.zeros((n, k), dtype=float)
        for pos, j in enumerate(self.order_):
            extra_cols = self.order_[:pos]
            Xj = np.hstack([X] + [probs[:, [c]] for c in extra_cols]) if extra_cols else X
            probs[:, j] = self.estimators_[j].predict_proba(Xj)[:, 1]
        return probs


def make_preprocessor(corr_threshold=0.95):
    return Pipeline(
        [
            ("missing", MissingFilter(max_frac=0.5)),
            ("impute", SimpleImputer(strategy="median")),
            ("var", VarianceThreshold(threshold=0.0)),
            ("clip", QuantileClipper()),
            ("corr", CorrelationPruner(threshold=corr_threshold)),
            ("scale", StandardScaler()),
        ]
    )


def fitted_feature_names(pre, input_names):
    names = np.asarray(input_names)
    for _, step in pre.steps:
        if hasattr(step, "keep_idx_"):
            names = names[step.keep_idx_]
        elif hasattr(step, "get_support"):
            names = names[step.get_support()]
    return list(names)


# ----------------------------------------------------------------
# Helper Scalar Functions
# ----------------------------------------------------------------
def _clean(a):
    a = np.asarray(a, dtype=float).ravel()
    return a[~np.isnan(a)]


def nmax(a):
    a = _clean(a)
    return float(np.max(a)) if a.size else np.nan


def nmin(a):
    a = _clean(a)
    return float(np.min(a)) if a.size else np.nan


def nmean(a):
    a = _clean(a)
    return float(np.mean(a)) if a.size else np.nan


def nmed(a):
    a = _clean(a)
    return float(np.median(a)) if a.size else np.nan


def nstd(a):
    a = _clean(a)
    return float(np.std(a)) if a.size > 1 else np.nan


def _nearest(ref, candidates, lo, hi):
    if candidates is None or len(candidates) == 0:
        return np.nan
    c = np.asarray(candidates, dtype=float)
    c = c[~np.isnan(c)]
    c = c[(c >= ref + lo) & (c <= ref + hi)]
    return float(c[np.argmin(np.abs(c - ref))]) if c.size else np.nan


# ----------------------------------------------------------------
# Feature Extraction Signal Analysis Functions
# ----------------------------------------------------------------
def spatial_velocity(signal, fs):
    sos = butter(2, [0.5, 40.0], btype="bandpass", fs=fs, output="sos")
    x = sosfiltfilt(sos, signal, axis=0)
    v = np.sqrt(np.sum(np.diff(x, axis=0) ** 2, axis=1)) * fs
    v = np.concatenate([v[:1], v])
    k = max(1, int(round(0.008 * fs)))
    return np.convolve(v, np.ones(k) / k, mode="same")


def refine_qrs_bounds(signal, r_peaks, fs, frac=QRS_VEL_FRAC, hold_ms=QRS_HOLD_MS):
    v = spatial_velocity(signal, fs)
    n = len(v)
    ms = lambda t: int(round(t * fs / 1000.0))
    hold = max(2, ms(hold_ms))
    floor = 2.0 * float(np.median(v))
    on = np.full(len(r_peaks), np.nan)
    off = np.full(len(r_peaks), np.nan)
    for k, r in enumerate(np.asarray(r_peaks, dtype=float)):
        if np.isnan(r):
            continue
        r = int(r)
        lo, hi = r - ms(130), r + ms(150)
        if lo < 0 or hi >= n:
            continue
        c0 = r - ms(60)
        core = v[c0 : r + ms(60) + 1]
        pk = c0 + int(np.argmax(core))
        vmax = float(v[pk])
        thr = max(frac * vmax, floor)
        if vmax <= 0 or thr >= 0.5 * vmax:
            continue
        run = 0
        for i in range(pk, lo - 1, -1):
            run = run + 1 if v[i] < thr else 0
            if run >= hold:
                on[k] = i + run - 1
                break
        run = 0
        for i in range(pk, hi + 1):
            run = run + 1 if v[i] < thr else 0
            if run >= hold:
                off[k] = i - run + 1
                break
    return on, off


def build_beat_table(waves, r_peaks, fs, signal=None):
    ms = lambda x: int(round(x * fs / 1000.0))
    win = {
        "P_on": (-400, -70),
        "P": (-350, -60),
        "P_off": (-300, -40),
        "QRS_on": (-120, -5),
        "Q": (-100, -2),
        "QRS_off": (5, 140),
        "S": (2, 120),
        "T_on": (40, 400),
        "T": (80, 600),
        "T_off": (120, 700),
    }
    key = {
        "P_on": "ECG_P_Onsets",
        "P": "ECG_P_Peaks",
        "P_off": "ECG_P_Offsets",
        "QRS_on": "ECG_R_Onsets",
        "Q": "ECG_Q_Peaks",
        "QRS_off": "ECG_R_Offsets",
        "S": "ECG_S_Peaks",
        "T_on": "ECG_T_Onsets",
        "T": "ECG_T_Peaks",
        "T_off": "ECG_T_Offsets",
    }
    rows = []
    for r in np.asarray(r_peaks, dtype=float):
        row = {"R": r}
        for name, (lo_ms, hi_ms) in win.items():
            row[name] = _nearest(r, waves.get(key[name], []), ms(lo_ms), ms(hi_ms))
        rows.append(row)
    bt = pd.DataFrame(rows)
    rr_prev = np.full(len(bt), np.nan)
    if len(bt) > 1:
        rr_prev[1:] = np.diff(bt["R"].values) / fs
    bt["RR_prev"] = rr_prev

    bt["QRS_refined"] = 0.0
    if signal is not None and len(bt):
        on_r, off_r = refine_qrs_bounds(signal, bt["R"].values, fs)
        good = ~np.isnan(on_r) & ~np.isnan(off_r) & (off_r > on_r)
        bt.loc[good, "QRS_on"] = on_r[good]
        bt.loc[good, "QRS_off"] = off_r[good]
        bt.loc[good, "QRS_refined"] = 1.0
    return bt


def detect_and_delineate(signal, fs):
    last_err = None
    for ln in DETECTION_LEADS:
        try:
            x = signal[:, LEAD_IDX[ln]]
            cleaned = nk.ecg_clean(x, sampling_rate=fs, method="neurokit")
            r = np.asarray(nk.ecg_peaks(cleaned, sampling_rate=fs)[1]["ECG_R_Peaks"], dtype=int)
            if len(r) < 3:
                raise ValueError(f"only {len(r)} R peaks on lead {ln}")
            _, waves = nk.ecg_delineate(cleaned, r, sampling_rate=fs, method="dwt")
            return cleaned, r, waves, ln
        except Exception as e:
            last_err = e
    raise ValueError(f"delineation failed on {DETECTION_LEADS}: {last_err!r}")


def extract_rhythm_features(r_peaks, fs):
    f = {f"rhythm_{k}": np.nan for k in RHYTHM_KEYS}
    f["rhythm_n_beats"] = float(len(r_peaks))
    if len(r_peaks) < 3:
        return f
    rr_all = np.diff(np.asarray(r_peaks, dtype=float)) / fs
    ok = (rr_all > 0.25) & (rr_all < 3.0)
    rr = rr_all[ok]
    if rr.size < 2:
        return f
    drr = np.diff(rr_all)[ok[:-1] & ok[1:]]
    m, s = np.mean(rr), np.std(rr)
    f["rhythm_heart_rate"] = 60.0 / m
    f["rhythm_mean_rr"] = m
    f["rhythm_median_rr"] = float(np.median(rr))
    f["rhythm_min_rr"] = float(np.min(rr))
    f["rhythm_max_rr"] = float(np.max(rr))
    f["rhythm_sdnn"] = float(np.std(rr, ddof=1))
    f["rhythm_rmssd"] = float(np.sqrt(np.mean(drr**2))) if drr.size else np.nan
    f["rhythm_pnn50"] = float(100.0 * np.mean(np.abs(drr) > 0.05)) if drr.size else np.nan
    f["rhythm_cvnn"] = f["rhythm_sdnn"] / m
    f["rhythm_rr_range"] = float(np.ptp(rr))
    f["rhythm_rr_iqr"] = float(np.percentile(rr, 75) - np.percentile(rr, 25))
    f["rhythm_rr_skew"] = float(np.mean(((rr - m) / s) ** 3)) if s > 0 else np.nan
    return f


def _gate(vals, key):
    lo, hi = RANGE[key]
    v = _clean(vals)
    return v[(v >= lo) & (v <= hi)]


def extract_interval_features(bt, fs):
    to_ms = lambda d: d / fs * 1000.0
    pr = _gate(to_ms(bt["QRS_on"] - bt["P_on"]).values, "pr")
    pr_seg = _gate(to_ms(bt["QRS_on"] - bt["P_off"]).values, "pr_seg")
    qrs = _gate(to_ms(bt["QRS_off"] - bt["QRS_on"]).values, "qrs")
    qt_raw = to_ms(bt["T_off"] - bt["QRS_on"]).values
    qt = _gate(qt_raw, "qt")
    st = _gate(to_ms(bt["T_on"] - bt["QRS_off"]).values, "st")
    jt = _gate(to_ms(bt["T_off"] - bt["QRS_off"]).values, "jt")

    rr_prev = bt["RR_prev"].values
    ok = (~np.isnan(qt_raw)) & (~np.isnan(rr_prev)) & (rr_prev > 0.25) & (rr_prev < 3.0)
    ok &= (qt_raw >= RANGE["qt"][0]) & (qt_raw <= RANGE["qt"][1])
    qtc_b = qt_raw[ok] / np.sqrt(rr_prev[ok])
    qtc_f = qt_raw[ok] / np.cbrt(rr_prev[ok])

    mean_rr_ms = nmean(rr_prev) * 1000.0
    return {
        "intv_pr": nmed(pr),
        "intv_pr_segment": nmed(pr_seg),
        "intv_qrs": nmed(qrs),
        "intv_qrs_sd": nstd(qrs),
        "intv_qt": nmed(qt),
        "intv_qtc_bazett": nmed(qtc_b),
        "intv_qtc_frid": nmed(qtc_f),
        "intv_st_segment": nmed(st),
        "intv_jt": nmed(jt),
        "intv_qt_rr_ratio": nmed(qt) / mean_rr_ms if mean_rr_ms and not np.isnan(mean_rr_ms) else np.nan,
        "intv_n_valid_qrs": float(len(qrs)),
        "intv_n_valid_qt": float(len(qt)),
        "intv_p_detect_frac": float(bt["P"].notna().mean()),
        "intv_t_detect_frac": float(bt["T"].notna().mean()),
        "intv_qrs_refined_frac": float(bt["QRS_refined"].mean()) if "QRS_refined" in bt else np.nan,
    }


def extract_clinical_lead_features(signal, bt, fs):
    f, n_s = {}, signal.shape[0]
    off60, off80, pre40 = int(round(0.060 * fs)), int(round(0.080 * fs)), int(round(0.040 * fs))

    valid = bt.dropna(subset=["QRS_on", "QRS_off"])
    beats = []
    for b in valid.itertuples(index=False):
        p_off = int(b.P_off) if not np.isnan(b.P_off) else -1
        t_pk = int(b.T) if not np.isnan(b.T) else -1
        beats.append((int(b.QRS_on), int(b.QRS_off), int(b.R), p_off, t_pk))

    per_lead = {}
    for name, li in LEAD_IDX.items():
        lead = signal[:, li]
        R_, S_, Q_, J_, ST60_, ST80_, T_, AREA_ = ([] for _ in range(8))
        for on, off, r, p_off, t_pk in beats:
            if not (0 <= on < off < n_s):
                continue
            if 0 <= p_off < on:
                base = float(np.median(lead[p_off:on]))
            else:
                lo = max(0, on - pre40)
                base = float(np.median(lead[lo:on])) if on > lo else 0.0
            seg = lead[on:off] - base
            if seg.size == 0:
                continue
            k = int(np.clip(r - on, 0, seg.size - 1))
            R_.append(max(float(np.max(seg)), 0.0))
            S_.append(min(float(np.min(seg[k:])), 0.0))
            Q_.append(min(float(np.min(seg[: max(k, 1)])), 0.0))
            AREA_.append(float(trapezoid(seg) / fs * 1000.0))
            J_.append(float(lead[off] - base))
            if off + off60 < n_s:
                ST60_.append(float(lead[off + off60] - base))
            if off + off80 < n_s:
                ST80_.append(float(lead[off + off80] - base))
            if 0 <= t_pk < n_s:
                T_.append(float(lead[t_pk] - base))

        m = {
            "R": nmed(R_),
            "S": nmed(S_),
            "Q": nmed(Q_),
            "J": nmed(J_),
            "ST60": nmed(ST60_),
            "ST80": nmed(ST80_),
            "T": nmed(T_),
            "AREA": nmed(AREA_),
        }
        per_lead[name] = m
        for k_, v_ in [
            ("R", m["R"]),
            ("S", m["S"]),
            ("Q", m["Q"]),
            ("J", m["J"]),
            ("ST60", m["ST60"]),
            ("ST80", m["ST80"]),
            ("T", m["T"]),
            ("area", m["AREA"]),
        ]:
            f[f"clin_{name}_{k_}"] = v_
        f[f"clin_{name}_QR_ratio"] = (
            abs(m["Q"]) / m["R"]
            if (not np.isnan(m["R"]) and m["R"] > 0.05 and not np.isnan(m["Q"]))
            else np.nan
        )
        f[f"clin_{name}_RS_ratio"] = (
            m["R"] / max(abs(m["S"]), 0.02)
            if not (np.isnan(m["R"]) or np.isnan(m["S"]))
            else np.nan
        )

    g = lambda ld, k: per_lead[ld][k]

    f["clin_sokolow_lyon"] = abs(g("V1", "S")) + np.fmax(g("V5", "R"), g("V6", "R"))
    f["clin_cornell_volt"] = g("aVL", "R") + abs(g("V3", "S"))
    f["clin_cornell_prod"] = np.nan
    f["clin_lewis_index"] = (g("I", "R") - g("III", "R")) + (abs(g("III", "S")) - abs(g("I", "S")))
    f["clin_RV5_SV1"] = g("V5", "R") + abs(g("V1", "S"))
    f["clin_gubner"] = g("I", "R") + abs(g("III", "S"))
    f["clin_rvh_index"] = g("V1", "R") + abs(g("V5", "S"))
    f["clin_peguero"] = abs(nmin([g(l, "S") for l in PRECORD])) + abs(g("V4", "S"))
    f["clin_RV6_RV5_ratio"] = (
        g("V6", "R") / g("V5", "R")
        if g("V5", "R") and g("V5", "R") > 0.05
        else np.nan
    )
    f["clin_max_R_precordial"] = nmax([g(l, "R") for l in PRECORD])
    f["clin_max_S_precordial"] = nmin([g(l, "S") for l in PRECORD])

    rs = np.array([g(l, "R") for l in PRECORD], dtype=float)
    ss = np.array([abs(g(l, "S")) for l in PRECORD], dtype=float)
    good = ~np.isnan(rs)
    f["clin_r_progression_slope"] = (
        float(np.polyfit(np.arange(6)[good], rs[good], 1)[0])
        if good.sum() >= 3
        else np.nan
    )
    both = ~np.isnan(rs) & ~np.isnan(ss)
    if both.sum() >= 4:
        trans = np.where(rs[both] > ss[both])[0]
        f["clin_transition_lead"] = float(np.arange(1, 7)[both][trans[0]]) if trans.size else 7.0
    else:
        f["clin_transition_lead"] = np.nan

    net_I, net_F = g("I", "AREA"), g("aVF", "AREA")
    if np.isnan(net_I) or np.isnan(net_F):
        ang = np.nan
    else:
        ang = float(np.degrees(np.arctan2(net_F, net_I)))
    f["clin_qrs_axis"] = ang
    f["clin_qrs_axis_sin"] = float(np.sin(np.radians(ang))) if not np.isnan(ang) else np.nan
    f["clin_qrs_axis_cos"] = float(np.cos(np.radians(ang))) if not np.isnan(ang) else np.nan
    f["clin_net_area_I"], f["clin_net_area_aVF"] = net_I, net_F

    for region, leads in [("ant", ANTERIOR), ("inf", INFERIOR), ("lat", LATERAL)]:
        st = [g(l, "ST60") for l in leads]
        tw = [g(l, "T") for l in leads]
        f[f"clin_st60_{region}_mean"] = nmean(st)
        f[f"clin_st60_{region}_max"] = nmax(st)
        f[f"clin_st60_{region}_min"] = nmin(st)
        f[f"clin_t_{region}_mean"] = nmean(tw)

    all_st = np.array([g(l, "ST60") for l in LEAD_NAMES], dtype=float)
    all_t = np.array([g(l, "T") for l in LEAD_NAMES], dtype=float)
    q_leads = [l for l in LEAD_NAMES if l not in ("aVR", "V1")]
    all_qr = np.array([f[f"clin_{l}_QR_ratio"] for l in q_leads], dtype=float)
    cnt = lambda arr, cond: float(np.sum(cond)) if np.any(~np.isnan(arr)) else np.nan
    f["clin_st_max_elev"] = nmax(all_st)
    f["clin_st_max_depr"] = nmin(all_st)
    f["clin_n_leads_st_up"] = cnt(all_st, all_st > 0.1)
    f["clin_n_leads_st_down"] = cnt(all_st, all_st < -0.1)
    f["clin_n_leads_t_inv"] = cnt(all_t, all_t < -0.1)
    f["clin_n_leads_path_q"] = cnt(all_qr, all_qr > 0.25)
    f["clin_max_qr_ratio"] = nmax(all_qr)
    return f


def extract_pwave_features(signal, bt, fs):
    f = {k: np.nan for k in PWAVE_KEYS}
    n = signal.shape[0]
    pre40 = int(round(0.040 * fs))
    pos, neg, ptf, durs = {"II": [], "V1": []}, {"II": [], "V1": []}, [], []
    for b in bt[["P_on", "P_off", "QRS_on"]].dropna().itertuples(index=False):
        p_on, p_off, q_on = int(b.P_on), int(b.P_off), int(b.QRS_on)
        d = (p_off - p_on) / fs * 1000.0
        if not (0 <= p_on < p_off < q_on < n) or not (40.0 <= d <= 200.0):
            continue
        durs.append(d)
        for ln in ("II", "V1"):
            x = signal[:, LEAD_IDX[ln]]
            base = float(np.median(x[p_off:q_on])) if q_on - p_off >= 2 else float(np.median(x[max(0, q_on - pre40) : q_on]))
            seg = x[p_on : p_off + 1] - base
            pos[ln].append(max(float(seg.max()), 0.0))
            neg[ln].append(min(float(seg.min()), 0.0))
            if ln == "V1":
                half = seg[len(seg) // 2 :]
                depth = min(float(half.min()), 0.0)
                width = float(np.sum(half < 0)) / fs * 1000.0
                ptf.append(abs(depth) * width)
    f["pwave_n_valid"] = float(len(durs))
    if durs:
        f["pwave_dur"], f["pwave_dur_sd"] = float(np.median(durs)), nstd(durs)
        f["pwave_II_pos"], f["pwave_II_neg"] = nmed(pos["II"]), nmed(neg["II"])
        f["pwave_V1_pos"], f["pwave_V1_neg"] = nmed(pos["V1"]), nmed(neg["V1"])
        f["pwave_V1_ptf"] = nmed(ptf)
    return f


def extract_morphology_features(signal, bt):
    lead = signal[:, LEAD_IDX["II"]]
    n = len(lead)
    f = {}

    def amps(col):
        idx = bt[col].dropna().values.astype(int)
        idx = idx[(idx >= 0) & (idx < n)]
        return lead[idx] if idx.size else np.array([])

    for wave, col in [("p", "P"), ("q", "Q"), ("r", "R"), ("s", "S"), ("t", "T")]:
        v = amps(col)
        f[f"morph_{wave}_amp_mean"] = float(np.mean(v)) if v.size else np.nan
        f[f"morph_{wave}_amp_std"] = float(np.std(v)) if v.size else np.nan
        f[f"morph_{wave}_amp_max"] = float(np.max(v)) if v.size else np.nan
        f[f"morph_{wave}_amp_min"] = float(np.min(v)) if v.size else np.nan

    r_, s_, q_ = f["morph_r_amp_mean"], abs(f["morph_s_amp_mean"]), abs(f["morph_q_amp_mean"])
    f["morph_r_s_ratio"] = r_ / max(s_, 0.02) if not np.isnan(r_) and not np.isnan(s_) else np.nan
    f["morph_r_q_ratio"] = r_ / max(q_, 0.02) if not np.isnan(r_) and not np.isnan(q_) else np.nan

    d = np.diff(lead)
    rms = float(np.sqrt(np.mean(lead**2)))
    var = float(np.var(lead))
    f["morph_peak_to_peak"] = float(np.ptp(lead))
    f["morph_signal_energy"] = float(np.sum(lead**2))
    f["morph_signal_rms"] = rms
    f["morph_mean_abs_amplitude"] = float(np.mean(np.abs(lead)))
    f["morph_crest_factor"] = float(np.max(np.abs(lead)) / rms) if rms > 0 else np.nan
    f["morph_waveform_length"] = float(np.sum(np.abs(d)))
    f["morph_hjorth_activity"] = var
    f["morph_hjorth_mobility"] = float(np.sqrt(np.var(d) / var)) if var > 0 else np.nan
    return f


def extract_beat_morphology_features(signal, bt, fs):
    lead = signal[:, LEAD_IDX["II"]]
    f = {}
    to_ms = lambda d: d / fs * 1000.0

    qw = _clean(to_ms((bt["QRS_off"] - bt["QRS_on"]).values))
    qw = qw[(qw >= 40) & (qw <= 250)]
    tw = _clean(to_ms((bt["T_off"] - bt["T_on"]).values))
    tw = tw[(tw >= 50) & (tw <= 400)]
    f["beat_qrs_width_mean"] = float(np.mean(qw)) if qw.size else np.nan
    f["beat_qrs_width_std"] = float(np.std(qw)) if qw.size > 1 else np.nan
    f["beat_t_width_mean"] = float(np.mean(tw)) if tw.size else np.nan
    f["beat_t_width_std"] = float(np.std(tw)) if tw.size > 1 else np.nan

    up, down, area = [], [], []
    for b in bt.itertuples(index=False):
        r = int(b.R)
        if not np.isnan(b.Q):
            q = int(b.Q)
            up.append((lead[r] - lead[q]) / max(r - q, 1))
        if not np.isnan(b.S):
            s = int(b.S)
            down.append((lead[r] - lead[s]) / max(s - r, 1))
        if not (np.isnan(b.QRS_on) or np.isnan(b.QRS_off)):
            on, off = int(b.QRS_on), int(b.QRS_off)
            if 0 <= on < off <= len(lead):
                area.append(float(np.sum(np.abs(lead[on:off]))))
    for name, vals in [("upstroke", up), ("downstroke", down), ("area", area)]:
        f[f"beat_{name}_mean"] = float(np.mean(vals)) if vals else np.nan
        f[f"beat_{name}_std"] = float(np.std(vals)) if len(vals) > 1 else np.nan
    return f


def extract_frequency_features(signal, fs):
    lead = signal[:, LEAD_IDX["II"]]
    fft_v = np.abs(rfft(lead))[1:]
    freqs = rfftfreq(len(lead), d=1.0 / fs)[1:]
    tot = float(np.sum(fft_v))
    centroid = float(np.sum(freqs * fft_v) / tot) if tot else np.nan
    bandwidth = float(np.sqrt(np.sum(((freqs - centroid) ** 2) * fft_v) / tot)) if tot else np.nan
    p = fft_v**2
    p = p / np.sum(p) if np.sum(p) else p
    fr, psd = welch(lead, fs=fs, nperseg=min(1024, len(lead)))
    return {
        "freq_dominant": float(freqs[int(np.argmax(fft_v))]),
        "freq_centroid": centroid,
        "freq_bandwidth": bandwidth,
        "freq_entropy": float(entropy(p)) if np.sum(p) else np.nan,
        "freq_total_power": float(trapezoid(psd, fr)),
    }


def extract_per_lead_features(signal):
    f = {}
    for name, i in LEAD_IDX.items():
        x = signal[:, i]
        f[f"lead_{name}_mean"] = float(np.mean(x))
        f[f"lead_{name}_std"] = float(np.std(x))
        f[f"lead_{name}_median"] = float(np.median(x))
        f[f"lead_{name}_max"] = float(np.max(x))
        f[f"lead_{name}_min"] = float(np.min(x))
        f[f"lead_{name}_rms"] = float(np.sqrt(np.mean(x**2)))
        f[f"lead_{name}_ptp"] = float(np.ptp(x))
    return f


def extract_complete_features(signal, fs=SAMPLING_RATE):
    cleaned, r_peaks, waves, det_lead = detect_and_delineate(signal, fs)
    bt = build_beat_table(waves, r_peaks, fs, signal)

    f = {}
    f.update(extract_rhythm_features(r_peaks, fs))
    f.update(extract_interval_features(bt, fs))
    f.update(extract_clinical_lead_features(signal, bt, fs))
    f.update(extract_pwave_features(signal, bt, fs))
    f.update(extract_morphology_features(signal, bt))
    f.update(extract_beat_morphology_features(signal, bt, fs))
    f.update(extract_frequency_features(signal, fs))
    f.update(extract_per_lead_features(signal))

    cv, qd = f.get("clin_cornell_volt", np.nan), f.get("intv_qrs", np.nan)
    f["clin_cornell_prod"] = cv * qd if not (np.isnan(cv) or np.isnan(qd)) else np.nan
    return f
