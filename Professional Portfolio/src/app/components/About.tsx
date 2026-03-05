const profileImage = 'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?fit=crop&w=800&h=800';

export function About() {
  return (
    <section id="about" className="py-20 bg-white">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <h2 className="text-4xl md:text-5xl mb-12 text-center text-gray-900">
          About Me
        </h2>

        <div className="grid md:grid-cols-2 gap-12 items-center">
          <div className="order-2 md:order-1">
            <p className="text-lg text-gray-600 mb-6">
              I'm a CNC Engineering student at the Egypt-Japan University of Science and Technology (E-JUST)
              with hands-on experience in front-end web development and embedded systems. I connect engineering
              fundamentals with software implementation to build practical, cross-disciplinary solutions.
            </p>
            <p className="text-lg text-gray-600 mb-6">
              As an Embedded Systems Graduate from AMIT, I combine hardware expertise with software development
              skills. My experience as a former Fundamentals of Programming Instructor at iSchool has strengthened
              my ability to break down complex technical concepts and share knowledge effectively.
            </p>
            <p className="text-lg text-gray-600">
              I'm passionate about bridging the gap between mechanical engineering, embedded systems, and web
              technologies to create innovative solutions that make a real-world impact.
            </p>
          </div>

          <div className="order-1 md:order-2">
            <div className="rounded-2xl overflow-hidden shadow-2xl">
              <img
                src={profileImage}
                alt="Mahmoud Elbahie"
                className="w-full h-full object-cover"
              />
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}