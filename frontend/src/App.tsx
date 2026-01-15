import { useState } from 'react';
import { Menu, Globe } from 'lucide-react';
import FileUpload from './components/FileUpload';
import Dashboard from './components/Dashboard';
import MappingManager from './components/MappingManager';
import Sidebar from './components/Sidebar';
import AIImportWizard from './components/AIImportWizard';
import ExecutiveDashboard from './components/ExecutiveDashboard';
import AnomalyDashboard from './components/AnomalyDashboard';
import TrendsDashboard from './components/TrendsDashboard';
import DRETable from './components/DRETable';
import CustomReports from './components/CustomReports';
import DataQuality from './components/DataQuality';
import Budgets from './components/Budgets';
import ImportHistory from './components/ImportHistory';
import ProfilePage from './components/ProfilePage';
import { motion, AnimatePresence } from 'framer-motion';

const translations = {
  pt: {
    currentView: 'Visualização Atual:',
    pages: {
      upload: { title: 'Importar Dados Financeiros', desc: 'Importe seu arquivo CSV do Conta Azul.' },
      'importar-v2': { title: 'Importar v2 (IA)', desc: 'Importação inteligente com análise de IA.' },
      dashboard: { title: 'Dashboard Financeiro', desc: 'Visão geral das métricas financeiras.' },
      'dashboard-executivo': { title: 'Dashboard Executivo', desc: 'Visão otimizada para mobile.' },
      anomalias: { title: 'Detecção de Anomalias', desc: 'Identifique transações incomuns.' },
      tendencias: { title: 'Análise de Tendências', desc: 'Projeções e padrões sazonais.' },
      pnl: { title: 'DRE - Demonstrativo de Resultados', desc: 'Receitas, custos e despesas.' },
      'relatorios-personalizados': { title: 'Relatórios Personalizados', desc: 'Crie relatórios customizados.' },
      'qualidade-dados': { title: 'Qualidade de Dados', desc: 'Métricas de validação e auditoria.' },
      mappings: { title: 'Mapeamentos', desc: 'Configure categorização de despesas.' },
      'mapeamentos-categorias': { title: 'Mapeamentos de Categorias', desc: 'Associe categorias às linhas do P&L.' },
      orcamentos: { title: 'Orçamentos', desc: 'Acompanhe orçado vs realizado.' },
      historico: { title: 'Histórico de Importações', desc: 'Veja importações anteriores.' },
      perfil: { title: 'Meu Perfil', desc: 'Configurações da conta.' },
    }
  },
  en: {
    currentView: 'Current View:',
    pages: {
      upload: { title: 'Import Financial Data', desc: 'Upload your Conta Azul CSV file.' },
      'importar-v2': { title: 'Import v2 (AI)', desc: 'Intelligent import with AI analysis.' },
      dashboard: { title: 'Financial Dashboard', desc: 'Overview of financial metrics.' },
      'dashboard-executivo': { title: 'Executive Dashboard', desc: 'Mobile-optimized view.' },
      anomalias: { title: 'Anomaly Detection', desc: 'Identify unusual transactions.' },
      tendencias: { title: 'Trend Analysis', desc: 'Forecasts and seasonal patterns.' },
      pnl: { title: 'P&L Statement', desc: 'Revenue, costs, and expenses.' },
      'relatorios-personalizados': { title: 'Custom Reports', desc: 'Build custom reports.' },
      'qualidade-dados': { title: 'Data Quality', desc: 'Validation and audit metrics.' },
      mappings: { title: 'Mappings', desc: 'Configure expense categorization.' },
      'mapeamentos-categorias': { title: 'Category Mappings', desc: 'Associate categories with P&L lines.' },
      orcamentos: { title: 'Budgets', desc: 'Track budget vs actual.' },
      historico: { title: 'Import History', desc: 'View previous imports.' },
      perfil: { title: 'My Profile', desc: 'Account settings.' },
    }
  }
};

type PageId = keyof typeof translations.pt.pages;

function App() {
  const [activeTab, setActiveTab] = useState<PageId>('upload');
  const [language, setLanguage] = useState<'pt' | 'en'>('pt');
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);

  const t = translations[language];
  const currentPage = t.pages[activeTab] || t.pages.upload;

  const renderContent = () => {
    switch (activeTab) {
      case 'upload':
        return <FileUpload language={language} />;
      case 'dashboard':
        return <Dashboard language={language} />;
      case 'pnl':
        return <DRETable language={language} />;
      case 'mappings':
        return <MappingManager language={language} />;

      // Placeholder pages for new features
      case 'importar-v2':
        return <AIImportWizard language={language} />;
      case 'dashboard-executivo':
        return <ExecutiveDashboard language={language} />;
      case 'anomalias':
        return <AnomalyDashboard language={language} />;
      case 'tendencias':
        return <TrendsDashboard language={language} />;
      case 'relatorios-personalizados':
        return <CustomReports language={language} />;
      case 'qualidade-dados':
        return <DataQuality language={language} />;
      case 'mapeamentos-categorias':
        return <MappingManager language={language} />;
      case 'orcamentos':
        return <Budgets language={language} />;
      case 'historico':
        return <ImportHistory language={language} />;
      case 'perfil':
        return <ProfilePage language={language} />;

      default:
        return <FileUpload language={language} />;
    }
  };

  return (
    <div className="flex h-screen min-h-screen-safe bg-[#0B1120] text-white overflow-hidden font-sans selection:bg-cyan-500/30 relative">
      {/* Ambient Background Effects */}
      <div className="fixed inset-0 pointer-events-none">
        <div className="absolute top-[-20%] left-[-10%] w-[50%] h-[50%] bg-purple-900/20 rounded-full blur-[120px] animate-pulse-slow" />
        <div className="absolute bottom-[-20%] right-[-10%] w-[50%] h-[50%] bg-cyan-900/20 rounded-full blur-[120px] animate-pulse-slow delay-1000" />
      </div>

      {/* Sidebar */}
      <Sidebar
        activeTab={activeTab}
        onTabChange={(id) => setActiveTab(id as PageId)}
        isSidebarOpen={isSidebarOpen}
        onClose={() => setIsSidebarOpen(false)}
        language={language}
      />

      {/* Mobile Overlay */}
      <AnimatePresence>
        {isSidebarOpen && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black/60 backdrop-blur-sm z-40 lg:hidden"
            onClick={() => setIsSidebarOpen(false)}
          />
        )}
      </AnimatePresence>

      {/* Main Content */}
      <main className="flex-1 flex flex-col min-w-0 overflow-hidden relative z-10">
        {/* Header */}
        <header className="h-16 sm:h-20 flex items-center px-4 sm:px-6 lg:px-8 justify-between bg-[#0B1120]/50 backdrop-blur-md border-b border-white/5 sticky top-0 z-30 safe-area-inset">
          <div className="flex items-center gap-4">
            <button
              onClick={() => setIsSidebarOpen(!isSidebarOpen)}
              className="lg:hidden p-2 text-slate-400 hover:text-white hover:bg-white/5 rounded-lg transition-colors"
              aria-label="Toggle menu"
            >
              <Menu size={24} />
            </button>

            <div className="hidden lg:flex items-center gap-3 text-sm">
              <span className="text-slate-500 font-medium">{t.currentView}</span>
              <div className="px-3 py-1 rounded-full bg-cyan-500/10 border border-cyan-500/20 text-cyan-400 font-semibold text-xs uppercase tracking-wide">
                {currentPage.title}
              </div>
            </div>
          </div>

          <div className="flex items-center gap-3">
            <button
              onClick={() => setLanguage(language === 'pt' ? 'en' : 'pt')}
              className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-white/5 hover:bg-white/10 border border-white/5 transition-all text-sm text-slate-300 hover:text-white"
            >
              <Globe size={16} className="text-cyan-400" />
              <span>{language === 'pt' ? 'PT' : 'EN'}</span>
            </button>
          </div>
        </header>

        {/* Content Area */}
        <div className="flex-1 overflow-auto p-4 sm:p-6 lg:p-8 scrollbar-thin scrollbar-thumb-slate-700 scrollbar-track-transparent">
          <div className="max-w-7xl mx-auto">
            <motion.div
              key={activeTab}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.4 }}
              className="mb-8"
            >
              <h2 className="text-2xl sm:text-3xl lg:text-4xl font-bold bg-gradient-to-r from-white via-slate-200 to-slate-400 bg-clip-text text-transparent mb-2 sm:mb-3 tracking-tight">
                {currentPage.title}
              </h2>
              <p className="text-slate-400 text-sm sm:text-base lg:text-lg max-w-2xl leading-relaxed">
                {currentPage.desc}
              </p>
            </motion.div>

            {renderContent()}
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="fixed bottom-2 sm:bottom-4 right-4 sm:right-6 pointer-events-none z-50 opacity-50 hover:opacity-100 transition-opacity safe-area-inset">
        <p className="text-[10px] text-slate-500 font-medium tracking-wider uppercase">
          POWERED BY FINANCE SPECIALIST CASTRO M. All Rights Reserved.
        </p>
      </footer>
    </div>
  );
}

export default App;

