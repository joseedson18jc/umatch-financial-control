import { motion } from 'framer-motion';
import { Construction } from 'lucide-react';

interface PlaceholderPageProps {
    title: string;
    description: string;
    icon?: React.ElementType;
}

export default function PlaceholderPage({ title, description, icon: Icon = Construction }: PlaceholderPageProps) {
    return (
        <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.4 }}
            className="flex flex-col items-center justify-center min-h-[60vh] text-center"
        >
            <div className="w-24 h-24 rounded-3xl bg-gradient-to-br from-cyan-500/10 to-blue-500/10 border border-cyan-500/20 flex items-center justify-center mb-8">
                <Icon size={48} className="text-cyan-400" />
            </div>
            <h2 className="text-3xl font-bold text-white mb-4">{title}</h2>
            <p className="text-slate-400 text-lg max-w-md mb-8">{description}</p>
            <div className="flex items-center gap-2 px-4 py-2 rounded-full bg-amber-500/10 border border-amber-500/20 text-amber-400 text-sm">
                <Construction size={16} />
                <span>Em desenvolvimento</span>
            </div>
        </motion.div>
    );
}
