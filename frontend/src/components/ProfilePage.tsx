import { useState } from 'react';
import { motion } from 'framer-motion';
import {
    User,
    Mail,
    Building,
    Shield,
    Key,
    Bell,
    Moon,
    Sun,
    Save,
    Camera
} from 'lucide-react';

interface ProfilePageProps {
    language: 'pt' | 'en';
}

const translations = {
    pt: {
        title: 'Meu Perfil',
        subtitle: 'Gerencie suas informações',
        personalInfo: 'Informações Pessoais',
        security: 'Segurança',
        preferences: 'Preferências',
        name: 'Nome',
        email: 'Email',
        company: 'Empresa',
        role: 'Cargo',
        changePassword: 'Alterar Senha',
        currentPassword: 'Senha Atual',
        newPassword: 'Nova Senha',
        confirmPassword: 'Confirmar Senha',
        notifications: 'Notificações',
        darkMode: 'Modo Escuro',
        emailNotifications: 'Notificações por Email',
        save: 'Salvar Alterações',
        photoUpdate: 'Atualizar Foto'
    },
    en: {
        title: 'My Profile',
        subtitle: 'Manage your information',
        personalInfo: 'Personal Information',
        security: 'Security',
        preferences: 'Preferences',
        name: 'Name',
        email: 'Email',
        company: 'Company',
        role: 'Role',
        changePassword: 'Change Password',
        currentPassword: 'Current Password',
        newPassword: 'New Password',
        confirmPassword: 'Confirm Password',
        notifications: 'Notifications',
        darkMode: 'Dark Mode',
        emailNotifications: 'Email Notifications',
        save: 'Save Changes',
        photoUpdate: 'Update Photo'
    }
};

export default function ProfilePage({ language }: ProfilePageProps) {
    const [activeTab, setActiveTab] = useState<'info' | 'security' | 'preferences'>('info');
    const [darkMode, setDarkMode] = useState(true);
    const [emailNotif, setEmailNotif] = useState(true);

    const t = translations[language];

    const user = {
        name: 'José Costa',
        email: 'jose@umatch.com.br',
        company: 'UMatch',
        role: 'Administrador'
    };

    return (
        <div className="max-w-4xl mx-auto space-y-6">
            {/* Profile Header */}
            <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                className="bg-gradient-to-r from-slate-800/50 to-slate-900/50 rounded-2xl p-6 border border-slate-700/50"
            >
                <div className="flex flex-col sm:flex-row items-center gap-6">
                    <div className="relative">
                        <div className="w-24 h-24 rounded-2xl bg-gradient-to-br from-cyan-500 to-blue-600 flex items-center justify-center text-3xl font-bold text-white">
                            JC
                        </div>
                        <button
                            className="absolute -bottom-2 -right-2 p-2 rounded-lg bg-slate-800 border border-slate-700 text-slate-400 hover:text-white transition-colors"
                            aria-label={t.photoUpdate}
                        >
                            <Camera size={16} />
                        </button>
                    </div>
                    <div className="text-center sm:text-left">
                        <h2 className="text-2xl font-bold text-white">{user.name}</h2>
                        <p className="text-slate-400">{user.email}</p>
                        <div className="flex items-center gap-2 mt-2 justify-center sm:justify-start">
                            <span className="px-2 py-1 rounded-md bg-cyan-500/10 text-cyan-400 text-xs font-medium">
                                {user.role}
                            </span>
                            <span className="px-2 py-1 rounded-md bg-purple-500/10 text-purple-400 text-xs font-medium">
                                {user.company}
                            </span>
                        </div>
                    </div>
                </div>
            </motion.div>

            {/* Tabs */}
            <div className="flex gap-2 border-b border-slate-700/50 pb-2">
                <button
                    onClick={() => setActiveTab('info')}
                    className={`flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-colors ${activeTab === 'info'
                            ? 'bg-cyan-500/10 text-cyan-400 border border-cyan-500/20'
                            : 'text-slate-400 hover:text-white hover:bg-slate-800'
                        }`}
                >
                    <User size={16} />
                    {t.personalInfo}
                </button>
                <button
                    onClick={() => setActiveTab('security')}
                    className={`flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-colors ${activeTab === 'security'
                            ? 'bg-cyan-500/10 text-cyan-400 border border-cyan-500/20'
                            : 'text-slate-400 hover:text-white hover:bg-slate-800'
                        }`}
                >
                    <Shield size={16} />
                    {t.security}
                </button>
                <button
                    onClick={() => setActiveTab('preferences')}
                    className={`flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-colors ${activeTab === 'preferences'
                            ? 'bg-cyan-500/10 text-cyan-400 border border-cyan-500/20'
                            : 'text-slate-400 hover:text-white hover:bg-slate-800'
                        }`}
                >
                    <Bell size={16} />
                    {t.preferences}
                </button>
            </div>

            {/* Content */}
            <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                className="bg-slate-800/30 rounded-2xl p-6 border border-slate-700/50"
            >
                {activeTab === 'info' && (
                    <div className="space-y-6">
                        <div className="grid grid-cols-1 sm:grid-cols-2 gap-6">
                            <div>
                                <label className="block text-sm text-slate-400 mb-2">{t.name}</label>
                                <div className="relative">
                                    <User size={18} className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-500" />
                                    <input
                                        type="text"
                                        defaultValue={user.name}
                                        className="w-full pl-10 pr-4 py-3 rounded-lg bg-slate-800/50 border border-slate-700/50 text-white focus:border-cyan-500/50 focus:outline-none"
                                        aria-label={t.name}
                                    />
                                </div>
                            </div>
                            <div>
                                <label className="block text-sm text-slate-400 mb-2">{t.email}</label>
                                <div className="relative">
                                    <Mail size={18} className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-500" />
                                    <input
                                        type="email"
                                        defaultValue={user.email}
                                        className="w-full pl-10 pr-4 py-3 rounded-lg bg-slate-800/50 border border-slate-700/50 text-white focus:border-cyan-500/50 focus:outline-none"
                                        aria-label={t.email}
                                    />
                                </div>
                            </div>
                            <div>
                                <label className="block text-sm text-slate-400 mb-2">{t.company}</label>
                                <div className="relative">
                                    <Building size={18} className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-500" />
                                    <input
                                        type="text"
                                        defaultValue={user.company}
                                        className="w-full pl-10 pr-4 py-3 rounded-lg bg-slate-800/50 border border-slate-700/50 text-white focus:border-cyan-500/50 focus:outline-none"
                                        aria-label={t.company}
                                    />
                                </div>
                            </div>
                            <div>
                                <label className="block text-sm text-slate-400 mb-2">{t.role}</label>
                                <div className="relative">
                                    <Shield size={18} className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-500" />
                                    <input
                                        type="text"
                                        defaultValue={user.role}
                                        disabled
                                        className="w-full pl-10 pr-4 py-3 rounded-lg bg-slate-800/50 border border-slate-700/50 text-slate-400 cursor-not-allowed"
                                        aria-label={t.role}
                                    />
                                </div>
                            </div>
                        </div>
                    </div>
                )}

                {activeTab === 'security' && (
                    <div className="space-y-6">
                        <h3 className="text-lg font-semibold text-white flex items-center gap-2">
                            <Key size={20} className="text-cyan-400" />
                            {t.changePassword}
                        </h3>
                        <div className="space-y-4 max-w-md">
                            <div>
                                <label className="block text-sm text-slate-400 mb-2">{t.currentPassword}</label>
                                <input
                                    type="password"
                                    className="w-full px-4 py-3 rounded-lg bg-slate-800/50 border border-slate-700/50 text-white focus:border-cyan-500/50 focus:outline-none"
                                    aria-label={t.currentPassword}
                                />
                            </div>
                            <div>
                                <label className="block text-sm text-slate-400 mb-2">{t.newPassword}</label>
                                <input
                                    type="password"
                                    className="w-full px-4 py-3 rounded-lg bg-slate-800/50 border border-slate-700/50 text-white focus:border-cyan-500/50 focus:outline-none"
                                    aria-label={t.newPassword}
                                />
                            </div>
                            <div>
                                <label className="block text-sm text-slate-400 mb-2">{t.confirmPassword}</label>
                                <input
                                    type="password"
                                    className="w-full px-4 py-3 rounded-lg bg-slate-800/50 border border-slate-700/50 text-white focus:border-cyan-500/50 focus:outline-none"
                                    aria-label={t.confirmPassword}
                                />
                            </div>
                        </div>
                    </div>
                )}

                {activeTab === 'preferences' && (
                    <div className="space-y-6">
                        <div className="flex items-center justify-between p-4 rounded-lg bg-slate-800/50 border border-slate-700/50">
                            <div className="flex items-center gap-3">
                                {darkMode ? <Moon size={20} className="text-purple-400" /> : <Sun size={20} className="text-amber-400" />}
                                <div>
                                    <p className="text-white font-medium">{t.darkMode}</p>
                                    <p className="text-slate-500 text-sm">Interface escura ativada</p>
                                </div>
                            </div>
                            <button
                                onClick={() => setDarkMode(!darkMode)}
                                className={`w-12 h-6 rounded-full transition-colors ${darkMode ? 'bg-cyan-500' : 'bg-slate-600'}`}
                                aria-label="Toggle dark mode"
                            >
                                <div className={`w-5 h-5 rounded-full bg-white transform transition-transform ${darkMode ? 'translate-x-6' : 'translate-x-0.5'}`} />
                            </button>
                        </div>

                        <div className="flex items-center justify-between p-4 rounded-lg bg-slate-800/50 border border-slate-700/50">
                            <div className="flex items-center gap-3">
                                <Bell size={20} className="text-cyan-400" />
                                <div>
                                    <p className="text-white font-medium">{t.emailNotifications}</p>
                                    <p className="text-slate-500 text-sm">Receber atualizações por email</p>
                                </div>
                            </div>
                            <button
                                onClick={() => setEmailNotif(!emailNotif)}
                                className={`w-12 h-6 rounded-full transition-colors ${emailNotif ? 'bg-cyan-500' : 'bg-slate-600'}`}
                                aria-label="Toggle email notifications"
                            >
                                <div className={`w-5 h-5 rounded-full bg-white transform transition-transform ${emailNotif ? 'translate-x-6' : 'translate-x-0.5'}`} />
                            </button>
                        </div>
                    </div>
                )}

                {/* Save Button */}
                <div className="mt-8 flex justify-end">
                    <button className="flex items-center gap-2 px-6 py-3 rounded-xl bg-gradient-to-r from-cyan-500 to-blue-500 text-white font-semibold hover:shadow-lg hover:shadow-cyan-500/30 transition-all">
                        <Save size={18} />
                        <span>{t.save}</span>
                    </button>
                </div>
            </motion.div>
        </div>
    );
}
