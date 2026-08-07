(() => {
  const screenshots = [...document.querySelectorAll(".theme-screenshot")];

  if (screenshots.length === 0) return;

  let appearance = "dark";

  try {
    if (window.localStorage.getItem("headmon-screenshot-appearance") === "light") {
      appearance = "light";
    }
  } catch (_) {
    appearance = "dark";
  }

  const applyAppearance = (nextAppearance) => {
    appearance = nextAppearance === "light" ? "light" : "dark";
    const opposite = appearance === "dark" ? "light" : "dark";

    screenshots.forEach((screenshot) => {
      screenshot.src = appearance === "dark"
        ? screenshot.dataset.darkSrc
        : screenshot.dataset.lightSrc;
      screenshot.dataset.appearance = appearance;
      screenshot.tabIndex = 0;
      screenshot.setAttribute("role", "button");
      screenshot.setAttribute(
        "aria-label",
        `${screenshot.alt}. ${appearance} appearance. Activate to show ${opposite} appearance.`
      );
    });

    try {
      window.localStorage.setItem("headmon-screenshot-appearance", appearance);
    } catch (_) {
      // The screenshots still switch when browser storage is unavailable.
    }
  };

  screenshots.forEach((screenshot) => {
    const toggle = () => {
      applyAppearance(appearance === "dark" ? "light" : "dark");
    };

    screenshot.addEventListener("click", toggle);
    screenshot.addEventListener("keydown", (event) => {
      if (event.key === "Enter" || event.key === " ") {
        event.preventDefault();
        toggle();
      }
    });
  });

  applyAppearance(appearance);
})();
