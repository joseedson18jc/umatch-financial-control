import { useState, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
    Upload,
    Sparkles,
    FileSearch,
    CheckCircle,
    ArrowRight,
    ArrowLeft,
    FileSpreadsheet,
    AlertCircle,
    Loader2,
    Check,
    X
} from 'lucide-react';
import api from '../api';

interface AIImportWizardProps {
    language: 'pt' | 'en';
}

const translations = {
    pt: {
        title: 'Importação Inteligente v2',
        subtitle: 'Importe seus dados financeiros com análise de IA',
        steps: {
            upload: { title: 'Upload', desc: 'Selecione o arquivo' },
            analysis: { title: 'Análise IA', desc: 'Processamento automático' },
            preview: { title: 'Preview', desc: 'Revise os dados' },
            process: { title: 'Processar', desc: 'Finalize a importação' }
        },
        dropzone: 'Arraste ou clique para selecionar',
        formats: 'Formatos suportados: Conta Azul, Omie',
        analyzing: 'Analisando arquivo com IA...',
        detectedColumns: 'Colunas detectadas',
        mapping: 'Mapeamento automático',
        confidence: 'Confiança',
        warnings: 'Avisos',
        process: 'Processar Importação',
        back: 'Voltar',
        next: 'Próximo',
        success: 'Importação Concluída!',
        totalRows: 'Total de linhas',
        mappedRows: 'Linhas mapeadas',
        quality: 'Qualidade'
    },
    en: {
        title: 'Intelligent Import v2',
        subtitle: 'Import your financial data with AI analysis',
        steps: {
            upload: { title: 'Upload', desc: 'Select file' },
            analysis: { title: 'AI Analysis', desc: 'Automatic processing' },
            preview: { title: 'Preview', desc: 'Review data' },
            process: { title: 'Process', desc: 'Finalize import' }
        },
        dropzone: 'Drag or click to select',
        formats: 'Supported formats: Conta Azul, Omie',
        analyzing: 'Analyzing file with AI...',
        detectedColumns: 'Detected columns',
        mapping: 'Automatic mapping',
        confidence: 'Confidence',
        warnings: 'Warnings',
        process: 'Process Import',
        back: 'Back',
        next: 'Next',
        success: 'Import Complete!',
        totalRows: 'Total rows',
        mappedRows: 'Mapped rows',
        quality: 'Quality'
    }
};

type Step = 'upload' | 'analysis' | 'preview' | 'process';
const STEPS: Step[] = ['upload', 'analysis', 'preview', 'process'];

export default function AIImportWizard({ language }: AIImportWizardProps) {
    const [currentStep, setCurrentStep] = useState<Step>('upload');
    const [file, setFile] = useState<File | null>(null);
    const [isLoading, setIsLoading] = useState(false);
    const [analysisResult, setAnalysisResult] = useState<any>(null);
    const [importResult, setImportResult] = useState<any>(null);
    const [error, setError] = useState<string | null>(null);

    const t = translations[language];
    const currentStepIndex = STEPS.indexOf(currentStep);

    const handleFileDrop = useCallback((e: React.DragEvent<HTMLDivElement>) => {
        e.preventDefault();
        const droppedFile = e.dataTransfer.files[0];
        if (droppedFile && droppedFile.name.endsWith('.csv')) {
            setFile(droppedFile);
            setError(null);
        }
    }, []);

    const handleFileSelect = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
        const selectedFile = e.target.files?.[0];
        if (selectedFile) {
            setFile(selectedFile);
            setError(null);
        }
    }, []);

    const analyzeFile = async () => {
        if (!file) return;

        setIsLoading(true);
        setError(null);
        setCurrentStep('analysis');

        try {
            const reader = new FileReader();
            reader.onload = async (e) => {
                const base64 = (e.target?.result as string).split(',')[1];

                try {
                    const response = await api.post('/api/conta-azul/import', {
                        file: base64,
                        apply_mappings: true
                    });

                    setAnalysisResult(response.data);
                    setCurrentStep('preview');
                } catch (err: any) {
                    setError(err.response?.data?.detail || 'Analysis failed');
                    setCurrentStep('upload');
                } finally {
                    setIsLoading(false);
                }
            };
            reader.readAsDataURL(file);
        } catch {
            setError('Failed to read file');
            setIsLoading(false);
            setCurrentStep('upload');
        }
    };

    const processImport = async () => {
        setIsLoading(true);
        setCurrentStep('process');

        // Simulate final processing (data is already imported)
        setTimeout(() => {
            setImportResult(analysisResult);
            setIsLoading(false);
        }, 1500);
    };

    const StepIndicator = ({ step, index }: { step: Step; index: number }) => {
        const isActive = currentStepIndex === index;
        const isComplete = currentStepIndex > index;
        const stepData = t.steps[step];

        return (
            <div className="flex items-center">
                <div className={`flex items-center gap-3 ${isActive ? 'text-white' : isComplete ? 'text-emerald-400' : 'text-slate-500'}`}>
                    <div className={`w-10 h-10 rounded-full flex items-center justify-center font-bold transition-all ${isActive
                        ? 'bg-gradient-to-r from-cyan-500 to-blue-500 text-white shadow-lg shadow-cyan-500/30'
                        : isComplete
                            ? 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/30'
                            : 'bg-slate-800 text-slate-500 border border-slate-700'
                        }`}>
                        {isComplete ? <Check size={18} /> : index + 1}
                    </div>
                    <div className="hidden sm:block">
                        <p className="font-medium text-sm">{stepData.title}</p>
                        <p className="text-xs text-slate-500">{stepData.desc}</p>
                    </div>
                </div>
                {index < STEPS.length - 1 && (
                    <div className={`w-8 sm:w-16 h-0.5 mx-2 sm:mx-4 ${isComplete ? 'bg-emerald-500' : 'bg-slate-700'
                        }`} />
                )}
            </div>
        );
    };

    return (
        <div className="max-w-4xl mx-auto">
            {/* Step Indicators */}
            <div className="flex items-center justify-center mb-12">
                {STEPS.map((step, index) => (
                    <StepIndicator key={step} step={step} index={index} />
                ))}
            </div>

            {/* Error Display */}
            <AnimatePresence>
                {error && (
                    <motion.div
                        initial={{ opacity: 0, y: -10 }}
                        animate={{ opacity: 1, y: 0 }}
                        exit={{ opacity: 0, y: -10 }}
                        className="mb-6 p-4 rounded-xl bg-red-500/10 border border-red-500/20 flex items-center gap-3 text-red-400"
                    >
                        <AlertCircle size={20} />
                        <span>{error}</span>
                        <button onClick={() => setError(null)} className="ml-auto hover:text-white" aria-label="Close error">
                            <X size={18} />
                        </button>
                    </motion.div>
                )}
            </AnimatePresence>

            {/* Step Content */}
            <AnimatePresence mode="wait">
                {/* Step 1: Upload */}
                {currentStep === 'upload' && (
                    <motion.div
                        key="upload"
                        initial={{ opacity: 0, x: 20 }}
                        animate={{ opacity: 1, x: 0 }}
                        exit={{ opacity: 0, x: -20 }}
                    >
                        <div
                            onDrop={handleFileDrop}
                            onDragOver={(e) => e.preventDefault()}
                            className={`border-2 border-dashed rounded-2xl p-12 text-center transition-all cursor-pointer ${file
                                ? 'border-emerald-500/50 bg-emerald-500/5'
                                : 'border-slate-700 hover:border-cyan-500/50 hover:bg-cyan-500/5'
                                }`}
                            onClick={() => document.getElementById('file-input')?.click()}
                        >
                            <input
                                id="file-input"
                                type="file"
                                accept=".csv"
                                onChange={handleFileSelect}
                                className="hidden"
                                aria-label="Select CSV file"
                            />

                            {file ? (
                                <div className="flex flex-col items-center gap-4">
                                    <div className="w-16 h-16 rounded-2xl bg-emerald-500/10 flex items-center justify-center">
                                        <FileSpreadsheet size={32} className="text-emerald-400" />
                                    </div>
                                    <div>
                                        <p className="text-lg font-semibold text-white">{file.name}</p>
                                        <p className="text-sm text-slate-400">{(file.size / 1024).toFixed(1)} KB</p>
                                    </div>
                                </div>
                            ) : (
                                <div className="flex flex-col items-center gap-4">
                                    <div className="w-20 h-20 rounded-2xl bg-gradient-to-br from-cyan-500/10 to-blue-500/10 border border-cyan-500/20 flex items-center justify-center">
                                        <Upload size={36} className="text-cyan-400" />
                                    </div>
                                    <div>
                                        <p className="text-lg text-white font-medium">{t.dropzone}</p>
                                        <p className="text-sm text-slate-500 mt-1">{t.formats}</p>
                                    </div>
                                </div>
                            )}
                        </div>

                        {file && (
                            <motion.div
                                initial={{ opacity: 0, y: 10 }}
                                animate={{ opacity: 1, y: 0 }}
                                className="mt-8 flex justify-end"
                            >
                                <button
                                    onClick={analyzeFile}
                                    className="flex items-center gap-2 px-6 py-3 rounded-xl bg-gradient-to-r from-cyan-500 to-blue-500 text-white font-semibold hover:shadow-lg hover:shadow-cyan-500/30 transition-all"
                                >
                                    <Sparkles size={20} />
                                    <span>{t.next}</span>
                                    <ArrowRight size={18} />
                                </button>
                            </motion.div>
                        )}
                    </motion.div>
                )}

                {/* Step 2: Analysis */}
                {currentStep === 'analysis' && isLoading && (
                    <motion.div
                        key="analysis"
                        initial={{ opacity: 0, x: 20 }}
                        animate={{ opacity: 1, x: 0 }}
                        exit={{ opacity: 0, x: -20 }}
                        className="flex flex-col items-center justify-center py-16"
                    >
                        <div className="w-24 h-24 rounded-3xl bg-gradient-to-br from-purple-500/20 to-pink-500/20 border border-purple-500/20 flex items-center justify-center mb-8">
                            <Sparkles size={48} className="text-purple-400 animate-pulse" />
                        </div>
                        <h3 className="text-2xl font-bold text-white mb-2">{t.analyzing}</h3>
                        <div className="flex items-center gap-2 text-slate-400">
                            <Loader2 size={20} className="animate-spin" />
                            <span>AI Processing...</span>
                        </div>
                    </motion.div>
                )}

                {/* Step 3: Preview */}
                {currentStep === 'preview' && analysisResult && (
                    <motion.div
                        key="preview"
                        initial={{ opacity: 0, x: 20 }}
                        animate={{ opacity: 1, x: 0 }}
                        exit={{ opacity: 0, x: -20 }}
                    >
                        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
                            <div className="bg-slate-800/50 rounded-xl p-6 border border-slate-700/50">
                                <FileSearch size={24} className="text-cyan-400 mb-3" />
                                <p className="text-2xl font-bold text-white">{analysisResult.total_rows}</p>
                                <p className="text-sm text-slate-400">{t.totalRows}</p>
                            </div>
                            <div className="bg-slate-800/50 rounded-xl p-6 border border-slate-700/50">
                                <CheckCircle size={24} className="text-emerald-400 mb-3" />
                                <p className="text-2xl font-bold text-white">{analysisResult.mapped_count}</p>
                                <p className="text-sm text-slate-400">{t.mappedRows}</p>
                            </div>
                            <div className="bg-slate-800/50 rounded-xl p-6 border border-slate-700/50">
                                <Sparkles size={24} className="text-purple-400 mb-3" />
                                <p className="text-2xl font-bold text-white">{analysisResult.quality_score}</p>
                                <p className="text-sm text-slate-400">{t.quality}</p>
                            </div>
                        </div>

                        {/* Warnings */}
                        {analysisResult.plan_summary?.warnings?.length > 0 && (
                            <div className="mb-8 p-4 rounded-xl bg-amber-500/10 border border-amber-500/20">
                                <h4 className="font-semibold text-amber-400 mb-2 flex items-center gap-2">
                                    <AlertCircle size={18} />
                                    {t.warnings}
                                </h4>
                                <ul className="text-sm text-amber-200/80 space-y-1">
                                    {analysisResult.plan_summary.warnings.map((w: string, i: number) => (
                                        <li key={i}>• {w}</li>
                                    ))}
                                </ul>
                            </div>
                        )}

                        {/* Preview Table */}
                        <div className="bg-slate-800/30 rounded-xl border border-slate-700/50 overflow-hidden mb-8">
                            <div className="p-4 border-b border-slate-700/50">
                                <h4 className="font-semibold text-white">Preview (primeiras 5 transações)</h4>
                            </div>
                            <div className="overflow-x-auto">
                                <table className="w-full text-sm">
                                    <thead className="bg-slate-800/50">
                                        <tr>
                                            <th className="px-4 py-3 text-left text-slate-400 font-medium">Data</th>
                                            <th className="px-4 py-3 text-left text-slate-400 font-medium">Descrição</th>
                                            <th className="px-4 py-3 text-right text-slate-400 font-medium">Valor</th>
                                        </tr>
                                    </thead>
                                    <tbody>
                                        {analysisResult.transactions?.slice(0, 5).map((tx: any, i: number) => (
                                            <tr key={i} className="border-t border-slate-700/50">
                                                <td className="px-4 py-3 text-slate-300">{tx.date}</td>
                                                <td className="px-4 py-3 text-slate-300 truncate max-w-[200px]">{tx.description}</td>
                                                <td className={`px-4 py-3 text-right font-mono ${tx.amount >= 0 ? 'text-emerald-400' : 'text-red-400'}`}>
                                                    R$ {tx.amount?.toLocaleString('pt-BR', { minimumFractionDigits: 2 })}
                                                </td>
                                            </tr>
                                        ))}
                                    </tbody>
                                </table>
                            </div>
                        </div>

                        <div className="flex justify-between">
                            <button
                                onClick={() => setCurrentStep('upload')}
                                className="flex items-center gap-2 px-6 py-3 rounded-xl bg-slate-800 text-slate-300 hover:bg-slate-700 transition-all"
                            >
                                <ArrowLeft size={18} />
                                <span>{t.back}</span>
                            </button>
                            <button
                                onClick={processImport}
                                className="flex items-center gap-2 px-6 py-3 rounded-xl bg-gradient-to-r from-emerald-500 to-teal-500 text-white font-semibold hover:shadow-lg hover:shadow-emerald-500/30 transition-all"
                            >
                                <CheckCircle size={20} />
                                <span>{t.process}</span>
                            </button>
                        </div>
                    </motion.div>
                )}

                {/* Step 4: Process Complete */}
                {currentStep === 'process' && (
                    <motion.div
                        key="process"
                        initial={{ opacity: 0, x: 20 }}
                        animate={{ opacity: 1, x: 0 }}
                        exit={{ opacity: 0, x: -20 }}
                        className="flex flex-col items-center justify-center py-16"
                    >
                        {isLoading ? (
                            <>
                                <Loader2 size={48} className="text-cyan-400 animate-spin mb-6" />
                                <p className="text-lg text-slate-400">Finalizando importação...</p>
                            </>
                        ) : importResult ? (
                            <>
                                <div className="w-24 h-24 rounded-full bg-emerald-500/20 flex items-center justify-center mb-8">
                                    <CheckCircle size={48} className="text-emerald-400" />
                                </div>
                                <h3 className="text-3xl font-bold text-white mb-4">{t.success}</h3>
                                <div className="grid grid-cols-3 gap-8 text-center">
                                    <div>
                                        <p className="text-3xl font-bold text-cyan-400">{importResult.total_rows}</p>
                                        <p className="text-sm text-slate-400">{t.totalRows}</p>
                                    </div>
                                    <div>
                                        <p className="text-3xl font-bold text-emerald-400">{importResult.mapped_count}</p>
                                        <p className="text-sm text-slate-400">{t.mappedRows}</p>
                                    </div>
                                    <div>
                                        <p className="text-3xl font-bold text-purple-400">{importResult.quality_score}</p>
                                        <p className="text-sm text-slate-400">{t.quality}</p>
                                    </div>
                                </div>
                            </>
                        ) : null}
                    </motion.div>
                )}
            </AnimatePresence>
        </div>
    );
}
