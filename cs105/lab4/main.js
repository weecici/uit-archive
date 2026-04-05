(function init() {
    var scene = new THREE.Scene();
    scene.background = new THREE.Color(0xf0f3f6);

    var camera = new THREE.PerspectiveCamera(
        45,
        window.innerWidth / window.innerHeight,
        0.1,
        1000
    );
    camera.position.set(1, 2, 5);
    camera.lookAt(0, 0, 0);

    var renderer = new THREE.WebGLRenderer({ antialias: true });
    renderer.setSize(window.innerWidth, window.innerHeight);
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));

    var webglContainer = document.getElementById("webgl");
    webglContainer.appendChild(renderer.domElement);

    var box = getBox(1, 1, 1);
    box.position.y = box.geometry.parameters.height / 2;

    var groundPlane = getGroundPlane(6);
    groundPlane.rotation.x = -Math.PI / 2;

    scene.add(box);
    scene.add(groundPlane);

    function renderScene() {
        renderer.render(scene, camera);
    }

    window.addEventListener("resize", function () {
        camera.aspect = window.innerWidth / window.innerHeight;
        camera.updateProjectionMatrix();
        renderer.setSize(window.innerWidth, window.innerHeight);
        renderScene();
    });

    renderScene();
})();

function getBox(width, height, depth) {
    var geometry = new THREE.BoxGeometry(width, height, depth);
    var material = new THREE.MeshBasicMaterial({ color: 0x00ff00 });

    return new THREE.Mesh(geometry, material);
}

function getGroundPlane(size) {
    var geometry = new THREE.PlaneGeometry(size, size);
    var material = new THREE.MeshBasicMaterial({
        color: 0xff0000,
        side: THREE.DoubleSide,
    });

    return new THREE.Mesh(geometry, material);
}
