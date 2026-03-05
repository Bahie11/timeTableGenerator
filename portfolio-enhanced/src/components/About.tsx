import { motion } from 'framer-motion';
import profileImage from '../assets/profile.jpg';

export function About() {
    return (
        <section className="py-32 bg-zinc-950 px-4">
            <div className="max-w-6xl mx-auto flex flex-col md:flex-row gap-16 items-center">
                <motion.div
                    initial={{ opacity: 0, x: -20 }}
                    whileInView={{ opacity: 1, x: 0 }}
                    viewport={{ once: true }}
                    className="flex-1"
                >
                    <div className="relative aspect-square max-w-md mx-auto rounded-3xl overflow-hidden grayscale hover:grayscale-0 transition-all duration-500">
                        <img
                            src={profileImage}
                            alt="Profile"
                            className="object-cover w-full h-full"
                        />
                    </div>
                </motion.div>

                <motion.div
                    initial={{ opacity: 0, x: 20 }}
                    whileInView={{ opacity: 1, x: 0 }}
                    viewport={{ once: true }}
                    className="flex-1"
                >
                    <h2 className="text-3xl md:text-5xl font-bold text-white mb-8">Engineering Logic <br /><span className="text-blue-500">Creative Design</span></h2>

                    <div className="space-y-6 text-lg text-zinc-400">
                        <p>
                            I'm a CNC Engineering student at the Egypt-Japan University of Science and Technology (E-JUST)
                            with hands-on experience in front-end web development and embedded systems. I connect engineering
                            fundamentals with software implementation to build practical, cross-disciplinary solutions.
                        </p>
                        <p>
                            As an Embedded Systems Graduate from AMIT, I combine hardware expertise with software development
                            skills. My experience as a former Fundamentals of Programming Instructor at iSchool has strengthened
                            my ability to break down complex technical concepts.
                        </p>
                    </div>
                </motion.div>
            </div>
        </section>
    );
}
