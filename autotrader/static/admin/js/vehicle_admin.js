document.addEventListener("DOMContentLoaded", function () {
    const makeField = document.querySelector("#id_make");
    const modelField = document.querySelector("#id_model");

    if (!makeField || !modelField) return;  // Ensure fields exist

    function updateModelDropdown() {
        const makeId = makeField.value;
        modelField.innerHTML = '<option value="">---------</option>';  // Reset model field

        if (makeId) {
            fetch(`/admin-api/get-models/?make_id=${makeId}`)
                .then(response => response.json())
                .then(data => {
                    data.models.forEach(model => {
                        let option = new Option(model.name, model.id);
                        modelField.appendChild(option);
                    });
                });
        }
    }

    makeField.addEventListener("change", updateModelDropdown);
});
