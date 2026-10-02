'use client';

import React, { useState, useEffect, useRef } from 'react';
import { ThemeProvider } from '@/components/ThemeContext';
import { Sidebar, SectionId } from '@/components/Sidebar';
import { Header } from '@/components/Header';
import { DashboardView } from '@/components/DashboardView';
import { UploadCard } from '@/components/UploadCard';
import { LoadingAnimation } from '@/components/LoadingAnimation';
import { SignalQualityCard } from '@/components/SignalQualityCard';
import { DiagnosisCard } from '@/components/DiagnosisCard';
import { ConfidenceCard } from '@/components/ConfidenceCard';
import { RiskBadge } from '@/components/RiskBadge';
import { ProbabilityChart } from '@/components/ProbabilityChart';
import { WaveformViewer } from '@/components/WaveformViewer';
import { ShapChart } from '@/components/ShapChart';
import { RecommendationCard } from '@/components/RecommendationCard';
import { ClinicianReviewCard } from '@/components/ClinicianReviewCard';
import { ECGReportModal } from '@/components/ECGReportModal';
import { ECGPredictionResponse, ClinicianReview } from '@/types/ecg';
import { uploadECGFiles, checkBackendHealth } from '@/lib/api';
import { AlertCircle, RefreshCw, Download, ShieldAlert, Activity, FileText } from 'lucide-react';

function CardioInsightApp() {
  const [activeSection, setActiveSection] = useState<SectionId>('dashboard');
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState<boolean>(false);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<ECGPredictionResponse | null>(null);
  const [isReportOpen, setIsReportOpen] = useState<boolean>(false);
  const [isHealthy, setIsHealthy] = useState<boolean | null>(null);

  const analysisRef = useRef<HTMLDivElement>(null);
  const waveformRef = useRef<HTMLDivElement>(null);
  const explanationRef = useRef<HTMLDivElement>(null);
  const reviewRef = useRef<HTMLDivElement>(null);

  const [clinicianReview, setClinicianReview] = useState<ClinicianReview>({
    clinician_name: '',
    review_status: '',
    notes: '',
    review_date: new Date().toLocaleString(),
  });

  // Periodically verify backend status
  useEffect(() => {
    const verify = async () => {
      const status = await checkBackendHealth();
      setIsHealthy(status);
    };
    verify();
    const interval = setInterval(verify, 15000);
    return () => clearInterval(interval);
  }, []);

  const handleAnalyze = async (heaFile: File, datFile: File) => {
    setIsLoading(true);
    setError(null);

    try {
      const response = await uploadECGFiles(heaFile, datFile);
      setResult(response);
      setActiveSection('analysis');
      setClinicianReview({
        clinician_name: '',
        review_status: '',
        notes: '',
        review_date: new Date().toLocaleString(),
      });
    } catch (err: any) {
      setError(err.message || 'An unexpected error occurred during ECG analysis.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleNewAnalysis = () => {
    setResult(null);
    setError(null);
    setIsReportOpen(false);
    setActiveSection('upload');
  };

  const handleSelectSection = (section: SectionId) => {
    setActiveSection(section);
    if (section === 'report') {
      if (result) {
        setIsReportOpen(true);
      }
      return;
    }

    // Scroll to target section if viewing analysis workflow
    if (result) {
      if (section === 'analysis' && analysisRef.current) {
        analysisRef.current.scrollIntoView({ behavior: 'smooth' });
      } else if (section === 'waveform' && waveformRef.current) {
        waveformRef.current.scrollIntoView({ behavior: 'smooth' });
      } else if (section === 'explanation' && explanationRef.current) {
        explanationRef.current.scrollIntoView({ behavior: 'smooth' });
      } else if (section === 'review' && reviewRef.current) {
        reviewRef.current.scrollIntoView({ behavior: 'smooth' });
      }
    }
  };

  const hasAnalysis = result !== null;

  return (
    <div className="min-h-screen flex bg-slate-50 dark:bg-slate-950 text-slate-900 dark:text-slate-100 transition-colors">
      {/* Left Sidebar */}
      <Sidebar
        activeSection={activeSection}
        onSelectSection={handleSelectSection}
        onNewAnalysis={handleNewAnalysis}
        hasAnalysis={hasAnalysis}
        isHealthy={isHealthy}
        isOpenMobile={isMobileMenuOpen}
        onCloseMobile={() => setIsMobileMenuOpen(false)}
      />

      {/* Main App Content Area */}
      <div className="flex-1 md:pl-64 flex flex-col min-w-0">
        {/* Sticky Header with Context Bar & Theme Switcher */}
        <Header
          onOpenMobileMenu={() => setIsMobileMenuOpen(true)}
          recordInfo={result?.record_info}
          diagnosis={result?.diagnosis}
          hasAnalysis={hasAnalysis}
        />

        {/* Dynamic Body Content based on Active Navigation */}
        <main className="flex-1 p-4 sm:p-6 lg:p-8 max-w-7xl w-full mx-auto space-y-8">
          
          {/* DASHBOARD VIEW */}
          {activeSection === 'dashboard' && !isLoading && (
            <DashboardView
              onNavigateToUpload={() => setActiveSection('upload')}
              onNavigateToAnalysis={() => setActiveSection('analysis')}
              hasAnalysis={hasAnalysis}
              result={result}
              isHealthy={isHealthy}
            />
          )}

          {/* UPLOAD ECG VIEW */}
          {activeSection === 'upload' && !isLoading && (
            <div className="max-w-4xl mx-auto space-y-6">
              <div className="text-center space-y-2 mb-4">
                <h1 className="text-2xl sm:text-3xl font-extrabold text-slate-900 dark:text-white tracking-tight">
                  Upload 12-Lead ECG Record
                </h1>
                <p className="text-xs sm:text-sm text-slate-500 dark:text-slate-400 max-w-xl mx-auto">
                  Upload paired PTB-XL WFDB header (.hea) and signal data (.dat) files for automated machine learning classification and SHAP explainability.
                </p>
              </div>

              {error && (
                <div className="bg-red-50 dark:bg-red-950/60 border border-red-200 dark:border-red-800 text-red-800 dark:text-red-300 rounded-2xl p-5 shadow-md flex items-start gap-4 animate-fadeIn">
                  <div className="p-2.5 bg-red-100 dark:bg-red-900/50 rounded-xl text-red-600 dark:text-red-400 flex-shrink-0">
                    <AlertCircle className="w-5 h-5" />
                  </div>
                  <div className="space-y-1 flex-1 text-xs">
                    <h4 className="font-bold text-red-900 dark:text-red-200 text-sm">ECG Upload Error</h4>
                    <p className="leading-relaxed">{error}</p>
                  </div>
                </div>
              )}

              <UploadCard onAnalyze={handleAnalyze} isLoading={isLoading} />
            </div>
          )}

          {/* LOADING STATE */}
          {isLoading && (
            <div className="py-12">
              <LoadingAnimation />
            </div>
          )}

          {/* RESULTS & ANALYSIS DASHBOARD (Analysis, Waveform, Explanation, Review, Report views) */}
          {result && !isLoading && activeSection !== 'dashboard' && activeSection !== 'upload' && (
            <div className="space-y-8 animate-fadeIn">
              
              {/* Header Action Bar */}
              <div className="bg-white dark:bg-slate-900 rounded-2xl p-5 border border-slate-200 dark:border-slate-800 shadow-md flex flex-wrap items-center justify-between gap-4 transition-colors">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded-xl bg-sky-100 dark:bg-sky-950 text-sky-700 dark:text-sky-300 flex items-center justify-center font-bold">
                    <Activity className="w-5 h-5" />
                  </div>
                  <div>
                    <h2 className="text-lg font-bold text-slate-900 dark:text-white tracking-tight">ECG Analysis Results</h2>
                    <p className="text-xs text-slate-500 dark:text-slate-400">
                      Record: <span className="font-mono font-bold text-slate-700 dark:text-slate-300">{result.record_info?.record_id || 'WFDB Upload'}</span> • Processed by XGBoost & SHAP engines
                    </p>
                  </div>
                </div>

                <div className="flex items-center gap-3">
                  <button
                    onClick={() => setIsReportOpen(true)}
                    className="inline-flex items-center gap-1.5 text-xs font-bold text-white bg-slate-900 dark:bg-sky-600 hover:bg-slate-800 dark:hover:bg-sky-500 px-4 py-2.5 rounded-xl shadow-md transition-colors"
                  >
                    <Download className="w-4 h-4 text-sky-400 dark:text-white" />
                    <span>Download Clinical Report</span>
                  </button>

                  <button
                    onClick={handleNewAnalysis}
                    className="inline-flex items-center gap-1.5 text-xs font-semibold text-slate-700 dark:text-slate-200 bg-white dark:bg-slate-800 border border-slate-300 dark:border-slate-700 px-4 py-2.5 rounded-xl hover:bg-slate-50 dark:hover:bg-slate-700 transition-colors"
                  >
                    <RefreshCw className="w-4 h-4" />
                    <span>+ New Analysis</span>
                  </button>
                </div>
              </div>

              {/* SECTION 1: SIGNAL QUALITY & RECORD SUMMARY */}
              <div ref={analysisRef} className="scroll-mt-20">
                <SignalQualityCard signalQuality={result.signal_quality} recordInfo={result.record_info} />
              </div>

              {/* SECTION 2: PRIMARY AI FINDING, CONFIDENCE & REVIEW PRIORITY */}
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <DiagnosisCard diagnosis={result.diagnosis} />
                <ConfidenceCard confidence={result.confidence} />
                <RiskBadge riskLevel={result.risk_level} />
              </div>

              {/* SECTION 3: CLASS PROBABILITY BREAKDOWN */}
              <div className="space-y-3">
                <h3 className="text-xs font-bold text-slate-500 dark:text-slate-400 uppercase tracking-wider">
                  Model Output Probabilities Breakdown
                </h3>
                <ProbabilityChart probabilities={result.probabilities} predictedDiagnosis={result.diagnosis} />
              </div>

              {/* SECTION 4: 12-LEAD ECG WAVEFORM */}
              <div ref={waveformRef} className="scroll-mt-20">
                <WaveformViewer waveformData={result.waveform_data} recordInfo={result.record_info} />
              </div>

              {/* SECTION 5: SHAP EXPLANATION */}
              <div ref={explanationRef} className="scroll-mt-20">
                <ShapChart topFeatures={result.top_features} predictedDiagnosis={result.diagnosis} decisionStatus={result.decision_status} />
              </div>

              {/* SECTION 6: CLINICAL DECISION SUPPORT & REVIEW GUIDANCE */}
              <div ref={reviewRef} className="scroll-mt-20 space-y-6">
                <RecommendationCard
                  recommendation={result.recommendation}
                  evidence={result.clinical_evidence}
                  guidance={result.review_guidance}
                />
                
                {/* SECTION 7: CLINICIAN REVIEW SIGN-OFF */}
                <ClinicianReviewCard review={clinicianReview} onChange={setClinicianReview} />
              </div>

              {/* REGULATORY DISCLAIMER */}
              <div className="bg-amber-50 dark:bg-amber-950/50 border border-amber-200 dark:border-amber-800 text-amber-900 dark:text-amber-200 rounded-2xl p-5 shadow-sm flex items-start gap-3">
                <ShieldAlert className="w-5 h-5 text-amber-600 dark:text-amber-400 flex-shrink-0 mt-0.5" />
                <div className="space-y-1 text-xs">
                  <h4 className="font-bold text-amber-950 dark:text-amber-100">Clinical Decision Support Notice</h4>
                  <p className="leading-relaxed">
                    {result.disclaimer || "AI-generated results are intended for clinical decision support and must not be used as a standalone diagnosis. Final interpretation must be performed by a qualified clinician."}
                  </p>
                </div>
              </div>

              {/* Printable Medical Report Modal */}
              <ECGReportModal
                isOpen={isReportOpen}
                onClose={() => setIsReportOpen(false)}
                result={result}
                clinicianReview={clinicianReview}
              />
            </div>
          )}
        </main>

        {/* Footer */}
        <footer className="bg-white dark:bg-slate-900 border-t border-slate-200 dark:border-slate-800 py-5 px-6 transition-colors mt-auto">
          <div className="max-w-7xl mx-auto flex flex-col sm:flex-row items-center justify-between gap-4 text-xs text-slate-500 dark:text-slate-400">
            <div className="flex items-center gap-2">
              <Activity className="w-4 h-4 text-sky-600 dark:text-sky-400" />
              <span>CardioInsight — Explainable AI-Based ECG Clinical Decision Support System</span>
            </div>
            <div>
              <span>Powered by XGBoost, SHAP, Next.js & FastAPI</span>
            </div>
          </div>
        </footer>
      </div>
    </div>
  );
}

export default function Home() {
  return (
    <ThemeProvider>
      <CardioInsightApp />
    </ThemeProvider>
  );
}
