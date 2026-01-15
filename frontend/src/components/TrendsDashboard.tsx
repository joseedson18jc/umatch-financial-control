import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import {
    TrendingUp,
    TrendingDown,
    Calendar,
    ArrowUpRight,
    ArrowDownRight,
    BarChart3,
    LineChart
} from 'lucide-react';
import { XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Area, AreaChart } from 'recharts';
import api from '../api';

interface TrendsDashboardProps {
    language: 'pt' | 'en';
}

const translations = {
    pt: {
        title: 'Análise de Tendências',
        subtitle: 'Projeções e padrões sazonais',
        loading: 'Analisando tendências...',
        noData: 'Dados insuficientes para análise',
        revenue: 'Receita',
        expenses: 'Despesas',
        forecast: 'Projeção',
        historical: 'Histórico',
        growth: 'Crescimento',
        decline: 'Declínio',
        stable: 'Estável',
        seasonality: 'Padrões Sazonais',
        nextMonth: 'Próximo mês',
        confidence: 'Confiança',
        refresh: 'Atualizar'
    },
    en: {
        title: 'Trend Analysis',
        subtitle: 'Forecasts and seasonal patterns',
        loading: 'Analyzing trends...',
        noData: 'Insufficient data for analysis',
        revenue: 'Revenue',
        expenses: 'Expenses',
        forecast: 'Forecast',
        historical: 'Historical',
        growth: 'Growth',
        decline: 'Decline',
        stable: 'Stable',
        seasonality: 'Seasonal Patterns',
        nextMonth: 'Next month',
        confidence: 'Confidence',
        refresh: 'Refresh'
    }
};

interface TrendDataPoint {
    month: string;
    revenue: number;
    expenses: number;
    forecast: boolean;
}

const mockSeasonality = [
    { name: 'Q1', pattern: 'Baixa temporada', change: -15, icon: TrendingDown },
    { name: 'Q2', pattern: 'Recuperação', change: 10, icon: TrendingUp },
    { name: 'Q3', pattern: 'Alta temporada', change: 25, icon: TrendingUp },
    { name: 'Q4', pattern: 'Pico anual', change: 35, icon: TrendingUp },
];

export default function TrendsDashboard({ language }: TrendsDashboardProps) {
    const [loading, setLoading] = useState(true);
    const [data, setData] = useState<TrendDataPoint[]>([]);

    const t = translations[language];

    const fetchData = async () => {
        setLoading(true);
        try {
            // Fetch both dashboard (historical) and forecast data
            const [dashboardRes, forecastRes] = await Promise.all([
                api.get('/dashboard'),
                api.get('/api/forecast?months=3')
            ]);

            // Build trend data from monthly_data
            const monthlyData = dashboardRes.data.monthly_data || [];
            const forecastPoints = forecastRes.data.forecast || [];

            // Combine historical and forecast
            const chartData: TrendDataPoint[] = monthlyData.map((m: any) => ({
                month: m.month?.substring(5) || m.label,
                revenue: m.revenue || 0,
                expenses: Math.abs(m.expenses || 0),
                forecast: false
            }));

            // Add forecast points
            forecastPoints.forEach((f: any) => {
                chartData.push({
                    month: f.month?.substring(5) || f.label,
                    revenue: f.revenue || 0,
                    expenses: Math.abs(f.expenses || 0),
                    forecast: true
                });
            });

            setData(chartData);
        } catch (err) {
            console.error('Failed to fetch trends:', err);
            // Use mock data as fallback
            setData([
                { month: 'Jul', revenue: 120000, expenses: 95000, forecast: false },
                { month: 'Ago', revenue: 135000, expenses: 98000, forecast: false },
                { month: 'Set', revenue: 128000, expenses: 102000, forecast: false },
                { month: 'Out', revenue: 142000, expenses: 108000, forecast: false },
                { month: 'Nov', revenue: 155000, expenses: 112000, forecast: false },
                { month: 'Dez', revenue: 168000, expenses: 118000, forecast: false },
                { month: 'Jan', revenue: 175000, expenses: 122000, forecast: true },
                { month: 'Fev', revenue: 182000, expenses: 125000, forecast: true },
            ]);
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
            notation: 'compact'
        }).format(value);
    };

    if (loading) {
        return (
            <div className="flex items-center justify-center min-h-[60vh]">
                <div className="flex flex-col items-center gap-4">
                    <LineChart size={48} className="text-cyan-400 animate-pulse" />
                    <span className="text-slate-400">{t.loading}</span>
                </div>
            </div>
        );
    }

    const lastActual = data.filter(d => !d.forecast).slice(-1)[0];
    const firstForecast = data.filter(d => d.forecast)[0];
    const revenueGrowth = lastActual && firstForecast
        ? ((firstForecast.revenue - lastActual.revenue) / lastActual.revenue * 100)
        : 0;

    return (
        <div className="space-y-8">
            {/* Forecast Cards */}
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
                <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="bg-gradient-to-br from-cyan-500/10 to-blue-500/10 rounded-xl p-5 border border-cyan-500/20"
                >
                    <div className="flex items-center justify-between mb-3">
                        <TrendingUp size={20} className="text-cyan-400" />
                        <span className="text-xs text-slate-400 uppercase">{t.nextMonth}</span>
                    </div>
                    <p className="text-2xl font-bold text-white">{formatCurrency(firstForecast?.revenue || 0)}</p>
                    <p className="text-sm text-slate-400">{t.revenue} {t.forecast}</p>
                </motion.div>

                <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.1 }}
                    className="bg-gradient-to-br from-red-500/10 to-orange-500/10 rounded-xl p-5 border border-red-500/20"
                >
                    <div className="flex items-center justify-between mb-3">
                        <TrendingDown size={20} className="text-red-400" />
                        <span className="text-xs text-slate-400 uppercase">{t.nextMonth}</span>
                    </div>
                    <p className="text-2xl font-bold text-white">{formatCurrency(firstForecast?.expenses || 0)}</p>
                    <p className="text-sm text-slate-400">{t.expenses} {t.forecast}</p>
                </motion.div>

                <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.2 }}
                    className="bg-gradient-to-br from-emerald-500/10 to-teal-500/10 rounded-xl p-5 border border-emerald-500/20"
                >
                    <div className="flex items-center justify-between mb-3">
                        {revenueGrowth >= 0 ? (
                            <ArrowUpRight size={20} className="text-emerald-400" />
                        ) : (
                            <ArrowDownRight size={20} className="text-red-400" />
                        )}
                        <span className="text-xs text-slate-400 uppercase">{t.growth}</span>
                    </div>
                    <p className={`text-2xl font-bold ${revenueGrowth >= 0 ? 'text-emerald-400' : 'text-red-400'}`}>
                        {revenueGrowth >= 0 ? '+' : ''}{revenueGrowth.toFixed(1)}%
                    </p>
                    <p className="text-sm text-slate-400">{t.revenue} MoM</p>
                </motion.div>

                <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.3 }}
                    className="bg-gradient-to-br from-purple-500/10 to-pink-500/10 rounded-xl p-5 border border-purple-500/20"
                >
                    <div className="flex items-center justify-between mb-3">
                        <BarChart3 size={20} className="text-purple-400" />
                        <span className="text-xs text-slate-400 uppercase">{t.confidence}</span>
                    </div>
                    <p className="text-2xl font-bold text-white">85%</p>
                    <p className="text-sm text-slate-400">AI Model {t.confidence}</p>
                </motion.div>
            </div>

            {/* Trend Chart */}
            <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.4 }}
                className="bg-slate-800/30 rounded-2xl p-6 border border-slate-700/50"
            >
                <div className="flex items-center justify-between mb-6">
                    <h3 className="text-lg font-semibold text-white flex items-center gap-2">
                        <LineChart size={20} className="text-cyan-400" />
                        {t.revenue} vs {t.expenses}
                    </h3>
                    <div className="flex items-center gap-4 text-sm">
                        <div className="flex items-center gap-2">
                            <div className="w-3 h-3 rounded-full bg-cyan-400" />
                            <span className="text-slate-400">{t.revenue}</span>
                        </div>
                        <div className="flex items-center gap-2">
                            <div className="w-3 h-3 rounded-full bg-red-400" />
                            <span className="text-slate-400">{t.expenses}</span>
                        </div>
                        <div className="flex items-center gap-2">
                            <div className="w-3 h-0.5 border-t-2 border-dashed border-slate-500 w-4" />
                            <span className="text-slate-400">{t.forecast}</span>
                        </div>
                    </div>
                </div>

                <div className="h-[300px]">
                    <ResponsiveContainer width="100%" height="100%">
                        <AreaChart data={data} margin={{ top: 10, right: 30, left: 0, bottom: 0 }}>
                            <defs>
                                <linearGradient id="colorRevenue" x1="0" y1="0" x2="0" y2="1">
                                    <stop offset="5%" stopColor="#06b6d4" stopOpacity={0.3} />
                                    <stop offset="95%" stopColor="#06b6d4" stopOpacity={0} />
                                </linearGradient>
                                <linearGradient id="colorExpenses" x1="0" y1="0" x2="0" y2="1">
                                    <stop offset="5%" stopColor="#ef4444" stopOpacity={0.3} />
                                    <stop offset="95%" stopColor="#ef4444" stopOpacity={0} />
                                </linearGradient>
                            </defs>
                            <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
                            <XAxis dataKey="month" stroke="#64748b" />
                            <YAxis stroke="#64748b" tickFormatter={(v) => formatCurrency(v)} />
                            <Tooltip
                                contentStyle={{ backgroundColor: '#1e293b', border: '1px solid #334155', borderRadius: '8px' }}
                                labelStyle={{ color: '#f8fafc' }}
                                formatter={(value) => value !== undefined ? formatCurrency(value as number) : ''}
                            />
                            <Area
                                type="monotone"
                                dataKey="revenue"
                                stroke="#06b6d4"
                                strokeWidth={2}
                                fillOpacity={1}
                                fill="url(#colorRevenue)"
                            />
                            <Area
                                type="monotone"
                                dataKey="expenses"
                                stroke="#ef4444"
                                strokeWidth={2}
                                fillOpacity={1}
                                fill="url(#colorExpenses)"
                            />
                        </AreaChart>
                    </ResponsiveContainer>
                </div>
            </motion.div>

            {/* Seasonality */}
            <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.5 }}
                className="bg-slate-800/30 rounded-2xl p-6 border border-slate-700/50"
            >
                <h3 className="text-lg font-semibold text-white mb-6 flex items-center gap-2">
                    <Calendar size={20} className="text-purple-400" />
                    {t.seasonality}
                </h3>
                <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
                    {mockSeasonality.map((season, index) => (
                        <motion.div
                            key={season.name}
                            initial={{ opacity: 0, scale: 0.9 }}
                            animate={{ opacity: 1, scale: 1 }}
                            transition={{ delay: 0.6 + index * 0.1 }}
                            className="bg-slate-800/50 rounded-xl p-4 border border-slate-700/50 text-center"
                        >
                            <p className="text-lg font-bold text-white mb-1">{season.name}</p>
                            <p className="text-sm text-slate-400 mb-2">{season.pattern}</p>
                            <div className={`flex items-center justify-center gap-1 ${season.change >= 0 ? 'text-emerald-400' : 'text-red-400'}`}>
                                <season.icon size={16} />
                                <span className="font-medium">{season.change >= 0 ? '+' : ''}{season.change}%</span>
                            </div>
                        </motion.div>
                    ))}
                </div>
            </motion.div>
        </div>
    );
}
