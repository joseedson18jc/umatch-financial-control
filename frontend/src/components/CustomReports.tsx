import { useState } from 'react';
import { motion } from 'framer-motion';
import {
    FileText,
    Plus,
    Download,
    Trash2,
    Calendar,
    BarChart3,
    PieChart,
    TrendingUp,
    Clock,
    Play
} from 'lucide-react';

interface CustomReportsProps {
    language: 'pt' | 'en';
}

const translations = {
    pt: {
        title: 'Relatórios Personalizados',
        subtitle: 'Crie e gerencie seus relatórios',
        newReport: 'Novo Relatório',
        myReports: 'Meus Relatórios',
        templates: 'Templates',
        noReports: 'Nenhum relatório criado',
        createFirst: 'Crie seu primeiro relatório personalizado',
        lastRun: 'Última execução',
        run: 'Executar',
        download: 'Baixar',
        delete: 'Excluir',
        schedule: 'Agendar'
    },
    en: {
        title: 'Custom Reports',
        subtitle: 'Create and manage your reports',
        newReport: 'New Report',
        myReports: 'My Reports',
        templates: 'Templates',
        noReports: 'No reports created',
        createFirst: 'Create your first custom report',
        lastRun: 'Last run',
        run: 'Run',
        download: 'Download',
        delete: 'Delete',
        schedule: 'Schedule'
    }
};

interface Report {
    id: string;
    name: string;
    type: 'bar' | 'pie' | 'line';
    lastRun: string;
    scheduled: boolean;
}

interface Template {
    id: string;
    name: string;
    description: string;
    icon: React.ElementType;
}

const mockReports: Report[] = [
    { id: '1', name: 'Receitas por Categoria', type: 'pie', lastRun: '2025-01-14', scheduled: true },
    { id: '2', name: 'Evolução Mensal de Despesas', type: 'line', lastRun: '2025-01-13', scheduled: false },
    { id: '3', name: 'Top 10 Fornecedores', type: 'bar', lastRun: '2025-01-10', scheduled: true },
];

const templates: Template[] = [
    { id: 't1', name: 'Análise de Receitas', description: 'Breakdown por categoria e período', icon: PieChart },
    { id: 't2', name: 'Fluxo de Caixa', description: 'Projeção de entradas e saídas', icon: TrendingUp },
    { id: 't3', name: 'Comparativo Mensal', description: 'Compare meses lado a lado', icon: BarChart3 },
];

const getTypeIcon = (type: string) => {
    switch (type) {
        case 'pie': return PieChart;
        case 'line': return TrendingUp;
        case 'bar': return BarChart3;
        default: return FileText;
    }
};

export default function CustomReports({ language }: CustomReportsProps) {
    const [reports, setReports] = useState<Report[]>(mockReports);
    const [activeTab, setActiveTab] = useState<'reports' | 'templates'>('reports');

    const t = translations[language];

    const handleDelete = (id: string) => {
        setReports(prev => prev.filter(r => r.id !== id));
    };

    const handleRun = (id: string) => {
        // Simulate running report
        setReports(prev => prev.map(r =>
            r.id === id ? { ...r, lastRun: new Date().toISOString().split('T')[0] } : r
        ));
    };

    return (
        <div className="space-y-6">
            {/* Header */}
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
                <div className="flex gap-2">
                    <button
                        onClick={() => setActiveTab('reports')}
                        className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${activeTab === 'reports'
                                ? 'bg-cyan-500/10 text-cyan-400 border border-cyan-500/20'
                                : 'text-slate-400 hover:text-white hover:bg-slate-800'
                            }`}
                    >
                        {t.myReports}
                    </button>
                    <button
                        onClick={() => setActiveTab('templates')}
                        className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${activeTab === 'templates'
                                ? 'bg-cyan-500/10 text-cyan-400 border border-cyan-500/20'
                                : 'text-slate-400 hover:text-white hover:bg-slate-800'
                            }`}
                    >
                        {t.templates}
                    </button>
                </div>
                <button className="flex items-center gap-2 px-4 py-2 rounded-lg bg-gradient-to-r from-cyan-500 to-blue-500 text-white font-medium hover:shadow-lg hover:shadow-cyan-500/30 transition-all">
                    <Plus size={18} />
                    <span>{t.newReport}</span>
                </button>
            </div>

            {/* Reports Tab */}
            {activeTab === 'reports' && (
                <div className="space-y-4">
                    {reports.length === 0 ? (
                        <motion.div
                            initial={{ opacity: 0 }}
                            animate={{ opacity: 1 }}
                            className="flex flex-col items-center justify-center py-16 bg-slate-800/30 rounded-2xl border border-slate-700/50"
                        >
                            <FileText size={48} className="text-slate-600 mb-4" />
                            <p className="text-slate-400 text-lg">{t.noReports}</p>
                            <p className="text-slate-500 text-sm">{t.createFirst}</p>
                        </motion.div>
                    ) : (
                        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                            {reports.map((report, index) => {
                                const TypeIcon = getTypeIcon(report.type);
                                return (
                                    <motion.div
                                        key={report.id}
                                        initial={{ opacity: 0, y: 20 }}
                                        animate={{ opacity: 1, y: 0 }}
                                        transition={{ delay: index * 0.1 }}
                                        className="bg-slate-800/30 rounded-xl p-5 border border-slate-700/50 hover:border-slate-600/50 transition-colors"
                                    >
                                        <div className="flex items-start justify-between mb-4">
                                            <div className="w-10 h-10 rounded-lg bg-cyan-500/10 flex items-center justify-center">
                                                <TypeIcon size={20} className="text-cyan-400" />
                                            </div>
                                            {report.scheduled && (
                                                <div className="flex items-center gap-1 px-2 py-1 rounded-md bg-purple-500/10 text-purple-400 text-xs">
                                                    <Clock size={12} />
                                                    <span>Agendado</span>
                                                </div>
                                            )}
                                        </div>

                                        <h3 className="text-white font-medium mb-1">{report.name}</h3>
                                        <p className="text-slate-500 text-sm flex items-center gap-1">
                                            <Calendar size={12} />
                                            {t.lastRun}: {report.lastRun}
                                        </p>

                                        <div className="flex gap-2 mt-4 pt-4 border-t border-slate-700/50">
                                            <button
                                                onClick={() => handleRun(report.id)}
                                                className="flex-1 flex items-center justify-center gap-1 px-3 py-2 rounded-lg bg-cyan-500/10 text-cyan-400 text-sm hover:bg-cyan-500/20 transition-colors"
                                                aria-label={`Run ${report.name}`}
                                            >
                                                <Play size={14} />
                                                {t.run}
                                            </button>
                                            <button
                                                className="p-2 rounded-lg bg-slate-700/50 text-slate-400 hover:bg-slate-600/50 transition-colors"
                                                aria-label={`Download ${report.name}`}
                                            >
                                                <Download size={16} />
                                            </button>
                                            <button
                                                onClick={() => handleDelete(report.id)}
                                                className="p-2 rounded-lg bg-red-500/10 text-red-400 hover:bg-red-500/20 transition-colors"
                                                aria-label={`Delete ${report.name}`}
                                            >
                                                <Trash2 size={16} />
                                            </button>
                                        </div>
                                    </motion.div>
                                );
                            })}
                        </div>
                    )}
                </div>
            )}

            {/* Templates Tab */}
            {activeTab === 'templates' && (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                    {templates.map((template, index) => {
                        const Icon = template.icon;
                        return (
                            <motion.div
                                key={template.id}
                                initial={{ opacity: 0, y: 20 }}
                                animate={{ opacity: 1, y: 0 }}
                                transition={{ delay: index * 0.1 }}
                                className="bg-gradient-to-br from-slate-800/50 to-slate-900/50 rounded-xl p-6 border border-slate-700/50 hover:border-cyan-500/30 cursor-pointer transition-all group"
                            >
                                <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-cyan-500/10 to-blue-500/10 border border-cyan-500/20 flex items-center justify-center mb-4 group-hover:scale-110 transition-transform">
                                    <Icon size={24} className="text-cyan-400" />
                                </div>
                                <h3 className="text-white font-medium mb-1">{template.name}</h3>
                                <p className="text-slate-500 text-sm">{template.description}</p>
                                <button className="mt-4 text-cyan-400 text-sm font-medium hover:text-cyan-300 transition-colors">
                                    Usar template →
                                </button>
                            </motion.div>
                        );
                    })}
                </div>
            )}
        </div>
    );
}
