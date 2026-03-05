import { Hero } from './components/Hero';
import { About } from './components/About';
import { Skills } from './components/Skills';
import { Projects } from './components/Projects';
import { Contact } from './components/Contact';

function App() {
  return (
    <div className="bg-zinc-950 min-h-screen text-zinc-50 selection:bg-blue-500/30">
      <Hero />
      <About />
      <Skills />
      <Projects />
      <Contact />

      <footer className="py-8 text-center text-zinc-600 text-sm border-t border-zinc-900">
        <p>© {new Date().getFullYear()} Mahmoud Elbahie. All rights reserved.</p>
      </footer>
    </div>
  );
}

export default App;
