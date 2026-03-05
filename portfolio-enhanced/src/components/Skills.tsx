import { motion } from 'framer-motion';
import { Code, Cpu, Terminal, Shield } from 'lucide-react';

const skillCategories = [
    {
        icon: Code,
        title: 'Front-End & Web',
        skills: ['HTML', 'CSS', 'JavaScript', 'React', 'Node.js', 'PHP', 'Tailwind']
    },
    {
        icon: Terminal,
        title: 'Programming',
        skills: ['Python', 'Java', 'C++', 'C#', 'Embedded C', 'Basic SQL']
    },
    {
        icon: Cpu,
        title: 'Embedded Systems',
        skills: ['Microcontrollers', 'Arduino', 'IoT', 'Hardware Integration']
    },
    {
        icon: Shield,
        title: 'Cyber Security',
        skills: ['Networking Fundamentals', 'Cryptography', 'Pic-Testing', 'Crypto-analysis']
    }
];

export function Skills() {
    return (
        <section className="py-32 bg-zinc-950 px-4">
            <div className="max-w-6xl mx-auto">
                <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    whileInView={{ opacity: 1, y: 0 }}
                    viewport={{ once: true }}
                    className="mb-16"
                >
                    <h2 className="text-3xl md:text-5xl font-bold text-white mb-6">Technical Arsenal</h2>
                    <div className="h-1 w-20 bg-blue-500 rounded-full" />
                </motion.div>

                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                    {skillCategories.map((category, index) => (
                        <motion.div
                            key={category.title}
                            initial={{ opacity: 0, y: 20 }}
                            whileInView={{ opacity: 1, y: 0 }}
                            viewport={{ once: true }}
                            transition={{ delay: index * 0.1 }}
                            className="p-6 rounded-2xl bg-zinc-900/50 border border-zinc-800 hover:border-zinc-700 transition-colors"
                        >
                            <category.icon className="w-8 h-8 text-blue-400 mb-6" />
                            <h3 className="text-xl font-semibold text-white mb-4">{category.title}</h3>
                            <div className="flex flex-wrap gap-2">
                                {category.skills.map((skill) => (
                                    <span key={skill} className="text-sm text-zinc-400 bg-zinc-950 px-3 py-1 rounded-full border border-zinc-900">
                                        {skill}
                                    </span>
                                ))}
                            </div>
                        </motion.div>
                    ))}
                </div>
            </div>
        </section>
    );
}
