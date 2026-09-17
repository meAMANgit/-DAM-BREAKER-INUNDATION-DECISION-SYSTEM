/**
 * SIH26161 - Main Application Controller (Enhanced Cyber-Tactical Edition)
 * Features:
 * - Real-time HTML5 Canvas Hydrodynamic Flow Particle System overlaid on Leaflet
 * - Interactive Time-Scrubber & Multi-Speed Hydrodynamic Wave Engine
 * - Time-Dependent Road Network Graph Status Updates
 * - Settlement Filtering & LSDT Emergency Action Directives
 * - Three.js SPH Visualizer, Chart.js Analytics, & Printable EAP Bulletins
 */

class DamBreakerApp {
  constructor() {
    this.currentScenarioId = 'chamoli_2021';
    this.scenarioData = null;
    this.simTimeMin = 0.0;
    this.isPlaying = false;
    this.playInterval = null;
    this.playbackSpeed = 1.0;
    this.activeFilter = 'all';
    
    // Leaflet map objects
    this.map = null;
    this.riverPolyline = null;
    this.roadLayers = [];
    this.settlementMarkers = [];
    this.shelterMarkers = [];
    this.evacRouteLayers = [];
    this.waveFrontMarker = null;
    this.floodBufferPolygon = null;
    this.showParticles = true;
    this.showRoutes = true;
    
    // Canvas Particles for Hydro Flow
    this.canvas = null;
    this.ctx = null;
    this.particles = [];
    this.particleCount = 180;
    this.animationReq = null;
    
    // Charts
    this.miniHydroChart = null;
    this.couplingChart = null;
    this.uqChart = null;
    this.ritterChart = null;
    
    // 3D SPH
    this.sphVisualizer = null;
  }

  async init() {
    this.initLeafletMap();
    this.initParticleCanvas();
    this.setupEventListeners();
    await this.loadScenario(this.currentScenarioId);
    this.startParticleLoop();
  }

  initLeafletMap() {
    // Dark matter high-contrast basemap
    this.map = L.map('leafletMap', {
      zoomControl: false,
      attributionControl: false
    }).setView([30.485, 79.725], 12);

    L.control.zoom({ position: 'bottomright' }).addTo(this.map);

    L.tileLayer('https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png', {
      maxZoom: 19,
      subdomains: 'abcd'
    }).addTo(this.map);

    this.map.on('move', () => this.resizeParticleCanvas());
    this.map.on('zoom', () => this.resizeParticleCanvas());
  }

  initParticleCanvas() {
    this.canvas = document.getElementById('hydroParticleCanvas');
    if (!this.canvas) return;
    this.ctx = this.canvas.getContext('2d');
    this.resizeParticleCanvas();
    window.addEventListener('resize', () => this.resizeParticleCanvas());
  }

  resizeParticleCanvas() {
    if (!this.canvas) return;
    const container = document.getElementById('tab-map');
    this.canvas.width = container.clientWidth;
    this.canvas.height = container.clientHeight;
  }

  setupEventListeners() {
    // Scenario selector
    document.getElementById('scenarioSelect').addEventListener('change', (e) => {
      this.loadScenario(e.target.value);
    });

    // Navigation Tabs
    document.querySelectorAll('.nav-tab-btn').forEach(btn => {
      btn.addEventListener('click', () => {
        const tabId = btn.getAttribute('data-tab');
        this.switchTab(tabId, btn);
      });
    });

    // Playback buttons
    document.getElementById('btnPlayPause').addEventListener('click', () => this.togglePlay());

    document.getElementById('btnStepBack').addEventListener('click', () => {
      this.setSimTime(Math.max(0, this.simTimeMin - 5));
    });

    document.getElementById('btnStepForward').addEventListener('click', () => {
      this.setSimTime(Math.min(360, this.simTimeMin + 5));
    });

    const slider = document.getElementById('simTimeSlider');
    slider.addEventListener('input', (e) => {
      this.setSimTime(parseFloat(e.target.value));
    });

    // Speed Controls
    document.querySelectorAll('.speed-btn').forEach(btn => {
      btn.addEventListener('click', () => {
        document.querySelectorAll('.speed-btn').forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        this.playbackSpeed = parseFloat(btn.getAttribute('data-speed'));
        if (this.isPlaying) {
          this.pause();
          this.play();
        }
      });
    });
    // Set 1x active by default
    const defSpeedBtn = document.querySelector('.speed-btn[data-speed="1.0"]');
    if (defSpeedBtn) defSpeedBtn.classList.add('active');

    // Settlement Filter Chips
    document.querySelectorAll('.filter-chip[data-filter]').forEach(chip => {
      chip.addEventListener('click', () => {
        document.querySelectorAll('.filter-chip[data-filter]').forEach(c => c.classList.remove('active'));
        chip.classList.add('active');
        this.activeFilter = chip.getAttribute('data-filter');
        this.renderSettlementCards();
      });
    });

    // Interactive Evac Parameters Sliders
    ['speedSlider', 'bufferSlider', 'depthLimitSlider'].forEach(id => {
      document.getElementById(id).addEventListener('input', () => this.handleParamChange());
    });

    // Layer Toggles
    document.getElementById('btnToggleParticles').addEventListener('click', (e) => {
      this.showParticles = !this.showParticles;
      e.target.innerHTML = `<i class="fa-solid fa-water"></i> Hydro Flow Particles: ${this.showParticles ? 'ON' : 'OFF'}`;
      if (!this.showParticles && this.ctx) {
        this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);
      }
    });

    document.getElementById('btnToggleRoutes').addEventListener('click', (e) => {
      this.showRoutes = !this.showRoutes;
      e.target.innerHTML = `<i class="fa-solid fa-route"></i> Escape Routes: ${this.showRoutes ? 'ON' : 'OFF'}`;
      this.evacRouteLayers.forEach(l => {
        if (this.showRoutes) this.map.addLayer(l);
        else this.map.removeLayer(l);
      });
    });

    // Theme Color Palette Switcher
    document.querySelectorAll('.theme-btn').forEach(btn => {
      btn.addEventListener('click', () => {
        document.querySelectorAll('.theme-btn').forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        const theme = btn.getAttribute('data-theme');
        
        document.body.className = '';
        if (theme !== 'theme-emerald') {
          document.body.classList.add(theme);
        }
        
        // Update 3D scene background if initialized
        if (this.sphVisualizer && this.sphVisualizer.scene) {
          const bgColors = {
            'theme-emerald': 0x090e0d,
            'theme-purple': 0x0a0612,
            'theme-amber': 0x0c0a06,
            'theme-obsidian': 0x0b0b0c
          };
          const hex = bgColors[theme] || 0x090e0d;
          this.sphVisualizer.scene.background = new THREE.Color(hex);
          this.sphVisualizer.scene.fog.color = new THREE.Color(hex);
        }
      });
    });

    // EAP Modal
    document.getElementById('btnOpenEAP').addEventListener('click', () => this.openEAPModal());
    document.getElementById('btnCloseEAP').addEventListener('click', () => this.closeEAPModal());
    document.getElementById('btnDismissEAP').addEventListener('click', () => this.closeEAPModal());
  }

  switchTab(tabId, btnElement) {
    document.querySelectorAll('.nav-tab-btn').forEach(b => b.classList.remove('active'));
    btnElement.classList.add('active');

    document.querySelectorAll('.view-tab-content').forEach(view => view.classList.remove('active'));
    document.getElementById('tab-map').style.display = 'none';

    if (tabId === 'tab-map') {
      document.getElementById('tab-map').style.display = 'block';
      setTimeout(() => {
        this.map.invalidateSize();
        this.resizeParticleCanvas();
      }, 100);
    } else {
      const targetView = document.getElementById(tabId);
      if (targetView) targetView.classList.add('active');

      if (tabId === 'tab-sph3d') {
        if (!this.sphVisualizer) {
          this.sphVisualizer = new SPHVisualizer3D('threeCanvasContainer');
          this.sphVisualizer.init();
        } else {
          this.sphVisualizer.onResize();
        }
      } else if (tabId === 'tab-coupling') {
        this.renderCouplingChart();
      } else if (tabId === 'tab-uq') {
        this.renderUQChart();
      } else if (tabId === 'tab-validation') {
        this.loadValidationView();
      }
      this.triggerMathRender();
    }
  }

  async loadScenario(scenarioId) {
    this.currentScenarioId = scenarioId;
    this.pause();
    this.setSimTime(0.0);

    try {
      const res = await fetch(`/api/scenario/${scenarioId}`);
      if (!res.ok) throw new Error("Failed to fetch scenario dataset");
      this.scenarioData = await res.json();
      
      this.initRiverParticles();
      this.renderScenarioIntel();
      this.renderMapEntities();
      this.renderSettlementCards();
      this.renderMiniHydrograph();
    } catch (err) {
      console.error("Error loading scenario:", err);
    }
  }

  initRiverParticles() {
    this.particles = [];
    for (let i = 0; i < this.particleCount; i++) {
      this.particles.push({
        progress: Math.random(), // 0.0 to 1.0 along river
        speed: 0.0015 + Math.random() * 0.003,
        offsetLat: (Math.random() - 0.5) * 0.0015,
        offsetLng: (Math.random() - 0.5) * 0.0015,
        size: 1.5 + Math.random() * 2.2,
        alpha: 0.4 + Math.random() * 0.6
      });
    }
  }

  startParticleLoop() {
    const loop = () => {
      this.drawHydroParticles();
      this.animationReq = requestAnimationFrame(loop);
    };
    loop();
  }

  drawHydroParticles() {
    if (!this.ctx || !this.showParticles || !this.scenarioData) return;
    this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);

    const riverCoords = this.scenarioData.river_channel.path_coordinates;
    if (!riverCoords || riverCoords.length < 2) return;

    // Calculate max allowed progress based on current wave front
    const totalLen = this.scenarioData.river_channel.length_km;
    const waveDist = Math.min(totalLen, (this.simTimeMin * 60.0 * 6.2) / 1000.0);
    const maxProgress = Math.max(0.05, Math.min(1.0, waveDist / totalLen));

    this.ctx.fillStyle = '#06B6D4';
    this.ctx.shadowBlur = 10;
    this.ctx.shadowColor = '#06B6D4';

    for (let i = 0; i < this.particles.length; i++) {
      const p = this.particles[i];
      p.progress += p.speed;
      if (p.progress > maxProgress) {
        p.progress = 0.0;
      }

      // Interpolate position along path coordinates
      const segFraction = p.progress * (riverCoords.length - 1);
      const segIdx = Math.floor(segFraction);
      const subFrac = segFraction - segIdx;
      const pt1 = riverCoords[segIdx];
      const pt2 = riverCoords[Math.min(riverCoords.length - 1, segIdx + 1)];

      const lat = pt1[0] + (pt2[0] - pt1[0]) * subFrac + p.offsetLat;
      const lng = pt1[1] + (pt2[1] - pt1[1]) * subFrac + p.offsetLng;

      const point = this.map.latLngToContainerPoint([lat, lng]);

      this.ctx.beginPath();
      this.ctx.arc(point.x, point.y, p.size, 0, Math.PI * 2);
      this.ctx.globalAlpha = p.alpha * (0.3 + 0.7 * (p.progress / maxProgress));
      this.ctx.fill();
    }

    this.ctx.globalAlpha = 1.0;
    this.ctx.shadowBlur = 0;
  }

  renderScenarioIntel() {
    const meta = this.scenarioData.metadata;
    const res = this.scenarioData.reservoir;
    const hydro = this.scenarioData.breach_hydrograph;
    
    document.getElementById('damTypeBadge').innerText = meta.dam_type;
    document.getElementById('scenarioDesc').innerText = `${meta.subtitle} in ${meta.region}. Initiated: ${meta.event_date}.`;
    
    document.getElementById('metricHead').innerHTML = `${res.dam_height_m} <span class="metric-unit">m</span>`;
    document.getElementById('metricVol').innerHTML = `${res.max_storage_mcm} <span class="metric-unit">MCM</span>`;
    document.getElementById('metricPeakQ').innerHTML = `${hydro.peak_discharge_m3s.toLocaleString()} <span class="metric-unit">m³/s</span>`;
    document.getElementById('metricTf').innerHTML = `${res.breach_formation_time_hrs} <span class="metric-unit">hrs</span>`;
    
    const totalPop = this.scenarioData.settlements.reduce((acc, s) => acc + s.population, 0);
    document.getElementById('topExposedPop').innerText = `${totalPop.toLocaleString()} Citizens`;

    const loc = meta.location;
    this.map.setView([loc.lat, loc.lng], loc.zoom);
  }

  renderMapEntities() {
    if (this.riverPolyline) this.map.removeLayer(this.riverPolyline);
    this.roadLayers.forEach(l => this.map.removeLayer(l));
    this.roadLayers = [];
    this.settlementMarkers.forEach(m => this.map.removeLayer(m));
    this.settlementMarkers = [];
    this.shelterMarkers.forEach(s => this.map.removeLayer(s));
    this.shelterMarkers = [];
    this.evacRouteLayers.forEach(r => this.map.removeLayer(r));
    this.evacRouteLayers = [];
    if (this.waveFrontMarker) this.map.removeLayer(this.waveFrontMarker);

    const s = this.scenarioData;
    const riverCoords = s.river_channel.path_coordinates.map(pt => [pt[0], pt[1]]);

    // 1. Draw River Valley Line
    this.riverPolyline = L.polyline(riverCoords, {
      color: '#0284C7',
      weight: 6,
      opacity: 0.8,
      dashArray: '8, 6'
    }).addTo(this.map);

    this.riverPolyline.bindTooltip(`
      <b style="color:#0284C7; font-size:0.95rem;">${s.river_channel.name}</b><br>
      Length: <b>${s.river_channel.length_km} km</b> | Slope: <b>${s.river_channel.avg_slope}</b><br>
      Manning n: <b>${s.river_channel.manning_n}</b> (Mountain Canyon)
    `, { sticky: true });

    // 2. Draw Dynamic Roads
    s.road_network.forEach(rd => {
      const roadLine = L.polyline(rd.coordinates, {
        color: rd.status_color || '#16A34A',
        weight: 4.5,
        opacity: 0.95
      }).addTo(this.map);
      
      roadLine.bindTooltip(`
        <b style="font-size:0.95rem;">${rd.name}</b><br>
        Status: <span style="color:${rd.status_color}; font-weight:800;">${rd.status}</span><br>
        Length: <b>${rd.length_km} km</b> | Flood Cutoff: <b>T+${rd.flood_arrival_min}m</b>
      `, { sticky: true });
      
      roadLine._roadId = rd.id;
      this.roadLayers.push(roadLine);
    });

    // 3. Shelters
    s.shelters.forEach(sh => {
      const shelterIcon = L.divIcon({
        className: 'shelter-marker-icon',
        html: `<div style="background:#7C3AED; border:2px solid #FFFFFF; width:28px; height:28px; border-radius:50%; display:flex; align-items:center; justify-content:center; color:#FFFFFF; font-size:13px; box-shadow:0 4px 12px rgba(124, 58, 237, 0.4);">
                 <i class="fa-solid fa-person-shelter"></i>
               </div>`,
        iconSize: [28, 28],
        iconAnchor: [14, 14]
      });

      const marker = L.marker([sh.lat, sh.lng], { icon: shelterIcon }).addTo(this.map);
      marker.bindTooltip(`
        <b style="color:#7C3AED; font-size:1rem;">${sh.name}</b><br>
        Type: <b>${sh.type}</b><br>
        Capacity: <b>${sh.capacity.toLocaleString()}</b> persons<br>
        Safe Elevation: <b>${sh.elevation_m} m</b>
      `, { sticky: true });
      this.shelterMarkers.push(marker);
    });

    // 4. Settlements
    s.settlements.forEach(st => {
      const isTrapped = st.routes_to_shelters.every(r => r.robustness_pct < 15);
      const markerColor = isTrapped ? '#DC2626' : '#0284C7';
      
      const settlementIcon = L.divIcon({
        className: 'settlement-marker-icon',
        html: `<div style="background:${markerColor}; border:2px solid #FFFFFF; width:26px; height:26px; border-radius:50%; display:flex; align-items:center; justify-content:center; color:#FFFFFF; font-size:11px; box-shadow:0 4px 12px rgba(0,0,0,0.2);">
                 <i class="fa-solid fa-house-chimney"></i>
               </div>`,
        iconSize: [26, 26],
        iconAnchor: [13, 13]
      });

      const marker = L.marker([st.lat, st.lng], { icon: settlementIcon }).addTo(this.map);
      marker.bindTooltip(`
        <b style="font-size:1rem; color:var(--text-primary);">${st.name}</b><br>
        Population: <b>${st.population.toLocaleString()}</b> citizens<br>
        Flood Arrival: <b>T+${st.nominal_arrival_time_min} min</b><br>
        Peak Depth: <b>${st.nominal_depth_m} m</b> (Vel: ${st.nominal_velocity_ms} m/s)
      `, { sticky: true });
      
      marker.on('click', () => this.highlightSettlement(st.id));
      this.settlementMarkers.push(marker);
    });

    // 5. Evacuation Routes
    s.settlements.forEach(st => {
      st.routes_to_shelters.forEach(rt => {
        const shelter = s.shelters.find(sh => sh.id === rt.shelter_id);
        if (shelter) {
          const routeLine = L.polyline([[st.lat, st.lng], [shelter.lat, shelter.lng]], {
            color: rt.robustness_pct > 50 ? '#16A34A' : '#DC2626',
            weight: 2.5,
            dashArray: '5, 5',
            opacity: 0.75
          }).addTo(this.map);
          this.evacRouteLayers.push(routeLine);
        }
      });
    });

    // 6. Wave Front Marker
    const startPt = riverCoords[0];
    const waveIcon = L.divIcon({
      className: 'wave-front-icon',
      html: `<div style="background:#0284C7; width:22px; height:22px; border-radius:50%; border:2.5px solid #FFFFFF; box-shadow:0 0 16px rgba(2, 132, 199, 0.6); animation:pulseGlow 1.2s infinite;"></div>`,
      iconSize: [22, 22],
      iconAnchor: [11, 11]
    });
    this.waveFrontMarker = L.marker(startPt, { icon: waveIcon }).addTo(this.map);
  }

  renderSettlementCards() {
    const container = document.getElementById('settlementsContainer');
    container.innerHTML = '';

    const decisions = this.scenarioData.evacuation_decisions;
    const uqData = this.scenarioData.multi_fidelity_uq.settlements;

    const filtered = decisions.filter(d => {
      if (this.activeFilter === 'nvr') return d.decision_status === 'NO_VIABLE_ROUTE';
      if (this.activeFilter === 'urgent') return d.urgency === 'HIGH';
      if (this.activeFilter === 'safe') return d.decision_status === 'MONITORING';
      return true;
    });

    if (filtered.length === 0) {
      container.innerHTML = `<div style="text-align:center; padding:20px; font-size:0.8rem; color:var(--text-muted);">No settlements in this filter category.</div>`;
      return;
    }

    filtered.forEach(d => {
      const uq = uqData[d.settlement_id] || {};
      const card = document.createElement('div');
      card.className = `settlement-card status-${d.decision_status === 'NO_VIABLE_ROUTE' ? 'nvr' : (d.urgency === 'HIGH' ? 'urgent' : 'safe')}`;
      card.id = `card_${d.settlement_id}`;

      let badgeHtml = '';
      if (d.decision_status === 'NO_VIABLE_ROUTE') {
        badgeHtml = `<span class="nvr-badge"><i class="fa-solid fa-ban"></i> NO VIABLE ROAD ROUTE</span>`;
      } else if (d.urgency === 'HIGH') {
        badgeHtml = `<span class="badge-tag" style="background:rgba(217,119,6,0.12); border-color:rgba(217,119,6,0.3); color:#B45309;"><i class="fa-solid fa-clock"></i> URGENT ACTION</span>`;
      } else {
        badgeHtml = `<span class="badge-tag" style="background:rgba(22,163,74,0.12); border-color:rgba(22,163,74,0.3); color:#15803D;"><i class="fa-solid fa-shield-check"></i> ROUTE VIABLE</span>`;
      }

      card.innerHTML = `
        <div style="display:flex; justify-content:space-between; align-items:flex-start; margin-bottom:6px;">
          <div>
            <h4 style="font-size:0.95rem; font-family:var(--font-system); font-weight:800; color:var(--text-primary);">${d.settlement_name}</h4>
            <div style="font-size:0.72rem; color:var(--text-secondary); font-family:var(--font-mono);">
              Pop: ${d.population.toLocaleString()} citizens | Dist: ${d.dist_from_dam_km} km
            </div>
          </div>
          ${badgeHtml}
        </div>

        <div style="background:#F8FAFC; border:1px solid var(--border-subtle); border-radius:10px; padding:10px; margin:8px 0; font-size:0.74rem; display:grid; grid-template-columns:1fr 1fr; gap:8px;">
          <div>
            <span style="color:var(--text-muted); text-transform:uppercase; font-size:0.65rem; font-weight:700;">Flood Arrival:</span>
            <div style="font-family:var(--font-mono); font-weight:800; color:var(--accent-cyan-light);">T+${d.flood_arrival_min} min</div>
            <div style="font-size:0.65rem; color:var(--text-muted);">UQ Range: ${uq.arrival_time_p10_min || d.flood_arrival_min - 2} - ${uq.arrival_time_p90_min || d.flood_arrival_min + 4}m</div>
          </div>
          <div>
            <span style="color:var(--text-muted); text-transform:uppercase; font-size:0.65rem; font-weight:700;">Latest Departure (LSDT):</span>
            <div class="lsdt-time-badge" style="color:${d.decision_status === 'NO_VIABLE_ROUTE' ? '#DC2626' : '#16A34A'};">
              ${d.lsdt_display}
            </div>
            <div style="font-size:0.65rem; color:var(--text-muted);">${d.best_route ? d.best_route.shelter_name : 'No Safe Road Route'}</div>
          </div>
        </div>

        <div style="font-size:0.74rem; color:var(--text-secondary); line-height:1.4; margin-top:6px;">
          <i class="fa-solid fa-bullhorn" style="color:var(--accent-cyan); margin-right:4px;"></i>
          ${d.action_directive}
        </div>
      `;

      card.addEventListener('click', () => this.highlightSettlement(d.settlement_id));
      container.appendChild(card);
    });
  }

  highlightSettlement(settlementId) {
    document.querySelectorAll('.settlement-card').forEach(c => c.classList.remove('selected'));
    const targetCard = document.getElementById(`card_${settlementId}`);
    if (targetCard) {
      targetCard.classList.add('selected');
      targetCard.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    }

    const st = this.scenarioData.settlements.find(s => s.id === settlementId);
    if (st) {
      this.map.flyTo([st.lat, st.lng], 13.5, { duration: 0.8 });
    }
  }

  setSimTime(timeMin) {
    this.simTimeMin = timeMin;
    document.getElementById('simTimeSlider').value = timeMin;

    const hrs = Math.floor(timeMin / 60);
    const mins = Math.floor(timeMin % 60);
    const formatted = `T+${String(hrs).padStart(2, '0')}:${String(mins).padStart(2, '0')}`;
    
    document.getElementById('sliderLabelTime').innerText = `${formatted} (${timeMin.toFixed(0)} min)`;
    document.getElementById('clockDisplay').innerText = formatted;
    document.getElementById('topSimTime').innerText = formatted;

    this.updateDynamicSimulationFrame(timeMin);
  }

  async updateDynamicSimulationFrame(timeMin) {
    try {
      const critDepth = parseFloat(document.getElementById('depthLimitSlider').value);
      const res = await fetch(`/api/simulation/frame/${this.currentScenarioId}?time_min=${timeMin}&critical_depth_m=${critDepth}`);
      if (!res.ok) return;
      const frame = await res.json();

      document.getElementById('topWaveFront').innerText = `${frame.wave_front_distance_km} km`;

      // Update Roads
      frame.road_network.forEach(rd => {
        const layer = this.roadLayers.find(l => l._roadId === rd.id);
        if (layer) {
          layer.setStyle({ color: rd.status_color });
          layer.setTooltipContent(`
            <b>${rd.name}</b><br>
            Status: <span style="color:${rd.status_color}; font-weight:700;">${rd.status}</span><br>
            Current Depth: <b>${rd.current_depth_m} m</b> (Vel: ${rd.current_velocity_ms} m/s)<br>
            Hazard (h·v): <b>${rd.current_hv_m2s} m²/s</b>
          `);
        }
      });

      // Update Wave Front Position
      const riverPts = this.scenarioData.river_channel.path_coordinates;
      const totalLen = this.scenarioData.river_channel.length_km;
      const progress = Math.min(1.0, frame.wave_front_distance_km / totalLen);
      const ptIndex = Math.min(riverPts.length - 1, Math.floor(progress * (riverPts.length - 1)));
      const activeCoord = [riverPts[ptIndex][0], riverPts[ptIndex][1]];
      
      if (this.waveFrontMarker) {
        this.waveFrontMarker.setLatLng(activeCoord);
      }

    } catch (err) {
      console.error("Frame update error:", err);
    }
  }

  togglePlay() {
    if (this.isPlaying) {
      this.pause();
    } else {
      this.play();
    }
  }

  play() {
    this.isPlaying = true;
    document.getElementById('btnPlayPause').innerHTML = `<i class="fa-solid fa-pause"></i>`;
    const intervalMs = Math.max(30, 150 / this.playbackSpeed);
    this.playInterval = setInterval(() => {
      let nextTime = this.simTimeMin + 1.0;
      if (nextTime > 360.0) nextTime = 0.0;
      this.setSimTime(nextTime);
    }, intervalMs);
  }

  pause() {
    this.isPlaying = false;
    document.getElementById('btnPlayPause').innerHTML = `<i class="fa-solid fa-play"></i>`;
    if (this.playInterval) clearInterval(this.playInterval);
  }

  async handleParamChange() {
    const speed = parseFloat(document.getElementById('speedSlider').value);
    const buffer = parseFloat(document.getElementById('bufferSlider').value);
    const depth = parseFloat(document.getElementById('depthLimitSlider').value);

    document.getElementById('speedVal').innerText = `${speed} km/h`;
    document.getElementById('bufferVal').innerText = `${buffer} min`;
    document.getElementById('depthLimitVal').innerText = `${depth.toFixed(2)} m`;

    try {
      const res = await fetch('/api/evacuation/recalculate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          scenario_id: this.currentScenarioId,
          evacuation_speed_kmh: speed,
          clearance_buffer_min: buffer,
          critical_depth_m: depth
        })
      });
      if (res.ok) {
        const data = await res.json();
        this.scenarioData.evacuation_decisions = data.evacuation_decisions;
        this.renderSettlementCards();
        this.setSimTime(this.simTimeMin);
      }
    } catch (err) {
      console.error("Param recalc error:", err);
    }
  }

  renderMiniHydrograph() {
    const ctx = document.getElementById('miniHydrographChart').getContext('2d');
    const hydro = this.scenarioData.breach_hydrograph.hydrograph;

    if (this.miniHydroChart) this.miniHydroChart.destroy();

    this.miniHydroChart = new Chart(ctx, {
      type: 'line',
      data: {
        labels: hydro.map(h => `${h.time_min}m`),
        datasets: [{
          label: 'Breach Discharge Q(t) [m³/s]',
          data: hydro.map(h => h.discharge_m3s),
          borderColor: '#0284C7',
          backgroundColor: 'rgba(2, 132, 199, 0.12)',
          fill: true,
          tension: 0.35,
          pointRadius: 0
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: { legend: { display: false } },
        scales: {
          x: { grid: { color: 'rgba(0,0,0,0.06)' }, ticks: { color: '#64748B', maxTicksLimit: 6 } },
          y: { grid: { color: 'rgba(0,0,0,0.06)' }, ticks: { color: '#64748B' } }
        }
      }
    });
  }

  renderCouplingChart() {
    const ctx = document.getElementById('couplingVelocityChart').getContext('2d');
    const ts = this.scenarioData.momentum_coupling.timeseries;

    document.getElementById('massBalanceVal').innerHTML = `${this.scenarioData.momentum_coupling.mass_balance_error_pct}% <span class="metric-unit">Error</span>`;

    if (this.couplingChart) this.couplingChart.destroy();

    this.couplingChart = new Chart(ctx, {
      type: 'line',
      data: {
        labels: ts.map(t => `${t.time_min}m`),
        datasets: [
          {
            label: 'Velocity Magnitude u_mag (m/s)',
            data: ts.map(t => t.u_mag_ms),
            borderColor: '#0284C7',
            borderWidth: 2,
            yAxisID: 'y'
          },
          {
            label: 'Momentum Flux (kN)',
            data: ts.map(t => t.momentum_flux_kn),
            borderColor: '#7C3AED',
            borderDash: [5, 5],
            borderWidth: 2,
            yAxisID: 'y1'
          }
        ]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        scales: {
          x: { grid: { color: 'rgba(0,0,0,0.06)' }, ticks: { color: '#64748B' } },
          y: { position: 'left', grid: { color: 'rgba(0,0,0,0.06)' }, ticks: { color: '#0284C7' } },
          y1: { position: 'right', grid: { display: false }, ticks: { color: '#7C3AED' } }
        }
      }
    });
  }

  renderUQChart() {
    const ctx = document.getElementById('uqDiscrepancyChart').getContext('2d');
    const uq = this.scenarioData.multi_fidelity_uq.settlements;
    const names = Object.values(uq).map(v => v.name);
    const p10 = Object.values(uq).map(v => v.arrival_time_p10_min);
    const p50 = Object.values(uq).map(v => v.arrival_time_p50_min);
    const p90 = Object.values(uq).map(v => v.arrival_time_p90_min);

    if (this.uqChart) this.uqChart.destroy();

    this.uqChart = new Chart(ctx, {
      type: 'bar',
      data: {
        labels: names,
        datasets: [
          {
            label: 'P10 Arrival (Earliest arrival risk)',
            data: p10,
            backgroundColor: 'rgba(220, 38, 38, 0.8)'
          },
          {
            label: 'P50 Arrival (Median calibrated)',
            data: p50,
            backgroundColor: 'rgba(2, 132, 199, 0.8)'
          },
          {
            label: 'P90 Arrival (Late bound)',
            data: p90,
            backgroundColor: 'rgba(22, 163, 74, 0.8)'
          }
        ]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        scales: {
          x: { grid: { color: 'rgba(0,0,0,0.06)' }, ticks: { color: '#475569' } },
          y: { grid: { color: 'rgba(0,0,0,0.06)' }, ticks: { color: '#64748B' }, title: { display: true, text: 'Minutes after Breach', color: '#475569' } }
        }
      }
    });
  }

  async loadValidationView() {
    try {
      const res = await fetch(`/api/validation/${this.currentScenarioId}`);
      if (!res.ok) return;
      const data = await res.json();

      const ritter = data.analytical_ritter;
      const sar = data.sentinel1_sar;

      document.getElementById('valCsi').innerText = sar.metrics.csi_critical_success_index;
      document.getElementById('valF1').innerText = `${sar.metrics.f1_score} / ${sar.metrics.iou_intersection_over_union}`;

      const ctx = document.getElementById('ritterValidationChart').getContext('2d');
      if (this.ritterChart) this.ritterChart.destroy();

      this.ritterChart = new Chart(ctx, {
        type: 'line',
        data: {
          labels: ritter.x_coords_m.map(x => `${x}m`),
          datasets: [
            {
              label: 'Ritter Analytical Exact Solution h(x) [m]',
              data: ritter.h_analytical_m,
              borderColor: '#16A34A',
              borderWidth: 2.5,
              pointRadius: 0
            },
            {
              label: 'DualSPHysics Numerical Solver h_sph [m]',
              data: ritter.h_sph_numerical_m,
              borderColor: '#0284C7',
              borderDash: [4, 4],
              borderWidth: 2.5,
              pointRadius: 0
            }
          ]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          scales: {
            x: { ticks: { color: '#64748B', maxTicksLimit: 8 }, grid: { color: 'rgba(0,0,0,0.06)' } },
            y: { ticks: { color: '#64748B' }, grid: { color: 'rgba(0,0,0,0.06)' }, title: { display: true, text: 'Water Depth (m)', color: '#475569' } }
          }
        }
      });

    } catch (err) {
      console.error("Validation load error:", err);
    }
  }

  async openEAPModal() {
    try {
      const res = await fetch(`/api/eap-report/${this.currentScenarioId}`);
      if (!res.ok) return;
      const data = await res.json();

      document.getElementById('eapBulletinId').innerText = data.bulletin_id;
      document.getElementById('eapTitle').innerText = `NDRF / DDMA Evacuation Action Plan: ${data.scenario_title}`;

      let matrixRows = data.settlements_decision_matrix.map(st => `
        <tr style="border-bottom:1px solid var(--border-subtle); text-align:left;">
          <td style="padding:10px; font-weight:800; color:var(--text-primary);">${st.settlement_name}</td>
          <td style="padding:10px; font-family:var(--font-mono); color:var(--text-secondary);">${st.population.toLocaleString()}</td>
          <td style="padding:10px; font-family:var(--font-mono); color:var(--accent-cyan-light); font-weight:800;">T+${st.flood_arrival_min}m</td>
          <td style="padding:10px; font-family:var(--font-mono); color:${st.decision_status === 'NO_VIABLE_ROUTE' ? '#DC2626' : '#16A34A'}; font-weight:800;">
            ${st.lsdt_display}
          </td>
          <td style="padding:10px; font-size:0.76rem; color:var(--text-secondary);">${st.best_route ? st.best_route.shelter_name : '<span style="color:#DC2626; font-weight:800;">Air Rescue Only</span>'}</td>
          <td style="padding:10px; font-size:0.76rem; color:var(--text-primary);">${st.action_directive}</td>
        </tr>
      `).join('');

      let directivesHtml = data.command_directives.map(d => `<li style="margin-bottom:8px; color:var(--text-primary);">${d}</li>`).join('');

      document.getElementById('eapBody').innerHTML = `
        <div style="background:#FEF2F2; border:1px solid rgba(220,38,38,0.3); border-radius:12px; padding:14px; margin-bottom:18px; display:flex; justify-content:space-between; box-shadow:0 2px 8px rgba(220,38,38,0.06);">
          <div>
            <div style="font-size:0.68rem; font-weight:800; color:#991B1B; text-transform:uppercase;">TOTAL EXPOSED CITIZENS</div>
            <div style="font-size:1.3rem; color:#B45309; font-family:var(--font-mono); font-weight:900; margin-top:2px;">${data.total_exposed_population.toLocaleString()}</div>
          </div>
          <div>
            <div style="font-size:0.68rem; font-weight:800; color:#991B1B; text-transform:uppercase;">CRITICAL ISOLATED (NVR)</div>
            <div style="font-size:1.3rem; color:#DC2626; font-family:var(--font-mono); font-weight:900; margin-top:2px;">${data.critical_nvr_count} Settlements</div>
          </div>
          <div>
            <div style="font-size:0.68rem; font-weight:800; color:#991B1B; text-transform:uppercase;">URGENT EVACUATION</div>
            <div style="font-size:1.3rem; color:#D97706; font-family:var(--font-mono); font-weight:900; margin-top:2px;">${data.urgent_evac_count} Settlements</div>
          </div>
        </div>

        <h3 style="font-size:0.92rem; font-family:var(--font-system); font-weight:800; color:var(--text-primary); margin-bottom:10px; text-transform:uppercase; letter-spacing:0.04em;">1. Settlement Evacuation Operational Matrix</h3>
        <table style="width:100%; border-collapse:collapse; margin-bottom:24px; font-size:0.82rem;">
          <thead>
            <tr style="background:#F1F5F9; color:var(--text-secondary); text-transform:uppercase; font-size:0.72rem; letter-spacing:0.04em; border-bottom:2px solid var(--border-subtle);">
              <th style="padding:10px;">Settlement</th>
              <th style="padding:10px;">Citizens</th>
              <th style="padding:10px;">Flood Arrival</th>
              <th style="padding:10px;">LSDT Deadline</th>
              <th style="padding:10px;">Assigned Safe Zone</th>
              <th style="padding:10px;">Action Directive</th>
            </tr>
          </thead>
          <tbody>
            ${matrixRows}
          </tbody>
        </table>

        <h3 style="font-size:0.92rem; font-family:var(--font-system); font-weight:800; color:var(--text-primary); margin-bottom:10px; text-transform:uppercase; letter-spacing:0.04em;">2. Tactical Field Directives</h3>
        <ul style="padding-left:20px; line-height:1.7;">
          ${directivesHtml}
        </ul>
      `;

      document.getElementById('eapModal').classList.add('active');
      this.triggerMathRender();
    } catch (err) {
      console.error("EAP generation error:", err);
    }
  }

  closeEAPModal() {
    document.getElementById('eapModal').classList.remove('active');
  }

  triggerMathRender() {
    if (window.renderMathInElement) {
      try {
        window.renderMathInElement(document.body, {
          delimiters: [
            { left: '$$', right: '$$', display: true },
            { left: '$', right: '$', display: false }
          ],
          throwOnError: false
        });
      } catch (e) {
        console.debug("KaTeX render notice:", e);
      }
    }
  }
}

window.addEventListener('DOMContentLoaded', () => {
  const app = new DamBreakerApp();
  app.init();
});
