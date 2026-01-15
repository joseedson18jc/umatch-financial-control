import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
    Upload,
    Sparkles,
    LayoutDashboard,
    Smartphone,
    AlertTriangle,
    TrendingUp,
    FileSpreadsheet,
    FileText,
    Settings,
    Tags,
    Wallet,
    History,
    User,
    CreditCard,
    ChevronDown,
    ChevronRight,
    X,
    Shield
} from 'lucide-react';

interface SidebarProps {
    activeTab: string;
    onTabChange: (tab: string) => void;
    isSidebarOpen: boolean;
    onClose: () => void;
    language: 'pt' | 'en';
}

interface NavSection {
    id: string;
    title: { pt: string; en: string };
    items: NavItem[];
}

interface NavItem {
    id: string;
    label: { pt: string; en: string };
    icon: React.ElementType;
    badge?: string;
}

const NAVIGATION: NavSection[] = [
    {
        id: 'import',
        title: { pt: 'Entrada de Dados', en: 'Data Entry' },
        items: [
            { id: 'upload', label: { pt: 'Importar', en: 'Import' }, icon: Upload },
            { id: 'importar-v2', label: { pt: 'Importar v2 (IA)', en: 'Import v2 (AI)' }, icon: Sparkles, badge: 'IA' },
        ]
    },
    {
        id: 'dashboards',
        title: { pt: 'Dashboards', en: 'Dashboards' },
        items: [
            { id: 'dashboard', label: { pt: 'Financeiro', en: 'Financial' }, icon: LayoutDashboard },
            { id: 'dashboard-executivo', label: { pt: 'Executivo', en: 'Executive' }, icon: Smartphone },
            { id: 'anomalias', label: { pt: 'Anomalias', en: 'Anomalies' }, icon: AlertTriangle },
            { id: 'tendencias', label: { pt: 'Tendências', en: 'Trends' }, icon: TrendingUp },
        ]
    },
    {
        id: 'reports',
        title: { pt: 'Relatórios', en: 'Reports' },
        items: [
            { id: 'pnl', label: { pt: 'DRE', en: 'P&L' }, icon: FileSpreadsheet },
            { id: 'relatorios-personalizados', label: { pt: 'Personalizados', en: 'Custom' }, icon: FileText },
        ]
    },
    {
        id: 'management',
        title: { pt: 'Gestão', en: 'Management' },
        items: [
            { id: 'qualidade-dados', label: { pt: 'Qualidade de Dados', en: 'Data Quality' }, icon: Shield },
            { id: 'mappings', label: { pt: 'Mapeamentos', en: 'Mappings' }, icon: Settings },
            { id: 'mapeamentos-categorias', label: { pt: 'Categorias', en: 'Categories' }, icon: Tags },
            { id: 'orcamentos', label: { pt: 'Orçamentos', en: 'Budgets' }, icon: Wallet },
            { id: 'historico', label: { pt: 'Histórico', en: 'History' }, icon: History },
        ]
    },
    {
        id: 'account',
        title: { pt: 'Conta', en: 'Account' },
        items: [
            { id: 'perfil', label: { pt: 'Perfil', en: 'Profile' }, icon: User },
        ]
    }
];

const NavItemComponent = ({
    item,
    isActive,
    onClick,
    language
}: {
    item: NavItem;
    isActive: boolean;
    onClick: () => void;
    language: 'pt' | 'en';
}) => {
    const Icon = item.icon;

    return (
        <button
            onClick={onClick}
            className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-lg transition-all duration-200 group relative ${isActive
                ? 'text-white bg-gradient-to-r from-cyan-500/15 to-blue-500/10 border border-cyan-500/20'
                : 'text-slate-400 hover:text-white hover:bg-white/5 border border-transparent'
                }`}
        >
            <Icon
                size={18}
                className={`transition-colors ${isActive ? 'text-cyan-400' : 'text-slate-500 group-hover:text-cyan-300'
                    }`}
            />
            <span className="text-sm font-medium flex-1 text-left">{item.label[language]}</span>
            {item.badge && (
                <span className="px-1.5 py-0.5 text-[10px] font-bold bg-gradient-to-r from-purple-500 to-pink-500 text-white rounded">
                    {item.badge}
                </span>
            )}
            {isActive && (
                <div className="w-1.5 h-1.5 rounded-full bg-cyan-400 shadow-[0_0_8px_rgba(34,211,238,0.8)]" />
            )}
        </button>
    );
};

const SectionGroup = ({
    section,
    activeTab,
    onTabChange,
    language,
    defaultOpen = true
}: {
    section: NavSection;
    activeTab: string;
    onTabChange: (tab: string) => void;
    language: 'pt' | 'en';
    defaultOpen?: boolean;
}) => {
    const [isOpen, setIsOpen] = useState(defaultOpen);
    const hasActiveItem = section.items.some(item => item.id === activeTab);

    return (
        <div className="mb-2">
            <button
                onClick={() => setIsOpen(!isOpen)}
                className={`w-full flex items-center justify-between px-3 py-2 text-xs font-semibold uppercase tracking-wider transition-colors ${hasActiveItem ? 'text-cyan-400' : 'text-slate-500 hover:text-slate-300'
                    }`}
            >
                <span>{section.title[language]}</span>
                {isOpen ? <ChevronDown size={14} /> : <ChevronRight size={14} />}
            </button>

            <AnimatePresence>
                {isOpen && (
                    <motion.div
                        initial={{ height: 0, opacity: 0 }}
                        animate={{ height: 'auto', opacity: 1 }}
                        exit={{ height: 0, opacity: 0 }}
                        transition={{ duration: 0.2 }}
                        className="overflow-hidden"
                    >
                        <div className="space-y-1 ml-1">
                            {section.items.map(item => (
                                <NavItemComponent
                                    key={item.id}
                                    item={item}
                                    isActive={activeTab === item.id}
                                    onClick={() => onTabChange(item.id)}
                                    language={language}
                                />
                            ))}
                        </div>
                    </motion.div>
                )}
            </AnimatePresence>
        </div>
    );
};

export default function Sidebar({
    activeTab,
    onTabChange,
    isSidebarOpen,
    onClose,
    language
}: SidebarProps) {
    return (
        <aside className={`
      fixed lg:static inset-y-0 left-0 z-50 w-72 
      bg-[#0f172a]/95 backdrop-blur-2xl 
      border-r border-white/[0.08] 
      transform transition-transform duration-300 ease-out
      shadow-2xl lg:shadow-none
      ${isSidebarOpen ? 'translate-x-0' : '-translate-x-full lg:translate-x-0'}
    `}>
            <div className="h-full flex flex-col">
                {/* Header */}
                <div className="p-5 border-b border-white/5">
                    <div className="flex items-center justify-between">
                        <div className="flex items-center gap-3">
                            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-cyan-500 via-blue-600 to-indigo-600 flex items-center justify-center shadow-lg shadow-cyan-500/25 p-1.5">
                                <img src="/logo.webp" alt="UMatch" className="w-full h-full object-contain" />
                            </div>
                            <div>
                                <h1 className="text-lg font-bold text-white tracking-tight">UMatch</h1>
                                <p className="text-[9px] text-cyan-400 font-semibold tracking-widest uppercase">Control & Analytics</p>
                            </div>
                        </div>
                        <button
                            onClick={onClose}
                            className="lg:hidden p-1.5 text-slate-400 hover:text-white hover:bg-white/10 rounded-lg transition-colors"
                            aria-label="Close sidebar"
                        >
                            <X size={18} />
                        </button>
                    </div>
                </div>

                {/* Navigation */}
                <nav className="flex-1 p-3 overflow-y-auto scrollbar-thin scrollbar-thumb-slate-700 scrollbar-track-transparent">
                    {NAVIGATION.map(section => (
                        <SectionGroup
                            key={section.id}
                            section={section}
                            activeTab={activeTab}
                            onTabChange={(id) => {
                                onTabChange(id);
                                onClose();
                            }}
                            language={language}
                            defaultOpen={['import', 'dashboards'].includes(section.id)}
                        />
                    ))}
                </nav>

                {/* Payment Section */}
                <div className="p-3 border-t border-white/5 space-y-2">
                    <p className="px-3 text-[10px] font-semibold text-slate-500 uppercase tracking-wider">
                        {language === 'pt' ? 'Pagamento Mensalidade' : 'Monthly Payment'}
                    </p>
                    <button
                        className="w-full flex items-center gap-3 px-3 py-2.5 rounded-lg bg-gradient-to-r from-emerald-500/10 to-teal-500/10 border border-emerald-500/20 text-emerald-400 hover:from-emerald-500/20 hover:to-teal-500/20 transition-all"
                        aria-label={language === 'pt' ? 'Pagamento PIX' : 'PIX Payment'}
                    >
                        <Wallet size={18} />
                        <span className="text-sm font-medium">Pagamento PIX</span>
                    </button>
                    <button
                        className="w-full flex items-center gap-3 px-3 py-2.5 rounded-lg bg-gradient-to-r from-blue-500/10 to-indigo-500/10 border border-blue-500/20 text-blue-400 hover:from-blue-500/20 hover:to-indigo-500/20 transition-all"
                        aria-label={language === 'pt' ? 'Cartão de Crédito' : 'Credit Card'}
                    >
                        <CreditCard size={18} />
                        <span className="text-sm font-medium">Cartão de Crédito</span>
                    </button>
                </div>
            </div>
        </aside>
    );
}
