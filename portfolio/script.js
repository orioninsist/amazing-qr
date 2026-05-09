function setLanguage(lang) {
    // Update active button state
    document.querySelectorAll('.lang-btn').forEach(btn => {
        btn.classList.toggle('active', btn.innerText.toLowerCase() === lang);
    });

    // Update all elements with data attributes
    document.querySelectorAll('[data-en]').forEach(el => {
        if (lang === 'tr') {
            el.innerText = el.getAttribute('data-tr');
        } else {
            el.innerText = el.getAttribute('data-en');
        }
    });

    // Save preference
    localStorage.setItem('preferred-lang', lang);
}

// Initialize language on load
document.addEventListener('DOMContentLoaded', () => {
    const savedLang = localStorage.getItem('preferred-lang') || 'en';
    setLanguage(savedLang);

    // Subtle scroll animation for cards
    const observerOptions = {
        threshold: 0.1
    };

    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.opacity = '1';
                entry.target.style.transform = 'translateY(0)';
            }
        });
    }, observerOptions);

    document.querySelectorAll('.card').forEach(card => {
        card.style.opacity = '0';
        card.style.transform = 'translateY(30px)';
        card.style.transition = 'all 0.6s ease-out';
        observer.observe(card);
    });
});
