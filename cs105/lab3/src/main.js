(function () {
  const registry = window.FractalRegistry || {};
  const orderedKeys = [
    "kochSnowflake",
    "minkowskiIsland",
    "sierpinskiTriangle",
    "sierpinskiSquare",
    "mandelbrot",
    "julia",
  ];

  const fractals = orderedKeys
    .map(function (key) {
      if (!registry[key] || typeof registry[key].draw !== "function") {
        return null;
      }
      return {
        key: key,
        label: registry[key].label,
        minLevel: registry[key].minLevel,
        maxLevel: registry[key].maxLevel,
        defaultLevel: registry[key].defaultLevel,
        description: registry[key].description,
        draw: registry[key].draw,
      };
    })
    .filter(Boolean);

  if (fractals.length === 0) {
    return;
  }

  const canvas = document.getElementById("fractalCanvas");
  const typeSelect = document.getElementById("fractalType");
  const levelRange = document.getElementById("levelRange");
  const levelValue = document.getElementById("levelValue");
  const fractalDescription = document.getElementById("fractalDescription");
  const levelBound = document.getElementById("levelBound");
  const cInputContainer = document.getElementById("cInputContainer");
  const cInput = document.getElementById("cInput");

  if (!canvas || !typeSelect || !levelRange || !levelValue) {
    return;
  }

  const ctx = canvas.getContext("2d");
  if (!ctx) {
    return;
  }

  fractals.forEach(function (fractal) {
    const option = document.createElement("option");
    option.value = fractal.key;
    option.textContent = fractal.label;
    typeSelect.appendChild(option);
  });

  function getCurrentFractal() {
    return (
      fractals.find(function (fractal) {
        return fractal.key === typeSelect.value;
      }) || fractals[0]
    );
  }

  function resizeCanvas() {
    const rect = canvas.getBoundingClientRect();
    const dpr = window.devicePixelRatio || 1;
    const targetWidth = Math.max(1, Math.floor(rect.width * dpr));
    const targetHeight = Math.max(1, Math.floor(rect.height * dpr));

    if (canvas.width !== targetWidth || canvas.height !== targetHeight) {
      canvas.width = targetWidth;
      canvas.height = targetHeight;
    }

    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
  }

  function updateControlBound() {
    const fractal = getCurrentFractal();
    const minLevel = Number.isFinite(fractal.minLevel) ? fractal.minLevel : 0;
    const maxLevel = Number.isFinite(fractal.maxLevel) ? fractal.maxLevel : 6;
    const defaultLevel = Number.isFinite(fractal.defaultLevel)
      ? fractal.defaultLevel
      : minLevel;

    levelRange.min = String(minLevel);
    levelRange.max = String(maxLevel);

    levelRange.value = String(defaultLevel);
    levelValue.textContent = String(defaultLevel);

    if (fractalDescription) {
      fractalDescription.textContent = fractal.description || "";
    }

    if (fractal.key === "julia") {
      if (cInputContainer) cInputContainer.style.display = "block";
    } else {
      if (cInputContainer) cInputContainer.style.display = "none";
    }

    if (levelBound) {
      levelBound.textContent =
        "Khoảng n phù hợp: " + minLevel + " - " + maxLevel + ".";
    }
  }

  function drawCurrentFractal() {
    const fractal = getCurrentFractal();
    const level = Number(levelRange.value);
    const width = canvas.clientWidth;
    const height = canvas.clientHeight;

    ctx.clearRect(0, 0, width, height);
    ctx.fillStyle = "#ffffff";
    ctx.fillRect(0, 0, width, height);
    fractal.draw(ctx, width, height, level);
  }

  typeSelect.value = fractals[0].key;
  updateControlBound();
  resizeCanvas();
  drawCurrentFractal();

  typeSelect.addEventListener("change", function () {
    updateControlBound();
    drawCurrentFractal();
  });

  levelRange.addEventListener("input", function () {
    levelValue.textContent = levelRange.value;
    drawCurrentFractal();
  });

  if (cInput) {
    cInput.addEventListener("input", function () {
      drawCurrentFractal();
    });
  }

  window.addEventListener("resize", function () {
    resizeCanvas();
    drawCurrentFractal();
  });
})();
