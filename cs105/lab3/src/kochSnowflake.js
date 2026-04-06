(function () {
  const registry = (window.FractalRegistry = window.FractalRegistry || {});

  function point(x, y) {
    return { x: x, y: y };
  }

  function appendKochSegment(start, end, level, output) {
    if (level === 0) {
      output.push(start);
      return;
    }

    const dx = (end.x - start.x) / 3;
    const dy = (end.y - start.y) / 3;
    const p1 = point(start.x + dx, start.y + dy);
    const p3 = point(start.x + 2 * dx, start.y + 2 * dy);

    const angle = Math.atan2(dy, dx) + Math.PI / 3;
    const length = Math.hypot(dx, dy);
    const p2 = point(
      p1.x + length * Math.cos(angle),
      p1.y + length * Math.sin(angle),
    );

    appendKochSegment(start, p1, level - 1, output);
    appendKochSegment(p1, p2, level - 1, output);
    appendKochSegment(p2, p3, level - 1, output);
    appendKochSegment(p3, end, level - 1, output);
  }

  function drawKochSnowflake(ctx, width, height, level) {
    const side = Math.min(width, height) * 0.62;
    const h = (Math.sqrt(3) * side) / 2;
    const cx = width / 2;
    const cy = height / 2;

    const a = point(cx - side / 2, cy + h / 3);
    const b = point(cx + side / 2, cy + h / 3);
    const c = point(cx, cy - (2 * h) / 3);

    const points = [];
    appendKochSegment(a, b, level, points);
    appendKochSegment(b, c, level, points);
    appendKochSegment(c, a, level, points);
    points.push(a);

    ctx.save();
    ctx.lineWidth = 1.4;
    ctx.strokeStyle = "#0c5a89";
    ctx.fillStyle = "rgba(30, 129, 176, 0.12)";

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

  registry.kochSnowflake = {
    label: "Bông tuyết Von Koch",
    minLevel: 0,
    maxLevel: 8,
    defaultLevel: 3,
    description:
      "Mỗi cạnh được thay bởi 4 đoạn theo tỉ lệ 1/3, tạo đường biên dạng bông tuyết.",
    draw: drawKochSnowflake,
  };
})();
