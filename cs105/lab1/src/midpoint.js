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

  // Midpoint Circle Algorithm
  this.drawCircle = function (p0, p1, rgba) {
    var xc = p0[0],
      yc = p0[1];
    var r = Math.round(
      Math.sqrt(Math.pow(p1[0] - xc, 2) + Math.pow(p1[1] - yc, 2)),
    );

    var x = r,
      y = 0;
    var P = 1 - r;

    this.drawSymmetricPoints(xc, yc, x, y, rgba);

    while (x > y) {
      y++;
      if (P <= 0) {
        P = P + 2 * y + 1;
      } else {
        x--;
        P = P + 2 * y - 2 * x + 1;
      }
      if (x < y) break;
      this.drawSymmetricPoints(xc, yc, x, y, rgba);
    }
  };

  this.drawSymmetricPoints = function (xc, yc, x, y, rgba) {
    this.setPixel(xc + x, yc + y, rgba);
    this.setPixel(xc - x, yc + y, rgba);
    this.setPixel(xc + x, yc - y, rgba);
    this.setPixel(xc - x, yc - y, rgba);
    if (x !== y) {
      this.setPixel(xc + y, yc + x, rgba);
      this.setPixel(xc - y, yc + x, rgba);
      this.setPixel(xc + y, yc - x, rgba);
      this.setPixel(xc - y, yc - x, rgba);
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

    // Draw complete circles using pairs of points
    for (var i = 0; i < n - 1; i += 2) {
      this.drawCircle(this.points[i], this.points[i + 1], lineRgba);
    }

    // Draw the incomplete circle (while moving mouse)
    if (
      n % 2 !== 0 &&
      (this.points[n - 1][0] != p[0] || this.points[n - 1][1] != p[1])
    ) {
      this.drawCircle(this.points[n - 1], p, vlineRgba);
    }

    this.context.putImageData(this.imageData, 0, 0);
  };

  this.clear();
  this.draw();
}

// In circles, state behavior should be 2-points based per shape
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
    window.state = 1; // Start drawing circle
  } else if (window.state == 1 && painter.points.length % 2 === 0) {
    window.state = 0; // Finished a circle, back to waiting
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
