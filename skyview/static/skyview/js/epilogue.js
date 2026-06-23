document.addEventListener("DOMContentLoaded", function () {
  initEpilogueModal();
});

function initEpilogueModal() {
  const epilogueBtn = document.getElementById("hero-epilogue-btn");
  const epilogueModal = document.getElementById("epilogue-modal");
  const epilogueIframe = document.getElementById("epilogue-iframe");
  const closeBtn = document.getElementById("close-epilogue-modal-btn");
  const titleEl = document.getElementById("epilogue-modal-title");

  if (!epilogueBtn || !epilogueModal || !epilogueIframe) {
    return;
  }

  const epilogueUrl = epilogueBtn.getAttribute("data-epilogue-url");
  const epilogueTitle = epilogueBtn.getAttribute("data-epilogue-title");

  function openEpilogueModal() {
    if (!epilogueUrl) {
      return;
    }

    if (titleEl && epilogueTitle) {
      titleEl.textContent = epilogueTitle;
    }

    epilogueIframe.src = epilogueUrl;
    epilogueModal.classList.add("map-modal--open");
    epilogueModal.setAttribute("aria-hidden", "false");
    document.body.style.overflow = "hidden";
  }

  function closeEpilogueModal() {
    epilogueModal.classList.remove("map-modal--open");
    epilogueModal.setAttribute("aria-hidden", "true");
    epilogueIframe.src = "about:blank";
    document.body.style.overflow = "";
  }

  epilogueBtn.addEventListener("click", openEpilogueModal);

  if (closeBtn) {
    closeBtn.addEventListener("click", closeEpilogueModal);
  }

  epilogueModal.addEventListener("click", function (event) {
    if (event.target === epilogueModal) {
      closeEpilogueModal();
    }
  });

  document.addEventListener("keydown", function (event) {
    if (event.key === "Escape" && epilogueModal.classList.contains("map-modal--open")) {
      closeEpilogueModal();
    }
  });
}
