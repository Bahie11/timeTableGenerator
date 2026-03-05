import { Github, Linkedin, Mail } from 'lucide-react';
import { useState } from 'react';
const profileImage = 'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?fit=crop&w=200&h=200';

export function Hero() {
  return (
    <section className="min-h-screen flex items-center justify-center bg-gradient-to-br from-gray-50 to-gray-100 pt-16">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20">
        <div className="text-center">
          <div className="mb-8">
            <img
              src={profileImage}
              alt="Mahmoud Elbahie"
              className="w-32 h-32 mx-auto rounded-full object-cover shadow-xl border-4 border-white"
            />
          </div>

          <h1 className="text-5xl md:text-7xl mb-6 text-gray-900">
            Hi, I'm <span className="text-transparent bg-clip-text bg-gradient-to-r from-blue-600 to-purple-600">Mahmoud Elbahie</span>
          </h1>

          <p className="text-xl md:text-2xl text-gray-600 mb-4 max-w-2xl mx-auto">
            CNC Student @ E-JUST | Front End Web Developer | Embedded Systems Graduate
          </p>

          <p className="text-lg text-gray-500 mb-8">
            📍 New Cairo, Egypt
          </p>

          <div className="flex items-center justify-center gap-6 mb-12">
            <a
              href="https://github.com"
              target="_blank"
              rel="noopener noreferrer"
              className="p-3 rounded-full bg-gray-900 text-white hover:bg-gray-700 transition-colors"
            >
              <Github className="w-6 h-6" />
            </a>
            <a
              href="https://linkedin.com"
              target="_blank"
              rel="noopener noreferrer"
              className="p-3 rounded-full bg-blue-600 text-white hover:bg-blue-700 transition-colors"
            >
              <Linkedin className="w-6 h-6" />
            </a>
            <a
              href="mailto:hello@example.com"
              className="p-3 rounded-full bg-purple-600 text-white hover:bg-purple-700 transition-colors"
            >
              <Mail className="w-6 h-6" />
            </a>
          </div>

          <button
            onClick={() => {
              const element = document.getElementById('work');
              if (element) element.scrollIntoView({ behavior: 'smooth' });
            }}
            className="px-8 py-4 bg-gray-900 text-white rounded-full hover:bg-gray-700 transition-all transform hover:scale-105"
          >
            View My Work
          </button>
        </div>
      </div>
    </section>
  );
}