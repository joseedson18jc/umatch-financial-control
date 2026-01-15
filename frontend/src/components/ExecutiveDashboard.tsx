import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import {
    TrendingUp,
    TrendingDown,
    DollarSign,
    PieChart,
    Activity,
    ArrowUpRight,
    ArrowDownRight,
    RefreshCw,
    Calendar
} from 'lucide-react';
import api from '../api';

interface ExecutiveDashboardProps {
    language: 'pt' | 'en';
}

const translations = {
    pt: {
        title: 'Visão Executiva',
        lastUpdate: 'Última atualização',
        revenue: 'Receita Total',
        expenses: 'Despesas Totais',
        netResult: 'Resultado Líquido',
        grossMargin: 'Margem Bruta',
        vsLastMonth: 'vs mês anterior',
        positive: 'Positivo',
        negative: 'Negativo',
        loading: 'Carregando...',
        noData: 'Nenhum dado disponível',
        refresh: 'Atualizar',
        period: 'Período'
    },
    en: {
        title: 'Executive View',
        lastUpdate: 'Last update',
        revenue: 'Total Revenue',
        expenses: 'Total Expenses',
        netResult: 'Net Result',
        grossMargin: 'Gross Margin',
        vsLastMonth: 'vs last month',
        positive: 'Positive',
        negative: 'Negative',
        loading: 'Loading...',
        noData: 'No data available',
        refresh: 'Refresh',
        period: 'Period'
    }
};

interface KPICardProps {
    icon: React.ElementType;
    label: string;
    value: string;
    change?: number;
    vsLabel: string;
    positive?: boolean;
    delay?: number;
}

const KPICard = ({ icon: Icon, label, value, change, vsLabel, positive, delay = 0 }: KPICardProps) => (
    <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.4, delay }}
        className="bg-gradient-to-br from-slate-800/80 to-slate-900/80 rounded-2xl p-6 border border-slate-700/50 backdrop-blur-sm"
    >
        <div className="flex items-start justify-between mb-4">
            <div className={`w-12 h-12 rounded-xl flex items-center justify-center ${positive === undefined
                    ? 'bg-cyan-500/10 text-cyan-400'
                    : positive
                        ? 'bg-emerald-500/10 text-emerald-400'
                        : 'bg-red-500/10 text-red-400'
                }`}>
                <Icon size={24} />
            </div>
            {change !== undefined && (
                <div className={`flex items-center gap-1 text-sm font-medium ${change >= 0 ? 'text-emerald-400' : 'text-red-400'
                    }`}>
                    {change >= 0 ? <ArrowUpRight size={16} /> : <ArrowDownRight size={16} />}
                    <span>{Math.abs(change).toFixed(1)}%</span>
                </div>
            )}
        </div>
        <p className="text-slate-400 text-sm mb-1">{label}</p>
        <p className="text-2xl sm:text-3xl font-bold text-white">{value}</p>
        {change !== undefined && (
            <p className="text-xs text-slate-500 mt-2">{vsLabel}</p>
        )}
    </motion.div>
);

export default function ExecutiveDashboard({ language }: ExecutiveDashboardProps) {
    const [data, setData] = useState<any>(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    const t = translations[language];

    const fetchData = async () => {
        setLoading(true);
        setError(null);
        try {
            const response = await api.get('/api/dashboard');
            setData(response.data);
        } catch (err) {
            console.error('Failed to fetch dashboard data:', err);
            setError('Failed to load data');
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchData();
    }, []);

    const formatCurrency = (value: number) => {
        return new Intl.NumberFormat('pt-BR', {
            style: 'currency',
            currency: 'BRL',
            minimumFractionDigits: 0,
            maximumFractionDigits: 0
        }).format(value);
    };

    const formatPercent = (value: number) => {
        return `${(value * 100).toFixed(1)}%`;
    };

    if (loading) {
        return (
            <div className="flex items-center justify-center min-h-[60vh]">
                <div className="flex items-center gap-3 text-slate-400">
                    <RefreshCw size={24} className="animate-spin" />
                    <span>{t.loading}</span>
                </div>
            </div>
        );
    }

    if (error || !data) {
        return (
            <div className="flex flex-col items-center justify-center min-h-[60vh] text-center">
                <Activity size={48} className="text-slate-600 mb-4" />
                <p className="text-slate-400 text-lg">{t.noData}</p>
                <button
                    onClick={fetchData}
                    className="mt-4 flex items-center gap-2 px-4 py-2 rounded-lg bg-cyan-500/10 border border-cyan-500/20 text-cyan-400 hover:bg-cyan-500/20 transition-all"
                >
                    <RefreshCw size={16} />
                    <span>{t.refresh}</span>
                </button>
            </div>
        );
    }

    const kpis = data.kpis || {};

    // Calculate changes (mock for now - could be from API)
    const revenueChange = kpis.revenue_change || 5.2;
    const expensesChange = kpis.expenses_change || -3.1;
    const netChange = kpis.net_change || 12.5;

    return (
        <div className="space-y-8">
            {/* Header with period selector */}
            <motion.div
                initial={{ opacity: 0, y: -10 }}
                animate={{ opacity: 1, y: 0 }}
                className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4"
            >
                <div className="flex items-center gap-3">
                    <Calendar size={20} className="text-slate-500" />
                    <span className="text-slate-400">{t.period}: YTD 2025</span>
                </div>
                <button
                    onClick={fetchData}
                    className="flex items-center gap-2 px-4 py-2 rounded-lg bg-slate-800 border border-slate-700 text-slate-300 hover:bg-slate-700 transition-all text-sm"
                    aria-label={t.refresh}
                >
                    <RefreshCw size={16} />
                    <span>{t.refresh}</span>
                </button>
            </motion.div>

            {/* KPI Cards Grid */}
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 sm:gap-6">
                <KPICard
                    icon={TrendingUp}
                    label={t.revenue}
                    value={formatCurrency(kpis.total_revenue || 0)}
                    change={revenueChange}
                    vsLabel={t.vsLastMonth}
                    positive={revenueChange >= 0}
                    delay={0}
                />
                <KPICard
                    icon={TrendingDown}
                    label={t.expenses}
                    value={formatCurrency(Math.abs(kpis.total_expenses || 0))}
                    change={expensesChange}
                    vsLabel={t.vsLastMonth}
                    positive={expensesChange <= 0}
                    delay={0.1}
                />
                <KPICard
                    icon={DollarSign}
                    label={t.netResult}
                    value={formatCurrency(kpis.net_result || 0)}
                    change={netChange}
                    vsLabel={t.vsLastMonth}
                    positive={(kpis.net_result || 0) >= 0}
                    delay={0.2}
                />
                <KPICard
                    icon={PieChart}
                    label={t.grossMargin}
                    value={formatPercent(kpis.gross_margin || 0)}
                    vsLabel={t.vsLastMonth}
                    delay={0.3}
                />
            </div>

            {/* Quick Stats */}
            <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.4, delay: 0.4 }}
                className="bg-gradient-to-r from-slate-800/50 to-slate-900/50 rounded-2xl p-6 border border-slate-700/50"
            >
                <h3 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
                    <Activity size={20} className="text-cyan-400" />
                    AI Insights
                </h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div className="p-4 rounded-xl bg-slate-800/50 border border-slate-700/50">
                        <p className="text-sm text-slate-400 mb-2">Análise Automática</p>
                        <p className="text-white">
                            {(kpis.net_result || 0) >= 0
                                ? `✅ Resultado positivo de ${formatCurrency(kpis.net_result || 0)} no período.`
                                : `⚠️ Resultado negativo de ${formatCurrency(kpis.net_result || 0)}. Revise as despesas.`
                            }
                        </p>
                    </div>
                    <div className="p-4 rounded-xl bg-slate-800/50 border border-slate-700/50">
                        <p className="text-sm text-slate-400 mb-2">Recomendação</p>
                        <p className="text-white">
                            {(kpis.gross_margin || 0) > 0.3
                                ? '📈 Margem bruta saudável. Mantenha o controle de custos.'
                                : '💡 Considere revisar pricing ou renegociar fornecedores.'
                            }
                        </p>
                    </div>
                </div>
            </motion.div>
        </div>
    );
}
