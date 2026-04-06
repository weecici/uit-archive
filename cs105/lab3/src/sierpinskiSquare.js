(function () {
  const registry = (window.FractalRegistry = window.FractalRegistry || {});

  function drawCarpet(ctx, x, y, size, level) {
    if (level === 0) {
      ctx.fillRect(x, y, size, size);
      return;
    }

    const child = size / 3;
    for (let row = 0; row < 3; row += 1) {
      for (let col = 0; col < 3; col += 1) {
        if (row === 1 && col === 1) {
          continue;
        }
        drawCarpet(ctx, x + col * child, y + row * child, child, level - 1);
      }
    }
  }

  function drawSierpinskiSquare(ctx, width, height, level) {
    const size = Math.min(width, height) * 0.78;
    const x = (width - size) / 2;
    const y = (height - size) / 2;

    ctx.save();
    ctx.fillStyle = "#8c2c13";
    drawCarpet(ctx, x, y, size, level);
    ctx.restore();
  }

  registry.sierpinskiSquare = {
    label: "Hình vuông Sierpinski",
    minLevel: 0,
    maxLevel: 6,
    defaultLevel: 3,
    description:
      "Hình vuông được chia 3x3, bỏ ô giữa và lặp lại cho 8 ô con còn lại.",
    draw: drawSierpinskiSquare,
  };
})();
