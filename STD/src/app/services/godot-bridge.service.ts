import { Injectable } from '@angular/core';
import { Subject, Observable } from 'rxjs';

export type GodotMode = 'viewer' | 'editor';

export interface GodotStandEvent {
  standId: string;
}

export interface GodotMapData {
  grid: {
    cell_size: number;
    cols: number;
    rows: number;
    meters_per_cell: number;
  };
  stands: GodotStand[];
  decorations: any[];
}

export interface GodotStand {
  id: string;
  col: number;
  row: number;
  w: number;
  h: number;
  label: string;
  status: 'available' | 'reserved' | 'unavailable';
  price: number;
  dimensions_text: string;
  zone?: string;
}

@Injectable({ providedIn: 'root' })
export class GodotBridgeService {
  private readonly CHANNEL = 'event-stand-map';
  private iframeRef: HTMLIFrameElement | null = null;
  private reqIdCounter = 0;
  private pendingReqId: number | null = null;

  private readonly readySubject = new Subject<void>();
  private readonly openStandSubject = new Subject<GodotStandEvent>();
  private readonly addToCartSubject = new Subject<GodotStandEvent>();
  private readonly saveMapSubject = new Subject<GodotMapData>();
  private readonly errorSubject = new Subject<{ message: string; context: any }>();

  readonly ready$: Observable<void> = this.readySubject.asObservable();
  readonly openStand$: Observable<GodotStandEvent> = this.openStandSubject.asObservable();
  readonly addToCart$: Observable<GodotStandEvent> = this.addToCartSubject.asObservable();
  readonly saveMap$: Observable<GodotMapData> = this.saveMapSubject.asObservable();
  readonly error$: Observable<{ message: string; context: any }> = this.errorSubject.asObservable();

  private mode: GodotMode = 'viewer';
  private currentMapData: GodotMapData | null = null;
  private listenerAttached = false;

  registerIframe(iframe: HTMLIFrameElement, mode: GodotMode): void {
    this.iframeRef = iframe;
    this.mode = mode;
    if (!this.listenerAttached) {
      window.addEventListener('message', this.handleMessage);
      this.listenerAttached = true;
    }
  }

  retryPush(): void {
    if (this.currentMapData) this.pushMapData(this.currentMapData);
  }

  unregisterIframe(): void {
    this.iframeRef = null;
  }

  pushMapData(data: GodotMapData, reqId?: number): void {
    this.currentMapData = data;
    const msg: any = {
      channel: this.CHANNEL,
      type: 'mapData',
      payload: data
    };
    if (reqId !== undefined) msg.reqId = reqId;
    this.postMessage(msg);
  }

  setMode(mode: GodotMode): void {
    this.mode = mode;
    this.postMessage({ channel: this.CHANNEL, type: 'setMode', payload: { mode } });
  }

  private handleMessage = (event: MessageEvent): void => {
    const data = event.data;
    if (!data) return;
    if (data.channel !== this.CHANNEL) return;

    switch (data.type) {
      case 'ready':
        this.readySubject.next();
        if (this.currentMapData) this.pushMapData(this.currentMapData);
        break;
      case 'getMapData':
        this.reqIdCounter += 1;
        this.pendingReqId = this.reqIdCounter;
        if (this.currentMapData) this.pushMapData(this.currentMapData, this.pendingReqId);
        break;
      case 'openStand':
        this.openStandSubject.next(data.payload);
        break;
      case 'addToCart':
        this.addToCartSubject.next(data.payload);
        break;
      case 'saveMap':
        this.saveMapSubject.next(data.payload);
        break;
      case 'error':
        this.errorSubject.next(data.payload);
        break;
    }
  };

  private postMessage(msg: any): void {
    if (!this.iframeRef?.contentWindow) return;
    this.iframeRef.contentWindow.postMessage(msg, window.location.origin);
  }
}
