"use strict";
const $ = (id) => document.getElementById(id);
const pretty = (value) => JSON.stringify(value, null, 2);
const state = {
    current: null,
    draft: null,
    dirty: false,
    busy: false,
    preview: null,
    job: null,
};
const session = new URLSearchParams(location.hash.slice(1)).get("session");
if (session) {
    sessionStorage.setItem("fail2test-session", session);
    history.replaceState(null, "", location.pathname);
}
const token = sessionStorage.getItem("fail2test-session") || "";

async function api(route, data) {
    const options = {
        headers: { Authorization: `Bearer ${token}` },
        cache: "no-store",
    };
    if (data !== undefined) {
        options.method = "POST";
        options.headers["Content-Type"] = "application/json";
        options.body = JSON.stringify(data);
    }
    const response = await fetch(route, options);
    const result = await response.json();
    if (!response.ok)
        throw new Error(
            `${result.error?.code || "REQUEST_FAILED"}: ${result.error?.message || "Request failed."}`,
        );
    return result;
}
function error(err) {
    $("error").textContent = err.message || String(err);
    $("error").hidden = false;
}
function notice(message) {
    $("notice").textContent = message;
    $("error").hidden = true;
}
function on(id, fn) {
    $(id).addEventListener("click", () =>
        Promise.resolve().then(fn).catch(error),
    );
}
function element(tag, text, className) {
    const e = document.createElement(tag);
    if (text !== undefined) e.textContent = text;
    if (className) e.className = className;
    return e;
}
function codeBlock(parent, title, data, open = false) {
    const d = element("details");
    d.open = open;
    d.append(
        element("summary", title),
        element("pre", typeof data === "string" ? data : pretty(data)),
    );
    parent.append(d);
}
function payload(extra = {}) {
    if (!state.current) throw new Error("Open a case first.");
    return {
        path: state.current.path,
        expected_digest: state.current.digest,
        ...extra,
    };
}
function saved() {
    if (state.dirty)
        throw new Error(
            "UNSAVED_CHANGES: Save your case edits before continuing.",
        );
    if (state.busy)
        throw new Error("WORKSPACE_BUSY: Wait for the active execution.");
}
function invalidatePreview() {
    state.preview = null;
    $("export").disabled = true;
    $("export-result").replaceChildren();
    $("export-help").textContent = state.dirty
        ? "Save your edits, approve the case and reproduce its failing baseline before export."
        : state.busy
          ? "Wait for the active job, then preview the export files."
          : !state.current?.review_valid
            ? "First approve this exact case in Review. Then reproduce its failing baseline in Execute."
            : !state.current.baseline_valid
              ? "In Execute, select a runner that reproduces the failure and click Validate failing baseline. Run regression alone does not establish a baseline. Editing or approving again clears it."
              : "Click Preview files first. Inspect the generated test and fixtures; Save export becomes enabled after a successful preview. Changing the directory or runner requires a new preview.";
}
function dirty() {
    invalidateAI();
    state.dirty = true;
    $("draft-state").textContent =
        "Unsaved changes. Save and review before execution.";
    $("acknowledge").checked = false;
    invalidatePreview();
}
function tab(name, focus = false) {
    for (const button of $("tabs").children) {
        const active = button.id === `tab-${name}`;
        button.setAttribute("aria-selected", String(active));
        button.tabIndex = active ? 0 : -1;
        $(button.getAttribute("aria-controls")).hidden = !active;
        if (active && focus) button.focus();
    }
    $("export-runner").textContent =
        `Runner: ${$("runner").value} · change it in Execute.`;
}
for (const button of $("tabs").children) {
    button.addEventListener("click", () => tab(button.id.slice(4)));
    button.addEventListener("keydown", (event) => {
        const buttons = [...$("tabs").children];
        let index = buttons.indexOf(button);
        if (event.key === "ArrowRight") index = (index + 1) % buttons.length;
        else if (event.key === "ArrowLeft")
            index = (index + buttons.length - 1) % buttons.length;
        else if (event.key === "Home") index = 0;
        else if (event.key === "End") index = buttons.length - 1;
        else return;
        event.preventDefault();
        tab(buttons[index].id.slice(4), true);
    });
}
async function refresh() {
    const cases = await api("/api/cases");
    $("case-list").replaceChildren();
    if (!cases.length)
        $("case-list").append(
            element("p", "No imported bundles yet.", "sidebar-note"),
        );
    for (const item of cases) {
        const b = element("button", item.title);
        b.setAttribute(
            "aria-current",
            String(state.current?.path === item.path),
        );
        b.title = item.path;
        b.addEventListener("click", () => openCase(item.path).catch(error));
        $("case-list").append(b);
    }
}
async function openCase(path) {
    saved();
    if (state.dirty) return;
    const item = await api(`/api/case?path=${encodeURIComponent(path)}`);
    state.job = null;
    $("run-result").replaceChildren();
    $("reduction-result").replaceChildren();
    $("job-status").textContent = "";
    showCase(item);
    await refresh();
    tab("evidence");
    notice("Case opened. Inspection does not execute application code.");
}
function showCase(item) {
    invalidateAI();
    state.current = item;
    state.draft = structuredClone(item.case);
    state.dirty = false;
    advancedApplied = true;
    advancedSource = null;
    invalidatePreview();
    $("welcome").hidden = true;
    $("case-workspace").hidden = false;
    $("case-title").textContent = item.case.title;
    $("case-path").textContent = item.path;
    $("case-digest").textContent = `SHA256 ${item.digest}`;
    $("case-state").textContent = item.baseline_valid
        ? "Baseline reproduced"
        : item.review_valid
          ? "Reviewed"
          : "Review required";
    $("input").textContent = pretty(item.case.input);
    $("models").textContent = pretty(item.case.model_fixtures);
    $("tools").textContent = pretty(item.case.tool_fixtures);
    $("provenance").textContent = pretty({
        provenance: item.case.provenance,
        changes: item.manifest.sanitization_changes,
        report: item["import-report.json"] || null,
        source_complete: item.manifest.source_complete,
    });
    $("events-section").hidden = !item["evidence.json"];
    $("events").textContent = item["evidence.json"]
        ? pretty(item["evidence.json"])
        : "";
    $("evidence-summary").replaceChildren();
    for (const [title, value, description] of [
        [
            "Evidence",
            item.manifest.source_complete ? "Complete" : "Trace only",
            "Declared source completeness; execution still requires matching fixtures.",
        ],
        [
            "Model fixtures",
            item.case.model_fixtures.length,
            "Recorded responses matched by slot, ordinal and request.",
        ],
        [
            "Tool fixtures",
            item.case.tool_fixtures.length,
            "Recorded results; unknown interactions stop execution.",
        ],
    ]) {
        const card = element("article");
        card.append(
            element("h3", title),
            element("strong", String(value)),
            element("p", description),
        );
        $("evidence-summary").append(card);
    }
    $("draft-state").textContent = "No unsaved changes.";
    $("acknowledge").checked = false;
    renderRules();
    $("case-json").value = pretty(state.draft);
    $("selected-rule").replaceChildren();
    for (const rule of item.case.rules) {
        const option = element("option", `${rule.id} · ${rule.kind}`);
        option.value = rule.id;
        $("selected-rule").append(option);
    }
    if (item.manifest.review) {
        $("reviewer").value = item.manifest.review.reviewer;
        $("selected-rule").value = item.manifest.review.selected_rule;
    }
}
function renderRules() {
    $("rule-editors").replaceChildren();
    state.draft.rules.forEach((rule, index) => {
        const card = element("div", undefined, "rule-card"),
            top = element("div", undefined, "rule-top");
        top.append(element("h3", `${index + 1}. ${rule.kind} · ${rule.id}`));
        const remove = element("button", "Remove");
        remove.setAttribute("aria-label", `Remove rule ${index + 1}`);
        remove.addEventListener("click", () => {
            try {
                readRules();
                state.draft.rules.splice(index, 1);
                advancedSource = null;
                dirty();
                renderRules();
                $("case-json").value = pretty(state.draft);
            } catch (err) {
                error(err);
            }
        });
        top.append(remove);
        const label = element("label", `Rule ${index + 1} JSON`);
        label.htmlFor = `rule-${index}`;
        const editor = element("textarea");
        editor.id = `rule-${index}`;
        editor.rows = Math.min(15, Object.keys(rule).length + 3);
        editor.spellcheck = false;
        editor.value = pretty(rule);
        editor.addEventListener("input", () => {
            advancedSource = null;
            dirty();
        });
        card.append(top, label, editor);
        $("rule-editors").append(card);
    });
}
function readRules() {
    state.draft.rules = [...$("rule-editors").querySelectorAll("textarea")].map(
        (editor) => JSON.parse(editor.value),
    );
}
function template(kind) {
    const base = {
        id: `rule-${Date.now()}`,
        requirement: "Describe the expected application behavior",
        kind,
    };
    const tool = state.draft.tool_fixtures[0]?.tool || "tool_name";
    return {
        ...base,
        ...{
            tool_call_count: {
                tool,
                group_by: [],
                min_calls: 0,
                max_calls: 1,
                require_any: true,
            },
            tool_argument: {
                tool,
                pointer: "/amount",
                operator: "lte",
                expected: 100,
                require_any: true,
            },
            forbidden_tool: { tool },
            output: { pointer: "/status", operator: "eq", expected: "ok" },
            max_tool_calls: { max_calls: 1 },
        }[kind],
    };
}
on("add-rule", () => {
    readRules();
    advancedSource = null;
    state.draft.rules.push(template($("rule-kind").value));
    dirty();
    renderRules();
    $("case-json").value = pretty(state.draft);
});
on("propose", async () => {
    saved();
    const result = await api("/api/propose", payload());
    state.draft.rules = result.rules;
    dirty();
    renderRules();
    $("case-json").value = pretty(state.draft);
    notice("Suggestions are unapproved. Inspect each rule, save, then review.");
});
$("case-json").addEventListener("input", () => {
    dirty();
    $("draft-state").textContent =
        "Advanced JSON changed. Apply JSON to draft, then save.";
});
let advancedApplied = true;
let advancedSource = null;
$("case-json").addEventListener("input", () => {
    advancedApplied = false;
});
on("apply-json", () => {
    state.draft = JSON.parse($("case-json").value);
    if (!Array.isArray(state.draft.rules))
        throw new Error("The case needs a rules array.");
    advancedApplied = true;
    advancedSource = $("case-json").value;
    dirty();
    renderRules();
    notice("JSON applied to draft; save to validate its schema.");
});
on("save", async () => {
    if (!advancedApplied)
        throw new Error("Apply advanced JSON to the draft before saving.");
    readRules();
    const item = await api(
        "/api/edit",
        payload(
            advancedSource !== null
                ? { case_text: advancedSource }
                : {
                      case_text: pretty(state.draft),
                      rule_texts: [
                          ...$("rule-editors").querySelectorAll("textarea"),
                      ].map((editor) => editor.value),
                  },
        ),
    );
    showCase(item);
    await refresh();
    notice("Case saved. Prior review and baseline validation were cleared.");
});
on("review", async () => {
    saved();
    const item = await api(
        "/api/review",
        payload({
            reviewer: $("reviewer").value,
            selected_rule: $("selected-rule").value,
            acknowledged: $("acknowledge").checked,
        }),
    );
    showCase(item);
    await refresh();
    notice("Exact case approved. Validate the known failing baseline next.");
    tab("execution");
});
on("refresh", refresh);
on("import-open", () => {
    saved();
    $("import-error").textContent = "";
    $("import-dialog").showModal();
    $("import-name").focus();
});
on("import-close", () => $("import-dialog").close());
$("import-file").addEventListener("change", async () => {
    const file = $("import-file").files[0];
    if (!file) return;
    if (file.size > 10 * 1024 * 1024) {
        $("import-json").value = "";
        $("import-error").textContent = "The file exceeds 10 MiB.";
        return;
    }
    $("import-json").value = await file.text();
});
$("import-form").addEventListener("submit", async (event) => {
    event.preventDefault();
    const button = event.submitter;
    button.disabled = true;
    try {
        saved();
        const item = await api("/api/import", {
            name: $("import-name").value,
            source_text: $("import-json").value,
        });
        $("import-json").value = "";
        $("import-file").value = "";
        $("import-dialog").close();
        showCase(item);
        await refresh();
        tab("evidence");
        notice(
            "Evidence sanitized and imported. Inspect the report and review the rules.",
        );
    } catch (err) {
        $("import-error").textContent = err.message;
    } finally {
        button.disabled = false;
    }
});
async function importSample() {
    saved();
    const item = await api("/api/import-sample", {
        name: `example-${Date.now()}`,
    });
    showCase(item);
    await refresh();
    $("import-dialog").close();
    tab("evidence");
    notice("Sample imported. Review the case before execution.");
}
on("sample", importSample);
on("welcome-sample", importSample);
on("import-sample", importSample);
function executionButtons() {
    for (const id of [
        "validate",
        "run",
        "reduce",
        "save",
        "review",
        "propose",
        "import-open",
        "sample",
        "welcome-sample",
        "import-sample",
        "runner",
        "preview",
    ])
        $(id).disabled = state.busy;
    for (const control of $("panel-review").querySelectorAll(
        "button, input, textarea, select",
    ))
        control.disabled = state.busy;
    $("ai-send").disabled =
        state.busy || !aiPreview || !$("ai-consent").checked;
}
async function startJob(action) {
    saved();
    const extra = { action, runner: $("runner").value };
    if (action === "reduce") {
        extra.name = $("reduce-name").value;
        extra.max_runs = Number($("max-runs").value);
    }
    const job = await api("/api/jobs", payload(extra));
    state.busy = true;
    state.job = job;
    executionButtons();
    invalidatePreview();
    $("job-status").textContent =
        `Running ${action} with ${job.runner}. ${action === "reduce" ? "30-second total reduction budget." : "Worker timeout capped at 30 seconds."} Keep this session open.`;
    notice(`Execution started: ${action}.`);
    pollJob(job.id);
}
async function pollJob(id) {
    try {
        const job = await api(`/api/jobs/${id}`);
        state.job = job;
        if (job.status === "running") {
            setTimeout(() => pollJob(id), 350);
            return;
        }
        state.busy = false;
        executionButtons();
        $("job-status").textContent =
            `${job.action} · ${job.runner || job.profile} · ${job.status}`;
        if (job.action === "suggest" && job.status === "error")
            $("ai-status").textContent =
                "Suggestion request failed. The saved case was not changed.";
        if (job.status === "error")
            throw new Error(`${job.error.code}: ${job.error.message}`);
        if (job.action === "suggest") {
            renderSuggestion(job.result);
            notice(
                "AI suggestions received. Inspect them before applying to the draft.",
            );
            return;
        }
        const updated = await api(
            `/api/case?path=${encodeURIComponent(state.current.path)}`,
        );
        showCase(updated);
        await refresh();
        if (job.action === "reduce") renderReduction(job.result);
        else renderRun(job, updated);
        notice("Execution finished. Inspect the outcome below.");
    } catch (err) {
        error(err);
        if (state.busy) {
            $("job-status").textContent =
                "Connection lost. Server job may still be running. Retrying…";
            setTimeout(() => pollJob(id), 1500);
        }
    }
}
function renderRun(job, item) {
    const r = job.result,
        container = $("run-result");
    container.replaceChildren();
    let text, style;
    if (r.execution_status !== "complete") {
        text = "Incomplete execution · assertions were not evaluated";
        style = "warning";
    } else if (job.action === "validate") {
        text = item.baseline_valid
            ? "Baseline reproduced · selected assertion failed as expected"
            : "Baseline not reproduced · selected assertion did not fail";
        style = item.baseline_valid ? "success" : "warning";
    } else {
        text =
            r.outcome === "pass"
                ? "Regression passed · all reviewed assertions hold"
                : "Regression failed · review the assertion results";
        style = r.outcome === "pass" ? "success" : "failure";
    }
    container.append(
        element("h3", text, style),
        element(
            "p",
            `${job.runner} · ${r.execution_status} · ${r.outcome}`,
            "muted",
        ),
    );
    for (const rule of r.rule_results || []) {
        const row = element("article");
        row.append(
            element("h3", `${rule.passed ? "PASS" : "FAIL"} · ${rule.rule_id}`),
            element("p", rule.reason),
        );
        container.append(row);
    }
    codeBlock(container, "Full execution report", r);
}
function renderReduction(result) {
    const parent = $("reduction-result");
    parent.replaceChildren(element("h3", "Derived case needs a new review"));
    const comparison = element("div", undefined, "comparison");
    codeBlock(comparison, "Original input", result.original_input, true);
    codeBlock(comparison, "Reduced input", result.reduced_input, true);
    parent.append(comparison);
    codeBlock(parent, "Reduction report", result.report, true);
    const open = element("button", "Open derived case for review", "primary");
    open.addEventListener("click", () =>
        openCase(result.derived_path)
            .then(() => tab("review"))
            .catch(error),
    );
    parent.append(open);
}
on("validate", () => startJob("validate"));
on("run", () => startJob("run"));
on("reduce", () => startJob("reduce"));
function exportPayload() {
    saved();
    return payload({ runner: $("runner").value, name: $("export-name").value });
}
on("preview", async () => {
    const input = exportPayload();
    const result = await api("/api/export-preview", input);
    state.preview = pretty(input);
    $("export-result").replaceChildren(
        element("p", `Preview only · ${result.path}`, "muted"),
    );
    for (const [name, content] of Object.entries(result.files))
        codeBlock(
            $("export-result"),
            name,
            content,
            name === "test_regression.py",
        );
    $("export").disabled = false;
    $("export-help").textContent =
        "Save export is now enabled. Inspect the preview, then click it to write these files.";
    notice("Preview prepared. No files have been written.");
});
on("export", async () => {
    const input = exportPayload();
    if (state.preview !== pretty(input))
        throw new Error("Preview these exact export settings first.");
    const result = await api("/api/export", input);
    $("export").disabled = true;
    $("export-help").textContent =
        "Export saved. To create another export, choose a new directory and preview again.";
    notice(
        `Export saved to ${result.path}. Run it with your normal pytest workflow.`,
    );
    $("export-result").prepend(
        element("p", `Saved: ${result.path}`, "success"),
    );
});
$("runner").addEventListener("change", invalidatePreview);
let aiPreview = null;
function invalidateAI() {
    aiPreview = null;
    $("ai-consent").checked = false;
    $("ai-send").disabled = true;
    $("ai-preview-content").replaceChildren();
    $("ai-result").replaceChildren();
    $("ai-status").textContent = "";
}
function aiPayload() {
    saved();
    return payload({
        profile: $("ai-profile").value,
        requirement: $("ai-requirement").value,
    });
}
on("ai-preview", async () => {
    const result = await api("/api/ai-preview", aiPayload());
    invalidateAI();
    aiPreview = result;
    $("ai-preview-content").append(
        element(
            "p",
            `${result.destination} · ${result.settings.model} · ${result.settings.free_only ? "Free-only profile" : "Pricing depends on your provider"}`,
            "warning",
        ),
    );
    codeBlock(
        $("ai-preview-content"),
        "Exact sanitized AI request",
        result.request,
        true,
    );
    notice(
        "Preview only. No provider request has been sent. Review the payload and destination.",
    );
});
$("ai-consent").addEventListener("change", () => {
    $("ai-send").disabled =
        state.busy || !aiPreview || !$("ai-consent").checked;
});
$("ai-profile").addEventListener("change", invalidateAI);
$("ai-requirement").addEventListener("input", invalidateAI);
on("ai-send", async () => {
    const input = aiPayload();
    if (!aiPreview || !$("ai-consent").checked)
        throw new Error("Preview and acknowledge this request first.");
    const job = await api("/api/ai-propose", {
        ...input,
        request_digest: aiPreview.request_digest,
        acknowledged: true,
    });
    state.busy = true;
    state.job = job;
    executionButtons();
    $("ai-status").textContent =
        `Requesting unapproved suggestions from ${job.profile}…`;
    pollJob(job.id);
});
function renderSuggestion(result) {
    $("ai-status").textContent =
        `Suggestions received · ${result.actual_model} · review required`;
    const parent = $("ai-result");
    parent.replaceChildren();
    codeBlock(parent, "Unapproved AI suggestions", result, true);
    const apply = element("button", "Apply suggestions to draft");
    apply.addEventListener("click", () => {
        try {
            saved();
            if (state.current.digest !== result.case_digest)
                throw new Error("STALE_CASE: Request fresh suggestions.");
            state.draft.rules = structuredClone(result.rules);
            advancedSource = null;
            advancedApplied = true;
            dirty();
            renderRules();
            $("case-json").value = pretty(state.draft);
            notice(
                "Suggestions applied to draft. Inspect, save and approve the case before running it.",
            );
        } catch (err) {
            error(err);
        }
    });
    parent.append(apply);
}
$("export-name").addEventListener("input", invalidatePreview);
window.addEventListener("beforeunload", (event) => {
    if (state.dirty || state.busy) {
        event.preventDefault();
        event.returnValue = "";
    }
});
(async () => {
    try {
        const workspace = await api("/api/workspace");
        $("workspace-name").textContent = workspace.name;
        $("sample").hidden = !workspace.sample_available;
        $("welcome-sample").hidden = !workspace.sample_available;
        $("import-sample").hidden = !workspace.sample_available;
        $("sample-setup").hidden = workspace.sample_available;
        $("config-name").textContent =
            `Trusted configuration: ${workspace.config}`;
        for (const [name, settings] of Object.entries(
            workspace.suggestion_profiles || {},
        )) {
            const option = element("option", `${name} · ${settings.model}`);
            option.value = name;
            $("ai-profile").append(option);
        }
        $("ai-setup").textContent = workspace.suggestion_error
            ? `${workspace.suggestion_error.code}: ${workspace.suggestion_error.message} Key-free suggestions remain available.`
            : $("ai-profile").options.length
              ? "Credentials stay on the local server. No key is sent to this browser."
              : "Add suggestions.profiles to your trusted TOML configuration to enable provider selection. Key-free suggestions remain available.";
        for (const runner of workspace.runners) {
            const option = element("option", runner);
            option.value = runner;
            $("runner").append(option);
        }
        await refresh();
    } catch (err) {
        error(err);
        $("workspace-name").textContent = "Session unavailable";
    }
})();
