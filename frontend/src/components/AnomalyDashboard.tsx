import { useState, useEffect, useCallback } from 'react';
import { motion } from 'framer-motion';
import {
    AlertTriangle,
    AlertCircle,
    TrendingUp,
    RefreshCw,
    Check,
    Eye,
    XCircle,
    Search
} from 'lucide-react';
import api from '../api';

interface AnomalyDashboardProps {
    language: 'pt' | 'en';
}

const translations = {
    pt: {
        title: 'Detecção de Anomalias',
        subtitle: 'Transações com padrões incomuns',
        loading: 'Analisando transações...',
        noData: 'Nenhuma anomalia detectada',
        investigate: 'Investigar',
        dismiss: 'Dispensar',
        high: 'Alta',
        medium: 'Média',
        low: 'Baixa',
        severity: 'Severidade',
        amount: 'Valor',
        date: 'Data',
        description: 'Descrição',
        reason: 'Motivo',
        search: 'Buscar transações...',
        filters: 'Filtros',
        allSeverities: 'Todas as severidades',
        detected: 'anomalias detectadas',
        totalValue: 'Valor total',
        refresh: 'Atualizar'
    },
    en: {
        title: 'Anomaly Detection',
        subtitle: 'Transactions with unusual patterns',
        loading: 'Analyzing transactions...',
        noData: 'No anomalies detected',
        investigate: 'Investigate',
        dismiss: 'Dismiss',
        high: 'High',
        medium: 'Medium',
        low: 'Low',
        severity: 'Severity',
        amount: 'Amount',
        date: 'Date',
        description: 'Description',
        reason: 'Reason',
        search: 'Search transactions...',
        filters: 'Filters',
        allSeverities: 'All severities',
        detected: 'anomalies detected',
        totalValue: 'Total value',
        refresh: 'Refresh'
    }
};

interface Anomaly {
    id: string;
    date: string;
    description: string;
    amount: number;
    severity: 'high' | 'medium' | 'low';
    reason: string;
    status?: 'pending' | 'investigated' | 'dismissed';
}

// Mock anomalies for fallback
const mockAnomalies: Anomaly[] = [
    {
        id: '1',
        date: '2025-01-10',
        description: 'Pagamento AWS - Valor atípico',
        amount: -15420.00,
        severity: 'high',
        reason: '3x acima da média histórica',
        status: 'pending'
    },
    {
        id: '2',
        date: '2025-01-08',
        description: 'Receita Google Play - Pico incomum',
        amount: 85000.00,
        severity: 'medium',
        reason: '150% acima do período anterior',
        status: 'pending'
    },
    {
        id: '3',
        date: '2025-01-05',
        description: 'Despesa Marketing - Fora do padrão',
        amount: -8500.00,
        severity: 'low',
        reason: 'Categoria sem histórico recente',
        status: 'pending'
    }
];

const SeverityBadge = ({ severity, t }: { severity: string; t: typeof translations.pt }) => {
    const colors = {
        high: 'bg-red-500/10 text-red-400 border-red-500/20',
        medium: 'bg-amber-500/10 text-amber-400 border-amber-500/20',
        low: 'bg-blue-500/10 text-blue-400 border-blue-500/20'
    };
    const labels = { high: t.high, medium: t.medium, low: t.low };

    return (
        <span className={`px-2 py-1 rounded-md text-xs font-medium border ${colors[severity as keyof typeof colors]}`}>
            {labels[severity as keyof typeof labels]}
        </span>
    );
};

export default function AnomalyDashboard({ language }: AnomalyDashboardProps) {
    const [anomalies, setAnomalies] = useState<Anomaly[]>([]);
    const [loading, setLoading] = useState(true);
    const [searchTerm, setSearchTerm] = useState('');
    const [severityFilter, setSeverityFilter] = useState<string>('all');

    const t = translations[language];

    const fetchAnomalies = useCallback(async () => {
        setLoading(true);
        try {
            const response = await api.get(`/api/anomalies${severityFilter !== 'all' ? `?severity=${severityFilter}` : ''}`);
            const data = response.data;
            setAnomalies(data.anomalies || []);
        } catch (err) {
            console.error('Failed to fetch anomalies:', err);
            // Use mock data as fallback
            setAnomalies(mockAnomalies);
        } finally {
            setLoading(false);
        }
    }, [severityFilter]);

    useEffect(() => {
        fetchAnomalies();
    }, [fetchAnomalies]);

    const filteredAnomalies = anomalies.filter(a => {
        const matchesSearch = a.description.toLowerCase().includes(searchTerm.toLowerCase());
        const matchesSeverity = severityFilter === 'all' || a.severity === severityFilter;
        return matchesSearch && matchesSeverity && a.status === 'pending';
    });

    const handleInvestigate = (id: string) => {
        setAnomalies(prev => prev.map(a =>
            a.id === id ? { ...a, status: 'investigated' as const } : a
        ));
    };

    const handleDismiss = (id: string) => {
        setAnomalies(prev => prev.map(a =>
            a.id === id ? { ...a, status: 'dismissed' as const } : a
        ));
    };

    const totalValue = filteredAnomalies.reduce((sum, a) => sum + Math.abs(a.amount), 0);

    const formatCurrency = (value: number) => {
        return new Intl.NumberFormat('pt-BR', {
            style: 'currency',
            currency: 'BRL'
        }).format(value);
    };

    if (loading) {
        return (
            <div className="flex items-center justify-center min-h-[60vh]">
                <div className="flex flex-col items-center gap-4">
                    <AlertTriangle size={48} className="text-amber-400 animate-pulse" />
                    <span className="text-slate-400">{t.loading}</span>
                </div>
            </div>
        );
    }

    return (
        <div className="space-y-6">
            {/* Stats Row */}
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
                <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="bg-slate-800/50 rounded-xl p-5 border border-slate-700/50"
                >
                    <div className="flex items-center gap-3">
                        <AlertCircle size={24} className="text-red-400" />
                        <div>
                            <p className="text-2xl font-bold text-white">{anomalies.filter(a => a.severity === 'high' && a.status === 'pending').length}</p>
                            <p className="text-sm text-slate-400">{t.severity}: {t.high}</p>
                        </div>
                    </div>
                </motion.div>
                <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.1 }}
                    className="bg-slate-800/50 rounded-xl p-5 border border-slate-700/50"
                >
                    <div className="flex items-center gap-3">
                        <AlertTriangle size={24} className="text-amber-400" />
                        <div>
                            <p className="text-2xl font-bold text-white">{filteredAnomalies.length}</p>
                            <p className="text-sm text-slate-400">{t.detected}</p>
                        </div>
                    </div>
                </motion.div>
                <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.2 }}
                    className="bg-slate-800/50 rounded-xl p-5 border border-slate-700/50"
                >
                    <div className="flex items-center gap-3">
                        <TrendingUp size={24} className="text-cyan-400" />
                        <div>
                            <p className="text-2xl font-bold text-white">{formatCurrency(totalValue)}</p>
                            <p className="text-sm text-slate-400">{t.totalValue}</p>
                        </div>
                    </div>
                </motion.div>
            </div>

            {/* Filters */}
            <div className="flex flex-col sm:flex-row gap-4">
                <div className="relative flex-1">
                    <Search size={18} className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-500" />
                    <input
                        type="text"
                        placeholder={t.search}
                        value={searchTerm}
                        onChange={(e) => setSearchTerm(e.target.value)}
                        className="w-full pl-10 pr-4 py-2.5 rounded-lg bg-slate-800/50 border border-slate-700/50 text-white placeholder-slate-500 focus:border-cyan-500/50 focus:outline-none transition-colors"
                        aria-label={t.search}
                    />
                </div>
                <select
                    value={severityFilter}
                    onChange={(e) => setSeverityFilter(e.target.value)}
                    className="px-4 py-2.5 rounded-lg bg-slate-800/50 border border-slate-700/50 text-white focus:border-cyan-500/50 focus:outline-none transition-colors"
                    aria-label={t.filters}
                >
                    <option value="all">{t.allSeverities}</option>
                    <option value="high">{t.high}</option>
                    <option value="medium">{t.medium}</option>
                    <option value="low">{t.low}</option>
                </select>
                <button
                    onClick={fetchAnomalies}
                    className="flex items-center gap-2 px-4 py-2.5 rounded-lg bg-slate-800/50 border border-slate-700/50 text-slate-300 hover:bg-slate-700/50 transition-colors"
                    aria-label="Refresh"
                >
                    <RefreshCw size={18} />
                </button>
            </div>

            {/* Anomaly Cards */}
            {filteredAnomalies.length === 0 ? (
                <motion.div
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    className="flex flex-col items-center justify-center py-16"
                >
                    <Check size={48} className="text-emerald-400 mb-4" />
                    <p className="text-slate-400 text-lg">{t.noData}</p>
                </motion.div>
            ) : (
                <div className="space-y-4">
                    {filteredAnomalies.map((anomaly, index) => (
                        <motion.div
                            key={anomaly.id}
                            initial={{ opacity: 0, x: -20 }}
                            animate={{ opacity: 1, x: 0 }}
                            transition={{ delay: index * 0.1 }}
                            className="bg-slate-800/30 rounded-xl p-5 border border-slate-700/50 hover:border-slate-600/50 transition-colors"
                        >
                            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
                                <div className="flex-1">
                                    <div className="flex items-center gap-3 mb-2">
                                        <SeverityBadge severity={anomaly.severity} t={t} />
                                        <span className="text-slate-500 text-sm">{anomaly.date}</span>
                                    </div>
                                    <h4 className="text-white font-medium mb-1">{anomaly.description}</h4>
                                    <p className="text-slate-400 text-sm">{anomaly.reason}</p>
                                </div>
                                <div className="flex items-center gap-4">
                                    <span className={`text-xl font-bold font-mono ${anomaly.amount >= 0 ? 'text-emerald-400' : 'text-red-400'}`}>
                                        {formatCurrency(anomaly.amount)}
                                    </span>
                                    <div className="flex gap-2">
                                        <button
                                            onClick={() => handleInvestigate(anomaly.id)}
                                            className="p-2 rounded-lg bg-cyan-500/10 text-cyan-400 hover:bg-cyan-500/20 transition-colors"
                                            title={t.investigate}
                                            aria-label={t.investigate}
                                        >
                                            <Eye size={18} />
                                        </button>
                                        <button
                                            onClick={() => handleDismiss(anomaly.id)}
                                            className="p-2 rounded-lg bg-slate-700/50 text-slate-400 hover:bg-slate-600/50 transition-colors"
                                            title={t.dismiss}
                                            aria-label={t.dismiss}
                                        >
                                            <XCircle size={18} />
                                        </button>
                                    </div>
                                </div>
                            </div>
                        </motion.div>
                    ))}
                </div>
            )}
        </div>
    );
}
