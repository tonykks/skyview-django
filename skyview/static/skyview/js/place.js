document.addEventListener("DOMContentLoaded", function () {
  initIntroModal();
  initMapModal();
});

function initIntroModal() {
  const introBtn = document.getElementById("place-intro-btn");
  const introModal = document.getElementById("intro-modal");
  const introIframe = document.getElementById("intro-iframe");
  const closeIntroBtn = document.getElementById("close-intro-modal-btn");

  if (!introBtn || !introModal || !introIframe) {
    return;
  }

  const introUrl = introBtn.getAttribute("data-intro-url");

  function openIntroModal() {
    if (!introUrl) {
      alert("소개 페이지 URL이 없습니다.");
      return;
    }

    introIframe.src = introUrl;
    introModal.classList.add("map-modal--open");
    introModal.setAttribute("aria-hidden", "false");
    document.body.style.overflow = "hidden";
  }

  function closeIntroModal() {
    introModal.classList.remove("map-modal--open");
    introModal.setAttribute("aria-hidden", "true");
    introIframe.src = "about:blank";
    document.body.style.overflow = "";
  }

  introBtn.addEventListener("click", openIntroModal);

  if (closeIntroBtn) {
    closeIntroBtn.addEventListener("click", closeIntroModal);
  }

  introModal.addEventListener("click", function (event) {
    if (event.target === introModal) {
      closeIntroModal();
    }
  });

  document.addEventListener("keydown", function (event) {
    if (event.key === "Escape" && introModal.classList.contains("map-modal--open")) {
      closeIntroModal();
    }
  });
}

function initMapModal() {
  const locBtn = document.getElementById("place-location-btn");
  const mapModal = document.getElementById("map-modal");
  const mapContainer = document.getElementById("place-map-modal-map");
  const mapTitle = document.getElementById("map-modal-title");
  const closeMapBtn = document.getElementById("close-map-modal-btn");

  if (!mapModal || !mapContainer || typeof L === "undefined") {
    return;
  }

  const lat = locBtn ? parseFloat(locBtn.getAttribute("data-lat")) : NaN;
  const lng = locBtn ? parseFloat(locBtn.getAttribute("data-lng")) : NaN;
  const placeName =
    (locBtn && locBtn.getAttribute("data-name")) || "위치";
  const hasLatLng = Number.isFinite(lat) && Number.isFinite(lng);

  let modalMap = null;
  let modalMarker = null;

  function ensureMap() {
    if (modalMap) {
      return modalMap;
    }

    modalMap = L.map(mapContainer, { zoomControl: true }).setView(
      hasLatLng ? [lat, lng] : [33.35, 126.53],
      13
    );
    L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
      maxZoom: 19,
      attribution: "© OpenStreetMap contributors",
    }).addTo(modalMap);

    return modalMap;
  }

  function openMapModal() {
    if (!hasLatLng) {
      alert(
        "이 장소는 아직 좌표가 없습니다. Places의 latitude/longitude를 입력해주세요."
      );
      return;
    }

    const map = ensureMap();
    map.setView([lat, lng], 13);

    if (modalMarker) {
      map.removeLayer(modalMarker);
    }

    modalMarker = L.marker([lat, lng]).addTo(map);
    modalMarker.bindTooltip(placeName, {
      permanent: true,
      direction: "top",
      className: "place-map-label",
    });

    if (mapTitle) {
      mapTitle.textContent = placeName + " 위치";
    }

    mapModal.classList.add("map-modal--open");
    mapModal.setAttribute("aria-hidden", "false");
    document.body.style.overflow = "hidden";

    setTimeout(function () {
      map.invalidateSize();
    }, 100);
  }

  function closeMapModal() {
    mapModal.classList.remove("map-modal--open");
    mapModal.setAttribute("aria-hidden", "true");
    document.body.style.overflow = "";
  }

  if (locBtn) {
    locBtn.addEventListener("click", openMapModal);
  }

  if (closeMapBtn) {
    closeMapBtn.addEventListener("click", closeMapModal);
  }

  mapModal.addEventListener("click", function (event) {
    if (event.target === mapModal) {
      closeMapModal();
    }
  });

  document.addEventListener("keydown", function (event) {
    if (event.key === "Escape" && mapModal.classList.contains("map-modal--open")) {
      closeMapModal();
    }
  });
}
