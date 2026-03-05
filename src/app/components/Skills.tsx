import { Code, Palette, Lightbulb, Briefcase } from 'lucide-react';

const skillCategories = [
  {
    icon: Code,
    title: 'Front-End Development',
    skills: ['HTML', 'CSS', 'JavaScript', 'React', 'TypeScript', 'Tailwind CSS']
  },
  {
    icon: Palette,
    title: 'Embedded Systems',
    skills: ['Microcontrollers', 'C/C++', 'Arduino', 'Hardware Integration', 'Sensor Integration', 'IoT']
  },
  {
    icon: Lightbulb,
    title: 'CNC & Automation',
    skills: ['CNC Programming', 'Manufacturing Systems', 'Automation Concepts', 'Control Systems', 'CAD/CAM', 'G-Code']
  },
  {
    icon: Briefcase,
    title: 'Professional',
    skills: ['Technical Instruction', 'Programming Fundamentals', 'Problem Solving', 'Team Collaboration', 'Project Management', 'Documentation']
  }
];

export function Skills() {
  return (
    <section id="skills" className="py-20 bg-white">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <h2 className="text-4xl md:text-5xl mb-12 text-center text-gray-900">
          Skills & Expertise
        </h2>
        
        <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-8">
          {skillCategories.map((category, index) => (
            <div
              key={index}
              className="p-6 bg-gradient-to-br from-gray-50 to-gray-100 rounded-2xl hover:shadow-xl transition-shadow"
            >
              <div className="w-12 h-12 bg-gradient-to-r from-blue-600 to-purple-600 rounded-lg flex items-center justify-center mb-4">
                <category.icon className="w-6 h-6 text-white" />
              </div>
              
              <h3 className="text-xl mb-4 text-gray-900">
                {category.title}
              </h3>
              
              <div className="flex flex-wrap gap-2">
                {category.skills.map((skill, skillIndex) => (
                  <span
                    key={skillIndex}
                    className="px-3 py-1 bg-white text-gray-700 rounded-full text-sm shadow-sm"
                  >
                    {skill}
                  </span>
                ))}
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}