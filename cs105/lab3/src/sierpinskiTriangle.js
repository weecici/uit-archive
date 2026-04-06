(function () {
  const registry = (window.FractalRegistry = window.FractalRegistry || {});

  function point(x, y) {
    return { x: x, y: y };
  }

  function midpoint(a, b) {
    return point((a.x + b.x) / 2, (a.y + b.y) / 2);
  }

  function fillTriangle(ctx, a, b, c) {
    ctx.beginPath();
    ctx.moveTo(a.x, a.y);
    ctx.lineTo(b.x, b.y);
    ctx.lineTo(c.x, c.y);
    ctx.closePath();
    ctx.fill();
  }

  function drawRecursiveTriangle(ctx, a, b, c, level) {
    if (level === 0) {
      fillTriangle(ctx, a, b, c);
      return;
    }

    const ab = midpoint(a, b);
    const bc = midpoint(b, c);
    const ca = midpoint(c, a);

    drawRecursiveTriangle(ctx, a, ab, ca, level - 1);
    drawRecursiveTriangle(ctx, ab, b, bc, level - 1);
    drawRecursiveTriangle(ctx, ca, bc, c, level - 1);
  }

  function drawSierpinskiTriangle(ctx, width, height, level) {
    const side = Math.min(width, height) * 0.76;
    const h = (Math.sqrt(3) * side) / 2;
    const cx = width / 2;
    const cy = height / 2;

    const a = point(cx - side / 2, cy + h / 3);
    const b = point(cx + side / 2, cy + h / 3);
    const c = point(cx, cy - (2 * h) / 3);

    ctx.save();
    ctx.fillStyle = "#b62b50";
    drawRecursiveTriangle(ctx, a, b, c, level);
    ctx.restore();
  }

  registry.sierpinskiTriangle = {
    label: "Tam giác Sierpinski",
    minLevel: 0,
    maxLevel: 9,
    defaultLevel: 5,
    description:
      "Mỗi tam giác tách thành 3 tam giác con ở ba đỉnh, bỏ phần giữa tại mỗi cấp n.",
    draw: drawSierpinskiTriangle,
  };
})();
