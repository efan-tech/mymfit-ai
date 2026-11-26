// ==========================================
// MYMFIT AI - ONBOARDING ENGINE
// ==========================================

document.addEventListener("DOMContentLoaded", function () {

    const form = document.getElementById("onboarding-form");

    const steps = document.querySelectorAll(".form-step");

    const nextButton = document.getElementById("next-button");
    const backButton = document.getElementById("back-button");
    const submitButton = document.getElementById("submit-button");

    const progressFill = document.getElementById("progress-fill");
    const stepLabel = document.getElementById("step-label");
    const progressPercent = document.getElementById("progress-percent");

    const goalsInput = document.getElementById("primary_goals");
    const equipmentInput = document.getElementById("equipment");

    let currentStep = 0;

    const totalSteps = steps.length;


    // ======================================
    // DISPLAY CURRENT STEP
    // ======================================

    function showStep(index) {

        steps.forEach((step, i) => {
            step.classList.toggle("active", i === index);
        });

        currentStep = index;

        const percentage = Math.round(
            ((currentStep + 1) / totalSteps) * 100
        );

        progressFill.style.width = percentage + "%";

        stepLabel.textContent =
            `STEP ${String(currentStep + 1).padStart(2, "0")} OF ${String(totalSteps).padStart(2, "0")}`;

        progressPercent.textContent = percentage + "%";

        backButton.disabled = currentStep === 0;

        if (currentStep === totalSteps - 1) {

            nextButton.style.display = "none";
            submitButton.style.display = "inline-block";

        } else {

            nextButton.style.display = "inline-block";
            submitButton.style.display = "none";

        }

        window.scrollTo({
            top: 0,
            behavior: "smooth"
        });

    }


    // ======================================
    // VALIDATE CURRENT STEP
    // ======================================

    function validateStep() {

        const currentSection = steps[currentStep];

        const requiredFields = currentSection.querySelectorAll(
            "input[required], select[required], textarea[required]"
        );

        for (const field of requiredFields) {

            if (!field.checkValidity()) {

                field.reportValidity();

                return false;

            }

        }


        // At least one fitness goal is required.

        if (currentStep === 1) {

            const selectedGoals = document.querySelectorAll(
                ".goal-choice:checked"
            );

            if (selectedGoals.length === 0) {

                alert("Please select at least one fitness goal.");

                return false;

            }

        }

        return true;

    }


    // ======================================
    // NEXT BUTTON
    // ======================================

    nextButton.addEventListener("click", function () {

        if (!validateStep()) {
            return;
        }

        if (currentStep < totalSteps - 1) {

            showStep(currentStep + 1);

        }

    });


    // ======================================
    // BACK BUTTON
    // ======================================

    backButton.addEventListener("click", function () {

        if (currentStep > 0) {

            showStep(currentStep - 1);

        }

    });


    // ======================================
    // FITNESS GOALS
    // ======================================

    const goalChoices = document.querySelectorAll(".goal-choice");

    function collectGoals() {

        const selectedGoals = Array.from(goalChoices)
            .filter(choice => choice.checked)
            .map(choice => choice.value);

        goalsInput.value = selectedGoals.join(", ");

    }

    goalChoices.forEach(choice => {

        choice.addEventListener("change", collectGoals);

    });


    // ======================================
    // EQUIPMENT SELECTION
    // ======================================

    const equipmentChoices = document.querySelectorAll(
        ".equipment-choice"
    );

    equipmentChoices.forEach(choice => {

        choice.addEventListener("change", function () {

            if (this.value === "None" && this.checked) {

                equipmentChoices.forEach(other => {

                    if (other !== this) {
                        other.checked = false;
                    }

                });

            } else if (this.checked) {

                const noneOption = document.querySelector(
                    '.equipment-choice[value="None"]'
                );

                noneOption.checked = false;

            }

        });

    });


    function collectEquipment() {

        const selectedEquipment = Array.from(equipmentChoices)
            .filter(choice => choice.checked)
            .map(choice => choice.value);

        equipmentInput.value = selectedEquipment.join(", ");

    }


    // ======================================
    // FINAL FORM SUBMISSION
    // ======================================

    form.addEventListener("submit", function (event) {

        if (!validateStep()) {

            event.preventDefault();

            return;

        }

        collectGoals();
        collectEquipment();

        submitButton.disabled = true;

        submitButton.textContent = "Creating Your Journey...";

    });


    // ======================================
    // INITIALIZE
    // ======================================

    showStep(0);

});
