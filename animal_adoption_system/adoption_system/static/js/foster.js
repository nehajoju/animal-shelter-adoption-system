// ================= GLOBAL STATE =================
let selectedAnimal = null;

// ================= PAGE LOAD ANIMATION =================
document.addEventListener("DOMContentLoaded", () => {
    const cards = document.querySelectorAll(".foster-card");

    cards.forEach((card, index) => {
        setTimeout(() => {
            card.classList.add("show");
        }, index * 150);
    });
});

// ================= SELECT ANIMAL =================
function openForm(animalName) {
    selectedAnimal = animalName;

    const formSection = document.getElementById("fosterForm");
    const selectedText = document.getElementById("selectedAnimal");

    selectedText.innerText = `You are applying to foster: ${animalName}`;
    selectedText.style.display = "block";

    formSection.scrollIntoView({
        behavior: "smooth",
        block: "start"
    });

    highlightSelectedCard(animalName);
}

// ================= HIGHLIGHT SELECTED CARD =================
function highlightSelectedCard(name) {
    const cards = document.querySelectorAll(".foster-card");

    cards.forEach(card => {
        const title = card.querySelector("h3").innerText;
        if (title === name) {
            card.style.border = "3px solid #be123c";
        } else {
            card.style.border = "none";
        }
    });
}

// ================= FORM VALIDATION =================
const form = document.querySelector("form");

if (form) {
    form.addEventListener("submit", function (e) {
        e.preventDefault();

        if (!selectedAnimal) {
            alert("Please select an animal to foster first 🐾");
            return;
        }

        const inputs = form.querySelectorAll("input, select, textarea");
        let valid = true;

        inputs.forEach(input => {
            if (!input.value.trim()) {
                input.style.borderColor = "#be123c";
                valid = false;
            } else {
                input.style.borderColor = "#e5e7eb";
            }
        });

        if (!valid) {
            alert("Please fill all required fields.");
            return;
        }

        submitFosterApplication();
    });
}

// ================= SUBMIT APPLICATION (DEMO MODE) =================
function submitFosterApplication() {
    const submitBtn = document.querySelector("form button");
    submitBtn.disabled = true;
    submitBtn.innerText = "Submitting...";

    // Simulate server request
    setTimeout(() => {
        showSuccessMessage();
        resetForm();
        submitBtn.disabled = false;
        submitBtn.innerText = "Submit Application";
    }, 1500);
}

// ================= SUCCESS MESSAGE =================
function showSuccessMessage() {
    const message = document.createElement("div");
    message.innerHTML = `
        <div style="
            background:#ecfdf5;
            color:#065f46;
            padding:18px;
            border-radius:12px;
            text-align:center;
            margin-bottom:20px;
            font-weight:600;">
            ✅ Foster application submitted successfully!<br>
            Our team will contact you soon.
        </div>
    `;

    const formSection = document.getElementById("fosterForm");
    formSection.prepend(message);

    setTimeout(() => {
        message.remove();
    }, 5000);
}

// ================= RESET FORM =================
function resetForm() {
    form.reset();
    selectedAnimal = null;

    document.getElementById("selectedAnimal").innerText = "";

    const cards = document.querySelectorAll(".foster-card");
    cards.forEach(card => card.style.border = "none");
}

// ================= FUTURE DJANGO NOTE =================
/*
    🔜 When connecting to Django:
    - Replace submitFosterApplication()
    - Use fetch() or form POST
    - Send animal_id, user_id, duration, reason
    - Handle response from backend
*/
// OPEN POPUP
function openForm(animalName) {
    document.getElementById("fosterModal").style.display = "flex";
    document.getElementById("modalAnimal").value = animalName;
    document.body.style.overflow = "hidden";
}

// CLOSE POPUP
function closeFosterForm() {
    document.getElementById("fosterModal").style.display = "none";
    document.body.style.overflow = "auto";
}

// CLOSE ON OUTSIDE CLICK
window.onclick = function(event) {
    const modal = document.getElementById("fosterModal");
    if (event.target === modal) {
        closeFosterForm();
    }
};

// DEMO SUBMIT HANDLING
document.getElementById("fosterApplicationForm")?.addEventListener("submit", function(e) {
    e.preventDefault();
    alert("✅ Foster application submitted successfully!");
    closeFosterForm();
    this.reset();
});
