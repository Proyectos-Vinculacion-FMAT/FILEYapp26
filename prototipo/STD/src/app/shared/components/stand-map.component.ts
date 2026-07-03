import { Component, OnDestroy, OnInit, ViewChild, ElementRef, input, output, effect, inject, signal, computed } from '@angular/core';
import { CommonModule } from '@angular/common';
import { DomSanitizer, SafeResourceUrl } from '@angular/platform-browser';
import { GodotBridgeService, GodotMapData, GodotMode, GodotStand } from '../../services/godot-bridge.service';
import { StandService } from '../../services/stand.service';
import { ParametrosService } from '../../services/parametros.service';

@Component({
  selector: 'app-stand-map',
  standalone: true,
  imports: [CommonModule],
  template: `
    <div class="map-container">
      <iframe
        #iframe
        [src]="iframeUrl()"
        (load)="onIframeLoaded()"
        style="width:100%; height:100%; border:0; display:block;"
        title="Mapa de Stands"
        allow="autoplay"
      ></iframe>
      <div *ngIf="!ready()" class="splash">
        <div class="splash-cover">
          <span class="cover-logo"><span>FIL</span><span>EY</span></span>
          <div class="cover-text">
            <strong>FILEY 2027</strong>
            <small>Mapa del showfloor</small>
          </div>
          <div class="cover-dots" aria-hidden="true">
            <span></span><span></span><span></span>
          </div>
          <p class="cover-caption">Cargando mapa del showfloor…</p>
        </div>
      </div>
    </div>
  `,
  styles: [`
    .map-container {
      position: relative;
      width: 100%;
      height: 100%;
      min-height: 400px;
      background: #1a1a1a;
    }
    .splash {
      position: absolute;
      inset: 0;
      display: flex;
      align-items: center;
      justify-content: center;
      /* Fully opaque branded cover that hides the Godot boot logo underneath */
      background:
        linear-gradient(160deg, #003b7a 0%, #00254d 70%),
        radial-gradient(circle at 80% 12%, rgba(201,162,39,.30), transparent 45%);
      z-index: 10;
    }
    .splash-cover {
      display: flex;
      flex-direction: column;
      align-items: center;
      text-align: center;
      color: #fff;
    }
    .cover-logo {
      width: 72px;
      height: 72px;
      border-radius: 16px;
      background: #fff;
      display: grid;
      place-items: center;
      line-height: 1;
      font-weight: 800;
      font-size: 22px;
      letter-spacing: .5px;
      color: var(--filey-primary-dark);
      box-shadow: var(--filey-shadow-md);
      margin-bottom: 20px;
    }
    .cover-logo span:last-child { color: var(--filey-secondary); }
    .cover-text strong {
      display: block;
      font-size: 22px;
      letter-spacing: .3px;
      color: #fff;
    }
    .cover-text small {
      display: block;
      margin-top: 4px;
      font-size: 12px;
      color: #f1e3b0;
      text-transform: uppercase;
      letter-spacing: 2px;
    }
    .cover-dots {
      display: flex;
      gap: 8px;
      margin: 26px 0 10px;
    }
    .cover-dots span {
      width: 9px;
      height: 9px;
      border-radius: 50%;
      background: var(--filey-secondary);
      animation: cover-pulse 1.2s ease-in-out infinite;
    }
    .cover-dots span:nth-child(2) { animation-delay: .2s; }
    .cover-dots span:nth-child(3) { animation-delay: .4s; }
    .cover-caption {
      margin: 0;
      font-size: 13px;
      color: #cfe0f3;
    }
    @keyframes cover-pulse {
      0%, 100% { opacity: .3; transform: translateY(0); }
      50% { opacity: 1; transform: translateY(-4px); }
    }
  `]
})
export class StandMapComponent implements OnInit, OnDestroy {
  private readonly sanitizer = inject(DomSanitizer);
  private readonly standService = inject(StandService);
  private readonly parametrosService = inject(ParametrosService);
  readonly bridge = inject(GodotBridgeService);

  mode = input<GodotMode>('viewer');
  ocultarNoDisponibles = input<boolean>(false);
  customMapData = input<GodotMapData | null>(null);

  standAddedToCart = output<{ standId: string }>();
  mapSaved = output<GodotMapData>();

  @ViewChild('iframe', { static: true }) iframeRef!: ElementRef<HTMLIFrameElement>;

  readonly ready = signal(false);
  private dataPushed = false;
  private fallbackTimeoutId: any;
  private readySub: any;
  private addToCartSub: any;
  private saveMapSub: any;

  readonly iframeUrl = computed<SafeResourceUrl>(() => {
    const origin = encodeURIComponent(window.location.origin);
    const base = document.baseURI.replace(/\/$/, '');
    return this.sanitizer.bypassSecurityTrustResourceUrl(
      `${base}/assets/godot/index.html?mode=${this.mode()}&hostOrigin=${origin}`
    );
  });

  constructor() {
    effect(() => {
      const data = this.customMapData();
      if (data && this.ready()) {
        this.bridge.pushMapData(data);
      }
    });
  }

  ngOnInit(): void {
    this.bridge.registerIframe(this.iframeRef.nativeElement, this.mode());

    this.readySub = this.bridge.ready$.subscribe(() => {
      this.markReady();
    });

    this.addToCartSub = this.bridge.addToCart$.subscribe(ev => this.standAddedToCart.emit(ev));
    this.saveMapSub = this.bridge.saveMap$.subscribe(data => this.mapSaved.emit(data));

    this.fallbackTimeoutId = setTimeout(() => {
      if (!this.ready()) {
        this.markReady();
      }
    }, 4000);
  }

  ngOnDestroy(): void {
    this.bridge.unregisterIframe();
    if (this.fallbackTimeoutId) clearTimeout(this.fallbackTimeoutId);
    this.readySub?.unsubscribe();
    this.addToCartSub?.unsubscribe();
    this.saveMapSub?.unsubscribe();
  }

  onIframeLoaded(): void {
    if (!this.ready()) {
      setTimeout(() => this.markReady(), 500);
    }
  }

  private markReady(): void {
    if (this.ready()) return;
    this.ready.set(true);
    if (this.fallbackTimeoutId) {
      clearTimeout(this.fallbackTimeoutId);
      this.fallbackTimeoutId = null;
    }
    if (!this.dataPushed) {
      this.dataPushed = true;
      this.pushCurrentData();
    }
  }

  private pushCurrentData(): void {
    if (this.customMapData()) {
      this.bridge.pushMapData(this.customMapData()!);
      return;
    }
    const data = this.buildMapData();
    this.bridge.pushMapData(data);
  }

  private buildMapData(): GodotMapData {
    const stands = this.standService.stands.map(s => {
      const status = this.ocultarNoDisponibles()
        ? (s.estado === 'Disponible' ? 'available' : 'unavailable')
        : s.estado === 'Disponible' ? 'available'
        : s.estado === 'Reservado' ? 'reserved'
        : 'unavailable';

      return {
        id: s.id,
        col: s.posX,
        row: s.posY,
        w: s.ancho,
        h: s.largo,
        label: s.clave,
        status: status as GodotStand['status'],
        price: this.standService.precioStand(s, this.parametrosService.parametros.costoM2),
        dimensions_text: `${s.ancho}m x ${s.largo}m (${s.metrosCuadrados} m²)`,
        zone: s.zona
      };
    });

    return {
      grid: {
        cell_size: 32,
        cols: 40,
        rows: 30,
        meters_per_cell: 3
      },
      stands,
      decorations: [
        { type: 'text', col: 2, row: 0, text: 'Pabellón Internacional' },
        { type: 'text', col: 2, row: 3, text: 'Pabellón Nacional' },
        { type: 'text', col: 2, row: 6, text: 'Pabellón Académico' },
        { type: 'text', col: 2, row: 9, text: 'Pabellón Independiente' },
        { type: 'text', col: 2, row: 12, text: 'Pabellón Premium' },
        { type: 'text', col: 2, row: 15, text: 'Pabellón Independiente' }
      ]
    };
  }

  refresh(): void {
    this.pushCurrentData();
  }
}
