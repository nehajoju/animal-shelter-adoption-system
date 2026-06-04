document.addEventListener("DOMContentLoaded", () => {

    /* ---------- Smooth Scroll ---------- */
    document.querySelectorAll("nav a[href^='#']").forEach(link => {
        link.addEventListener("click", e => {
            e.preventDefault();
            document.querySelector(link.getAttribute("href"))
                .scrollIntoView({ behavior: "smooth" });
        });
    });


    /* ---------- Sticky Navbar ---------- */
    const navbar = document.querySelector(".navbar");
    window.addEventListener("scroll", () => {
        navbar.classList.toggle("sticky", window.scrollY > 60);
    });


    /* ---------- Scroll Animation ---------- */
    const observer = new IntersectionObserver(entries => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add("show");
            }
        });
    }, { threshold: 0.2 });

    document.querySelectorAll(
        ".module-card, .animal, .process-card, .box"
    ).forEach(el => observer.observe(el));


    /* ---------- BEAUTIFUL POPUPS ---------- */

    // Adopt buttons
    document.querySelectorAll(".primary-btn").forEach(btn => {
        btn.addEventListener("click", e => {
            if (btn.textContent.includes("Adopt")) {
                e.preventDefault();

                Swal.fire({
                    title: "🐾 Ready to Adopt?",
                    text: "Please login or create an account to adopt your new best friend.",
                    icon: "info",
                    showCancelButton: true,
                    confirmButtonText: "Login Now",
                    cancelButtonText: "Later",
                    confirmButtonColor: "#ff7a00",
                    background: "#fff",
                }).then(result => {
                    if (result.isConfirmed) {
                        window.location.href = "/login/";
                    }
                });
            }
        });
    });


    // Donate button
    document.querySelectorAll(".secondary-btn").forEach(btn => {
        btn.addEventListener("click", e => {
            if (btn.textContent.includes("Donate")) {
                e.preventDefault();

                Swal.fire({
                    title: "❤️ Thank You!",
                    text: "Your support helps save innocent lives.",
                    icon: "success",
                    confirmButtonText: "Continue",
                    confirmButtonColor: "#28a745"
                });
            }
        });
    });

});


/* ===============================
   DASHBOARD INTERACTIONS
   =============================== */

document.addEventListener("DOMContentLoaded", () => {

    /* Smooth hover animation for buttons */
    document.querySelectorAll(".primary-btn, .secondary-btn").forEach(btn => {
        btn.addEventListener("mouseenter", () => {
            btn.style.transform = "scale(1.05)";
        });
        btn.addEventListener("mouseleave", () => {
            btn.style.transform = "scale(1)";
        });
    });

    /* Navbar shadow on scroll */
    const navbar = document.querySelector(".navbar");
    window.addEventListener("scroll", () => {
        if (window.scrollY > 50) {
            navbar.style.boxShadow = "0 6px 18px rgba(0,0,0,0.12)";
        } else {
            navbar.style.boxShadow = "0 4px 10px rgba(0,0,0,0.08)";
        }
    });

});
