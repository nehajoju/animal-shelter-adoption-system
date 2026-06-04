const amountInput = document.getElementById("amount");
const summary = document.getElementById("donationSummary");

document.querySelectorAll(".amount-btn").forEach(btn => {
    btn.addEventListener("click", () => {
        document.querySelectorAll(".amount-btn")
            .forEach(b => b.classList.remove("active"));

        btn.classList.add("active");
        amountInput.value = btn.dataset.amount;
        updateSummary();
    });
});

amountInput.addEventListener("input", updateSummary);

function updateSummary() {
    const amount = amountInput.value || 0;
    let impact = "general shelter support";

    if (amount >= 500 && amount < 1000) impact = "food & nutrition";
    if (amount >= 1000 && amount < 2000) impact = "medical treatment";
    if (amount >= 2000) impact = "critical rescue care";

    summary.innerHTML = `
        💖 <strong>Donation Summary</strong><br>
        Amount: ₹${amount}<br>
        Impact: ${impact}
    `;
}

document.getElementById("donationForm").addEventListener("submit", function(e) {
    e.preventDefault();

    const amount = amountInput.value;
    if (!amount || amount <= 0) {
        alert("Please enter a valid donation amount");
        return;
    }

    const btn = document.querySelector(".submit-btn");
    btn.innerText = "Processing...";
    btn.disabled = true;

    setTimeout(() => {
        showSuccess(amount);
        this.reset();
        btn.innerText = "Donate Now";
        btn.disabled = false;
        document.querySelectorAll(".amount-btn")
            .forEach(b => b.classList.remove("active"));
        summary.innerHTML = "💡 Select an amount to see its impact";
    }, 1500);
});

function showSuccess(amount) {
    const msg = document.createElement("div");
    msg.className = "donation-success";
    msg.innerHTML = `🙏 Thank you for donating ₹${amount}!<br>Your support saves lives 🐾`;

    document.querySelector(".donation-card").appendChild(msg);

    setTimeout(() => msg.remove(), 5000);
}
