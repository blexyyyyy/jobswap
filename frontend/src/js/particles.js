/**
 * Interactive Particles - Antigravity-style floating elements
 * White particles that react to mouse movement with physics
 */

class ParticleSystem {
    constructor() {
        this.canvas = document.createElement('canvas');
        this.ctx = this.canvas.getContext('2d');
        this.particles = [];
        this.mouse = { x: null, y: null, radius: 150 };
        this.particleCount = 80;

        this.init();
    }

    init() {
        // Style canvas
        this.canvas.id = 'particle-canvas';
        this.canvas.style.cssText = `
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            pointer-events: none;
            z-index: 0;
        `;

        document.body.insertBefore(this.canvas, document.body.firstChild);

        this.resize();
        this.createParticles();
        this.bindEvents();
        this.animate();
    }

    resize() {
        this.canvas.width = window.innerWidth;
        this.canvas.height = window.innerHeight;
    }

    createParticles() {
        this.particles = [];

        for (let i = 0; i < this.particleCount; i++) {
            this.particles.push({
                x: Math.random() * this.canvas.width,
                y: Math.random() * this.canvas.height,
                baseX: 0,
                baseY: 0,
                size: Math.random() * 3 + 1,
                speedX: (Math.random() - 0.5) * 0.5,
                speedY: (Math.random() - 0.5) * 0.5,
                opacity: Math.random() * 0.5 + 0.2,
                // Physics properties
                vx: 0,
                vy: 0,
                friction: 0.98,
                ease: 0.03
            });
        }

        // Store base positions
        this.particles.forEach(p => {
            p.baseX = p.x;
            p.baseY = p.y;
        });
    }

    bindEvents() {
        window.addEventListener('resize', () => {
            this.resize();
            this.createParticles();
        });

        window.addEventListener('mousemove', (e) => {
            this.mouse.x = e.clientX;
            this.mouse.y = e.clientY;
        });

        window.addEventListener('mouseout', () => {
            this.mouse.x = null;
            this.mouse.y = null;
        });
    }

    animate() {
        this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);

        this.particles.forEach((particle, i) => {
            // Floating movement
            particle.baseX += particle.speedX;
            particle.baseY += particle.speedY;

            // Wrap around edges
            if (particle.baseX < 0) particle.baseX = this.canvas.width;
            if (particle.baseX > this.canvas.width) particle.baseX = 0;
            if (particle.baseY < 0) particle.baseY = this.canvas.height;
            if (particle.baseY > this.canvas.height) particle.baseY = 0;

            // Mouse interaction - antigravity effect
            if (this.mouse.x !== null && this.mouse.y !== null) {
                const dx = this.mouse.x - particle.x;
                const dy = this.mouse.y - particle.y;
                const distance = Math.sqrt(dx * dx + dy * dy);

                if (distance < this.mouse.radius) {
                    // Push particles away from cursor (antigravity)
                    const force = (this.mouse.radius - distance) / this.mouse.radius;
                    const angle = Math.atan2(dy, dx);

                    particle.vx -= Math.cos(angle) * force * 2;
                    particle.vy -= Math.sin(angle) * force * 2;
                }
            }

            // Apply friction and ease back to base position
            particle.vx *= particle.friction;
            particle.vy *= particle.friction;

            particle.vx += (particle.baseX - particle.x) * particle.ease;
            particle.vy += (particle.baseY - particle.y) * particle.ease;

            particle.x += particle.vx;
            particle.y += particle.vy;

            // Draw particle
            this.ctx.beginPath();
            this.ctx.arc(particle.x, particle.y, particle.size, 0, Math.PI * 2);
            this.ctx.fillStyle = `rgba(255, 255, 255, ${particle.opacity})`;
            this.ctx.fill();

            // Draw connections to nearby particles
            for (let j = i + 1; j < this.particles.length; j++) {
                const other = this.particles[j];
                const distX = particle.x - other.x;
                const distY = particle.y - other.y;
                const dist = Math.sqrt(distX * distX + distY * distY);

                if (dist < 120) {
                    const opacity = (1 - dist / 120) * 0.15;
                    this.ctx.beginPath();
                    this.ctx.strokeStyle = `rgba(255, 255, 255, ${opacity})`;
                    this.ctx.lineWidth = 0.5;
                    this.ctx.moveTo(particle.x, particle.y);
                    this.ctx.lineTo(other.x, other.y);
                    this.ctx.stroke();
                }
            }
        });

        requestAnimationFrame(() => this.animate());
    }
}

// Initialize particles when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    new ParticleSystem();
});
