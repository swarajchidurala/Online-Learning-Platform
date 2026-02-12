 const menuIcon = document.getElementById("menu-icon");
    const navLinks = document.getElementById("nav-links");

    menuIcon.addEventListener("click", () => {
      navLinks.classList.toggle("active");
    });

document.addEventListener('DOMContentLoaded', () => {

    // Function to add a class to an element when it's in the viewport
    const animateOnScroll = (entries, observer) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('visible');
                observer.unobserve(entry.target); // Stop observing after animation
            }
        });
    };

    // Create a new Intersection Observer
    const observer = new IntersectionObserver(animateOnScroll, {
        root: null, // Use the viewport as the root
        threshold: 0.2 // Trigger when 20% of the element is visible
    });

    // Observe all elements with the animation class
    document.querySelectorAll('.feature-card, .course-card, .testimonial-card, .headpara-card').forEach(card => {
        observer.observe(card);
    });

    // Smooth scroll for navigation links
    document.querySelectorAll('nav a').forEach(link => {
        link.addEventListener('click', (e) => {
            e.preventDefault();
            const targetId = link.getAttribute('href').substring(1);
            const targetSection = document.getElementById(targetId);
            if (targetSection) {
                targetSection.scrollIntoView({ behavior: 'smooth' });
            }
        });
    });

    // Hamburger menu toggle
    const hamburger = document.querySelector('.hamburger');
    const navLinks = document.querySelector('.nav-links');

    if (hamburger && navLinks) {
        hamburger.addEventListener('click', () => {
            navLinks.classList.toggle('active');
        });
    }
});
