(function () {
  const registry = (window.FractalRegistry = window.FractalRegistry || {});

  let offsetX = -2.5;
  let offsetY = -1.5;
  let isDragging = false;
  let dragStartX = 0;
  let dragStartY = 0;
  let zoom = 1;
  let setupListeners = false;

  function parseComplex(input) {
    if (!input) return { re: -0.7, im: 0.27015 };
    const match = input.match(/([-+]?\d*\.?\d+)([-+]\d*\.?\d*)i/);
    if (!match) return { re: -0.7, im: 0.27015 };
    return {
      re: parseFloat(match[1]),
      im: parseFloat(match[2]),
    };
  }

  function getColor(iter, maxIter) {
    if (iter === maxIter) return [0, 0, 0];
    const t = iter / maxIter;
    const r = Math.floor(9 * (1 - t) * t * t * t * 255);
    const g = Math.floor(15 * (1 - t) * (1 - t) * t * t * 255);
    const b = Math.floor(8.5 * (1 - t) * (1 - t) * (1 - t) * t * 255);
    return [r, g, b];
  }

  function drawFractal(mode, ctx, width, height, maxIter, isSmoothPass) {
    // Reset offset/zoom if first time or canvas changed
    if (zoom === 1 || (zoom !== width / 3.5 && !isDragging)) {
      if (zoom === 1) {
        // only first load
        zoom = width / 3.5;
        offsetX = -2.5;
        offsetY = -1.5;
      }
    }

    if (!setupListeners) {
      const canvas = ctx.canvas;
      canvas.addEventListener("mousedown", (e) => {
        const typeSelect = document.getElementById("fractalType");
        if (
          typeSelect &&
          (typeSelect.value === "mandelbrot" || typeSelect.value === "julia")
        ) {
          isDragging = true;
          dragStartX = e.clientX;
          dragStartY = e.clientY;
        }
      });

      canvas.addEventListener("mousemove", (e) => {
        if (isDragging) {
          const dx = (e.clientX - dragStartX) / zoom;
          const dy = (e.clientY - dragStartY) / zoom;
          offsetX -= dx;
          offsetY -= dy;
          dragStartX = e.clientX;
          dragStartY = e.clientY;

          // Trigger a low-res fast redraw for smooth dragging
          const typeSelect = document.getElementById("fractalType");
          const mode = typeSelect.value;
          drawFractal(
            mode,
            ctx,
            canvas.clientWidth,
            canvas.clientHeight,
            document.getElementById("levelRange").value,
            true,
          );
        }
      });

      window.addEventListener("mouseup", () => {
        if (isDragging) {
          isDragging = false;
          // Trigger a high-res redraw
          const event = new Event("input");
          document.getElementById("levelRange").dispatchEvent(event);
        }
      });

      canvas.addEventListener("wheel", (e) => {
        const typeSelect = document.getElementById("fractalType");
        if (
          typeSelect &&
          (typeSelect.value === "mandelbrot" || typeSelect.value === "julia")
        ) {
          e.preventDefault();
          const zoomFactor = 1.1;
          const rect = canvas.getBoundingClientRect();
          const mouseX = e.clientX - rect.left;
          const mouseY = e.clientY - rect.top;

          // Compute the complex coordinates under the mouse before zoom
          const x0 = mouseX / zoom + offsetX;
          const y0 = mouseY / zoom + offsetY;

          if (e.deltaY < 0) {
            zoom *= zoomFactor; // Zoom in
          } else {
            zoom /= zoomFactor; // Zoom out
          }

          // Adjust offsetX/Y so the mouse points to the same complex coords
          offsetX = x0 - mouseX / zoom;
          offsetY = y0 - mouseY / zoom;

          // Trigger high-res redraw
          const event = new Event("input");
          document.getElementById("levelRange").dispatchEvent(event);
        }
      });

      setupListeners = true;
    }

    const stepSize = isSmoothPass ? 4 : 1;

    // For smooth dragging, just fill a smaller imageData to save CPU
    const imgW = Math.ceil(width / stepSize);
    const imgH = Math.ceil(height / stepSize);
    const imageData = ctx.createImageData(imgW, imgH);

    let c = { re: -0.7, im: 0.27015 };
    if (mode === "julia") {
      const cInput = document.getElementById("cInput");
      if (cInput) {
        c = parseComplex(cInput.value);
      }
    }

    // Quick trick, reduce maxIter during drag so it remains 60fps fast
    const renderMaxIter = isSmoothPass ? Math.min(maxIter, 50) : maxIter;

    for (let px = 0; px < imgW; px++) {
      for (let py = 0; py < imgH; py++) {
        const cx = px * stepSize;
        const cy = py * stepSize;

        const x0 = cx / zoom + offsetX;
        const y0 = cy / zoom + offsetY;

        let iter = 0;
        let real = x0;
        let imag = y0;

        if (mode === "mandelbrot") {
          real = 0;
          imag = 0;
          for (let i = 0; i < renderMaxIter; i++) {
            let real2 = real * real - imag * imag + x0;
            let imag2 = 2 * real * imag + y0;
            real = real2;
            imag = imag2;
            if (real * real + imag * imag > 4) {
              iter = i;
              break;
            }
            iter = i;
          }
          if (iter === renderMaxIter - 1) iter = renderMaxIter;
        } else {
          for (let i = 0; i < renderMaxIter; i++) {
            let real2 = real * real - imag * imag + c.re;
            let imag2 = 2 * real * imag + c.im;
            real = real2;
            imag = imag2;
            if (real * real + imag * imag > 4) {
              iter = i;
              break;
            }
            iter = i;
          }
          if (iter === renderMaxIter - 1) iter = renderMaxIter;
        }

        const [r, g, b] = getColor(iter, renderMaxIter);
        const index = (py * imgW + px) * 4;
        imageData.data[index] = r;
        imageData.data[index + 1] = g;
        imageData.data[index + 2] = b;
        imageData.data[index + 3] = 255;
      }
    }

    const offCanvas = document.createElement("canvas");
    offCanvas.width = imgW;
    offCanvas.height = imgH;
    offCanvas.getContext("2d").putImageData(imageData, 0, 0);

    if (isSmoothPass) {
      // Draw low res imageData scaled up
      ctx.clearRect(0, 0, width, height);
      ctx.imageSmoothingEnabled = false;
      ctx.drawImage(
        offCanvas,
        0,
        0,
        imgW,
        imgH,
        0,
        0,
        imgW * stepSize,
        imgH * stepSize,
      );
      ctx.imageSmoothingEnabled = true;
    } else {
      // Draw exactly in logical pixel scale to align with main viewport
      ctx.clearRect(0, 0, width, height);
      ctx.drawImage(offCanvas, 0, 0, imgW, imgH, 0, 0, width, height);
    }

    // Coordinate axes
    ctx.strokeStyle = "red";
    ctx.lineWidth = 1;

    const originX = Math.round((0 - offsetX) * zoom);
    const originY = Math.round((0 - offsetY) * zoom);

    if (originX >= 0 && originX <= width) {
      ctx.beginPath();
      ctx.moveTo(originX, 0);
      ctx.lineTo(originX, height);
      ctx.stroke();
    }
    if (originY >= 0 && originY <= height) {
      ctx.beginPath();
      ctx.moveTo(0, originY);
      ctx.lineTo(width, originY);
      ctx.stroke();
    }

    ctx.fillStyle = "white";
    ctx.font = "12px sans-serif";
    ctx.textAlign = "center";
    ctx.textBaseline = "top";

    // Dynamic grid step based on zoom
    // We want the lines to be around 50-100 pixels apart
    let step = 1;
    while (step * zoom > 150) step /= 2;
    while (step * zoom < 50) step *= 2;

    const pixelStep = step * zoom;

    for (let x = originX % pixelStep; x <= width; x += pixelStep) {
      // Small precision formatting based on step
      const re = ((x - originX) / zoom).toFixed(
        Math.max(0, -Math.floor(Math.log10(step))),
      );
      if (originY >= 0 && originY <= height) ctx.fillText(re, x, originY + 2);
    }

    ctx.textAlign = "left";
    ctx.textBaseline = "middle";
    for (let y = originY % pixelStep; y <= height; y += pixelStep) {
      const im = ((originY - y) / zoom).toFixed(
        Math.max(0, -Math.floor(Math.log10(step))),
      );
      if (originX >= 0 && originX <= width) ctx.fillText(im, originX + 4, y);
    }
  }

  registry.mandelbrot = {
    label: "Tập hợp Mandelbrot",
    minLevel: 10,
    maxLevel: 250,
    defaultLevel: 100,
    description:
      "Tập hợp Mandelbrot. Cuộn chuột để zoom, kéo thả để di chuyển. Mức n là số vòng lặp tối đa.",
    draw: function (ctx, w, h, level) {
      drawFractal("mandelbrot", ctx, w, h, level, false);
    },
  };

  registry.julia = {
    label: "Tập hợp Julia",
    minLevel: 10,
    maxLevel: 250,
    defaultLevel: 100,
    description:
      "Tập hợp Julia. Xác định bởi tham số c. Cuộn chuột để zoom, kéo thả để di chuyển.",
    draw: function (ctx, w, h, level) {
      drawFractal("julia", ctx, w, h, level, false);
    },
  };
})();
