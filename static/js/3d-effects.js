/**
 * FleetFlow - 3D Effects & Animations
 * Three.js powered background animations and interactive 3D effects
 */

(function() {
    'use strict';

    // ==========================================================================
    // 3D Background Scene
    // ==========================================================================

    let bgScene = null;
    let bgCamera = null;
    let bgRenderer = null;
    let bgParticles = [];
    let bgGeometries = [];
    let animationId = null;
    let mouseX = 0;
    let mouseY = 0;
    let targetX = 0;
    let targetY = 0;
    let isReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

    const BG_CONFIG = {
        particleCount: 80,
        geometryCount: 12,
        floatSpeed: 0.0008,
        rotateSpeed: 0.0003,
        mouseInfluence: 0.02,
        colors: {
            light: [0x2860E8, 0x087B59, 0xB86B00, 0xD92D20],
            dark: [0x4A80F0, 0x22C55E, 0xFBBF24, 0xF87171]
        }
    };

    function init3DBackground() {
        const canvas = document.getElementById('bg-canvas');
        if (!canvas || isReducedMotion) return;

        const width = window.innerWidth;
        const height = window.innerHeight;

        // Scene
        bgScene = new THREE.Scene();

        // Camera
        bgCamera = new THREE.PerspectiveCamera(60, width / height, 1, 1000);
        bgCamera.position.z = 50;

        // Renderer
        bgRenderer = new THREE.WebGLRenderer({
            canvas: canvas,
            alpha: true,
            antialias: true
        });
        bgRenderer.setSize(width, height);
        bgRenderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));

        // Create particles
        createParticles();
        createFloatingGeometries();

        // Event listeners
        window.addEventListener('resize', onResize);
        document.addEventListener('mousemove', onMouseMove);

        // Start animation
        animate();

        // Expose for cleanup
        window.FleetFlow3D = {
            destroy: destroy3DBackground,
            scene: bgScene,
            camera: bgCamera,
            renderer: bgRenderer
        };
    }

    function createParticles() {
        const geometry = new THREE.BufferGeometry();
        const positions = new Float32Array(BG_CONFIG.particleCount * 3);
        const sizes = new Float32Array(BG_CONFIG.particleCount);
        const alphas = new Float32Array(BG_CONFIG.particleCount);
        const colorIndices = new Float32Array(BG_CONFIG.particleCount);

        const isDark = document.documentElement.getAttribute('data-theme') === 'dark';
        const colors = BG_CONFIG.colors[isDark ? 'dark' : 'light'];

        for (let i = 0; i < BG_CONFIG.particleCount; i++) {
            positions[i * 3] = (Math.random() - 0.5) * 120;
            positions[i * 3 + 1] = (Math.random() - 0.5) * 120;
            positions[i * 3 + 2] = (Math.random() - 0.5) * 120 - 20;
            sizes[i] = Math.random() * 3 + 1;
            alphas[i] = Math.random() * 0.5 + 0.1;
            colorIndices[i] = Math.floor(Math.random() * colors.length);
            bgParticles.push({
                x: positions[i * 3],
                y: positions[i * 3 + 1],
                z: positions[i * 3 + 2],
                vx: (Math.random() - 0.5) * 0.02,
                vy: (Math.random() - 0.5) * 0.02,
                vz: (Math.random() - 0.5) * 0.02,
                size: sizes[i],
                alpha: alphas[i],
                colorIndex: colorIndices[i],
                originalX: positions[i * 3],
                originalY: positions[i * 3 + 1],
                originalZ: positions[i * 3 + 2]
            });
        }

        geometry.setAttribute('position', new THREE.BufferAttribute(positions, 3));
        geometry.setAttribute('size', new THREE.BufferAttribute(sizes, 1));
        geometry.setAttribute('alpha', new THREE.BufferAttribute(alphas, 1));
        geometry.setAttribute('colorIndex', new THREE.BufferAttribute(colorIndices, 1));

        const material = new THREE.PointsMaterial({
            size: 1,
            vertexColors: false,
            transparent: true,
            opacity: 0.6,
            blending: THREE.AdditiveBlending,
            depthWrite: false
        });

        const points = new THREE.Points(geometry, material);
        points.userData = { type: 'particles', particles: bgParticles };
        bgScene.add(points);
    }

    function createFloatingGeometries() {
        const isDark = document.documentElement.getAttribute('data-theme') === 'dark';
        const colors = BG_CONFIG.colors[isDark ? 'dark' : 'light'];
        const geometries = [
            new THREE.OctahedronGeometry(2, 0),
            new THREE.TetrahedronGeometry(2, 0),
            new THREE.IcosahedronGeometry(1.5, 0),
            new THREE.BoxGeometry(2, 2, 2, 1, 1, 1),
            new THREE.DodecahedronGeometry(1.8, 0)
        ];

        for (let i = 0; i < BG_CONFIG.geometryCount; i++) {
            const geo = geometries[Math.floor(Math.random() * geometries.length)];
            const color = colors[Math.floor(Math.random() * colors.length)];
            
            const material = new THREE.MeshBasicMaterial({
                color: color,
                wireframe: true,
                transparent: true,
                opacity: 0.15,
                side: THREE.DoubleSide
            });

            const mesh = new THREE.Mesh(geo, material);
            mesh.position.set(
                (Math.random() - 0.5) * 100,
                (Math.random() - 0.5) * 100,
                (Math.random() - 0.5) * 60 - 30
            );
            mesh.rotation.set(
                Math.random() * Math.PI,
                Math.random() * Math.PI,
                Math.random() * Math.PI
            );
            mesh.userData = {
                rotationSpeed: {
                    x: (Math.random() - 0.5) * BG_CONFIG.rotateSpeed * 2,
                    y: (Math.random() - 0.5) * BG_CONFIG.rotateSpeed * 2,
                    z: (Math.random() - 0.5) * BG_CONFIG.rotateSpeed
                },
                floatOffset: Math.random() * Math.PI * 2,
                floatSpeed: BG_CONFIG.floatSpeed * (0.5 + Math.random() * 0.5),
                amplitude: 5 + Math.random() * 10,
                originalY: mesh.position.y
            };
            bgGeometries.push(mesh);
            bgScene.add(mesh);
        }
    }

    function onMouseMove(event) {
        mouseX = (event.clientX / window.innerWidth) * 2 - 1;
        mouseY = -(event.clientY / window.innerHeight) * 2 + 1;
    }

    function onResize() {
        if (!bgCamera || !bgRenderer) return;
        
        const width = window.innerWidth;
        const height = window.innerHeight;
        
        bgCamera.aspect = width / height;
        bgCamera.updateProjectionMatrix();
        bgRenderer.setSize(width, height);
    }

    function animate() {
        if (isReducedMotion) return;
        
        animationId = requestAnimationFrame(animate);
        
        // Smooth mouse follow
        targetX += (mouseX - targetX) * 0.05;
        targetY += (mouseY - targetY) * 0.05;
        
        // Camera subtle movement
        if (bgCamera) {
            bgCamera.position.x += (targetX * 3 - bgCamera.position.x) * 0.02;
            bgCamera.position.y += (targetY * 3 - bgCamera.position.y) * 0.02;
            bgCamera.lookAt(0, 0, 0);
        }

        // Animate particles
        const time = Date.now() * 0.001;
        bgScene.traverse((object) => {
            if (object.userData.type === 'particles') {
                const particles = object.userData.particles;
                const positions = object.geometry.attributes.position.array;
                
                particles.forEach((p, i) => {
                    // Floating motion
                    p.x = p.originalX + Math.sin(time * p.floatSpeed + p.floatOffset) * 3;
                    p.y = p.originalY + Math.cos(time * p.floatSpeed + p.floatOffset) * 2;
                    p.z = p.originalZ + Math.sin(time * p.floatSpeed * 0.7 + p.floatOffset) * 2;
                    
                    // Mouse influence
                    p.x += targetX * BG_CONFIG.mouseInfluence * 20;
                    p.y += targetY * BG_CONFIG.mouseInfluence * 20;
                    
                    // Boundary wrap
                    if (p.x > 60) p.x = -60;
                    if (p.x < -60) p.x = 60;
                    if (p.y > 60) p.y = -60;
                    if (p.y < -60) p.y = 60;
                    
                    positions[i * 3] = p.x;
                    positions[i * 3 + 1] = p.y;
                    positions[i * 3 + 2] = p.z;
                });
                object.geometry.attributes.position.needsUpdate = true;
            }
            
            // Animate floating geometries
            if (object.userData.rotationSpeed) {
                const ud = object.userData;
                object.rotation.x += ud.rotationSpeed.x;
                object.rotation.y += ud.rotationSpeed.y;
                object.rotation.z += ud.rotationSpeed.z;
                
                object.position.y = ud.originalY + Math.sin(time * ud.floatSpeed + ud.floatOffset) * ud.amplitude;
                object.position.x += Math.sin(time * ud.floatSpeed * 0.5 + ud.floatOffset) * 0.3;
            }
        });
        
        if (bgRenderer && bgScene && bgCamera) {
            bgRenderer.render(bgScene, bgCamera);
        }
    }

    function destroy3DBackground() {
        if (animationId) cancelAnimationFrame(animationId);
        window.removeEventListener('resize', onResize);
        document.removeEventListener('mousemove', onMouseMove);
        
        if (bgScene) {
            bgScene.traverse((object) => {
                if (object.geometry) object.geometry.dispose();
                if (object.material) {
                    if (Array.isArray(object.material)) {
                        object.material.forEach(m => m.dispose());
                    } else {
                        object.material.dispose();
                    }
                }
            });
        }
        if (bgRenderer) bgRenderer.dispose();
        
        bgScene = null;
        bgCamera = null;
        bgRenderer = null;
        bgParticles = [];
        bgGeometries = [];
    }

    // ==========================================================================
    // 3D Card Hover Effects (CSS-based)
    // ==========================================================================

    function init3DCardEffects() {
        if (isReducedMotion) return;
        
        const cards = document.querySelectorAll('.stat-card, .vehicle-card, .card, .form-card, .summary-card');
        
        cards.forEach(card => {
            card.addEventListener('mousemove', handleCardTilt);
            card.addEventListener('mouseleave', handleCardLeave);
            card.addEventListener('mouseenter', handleCardEnter);
        });
    }

    function handleCardTilt(e) {
        const card = e.currentTarget;
        const rect = card.getBoundingClientRect();
        const x = e.clientX - rect.left;
        const y = e.clientY - rect.top;
        const centerX = rect.width / 2;
        const centerY = rect.height / 2;
        const rotateX = ((y - centerY) / centerY) * -8;
        const rotateY = ((x - centerX) / centerX) * 8;
        
        card.style.transform = `perspective(1000px) rotateX(${rotateX}deg) rotateY(${rotateY}deg) translateZ(10px)`;
        card.style.boxShadow = `
            ${10 + Math.abs(rotateY)}px ${10 + Math.abs(rotateX)}px 30px -10px rgba(23, 32, 51, 0.15),
            ${5 + Math.abs(rotateY)}px ${5 + Math.abs(rotateX)}px 15px -5px rgba(23, 32, 51, 0.08)
        `;
    }

    function handleCardLeave(e) {
        const card = e.currentTarget;
        card.style.transform = 'perspective(1000px) rotateX(0) rotateY(0) translateZ(0)';
        card.style.boxShadow = '';
        card.style.transition = 'transform 0.4s cubic-bezier(0.23, 1, 0.32, 1), box-shadow 0.4s ease';
    }

    function handleCardEnter(e) {
        const card = e.currentTarget;
        card.style.transition = 'transform 0.1s ease, box-shadow 0.1s ease';
    }

    // ==========================================================================
    // 3D Button Effects
    // ==========================================================================

    function init3DButtonEffects() {
        if (isReducedMotion) return;
        
        const buttons = document.querySelectorAll('.btn:not(.btn-ghost), .icon-btn, .nav-step-link, .user-menu-btn');
        
        buttons.forEach(btn => {
            btn.addEventListener('mousedown', handleButtonPress);
            btn.addEventListener('mouseup', handleButtonRelease);
            btn.addEventListener('mouseleave', handleButtonRelease);
        });
    }

    function handleButtonPress(e) {
        const btn = e.currentTarget;
        btn.style.transform = 'translateZ(-2px) scale(0.98)';
        btn.style.transition = 'transform 0.05s ease';
    }

    function handleButtonRelease(e) {
        const btn = e.currentTarget;
        btn.style.transform = 'translateZ(0) scale(1)';
        btn.style.transition = 'transform 0.2s cubic-bezier(0.23, 1, 0.32, 1)';
    }

    // ==========================================================================
    // 3D Stat Counter Animation
    // ==========================================================================

    function initStatCounters() {
        const statValues = document.querySelectorAll('.stat-value');
        
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    animateCounter(entry.target);
                    observer.unobserve(entry.target);
                }
            });
        }, { threshold: 0.5 });
        
        statValues.forEach(el => observer.observe(el));
    }

    function animateCounter(element) {
        const text = element.textContent.trim();
        const isCurrency = text.includes('₹') || text.includes('$');
        const isFormatted = text.includes(',');
        const numText = text.replace(/[₹$,]/g, '');
        const target = parseFloat(numText);
        
        if (isNaN(target)) return;
        
        const duration = 1500;
        const startTime = performance.now();
        const isDecimal = numText.includes('.');
        
        function updateCounter(currentTime) {
            const elapsed = currentTime - startTime;
            const progress = Math.min(elapsed / duration, 1);
            const eased = 1 - Math.pow(1 - progress, 3);
            const current = target * eased;
            
            let displayValue = isDecimal ? current.toFixed(2) : Math.floor(current).toString();
            if (isFormatted) {
                displayValue = Number(displayValue).toLocaleString();
            }
            if (isCurrency) {
                displayValue = '₹' + displayValue;
            }
            
            element.textContent = displayValue;
            
            if (progress < 1) {
                requestAnimationFrame(updateCounter);
            }
        }
        
        requestAnimationFrame(updateCounter);
    }

    // ==========================================================================
    // Floating 3D Icons for Dashboard
    // ==========================================================================

    function createFloatingIcons() {
        const container = document.querySelector('.page-header');
        if (!container || isReducedMotion) return;
        
        const icons = [
            { icon: 'truck', color: 'var(--color-primary)', delay: 0 },
            { icon: 'calendar', color: 'var(--color-success)', delay: 1000 },
            { icon: 'dollar-sign', color: 'var(--color-warning)', delay: 2000 },
            { icon: 'map-pin', color: 'var(--color-danger)', delay: 3000 }
        ];
        
        const floatingContainer = document.createElement('div');
        floatingContainer.className = 'floating-icons-3d';
        floatingContainer.style.cssText = `
            position: absolute;
            top: 0; left: 0; right: 0; bottom: 0;
            pointer-events: none;
            overflow: hidden;
            z-index: 0;
        `;
        
        icons.forEach((iconData, i) => {
            const iconEl = document.createElement('div');
            iconEl.className = 'floating-icon-3d';
            iconEl.innerHTML = `<i data-lucide="${iconData.icon}" style="width: 48px; height: 48px; color: ${iconData.color}; filter: drop-shadow(0 4px 12px ${iconData.color}40);"></i>`;
            iconEl.style.cssText = `
                position: absolute;
                opacity: 0.15;
                animation: floatIcon3d ${8 + i * 2}s ease-in-out infinite;
                animation-delay: ${iconData.delay}ms;
                transform-style: preserve-3d;
            `;
            
            // Random position
            iconEl.style.left = `${10 + Math.random() * 80}%`;
            iconEl.style.top = `${20 + Math.random() * 60}%`;
            
            floatingContainer.appendChild(iconEl);
        });
        
        container.style.position = 'relative';
        container.appendChild(floatingContainer);
        
        // Add keyframes
        if (!document.getElementById('floating-3d-styles')) {
            const style = document.createElement('style');
            style.id = 'floating-3d-styles';
            style.textContent = `
                @keyframes floatIcon3d {
                    0%, 100% {
                        transform: translate3d(0, 0, 0) rotateX(0deg) rotateY(0deg);
                    }
                    25% {
                        transform: translate3d(20px, -30px, 20px) rotateX(15deg) rotateY(20deg);
                    }
                    50% {
                        transform: translate3d(-15px, 20px, -10px) rotateX(-10deg) rotateY(-15deg);
                    }
                    75% {
                        transform: translate3d(30px, 10px, 15px) rotateX(20deg) rotateY(10deg);
                    }
                }
            `;
            document.head.appendChild(style);
        }
        
        // Re-initialize icons
        if (window.lucide) {
            window.lucide.createIcons();
        }
    }

    // ==========================================================================
    // 3D Page Transition Effect
    // ==========================================================================

    function initPageTransitions() {
        const mainContent = document.querySelector('.main-content');
        if (!mainContent || isReducedMotion) return;
        
        mainContent.style.opacity = '0';
        mainContent.style.transform = 'translate3d(0, 20px, -50px) rotateX(5deg)';
        mainContent.style.transition = 'opacity 0.6s cubic-bezier(0.23, 1, 0.32, 1), transform 0.6s cubic-bezier(0.23, 1, 0.32, 1)';
        
        requestAnimationFrame(() => {
            mainContent.style.opacity = '1';
            mainContent.style.transform = 'translate3d(0, 0, 0) rotateX(0)';
        });
    }

    // ==========================================================================
    // 3D Notification/Toast Effects
    // ==========================================================================

    function enhanceFlashMessages() {
        const flashMessages = document.querySelectorAll('.flash-message');
        
        flashMessages.forEach((msg, i) => {
            msg.style.opacity = '0';
            msg.style.transform = 'translate3d(100px, 0, -50px) rotateY(15deg)';
            msg.style.transition = `opacity 0.4s cubic-bezier(0.23, 1, 0.32, 1), transform 0.4s cubic-bezier(0.23, 1, 0.32, 1)`;
            msg.style.transitionDelay = `${i * 100}ms`;
            
            requestAnimationFrame(() => {
                msg.style.opacity = '1';
                msg.style.transform = 'translate3d(0, 0, 0) rotateY(0)';
            });
        });
    }

    // ==========================================================================
    // 3D Modal Effects
    // ==========================================================================

    function enhanceModals() {
        const modals = document.querySelectorAll('.modal-overlay');
        
        modals.forEach(modal => {
            const modalEl = modal.querySelector('.modal');
            if (!modalEl) return;
            
            const observer = new MutationObserver(() => {
                if (!modal.hidden) {
                    modalEl.style.opacity = '0';
                    modalEl.style.transform = 'translate3d(0, 20px, -100px) scale(0.9) rotateX(10deg)';
                    modalEl.style.transition = 'opacity 0.3s cubic-bezier(0.23, 1, 0.32, 1), transform 0.3s cubic-bezier(0.23, 1, 0.32, 1)';
                    
                    requestAnimationFrame(() => {
                        modalEl.style.opacity = '1';
                        modalEl.style.transform = 'translate3d(0, 0, 0) scale(1) rotateX(0)';
                    });
                }
            });
            
            observer.observe(modal, { attributes: true, attributeFilter: ['hidden'] });
        });
    }

    // ==========================================================================
    // 3D Dropdown Effects
    // ==========================================================================

    function enhanceDropdowns() {
        const dropdowns = document.querySelectorAll('.notification-dropdown, .user-menu-dropdown');
        
        dropdowns.forEach(dropdown => {
            const observer = new MutationObserver(() => {
                if (!dropdown.hidden) {
                    dropdown.style.opacity = '0';
                    dropdown.style.transform = 'translate3d(0, -10px, -20px) rotateX(-10deg) scale(0.95)';
                    dropdown.style.transition = 'opacity 0.2s ease, transform 0.2s cubic-bezier(0.23, 1, 0.32, 1)';
                    
                    requestAnimationFrame(() => {
                        dropdown.style.opacity = '1';
                        dropdown.style.transform = 'translate3d(0, 0, 0) rotateX(0) scale(1)';
                    });
                }
            });
            
            observer.observe(dropdown, { attributes: true, attributeFilter: ['hidden'] });
        });
    }

    // ==========================================================================
    // Theme Change Handler for 3D Colors
    // ==========================================================================

    function handleThemeChange() {
        const observer = new MutationObserver((mutations) => {
            mutations.forEach(mutation => {
                if (mutation.attributeName === 'data-theme') {
                    recreate3DScene();
                }
            });
        });
        
        observer.observe(document.documentElement, { attributes: true, attributeFilter: ['data-theme'] });
    }

    function recreate3DBackground() {
        destroy3DBackground();
        setTimeout(init3DBackground, 100);
    }

    function recreate3DScene() {
        if (window.FleetFlow3D) {
            recreate3DBackground();
        }
    }

    // ==========================================================================
    // Initialize All 3D Effects
    // ==========================================================================

    function init() {
        if (isReducedMotion) {
            console.log('3D effects disabled: prefers-reduced-motion');
            return;
        }
        
        // Wait for Three.js to load
        if (typeof THREE === 'undefined') {
            setTimeout(init, 100);
            return;
        }
        
        init3DBackground();
        init3DCardEffects();
        init3DButtonEffects();
        initStatCounters();
        createFloatingIcons();
        initPageTransitions();
        enhanceFlashMessages();
        enhanceModals();
        enhanceDropdowns();
        handleThemeChange();
        
        console.log('FleetFlow 3D Effects initialized');
    }

    // Run on DOM ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }

    // Re-initialize on dynamic content
    const observer = new MutationObserver(() => {
        init3DCardEffects();
        init3DButtonEffects();
        enhanceFlashMessages();
    });
    observer.observe(document.body, { childList: true, subtree: true });
})();