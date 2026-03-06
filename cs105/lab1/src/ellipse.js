// Initialize
if (window.cleanUp) window.cleanUp();

var canvas = document.getElementById("canvas");
var context = canvas.getContext("2d");

var width = 800;
var height = 600;

var bgRgba = [241, 245, 249, 255]; // slate 100
var pointRgba = [14, 165, 233, 255]; // sky 500
var lineRgba = [15, 23, 42, 255]; // slate 900
var vlineRgba = [239, 68, 68, 255]; // red 500

canvas.setAttribute("width", width);
canvas.setAttribute("height", height);

function Painter(context, width, height) {
  this.context = context;
  this.imageData = context.createImageData(width, height);
  this.points = [];
  this.width = width;
  this.height = height;

  this.getPixelIndex = function (x, y) {
    if (x < 0 || y < 0 || x >= this.width || y >= this.height) return -1;
    return (x + y * width) << 2;
  };

  this.setPixel = function (x, y, rgba) {
    var pixelIndex = this.getPixelIndex(x, y);
    if (pixelIndex == -1) return;
    for (var i = 0; i < 4; i++) {
      this.imageData.data[pixelIndex + i] = rgba[i];
    }
  };

  this.drawPoint = function (p, rgba) {
    var x = p[0];
    var y = p[1];
    for (var i = -2; i <= 2; i++)
      for (var j = -2; j <= 2; j++) this.setPixel(x + i, y + j, rgba);
  };

  // Midpoint Ellipse Algorithm
  this.drawEllipse = function (p0, p1, rgba) {
    var xc = p0[0],
      yc = p0[1];
    // Ensure strictly positive axes to avoid div/zero or infinite loops
    var rx = Math.max(1, Math.abs(p1[0] - xc));
    var ry = Math.max(1, Math.abs(p1[1] - yc));

    var rxSq = rx * rx;
    var rySq = ry * ry;
    var x = 0,
      y = ry;
    var px = 0,
      py = 2 * rxSq * y;
    var p;

    this.drawSymmetricPoints(xc, yc, x, y, rgba);

    // Region 1
    p = Math.round(rySq - rxSq * ry + 0.25 * rxSq);
    while (px < py) {
      x++;
      px = px + 2 * rySq;
      if (p < 0) {
        p = p + rySq + px;
      } else {
        y--;
        py = py - 2 * rxSq;
        p = p + rySq + px - py;
      }
      this.drawSymmetricPoints(xc, yc, x, y, rgba);
    }

    // Region 2
    p = Math.round(
      rySq * (x + 0.5) * (x + 0.5) + rxSq * (y - 1) * (y - 1) - rxSq * rySq,
    );
    while (y > 0) {
      y--;
      py = py - 2 * rxSq;
      if (p > 0) {
        p = p + rxSq - py;
      } else {
        x++;
        px = px + 2 * rySq;
        p = p + rxSq - py + px;
      }
      this.drawSymmetricPoints(xc, yc, x, y, rgba);
    }
  };

  this.drawSymmetricPoints = function (cx, cy, x, y, rgba) {
    this.setPixel(cx + x, cy + y, rgba);
    this.setPixel(cx - x, cy + y, rgba);
    this.setPixel(cx + x, cy - y, rgba);
    this.setPixel(cx - x, cy - y, rgba);
  };

  this.drawBkg = function (rgba) {
    for (var i = 0; i < this.width; i++)
      for (var j = 0; j < this.height; j++) this.setPixel(i, j, rgba);
  };

  this.clear = function () {
    this.points.length = 0;
    this.drawBkg(bgRgba);
    this.context.putImageData(this.imageData, 0, 0);
  };

  this.addPoint = function (p) {
    this.points.push(p);
  };

  this.draw = function (p) {
    var n = this.points.length;
    this.drawBkg(bgRgba);

    for (var i = 0; i < n; i++) this.drawPoint(this.points[i], pointRgba);

    // Draw complete ellipses using pairs of points
    for (var i = 0; i < n - 1; i += 2) {
      this.drawEllipse(this.points[i], this.points[i + 1], lineRgba);
    }

    // Draw the incomplete ellipse (while moving mouse)
    if (
      n % 2 !== 0 &&
      (this.points[n - 1][0] != p[0] || this.points[n - 1][1] != p[1])
    ) {
      this.drawEllipse(this.points[n - 1], p, vlineRgba);
    }

    this.context.putImageData(this.imageData, 0, 0);
  };

  this.clear();
  this.draw();
}

// In ellipses, state behavior should be 2-points based per shape
window.state = 0;
var clickPos = [-1, -1];
var painter = new Painter(context, width, height);

window.getPosOnCanvas = function (x, y) {
  var bbox = canvas.getBoundingClientRect();
  return [
    Math.floor(x - bbox.left * (canvas.width / bbox.width) + 0.5),
    Math.floor(y - bbox.top * (canvas.height / bbox.height) + 0.5),
  ];
};

window.doMouseMove = function (e) {
  if (window.state == 0 || window.state == 2) return;
  var p = window.getPosOnCanvas(e.clientX, e.clientY);
  painter.draw(p);
};

window.doMouseDown = function (e) {
  if (window.state == 2 || e.button != 0) return;
  var p = window.getPosOnCanvas(e.clientX, e.clientY);
  painter.addPoint(p);
  painter.draw(p);
  if (window.state == 0) {
    window.state = 1; // Start drawing ellipse
  } else if (window.state == 1 && painter.points.length % 2 === 0) {
    window.state = 0; // Finished an ellipse, back to waiting
  }
};

window.doKeyDown = function (e) {
  var keyId = e.keyCode ? e.keyCode : e.which;
  if (keyId == 27) {
    // esc
    window.state = 2; // Finished completely
    if (painter.points.length % 2 !== 0) {
      painter.points.pop(); // Remove the unpaired center point
      painter.draw(window.getPosOnCanvas(-1000, -1000));
    }
  }
};

window.doReset = function () {
  window.state = 0;
  painter.clear();
};

canvas.addEventListener("mousedown", window.doMouseDown, false);
canvas.addEventListener("mousemove", window.doMouseMove, false);
window.addEventListener("keydown", window.doKeyDown, false);

var resetButton = document.getElementById("reset");
resetButton.addEventListener("click", window.doReset, false);

window.cleanUp = function () {
  canvas.removeEventListener("mousedown", window.doMouseDown, false);
  canvas.removeEventListener("mousemove", window.doMouseMove, false);
  window.removeEventListener("keydown", window.doKeyDown, false);
  resetButton.removeEventListener("click", window.doReset, false);
};
