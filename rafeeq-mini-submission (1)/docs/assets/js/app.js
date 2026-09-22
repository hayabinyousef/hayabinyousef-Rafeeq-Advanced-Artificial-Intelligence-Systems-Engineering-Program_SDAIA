(() => {
  "use strict";

  const LANGUAGE_KEY = "rafeeq-language";
  const STEP_KEY = "rafeeq-setup-step";
  const READINESS_KEY = "rafeeq-readiness-check";
  const UPLOAD_KEY = "rafeeq-upload-checklist";
  const root = document.documentElement;
  const languageButtons = [...document.querySelectorAll("[data-lang-switch]")];

  const setupSteps = [
    {
      icon: "◉",
      titleEn: "Create account",
      titleAr: "إنشاء الحساب",
      bodyEn: "Create a personal GitHub account, verify your email, and choose a professional username.",
      bodyAr: "أنشئ حساب GitHub شخصيًا، ووثّق بريدك، واختر اسم مستخدم مهنيًا.",
      actionUrl: "https://github.com/signup",
      actionText: "Open GitHub signup · افتح تسجيل GitHub ↗",
    },
    {
      icon: "⑂",
      titleEn: "Create repository",
      titleAr: "إنشاء المستودع",
      bodyEn: "Create a public repository, add a clear About description, and create only LEARNING_PROGRESS.md from the safe template. Keep code and runtime evidence in Drive until C29.",
      bodyAr: "أنشئ مستودعًا عامًا، وأضف وصف About واضحًا، وأنشئ فقط LEARNING_PROGRESS.md من القالب الآمن. أبقِ الكود وأدلة التشغيل في Drive حتى C29.",
      actionUrl: "https://github.com/new",
      actionText: "Create repository · أنشئ المستودع ↗",
    },
    {
      icon: "☁",
      titleEn: "Prepare Colab",
      titleAr: "تجهيز كولاب",
      bodyEn: "Open the verified notebook, save a working copy in Drive, and keep the standard CPU runtime.",
      bodyAr: "افتح الدفتر بعد التحقق منه، واحفظ نسخة عمل في Drive، واستخدم بيئة CPU القياسية.",
      actionUrl: "https://colab.research.google.com/github/almiyead-rgb/rafeeq-agentic-ai-labs/blob/v0.9.0-rc3/notebooks/Rafeeq_Mini_Capstone.ipynb",
      actionText: "Open Colab · افتح كولاب ↗",
    },
    {
      icon: "✓",
      titleEn: "Reach C0 READY",
      titleAr: "الوصول إلى C0 READY",
      bodyEn: "Run C0_ENV_DOCTOR and continue only when every check passes and all_passed=true.",
      bodyAr: "شغّل C0_ENV_DOCTOR، ولا تتابع حتى تنجح جميع الفحوص وتظهر all_passed=true.",
      actionUrl: "https://github.com/almiyead-rgb/rafeeq-agentic-ai-labs/blob/v0.9.0-rc3/notebooks/Rafeeq_Mini_Capstone.ipynb",
      actionText: "View notebook source · اعرض ملف الدفتر →",
    },
  ];

  function safeRead(key) {
    try {
      return localStorage.getItem(key);
    } catch (_error) {
      return null;
    }
  }

  function safeWrite(key, value) {
    try {
      localStorage.setItem(key, value);
    } catch (_error) {
      // Local preferences are optional; the portal remains usable without storage.
    }
  }

  function applyLanguage(language) {
    const allowed = ["en", "both", "ar"];
    const next = allowed.includes(language) ? language : "both";
    root.dataset.language = next;
    root.lang = next === "ar" ? "ar" : "en";
    root.dir = next === "ar" ? "rtl" : "ltr";
    languageButtons.forEach((button) => {
      const active = button.dataset.langSwitch === next;
      button.classList.toggle("active", active);
      button.setAttribute("aria-pressed", String(active));
    });
    safeWrite(LANGUAGE_KEY, next);
  }

  const savedLanguage = safeRead(LANGUAGE_KEY);
  // Keep the promised side-by-side bilingual experience on every screen size.
  // Learners can still switch to one language explicitly, and that preference
  // remains local to their browser.
  const defaultLanguage = savedLanguage || "both";
  applyLanguage(defaultLanguage);
  languageButtons.forEach((button) => button.addEventListener("click", () => applyLanguage(button.dataset.langSwitch)));

  const board = document.querySelector("[data-setup-board]");
  if (board) {
    const stepButtons = [...board.querySelectorAll("[data-step]")];
    const progress = board.querySelector(".setup-progress");
    const progressBar = progress?.querySelector("span");
    const icon = board.querySelector("[data-step-icon]");
    const countEn = board.querySelector("[data-step-count-en]");
    const countAr = board.querySelector("[data-step-count-ar]");
    const titleEn = board.querySelector("[data-step-title-en]");
    const titleAr = board.querySelector("[data-step-title-ar]");
    const bodyEn = board.querySelector("[data-step-body-en]");
    const bodyAr = board.querySelector("[data-step-body-ar]");
    const nextButton = board.querySelector("[data-next-step]");
    const actionLink = board.querySelector("[data-step-action]");
    const panel = board.querySelector('[role="tabpanel"]');
    const savedStep = Number.parseInt(safeRead(STEP_KEY) || "0", 10);
    let activeStep = Number.isFinite(savedStep) ? Math.min(Math.max(savedStep, 0), setupSteps.length - 1) : 0;

    function renderStep(index) {
      activeStep = Math.min(Math.max(index, 0), setupSteps.length - 1);
      const step = setupSteps[activeStep];
      stepButtons.forEach((button, buttonIndex) => {
        button.classList.toggle("current", buttonIndex === activeStep);
        button.classList.toggle("done", buttonIndex < activeStep);
        button.setAttribute("aria-selected", String(buttonIndex === activeStep));
        button.tabIndex = buttonIndex === activeStep ? 0 : -1;
      });
      if (panel) panel.setAttribute("aria-labelledby", stepButtons[activeStep].id);
      if (progressBar) progressBar.style.width = `${((activeStep + 1) / setupSteps.length) * 100}%`;
      if (progress) progress.setAttribute("aria-valuenow", String(activeStep + 1));
      if (icon) icon.textContent = step.icon;
      if (countEn) countEn.textContent = `STEP ${activeStep + 1} OF ${setupSteps.length}`;
      if (countAr) countAr.textContent = `الخطوة ${activeStep + 1} من ${setupSteps.length}`;
      if (titleEn) titleEn.textContent = step.titleEn;
      if (titleAr) titleAr.textContent = step.titleAr;
      if (bodyEn) bodyEn.textContent = step.bodyEn;
      if (bodyAr) bodyAr.textContent = step.bodyAr;
      if (actionLink) {
        actionLink.href = step.actionUrl;
        actionLink.textContent = step.actionText;
      }
      if (nextButton) {
        nextButton.innerHTML = activeStep === setupSteps.length - 1
          ? "Return to first step · عُد إلى الخطوة الأولى <span aria-hidden=\"true\">↺</span>"
          : "Next step · الخطوة التالية <span aria-hidden=\"true\">→</span>";
      }
      safeWrite(STEP_KEY, String(activeStep));
    }

    stepButtons.forEach((button) => {
      button.addEventListener("click", () => renderStep(Number(button.dataset.step)));
      button.addEventListener("keydown", (event) => {
        const keys = ["ArrowRight", "ArrowLeft", "Home", "End"];
        if (!keys.includes(event.key)) return;
        event.preventDefault();
        let target = activeStep;
        if (event.key === "Home") target = 0;
        if (event.key === "End") target = setupSteps.length - 1;
        if (event.key === "ArrowRight") target = (activeStep + 1) % setupSteps.length;
        if (event.key === "ArrowLeft") target = (activeStep - 1 + setupSteps.length) % setupSteps.length;
        renderStep(target);
        stepButtons[target].focus();
      });
    });
    nextButton?.addEventListener("click", () => renderStep(activeStep === setupSteps.length - 1 ? 0 : activeStep + 1));
    renderStep(activeStep);
  }

  function readBooleanList(key, length) {
    try {
      const value = JSON.parse(safeRead(key) || "[]");
      if (!Array.isArray(value)) return Array(length).fill(false);
      return Array.from({ length }, (_item, index) => value[index] === true);
    } catch (_error) {
      return Array(length).fill(false);
    }
  }

  function bindReadinessCheck() {
    const form = document.querySelector("[data-readiness-check]");
    if (!form) return;
    const inputs = [...form.querySelectorAll('input[type="checkbox"]')];
    const saved = readBooleanList(READINESS_KEY, inputs.length);
    inputs.forEach((input, index) => { input.checked = saved[index]; });

    const score = form.querySelector("[data-readiness-score]");
    const titleEn = form.querySelector("[data-readiness-title-en]");
    const titleAr = form.querySelector("[data-readiness-title-ar]");
    const bodyEn = form.querySelector("[data-readiness-body-en]");
    const bodyAr = form.querySelector("[data-readiness-body-ar]");

    function renderReadiness() {
      const count = inputs.filter((input) => input.checked).length;
      if (score) score.textContent = `${count}/${inputs.length}`;

      if (count === inputs.length) {
        if (titleEn) titleEn.textContent = "Ready for C1.";
        if (titleAr) titleAr.textContent = "جاهز للبدء في C1.";
        if (bodyEn) bodyEn.textContent = "Continue to C0_ENV_DOCTOR. Its result remains the official environment check.";
        if (bodyAr) bodyAr.textContent = "انتقل إلى C0_ENV_DOCTOR؛ فنتيجته هي فحص البيئة الرسمي.";
      } else if (count === inputs.length - 1) {
        if (titleEn) titleEn.textContent = "Almost ready.";
        if (titleAr) titleAr.textContent = "جاهز تقريبًا.";
        if (bodyEn) bodyEn.textContent = "Review the one unchecked skill, then run the guided setup before C1.";
        if (bodyAr) bodyAr.textContent = "راجع المهارة الوحيدة غير المحددة، ثم نفّذ التجهيز الموجّه قبل C1.";
      } else {
        if (titleEn) titleEn.textContent = "Start with the guided path.";
        if (titleAr) titleAr.textContent = "ابدأ بالمسار الموجّه.";
        if (bodyEn) bodyEn.textContent = "Complete the setup above and tell the trainer before C1 if you need a quick support check.";
        if (bodyAr) bodyAr.textContent = "أكمل خطوات التجهيز أعلاه، وأبلغ المدربة قبل C1 إذا احتجت فحص دعم سريعًا.";
      }
      safeWrite(READINESS_KEY, JSON.stringify(inputs.map((input) => input.checked)));
    }

    inputs.forEach((input) => input.addEventListener("change", renderReadiness));
    renderReadiness();
  }

  function bindUploadChecklist() {
    const wizard = document.querySelector("[data-upload-checklist]");
    if (!wizard) return;
    const inputs = [...wizard.querySelectorAll('.wizard-steps input[type="checkbox"]')];
    const saved = readBooleanList(UPLOAD_KEY, inputs.length);
    inputs.forEach((input, index) => { input.checked = saved[index]; });

    const countLabel = wizard.querySelector("[data-upload-count]");
    const progress = wizard.querySelector("[data-upload-progress]");
    const state = wizard.querySelector("[data-upload-state]");
    const messageEn = wizard.querySelector("[data-upload-message-en]");
    const messageAr = wizard.querySelector("[data-upload-message-ar]");

    function renderUpload() {
      const count = inputs.filter((input) => input.checked).length;
      const complete = count === inputs.length;
      if (countLabel) countLabel.textContent = `${count}/${inputs.length}`;
      if (progress) progress.style.width = `${(count / inputs.length) * 100}%`;
      if (state) {
        state.textContent = complete ? "READY TO SUBMIT · جاهز للتسليم" : "IN PROGRESS · قيد التنفيذ";
        state.classList.toggle("complete", complete);
      }
      if (messageEn) messageEn.textContent = complete
        ? "All upload checks are complete. Use the channel announced by the trainer."
        : "Complete all eight checks before opening the submission channel.";
      if (messageAr) messageAr.textContent = complete
        ? "اكتملت فحوص الرفع. استخدم قناة التسليم التي أعلنتها المدربة."
        : "أكمل الفحوص الثمانية قبل فتح قناة التسليم.";
      safeWrite(UPLOAD_KEY, JSON.stringify(inputs.map((input) => input.checked)));
    }

    inputs.forEach((input) => input.addEventListener("change", renderUpload));
    renderUpload();
  }

  async function loadSiteMeta() {
    try {
      const response = await fetch("assets/data/site-meta.json", { cache: "no-store" });
      if (!response.ok) return;
      const meta = await response.json();

      document.querySelectorAll("[data-meta-deadline-en]").forEach((node) => {
        node.textContent = meta.submission_deadline_en || "Announced by the trainer";
      });
      document.querySelectorAll("[data-meta-deadline-ar]").forEach((node) => {
        node.textContent = meta.submission_deadline_ar || "تعلنه المدربة أثناء الدورة";
      });
      document.querySelectorAll("[data-meta-form-en]").forEach((node) => {
        node.textContent = meta.submission_channel_en || "Announced by the trainer";
      });
      document.querySelectorAll("[data-meta-form-ar]").forEach((node) => {
        node.textContent = meta.submission_channel_ar || "تعلنها المدربة أثناء الدورة";
      });
      document.querySelectorAll("[data-meta-passing-score]").forEach((node) => {
        node.textContent = String(meta.passing_score ?? 70);
      });
      document.querySelectorAll("[data-support-link]").forEach((link) => {
        if (meta.support_issue_url) link.href = meta.support_issue_url;
      });

      const submissionLink = document.querySelector("[data-submission-link]");
      const submissionLabel = submissionLink?.querySelector("[data-submission-link-label]");
      if (submissionLink && meta.submission_form_url) {
        submissionLink.href = meta.submission_form_url;
        submissionLink.target = "_blank";
        submissionLink.rel = "noopener noreferrer";
        submissionLink.classList.remove("unavailable");
        submissionLink.setAttribute("aria-disabled", "false");
        if (submissionLabel) submissionLabel.textContent = "Open submission form · افتح نموذج التسليم";
      } else if (submissionLabel) {
        submissionLabel.textContent = `${meta.submission_link_en || "Submission link announced by trainer"} · ${meta.submission_link_ar || "رابط التسليم تعلنه المدربة"}`;
      }
    } catch (_error) {
      // Static fallback text keeps every instruction usable when metadata cannot be loaded.
    }
  }

  bindReadinessCheck();
  bindUploadChecklist();
  loadSiteMeta();

  const copyButton = document.querySelector("[data-copy-help]");
  const toast = document.querySelector("[data-toast]");
  const helpTemplate = [
    "Rafeeq Mini — Safe help request",
    "1. Cell ID / رقم الخلية:",
    "2. Last passed gate / آخر بوابة ناجحة:",
    "3. First useful error line / أول سطر خطأ مفيد:",
    "4. Expected behavior / السلوك المتوقع:",
    "5. Actual behavior / السلوك الفعلي:",
    "6. Runtime type and whether it reset / نوع البيئة وهل أعيد ضبطها:",
    "No passwords, tokens, private links, or real customer data.",
  ].join("\n");

  async function copyText(text) {
    if (navigator.clipboard && window.isSecureContext) {
      await navigator.clipboard.writeText(text);
      return;
    }
    const field = document.createElement("textarea");
    field.value = text;
    field.setAttribute("readonly", "");
    field.style.position = "fixed";
    field.style.opacity = "0";
    document.body.append(field);
    field.select();
    document.execCommand("copy");
    field.remove();
  }

  copyButton?.addEventListener("click", async () => {
    try {
      await copyText(helpTemplate);
      if (toast) {
        toast.hidden = false;
        window.setTimeout(() => { toast.hidden = true; }, 2600);
      }
    } catch (_error) {
      if (toast) {
        toast.textContent = "Copy unavailable · تعذر النسخ";
        toast.hidden = false;
        window.setTimeout(() => {
          toast.hidden = true;
          toast.textContent = "Copied safely · تم النسخ بأمان";
        }, 2600);
      }
    }
  });
})();
