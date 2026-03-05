import { ExternalLink } from 'lucide-react';
import { ImageWithFallback } from './figma/ImageWithFallback';

const projects = [
  {
    id: 1,
    title: 'Two-Pass Assembler',
    description: 'A dedicated assembler written in C++ that translates assembly language into machine code using a two-pass process. Key features include symbol table management and complex opcode resolution.',
    image: 'https://images.unsplash.com/photo-1555066931-4365d14bab8c?auto=format&fit=crop&q=80&w=1080',
    tags: ['C++', 'Systems Programming', 'Compiler Design'],
    link: '#'
  },
  {
    id: 2,
    title: 'Simple Bank System',
    description: 'Desktop banking application built with Python. Features a graphical user interface for account management, secure transaction processing, and user history tracking.',
    image: 'https://images.unsplash.com/photo-1601597111158-2fceff292cdc?auto=format&fit=crop&q=80&w=1080',
    tags: ['Python', 'GUI', 'SQL'],
    link: '#'
  },
  {
    id: 3,
    title: 'Dental Clinic Website',
    description: 'A modern, responsive website designed for a dental clinic. Includes features for appointment booking, service showcases, and patient information portals.',
    image: 'https://images.unsplash.com/photo-1629909613654-28e377c37b09?auto=format&fit=crop&q=80&w=1080',
    tags: ['HTML5', 'CSS3', 'JavaScript'],
    link: '#'
  },
  {
    id: 4,
    title: 'FCFS CPU Scheduler',
    description: 'Simulation of the First-Come First-Served (FCFS) CPU scheduling algorithm. Analyzes process execution, calculating wait times and turnaround metrics for system optimization.',
    image: 'https://images.unsplash.com/photo-1518770660439-4636190af475?auto=format&fit=crop&q=80&w=1080',
    tags: ['Python', 'Algorithms', 'Operating Systems'],
    link: '#'
  },
  {
    id: 5,
    title: 'IDS V2 (TensorFlow)',
    description: 'Sequence-level Intrusion Detection System utilizing Packet-Level 1-D CNN and LSTM Autoencoders implemented in TensorFlow/Keras for efficient anomaly detection.',
    image: 'https://images.unsplash.com/photo-1550751827-4bd374c3f58b?auto=format&fit=crop&q=80&w=1080',
    tags: ['Python', 'TensorFlow', 'Deep Learning'],
    link: '#'
  },
  {
    id: 6,
    title: 'Elevator MDP',
    description: 'Intelligent elevator control system using Markov Decision Processes (MDP). Optimizes floor scheduling and minimizes passenger wait times through reinforcement learning strategies.',
    image: 'https://images.unsplash.com/photo-1533230831633-e074fb06e23c?auto=format&fit=crop&q=80&w=1080',
    tags: ['Python', 'Reinforcement Learning', 'AI'],
    link: '#'
  },
  {
    id: 7,
    title: 'Neural Network Framework',
    description: 'PyTorch-based implementation of advanced neural network architectures, focusing on CNN-LSTM Autoencoders for robust sequence analysis and pattern recognition.',
    image: 'https://images.unsplash.com/photo-1620712943543-bcc4688e7485?auto=format&fit=crop&q=80&w=1080',
    tags: ['Python', 'PyTorch', 'Neural Networks'],
    link: '#'
  }
];

export function Work() {
  return (
    <section id="work" className="py-20 bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <h2 className="text-4xl md:text-5xl mb-12 text-center text-gray-900">
          Featured Work
        </h2>
        
        <div className="grid md:grid-cols-2 gap-8">
          {projects.map((project) => (
            <div
              key={project.id}
              className="group bg-white rounded-2xl overflow-hidden shadow-lg hover:shadow-2xl transition-all transform hover:-translate-y-2"
            >
              <div className="relative h-64 overflow-hidden">
                <ImageWithFallback
                  src={project.image}
                  alt={project.title}
                  className="w-full h-full object-cover group-hover:scale-110 transition-transform duration-300"
                />
              </div>
              
              <div className="p-6">
                <h3 className="text-2xl mb-3 text-gray-900">
                  {project.title}
                </h3>
                <p className="text-gray-600 mb-4">
                  {project.description}
                </p>
                
                <div className="flex flex-wrap gap-2 mb-4">
                  {project.tags.map((tag, index) => (
                    <span
                      key={index}
                      className="px-3 py-1 bg-gray-100 text-gray-700 rounded-full text-sm"
                    >
                      {tag}
                    </span>
                  ))}
                </div>
                
                <a
                  href={project.link}
                  className="inline-flex items-center gap-2 text-blue-600 hover:text-blue-700 transition-colors"
                >
                  View Project
                  <ExternalLink className="w-4 h-4" />
                </a>
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}