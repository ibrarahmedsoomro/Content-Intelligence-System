// Interactive 3D Animated Background with Three.js
class AgentThreeScene {
  constructor() {
    this.container = document.getElementById('webgl-bg');
    if (!this.container) return;

    this.scene = new THREE.Scene();
    this.camera = new THREE.PerspectiveCamera(60, window.innerWidth / window.innerHeight, 0.1, 1000);
    this.renderer = new THREE.WebGLRenderer({ alpha: true, antialias: true });

    this.renderer.setSize(window.innerWidth, window.innerHeight);
    this.renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    this.container.appendChild(this.renderer.domElement);

    this.camera.position.z = 45;

    this.mouseX = 0;
    this.mouseY = 0;
    this.targetX = 0;
    this.targetY = 0;

    this.initObjects();
    this.addEventListeners();
    this.animate();
  }

  initObjects() {
    // 1. Particle Constellation Network
    const particleCount = 200;
    const geometry = new THREE.BufferGeometry();
    const positions = new Float32Array(particleCount * 3);
    const colors = new Float32Array(particleCount * 3);

    const color1 = new THREE.Color(0x06b6d4); // Cyan
    const color2 = new THREE.Color(0x8b5cf6); // Purple

    for (let i = 0; i < particleCount * 3; i += 3) {
      positions[i] = (Math.random() - 0.5) * 120;
      positions[i + 1] = (Math.random() - 0.5) * 80;
      positions[i + 2] = (Math.random() - 0.5) * 60;

      const mixed = color1.clone().lerp(color2, Math.random());
      colors[i] = mixed.r;
      colors[i + 1] = mixed.g;
      colors[i + 2] = mixed.b;
    }

    geometry.setAttribute('position', new THREE.BufferAttribute(positions, 3));
    geometry.setAttribute('color', new THREE.BufferAttribute(colors, 3));

    const pMaterial = new THREE.PointsMaterial({
      size: 1.5,
      vertexColors: true,
      transparent: true,
      opacity: 0.7,
      blending: THREE.AdditiveBlending
    });

    this.particleSystem = new THREE.Points(geometry, pMaterial);
    this.scene.add(this.particleSystem);

    // 2. Central 3D Decision Core Hologram (Wireframe Icosahedron & Rings)
    const coreGeo = new THREE.IcosahedronGeometry(9, 1);
    const coreMat = new THREE.MeshBasicMaterial({
      color: 0x06b6d4,
      wireframe: true,
      transparent: true,
      opacity: 0.35
    });
    this.decisionCore = new THREE.Mesh(coreGeo, coreMat);
    this.decisionCore.position.set(32, -4, -10);
    this.scene.add(this.decisionCore);

    // Inner Glowing Core
    const innerGeo = new THREE.OctahedronGeometry(4, 0);
    const innerMat = new THREE.MeshBasicMaterial({
      color: 0x8b5cf6,
      wireframe: true,
      transparent: true,
      opacity: 0.6
    });
    this.innerCore = new THREE.Mesh(innerGeo, innerMat);
    this.innerCore.position.copy(this.decisionCore.position);
    this.scene.add(this.innerCore);

    // Orbit Ring 1
    const ringGeo = new THREE.RingGeometry(12, 12.3, 64);
    const ringMat = new THREE.MeshBasicMaterial({
      color: 0x38bdf8,
      side: THREE.DoubleSide,
      transparent: true,
      opacity: 0.25
    });
    this.orbitRing1 = new THREE.Mesh(ringGeo, ringMat);
    this.orbitRing1.position.copy(this.decisionCore.position);
    this.orbitRing1.rotation.x = Math.PI / 3;
    this.scene.add(this.orbitRing1);

    // Orbit Ring 2
    const ringGeo2 = new THREE.RingGeometry(14, 14.2, 64);
    const ringMat2 = new THREE.MeshBasicMaterial({
      color: 0xa855f7,
      side: THREE.DoubleSide,
      transparent: true,
      opacity: 0.2
    });
    this.orbitRing2 = new THREE.Mesh(ringGeo2, ringMat2);
    this.orbitRing2.position.copy(this.decisionCore.position);
    this.orbitRing2.rotation.y = Math.PI / 4;
    this.scene.add(this.orbitRing2);
  }

  setDecisionTheme(decisionType) {
    let targetColor = 0x06b6d4; // Default Cyan
    if (decisionType === 'MAKE_NOW') targetColor = 0x10b981; // Emerald
    else if (decisionType === 'MAKE') targetColor = 0x06b6d4; // Cyan
    else if (decisionType === 'REFRAME' || decisionType === 'TEST_SHORT') targetColor = 0xf59e0b; // Amber
    else if (decisionType === 'SKIP' || decisionType === 'NEED_MORE_RESEARCH') targetColor = 0xf43f5e; // Rose

    if (this.decisionCore) {
      this.decisionCore.material.color.setHex(targetColor);
    }
  }

  addEventListeners() {
    window.addEventListener('resize', () => {
      this.camera.aspect = window.innerWidth / window.innerHeight;
      this.camera.updateProjectionMatrix();
      this.renderer.setSize(window.innerWidth, window.innerHeight);
    });

    window.addEventListener('mousemove', (e) => {
      this.mouseX = (e.clientX - window.innerWidth / 2) * 0.015;
      this.mouseY = (e.clientY - window.innerHeight / 2) * 0.015;
    });
  }

  animate() {
    requestAnimationFrame(() => this.animate());

    // Mouse parallax
    this.targetX += (this.mouseX - this.targetX) * 0.05;
    this.targetY += (this.mouseY - this.targetY) * 0.05;

    this.camera.position.x = this.targetX * 2;
    this.camera.position.y = -this.targetY * 2;
    this.camera.lookAt(0, 0, 0);

    // Rotate 3D Decision Core
    if (this.decisionCore) {
      this.decisionCore.rotation.x += 0.003;
      this.decisionCore.rotation.y += 0.005;
    }
    if (this.innerCore) {
      this.innerCore.rotation.x -= 0.006;
      this.innerCore.rotation.y += 0.008;
    }
    if (this.orbitRing1) {
      this.orbitRing1.rotation.z += 0.004;
    }
    if (this.orbitRing2) {
      this.orbitRing2.rotation.z -= 0.003;
    }

    // Gentle particle drift
    if (this.particleSystem) {
      this.particleSystem.rotation.y += 0.0008;
    }

    this.renderer.render(this.scene, this.camera);
  }
}

window.addEventListener('DOMContentLoaded', () => {
  window.threeScene = new AgentThreeScene();
});
