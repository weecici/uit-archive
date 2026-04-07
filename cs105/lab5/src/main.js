(() => {
    const canvas = document.getElementById("sceneCanvas");
    const viewport = document.getElementById("viewport");

    const scene = new THREE.Scene();
    scene.background = new THREE.Color(0x0f1d30);
    scene.fog = new THREE.Fog(0x0f1d30, 20, 44);

    const renderer = new THREE.WebGLRenderer({ canvas, antialias: true });
    renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 2));

    const camera = new THREE.PerspectiveCamera(60, 1, 0.1, 100);

    const transformState = {
        tx: 0,
        ty: 0,
        tz: 0,
        rx: 0,
        ry: 0,
        rz: 0,
        sx: 1,
        sy: 1,
        sz: 1
    };

    const cameraState = {
        vrpX: 5,
        vrpY: 3,
        vrpZ: 5,
        lookX: 0,
        lookY: 0,
        lookZ: 0
    };

    const model = new THREE.Group();
    const bodyMaterial = new THREE.MeshStandardMaterial({
        color: 0x38bdf8,
        roughness: 0.28,
        metalness: 0.22
    });
    const accentMaterial = new THREE.MeshStandardMaterial({
        color: 0xfb923c,
        roughness: 0.38,
        metalness: 0.1
    });

    const body = new THREE.Mesh(new THREE.BoxGeometry(1.8, 1.2, 1.2), bodyMaterial);
    body.position.y = 0.6;
    body.castShadow = true;
    body.receiveShadow = true;

    const topCone = new THREE.Mesh(new THREE.ConeGeometry(0.42, 1, 32), accentMaterial);
    topCone.position.set(0, 1.7, 0);
    topCone.castShadow = true;

    const wingLeft = new THREE.Mesh(new THREE.BoxGeometry(0.28, 0.35, 1.6), accentMaterial);
    wingLeft.position.set(-1.02, 0.65, 0);
    wingLeft.rotation.z = 0.34;
    wingLeft.castShadow = true;

    const wingRight = wingLeft.clone();
    wingRight.position.x = 1.02;
    wingRight.rotation.z = -0.34;

    model.add(body, topCone, wingLeft, wingRight);
    scene.add(model);

    const grid = new THREE.GridHelper(24, 24, 0x2dd4bf, 0x334155);
    grid.position.y = 0;
    scene.add(grid);

    const axes = new THREE.AxesHelper(3);
    scene.add(axes);

    const floor = new THREE.Mesh(
        new THREE.PlaneGeometry(60, 60),
        new THREE.MeshStandardMaterial({
            color: 0x0f172a,
            roughness: 0.92,
            metalness: 0,
            transparent: true,
            opacity: 0.35,
            side: THREE.DoubleSide,
            depthWrite: false
        })
    );
    floor.rotation.x = -Math.PI / 2;
    floor.position.y = 0;
    floor.receiveShadow = true;
    floor.renderOrder = 1;
    scene.add(floor);

    const ambientLight = new THREE.AmbientLight(0xffffff, 0.42);
    scene.add(ambientLight);

    const keyLight = new THREE.DirectionalLight(0xfff7d6, 1.05);
    keyLight.position.set(8, 10, 6);
    keyLight.castShadow = true;
    scene.add(keyLight);

    const fillLight = new THREE.DirectionalLight(0x8be9fd, 0.55);
    fillLight.position.set(-6, 4, -8);
    scene.add(fillLight);

    const inputHandlers = new Map();

    function applyTransform() {
        model.position.set(transformState.tx, transformState.ty, transformState.tz);
        model.rotation.set(
            THREE.MathUtils.degToRad(transformState.rx),
            THREE.MathUtils.degToRad(transformState.ry),
            THREE.MathUtils.degToRad(transformState.rz)
        );
        model.scale.set(transformState.sx, transformState.sy, transformState.sz);
    }

    function applyCamera() {
        camera.position.set(cameraState.vrpX, cameraState.vrpY, cameraState.vrpZ);
        camera.lookAt(cameraState.lookX, cameraState.lookY, cameraState.lookZ);
        camera.updateMatrixWorld();
    }

    function formatByStep(input, value) {
        const step = input.step || "1";
        const decimals = step.includes(".") ? step.split(".")[1].length : 0;
        return value.toFixed(decimals);
    }

    function bindInputs() {
        const sliders = document.querySelectorAll("input[type='range'][data-group][data-key]");

        sliders.forEach((input) => {
            const group = input.dataset.group;
            const key = input.dataset.key;
            const output = document.querySelector(`[data-output-for='${input.id}']`);

            const handler = () => {
                const value = Number(input.value);

                if (group === "transform") {
                    transformState[key] = value;
                    applyTransform();
                } else {
                    cameraState[key] = value;
                    applyCamera();
                }

                if (output) {
                    output.textContent = formatByStep(input, value);
                }
            };

            input.addEventListener("input", handler);
            inputHandlers.set(input.id, handler);
            handler();
        });
    }

    function updateSliderGroup(groupName, values) {
        Object.entries(values).forEach(([key, value]) => {
            const input = document.querySelector(`input[data-group='${groupName}'][data-key='${key}']`);
            if (!input) {
                return;
            }

            input.value = String(value);
            const handler = inputHandlers.get(input.id);
            if (handler) {
                handler();
            }
        });
    }

    function wireButtons() {
        const resetTransform = document.getElementById("resetTransform");
        const resetCamera = document.getElementById("resetCamera");

        resetTransform.addEventListener("click", () => {
            updateSliderGroup("transform", {
                tx: 0,
                ty: 0,
                tz: 0,
                rx: 0,
                ry: 0,
                rz: 0,
                sx: 1,
                sy: 1,
                sz: 1
            });
        });

        resetCamera.addEventListener("click", () => {
            updateSliderGroup("camera", {
                vrpX: 5,
                vrpY: 3,
                vrpZ: 5,
                lookX: 0,
                lookY: 0,
                lookZ: 0
            });
        });
    }

    function onResize() {
        const width = Math.max(1, viewport.clientWidth);
        const height = Math.max(1, viewport.clientHeight);

        renderer.setSize(width, height, false);
        camera.aspect = width / height;
        camera.updateProjectionMatrix();
    }

    function animate() {
        requestAnimationFrame(animate);
        renderer.render(scene, camera);
    }

    bindInputs();
    wireButtons();
    onResize();

    window.addEventListener("resize", onResize);
    animate();
})();
