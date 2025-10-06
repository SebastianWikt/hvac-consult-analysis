/**
 * Service Call Analyzer - Main JavaScript
 * Handles navigation, smooth scrolling, and interactive features
 */

document.addEventListener('DOMContentLoaded', function() {
    initializeNavigation();
    initializeScrollSpy();
    initializeAnimations();
    initializeAnalysisSync();
});

/**
 * Initialize stage navigation functionality
 */
function initializeNavigation() {
    const navLinks = document.querySelectorAll('.stage-nav-horizontal .nav-link');
    
    navLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            
            // Remove active class from all links
            navLinks.forEach(l => l.classList.remove('active'));
            
            // Add active class to clicked link
            this.classList.add('active');
            
            // Get target section
            const targetId = this.getAttribute('href');
            const targetSection = document.querySelector(targetId);
            
            if (targetSection) {
                // Smooth scroll to target section with offset for fixed navigation
                const offset = 120; // Account for the horizontal nav bar
                const elementPosition = targetSection.offsetTop;
                const offsetPosition = elementPosition - offset;
                
                window.scrollTo({
                    top: offsetPosition,
                    behavior: 'smooth'
                });
                
                // Update URL without triggering page reload
                history.pushState(null, null, targetId);
            }
        });
    });
    
    // Handle direct URL navigation (e.g., page refresh with hash)
    if (window.location.hash) {
        const targetSection = document.querySelector(window.location.hash);
        if (targetSection) {
            setTimeout(() => {
                const offset = 120;
                const elementPosition = targetSection.offsetTop;
                const offsetPosition = elementPosition - offset;
                
                window.scrollTo({
                    top: offsetPosition,
                    behavior: 'smooth'
                });
                updateActiveNavLink(window.location.hash);
            }, 100);
        }
    }
}

/**
 * Initialize scroll spy to highlight current section and sync analysis panel
 */
function initializeScrollSpy() {
    const sections = document.querySelectorAll('.transcript-section');
    
    if (sections.length === 0) return;
    
    // Simple and reliable scroll listener
    function handleScroll() {
        const scrollPosition = window.scrollY + 200; // Check what's 200px from top
        let activeSection = null;
        let activeSectionNumber = null;
        
        sections.forEach((section, index) => {
            const sectionTop = section.offsetTop;
            const sectionBottom = sectionTop + section.offsetHeight;
            
            if (scrollPosition >= sectionTop && scrollPosition < sectionBottom) {
                activeSection = section;
                activeSectionNumber = index + 1;
            }
        });
        
        if (activeSection && activeSectionNumber) {
            const sectionId = '#' + activeSection.id;
            updateActiveNavLink(sectionId);
            syncAnalysisPanel(activeSectionNumber);
        }
    }
    
    // Call immediately and on scroll
    handleScroll();
    window.addEventListener('scroll', handleScroll);
}

/**
 * Update active navigation link and transcript section
 */
function updateActiveNavLink(targetId) {
    const navLinks = document.querySelectorAll('.stage-nav-horizontal .nav-link');
    const transcriptSections = document.querySelectorAll('.transcript-section');
    
    // Update navigation links
    navLinks.forEach(link => {
        link.classList.remove('active');
        if (link.getAttribute('href') === targetId) {
            link.classList.add('active');
        }
    });
    
    // Update transcript sections
    transcriptSections.forEach(section => {
        section.classList.remove('active');
        if ('#' + section.id === targetId) {
            section.classList.add('active');
        }
    });
}

/**
 * Synchronize analysis panel with current transcript section
 */
function syncAnalysisPanel(sectionNumber) {
    const targetAnalysis = document.querySelector(`#analysis-${sectionNumber}`);
    
    if (!targetAnalysis) {
        console.log(`Analysis section not found: analysis-${sectionNumber}`);
        return;
    }
    
    // Don't sync if already active
    if (targetAnalysis.classList.contains('active')) return;
    
    // Hide all analysis sections immediately
    const allAnalysisSections = document.querySelectorAll('.analysis-section');
    allAnalysisSections.forEach(section => {
        section.classList.remove('active');
    });
    
    // Show and activate the target analysis section immediately
    targetAnalysis.classList.add('active');
    
    console.log(`Switched to analysis section: ${sectionNumber}`);
}

/**
 * Initialize analysis panel synchronization
 */
function initializeAnalysisSync() {
    // Show the first analysis section by default
    const firstAnalysisSection = document.querySelector('.analysis-section');
    if (firstAnalysisSection) {
        firstAnalysisSection.classList.add('active');
    }
    
    // Update analysis sync when navigation links are clicked
    const navLinks = document.querySelectorAll('.stage-nav-horizontal .nav-link');
    navLinks.forEach((link, index) => {
        link.addEventListener('click', function() {
            const sectionNumber = index + 1;
            syncAnalysisPanel(sectionNumber);
        });
    });
}

/**
 * Initialize animations and interactive features
 */
function initializeAnimations() {
    // Animate compliance score bars
    animateScoreBars();
    
    // Add hover effects to utterances
    addUtteranceHoverEffects();
    
    // Initialize tooltips if Bootstrap is available
    if (typeof bootstrap !== 'undefined') {
        const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
        tooltipTriggerList.map(function (tooltipTriggerEl) {
            return new bootstrap.Tooltip(tooltipTriggerEl);
        });
    }
}

/**
 * Animate compliance score bars
 */
function animateScoreBars() {
    const scoreBars = document.querySelectorAll('.score-fill');
    
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const bar = entry.target;
                const width = bar.style.width;
                
                // Reset width and animate
                bar.style.width = '0%';
                setTimeout(() => {
                    bar.style.width = width;
                }, 100);
                
                observer.unobserve(bar);
            }
        });
    }, {
        threshold: 0.5
    });
    
    scoreBars.forEach(bar => {
        observer.observe(bar);
    });
}

/**
 * Add hover effects to utterances
 */
function addUtteranceHoverEffects() {
    const utterances = document.querySelectorAll('.utterance');
    
    utterances.forEach(utterance => {
        utterance.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-2px)';
        });
        
        utterance.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0)';
        });
    });
}

/**
 * Utility function to format timestamps
 */
function formatTimestamp(seconds) {
    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = Math.floor(seconds % 60);
    return `${minutes.toString().padStart(2, '0')}:${remainingSeconds.toString().padStart(2, '0')}`;
}

/**
 * Utility function to scroll to top
 */
function scrollToTop() {
    window.scrollTo({
        top: 0,
        behavior: 'smooth'
    });
}

/**
 * Add scroll to top functionality
 */
function addScrollToTop() {
    // Create scroll to top button
    const scrollButton = document.createElement('button');
    scrollButton.innerHTML = '<i class="bi bi-arrow-up"></i>';
    scrollButton.className = 'btn btn-primary position-fixed';
    scrollButton.style.cssText = `
        bottom: 20px;
        right: 20px;
        z-index: 1000;
        border-radius: 50%;
        width: 50px;
        height: 50px;
        display: none;
        box-shadow: 0 2px 10px rgba(0,0,0,0.3);
    `;
    scrollButton.setAttribute('title', 'Scroll to top');
    scrollButton.onclick = scrollToTop;
    
    document.body.appendChild(scrollButton);
    
    // Show/hide button based on scroll position
    window.addEventListener('scroll', function() {
        if (window.pageYOffset > 300) {
            scrollButton.style.display = 'block';
        } else {
            scrollButton.style.display = 'none';
        }
    });
}

// Initialize scroll to top button
document.addEventListener('DOMContentLoaded', function() {
    addScrollToTop();
});

/**
 * Handle responsive navigation for mobile
 */
function handleMobileNavigation() {
    const stageNav = document.querySelector('.stage-nav-horizontal');
    if (!stageNav) return;
    
    // The horizontal navigation works well on mobile with the responsive CSS
    // No additional JavaScript needed for the horizontal layout
}

// Handle window resize
window.addEventListener('resize', function() {
    handleMobileNavigation();
});

// Initialize mobile navigation
document.addEventListener('DOMContentLoaded', function() {
    handleMobileNavigation();
});