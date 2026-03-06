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
  this.now = [-1, -1];
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

  // Bresenham line algorithm
  this.drawLine = function (p0, p1, rgba) {
    var x0 = p0[0],
      y0 = p0[1];
    var x1 = p1[0],
      y1 = p1[1];

    var dx = Math.abs(x1 - x0);
    var sx = x0 < x1 ? 1 : -1;
    var dy = -Math.abs(y1 - y0); // note: dy is negative
    var sy = y0 < y1 ? 1 : -1;
    var err = dx + dy; // = dx - abs(dy)

    while (true) {
      this.setPixel(x0, y0, rgba);
      if (x0 === x1 && y0 === y1) break;
      var e2 = 2 * err;
      if (e2 >= dy) {
        // e2 >= dy  <=>  e2 >= -abs(dy)
        err += dy; // err = err - abs(dy)
        x0 += sx;
      }
      if (e2 <= dx) {
        err += dx; // err = err + abs(dx)
        y0 += sy;
      }
    }
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

    for (var i = 0; i < n - 1; i++)
      this.drawLine(this.points[i], this.points[i + 1], lineRgba);

    if (
      n > 0 &&
      (this.points[n - 1][0] != p[0] || this.points[n - 1][1] != p[1])
    ) {
      this.drawLine(this.points[n - 1], p, vlineRgba);
    }
    this.context.putImageData(this.imageData, 0, 0);
  };

  this.clear();
  this.draw();
}

window.state = 0; // 0: waiting 1: drawing 2: finished
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
    window.state = 1;
  }
};

window.doKeyDown = function (e) {
  if (window.state == 2) return;
  var keyId = e.keyCode ? e.keyCode : e.which;
  if (keyId == 27 && window.state == 1) {
    // esc
    window.state = 2;
    painter.draw(painter.points[painter.points.length - 1]); // clear red line
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
