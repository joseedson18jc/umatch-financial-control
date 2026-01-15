import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import {
    Shield,
    CheckCircle,
    AlertTriangle,
    Search,
    TrendingUp
} from 'lucide-react';

interface DataQualityProps {
    language: 'pt' | 'en';
}

const translations = {
    pt: {
        title: 'Qualidade de Dados',
        subtitle: 'Análise de integridade dos dados',
        loading: 'Analisando qualidade...',
        overallScore: 'Score Geral',
        excellent: 'Excelente',
        good: 'Bom',
        needsAttention: 'Precisa Atenção',
        critical: 'Crítico',
        completeness: 'Completude',
        accuracy: 'Precisão',
        consistency: 'Consistência',
        timeliness: 'Atualidade',
        issues: 'Problemas Detectados',
        noIssues: 'Nenhum problema detectado',
        fix: 'Corrigir',
        ignore: 'Ignorar',
        refresh: 'Atualizar'
    },
    en: {
        title: 'Data Quality',
        subtitle: 'Data integrity analysis',
        loading: 'Analyzing quality...',
        overallScore: 'Overall Score',
        excellent: 'Excellent',
        good: 'Good',
        needsAttention: 'Needs Attention',
        critical: 'Critical',
        completeness: 'Completeness',
        accuracy: 'Accuracy',
        consistency: 'Consistency',
        timeliness: 'Timeliness',
        issues: 'Detected Issues',
        noIssues: 'No issues detected',
        fix: 'Fix',
        ignore: 'Ignore',
        refresh: 'Refresh'
    }
};

interface QualityMetric {
    id: string;
    label: string;
    score: number;
    status: 'excellent' | 'good' | 'warning' | 'critical';
}

interface QualityIssue {
    id: string;
    type: 'missing' | 'duplicate' | 'invalid' | 'inconsistent';
    field: string;
    count: number;
    severity: 'high' | 'medium' | 'low';
    description: string;
}

const mockMetrics: QualityMetric[] = [
    { id: 'completeness', label: 'Completude', score: 94, status: 'excellent' },
    { id: 'accuracy', label: 'Precisão', score: 87, status: 'good' },
    { id: 'consistency', label: 'Consistência', score: 91, status: 'excellent' },
    { id: 'timeliness', label: 'Atualidade', score: 78, status: 'warning' },
];

const mockIssues: QualityIssue[] = [
    { id: '1', type: 'missing', field: 'categoria', count: 23, severity: 'medium', description: 'Transações sem categoria definida' },
    { id: '2', type: 'duplicate', field: 'descricao', count: 8, severity: 'low', description: 'Possíveis transações duplicadas' },
    { id: '3', type: 'invalid', field: 'data', count: 3, severity: 'high', description: 'Datas em formato inválido' },
    { id: '4', type: 'inconsistent', field: 'valor', count: 5, severity: 'medium', description: 'Valores inconsistentes com padrão' },
];

const getStatusColor = (status: string) => {
    switch (status) {
        case 'excellent': return 'text-emerald-400 bg-emerald-500/10 border-emerald-500/20';
        case 'good': return 'text-cyan-400 bg-cyan-500/10 border-cyan-500/20';
        case 'warning': return 'text-amber-400 bg-amber-500/10 border-amber-500/20';
        case 'critical': return 'text-red-400 bg-red-500/10 border-red-500/20';
        default: return 'text-slate-400 bg-slate-500/10 border-slate-500/20';
    }
};

const getSeverityBadge = (severity: string) => {
    const colors = {
        high: 'bg-red-500/10 text-red-400 border-red-500/20',
        medium: 'bg-amber-500/10 text-amber-400 border-amber-500/20',
        low: 'bg-blue-500/10 text-blue-400 border-blue-500/20'
    };
    const labels = { high: 'Alto', medium: 'Médio', low: 'Baixo' };
    return (
        <span className={`px-2 py-0.5 rounded text-xs font-medium border ${colors[severity as keyof typeof colors]}`}>
            {labels[severity as keyof typeof labels]}
        </span>
    );
};

const MetricCard = ({ metric }: { metric: QualityMetric }) => {
    const Icon = metric.score >= 90 ? CheckCircle : metric.score >= 70 ? TrendingUp : AlertTriangle;

    return (
        <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            className={`rounded-xl p-5 border ${getStatusColor(metric.status)}`}
        >
            <div className="flex items-start justify-between mb-3">
                <Icon size={20} />
                <span className="text-2xl font-bold">{metric.score}%</span>
            </div>
            <p className="text-sm font-medium">{metric.label}</p>
            <div className="mt-3 h-2 bg-slate-800 rounded-full overflow-hidden">
                <motion.div
                    initial={{ width: 0 }}
                    animate={{ width: `${metric.score}%` }}
                    transition={{ duration: 0.8, delay: 0.2 }}
                    className={`h-full rounded-full ${metric.score >= 90 ? 'bg-emerald-500' :
                        metric.score >= 70 ? 'bg-cyan-500' :
                            metric.score >= 50 ? 'bg-amber-500' : 'bg-red-500'
                        }`}
                />
            </div>
        </motion.div>
    );
};

export default function DataQuality({ language }: DataQualityProps) {
    const [loading, setLoading] = useState(true);
    const [metrics, setMetrics] = useState<QualityMetric[]>([]);
    const [issues, setIssues] = useState<QualityIssue[]>(mockIssues);
    const [searchTerm, setSearchTerm] = useState('');

    const t = translations[language];

    useEffect(() => {
        const loadData = async () => {
            setLoading(true);
            await new Promise(resolve => setTimeout(resolve, 1000));
            setMetrics(mockMetrics);
            setLoading(false);
        };
        loadData();
    }, []);

    const overallScore = metrics.length > 0
        ? Math.round(metrics.reduce((acc, m) => acc + m.score, 0) / metrics.length)
        : 0;

    const handleFix = (id: string) => {
        setIssues(prev => prev.filter(i => i.id !== id));
    };

    const handleIgnore = (id: string) => {
        setIssues(prev => prev.filter(i => i.id !== id));
    };

    const filteredIssues = issues.filter(issue =>
        issue.field.toLowerCase().includes(searchTerm.toLowerCase()) ||
        issue.description.toLowerCase().includes(searchTerm.toLowerCase())
    );

    if (loading) {
        return (
            <div className="flex items-center justify-center min-h-[60vh]">
                <div className="flex flex-col items-center gap-4">
                    <Shield size={48} className="text-cyan-400 animate-pulse" />
                    <span className="text-slate-400">{t.loading}</span>
                </div>
            </div>
        );
    }

    return (
        <div className="space-y-8">
            {/* Overall Score */}
            <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                className="bg-gradient-to-r from-slate-800/50 to-slate-900/50 rounded-2xl p-6 border border-slate-700/50"
            >
                <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
                    <div className="flex items-center gap-4">
                        <div className={`w-16 h-16 rounded-2xl flex items-center justify-center ${overallScore >= 85 ? 'bg-emerald-500/20' :
                            overallScore >= 70 ? 'bg-cyan-500/20' : 'bg-amber-500/20'
                            }`}>
                            <Shield size={32} className={
                                overallScore >= 85 ? 'text-emerald-400' :
                                    overallScore >= 70 ? 'text-cyan-400' : 'text-amber-400'
                            } />
                        </div>
                        <div>
                            <p className="text-sm text-slate-400">{t.overallScore}</p>
                            <p className="text-4xl font-bold text-white">{overallScore}%</p>
                        </div>
                    </div>
                    <div className={`px-4 py-2 rounded-lg ${overallScore >= 85 ? 'bg-emerald-500/10 text-emerald-400' :
                        overallScore >= 70 ? 'bg-cyan-500/10 text-cyan-400' : 'bg-amber-500/10 text-amber-400'
                        }`}>
                        {overallScore >= 85 ? t.excellent : overallScore >= 70 ? t.good : t.needsAttention}
                    </div>
                </div>
            </motion.div>

            {/* Metric Cards */}
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
                {metrics.map((metric, index) => (
                    <motion.div
                        key={metric.id}
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ delay: index * 0.1 }}
                    >
                        <MetricCard metric={metric} />
                    </motion.div>
                ))}
            </div>

            {/* Issues Section */}
            <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.4 }}
                className="bg-slate-800/30 rounded-2xl border border-slate-700/50 overflow-hidden"
            >
                <div className="p-4 border-b border-slate-700/50 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
                    <h3 className="text-lg font-semibold text-white flex items-center gap-2">
                        <AlertTriangle size={20} className="text-amber-400" />
                        {t.issues} ({filteredIssues.length})
                    </h3>
                    <div className="relative">
                        <Search size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-500" />
                        <input
                            type="text"
                            placeholder="Buscar..."
                            value={searchTerm}
                            onChange={(e) => setSearchTerm(e.target.value)}
                            className="pl-9 pr-4 py-2 rounded-lg bg-slate-800/50 border border-slate-700/50 text-white text-sm focus:border-cyan-500/50 focus:outline-none"
                            aria-label="Search issues"
                        />
                    </div>
                </div>

                {filteredIssues.length === 0 ? (
                    <div className="p-8 text-center">
                        <CheckCircle size={48} className="text-emerald-400 mx-auto mb-4" />
                        <p className="text-slate-400">{t.noIssues}</p>
                    </div>
                ) : (
                    <div className="divide-y divide-slate-700/30">
                        {filteredIssues.map(issue => (
                            <div key={issue.id} className="p-4 hover:bg-slate-800/30 transition-colors">
                                <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
                                    <div className="flex-1">
                                        <div className="flex items-center gap-2 mb-1">
                                            {getSeverityBadge(issue.severity)}
                                            <span className="text-slate-500 text-sm">{issue.count} registros</span>
                                        </div>
                                        <p className="text-white font-medium">{issue.description}</p>
                                        <p className="text-slate-500 text-sm">Campo: {issue.field}</p>
                                    </div>
                                    <div className="flex gap-2">
                                        <button
                                            onClick={() => handleFix(issue.id)}
                                            className="px-3 py-1.5 rounded-lg bg-cyan-500/10 text-cyan-400 text-sm hover:bg-cyan-500/20 transition-colors"
                                            aria-label={`Fix ${issue.description}`}
                                        >
                                            {t.fix}
                                        </button>
                                        <button
                                            onClick={() => handleIgnore(issue.id)}
                                            className="px-3 py-1.5 rounded-lg bg-slate-700/50 text-slate-400 text-sm hover:bg-slate-600/50 transition-colors"
                                            aria-label={`Ignore ${issue.description}`}
                                        >
                                            {t.ignore}
                                        </button>
                                    </div>
                                </div>
                            </div>
                        ))}
                    </div>
                )}
            </motion.div>
        </div>
    );
}
