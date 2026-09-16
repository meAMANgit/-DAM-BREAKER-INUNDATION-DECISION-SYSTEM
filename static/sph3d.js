/**
 * SIH26161 - Enhanced 3D SPH Near-Field Fluid Simulation (Three.js WebGL)
 * Visualizes 3D violent breach dynamics, vertical jet plunging, free-surface deformation,
 * and the momentum-aware control plane interface.
 */

class SPHVisualizer3D {
  constructor(containerId) {
    this.container = document.getElementById(containerId);
    this.scene = null;
    this.camera = null;
    this.renderer = null;
    this.controls = null;
    this.particles = null;
    this.particleCount = 16000;
    this.positions = null;
    this.velocities = null;
    this.colors = null;
    this.sizes = null;
    this.isInitialized = false;
    this.animationFrameId = null;
  }

  init() {
    if (this.isInitialized || !this.container) return;

    const width = this.container.clientWidth || 800;
    const height = this.container.clientHeight || 500;

    // 1. Scene
    this.scene = new THREE.Scene();
    this.scene.background = new THREE.Color(0x050811);
    this.scene.fog = new THREE.FogExp2(0x050811, 0.0035);

    // 2. Camera
    this.camera = new THREE.PerspectiveCamera(45, width / height, 0.1, 1000);
    this.camera.position.set(-65, 48, 95);

    // 3. Renderer
    this.renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
    this.renderer.setSize(width, height);
    this.renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    this.renderer.shadowMap.enabled = true;
    this.container.appendChild(this.renderer.domElement);

    // 4. Controls
    this.controls = new THREE.OrbitControls(this.camera, this.renderer.domElement);
    this.controls.enableDamping = true;
    this.controls.dampingFactor = 0.06;
    this.controls.target.set(12, 6, 0);
    this.controls.maxPolarAngle = Math.PI / 2 - 0.05;

    // 5. Lighting
    const ambientLight = new THREE.AmbientLight(0x38bdf8, 0.75);
    this.scene.add(ambientLight);

    const dirLight = new THREE.DirectionalLight(0xffffff, 1.4);
    dirLight.position.set(60, 120, 60);
    this.scene.add(dirLight);

    const blueLight = new THREE.PointLight(0x00f2fe, 3.5, 160);
    blueLight.position.set(0, 25, 0);
    this.scene.add(blueLight);

    const violetLight = new THREE.PointLight(0xa855f7, 2.2, 120);
    violetLight.position.set(25, 15, 0);
    this.scene.add(violetLight);

    // 6. Build Geometry
    this.buildTerrainAndDam();
    this.buildControlPlane();
    this.buildParticleSystem();

    // 7. Event Listeners
    window.addEventListener('resize', () => this.onResize());

    this.isInitialized = true;
    this.animate();
  }

  buildTerrainAndDam() {
    // Mountain Gorge Mesh
    const canyonGeo = new THREE.PlaneGeometry(180, 130, 70, 70);
    canyonGeo.rotateX(-Math.PI / 2);
    const pos = canyonGeo.attributes.position;
    for (let i = 0; i < pos.count; i++) {
      const x = pos.getX(i);
      const z = pos.getZ(i);
      let y = Math.pow(z / 17.0, 2) * 2.4;
      y -= (x + 90) * 0.16;
      y += Math.sin(x * 0.08) * Math.cos(z * 0.12) * 2.2;
      pos.setY(i, y);
    }
    canyonGeo.computeVertexNormals();
    const canyonMat = new THREE.MeshStandardMaterial({
      color: 0x0f172a,
      roughness: 0.85,
      metalness: 0.2
    });
    const canyonMesh = new THREE.Mesh(canyonGeo, canyonMat);
    this.scene.add(canyonMesh);

    // Canyon Grid Overlay
    const wireGeo = new THREE.WireframeGeometry(canyonGeo);
    const wireMat = new THREE.LineBasicMaterial({
      color: 0x1e293b,
      transparent: true,
      opacity: 0.45
    });
    const wireMesh = new THREE.LineSegments(wireGeo, wireMat);
    this.scene.add(wireMesh);

    // Dam Structure
    const damGeo = new THREE.BoxGeometry(12, 28, 70);
    const damMat = new THREE.MeshStandardMaterial({
      color: 0x334155,
      roughness: 0.5,
      metalness: 0.4
    });
    const damMesh = new THREE.Mesh(damGeo, damMat);
    damMesh.position.set(-38, 14, 0);
    this.scene.add(damMesh);

    // Dam Crest Roadway
    const crestGeo = new THREE.BoxGeometry(13, 1.8, 74);
    const crestMat = new THREE.MeshStandardMaterial({ color: 0x475569 });
    const crestMesh = new THREE.Mesh(crestGeo, crestMat);
    crestMesh.position.set(-38, 28, 0);
    this.scene.add(crestMesh);
  }

  buildControlPlane() {
    // Semi-transparent coupling control plane at x = 25 (0.85 km downstream)
    const planeGeo = new THREE.PlaneGeometry(1, 30, 48);
    const planeMat = new THREE.MeshBasicMaterial({
      color: 0xa855f7,
      transparent: true,
      opacity: 0.3,
      side: THREE.DoubleSide
    });
    const planeMesh = new THREE.Mesh(planeGeo, planeMat);
    planeMesh.rotation.y = Math.PI / 2;
    planeMesh.position.set(25, 14, 0);
    this.scene.add(planeMesh);

    const wireGeo = new THREE.WireframeGeometry(planeGeo);
    const wireMat = new THREE.LineBasicMaterial({ color: 0xc084fc });
    const wireLine = new THREE.LineSegments(wireGeo, wireMat);
    wireLine.rotation.y = Math.PI / 2;
    wireLine.position.set(25, 14, 0);
    this.scene.add(wireLine);
  }

  buildParticleSystem() {
    const geo = new THREE.BufferGeometry();
    this.positions = new Float32Array(this.particleCount * 3);
    this.velocities = new Float32Array(this.particleCount * 3);
    this.colors = new Float32Array(this.particleCount * 3);

    for (let i = 0; i < this.particleCount; i++) {
      this.resetParticle(i, true);
    }

    geo.setAttribute('position', new THREE.BufferAttribute(this.positions, 3));
    geo.setAttribute('color', new THREE.BufferAttribute(this.colors, 3));

    const particleMat = new THREE.PointsMaterial({
      size: 1.4,
      vertexColors: true,
      transparent: true,
      opacity: 0.95,
      blending: THREE.AdditiveBlending
    });

    this.particles = new THREE.Points(geo, particleMat);
    this.scene.add(this.particles);
  }

  resetParticle(i, initialSpread = false) {
    const idx = i * 3;
    
    if (initialSpread) {
      this.positions[idx] = -55 + Math.random() * 125;
      this.positions[idx + 1] = 6 + Math.random() * 22;
      this.positions[idx + 2] = (Math.random() - 0.5) * 24;
    } else {
      this.positions[idx] = -38 + (Math.random() - 0.5) * 4;
      this.positions[idx + 1] = 20 + (Math.random() - 0.5) * 6;
      this.positions[idx + 2] = (Math.random() - 0.5) * 11;
    }

    this.velocities[idx] = 1.3 + Math.random() * 1.6;
    this.velocities[idx + 1] = -0.45 + (Math.random() - 0.5) * 0.35;
    this.velocities[idx + 2] = (Math.random() - 0.5) * 0.45;

    this.updateParticleColor(i, this.velocities[idx]);
  }

  updateParticleColor(i, speed) {
    const idx = i * 3;
    if (speed > 2.2) {
      // White Foam Kinetic Jet
      this.colors[idx] = 0.98;
      this.colors[idx + 1] = 1.0;
      this.colors[idx + 2] = 1.0;
    } else if (speed > 1.3) {
      // Electric Neon Cyan Turbulent Stream
      this.colors[idx] = 0.0;
      this.colors[idx + 1] = 0.95;
      this.colors[idx + 2] = 1.0;
    } else {
      // Deep Aqua Blue
      this.colors[idx] = 0.01;
      this.colors[idx + 1] = 0.45;
      this.colors[idx + 2] = 0.85;
    }
  }

  animate() {
    this.animationFrameId = requestAnimationFrame(() => this.animate());

    if (this.controls) this.controls.update();

    if (this.particles) {
      const posAttr = this.particles.geometry.attributes.position;
      const colorAttr = this.particles.geometry.attributes.color;

      for (let i = 0; i < this.particleCount; i++) {
        const idx = i * 3;
        
        this.velocities[idx + 1] -= 0.016; // Gravity
        
        const z = this.positions[idx + 2];
        const canyonWidth = 15 + (this.positions[idx] + 45) * 0.13;
        if (Math.abs(z) > canyonWidth) {
          this.velocities[idx + 2] *= -0.75;
        }

        const x = this.positions[idx];
        const bedHeight = Math.pow(z / 17.0, 2) * 2.2 - (x + 90) * 0.16;
        if (this.positions[idx + 1] <= bedHeight + 0.5) {
          this.positions[idx + 1] = bedHeight + 0.5;
          this.velocities[idx + 1] = Math.abs(this.velocities[idx + 1]) * 0.32 + 0.06;
          this.velocities[idx] *= 0.985;
        }

        this.positions[idx] += this.velocities[idx];
        this.positions[idx + 1] += this.velocities[idx + 1];
        this.positions[idx + 2] += this.velocities[idx + 2];

        if (this.positions[idx] > 70 || this.positions[idx + 1] < -25) {
          this.resetParticle(i, false);
        }

        const currentSpeed = Math.sqrt(
          this.velocities[idx] ** 2 + this.velocities[idx + 1] ** 2 + this.velocities[idx + 2] ** 2
        );
        this.updateParticleColor(i, currentSpeed);
      }

      posAttr.needsUpdate = true;
      colorAttr.needsUpdate = true;
    }

    if (this.renderer && this.scene && this.camera) {
      this.renderer.render(this.scene, this.camera);
    }
  }

  onResize() {
    if (!this.container || !this.renderer || !this.camera) return;
    const width = this.container.clientWidth;
    const height = this.container.clientHeight;
    this.camera.aspect = width / height;
    this.camera.updateProjectionMatrix();
    this.renderer.setSize(width, height);
  }
}

window.SPHVisualizer3D = SPHVisualizer3D;
