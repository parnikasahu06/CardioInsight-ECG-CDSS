'use client';

import React, { useState, useRef } from 'react';
import { Upload, FileCode, CheckCircle2, AlertCircle, X, ArrowRight, Activity, Database } from 'lucide-react';
import { UploadState } from '@/types/ecg';

interface UploadCardProps {
  onAnalyze: (heaFile: File, datFile: File) => void;
  isLoading: boolean;
}

export const UploadCard: React.FC<UploadCardProps> = ({ onAnalyze, isLoading }) => {
  const [files, setFiles] = useState<UploadState>({ heaFile: null, datFile: null });
  const [dragActive, setDragActive] = useState<boolean>(false);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  const heaInputRef = useRef<HTMLInputElement>(null);
  const datInputRef = useRef<HTMLInputElement>(null);

  const processFiles = (fileList: FileList | File[]) => {
    setErrorMsg(null);
    let hea: File | null = files.heaFile;
    let dat: File | null = files.datFile;

    Array.from(fileList).forEach(file => {
      if (file.name.toLowerCase().endsWith('.hea')) {
        hea = file;
      } else if (file.name.toLowerCase().endsWith('.dat')) {
        dat = file;
      }
    });

    if (!hea && !dat) {
      setErrorMsg('Please select or drop valid WFDB files (.hea and .dat).');
      return;
    }

    setFiles({ heaFile: hea, datFile: dat });
  };

  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true);
    } else if (e.type === 'dragleave') {
      setDragActive(false);
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      processFiles(e.dataTransfer.files);
    }
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>, type: 'hea' | 'dat') => {
    if (e.target.files && e.target.files[0]) {
      const selectedFile = e.target.files[0];
      if (type === 'hea' && selectedFile.name.endsWith('.hea')) {
        setFiles(prev => ({ ...prev, heaFile: selectedFile }));
        setErrorMsg(null);
      } else if (type === 'dat' && selectedFile.name.endsWith('.dat')) {
        setFiles(prev => ({ ...prev, datFile: selectedFile }));
        setErrorMsg(null);
      } else {
        setErrorMsg(`Invalid file type for ${type.toUpperCase()}. Expected .${type}`);
      }
    }
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!files.heaFile) {
      setErrorMsg('Missing .hea header file.');
      return;
    }
    if (!files.datFile) {
      setErrorMsg('Missing .dat signal data file.');
      return;
    }
    onAnalyze(files.heaFile, files.datFile);
  };

  // Helper to load sample files from backend ptb-xl dataset
  const loadSampleRecord = async () => {
    try {
      setErrorMsg(null);
      const [heaRes, datRes] = await Promise.all([
        fetch('/samples/00001_hr.hea'),
        fetch('/samples/00001_hr.dat')
      ]);

      if (!heaRes.ok || !datRes.ok) {
        throw new Error('Could not fetch sample files');
      }

      const heaBlob = await heaRes.blob();
      const datBlob = await datRes.blob();

      const sampleHeaFile = new File([heaBlob], '00001_hr.hea', { type: 'text/plain' });
      const sampleDatFile = new File([datBlob], '00001_hr.dat', { type: 'application/octet-stream' });

      setFiles({ heaFile: sampleHeaFile, datFile: sampleDatFile });
    } catch (err) {
      setErrorMsg('Failed to load sample record.');
    }
  };

  const isReady = files.heaFile !== null && files.datFile !== null;

  return (
    <div className="bg-white dark:bg-slate-900 rounded-2xl shadow-xl border border-slate-200 dark:border-slate-800 overflow-hidden transition-colors">
      {/* Header bar */}
      <div className="bg-slate-50 dark:bg-slate-800/60 px-6 py-4 border-b border-slate-200 dark:border-slate-800 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 rounded-lg bg-sky-100 dark:bg-sky-950 text-sky-700 dark:text-sky-300 flex items-center justify-center font-bold">
            <Upload className="w-4 h-4" />
          </div>
          <div>
            <h2 className="font-semibold text-slate-800 dark:text-white text-base">WFDB ECG Upload Center</h2>
            <p className="text-xs text-slate-500 dark:text-slate-400">Provide paired .hea header and .dat signal files</p>
          </div>
        </div>

        <button
          type="button"
          onClick={loadSampleRecord}
          disabled={isLoading}
          className="inline-flex items-center gap-1.5 text-xs font-medium text-sky-700 dark:text-sky-300 bg-sky-50 dark:bg-sky-950/80 hover:bg-sky-100 dark:hover:bg-sky-900/80 border border-sky-200 dark:border-sky-800 px-3 py-1.5 rounded-lg transition-colors"
        >
          <Database className="w-3.5 h-3.5" />
          <span>Load Sample WFDB Record</span>
        </button>
      </div>

      <div className="p-6 space-y-5">
        {/* 3-Step Workflow Banner */}
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 text-xs font-semibold bg-slate-50 dark:bg-slate-800/50 p-3 rounded-xl border border-slate-200 dark:border-slate-800">
          <div className="flex items-center gap-2 text-sky-800 dark:text-sky-300">
            <span className="w-5 h-5 rounded-full bg-sky-100 dark:bg-sky-950 text-sky-700 dark:text-sky-300 flex items-center justify-center text-[11px] font-bold">1</span>
            <span>Select .hea Header</span>
          </div>
          <div className="flex items-center gap-2 text-sky-800 dark:text-sky-300">
            <span className="w-5 h-5 rounded-full bg-sky-100 dark:bg-sky-950 text-sky-700 dark:text-sky-300 flex items-center justify-center text-[11px] font-bold">2</span>
            <span>Select Matching .dat Signal</span>
          </div>
          <div className="flex items-center gap-2 text-sky-800 dark:text-sky-300">
            <span className="w-5 h-5 rounded-full bg-sky-100 dark:bg-sky-950 text-sky-700 dark:text-sky-300 flex items-center justify-center text-[11px] font-bold">3</span>
            <span>Analyze ECG</span>
          </div>
        </div>

        <form onSubmit={handleSubmit} className="space-y-6">
          {/* Drag and Drop Zone */}
          <div
            onDragEnter={handleDrag}
            onDragOver={handleDrag}
            onDragLeave={handleDrag}
            onDrop={handleDrop}
            className={`relative border-2 border-dashed rounded-2xl p-8 text-center transition-all duration-200 ${
              dragActive
                ? 'border-sky-500 bg-sky-50/80 dark:bg-sky-950/80 scale-[1.01]'
                : isReady
                ? 'border-emerald-300 dark:border-emerald-700 bg-emerald-50/30 dark:bg-emerald-950/20'
                : 'border-slate-300 dark:border-slate-700 bg-slate-50/50 dark:bg-slate-800/40 hover:border-sky-400 dark:hover:border-sky-500'
            }`}
          >
            <div className="flex flex-col items-center justify-center space-y-3">
              <div className={`w-14 h-14 rounded-2xl flex items-center justify-center transition-colors ${
                isReady ? 'bg-emerald-100 dark:bg-emerald-950 text-emerald-600 dark:text-emerald-400' : 'bg-sky-100 dark:bg-sky-950 text-sky-600 dark:text-sky-400'
              }`}>
                {isReady ? <CheckCircle2 className="w-7 h-7" /> : <Upload className="w-7 h-7" />}
              </div>

              <div>
                <p className="text-base font-semibold text-slate-800 dark:text-white">
                  {dragActive ? 'Drop your WFDB files here' : 'Drag & drop paired ECG files here'}
                </p>
                <p className="text-xs text-slate-500 dark:text-slate-400 mt-1">
                  Supports <span className="font-mono font-semibold text-sky-700 dark:text-sky-400">.hea</span> header &{' '}
                  <span className="font-mono font-semibold text-sky-700 dark:text-sky-400">.dat</span> binary signal (must belong to the same record stem)
                </p>
              </div>

              {/* Individual File Pickers */}
              <div className="pt-2 flex flex-wrap items-center justify-center gap-3">
                <input
                  ref={heaInputRef}
                  type="file"
                  accept=".hea"
                  onChange={e => handleFileChange(e, 'hea')}
                  className="hidden"
                />
                <button
                  type="button"
                  onClick={() => heaInputRef.current?.click()}
                  className="px-3.5 py-2 text-xs font-semibold rounded-lg bg-white dark:bg-slate-800 border border-slate-300 dark:border-slate-700 text-slate-700 dark:text-slate-200 hover:bg-slate-100 dark:hover:bg-slate-700 shadow-sm flex items-center gap-2"
                >
                  <FileCode className="w-4 h-4 text-sky-600 dark:text-sky-400" />
                  <span>{files.heaFile ? files.heaFile.name : 'Select .hea File'}</span>
                </button>

                <input
                  ref={datInputRef}
                  type="file"
                  accept=".dat"
                  onChange={e => handleFileChange(e, 'dat')}
                  className="hidden"
                />
                <button
                  type="button"
                  onClick={() => datInputRef.current?.click()}
                  className="px-3.5 py-2 text-xs font-semibold rounded-lg bg-white dark:bg-slate-800 border border-slate-300 dark:border-slate-700 text-slate-700 dark:text-slate-200 hover:bg-slate-100 dark:hover:bg-slate-700 shadow-sm flex items-center gap-2"
                >
                  <Activity className="w-4 h-4 text-indigo-600 dark:text-indigo-400" />
                  <span>{files.datFile ? files.datFile.name : 'Select .dat File'}</span>
                </button>
              </div>
            </div>
          </div>

          {/* Selected File Status Display */}
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            {/* HEA Status */}
            <div className={`p-3.5 rounded-xl border flex items-center justify-between ${
              files.heaFile
                ? 'bg-emerald-50/60 dark:bg-emerald-950/40 border-emerald-200 dark:border-emerald-800 text-emerald-900 dark:text-emerald-200'
                : 'bg-slate-50 dark:bg-slate-800/40 border-slate-200 dark:border-slate-700 text-slate-500 dark:text-slate-400'
            }`}>
              <div className="flex items-center gap-2.5 overflow-hidden">
                <FileCode className={`w-4 h-4 flex-shrink-0 ${files.heaFile ? 'text-emerald-600 dark:text-emerald-400' : 'text-slate-400'}`} />
                <div className="truncate">
                  <p className="text-xs font-bold uppercase tracking-wider text-slate-500 dark:text-slate-400">Header (.hea)</p>
                  <p className="text-xs font-medium truncate">{files.heaFile ? files.heaFile.name : 'No file selected'}</p>
                </div>
              </div>
              {files.heaFile && (
                <button
                  type="button"
                  onClick={() => setFiles(prev => ({ ...prev, heaFile: null }))}
                  className="text-slate-400 hover:text-red-500 transition-colors p-1"
                >
                  <X className="w-4 h-4" />
                </button>
              )}
            </div>

            {/* DAT Status */}
            <div className={`p-3.5 rounded-xl border flex items-center justify-between ${
              files.datFile
                ? 'bg-emerald-50/60 dark:bg-emerald-950/40 border-emerald-200 dark:border-emerald-800 text-emerald-900 dark:text-emerald-200'
                : 'bg-slate-50 dark:bg-slate-800/40 border-slate-200 dark:border-slate-700 text-slate-500 dark:text-slate-400'
            }`}>
              <div className="flex items-center gap-2.5 overflow-hidden">
                <Activity className={`w-4 h-4 flex-shrink-0 ${files.datFile ? 'text-emerald-600 dark:text-emerald-400' : 'text-slate-400'}`} />
                <div className="truncate">
                  <p className="text-xs font-bold uppercase tracking-wider text-slate-500 dark:text-slate-400">Signal (.dat)</p>
                  <p className="text-xs font-medium truncate">
                    {files.datFile ? `${files.datFile.name} (${(files.datFile.size / 1024).toFixed(1)} KB)` : 'No file selected'}
                  </p>
                </div>
              </div>
              {files.datFile && (
                <button
                  type="button"
                  onClick={() => setFiles(prev => ({ ...prev, datFile: null }))}
                  className="text-slate-400 hover:text-red-500 transition-colors p-1"
                >
                  <X className="w-4 h-4" />
                </button>
              )}
            </div>
          </div>

          {/* Error Message */}
          {errorMsg && (
            <div className="p-3.5 bg-red-50 dark:bg-red-950/60 border border-red-200 dark:border-red-800 text-red-700 dark:text-red-300 text-xs font-medium rounded-xl flex items-center gap-2">
              <AlertCircle className="w-4 h-4 text-red-500 flex-shrink-0" />
              <span>{errorMsg}</span>
            </div>
          )}

          {/* Submit Button */}
          <button
            type="submit"
            disabled={!isReady || isLoading}
            className={`w-full py-3.5 px-6 rounded-xl text-white font-semibold text-sm shadow-lg flex items-center justify-center gap-2 transition-all duration-200 ${
              isReady && !isLoading
                ? 'bg-gradient-to-r from-sky-600 via-blue-600 to-indigo-700 hover:from-sky-700 hover:to-indigo-800 shadow-sky-500/25 hover:shadow-sky-500/40 hover:scale-[1.01]'
                : 'bg-slate-300 dark:bg-slate-800 dark:text-slate-500 cursor-not-allowed shadow-none'
            }`}
          >
            <span>Analyze ECG & Run Inference</span>
            <ArrowRight className="w-4 h-4" />
          </button>
        </form>
      </div>
    </div>
  );
};
