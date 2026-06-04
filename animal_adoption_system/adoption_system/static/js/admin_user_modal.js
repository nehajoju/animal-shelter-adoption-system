function openUserModal(btn) {
    document.getElementById("uName").innerText = btn.dataset.name;
    document.getElementById("uEmail").innerText = btn.dataset.email;
    document.getElementById("uPhone").innerText = btn.dataset.phone;
    document.getElementById("uOccupation").innerText = btn.dataset.occupation;
    document.getElementById("uAddress").innerText = btn.dataset.address;
    document.getElementById("uHousing").innerText = btn.dataset.housing;
    document.getElementById("uOwnership").innerText = btn.dataset.ownership;
    document.getElementById("uFamily").innerText = btn.dataset.family;
    document.getElementById("uChildren").innerText = btn.dataset.children;
    document.getElementById("uPets").innerText = btn.dataset.pets;
    document.getElementById("uAdoptions").innerText = btn.dataset.adoptions;
    document.getElementById("uFoster").innerText = btn.dataset.foster;
    document.getElementById("uDonations").innerText = btn.dataset.donations;

    document.getElementById("userModal").style.display = "flex";
}

function closeUserModal() {
    document.getElementById("userModal").style.display = "none";
}

window.addEventListener("click", function (e) {
    const modal = document.getElementById("userModal");
    if (e.target === modal) closeUserModal();
});

function openAnimalModal(button) {
    document.getElementById("modalName").innerText =
        button.dataset.name || "—";

    document.getElementById("modalSpecies").innerText =
        button.dataset.species || "—";

    document.getElementById("animalModal").style.display = "flex";
}

function closeAnimalModal() {
    document.getElementById("animalModal").style.display = "none";
}

/* Close when clicking outside modal */
window.addEventListener("click", function (e) {
    const modal = document.getElementById("animalModal");
    if (e.target === modal) {
        closeAnimalModal();
    }
});
