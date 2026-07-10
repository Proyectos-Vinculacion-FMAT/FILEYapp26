import { Component, inject, OnInit, computed, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ReactiveFormsModule, FormBuilder, FormGroup, FormArray, Validators, FormsModule } from '@angular/forms';
import { MatCardModule } from '@angular/material/card';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatSelectModule } from '@angular/material/select';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatChipsModule } from '@angular/material/chips';
import { MatExpansionModule } from '@angular/material/expansion';
import { MatSnackBar, MatSnackBarModule } from '@angular/material/snack-bar';
import { MatDividerModule } from '@angular/material/divider';
import { MatTooltipModule } from '@angular/material/tooltip';
import { MatDialog, MatDialogModule, MatDialogRef, MAT_DIALOG_DATA } from '@angular/material/dialog';
import { FormsModule as NgFormsModule } from '@angular/forms';
import { Router } from '@angular/router';
import { AuthService } from '../../../services/auth.service';
import { AplicacionService } from '../../../services/aplicacion.service';
import { EditorialService } from '../../../services/editorial.service';
import { FaseService } from '../../../services/fase.service';
import { Documento, SelloEditorial } from '../../../data/models';
import { StatusBadgeComponent } from '../../../shared/components/status-badge.component';
import { DateMxPipe } from '../../../shared/pipes/date-mx.pipe';

@Component({
  selector: 'app-motivo-dialog',
  standalone: true,
  imports: [CommonModule, MatDialogModule, MatFormFieldModule, MatInputModule, MatButtonModule, FormsModule],
  template: `
    <h2 mat-dialog-title>{{ data.titulo }}</h2>
    <mat-dialog-content>
      <p class="text-muted">{{ data.subtitulo }}</p>
      <mat-form-field appearance="outline" class="full-width">
        <mat-label>Motivo {{ data.opcional ? '(opcional)' : '' }}</mat-label>
        <textarea matInput [(ngModel)]="motivo" rows="4"
          [placeholder]="data.placeholder || 'Describa el motivo...'"></textarea>
      </mat-form-field>
    </mat-dialog-content>
    <mat-dialog-actions align="end">
      <button mat-button (click)="cancelar()">Cancelar</button>
      <button mat-raised-button [color]="data.color || 'primary'" (click)="confirmar()"
        [disabled]="!data.opcional && !motivo.trim()">
        {{ data.confirmarTexto || 'Confirmar' }}
      </button>
    </mat-dialog-actions>
  `,
  styles: [`.full-width { width: 100%; min-width: 400px; }`]
})
export class MotivoDialogComponent {
  motivo = '';
  data = inject<any>(MAT_DIALOG_DATA);
  private readonly ref = inject(MatDialogRef<MotivoDialogComponent>);
  cancelar() { this.ref.close(); }
  confirmar() { this.ref.close(this.motivo); }
}

@Component({
  selector: 'app-aplicacion',
  standalone: true,
  imports: [
    CommonModule, ReactiveFormsModule, FormsModule, MatCardModule, MatFormFieldModule,
    MatInputModule, MatSelectModule, MatButtonModule, MatIconModule, MatChipsModule,
    MatExpansionModule, MatSnackBarModule, MatDividerModule, MatTooltipModule, MatDialogModule,
    StatusBadgeComponent, DateMxPipe
  ],
  template: `
    <div class="page-container">
      <ng-container *ngIf="aplicacion(); else nuevaApp">
        <div class="header-row">
          <div>
            <h1 class="page-title">Mi aplicación a expositor</h1>
            <p class="page-subtitle">Folio: {{ aplicacion()!.id }} · Enviada: {{ aplicacion()!.fechaEnvio | dateMx }}</p>
          </div>
          <app-status-badge [estado]="aplicacion()!.estado"></app-status-badge>
        </div>

        <div *ngIf="aplicacion()!.estado === 'pendiente'" class="info-banner">
          <mat-icon>hourglass_empty</mat-icon>
          <div>
            <strong>Su solicitud está en proceso de revisión.</strong><br>
            Le notificaremos por correo cuando haya una resolución.
          </div>
        </div>

        <div *ngIf="aplicacion()!.estado === 'aceptada'" class="success-banner">
          <mat-icon>check_circle</mat-icon>
          <div class="flex-grow">
            <div>
              <strong>¡Su aplicación fue aceptada!</strong><br>
              Ya puede seleccionar y reservar sus stands en el mapa del showfloor.
            </div>
            <button mat-raised-button color="primary" (click)="irASeleccion()" class="cta-aceptada">
              Ir a selección de stands
              <mat-icon>arrow_forward</mat-icon>
            </button>
          </div>
        </div>

        <div *ngIf="aplicacion()!.estado === 'rechazada'" class="danger-banner">
          <mat-icon>cancel</mat-icon>
          <div>
            <strong>Aplicación rechazada.</strong>
            <div *ngIf="aplicacion()!.motivoPeticion" class="mt-1">
              Motivo: {{ aplicacion()!.motivoPeticion }}
            </div>
            <div class="mt-2">
              <button mat-raised-button color="primary" (click)="crearNuevaApp()">
                <mat-icon>refresh</mat-icon> Crear nueva aplicación
              </button>
            </div>
          </div>
        </div>

        <div *ngIf="aplicacion()!.estado === 'cambios_solicitados'" class="warning-banner">
          <mat-icon>edit</mat-icon>
          <div>
            <strong>El administrador solicitó cambios a su aplicación.</strong>
            <div class="mt-1">
              <strong>Motivo:</strong> {{ aplicacion()!.motivoPeticion }}
            </div>
            <div class="mt-1 text-muted"><small>Edite los datos necesarios abajo y use el botón "Reenviar".</small></div>
          </div>
        </div>

        <mat-card class="simular-panel mt-2"
          *ngIf="aplicacion()!.estado === 'pendiente' || aplicacion()!.estado === 'aceptada'">
          <mat-card-content>
            <div class="simular-header">
              <mat-icon>science</mat-icon>
              <div>
                <strong>Modo demostración</strong>
                <div class="text-muted small">
                  Como esto es un prototipo sin backend, use estos botones para simular la decisión del administrador.
                </div>
              </div>
            </div>
            <div class="simular-actions">
              <ng-container *ngIf="aplicacion()!.estado === 'pendiente'">
                <button mat-stroked-button class="btn-success" (click)="simularAprobar()">
                  <mat-icon>check_circle</mat-icon> Simular aprobación
                </button>
                <button mat-stroked-button class="btn-warn" (click)="simularSolicitarCambios()">
                  <mat-icon>edit</mat-icon> Simular solicitud de cambios
                </button>
                <button mat-stroked-button class="btn-danger" (click)="simularRechazar()">
                  <mat-icon>cancel</mat-icon> Simular rechazo
                </button>
              </ng-container>
              <ng-container *ngIf="aplicacion()!.estado === 'aceptada'">
                <button mat-stroked-button class="btn-warn" (click)="simularVolverAPendiente()">
                  <mat-icon>hourglass_empty</mat-icon> Volver a pendiente
                </button>
                <button mat-stroked-button class="btn-danger" (click)="simularRechazar()">
                  <mat-icon>cancel</mat-icon> Simular rechazo
                </button>
              </ng-container>
            </div>
          </mat-card-content>
        </mat-card>

        <mat-card class="mt-2">
          <mat-card-content>
            <mat-accordion multi>
              <mat-expansion-panel expanded>
                <mat-expansion-panel-header>
                  <mat-panel-title>Datos de la editorial</mat-panel-title>
                </mat-expansion-panel-header>
                <form [formGroup]="form" class="grid-2">
                  <mat-form-field appearance="outline">
                    <mat-label>Nombre de la editorial</mat-label>
                    <input matInput formControlName="nombre" [readonly]="!modoEdicion()">
                  </mat-form-field>
                  <mat-form-field appearance="outline">
                    <mat-label>Giro</mat-label>
                    <mat-select formControlName="giro" [disabled]="!modoEdicion()">
                      <mat-option value="Editor">Editor</mat-option>
                      <mat-option value="Librero">Librero</mat-option>
                      <mat-option value="Distribuidor">Distribuidor</mat-option>
                    </mat-select>
                  </mat-form-field>
                  <mat-form-field appearance="outline">
                    <mat-label>Calle</mat-label>
                    <input matInput formControlName="calle" [readonly]="!modoEdicion()">
                  </mat-form-field>
                  <mat-form-field appearance="outline">
                    <mat-label>Número</mat-label>
                    <input matInput formControlName="numero" [readonly]="!modoEdicion()">
                  </mat-form-field>
                  <mat-form-field appearance="outline">
                    <mat-label>Colonia</mat-label>
                    <input matInput formControlName="colonia" [readonly]="!modoEdicion()">
                  </mat-form-field>
                  <mat-form-field appearance="outline">
                    <mat-label>Código Postal</mat-label>
                    <input matInput formControlName="cp" [readonly]="!modoEdicion()">
                  </mat-form-field>
                  <mat-form-field appearance="outline">
                    <mat-label>Municipio</mat-label>
                    <input matInput formControlName="municipio" [readonly]="!modoEdicion()">
                  </mat-form-field>
                  <mat-form-field appearance="outline">
                    <mat-label>Estado</mat-label>
                    <input matInput formControlName="estado" [readonly]="!modoEdicion()">
                  </mat-form-field>
                  <mat-form-field appearance="outline">
                    <mat-label>Nombre del responsable del stand</mat-label>
                    <input matInput formControlName="responsableStand" [readonly]="!modoEdicion()">
                  </mat-form-field>
                  <mat-form-field appearance="outline">
                    <mat-label>Nombre en el antepecho</mat-label>
                    <input matInput formControlName="nombreAntepecho" [readonly]="!modoEdicion()">
                  </mat-form-field>
                  <mat-form-field appearance="outline">
                    <mat-label>Teléfono oficina</mat-label>
                    <input matInput formControlName="telefonoOficina" [readonly]="!modoEdicion()">
                  </mat-form-field>
                  <mat-form-field appearance="outline">
                    <mat-label>Teléfono celular</mat-label>
                    <input matInput formControlName="telefonoCelular" [readonly]="!modoEdicion()">
                  </mat-form-field>
                  <mat-form-field appearance="outline">
                    <mat-label>Correo electrónico</mat-label>
                    <input matInput formControlName="correoElectronico" [readonly]="!modoEdicion()">
                  </mat-form-field>
                  <mat-form-field appearance="outline">
                    <mat-label>Personas que atenderán</mat-label>
                    <input matInput type="number" formControlName="numPersonasAtienden" [readonly]="!modoEdicion()">
                  </mat-form-field>
                  <mat-form-field appearance="outline">
                    <mat-label>Cantidad de libros (aprox.)</mat-label>
                    <input matInput type="number" formControlName="cantidadLibrosAprox" [readonly]="!modoEdicion()">
                  </mat-form-field>
                  <mat-form-field appearance="outline">
                    <mat-label>Cantidad de títulos (aprox.)</mat-label>
                    <input matInput type="number" formControlName="cantidadTitulosAprox" [readonly]="!modoEdicion()">
                  </mat-form-field>
                </form>
              </mat-expansion-panel>

              <mat-expansion-panel>
                <mat-expansion-panel-header>
                  <mat-panel-title>Contactos</mat-panel-title>
                </mat-expansion-panel-header>
                <form [formGroup]="form" class="grid-2">
                  <mat-form-field appearance="outline">
                    <mat-label>Director general - Nombre</mat-label>
                    <input matInput formControlName="dg_nombre" [readonly]="!modoEdicion()">
                  </mat-form-field>
                  <mat-form-field appearance="outline">
                    <mat-label>Director general - Email</mat-label>
                    <input matInput formControlName="dg_email" [readonly]="!modoEdicion()">
                  </mat-form-field>
                  <mat-form-field appearance="outline">
                    <mat-label>Director comercial - Nombre</mat-label>
                    <input matInput formControlName="dc_nombre" [readonly]="!modoEdicion()">
                  </mat-form-field>
                  <mat-form-field appearance="outline">
                    <mat-label>Director comercial - Email</mat-label>
                    <input matInput formControlName="dc_email" [readonly]="!modoEdicion()">
                  </mat-form-field>
                  <mat-form-field appearance="outline">
                    <mat-label>Director editorial - Nombre</mat-label>
                    <input matInput formControlName="de_nombre" [readonly]="!modoEdicion()">
                  </mat-form-field>
                  <mat-form-field appearance="outline">
                    <mat-label>Director editorial - Email</mat-label>
                    <input matInput formControlName="de_email" [readonly]="!modoEdicion()">
                  </mat-form-field>
                  <mat-form-field appearance="outline">
                    <mat-label>Director promoción - Nombre</mat-label>
                    <input matInput formControlName="dp_nombre" [readonly]="!modoEdicion()">
                  </mat-form-field>
                  <mat-form-field appearance="outline">
                    <mat-label>Director promoción - Email</mat-label>
                    <input matInput formControlName="dp_email" [readonly]="!modoEdicion()">
                  </mat-form-field>
                </form>
              </mat-expansion-panel>

              <mat-expansion-panel>
                <mat-expansion-panel-header>
                  <mat-panel-title>Sellos editoriales</mat-panel-title>
                </mat-expansion-panel-header>
                <form [formGroup]="form">
                  <div formArrayName="sellos">
                    <div *ngFor="let sello of sellosControls.controls; let i = index" [formGroupName]="i" class="sello-row">
                      <mat-form-field appearance="outline" class="flex-grow">
                        <mat-label>Nombre del sello</mat-label>
                        <input matInput formControlName="nombre" [readonly]="!modoEdicion()">
                      </mat-form-field>
                      <mat-form-field appearance="outline" class="flex-grow">
                        <mat-label>Carta de representación (opcional)</mat-label>
                        <input matInput formControlName="cartaRepresentacion" [readonly]="!modoEdicion()" placeholder="Carta adjunta">
                      </mat-form-field>
                      <button mat-icon-button color="warn" (click)="quitarSello(i)" *ngIf="modoEdicion()" matTooltip="Quitar sello">
                        <mat-icon>delete</mat-icon>
                      </button>
                    </div>
                  </div>
                </form>
                <button mat-stroked-button (click)="agregarSello()" *ngIf="modoEdicion()">
                  <mat-icon>add</mat-icon> Agregar sello
                </button>
                <p class="text-muted mt-2" *ngIf="sellosControls.length === 0">
                  No ha declarado sellos editoriales.
                </p>
              </mat-expansion-panel>

              <mat-expansion-panel>
                <mat-expansion-panel-header>
                  <mat-panel-title>Materiales y temáticas</mat-panel-title>
                </mat-expansion-panel-header>
                <div>
                  <label class="lbl">Materiales</label>
                  <mat-form-field appearance="outline" class="full-width">
                    <mat-chip-grid #chipGridMateriales>
                      <mat-chip-row *ngFor="let material of materialesSeleccionados()" (removed)="quitarMaterial(material)">
                        {{ material }}
                        <button matChipRemove [attr.aria-label]="'Quitar ' + material" *ngIf="modoEdicion()">
                          <mat-icon>cancel</mat-icon>
                        </button>
                      </mat-chip-row>
                    </mat-chip-grid>
                    <input placeholder="Agregar material..." [matChipInputFor]="chipGridMateriales"
                      [matChipInputSeparatorKeyCodes]="separatorKeysCodes"
                      (matChipInputTokenEnd)="agregarMaterial($event)" [readonly]="!modoEdicion()">
                  </mat-form-field>

                  <label class="lbl">Temáticas</label>
                  <mat-form-field appearance="outline" class="full-width">
                    <mat-chip-grid #chipGridTematicas>
                      <mat-chip-row *ngFor="let tematica of tematicasSeleccionadas()" (removed)="quitarTematica(tematica)">
                        {{ tematica }}
                        <button matChipRemove [attr.aria-label]="'Quitar ' + tematica" *ngIf="modoEdicion()">
                          <mat-icon>cancel</mat-icon>
                        </button>
                      </mat-chip-row>
                    </mat-chip-grid>
                    <input placeholder="Agregar temática..." [matChipInputFor]="chipGridTematicas"
                      [matChipInputSeparatorKeyCodes]="separatorKeysCodes"
                      (matChipInputTokenEnd)="agregarTematica($event)" [readonly]="!modoEdicion()">
                  </mat-form-field>
                </div>
              </mat-expansion-panel>

              <mat-expansion-panel>
                <mat-expansion-panel-header>
                  <mat-panel-title>Documentos</mat-panel-title>
                </mat-expansion-panel-header>
                <div class="doc-list">
                  <div *ngFor="let doc of aplicacion()!.documentos" class="doc-item">
                    <mat-icon>description</mat-icon>
                    <div class="flex-grow">
                      <div class="doc-name">{{ doc.nombreArchivo }}</div>
                      <div class="doc-type text-muted">{{ doc.tipo }}</div>
                    </div>
                    <button mat-icon-button (click)="descargarDoc(doc)" matTooltip="Descargar">
                      <mat-icon>download</mat-icon>
                    </button>
                  </div>
                </div>
                <div *ngIf="modoEdicion()" class="mt-2">
                  <button mat-stroked-button (click)="simularCarga()">
                    <mat-icon>upload</mat-icon> Adjuntar documento
                  </button>
                  <p class="text-muted mt-1"><small>Prototipo: la carga de archivos es simulada</small></p>
                </div>
              </mat-expansion-panel>
            </mat-accordion>

            <div class="action-bar">
              <button mat-raised-button color="primary" (click)="reenviar()" *ngIf="modoEdicion()">
                <mat-icon>send</mat-icon>
                {{ aplicacion()!.estado === 'cambios_solicitados' ? 'Reenviar aplicación' : 'Enviar' }}
              </button>
            </div>
          </mat-card-content>
        </mat-card>
      </ng-container>

      <ng-template #nuevaApp>
        <div class="nueva-app">
          <mat-icon class="big-icon">description</mat-icon>
          <h1 class="page-title">Aplicar a ser expositor</h1>
          <p class="page-subtitle">
            Complete el siguiente formulario para iniciar su proceso de aplicación a FILEY.
          </p>
          <button mat-raised-button color="primary" (click)="crearNuevaApp()">
            <mat-icon>add</mat-icon> Iniciar nueva aplicación
          </button>
        </div>
      </ng-template>
    </div>
  `,
  styles: [`
    .header-row { display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px; gap: 12px; }
    .grid-2 { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; }
    .sello-row { display: flex; gap: 8px; align-items: center; margin-bottom: 8px; }
    .lbl { display: block; font-weight: 600; margin: 16px 0 8px; color: var(--filey-primary); }
    .doc-list { display: flex; flex-direction: column; gap: 8px; }
    .doc-item {
      display: flex; align-items: center; gap: 12px; padding: 12px;
      background: var(--filey-bg-soft); border: 1px solid var(--filey-border); border-radius: 4px;
    }
    .doc-name { font-weight: 500; }
    .doc-type { font-size: 12px; text-transform: uppercase; }
    .flex-grow { flex: 1; }
    mat-form-field { width: 100%; }
    .mt-1 { margin-top: 8px; }
    .mt-2 { margin-top: 16px; }
    .text-muted { color: var(--filey-text-muted); }
    .small { font-size: 12px; }
    .success-banner > div {
      display: flex; gap: 16px; align-items: center; justify-content: space-between; flex-wrap: wrap;
    }
    .cta-aceptada { white-space: nowrap; }
    .simular-panel { background: #f3f4f6; border: 1px dashed #9ca3af; }
    .simular-header { display: flex; gap: 12px; align-items: flex-start; margin-bottom: 16px; }
    .simular-header mat-icon { color: var(--filey-secondary); }
    .simular-actions { display: flex; gap: 8px; flex-wrap: wrap; }
    .btn-success { color: var(--filey-success) !important; border-color: var(--filey-success) !important; }
    .btn-warn { color: var(--filey-secondary) !important; border-color: var(--filey-secondary) !important; }
    .btn-danger { color: #c0473b !important; border-color: #c0473b !important; }
    .nueva-app { text-align: center; padding: 48px 24px; }
    .big-icon { font-size: 64px; width: 64px; height: 64px; color: var(--filey-primary); }
  `]
})
export class AplicacionComponent implements OnInit {
  private readonly fb = inject(FormBuilder);
  private readonly authService = inject(AuthService);
  private readonly aplicacionService = inject(AplicacionService);
  private readonly editorialService = inject(EditorialService);
  private readonly faseService = inject(FaseService);
  private readonly router = inject(Router);
  private readonly snackBar = inject(MatSnackBar);
  private readonly dialog = inject(MatDialog);

  readonly aplicacion = signal<any>(null);
  readonly modoEdicion = signal(false);

  readonly materialesSeleccionados = signal<string[]>([]);
  readonly tematicasSeleccionadas = signal<string[]>([]);
  readonly separatorKeysCodes = [13, 188];

  form!: FormGroup;
  sellosControls!: FormArray;

  ngOnInit(): void {
    this.aplicacion.set(this.aplicacionService.getAplicacionActual());
    if (this.aplicacion()) {
      this.modoEdicion.set(this.aplicacion().estado === 'cambios_solicitados' || this.aplicacion().estado === 'pendiente');
      this.cargarFormulario();
    }
  }

  cargarFormulario(): void {
    const ed = this.editorialService.getById(this.authService.editorialActual);
    const app = this.aplicacion();
    if (!ed || !app) return;

    this.materialesSeleccionados.set([...ed.materiales]);
    this.tematicasSeleccionadas.set([...ed.tematicas]);

    this.form = this.fb.group({
      nombre: [ed.nombre, Validators.required],
      giro: [ed.giro, Validators.required],
      calle: [ed.domicilio.calle, Validators.required],
      numero: [ed.domicilio.numero, Validators.required],
      colonia: [ed.domicilio.colonia, Validators.required],
      cp: [ed.domicilio.cp, Validators.required],
      municipio: [ed.domicilio.municipio, Validators.required],
      estado: [ed.domicilio.estado, Validators.required],
      responsableStand: [ed.responsableStand, Validators.required],
      nombreAntepecho: [ed.nombreAntepecho, Validators.required],
      telefonoOficina: [ed.telefonoOficina, Validators.required],
      telefonoCelular: [ed.telefonoCelular, Validators.required],
      correoElectronico: [ed.correoElectronico, [Validators.required, Validators.email]],
      numPersonasAtienden: [ed.numPersonasAtienden, Validators.required],
      cantidadLibrosAprox: [ed.cantidadLibrosAprox, Validators.required],
      cantidadTitulosAprox: [ed.cantidadTitulosAprox, Validators.required],
      dg_nombre: [ed.contactos.directorGeneral.nombre],
      dg_email: [ed.contactos.directorGeneral.email],
      dc_nombre: [ed.contactos.directorComercial.nombre],
      dc_email: [ed.contactos.directorComercial.email],
      de_nombre: [ed.contactos.directorEditorial.nombre],
      de_email: [ed.contactos.directorEditorial.email],
      dp_nombre: [ed.contactos.directorPromocion.nombre],
      dp_email: [ed.contactos.directorPromocion.email],
      sellos: this.fb.array(app.sellos.map((s: SelloEditorial) => this.fb.group({
        nombre: [s.nombre, Validators.required],
        cartaRepresentacion: [s.cartaRepresentacionId ? 'Carta adjunta' : '']
      })))
    });
    this.sellosControls = this.form.get('sellos') as FormArray;
  }

  get sellos(): FormArray { return this.sellosControls; }

  agregarSello(): void {
    this.sellosControls.push(this.fb.group({
      nombre: ['', Validators.required],
      cartaRepresentacion: ['']
    }));
  }

  quitarSello(i: number): void {
    this.sellosControls.removeAt(i);
  }

  agregarMaterial(event: any): void {
    const value = (event.value || '').trim();
    if (value && !this.materialesSeleccionados().includes(value)) {
      this.materialesSeleccionados.update(list => [...list, value]);
    }
    event.chipInput?.clear();
  }

  quitarMaterial(mat: string): void {
    this.materialesSeleccionados.update(list => list.filter(m => m !== mat));
  }

  agregarTematica(event: any): void {
    const value = (event.value || '').trim();
    if (value && !this.tematicasSeleccionadas().includes(value)) {
      this.tematicasSeleccionadas.update(list => [...list, value]);
    }
    event.chipInput?.clear();
  }

  quitarTematica(t: string): void {
    this.tematicasSeleccionadas.update(list => list.filter(x => x !== t));
  }

  descargarDoc(doc: Documento): void {
    this.snackBar.open(`Descargando ${doc.nombreArchivo} (simulado)`, 'OK', { duration: 2000 });
  }

  simularCarga(): void {
    this.snackBar.open('Carga de archivo simulada (prototipo sin backend)', 'OK', { duration: 2000 });
  }

  reenviar(): void {
    if (this.form && this.form.invalid) {
      this.snackBar.open('Complete todos los campos requeridos', 'OK', { duration: 3000 });
      return;
    }
    const app = this.aplicacion();
    if (app) {
      const sellos: SelloEditorial[] = this.sellosControls.value.map((s: any, i: number) => ({
        id: app.sellos[i]?.id || `SL-${Date.now()}-${i}`,
        editorialId: app.editorialId,
        nombre: s.nombre,
        cartaRepresentacionId: s.cartaRepresentacion ? `DOC-CR-${Date.now()}` : undefined
      }));
      this.aplicacionService.reenviar(app.id, sellos, app.documentos);
      this.snackBar.open('Aplicación reenviada con éxito', 'OK', { duration: 3000 });
      this.aplicacion.set(this.aplicacionService.getAplicacionActual());
      this.modoEdicion.set(false);
      this.faseService.refrescar();
    }
  }

  irASeleccion(): void {
    this.router.navigate(['/usuario/seleccion']);
  }

  crearNuevaApp(): void {
    this.aplicacionService.crear(
      this.authService.editorialActual,
      'EVT-001',
      [],
      [{ id: `DOC-${Date.now()}`, tipo: 'constancia_fiscal', nombreArchivo: 'Nueva_Constancia.pdf', url: '#', fechaCarga: new Date() }]
    );
    this.aplicacion.set(this.aplicacionService.getAplicacionActual());
    this.modoEdicion.set(true);
    this.cargarFormulario();
    this.faseService.refrescar();
  }

  simularAprobar(): void {
    const app = this.aplicacion();
    if (!app) return;
    this.aplicacionService.aceptar(app.id);
    this.aplicacion.set(this.aplicacionService.getAplicacionActual());
    this.modoEdicion.set(false);
    this.faseService.refrescar();
    this.snackBar.open('Simulación: aplicación aprobada', 'OK', { duration: 2500 });
  }

  simularVolverAPendiente(): void {
    const app = this.aplicacion();
    if (!app) return;
    this.aplicacionService.actualizar(app.id, {
      estado: 'pendiente',
      fechaRevision: undefined,
      revisadoPor: undefined,
      motivoPeticion: undefined
    });
    this.aplicacion.set(this.aplicacionService.getAplicacionActual());
    this.modoEdicion.set(true);
    this.faseService.refrescar();
    this.snackBar.open('Simulación: estado revertido a pendiente', 'OK', { duration: 2500 });
  }

  simularRechazar(): void {
    const app = this.aplicacion();
    if (!app) return;
    const ref = this.dialog.open(MotivoDialogComponent, {
      data: {
        titulo: 'Simular rechazo de la aplicación',
        subtitulo: 'Como administrador, ingrese un motivo (se mostrará al usuario).',
        color: 'warn',
        confirmarTexto: 'Simular rechazo'
      }
    });
    ref.afterClosed().subscribe(motivo => {
      if (motivo === undefined) return;
      this.aplicacionService.rechazar(app.id, motivo);
      this.aplicacion.set(this.aplicacionService.getAplicacionActual());
      this.modoEdicion.set(false);
      this.faseService.refrescar();
      this.snackBar.open('Simulación: aplicación rechazada', 'OK', { duration: 2500 });
    });
  }

  simularSolicitarCambios(): void {
    const app = this.aplicacion();
    if (!app) return;
    const ref = this.dialog.open(MotivoDialogComponent, {
      data: {
        titulo: 'Simular solicitud de cambios',
        subtitulo: 'Como administrador, ingrese el motivo de los cambios solicitados.',
        color: 'accent',
        confirmarTexto: 'Solicitar cambios'
      }
    });
    ref.afterClosed().subscribe(motivo => {
      if (motivo === undefined) return;
      this.aplicacionService.solicitarCambios(app.id, motivo);
      this.aplicacion.set(this.aplicacionService.getAplicacionActual());
      this.modoEdicion.set(true);
      this.faseService.refrescar();
      this.snackBar.open('Simulación: cambios solicitados al usuario', 'OK', { duration: 2500 });
    });
  }
}
