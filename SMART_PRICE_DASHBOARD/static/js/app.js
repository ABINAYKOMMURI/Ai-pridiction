/* ═══════════════════════════════════════════════════════════════════════
   SMART PRICE DASHBOARD — Frontend JavaScript
   ═══════════════════════════════════════════════════════════════════════ */

document.addEventListener('DOMContentLoaded', function () {

    // ── 1. Loading Screen ────────────────────────────────────────────────
    const loader = document.getElementById('loading-overlay');
    if (loader) {
        window.addEventListener('load', () => {
            setTimeout(() => {
                loader.style.opacity = '0';
                setTimeout(() => loader.remove(), 500);
            }, 400);
        });
    }

    // ── 2. Navbar Active State ───────────────────────────────────────────
    const currentPath = window.location.pathname;
    document.querySelectorAll('.navbar-nav .nav-link').forEach(link => {
        const href = link.getAttribute('href');
        if (href === currentPath) {
            link.classList.add('active');
        }
    });

    // ── 3. Scroll Animation (Intersection Observer) ──────────────────────
    const observerOptions = {
        root: null,
        rootMargin: '0px',
        threshold: 0.1
    };

    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('animate-fade-in-up');
                entry.target.style.opacity = '1';
                observer.unobserve(entry.target);
            }
        });
    }, observerOptions);

    document.querySelectorAll('.observe-animate').forEach(el => {
        el.style.opacity = '0';
        observer.observe(el);
    });

    // ── 4. Counter Animation ─────────────────────────────────────────────
    function animateCounter(el) {
        const target = parseFloat(el.getAttribute('data-count'));
        const suffix = el.getAttribute('data-suffix') || '';
        const prefix = el.getAttribute('data-prefix') || '';
        const decimals = el.getAttribute('data-decimals') ? parseInt(el.getAttribute('data-decimals')) : 0;
        const duration = 2000;
        const startTime = performance.now();

        function update(currentTime) {
            const elapsed = currentTime - startTime;
            const progress = Math.min(elapsed / duration, 1);
            // Ease-out cubic
            const eased = 1 - Math.pow(1 - progress, 3);
            const current = eased * target;

            el.textContent = prefix + current.toFixed(decimals).replace(/\B(?=(\d{3})+(?!\d))/g, ',') + suffix;

            if (progress < 1) {
                requestAnimationFrame(update);
            }
        }

        requestAnimationFrame(update);
    }

    const counterObserver = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                animateCounter(entry.target);
                counterObserver.unobserve(entry.target);
            }
        });
    }, { threshold: 0.3 });

    document.querySelectorAll('.counter').forEach(el => {
        counterObserver.observe(el);
    });

    // ── 5. Plotly Chart Rendering ────────────────────────────────────────
    document.querySelectorAll('.plotly-chart').forEach(container => {
        const chartDataEl = container.getAttribute('data-chart');
        if (chartDataEl) {
            try {
                const chartData = JSON.parse(document.getElementById(chartDataEl).textContent);
                const config = {
                    responsive: true,
                    displayModeBar: true,
                    displaylogo: false,
                    modeBarButtonsToRemove: ['lasso2d', 'select2d'],
                    toImageButtonOptions: {
                        format: 'png',
                        filename: chartDataEl,
                        scale: 2
                    }
                };
                Plotly.newPlot(container, chartData.data, chartData.layout, config);
            } catch (e) {
                console.error('Chart render error:', chartDataEl, e);
                container.innerHTML = '<p class="text-center text-muted p-4">Error loading chart</p>';
            }
        }
    });

    // ── 6. CSV Upload Drag & Drop ────────────────────────────────────────
    const uploadZone = document.getElementById('upload-zone');
    const csvInput = document.getElementById('csv_file');

    if (uploadZone && csvInput) {
        uploadZone.addEventListener('click', () => csvInput.click());

        uploadZone.addEventListener('dragover', (e) => {
            e.preventDefault();
            uploadZone.classList.add('drag-over');
        });

        uploadZone.addEventListener('dragleave', () => {
            uploadZone.classList.remove('drag-over');
        });

        uploadZone.addEventListener('drop', (e) => {
            e.preventDefault();
            uploadZone.classList.remove('drag-over');
            if (e.dataTransfer.files.length > 0) {
                csvInput.files = e.dataTransfer.files;
                const fileName = e.dataTransfer.files[0].name;
                uploadZone.querySelector('h5').textContent = fileName;
                uploadZone.querySelector('p').textContent = 'File ready to upload';
            }
        });

        csvInput.addEventListener('change', () => {
            if (csvInput.files.length > 0) {
                uploadZone.querySelector('h5').textContent = csvInput.files[0].name;
                uploadZone.querySelector('p').textContent = 'File ready to upload';
            }
        });
    }

    // ── 7. Form Calculation Preview ──────────────────────────────────────
    const prevPriceInput = document.getElementById('previous_price');
    const currPriceInput = document.getElementById('current_price');
    const growthPreview   = document.getElementById('growth-preview');
    const futurePreview   = document.getElementById('future-preview');

    function updatePricePreview() {
        if (prevPriceInput && currPriceInput && growthPreview && futurePreview) {
            const prev = parseFloat(prevPriceInput.value) || 0;
            const curr = parseFloat(currPriceInput.value) || 0;

            if (prev > 0 && curr > 0) {
                const growthRate = (curr - prev) / prev;
                const futurePrice = curr * Math.pow(1 + growthRate, 3);

                growthPreview.textContent = (growthRate * 100).toFixed(2) + '%';
                growthPreview.className = growthRate >= 0 ? 'positive mono fw-bold' : 'negative mono fw-bold';

                futurePreview.textContent = '₹' + futurePrice.toFixed(2).replace(/\B(?=(\d{3})+(?!\d))/g, ',');
                futurePreview.className = 'text-accent-yellow mono fw-bold';
            } else {
                growthPreview.textContent = '—';
                futurePreview.textContent = '—';
            }
        }
    }

    if (prevPriceInput) prevPriceInput.addEventListener('input', updatePricePreview);
    if (currPriceInput) currPriceInput.addEventListener('input', updatePricePreview);

    // ── 8. Hero Particles ────────────────────────────────────────────────
    const particlesBg = document.querySelector('.particles-bg');
    if (particlesBg) {
        for (let i = 0; i < 30; i++) {
            const particle = document.createElement('div');
            particle.classList.add('particle');
            particle.style.left = Math.random() * 100 + '%';
            particle.style.animationDuration = (8 + Math.random() * 15) + 's';
            particle.style.animationDelay = (Math.random() * 10) + 's';
            particle.style.width = (2 + Math.random() * 4) + 'px';
            particle.style.height = particle.style.width;
            particle.style.opacity = (0.1 + Math.random() * 0.4);
            particlesBg.appendChild(particle);
        }
    }

    // ── 9. Smooth Scroll ─────────────────────────────────────────────────
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({ behavior: 'smooth', block: 'start' });
            }
        });
    });

    // ── 10. Flash Message Auto-dismiss ───────────────────────────────────
    document.querySelectorAll('.alert-dismissible').forEach(alert => {
        setTimeout(() => {
            alert.style.opacity = '0';
            alert.style.transform = 'translateY(-10px)';
            setTimeout(() => alert.remove(), 300);
        }, 5000);
    });

    // ── 11. Navbar Shrink on Scroll ──────────────────────────────────────
    window.addEventListener('scroll', () => {
        const navbar = document.querySelector('.navbar-custom');
        if (navbar) {
            if (window.scrollY > 50) {
                navbar.style.padding = '0.3rem 0';
                navbar.style.boxShadow = '0 4px 20px rgba(0,0,0,0.3)';
            } else {
                navbar.style.padding = '0.6rem 0';
                navbar.style.boxShadow = 'none';
            }
        }
    });

});
