const lb = document.getElementById("lightbox");
const lbTarget = document.getElementById("lightbox-player");
const lbClose = document.getElementById("lb-close");

function openLightbox(youtubeId, videoType) {
  if (!youtubeId || !lb || !lbTarget) {
    return;
  }

  lbTarget.innerHTML = "";
  lbTarget.className = "lightbox-player";

  if (videoType === "S") {
    lbTarget.classList.add("lightbox-player--shorts");
  } else {
    lbTarget.classList.add("lightbox-player--landscape");
  }

  const iframe = document.createElement("iframe");
  iframe.src =
    "https://www.youtube.com/embed/" +
    youtubeId +
    "?autoplay=1&mute=0&playsinline=1";
  iframe.allow = "autoplay; encrypted-media";
  iframe.allowFullscreen = true;
  iframe.setAttribute("frameborder", "0");
  iframe.setAttribute("referrerpolicy", "strict-origin-when-cross-origin");
  iframe.title =
    videoType === "S" ? "YouTube Shorts player" : "YouTube video player";

  lbTarget.appendChild(iframe);
  lb.style.display = "flex";
  lb.setAttribute("aria-hidden", "false");
  document.body.style.overflow = "hidden";
}

function closeLightbox() {
  if (!lb || !lbTarget) {
    return;
  }

  lbTarget.innerHTML = "";
  lb.style.display = "none";
  lb.setAttribute("aria-hidden", "true");
  document.body.style.overflow = "";
}

function playFromElement(element) {
  if (!element) {
    return;
  }

  openLightbox(
    element.getAttribute("data-youtube-id"),
    element.getAttribute("data-video-type") || "L"
  );
}

document.addEventListener("DOMContentLoaded", function () {
  document
    .querySelectorAll(".hero--playable[data-youtube-id]")
    .forEach(function (hero) {
      hero.addEventListener("click", function () {
        playFromElement(hero);
      });

      hero.addEventListener("keydown", function (event) {
        if (event.key === "Enter" || event.key === " ") {
          event.preventDefault();
          playFromElement(hero);
        }
      });
    });

  document.querySelectorAll(".card[data-youtube-id]").forEach(function (card) {
    card.addEventListener("click", function (event) {
      if (event.target.closest(".card__action")) {
        return;
      }
      playFromElement(card);
    });

    card.addEventListener("keydown", function (event) {
      if (event.key === "Enter" || event.key === " ") {
        event.preventDefault();
        playFromElement(card);
      }
    });
  });

  if (lbClose) {
    lbClose.addEventListener("click", closeLightbox);
  }

  if (lb) {
    lb.addEventListener("click", function (event) {
      if (event.target === lb) {
        closeLightbox();
      }
    });
  }

  document.addEventListener("keydown", function (event) {
    if (event.key === "Escape") {
      closeLightbox();
    }
  });
});
