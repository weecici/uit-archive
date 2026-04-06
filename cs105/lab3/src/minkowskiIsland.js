(function () {
  const registry = (window.FractalRegistry = window.FractalRegistry || {});

  function point(x, y) {
    return { x: x, y: y };
  }

  function appendMinkowskiSegment(start, end, level, output) {
    if (level === 0) {
      output.push(start);
      return;
    }

    const ux = (end.x - start.x) / 4;
    const uy = (end.y - start.y) / 4;
    const vx = -uy;
    const vy = ux;

    // Mot canh duoc thay bang 8 canh theo mau Minkowski de tao bien dao.
    const p1 = point(start.x + ux, start.y + uy);
    const p2 = point(p1.x + vx, p1.y + vy);
    const p3 = point(p2.x + ux, p2.y + uy);
    const p4 = point(p3.x - vx, p3.y - vy);
    const p5 = point(p4.x - vx, p4.y - vy);
    const p6 = point(p5.x + ux, p5.y + uy);
    const p7 = point(p6.x + vx, p6.y + vy);
    const p8 = end;

    const chain = [start, p1, p2, p3, p4, p5, p6, p7, p8];
    for (let i = 0; i < chain.length - 1; i += 1) {
      appendMinkowskiSegment(chain[i], chain[i + 1], level - 1, output);
    }
  }

  function drawMinkowskiIsland(ctx, width, height, level) {
    const side = Math.min(width, height) * 0.58;
    const cx = width / 2;
    const cy = height / 2;

    const p1 = point(cx - side / 2, cy - side / 2);
    const p2 = point(cx + side / 2, cy - side / 2);
    const p3 = point(cx + side / 2, cy + side / 2);
    const p4 = point(cx - side / 2, cy + side / 2);

    const points = [];
    appendMinkowskiSegment(p1, p2, level, points);
    appendMinkowskiSegment(p2, p3, level, points);
    appendMinkowskiSegment(p3, p4, level, points);
    appendMinkowskiSegment(p4, p1, level, points);
    points.push(p1);

    ctx.save();
    ctx.lineWidth = 1.25;
    ctx.strokeStyle = "#1e6b2e";
    ctx.fillStyle = "rgba(80, 162, 97, 0.13)";

    ctx.beginPath();
    ctx.moveTo(points[0].x, points[0].y);
    for (let i = 1; i < points.length; i += 1) {
      ctx.lineTo(points[i].x, points[i].y);
    }
    ctx.closePath();
    ctx.fill();
    ctx.stroke();
    ctx.restore();
  }

  registry.minkowskiIsland = {
    label: "Đảo Minkowski",
    minLevel: 0,
    maxLevel: 5,
    defaultLevel: 2,
    description:
      "Bắt đầu từ hình vuông, mỗi cạnh thay bởi 8 đoạn theo mẫu gấp khúc để tạo đường biên đảo.",
    draw: drawMinkowskiIsland,
  };
})();
