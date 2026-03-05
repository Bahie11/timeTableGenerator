import profileImage from '../../assets/profile.png';

export function About() {
  return (
    <section id="about" className="py-20 relative overflow-hidden" style={{ background: 'linear-gradient(180deg, #0a0a0f 0%, #0d1117 100%)' }}>

      {/* Decorative glow */}
      <div className="absolute top-0 right-0 w-72 h-72 bg-purple-500/10 rounded-full blur-3xl pointer-events-none" />
      <div className="absolute bottom-0 left-0 w-72 h-72 bg-cyan-500/10 rounded-full blur-3xl pointer-events-none" />

      <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <h2 className="text-4xl md:text-5xl mb-4 text-center font-bold text-white">
          About <span className="bg-gradient-to-r from-cyan-400 to-purple-500 bg-clip-text text-transparent">Me</span>
        </h2>
        <p className="text-center text-cyan-400/60 mb-12 tracking-widest text-sm uppercase">Who I Am</p>

        <div className="grid md:grid-cols-2 gap-12 items-start">
          <div className="order-2 md:order-1 space-y-5">
            <p className="text-gray-300 leading-relaxed">
              I am a passionate and detail-oriented <span className="text-cyan-400 font-medium">Penetration Tester</span> with a strong foundation in networking, cybersecurity principles, and ethical hacking methodologies. My goal is to help organizations identify vulnerabilities before attackers do, strengthen their security posture, and build resilient systems against modern cyber threats.
            </p>
            <p className="text-gray-400 leading-relaxed">
              I have successfully completed the <span className="text-purple-400 font-medium">Cisco Certified Network Associate (CCNA)</span> coursework, gaining solid knowledge in networking fundamentals, routing and switching, network security, IP services, and troubleshooting.
            </p>
            <p className="text-gray-400 leading-relaxed">
              In addition, I completed professional penetration testing training at <span className="text-pink-400 font-medium">DEPI (Digital Egypt Pioneers Initiative)</span>, gaining hands-on experience in vulnerability assessment, web application testing, network penetration testing, privilege escalation, and security reporting.
            </p>
            <p className="text-gray-400 leading-relaxed">
              I am continuously learning and staying updated with emerging threats, security tools, and best practices. I am driven by curiosity, persistence, and a commitment to ethical standards in cybersecurity.
            </p>
          </div>

          <div className="order-1 md:order-2 space-y-4">
            {/* Profile image */}
            <div className="rounded-2xl overflow-hidden shadow-2xl border border-cyan-500/20 mb-6 relative">
              <div className="absolute inset-0 bg-gradient-to-t from-[#0a0a0f] via-transparent to-transparent z-10" />
              <img
                src={profileImage}
                alt="Mahmoud Elbahie"
                className="w-full h-64 object-cover"
              />
            </div>

            {/* Certifications */}
            <div className="rounded-2xl border border-purple-500/20 bg-purple-500/5 p-6">
              <p className="text-purple-400 font-semibold mb-4 uppercase tracking-wider text-sm">Relevant Courses & Certifications</p>
              <ul className="space-y-2">
                {[
                  'CCNA – Cisco Certified Network Associate',
                  'Network Security Fundamentals',
                  'Ethical Hacking & Penetration Testing',
                  'Web Application Penetration Testing',
                  'Vulnerability Assessment & Exploitation',
                  'Linux for Cybersecurity',
                  'Python for Security Professionals',
                  'OWASP Top 10 & Web Security Testing',
                  'DEPI – Penetration Testing Track',
                ].map((cert, i) => (
                  <li key={i} className="flex items-start gap-2 text-gray-300 text-sm">
                    <span className="text-cyan-400 mt-0.5 flex-shrink-0">▸</span>
                    {cert}
                  </li>
                ))}
              </ul>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}