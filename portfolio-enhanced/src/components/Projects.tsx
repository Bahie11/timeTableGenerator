import { motion } from 'framer-motion';
import { ExternalLink } from 'lucide-react';
import elevatorImg from '../assets/elevator-mdp.png';

const projects = [
    {
        id: 1,
        title: 'Two-Pass Assembler',
        description: 'A dedicated assembler written in C++ that translates assembly language into machine code using a two-pass process.',
        image: 'https://images.unsplash.com/photo-1555066931-4365d14bab8c?auto=format&fit=crop&q=80&w=1080',
        tags: ['C++', 'Systems', 'Compiler']
    },
    {
        id: 2,
        title: 'Simple Bank System',
        description: 'Desktop banking application built with Python. Features a GUI for account management and transaction processing.',
        image: 'https://images.unsplash.com/photo-1601597111158-2fceff292cdc?auto=format&fit=crop&q=80&w=1080',
        tags: ['Python', 'GUI', 'SQL']
    },
    {
        id: 3,
        title: 'Dental Clinic Website',
        description: 'Modern, responsive website for a dental clinic featuring appointment booking and service showcases.',
        image: 'https://images.unsplash.com/photo-1629909613654-28e377c37b09?auto=format&fit=crop&q=80&w=1080',
        tags: ['HTML5', 'CSS', 'JS']
    },
    {
        id: 4,
        title: 'FCFS CPU Scheduler',
        description: 'Simulation of the First-Come First-Served (FCFS) CPU scheduling algorithm analyzing process execution.',
        image: 'https://images.unsplash.com/photo-1518770660439-4636190af475?auto=format&fit=crop&q=80&w=1080',
        tags: ['Python', 'OS', 'Algo']
    },
    {
        id: 5,
        title: 'IDS V2 (TensorFlow)',
        description: 'Sequence-level Intrusion Detection System utilizing Packet-Level 1-D CNN and LSTM Autoencoders.',
        image: 'https://images.unsplash.com/photo-1550751827-4bd374c3f58b?auto=format&fit=crop&q=80&w=1080',
        tags: ['Python', 'AI', 'Security']
    },
    {
        id: 6,
        title: 'Elevator MDP',
        description: 'Intelligent elevator control system using Markov Decision Processes (MDP) to optimize floor scheduling.',
        image: elevatorImg,
        tags: ['Python', 'RL', 'MDP']
    },
    {
        id: 7,
        title: 'Neural Framework',
        description: 'PyTorch-based implementation of advanced neural network architectures, focusing on CNN-LSTM.',
        image: 'https://images.unsplash.com/photo-1620712943543-bcc4688e7485?auto=format&fit=crop&q=80&w=1080',
        tags: ['Python', 'PyTorch', 'NN']
    }
];

export function Projects() {
    return (
        <section id="work" className="py-32 bg-zinc-950 px-4">
            <div className="max-w-7xl mx-auto">
                <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    whileInView={{ opacity: 1, y: 0 }}
                    viewport={{ once: true }}
                    className="mb-16"
                >
                    <h2 className="text-3xl md:text-5xl font-bold text-white mb-6">Selected Works</h2>
                    <div className="h-1 w-20 bg-purple-500 rounded-full" />
                </motion.div>

                <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
                    {projects.map((project, index) => (
                        <motion.div
                            key={project.id}
                            initial={{ opacity: 0, y: 20 }}
                            whileInView={{ opacity: 1, y: 0 }}
                            viewport={{ once: true }}
                            transition={{ delay: index * 0.1 }}
                            className="group relative bg-zinc-900 rounded-2xl overflow-hidden border border-zinc-800 hover:border-zinc-700 transition-colors"
                        >
                            <div className="aspect-video overflow-hidden">
                                <img
                                    src={project.image}
                                    alt={project.title}
                                    className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500"
                                />
                            </div>

                            <div className="p-6">
                                <div className="flex justify-between items-start mb-4">
                                    <h3 className="text-xl font-bold text-white group-hover:text-blue-400 transition-colors">{project.title}</h3>
                                    <a href="#" className="text-zinc-500 hover:text-white transition-colors">
                                        <ExternalLink className="w-5 h-5" />
                                    </a>
                                </div>

                                <p className="text-zinc-400 text-sm mb-6 line-clamp-3">
                                    {project.description}
                                </p>

                                <div className="flex flex-wrap gap-2">
                                    {project.tags.map(tag => (
                                        <span key={tag} className="text-xs font-medium text-zinc-300 bg-zinc-800 px-2 py-1 rounded">
                                            {tag}
                                        </span>
                                    ))}
                                </div>
                            </div>
                        </motion.div>
                    ))}
                </div>
            </div>
        </section>
    );
}
