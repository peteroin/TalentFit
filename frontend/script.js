const resumeInput = document.getElementById("resume");
const dropZone = document.getElementById("dropZone");

const selectedFile = document.getElementById("selectedFile");
const fileName = document.getElementById("fileName");
const fileSize = document.getElementById("fileSize");

const removeFileButton =
    document.getElementById("removeFile");

const requirementsInput =
    document.getElementById("requirements");

const analyzeButton =
    document.getElementById("analyzeButton");

const errorMessage =
    document.getElementById("errorMessage");

const resultsSection =
    document.getElementById("resultsSection");

let currentFile = null;


// ============================================================
// FILE HANDLING
// ============================================================

function setSelectedFile(file) {

    if (!file) {
        return;
    }

    const extension =
        file.name
            .split(".")
            .pop()
            .toLowerCase();

    if (!["pdf", "docx"].includes(extension)) {

        showError(
            "Unsupported file type. Please upload a PDF or DOCX resume."
        );

        return;
    }

    currentFile = file;

    fileName.textContent = file.name;
    fileSize.textContent =
        formatFileSize(file.size);

    selectedFile.classList.remove("hidden");

    dropZone.classList.add("has-file");

    clearError();
}


function formatFileSize(bytes) {

    if (bytes < 1024) {
        return `${bytes} B`;
    }

    if (bytes < 1024 * 1024) {
        return `${(bytes / 1024).toFixed(1)} KB`;
    }

    return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}


function removeSelectedFile() {

    currentFile = null;

    resumeInput.value = "";

    fileName.textContent =
        "No file selected";

    fileSize.textContent = "";

    selectedFile.classList.add("hidden");

    dropZone.classList.remove("has-file");
}


// ============================================================
// FILE INPUT
// ============================================================

resumeInput.addEventListener(
    "change",
    function () {

        if (
            this.files &&
            this.files.length > 0
        ) {

            setSelectedFile(
                this.files[0]
            );
        }
    }
);


removeFileButton.addEventListener(
    "click",
    removeSelectedFile
);


// ============================================================
// DRAG AND DROP
// ============================================================

dropZone.addEventListener(
    "dragover",
    function (event) {

        event.preventDefault();

        dropZone.classList.add(
            "dragging"
        );
    }
);


dropZone.addEventListener(
    "dragleave",
    function () {

        dropZone.classList.remove(
            "dragging"
        );
    }
);


dropZone.addEventListener(
    "drop",
    function (event) {

        event.preventDefault();

        dropZone.classList.remove(
            "dragging"
        );

        const files =
            event.dataTransfer.files;

        if (
            files &&
            files.length > 0
        ) {

            setSelectedFile(
                files[0]
            );
        }
    }
);


// ============================================================
// ERROR
// ============================================================

function showError(message) {

    errorMessage.textContent =
        message;

    errorMessage.classList.remove(
        "hidden"
    );

    errorMessage.classList.add(
        "show"
    );
}


function clearError() {

    errorMessage.textContent = "";

    errorMessage.classList.remove(
        "show"
    );

    errorMessage.classList.add(
        "hidden"
    );
}


// ============================================================
// LOADING
// ============================================================

function setLoading(isLoading) {

    if (isLoading) {

        analyzeButton.disabled = true;

        analyzeButton.innerHTML = `
            <span class="spinner"></span>
            Analyzing Resume...
        `;

    } else {

        analyzeButton.disabled = false;

        analyzeButton.innerHTML = `
            Analyze Candidate
        `;
    }
}


// ============================================================
// ANALYZE
// ============================================================

analyzeButton.addEventListener(
    "click",
    analyzeResume
);


async function analyzeResume() {

    clearError();


    if (!currentFile) {

        showError(
            "Please upload a PDF or DOCX resume."
        );

        return;
    }


    if (
        !requirementsInput.value.trim()
    ) {

        showError(
            "Please enter the HR requirements or job description."
        );

        return;
    }


    const formData =
        new FormData();


    formData.append(
        "resume",
        currentFile
    );


    formData.append(
        "requirements",
        requirementsInput.value.trim()
    );


    setLoading(true);


    try {

        const response =
            await fetch(
                "/api/analyze",
                {
                    method: "POST",
                    body: formData
                }
            );


        const data =
            await response.json();


        if (!response.ok) {

            throw new Error(
                data.detail ||
                "Resume analysis failed."
            );
        }


        if (!data.success) {

            throw new Error(
                "Resume analysis failed."
            );
        }


        renderResults(data);


    } catch (error) {

        console.error(error);

        showError(
            error.message ||
            "Something went wrong while analyzing the resume."
        );

    } finally {

        setLoading(false);
    }
}


// ============================================================
// RENDER RESULTS
// ============================================================

function renderResults(data) {

    const matching =
        data.matching;


    if (!matching) {

        showError(
            "No matching result was returned."
        );

        return;
    }


    // Overall score

    document.getElementById(
        "overallScore"
    ).textContent =
        `${Math.round(
            matching.overall_score
        )}%`;


    // Recommendation

    const recommendation =
        document.getElementById(
            "recommendation"
        );


    recommendation.textContent =
        matching.recommendation;


    recommendation.className =
        "recommendation " +
        getRecommendationClass(
            matching.recommendation
        );


    // Mandatory requirements

    const mandatory =
        matching.mandatory_requirements;


    document.getElementById(
        "mandatoryCount"
    ).textContent =
        `${mandatory.missing} / ${mandatory.total} gaps`;


    document.getElementById(
        "mandatoryStatus"
    ).textContent =
        mandatory.all_satisfied
            ? "All mandatory requirements satisfied"
            : "Mandatory requirements need attention";


    // Candidate

    renderCandidate(
        data.candidate
    );


    // Category scores

    updateCategoryScore(
        "skills",
        matching.skills
    );

    updateCategoryScore(
        "experience",
        matching.experience
    );

    updateCategoryScore(
        "projects",
        matching.projects
    );

    updateCategoryScore(
        "education",
        matching.education
    );

    updateCategoryScore(
        "certification",
        matching.certifications
    );


    // Detail sections

    renderRequirementList(
        "skillsResults",
        matching.skills
    );

    renderRequirementList(
        "experienceResults",
        matching.experience
    );

    renderRequirementList(
        "projectsResults",
        matching.projects
    );

    renderRequirementList(
        "educationResults",
        matching.education
    );

    renderRequirementList(
        "certificationResults",
        matching.certifications
    );


    // Summary counts

    updateSummary(
        "skillsSummary",
        matching.skills
    );

    updateSummary(
        "experienceSummary",
        matching.experience
    );

    updateSummary(
        "projectsSummary",
        matching.projects
    );

    updateSummary(
        "educationSummary",
        matching.education
    );

    updateSummary(
        "certificationSummary",
        matching.certifications
    );


    // Mandatory gaps

    renderMandatoryGaps(
        matching
    );


    // Show results

    resultsSection.classList.remove(
        "hidden"
    );

    resultsSection.classList.add(
        "show"
    );


    resultsSection.scrollIntoView({
        behavior: "smooth"
    });
}


// ============================================================
// CATEGORY SCORE
// ============================================================

function updateCategoryScore(
    category,
    result
) {

    if (!result) {
        return;
    }


    const score =
        Math.round(result.score);


    const scoreElement =
        document.getElementById(
            `${category}Score`
        );


    const progressElement =
        document.getElementById(
            `${category}Progress`
        );


    if (scoreElement) {

        scoreElement.textContent =
            `${score}%`;
    }


    if (progressElement) {

        progressElement.style.width =
            `${score}%`;
    }
}


// ============================================================
// SUMMARY COUNT
// ============================================================

function updateSummary(
    elementId,
    result
) {

    const element =
        document.getElementById(
            elementId
        );


    if (!element || !result) {
        return;
    }


    const total =
        (result.matched || []).length +
        (result.partial || []).length +
        (result.missing || []).length;


    element.textContent =
        total;
}


// ============================================================
// CANDIDATE
// ============================================================

function renderCandidate(
    candidate
) {

    document.getElementById(
        "candidateName"
    ).textContent =
        candidate.name ||
        "Not available";


    document.getElementById(
        "candidateEmail"
    ).textContent =
        candidate.email ||
        "Not available";


    document.getElementById(
        "candidatePhone"
    ).textContent =
        candidate.phone ||
        "Not available";
}


// ============================================================
// REQUIREMENT LIST
// ============================================================

function renderRequirementList(
    containerId,
    result
) {

    const container =
        document.getElementById(
            containerId
        );


    if (!container) {
        return;
    }


    if (!result) {

        container.innerHTML = `
            <div class="empty-state">
                No requirements specified.
            </div>
        `;

        return;
    }


    const items = [
        ...(result.matched || []),
        ...(result.partial || []),
        ...(result.missing || [])
    ];


    if (items.length === 0) {

        container.innerHTML = `
            <div class="empty-state">
                No requirements specified.
            </div>
        `;

        return;
    }


    container.innerHTML =
        items.map(
            item => {

                const status =
                    item.status ||
                    "missing";


                let statusText =
                    "Missing";


                if (
                    status === "matched"
                ) {

                    statusText =
                        "Matched";

                } else if (
                    status === "partial"
                ) {

                    statusText =
                        "Partial";
                }


                let extraInformation =
                    "";


                // Experience

                if (
                    item.experience_status ===
                    "insufficient_experience"
                ) {

                    extraInformation = `
                        <div class="requirement-extra">
                            Candidate:
                            <strong>
                                ${item.candidate_years}
                            </strong>
                            years
                            /
                            Required:
                            <strong>
                                ${item.minimum_years}
                            </strong>
                            years
                        </div>
                    `;
                }


                return `

                    <div class="requirement-item">

                        <div class="requirement-main">

                            <div class="requirement-title">

                                ${escapeHtml(
                                    item.requirement ||
                                    ""
                                )}

                            </div>


                            ${
                                item.matched_with
                                    ? `
                                        <div class="matched-with">

                                            Matched with:
                                            ${escapeHtml(
                                                item.matched_with
                                            )}

                                        </div>
                                      `
                                    : ""
                            }


                            ${extraInformation}

                        </div>


                        <div class="requirement-meta">

                            <span
                                class="status-badge ${status}"
                            >
                                ${statusText}
                            </span>


                            <span class="match-score">

                                ${Math.round(
                                    item.score || 0
                                )}%

                            </span>

                        </div>

                    </div>

                `;
            }
        ).join("");
}


// ============================================================
// MANDATORY GAPS
// ============================================================

function renderMandatoryGaps(
    matching
) {

    const container =
        document.getElementById(
            "mandatoryGaps"
        );


    const gapsCard =
        document.getElementById(
            "gapsCard"
        );


    if (!container) {
        return;
    }


    const gaps = [];


    if (matching.skills) {

        gaps.push(
            ...(matching.skills.required_missing || [])
        );
    }


    if (matching.experience) {

        gaps.push(
            ...(matching.experience.required_missing || [])
        );
    }


    if (matching.projects) {

        gaps.push(
            ...(matching.projects.required_missing || [])
        );
    }


    if (matching.education) {

        gaps.push(
            ...(matching.education.required_missing || [])
        );
    }


    if (matching.certifications) {

        gaps.push(
            ...(matching.certifications.required_missing || [])
        );
    }


    if (gaps.length === 0) {

        container.innerHTML = `
            <div class="no-gaps">
                ✓ All mandatory requirements are satisfied.
            </div>
        `;

        if (gapsCard) {
            gapsCard.classList.add(
                "hidden"
            );
        }

        return;
    }


    if (gapsCard) {

        gapsCard.classList.remove(
            "hidden"
        );

        gapsCard.classList.add(
            "show"
        );
    }


    container.innerHTML =
        gaps.map(
            gap => {

                let explanation = "";


                if (
                    gap.experience_status ===
                    "insufficient_experience"
                ) {

                    explanation = `
                        <div class="gap-explanation">

                            Candidate has
                            <strong>
                                ${gap.candidate_years}
                            </strong>
                            years of relevant experience,

                            while
                            <strong>
                                ${gap.minimum_years}
                            </strong>
                            years are required.

                        </div>
                    `;
                }


                return `

                    <div class="mandatory-gap">

                        <div class="gap-icon">
                            !
                        </div>


                        <div class="gap-content">

                            <div class="gap-title">

                                ${escapeHtml(
                                    gap.requirement ||
                                    ""
                                )}

                            </div>


                            ${
                                gap.matched_with
                                    ? `
                                        <div class="gap-match">

                                            Related experience:
                                            ${escapeHtml(
                                                gap.matched_with
                                            )}

                                        </div>
                                      `
                                    : ""
                            }


                            ${explanation}

                        </div>

                    </div>

                `;
            }
        ).join("");
}


// ============================================================
// RECOMMENDATION
// ============================================================

function getRecommendationClass(
    recommendation
) {

    const value =
        recommendation.toLowerCase();


    if (
        value.includes("strong")
    ) {

        return "strong";
    }


    if (
        value.includes("good")
    ) {

        return "good";
    }


    if (
        value.includes("partial")
    ) {

        return "partial";
    }


    return "low";
}


// ============================================================
// HTML ESCAPE
// ============================================================

function escapeHtml(value) {

    if (
        value === null ||
        value === undefined
    ) {

        return "";
    }


    return String(value)
        .replace(
            /&/g,
            "&amp;"
        )
        .replace(
            /</g,
            "&lt;"
        )
        .replace(
            />/g,
            "&gt;"
        )
        .replace(
            /"/g,
            "&quot;"
        )
        .replace(
            /'/g,
            "&#039;"
        );
}


// ============================================================
// NEW ANALYSIS
// ============================================================

const newAnalysisButton =
    document.getElementById(
        "newAnalysisButton"
    );


newAnalysisButton.addEventListener(
    "click",
    function () {

        removeSelectedFile();

        clearError();

        requirementsInput.value = "";

        resultsSection.classList.remove(
            "show"
        );

        resultsSection.classList.add(
            "hidden"
        );

        document.getElementById(
            "gapsCard"
        ).classList.add(
            "hidden"
        );

        window.scrollTo({
            top: 0,
            behavior: "smooth"
        });
    }
);