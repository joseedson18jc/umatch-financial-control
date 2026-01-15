import { useState } from 'react';
import { motion } from 'framer-motion';
import {
    History,
    CheckCircle,
    XCircle,
    Clock,
    FileSpreadsheet,
    Download,
    Eye,
    RefreshCw,
    Search
} from 'lucide-react';

interface ImportHistoryProps {
    language: 'pt' | 'en';
}

const translations = {
    pt: {
        title: 'Histórico de Importações',
        subtitle: 'Todas as importações realizadas',
        loading: 'Carregando...',
        noHistory: 'Nenhuma importação registrada',
        filename: 'Arquivo',
        date: 'Data',
        rows: 'Linhas',
        status: 'Status',
        success: 'Sucesso',
        failed: 'Falhou',
        processing: 'Processando',
        view: 'Visualizar',
        download: 'Baixar',
        retry: 'Tentar novamente'
    },
    en: {
        title: 'Import History',
        subtitle: 'All imports performed',
        loading: 'Loading...',
        noHistory: 'No imports recorded',
        filename: 'File',
        date: 'Date',
        rows: 'Rows',
        status: 'Status',
        success: 'Success',
        failed: 'Failed',
        processing: 'Processing',
        view: 'View',
        download: 'Download',
        retry: 'Retry'
    }
};

interface ImportRecord {
    id: string;
    filename: string;
    date: string;
    rows: number;
    status: 'success' | 'failed' | 'processing';
    source: string;
    mappedCount: number;
    errorMessage?: string;
}

const mockHistory: ImportRecord[] = [
    { id: '1', filename: 'Extrato_Jan_2025.csv', date: '2025-01-14 14:30', rows: 156, status: 'success', source: 'Conta Azul', mappedCount: 152 },
    { id: '2', filename: 'Extrato_Dez_2024.csv', date: '2025-01-10 09:15', rows: 203, status: 'success', source: 'Conta Azul', mappedCount: 198 },
    { id: '3', filename: 'Export_Omie.csv', date: '2025-01-08 16:45', rows: 89, status: 'failed', source: 'Omie', mappedCount: 0, errorMessage: 'Formato de data inválido' },
    { id: '4', filename: 'Extrato_Nov_2024.csv', date: '2025-01-05 11:20', rows: 178, status: 'success', source: 'Conta Azul', mappedCount: 175 },
    { id: '5', filename: 'Lançamentos_Q4.csv', date: '2025-01-02 08:00', rows: 412, status: 'success', source: 'Manual', mappedCount: 408 },
];

const StatusBadge = ({ status, t }: { status: string; t: typeof translations.pt }) => {
    const config = {
        success: { icon: CheckCircle, color: 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20', label: t.success },
        failed: { icon: XCircle, color: 'bg-red-500/10 text-red-400 border-red-500/20', label: t.failed },
        processing: { icon: Clock, color: 'bg-amber-500/10 text-amber-400 border-amber-500/20', label: t.processing },
    };
    const { icon: Icon, color, label } = config[status as keyof typeof config];

    return (
        <span className={`inline-flex items-center gap-1 px-2 py-1 rounded-md text-xs font-medium border ${color}`}>
            <Icon size={12} />
            {label}
        </span>
    );
};

export default function ImportHistory({ language }: ImportHistoryProps) {
    const [history] = useState<ImportRecord[]>(mockHistory);
    const [searchTerm, setSearchTerm] = useState('');
    const [filterStatus, setFilterStatus] = useState<string>('all');

    const t = translations[language];

    const filteredHistory = history.filter(record => {
        const matchesSearch = record.filename.toLowerCase().includes(searchTerm.toLowerCase());
        const matchesStatus = filterStatus === 'all' || record.status === filterStatus;
        return matchesSearch && matchesStatus;
    });

    const totalRows = history.reduce((acc, r) => acc + r.rows, 0);
    const successCount = history.filter(r => r.status === 'success').length;

    return (
        <div className="space-y-6">
            {/* Stats */}
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
                <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="bg-slate-800/50 rounded-xl p-5 border border-slate-700/50"
                >
                    <History size={20} className="text-cyan-400 mb-2" />
                    <p className="text-2xl font-bold text-white">{history.length}</p>
                    <p className="text-sm text-slate-400">Total de importações</p>
                </motion.div>
                <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.1 }}
                    className="bg-slate-800/50 rounded-xl p-5 border border-slate-700/50"
                >
                    <FileSpreadsheet size={20} className="text-emerald-400 mb-2" />
                    <p className="text-2xl font-bold text-white">{totalRows.toLocaleString()}</p>
                    <p className="text-sm text-slate-400">Linhas importadas</p>
                </motion.div>
                <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.2 }}
                    className="bg-slate-800/50 rounded-xl p-5 border border-slate-700/50"
                >
                    <CheckCircle size={20} className="text-purple-400 mb-2" />
                    <p className="text-2xl font-bold text-white">{((successCount / history.length) * 100).toFixed(0)}%</p>
                    <p className="text-sm text-slate-400">Taxa de sucesso</p>
                </motion.div>
            </div>

            {/* Filters */}
            <div className="flex flex-col sm:flex-row gap-4">
                <div className="relative flex-1">
                    <Search size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-500" />
                    <input
                        type="text"
                        placeholder="Buscar arquivo..."
                        value={searchTerm}
                        onChange={(e) => setSearchTerm(e.target.value)}
                        className="w-full pl-9 pr-4 py-2.5 rounded-lg bg-slate-800/50 border border-slate-700/50 text-white text-sm focus:border-cyan-500/50 focus:outline-none"
                        aria-label="Search imports"
                    />
                </div>
                <select
                    value={filterStatus}
                    onChange={(e) => setFilterStatus(e.target.value)}
                    className="px-4 py-2.5 rounded-lg bg-slate-800/50 border border-slate-700/50 text-white text-sm focus:border-cyan-500/50 focus:outline-none"
                    aria-label="Filter by status"
                >
                    <option value="all">Todos os status</option>
                    <option value="success">{t.success}</option>
                    <option value="failed">{t.failed}</option>
                    <option value="processing">{t.processing}</option>
                </select>
            </div>

            {/* History Table */}
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
                                <th className="py-4 px-4 text-left text-slate-400 font-semibold">{t.filename}</th>
                                <th className="py-4 px-4 text-left text-slate-400 font-semibold">Fonte</th>
                                <th className="py-4 px-4 text-left text-slate-400 font-semibold">{t.date}</th>
                                <th className="py-4 px-4 text-right text-slate-400 font-semibold">{t.rows}</th>
                                <th className="py-4 px-4 text-center text-slate-400 font-semibold">{t.status}</th>
                                <th className="py-4 px-4 text-center text-slate-400 font-semibold">Ações</th>
                            </tr>
                        </thead>
                        <tbody>
                            {filteredHistory.length === 0 ? (
                                <tr>
                                    <td colSpan={6} className="py-12 text-center">
                                        <History size={48} className="text-slate-600 mx-auto mb-4" />
                                        <p className="text-slate-400">{t.noHistory}</p>
                                    </td>
                                </tr>
                            ) : (
                                filteredHistory.map(record => (
                                    <tr key={record.id} className="border-t border-slate-700/30 hover:bg-slate-800/30">
                                        <td className="py-4 px-4">
                                            <div className="flex items-center gap-3">
                                                <FileSpreadsheet size={18} className="text-slate-500" />
                                                <div>
                                                    <p className="text-white font-medium">{record.filename}</p>
                                                    {record.errorMessage && (
                                                        <p className="text-red-400 text-xs">{record.errorMessage}</p>
                                                    )}
                                                </div>
                                            </div>
                                        </td>
                                        <td className="py-4 px-4 text-slate-400">{record.source}</td>
                                        <td className="py-4 px-4 text-slate-400">{record.date}</td>
                                        <td className="py-4 px-4 text-right">
                                            <span className="text-white">{record.rows}</span>
                                            {record.status === 'success' && (
                                                <span className="text-slate-500 text-xs ml-1">({record.mappedCount} mapeadas)</span>
                                            )}
                                        </td>
                                        <td className="py-4 px-4 text-center">
                                            <StatusBadge status={record.status} t={t} />
                                        </td>
                                        <td className="py-4 px-4">
                                            <div className="flex justify-center gap-2">
                                                {record.status === 'success' && (
                                                    <>
                                                        <button
                                                            className="p-1.5 rounded-lg hover:bg-slate-700/50 text-slate-400 hover:text-white transition-colors"
                                                            aria-label={`View ${record.filename}`}
                                                        >
                                                            <Eye size={16} />
                                                        </button>
                                                        <button
                                                            className="p-1.5 rounded-lg hover:bg-slate-700/50 text-slate-400 hover:text-white transition-colors"
                                                            aria-label={`Download ${record.filename}`}
                                                        >
                                                            <Download size={16} />
                                                        </button>
                                                    </>
                                                )}
                                                {record.status === 'failed' && (
                                                    <button
                                                        className="p-1.5 rounded-lg hover:bg-cyan-500/20 text-slate-400 hover:text-cyan-400 transition-colors"
                                                        aria-label={`Retry ${record.filename}`}
                                                    >
                                                        <RefreshCw size={16} />
                                                    </button>
                                                )}
                                            </div>
                                        </td>
                                    </tr>
                                ))
                            )}
                        </tbody>
                    </table>
                </div>
            </motion.div>
        </div>
    );
}
