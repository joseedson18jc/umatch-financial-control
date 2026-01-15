import { useState } from 'react';
import { motion } from 'framer-motion';
import {
    Wallet,
    Plus,
    TrendingUp,
    TrendingDown,
    AlertTriangle,
    CheckCircle,
    Edit,
    Trash2
} from 'lucide-react';

interface BudgetsProps {
    language: 'pt' | 'en';
}

const translations = {
    pt: {
        title: 'Orçamentos',
        subtitle: 'Planejamento e controle de gastos',
        newBudget: 'Novo Orçamento',
        category: 'Categoria',
        planned: 'Planejado',
        actual: 'Realizado',
        variance: 'Variação',
        status: 'Status',
        onTrack: 'No Alvo',
        overBudget: 'Acima',
        underBudget: 'Abaixo',
        totalBudget: 'Orçamento Total',
        totalSpent: 'Total Gasto',
        remaining: 'Restante'
    },
    en: {
        title: 'Budgets',
        subtitle: 'Spending planning and control',
        newBudget: 'New Budget',
        category: 'Category',
        planned: 'Planned',
        actual: 'Actual',
        variance: 'Variance',
        status: 'Status',
        onTrack: 'On Track',
        overBudget: 'Over',
        underBudget: 'Under',
        totalBudget: 'Total Budget',
        totalSpent: 'Total Spent',
        remaining: 'Remaining'
    }
};

interface Budget {
    id: string;
    category: string;
    planned: number;
    actual: number;
    color: string;
}

const mockBudgets: Budget[] = [
    { id: '1', category: 'Marketing', planned: 15000, actual: 12500, color: 'cyan' },
    { id: '2', category: 'Tecnologia', planned: 25000, actual: 28000, color: 'purple' },
    { id: '3', category: 'Pessoal', planned: 80000, actual: 78500, color: 'emerald' },
    { id: '4', category: 'Infraestrutura', planned: 10000, actual: 9200, color: 'amber' },
    { id: '5', category: 'Administrativo', planned: 8000, actual: 7800, color: 'blue' },
];

const getVarianceStatus = (planned: number, actual: number) => {
    const variance = ((actual - planned) / planned) * 100;
    if (variance > 10) return 'over';
    if (variance < -10) return 'under';
    return 'onTrack';
};

export default function Budgets({ language }: BudgetsProps) {
    const [budgets, setBudgets] = useState<Budget[]>(mockBudgets);

    const t = translations[language];

    const formatCurrency = (value: number) => {
        return new Intl.NumberFormat('pt-BR', {
            style: 'currency',
            currency: 'BRL',
            minimumFractionDigits: 0,
            maximumFractionDigits: 0
        }).format(value);
    };

    const totalPlanned = budgets.reduce((acc, b) => acc + b.planned, 0);
    const totalActual = budgets.reduce((acc, b) => acc + b.actual, 0);
    const totalRemaining = totalPlanned - totalActual;

    const handleDelete = (id: string) => {
        setBudgets(prev => prev.filter(b => b.id !== id));
    };

    return (
        <div className="space-y-6">
            {/* Summary Cards */}
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
                <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="bg-gradient-to-br from-cyan-500/10 to-blue-500/10 rounded-xl p-5 border border-cyan-500/20"
                >
                    <Wallet size={20} className="text-cyan-400 mb-2" />
                    <p className="text-2xl font-bold text-white">{formatCurrency(totalPlanned)}</p>
                    <p className="text-sm text-slate-400">{t.totalBudget}</p>
                </motion.div>
                <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.1 }}
                    className="bg-gradient-to-br from-purple-500/10 to-pink-500/10 rounded-xl p-5 border border-purple-500/20"
                >
                    <TrendingDown size={20} className="text-purple-400 mb-2" />
                    <p className="text-2xl font-bold text-white">{formatCurrency(totalActual)}</p>
                    <p className="text-sm text-slate-400">{t.totalSpent}</p>
                </motion.div>
                <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.2 }}
                    className={`rounded-xl p-5 border ${totalRemaining >= 0
                        ? 'bg-gradient-to-br from-emerald-500/10 to-teal-500/10 border-emerald-500/20'
                        : 'bg-gradient-to-br from-red-500/10 to-orange-500/10 border-red-500/20'
                        }`}
                >
                    {totalRemaining >= 0 ? (
                        <TrendingUp size={20} className="text-emerald-400 mb-2" />
                    ) : (
                        <AlertTriangle size={20} className="text-red-400 mb-2" />
                    )}
                    <p className={`text-2xl font-bold ${totalRemaining >= 0 ? 'text-emerald-400' : 'text-red-400'}`}>
                        {formatCurrency(Math.abs(totalRemaining))}
                    </p>
                    <p className="text-sm text-slate-400">{t.remaining}</p>
                </motion.div>
            </div>

            {/* New Budget Button */}
            <div className="flex justify-end">
                <button className="flex items-center gap-2 px-4 py-2 rounded-lg bg-gradient-to-r from-cyan-500 to-blue-500 text-white font-medium hover:shadow-lg hover:shadow-cyan-500/30 transition-all">
                    <Plus size={18} />
                    <span>{t.newBudget}</span>
                </button>
            </div>

            {/* Budget Table */}
            <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.3 }}
                className="bg-slate-800/30 rounded-2xl border border-slate-700/50 overflow-hidden"
            >
                <div className="overflow-x-auto">
                    <table className="w-full text-sm">
                        <thead className="bg-slate-800/80">
                            <tr>
                                <th className="py-4 px-4 text-left text-slate-400 font-semibold">{t.category}</th>
                                <th className="py-4 px-4 text-right text-slate-400 font-semibold">{t.planned}</th>
                                <th className="py-4 px-4 text-right text-slate-400 font-semibold">{t.actual}</th>
                                <th className="py-4 px-4 text-center text-slate-400 font-semibold">Progresso</th>
                                <th className="py-4 px-4 text-center text-slate-400 font-semibold">{t.status}</th>
                                <th className="py-4 px-4 text-center text-slate-400 font-semibold">Ações</th>
                            </tr>
                        </thead>
                        <tbody>
                            {budgets.map(budget => {
                                const status = getVarianceStatus(budget.planned, budget.actual);
                                const progress = Math.min((budget.actual / budget.planned) * 100, 100);
                                const variance = budget.actual - budget.planned;

                                return (
                                    <tr key={budget.id} className="border-t border-slate-700/30 hover:bg-slate-800/30">
                                        <td className="py-4 px-4">
                                            <div className="flex items-center gap-3">
                                                <div className={`w-3 h-3 rounded-full bg-${budget.color}-400`} />
                                                <span className="text-white font-medium">{budget.category}</span>
                                            </div>
                                        </td>
                                        <td className="py-4 px-4 text-right text-slate-300 font-mono">
                                            {formatCurrency(budget.planned)}
                                        </td>
                                        <td className="py-4 px-4 text-right font-mono">
                                            <span className={variance > 0 ? 'text-red-400' : 'text-emerald-400'}>
                                                {formatCurrency(budget.actual)}
                                            </span>
                                        </td>
                                        <td className="py-4 px-4">
                                            <div className="w-full h-2 bg-slate-700 rounded-full overflow-hidden">
                                                <div
                                                    className={`h-full rounded-full transition-all ${progress > 100 ? 'bg-red-500' : progress > 80 ? 'bg-amber-500' : 'bg-emerald-500'
                                                        } ${progress >= 100 ? 'w-full' :
                                                            progress >= 90 ? 'w-[90%]' :
                                                                progress >= 80 ? 'w-[80%]' :
                                                                    progress >= 70 ? 'w-[70%]' :
                                                                        progress >= 60 ? 'w-[60%]' :
                                                                            progress >= 50 ? 'w-[50%]' :
                                                                                progress >= 40 ? 'w-[40%]' :
                                                                                    progress >= 30 ? 'w-[30%]' :
                                                                                        progress >= 20 ? 'w-[20%]' :
                                                                                            progress >= 10 ? 'w-[10%]' : 'w-[5%]'
                                                        }`}
                                                />
                                            </div>
                                            <p className="text-xs text-slate-500 mt-1 text-center">{progress.toFixed(0)}%</p>
                                        </td>
                                        <td className="py-4 px-4 text-center">
                                            {status === 'onTrack' && (
                                                <span className="inline-flex items-center gap-1 px-2 py-1 rounded-md bg-emerald-500/10 text-emerald-400 text-xs">
                                                    <CheckCircle size={12} />
                                                    {t.onTrack}
                                                </span>
                                            )}
                                            {status === 'over' && (
                                                <span className="inline-flex items-center gap-1 px-2 py-1 rounded-md bg-red-500/10 text-red-400 text-xs">
                                                    <AlertTriangle size={12} />
                                                    {t.overBudget}
                                                </span>
                                            )}
                                            {status === 'under' && (
                                                <span className="inline-flex items-center gap-1 px-2 py-1 rounded-md bg-cyan-500/10 text-cyan-400 text-xs">
                                                    <TrendingDown size={12} />
                                                    {t.underBudget}
                                                </span>
                                            )}
                                        </td>
                                        <td className="py-4 px-4">
                                            <div className="flex justify-center gap-2">
                                                <button
                                                    className="p-1.5 rounded-lg hover:bg-slate-700/50 text-slate-400 hover:text-white transition-colors"
                                                    aria-label={`Edit ${budget.category}`}
                                                >
                                                    <Edit size={16} />
                                                </button>
                                                <button
                                                    onClick={() => handleDelete(budget.id)}
                                                    className="p-1.5 rounded-lg hover:bg-red-500/20 text-slate-400 hover:text-red-400 transition-colors"
                                                    aria-label={`Delete ${budget.category}`}
                                                >
                                                    <Trash2 size={16} />
                                                </button>
                                            </div>
                                        </td>
                                    </tr>
                                );
                            })}
                        </tbody>
                    </table>
                </div>
            </motion.div>
        </div>
    );
}
