import { motion } from 'framer-motion';
import { Github, Linkedin, Mail, ArrowRight } from 'lucide-react';
import profileImage from '../assets/profile.jpg';

export function Hero() {
    const socialLinks = [
        { icon: Github, href: "https://github.com/Bahie11", label: "GitHub" },
        { icon: Linkedin, href: "https://linkedin.com/in/mahmoud-elbahie", label: "LinkedIn" },
        { icon: Mail, href: "mailto:hello@example.com", label: "Email" }
    ];

    return (
        <section className="min-h-screen flex items-center justify-center bg-zinc-950 text-white relative overflow-hidden px-4">
            {/* Background gradients */}
            <div className="absolute top-0 left-1/4 w-96 h-96 bg-purple-600/20 rounded-full blur-[128px]" />
            <div className="absolute bottom-0 right-1/4 w-96 h-96 bg-blue-600/20 rounded-full blur-[128px]" />

            <div className="max-w-5xl mx-auto text-center relative z-10 px-4">
                <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.5 }}
                >
                    <div className="mb-8 relative inline-block">
                        <div className="absolute inset-0 bg-gradient-to-r from-blue-500 to-purple-500 rounded-full blur-xl opacity-50 animate-pulse" />
                        <img
                            src={profileImage}
                            alt="Mahmoud Elbahie"
                            className="relative w-32 h-32 md:w-40 md:h-40 rounded-full object-cover border-4 border-zinc-900 shadow-2xl"
                        />
                    </div>

                    <h2 className="text-zinc-400 text-lg md:text-xl font-medium tracking-wide mb-4">
                        HELLO, I'M
                    </h2>
                    <h1 className="text-5xl md:text-8xl font-bold mb-6 tracking-tight">
                        Mahmoud <span className="text-transparent bg-clip-text bg-gradient-to-r from-blue-400 to-purple-500">Elbahie</span>
                    </h1>

                    <div className="text-xl md:text-2xl text-zinc-400 mb-8 max-w-2xl mx-auto leading-relaxed">
                        CNC Student @ E-JUST <span className="mx-2 text-zinc-700">|</span>
                        Front End Developer <span className="mx-2 text-zinc-700">|</span>
                        Embedded Systems Graduate
                    </div>

                    <div className="flex gap-4 justify-center mb-12">
                        {socialLinks.map((link) => (
                            <motion.a
                                key={link.label}
                                href={link.href}
                                target="_blank"
                                rel="noopener noreferrer"
                                whileHover={{ scale: 1.1 }}
                                whileTap={{ scale: 0.95 }}
                                className="p-3 bg-zinc-900/50 border border-zinc-800 rounded-full hover:bg-zinc-800 transition-colors text-zinc-300"
                            >
                                <link.icon className="w-5 h-5" />
                            </motion.a>
                        ))}
                    </div>

                    <motion.button
                        whileHover={{ scale: 1.05 }}
                        whileTap={{ scale: 0.95 }}
                        onClick={() => document.getElementById('work')?.scrollIntoView({ behavior: 'smooth' })}
                        className="group px-8 py-4 bg-white text-black rounded-full font-semibold flex items-center gap-2 mx-auto hover:bg-zinc-200 transition-colors"
                    >
                        View Projects
                        <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
                    </motion.button>
                </motion.div>
            </div>
        </section>
    );
}
