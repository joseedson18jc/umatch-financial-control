import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import {
    FileSpreadsheet,
    TrendingUp,
    TrendingDown,
    RefreshCw,
    Download,
    Calendar,
    ChevronDown,
    ChevronRight
} from 'lucide-react';

interface DRETableProps {
    language: 'pt' | 'en';
}

const translations = {
    pt: {
        title: 'Demonstração do Resultado',
        subtitle: 'Análise de receitas e despesas',
        loading: 'Carregando dados...',
        noData: 'Nenhum dado disponível',
        refresh: 'Atualizar',
        export: 'Exportar',
        period: 'Período',
        revenue: 'Receitas',
        expenses: 'Despesas',
        grossProfit: 'Lucro Bruto',
        operatingExpenses: 'Despesas Operacionais',
        netIncome: 'Resultado Líquido',
        margin: 'Margem',
        ytd: 'Acumulado'
    },
    en: {
        title: 'Income Statement',
        subtitle: 'Revenue and expense analysis',
        loading: 'Loading data...',
        noData: 'No data available',
        refresh: 'Refresh',
        export: 'Export',
        period: 'Period',
        revenue: 'Revenue',
        expenses: 'Expenses',
        grossProfit: 'Gross Profit',
        operatingExpenses: 'Operating Expenses',
        netIncome: 'Net Income',
        margin: 'Margin',
        ytd: 'YTD'
    }
};

interface DRERow {
    id: string;
    label: string;
    values: number[];
    isTotal?: boolean;
    isSubtotal?: boolean;
    indent?: number;
    children?: DRERow[];
}

// Mock DRE data structure
const mockDREData: DRERow[] = [
    {
        id: 'revenue',
        label: 'Receita Operacional Bruta',
        values: [180000, 195000, 210000],
        isTotal: true,
        children: [
            { id: 'rev-products', label: 'Vendas de Produtos', values: [120000, 130000, 140000], indent: 1 },
            { id: 'rev-services', label: 'Prestação de Serviços', values: [60000, 65000, 70000], indent: 1 },
        ]
    },
    {
        id: 'deductions',
        label: 'Deduções da Receita',
        values: [-18000, -19500, -21000],
        isSubtotal: true,
        children: [
            { id: 'ded-taxes', label: 'Impostos sobre Vendas', values: [-10800, -11700, -12600], indent: 1 },
            { id: 'ded-returns', label: 'Devoluções e Cancelamentos', values: [-7200, -7800, -8400], indent: 1 },
        ]
    },
    {
        id: 'net-revenue',
        label: 'Receita Operacional Líquida',
        values: [162000, 175500, 189000],
        isTotal: true
    },
    {
        id: 'cogs',
        label: 'Custo das Mercadorias/Serviços',
        values: [-64800, -70200, -75600],
        isSubtotal: true
    },
    {
        id: 'gross-profit',
        label: 'Lucro Bruto',
        values: [97200, 105300, 113400],
        isTotal: true
    },
    {
        id: 'opex',
        label: 'Despesas Operacionais',
        values: [-48600, -52650, -56700],
        isSubtotal: true,
        children: [
            { id: 'opex-admin', label: 'Administrativas', values: [-24300, -26325, -28350], indent: 1 },
            { id: 'opex-sales', label: 'Comerciais', values: [-14580, -15795, -17010], indent: 1 },
            { id: 'opex-other', label: 'Outras Despesas', values: [-9720, -10530, -11340], indent: 1 },
        ]
    },
    {
        id: 'ebitda',
        label: 'EBITDA',
        values: [48600, 52650, 56700],
        isTotal: true
    },
    {
        id: 'net-income',
        label: 'Resultado Líquido',
        values: [38880, 42120, 45360],
        isTotal: true
    }
];

const periods = ['Nov/24', 'Dez/24', 'Jan/25'];

const DRERowComponent = ({
    row,
    isExpanded,
    onToggle
}: {
    row: DRERow;
    isExpanded: boolean;
    onToggle: () => void;
}) => {
    const hasChildren = row.children && row.children.length > 0;
    const total = row.values.reduce((a, b) => a + b, 0);

    const formatValue = (value: number) => {
        return new Intl.NumberFormat('pt-BR', {
            style: 'currency',
            currency: 'BRL',
            minimumFractionDigits: 0,
            maximumFractionDigits: 0
        }).format(value);
    };

    return (
        <>
            <tr className={`border-b border-slate-700/30 ${row.isTotal ? 'bg-slate-800/50 font-semibold' :
                row.isSubtotal ? 'bg-slate-800/30' : ''
                }`}>
                <td className="py-3 px-4">
                    <div
                        className={`flex items-center gap-2 ${row.indent === 1 ? 'pl-4' : row.indent === 2 ? 'pl-8' : ''}`}
                    >
                        {hasChildren && (
                            <button
                                onClick={onToggle}
                                className="p-0.5 hover:bg-slate-700/50 rounded"
                                aria-label={isExpanded ? 'Collapse' : 'Expand'}
                            >
                                {isExpanded ? <ChevronDown size={14} /> : <ChevronRight size={14} />}
                            </button>
                        )}
                        <span className={`${row.isTotal ? 'text-white' : row.isSubtotal ? 'text-slate-300' : 'text-slate-400'}`}>
                            {row.label}
                        </span>
                    </div>
                </td>
                {row.values.map((value, idx) => (
                    <td key={idx} className={`py-3 px-4 text-right font-mono ${value >= 0 ? 'text-emerald-400' : 'text-red-400'
                        }`}>
                        {formatValue(value)}
                    </td>
                ))}
                <td className={`py-3 px-4 text-right font-mono font-semibold ${total >= 0 ? 'text-cyan-400' : 'text-orange-400'
                    }`}>
                    {formatValue(total)}
                </td>
            </tr>
            {hasChildren && isExpanded && row.children?.map(child => (
                <DRERowComponent key={child.id} row={child} isExpanded={false} onToggle={() => { }} />
            ))}
        </>
    );
};

export default function DRETable({ language }: DRETableProps) {
    const [loading, setLoading] = useState(true);
    const [data, setData] = useState<DRERow[]>([]);
    const [expandedRows, setExpandedRows] = useState<Set<string>>(new Set(['revenue', 'opex']));

    const t = translations[language];

    useEffect(() => {
        const loadData = async () => {
            setLoading(true);
            await new Promise(resolve => setTimeout(resolve, 800));
            setData(mockDREData);
            setLoading(false);
        };
        loadData();
    }, []);

    const toggleRow = (id: string) => {
        setExpandedRows(prev => {
            const next = new Set(prev);
            if (next.has(id)) {
                next.delete(id);
            } else {
                next.add(id);
            }
            return next;
        });
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

    return (
        <div className="space-y-6">
            {/* Header */}
            <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
                <div className="flex items-center gap-3">
                    <Calendar size={20} className="text-slate-500" />
                    <span className="text-slate-400">{t.period}: Nov 2024 - Jan 2025</span>
                </div>
                <div className="flex gap-2">
                    <button
                        className="flex items-center gap-2 px-4 py-2 rounded-lg bg-slate-800 border border-slate-700 text-slate-300 hover:bg-slate-700 transition-all text-sm"
                        aria-label={t.refresh}
                    >
                        <RefreshCw size={16} />
                        <span>{t.refresh}</span>
                    </button>
                    <button
                        className="flex items-center gap-2 px-4 py-2 rounded-lg bg-cyan-500/10 border border-cyan-500/20 text-cyan-400 hover:bg-cyan-500/20 transition-all text-sm"
                        aria-label={t.export}
                    >
                        <Download size={16} />
                        <span>{t.export}</span>
                    </button>
                </div>
            </div>

            {/* DRE Table */}
            <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                className="bg-slate-800/30 rounded-2xl border border-slate-700/50 overflow-hidden"
            >
                <div className="overflow-x-auto">
                    <table className="w-full text-sm">
                        <thead className="bg-slate-800/80">
                            <tr>
                                <th className="py-4 px-4 text-left text-slate-400 font-semibold w-1/3">
                                    <div className="flex items-center gap-2">
                                        <FileSpreadsheet size={16} />
                                        <span>Conta</span>
                                    </div>
                                </th>
                                {periods.map(period => (
                                    <th key={period} className="py-4 px-4 text-right text-slate-400 font-semibold">
                                        {period}
                                    </th>
                                ))}
                                <th className="py-4 px-4 text-right text-cyan-400 font-semibold">{t.ytd}</th>
                            </tr>
                        </thead>
                        <tbody>
                            {data.map(row => (
                                <DRERowComponent
                                    key={row.id}
                                    row={row}
                                    isExpanded={expandedRows.has(row.id)}
                                    onToggle={() => toggleRow(row.id)}
                                />
                            ))}
                        </tbody>
                    </table>
                </div>
            </motion.div>

            {/* Summary Cards */}
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
                <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.1 }}
                    className="bg-gradient-to-br from-emerald-500/10 to-teal-500/10 rounded-xl p-5 border border-emerald-500/20"
                >
                    <TrendingUp size={20} className="text-emerald-400 mb-2" />
                    <p className="text-2xl font-bold text-white">R$ 526.500</p>
                    <p className="text-sm text-slate-400">{t.revenue} {t.ytd}</p>
                </motion.div>
                <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.2 }}
                    className="bg-gradient-to-br from-red-500/10 to-orange-500/10 rounded-xl p-5 border border-red-500/20"
                >
                    <TrendingDown size={20} className="text-red-400 mb-2" />
                    <p className="text-2xl font-bold text-white">R$ 400.140</p>
                    <p className="text-sm text-slate-400">{t.expenses} {t.ytd}</p>
                </motion.div>
                <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.3 }}
                    className="bg-gradient-to-br from-cyan-500/10 to-blue-500/10 rounded-xl p-5 border border-cyan-500/20"
                >
                    <FileSpreadsheet size={20} className="text-cyan-400 mb-2" />
                    <p className="text-2xl font-bold text-white">R$ 126.360</p>
                    <p className="text-sm text-slate-400">{t.netIncome} {t.ytd}</p>
                </motion.div>
            </div>
        </div>
    );
}
