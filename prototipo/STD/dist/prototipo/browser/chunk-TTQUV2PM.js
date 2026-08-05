import{a as Le,b as Ue,c as Ze}from"./chunk-EAR2MWQS.js";import{a as Ke,b as Je,c as Qe,d as We,e as Ye,f as et,g as tt,h as nt,i as at,j as rt,k as it}from"./chunk-WEECC5BN.js";import{b as Fe,c as Ve}from"./chunk-47X6MSTQ.js";import{a as $e}from"./chunk-KAAH2LQN.js";import{a as Ge}from"./chunk-LOUJGX4A.js";import{a as qe}from"./chunk-KNVYK7P3.js";import{a as He}from"./chunk-XKPGVGF3.js";import{a as ze,b as Ne}from"./chunk-PM6EGITH.js";import{a as we,b as ke,c as De,d as Be,e as Ae}from"./chunk-MV7FNB7P.js";import{a as Te}from"./chunk-QAW7Y32V.js";import{B as Me,F as Ce,G as Ee,J as Se,L as Pe,M as Re,d as le,f as M,h as ce,i as de,l as pe,m as ue,p as ge,q as _e,s as fe,u as ve,v as be,w as xe,y as he,z as ye}from"./chunk-YFX3RNMQ.js";import{a as Xe,b as je}from"./chunk-USSMPJOG.js";import"./chunk-QMLWXKMV.js";import{b as Ie}from"./chunk-JF3SS6UH.js";import{M as oe,Y as me,Z as se,d as ae,e as re,f as ie}from"./chunk-4YXYQSCY.js";import"./chunk-73ALEGO2.js";import{a as Oe}from"./chunk-TSHVXL4N.js";import"./chunk-4FL4YEM7.js";import{a as ne}from"./chunk-7YINBZDF.js";import{d as Y,e as ee,i as te}from"./chunk-JUEAZOHP.js";import{g as J,h as Q,j as W}from"./chunk-57DNE6ZE.js";import{$ as z,Aa as j,Ab as G,Bb as L,Fb as d,Gb as t,Hb as e,Hc as K,Ib as g,Jb as I,Kb as T,Lb as C,Lc as F,Mb as f,Nb as v,Pb as k,Rb as w,Tb as x,Xa as o,Z as V,ba as u,bc as D,cc as B,db as $,dc as y,ec as U,fc as n,ga as S,gc as c,ha as P,hc as b,ic as Z,kb as O,lb as q,oa as N,pa as X,qb as p,rc as _,sc as h,ta as R,tc as E,uc as A,zb as H}from"./chunk-RGBEC4WX.js";function dt(a,i){a&1&&C(0,"div",2)}var pt=new z("MAT_PROGRESS_BAR_DEFAULT_OPTIONS");var mt=(()=>{class a{_elementRef=u(j);_ngZone=u(X);_changeDetectorRef=u(K);_renderer=u($);_cleanupTransitionEnd;constructor(){let r=oe(),s=u(pt,{optional:!0});this._isNoopAnimation=r==="di-disabled",r==="reduced-motion"&&this._elementRef.nativeElement.classList.add("mat-progress-bar-reduced-motion"),s&&(s.color&&(this.color=this._defaultColor=s.color),this.mode=s.mode||this.mode)}_isNoopAnimation;get color(){return this._color||this._defaultColor}set color(r){this._color=r}_color;_defaultColor="primary";get value(){return this._value}set value(r){this._value=ot(r||0),this._changeDetectorRef.markForCheck()}_value=0;get bufferValue(){return this._bufferValue||0}set bufferValue(r){this._bufferValue=ot(r||0),this._changeDetectorRef.markForCheck()}_bufferValue=0;animationEnd=new N;get mode(){return this._mode}set mode(r){this._mode=r,this._changeDetectorRef.markForCheck()}_mode="determinate";ngAfterViewInit(){this._ngZone.runOutsideAngular(()=>{this._cleanupTransitionEnd=this._renderer.listen(this._elementRef.nativeElement,"transitionend",this._transitionendHandler)})}ngOnDestroy(){this._cleanupTransitionEnd?.()}_getPrimaryBarTransform(){return`scaleX(${this._isIndeterminate()?1:this.value/100})`}_getBufferBarFlexBasis(){return`${this.mode==="buffer"?this.bufferValue:100}%`}_isIndeterminate(){return this.mode==="indeterminate"||this.mode==="query"}_transitionendHandler=r=>{this.animationEnd.observers.length===0||!r.target||!r.target.classList.contains("mdc-linear-progress__primary-bar")||(this.mode==="determinate"||this.mode==="buffer")&&this._ngZone.run(()=>this.animationEnd.next({value:this.value}))};static \u0275fac=function(s){return new(s||a)};static \u0275cmp=O({type:a,selectors:[["mat-progress-bar"]],hostAttrs:["role","progressbar","aria-valuemin","0","aria-valuemax","100","tabindex","-1",1,"mat-mdc-progress-bar","mdc-linear-progress"],hostVars:10,hostBindings:function(s,l){s&2&&(H("aria-valuenow",l._isIndeterminate()?null:l.value)("mode",l.mode),U("mat-"+l.color),y("_mat-animation-noopable",l._isNoopAnimation)("mdc-linear-progress--animation-ready",!l._isNoopAnimation)("mdc-linear-progress--indeterminate",l._isIndeterminate()))},inputs:{color:"color",value:[2,"value","value",F],bufferValue:[2,"bufferValue","bufferValue",F],mode:"mode"},outputs:{animationEnd:"animationEnd"},exportAs:["matProgressBar"],decls:7,vars:5,consts:[["aria-hidden","true",1,"mdc-linear-progress__buffer"],[1,"mdc-linear-progress__buffer-bar"],[1,"mdc-linear-progress__buffer-dots"],["aria-hidden","true",1,"mdc-linear-progress__bar","mdc-linear-progress__primary-bar"],[1,"mdc-linear-progress__bar-inner"],["aria-hidden","true",1,"mdc-linear-progress__bar","mdc-linear-progress__secondary-bar"]],template:function(s,l){s&1&&(I(0,"div",0),C(1,"div",1),G(2,dt,1,0,"div",2),T(),I(3,"div",3),C(4,"span",4),T(),I(5,"div",5),C(6,"span",4),T()),s&2&&(o(),B("flex-basis",l._getBufferBarFlexBasis()),o(),L(l.mode==="buffer"?2:-1),o(),B("transform",l._getPrimaryBarTransform()))},styles:[`.mat-mdc-progress-bar {
  --mat-progress-bar-animation-multiplier: 1;
  display: block;
  text-align: start;
}
.mat-mdc-progress-bar[mode=query] {
  transform: scaleX(-1);
}
.mat-mdc-progress-bar._mat-animation-noopable .mdc-linear-progress__buffer-dots,
.mat-mdc-progress-bar._mat-animation-noopable .mdc-linear-progress__primary-bar,
.mat-mdc-progress-bar._mat-animation-noopable .mdc-linear-progress__secondary-bar,
.mat-mdc-progress-bar._mat-animation-noopable .mdc-linear-progress__bar-inner.mdc-linear-progress__bar-inner {
  animation: none;
}
.mat-mdc-progress-bar._mat-animation-noopable .mdc-linear-progress__primary-bar,
.mat-mdc-progress-bar._mat-animation-noopable .mdc-linear-progress__buffer-bar {
  transition: transform 1ms;
}

.mat-progress-bar-reduced-motion {
  --mat-progress-bar-animation-multiplier: 2;
}

.mdc-linear-progress {
  position: relative;
  width: 100%;
  transform: translateZ(0);
  outline: 1px solid transparent;
  overflow-x: hidden;
  transition: opacity 250ms 0ms cubic-bezier(0.4, 0, 0.6, 1);
  height: max(var(--mat-progress-bar-track-height, 4px), var(--mat-progress-bar-active-indicator-height, 4px));
}
@media (forced-colors: active) {
  .mdc-linear-progress {
    outline-color: CanvasText;
  }
}

.mdc-linear-progress__bar {
  position: absolute;
  top: 0;
  bottom: 0;
  margin: auto 0;
  width: 100%;
  animation: none;
  transform-origin: top left;
  transition: transform 250ms 0ms cubic-bezier(0.4, 0, 0.6, 1);
  height: var(--mat-progress-bar-active-indicator-height, 4px);
}
.mdc-linear-progress--indeterminate .mdc-linear-progress__bar {
  transition: none;
}
[dir=rtl] .mdc-linear-progress__bar {
  right: 0;
  transform-origin: center right;
}

.mdc-linear-progress__bar-inner {
  display: inline-block;
  position: absolute;
  width: 100%;
  animation: none;
  border-top-style: solid;
  border-color: var(--mat-progress-bar-active-indicator-color, var(--mat-sys-primary));
  border-top-width: var(--mat-progress-bar-active-indicator-height, 4px);
}

.mdc-linear-progress__buffer {
  display: flex;
  position: absolute;
  top: 0;
  bottom: 0;
  margin: auto 0;
  width: 100%;
  overflow: hidden;
  height: var(--mat-progress-bar-track-height, 4px);
  border-radius: var(--mat-progress-bar-track-shape, var(--mat-sys-corner-none));
}

.mdc-linear-progress__buffer-dots {
  background-image: radial-gradient(circle, var(--mat-progress-bar-track-color, var(--mat-sys-surface-variant)) calc(var(--mat-progress-bar-track-height, 4px) / 2), transparent 0);
  background-repeat: repeat-x;
  background-size: calc(calc(var(--mat-progress-bar-track-height, 4px) / 2) * 5);
  background-position: left;
  flex: auto;
  transform: rotate(180deg);
  animation: mdc-linear-progress-buffering calc(250ms * var(--mat-progress-bar-animation-multiplier)) infinite linear;
}
@media (forced-colors: active) {
  .mdc-linear-progress__buffer-dots {
    background-color: ButtonBorder;
  }
}
[dir=rtl] .mdc-linear-progress__buffer-dots {
  animation: mdc-linear-progress-buffering-reverse calc(250ms * var(--mat-progress-bar-animation-multiplier)) infinite linear;
  transform: rotate(0);
}

.mdc-linear-progress__buffer-bar {
  flex: 0 1 100%;
  transition: flex-basis 250ms 0ms cubic-bezier(0.4, 0, 0.6, 1);
  background-color: var(--mat-progress-bar-track-color, var(--mat-sys-surface-variant));
}

.mdc-linear-progress__primary-bar {
  transform: scaleX(0);
}
.mdc-linear-progress--indeterminate .mdc-linear-progress__primary-bar {
  left: -145.166611%;
}
.mdc-linear-progress--indeterminate.mdc-linear-progress--animation-ready .mdc-linear-progress__primary-bar {
  animation: mdc-linear-progress-primary-indeterminate-translate calc(2s * var(--mat-progress-bar-animation-multiplier)) infinite linear;
}
.mdc-linear-progress--indeterminate.mdc-linear-progress--animation-ready .mdc-linear-progress__primary-bar > .mdc-linear-progress__bar-inner {
  animation: mdc-linear-progress-primary-indeterminate-scale calc(2s * var(--mat-progress-bar-animation-multiplier)) infinite linear;
}
[dir=rtl] .mdc-linear-progress.mdc-linear-progress--animation-ready .mdc-linear-progress__primary-bar {
  animation-name: mdc-linear-progress-primary-indeterminate-translate-reverse;
}
[dir=rtl] .mdc-linear-progress.mdc-linear-progress--indeterminate .mdc-linear-progress__primary-bar {
  right: -145.166611%;
  left: auto;
}

.mdc-linear-progress__secondary-bar {
  display: none;
}
.mdc-linear-progress--indeterminate .mdc-linear-progress__secondary-bar {
  left: -54.888891%;
  display: block;
}
.mdc-linear-progress--indeterminate.mdc-linear-progress--animation-ready .mdc-linear-progress__secondary-bar {
  animation: mdc-linear-progress-secondary-indeterminate-translate calc(2s * var(--mat-progress-bar-animation-multiplier)) infinite linear;
}
.mdc-linear-progress--indeterminate.mdc-linear-progress--animation-ready .mdc-linear-progress__secondary-bar > .mdc-linear-progress__bar-inner {
  animation: mdc-linear-progress-secondary-indeterminate-scale calc(2s * var(--mat-progress-bar-animation-multiplier)) infinite linear;
}
[dir=rtl] .mdc-linear-progress.mdc-linear-progress--animation-ready .mdc-linear-progress__secondary-bar {
  animation-name: mdc-linear-progress-secondary-indeterminate-translate-reverse;
}
[dir=rtl] .mdc-linear-progress.mdc-linear-progress--indeterminate .mdc-linear-progress__secondary-bar {
  right: -54.888891%;
  left: auto;
}

@keyframes mdc-linear-progress-buffering {
  from {
    transform: rotate(180deg) translateX(calc(var(--mat-progress-bar-track-height, 4px) * -2.5));
  }
}
@keyframes mdc-linear-progress-primary-indeterminate-translate {
  0% {
    transform: translateX(0);
  }
  20% {
    animation-timing-function: cubic-bezier(0.5, 0, 0.701732, 0.495819);
    transform: translateX(0);
  }
  59.15% {
    animation-timing-function: cubic-bezier(0.302435, 0.381352, 0.55, 0.956352);
    transform: translateX(83.67142%);
  }
  100% {
    transform: translateX(200.611057%);
  }
}
@keyframes mdc-linear-progress-primary-indeterminate-scale {
  0% {
    transform: scaleX(0.08);
  }
  36.65% {
    animation-timing-function: cubic-bezier(0.334731, 0.12482, 0.785844, 1);
    transform: scaleX(0.08);
  }
  69.15% {
    animation-timing-function: cubic-bezier(0.06, 0.11, 0.6, 1);
    transform: scaleX(0.661479);
  }
  100% {
    transform: scaleX(0.08);
  }
}
@keyframes mdc-linear-progress-secondary-indeterminate-translate {
  0% {
    animation-timing-function: cubic-bezier(0.15, 0, 0.515058, 0.409685);
    transform: translateX(0);
  }
  25% {
    animation-timing-function: cubic-bezier(0.31033, 0.284058, 0.8, 0.733712);
    transform: translateX(37.651913%);
  }
  48.35% {
    animation-timing-function: cubic-bezier(0.4, 0.627035, 0.6, 0.902026);
    transform: translateX(84.386165%);
  }
  100% {
    transform: translateX(160.277782%);
  }
}
@keyframes mdc-linear-progress-secondary-indeterminate-scale {
  0% {
    animation-timing-function: cubic-bezier(0.205028, 0.057051, 0.57661, 0.453971);
    transform: scaleX(0.08);
  }
  19.15% {
    animation-timing-function: cubic-bezier(0.152313, 0.196432, 0.648374, 1.004315);
    transform: scaleX(0.457104);
  }
  44.15% {
    animation-timing-function: cubic-bezier(0.257759, -0.003163, 0.211762, 1.38179);
    transform: scaleX(0.72796);
  }
  100% {
    transform: scaleX(0.08);
  }
}
@keyframes mdc-linear-progress-primary-indeterminate-translate-reverse {
  0% {
    transform: translateX(0);
  }
  20% {
    animation-timing-function: cubic-bezier(0.5, 0, 0.701732, 0.495819);
    transform: translateX(0);
  }
  59.15% {
    animation-timing-function: cubic-bezier(0.302435, 0.381352, 0.55, 0.956352);
    transform: translateX(-83.67142%);
  }
  100% {
    transform: translateX(-200.611057%);
  }
}
@keyframes mdc-linear-progress-secondary-indeterminate-translate-reverse {
  0% {
    animation-timing-function: cubic-bezier(0.15, 0, 0.515058, 0.409685);
    transform: translateX(0);
  }
  25% {
    animation-timing-function: cubic-bezier(0.31033, 0.284058, 0.8, 0.733712);
    transform: translateX(-37.651913%);
  }
  48.35% {
    animation-timing-function: cubic-bezier(0.4, 0.627035, 0.6, 0.902026);
    transform: translateX(-84.386165%);
  }
  100% {
    transform: translateX(-160.277782%);
  }
}
@keyframes mdc-linear-progress-buffering-reverse {
  from {
    transform: translateX(-10px);
  }
}
`],encapsulation:2,changeDetection:0})}return a})();function ot(a,i=0,r=100){return Math.max(i,Math.min(r,a))}var st=(()=>{class a{static \u0275fac=function(s){return new(s||a)};static \u0275mod=q({type:a});static \u0275inj=V({imports:[ae]})}return a})();function gt(a,i){a&1&&(t(0,"div",55)(1,"mat-icon"),n(2,"warning"),e(),t(3,"div")(4,"strong"),n(5,"Su reserva puede ser cancelada."),e(),g(6,"br"),n(7,' El plazo de 30 d\xEDas para cubrir el anticipo del 50% ha vencido. A\xFAn no ha cubierto el monto m\xEDnimo. Por favor regularice su situaci\xF3n registrando un pago en la pesta\xF1a "Pagos", o contacte a la organizaci\xF3n. '),e()())}function _t(a,i){if(a&1&&(t(0,"div",14)(1,"span",15),n(2),e(),t(3,"span",56),n(4),_(5,"currencyMx"),e()()),a&2){let r=i.$implicit;o(2),Z(" Descuento ",r.tipo==="pronto_pago"?"pronto pago":"especial"," (",r.porcentaje,"%) "),o(2),b("- ",h(5,3,r.montoDescontado))}}function ft(a,i){if(a&1&&(t(0,"div",27)(1,"mat-icon"),n(2,"event"),e(),t(3,"div")(4,"div",28),n(5,"Fecha de corte (pago total)"),e(),t(6,"div",29),n(7),_(8,"dateMx"),e()()()),a&2){let r=x(2);o(7),c(E(8,1,r.reserva().fechaCortePagoTotal,"largo"))}}function vt(a,i){if(a&1&&(t(0,"div",57)(1,"div",58),n(2),e(),t(3,"div",59)(4,"div"),n(5),e(),t(6,"div",60),n(7),e()(),t(8,"div",61),n(9),_(10,"currencyMx"),e()()),a&2){let r=i.$implicit;o(2),c(r.clave),o(3),c(r.zona),o(2),b("",r.metrosCuadradosSnapshot," m\xB2"),o(2),c(h(10,4,r.precioSnapshot))}}function bt(a,i){a&1&&(t(0,"mat-error"),n(1,"El monto es requerido"),e())}function xt(a,i){a&1&&(t(0,"mat-error"),n(1,"El monto excede el saldo pendiente"),e())}function ht(a,i){a&1&&(t(0,"p",62)(1,"small"),n(2,"* Prototipo: la carga de archivo es simulada. En el sistema real se requiere comprobante obligatorio."),e()())}function yt(a,i){a&1&&(t(0,"th",75),n(1,"Fecha"),e())}function Mt(a,i){if(a&1&&(t(0,"td",76),n(1),_(2,"dateMx"),e()),a&2){let r=i.$implicit;o(),c(E(2,1,r.fechaRegistro,"corto"))}}function Ct(a,i){a&1&&(t(0,"th",75),n(1,"Monto"),e())}function Et(a,i){if(a&1&&(t(0,"td",76),n(1),_(2,"currencyMx"),e()),a&2){let r=i.$implicit;o(),c(h(2,1,r.monto))}}function St(a,i){a&1&&(t(0,"th",75),n(1,"M\xE9todo"),e())}function Pt(a,i){if(a&1&&(t(0,"td",76),n(1),e()),a&2){let r=i.$implicit;o(),c(r.metodo)}}function Rt(a,i){a&1&&(t(0,"th",75),n(1,"Origen"),e())}function Ot(a,i){if(a&1&&(t(0,"td",76),n(1),e()),a&2){let r=i.$implicit;o(),c(r.origen==="usuario"?"Usuario":"Administrador")}}function It(a,i){a&1&&(t(0,"th",75),n(1,"Estado"),e())}function Tt(a,i){if(a&1&&(t(0,"td",76),g(1,"app-status-badge",10),e()),a&2){let r=i.$implicit;o(),d("estado",r.estado)}}function wt(a,i){a&1&&(t(0,"th",75),n(1,"Comprobante"),e())}function kt(a,i){if(a&1){let r=k();t(0,"button",78),w("click",function(){S(r);let l=x().$implicit,m=x(3);return P(m.verComprobante(l))}),t(1,"mat-icon"),n(2,"description"),e(),n(3," Ver "),e()}}function Dt(a,i){if(a&1&&(t(0,"td",76),p(1,kt,4,0,"button",77),e()),a&2){let r=i.$implicit;o(),d("ngIf",r.comprobanteNombre)}}function Bt(a,i){a&1&&g(0,"th",75)}function At(a,i){if(a&1&&(t(0,"span",60),n(1),e()),a&2){let r=x().$implicit;o(),b(" ",r.motivoRechazo," ")}}function Ft(a,i){if(a&1&&(t(0,"td",76),p(1,At,2,1,"span",79),e()),a&2){let r=i.$implicit;o(),d("ngIf",r.motivoRechazo)}}function Vt(a,i){a&1&&g(0,"tr",80)}function zt(a,i){a&1&&g(0,"tr",81)}function Nt(a,i){if(a&1&&(f(0),t(1,"table",63),f(2,64),p(3,yt,2,0,"th",65)(4,Mt,3,4,"td",66),v(),f(5,67),p(6,Ct,2,0,"th",65)(7,Et,3,3,"td",66),v(),f(8,68),p(9,St,2,0,"th",65)(10,Pt,2,1,"td",66),v(),f(11,69),p(12,Rt,2,0,"th",65)(13,Ot,2,1,"td",66),v(),f(14,70),p(15,It,2,0,"th",65)(16,Tt,2,1,"td",66),v(),f(17,71),p(18,wt,2,0,"th",65)(19,Dt,2,1,"td",66),v(),f(20,72),p(21,Bt,1,0,"th",65)(22,Ft,2,1,"td",66),v(),p(23,Vt,1,0,"tr",73)(24,zt,1,0,"tr",74),e(),v()),a&2){let r=x(2);o(),d("dataSource",r.movimientos()),o(22),d("matHeaderRowDef",r.columnasMov),o(),d("matRowDefColumns",r.columnasMov)}}function Xt(a,i){a&1&&g(0,"app-empty-state",82)}function jt(a,i){if(a&1){let r=k();f(0),p(1,gt,8,0,"div",6),t(2,"mat-card")(3,"mat-card-content")(4,"div",7)(5,"div")(6,"div",8),n(7),e(),t(8,"div",9),n(9),_(10,"dateMx"),e()(),g(11,"app-status-badge",10),e()()(),t(12,"mat-tab-group",11)(13,"mat-tab",12)(14,"div",13)(15,"mat-card")(16,"mat-card-header")(17,"mat-card-title"),n(18,"Desglose financiero"),e()(),t(19,"mat-card-content")(20,"div",14)(21,"span",15),n(22,"Total sin descuento"),e(),t(23,"span",16),n(24),_(25,"currencyMx"),e()(),p(26,_t,6,5,"div",17),t(27,"div",14)(28,"span",15),n(29,"Total con descuento"),e(),t(30,"span",16),n(31),_(32,"currencyMx"),e()(),t(33,"div",14)(34,"span",15),n(35),e(),t(36,"span",18),n(37),_(38,"currencyMx"),e()(),t(39,"div",14)(40,"span",15),n(41,"Monto abonado"),e(),t(42,"span",16),n(43),_(44,"currencyMx"),e()(),t(45,"div",19)(46,"span"),n(47,"Saldo pendiente"),e(),t(48,"span"),n(49),_(50,"currencyMx"),e()(),t(51,"div",20)(52,"div",21)(53,"span"),n(54,"Progreso de pago"),e(),t(55,"span"),n(56),e()(),g(57,"mat-progress-bar",22),t(58,"div",23)(59,"span",24),n(60,"50% Confirmada"),e(),t(61,"span",24),n(62,"100% Pagada"),e()()(),g(63,"mat-divider",25),t(64,"h3"),n(65,"Fechas clave"),e(),t(66,"div",26)(67,"div",27)(68,"mat-icon"),n(69,"schedule"),e(),t(70,"div")(71,"div",28),n(72,"Vencimiento del anticipo"),e(),t(73,"div",29),n(74),_(75,"dateMx"),e()()(),p(76,ft,9,4,"div",30),e()()(),t(77,"mat-card")(78,"mat-card-header")(79,"mat-card-title"),n(80,"Stands reservados"),e()(),t(81,"mat-card-content"),p(82,vt,11,6,"div",31),e()()()(),t(83,"mat-tab",32)(84,"div",33)(85,"div",34)(86,"mat-icon"),n(87,"info"),e(),t(88,"div")(89,"strong"),n(90,"Importante:"),e(),n(91," No se aceptan pagos en efectivo. Los m\xE9todos aceptados son transferencia bancaria, dep\xF3sito bancario o cheque. "),e()(),t(92,"h3"),n(93,"Datos bancarios"),e(),t(94,"div",35)(95,"div",36)(96,"span",37),n(97,"Titular"),e(),t(98,"span",38),n(99),e()(),t(100,"div",36)(101,"span",37),n(102,"Banco"),e(),t(103,"span",38),n(104),e()(),t(105,"div",36)(106,"span",37),n(107,"N\xFAmero de cuenta"),e(),t(108,"span",38),n(109),e()(),t(110,"div",36)(111,"span",37),n(112,"CLABE"),e(),t(113,"span",38),n(114),e()(),t(115,"div",36)(116,"span",37),n(117,"Sucursal"),e(),t(118,"span",38),n(119),e()(),t(120,"div",36)(121,"span",37),n(122,"Concepto / Referencia"),e(),t(123,"span",38),n(124),e()()(),t(125,"p",39)(126,"small"),n(127),e()(),g(128,"mat-divider",25),t(129,"h3"),n(130,"Registrar nuevo abono"),e(),t(131,"form",40),w("ngSubmit",function(){S(r);let l=x();return P(l.registrarPago())}),t(132,"div",41)(133,"mat-form-field",42)(134,"mat-label"),n(135,"Monto del abono"),e(),t(136,"span",43),n(137,"$\xA0"),e(),g(138,"input",44),p(139,bt,2,0,"mat-error",45)(140,xt,2,0,"mat-error",45),e(),t(141,"mat-form-field",42)(142,"mat-label"),n(143,"M\xE9todo de pago"),e(),t(144,"mat-select",46)(145,"mat-option",47),n(146,"Transferencia bancaria"),e(),t(147,"mat-option",48),n(148,"Dep\xF3sito bancario"),e(),t(149,"mat-option",49),n(150,"Cheque"),e()()()(),t(151,"div",50)(152,"label",37),n(153,"Comprobante de pago *"),e(),t(154,"button",51),w("click",function(){S(r);let l=x();return P(l.simularComprobante())}),t(155,"mat-icon"),n(156,"upload"),e(),n(157),e(),p(158,ht,3,0,"p",52),e(),t(159,"div",53)(160,"button",54)(161,"mat-icon"),n(162,"send"),e(),n(163," Registrar pago "),e()()(),g(164,"mat-divider",25),t(165,"h3"),n(166,"Historial de pagos"),e(),p(167,Nt,25,3,"ng-container",5)(168,Xt,1,0,"ng-template",null,1,A),e()()(),v()}if(a&2){let r,s,l=D(169),m=x();o(),d("ngIf",m.estaVencida()),o(6),b("Reserva ",m.reserva().id),o(2),b("Creada: ",E(10,38,m.reserva().fechaCreacion,"largo")),o(2),d("estado",m.reserva().estado),o(13),c(h(25,41,m.reserva().montoOriginal)),o(2),d("ngForOf",m.reserva().descuentos),o(5),c(h(32,43,m.reserva().montoTotal)),o(4),b("Anticipo requerido (",m.porcentajeAnticipo,"%)"),o(2),c(h(38,45,m.reserva().anticipoRequerido)),o(6),c(h(44,47,m.reserva().montoAbonado)),o(6),c(h(50,49,m.reserva().montoPendiente)),o(7),b("",m.porcentajePagado(),"%"),o(),d("value",m.porcentajePagado())("color",m.porcentajePagado()>=100?"primary":"accent"),o(2),y("reached",m.porcentajePagado()>=50),o(2),y("reached",m.porcentajePagado()>=100),o(12),y("warn",m.estaVencida()),o(),b(" ",E(75,51,m.reserva().fechaVencimientoAnticipo,"largo")," "),o(2),d("ngIf",m.reserva().fechaCortePagoTotal),o(6),d("ngForOf",m.reserva().stands),o(17),c(m.datos.titular),o(5),c(m.datos.banco),o(5),c(m.datos.cuenta),o(5),c(m.datos.clabe),o(5),c(m.datos.sucursal),o(5),c(m.datos.referencia),o(3),c(m.params.instruccionesPago),o(4),d("formGroup",m.formPago),o(8),d("ngIf",(r=m.formPago.get("monto"))==null?null:r.hasError("required")),o(),d("ngIf",(s=m.formPago.get("monto"))==null?null:s.hasError("excede")),o(17),b(" ",m.nombreComprobante()||"Adjuntar comprobante"," "),o(),d("ngIf",!m.nombreComprobante()),o(2),d("disabled",m.formPago.invalid||!m.nombreComprobante()),o(7),d("ngIf",m.movimientos().length>0)("ngIfElse",l)}}function $t(a,i){a&1&&(t(0,"mat-card")(1,"mat-card-content",83)(2,"mat-icon",84),n(3,"event_busy"),e(),t(4,"h2"),n(5,"No tienes una reserva activa"),e(),t(6,"p",9),n(7,"Selecciona stands en el mapa del showfloor para iniciar tu reserva."),e(),t(8,"a",85)(9,"mat-icon"),n(10,"map"),e(),n(11," Ir a selecci\xF3n de stands "),e()()())}var lt=class a{reservaService=u(Ie);movimientoService=u(Te);parametrosService=u(Oe);authService=u(ne);router=u(Y);snackBar=u(ze);fb=u(ve);reserva=R(null);movimientos=R([]);nombreComprobante=R(null);params=this.parametrosService.parametros;datos=this.params.datosBancarios;porcentajeAnticipo=50;columnasMov=["fecha","monto","metodo","origen","estado","comprobante","motivo"];formPago;ngOnInit(){this.reservaService.reservas$.subscribe(()=>{this.reserva.set(this.reservaService.getReservaActual()||null),this.cargarMovimientos()}),this.movimientoService.movimientos$.subscribe(()=>this.cargarMovimientos()),this.reserva.set(this.reservaService.getReservaActual()||null),this.cargarMovimientos(),this.formPago=this.fb.group({monto:[null,[M.required,M.min(.01)]],metodo:["transferencia",M.required]});let i=this.reserva();i&&(this.formPago.get("monto")?.setValidators([M.required,M.min(.01),r=>r.value>i.montoPendiente?{excede:!0}:null]),this.formPago.get("monto")?.updateValueAndValidity())}cargarMovimientos(){let i=this.reserva();i&&this.movimientos.set(this.movimientoService.getByReserva(i.id))}totalDescuentos(){return this.reserva()?.descuentos.reduce((i,r)=>i+r.montoDescontado,0)||0}porcentajePagado(){let i=this.reserva();return!i||i.montoTotal===0?0:Math.min(100,Math.round(i.montoAbonado/i.montoTotal*100))}estaVencida(){let i=this.reserva();return i?i.estado==="Por confirmar"&&i.fechaVencimientoAnticipo<new Date&&i.montoAbonado<i.anticipoRequerido:!1}simularComprobante(){let i=`comprobante_${Date.now()}.pdf`;this.nombreComprobante.set(i),this.snackBar.open("Comprobante simulado adjunto","OK",{duration:2e3})}registrarPago(){let i=this.reserva();if(!i||!this.formPago.valid||!this.nombreComprobante()){this.snackBar.open("Complete todos los campos","OK",{duration:3e3});return}let{monto:r,metodo:s}=this.formPago.value;this.movimientoService.registrarPagoUsuario(i.id,r,s,this.nombreComprobante()),this.snackBar.open("Pago registrado. Est\xE1 en revisi\xF3n por el administrador.","OK",{duration:4e3}),this.formPago.reset({metodo:"transferencia"}),this.nombreComprobante.set(null)}verComprobante(i){this.snackBar.open(`Viendo ${i.comprobanteNombre} (simulado)`,"OK",{duration:2e3})}static \u0275fac=function(r){return new(r||a)};static \u0275cmp=O({type:a,selectors:[["app-mi-reserva"]],decls:8,vars:2,consts:[["sinReserva",""],["sinMovs",""],[1,"page-container"],[1,"page-title"],[1,"page-subtitle"],[4,"ngIf","ngIfElse"],["class","warning-banner",4,"ngIf"],[1,"reserva-header"],[1,"reserva-id"],[1,"text-muted"],[3,"estado"],[1,"mt-2"],["label","Resumen"],[1,"grid-layout"],[1,"summary-row"],[1,"summary-label"],[1,"summary-value"],["class","summary-row",4,"ngFor","ngForOf"],[1,"summary-value","warn"],[1,"summary-row","total"],[1,"progress-section","mt-3"],[1,"progress-label"],["mode","determinate",3,"value","color"],[1,"progress-marks"],[1,"mark"],[1,"my-3"],[1,"fechas-grid"],[1,"fecha-item"],[1,"fecha-label"],[1,"fecha-value"],["class","fecha-item",4,"ngIf"],["class","stand-item",4,"ngFor","ngForOf"],["label","Pagos"],[1,"pagos-content"],[1,"info-banner"],[1,"datos-bancarios"],[1,"dato"],[1,"lbl"],[1,"val"],[1,"mt-2","text-muted"],[1,"form-pago",3,"ngSubmit","formGroup"],[1,"grid-2"],["appearance","outline"],["matTextPrefix",""],["matInput","","type","number","formControlName","monto","min","0.01"],[4,"ngIf"],["formControlName","metodo"],["value","transferencia"],["value","deposito"],["value","cheque"],[1,"comprobante-upload"],["mat-stroked-button","","type","button",3,"click"],["class","text-muted mt-1",4,"ngIf"],[1,"action-bar"],["mat-raised-button","","color","primary","type","submit",3,"disabled"],[1,"warning-banner"],[1,"summary-value","discount"],[1,"stand-item"],[1,"clave"],[1,"info"],[1,"text-muted","small"],[1,"precio"],[1,"text-muted","mt-1"],["mat-table","",1,"full-width",3,"dataSource"],["matColumnDef","fecha"],["mat-header-cell","",4,"matHeaderCellDef"],["mat-cell","",4,"matCellDef"],["matColumnDef","monto"],["matColumnDef","metodo"],["matColumnDef","origen"],["matColumnDef","estado"],["matColumnDef","comprobante"],["matColumnDef","motivo"],["mat-header-row","",4,"matHeaderRowDef"],["mat-row","",4,"matRowDef","matRowDefColumns"],["mat-header-cell",""],["mat-cell",""],["mat-button","",3,"click",4,"ngIf"],["mat-button","",3,"click"],["class","text-muted small",4,"ngIf"],["mat-header-row",""],["mat-row",""],["icono","receipt_long","titulo","A\xFAn no se han registrado pagos","mensaje","Cuando registres un pago, aparecer\xE1 aqu\xED."],[1,"text-center","p-4"],[1,"big-icon"],["mat-raised-button","","color","primary","routerLink","/usuario/seleccion"]],template:function(r,s){if(r&1&&(t(0,"div",2)(1,"h1",3),n(2,"Mi reserva"),e(),t(3,"p",4),n(4,"Estado de tu reserva, stands seleccionados y gesti\xF3n de pagos."),e(),p(5,jt,170,54,"ng-container",5)(6,$t,12,0,"ng-template",null,0,A),e()),r&2){let l=D(7);o(5),d("ngIf",s.reserva())("ngIfElse",l)}},dependencies:[W,J,Q,te,ee,xe,pe,le,ue,ce,de,fe,_e,ge,be,Ae,we,De,Be,ke,se,me,ie,re,st,mt,je,Xe,Ze,Le,Ue,it,Ke,Qe,tt,We,Je,nt,Ye,et,at,rt,Se,Ce,he,ye,Me,Ve,Fe,Re,Pe,Ee,Ne,$e,Ge,He,qe],styles:[".mt-2[_ngcontent-%COMP%]{margin-top:16px}.my-3[_ngcontent-%COMP%]{margin:16px 0}.reserva-header[_ngcontent-%COMP%]{display:flex;justify-content:space-between;align-items:center;gap:12px}.reserva-id[_ngcontent-%COMP%]{font-size:18px;font-weight:600;color:var(--filey-primary)}.text-muted[_ngcontent-%COMP%]{color:var(--filey-text-muted)}.small[_ngcontent-%COMP%]{font-size:12px}.grid-layout[_ngcontent-%COMP%]{display:grid;grid-template-columns:1.4fr 1fr;gap:24px;margin-top:16px}.progress-section[_ngcontent-%COMP%]{background:var(--filey-bg-soft);padding:16px;border-radius:8px}.progress-label[_ngcontent-%COMP%]{display:flex;justify-content:space-between;margin-bottom:8px;font-size:14px;color:var(--filey-text-muted)}.progress-marks[_ngcontent-%COMP%]{display:flex;justify-content:space-between;margin-top:8px;font-size:12px}.mark[_ngcontent-%COMP%]{color:#9ca3af}.mark.reached[_ngcontent-%COMP%]{color:var(--filey-success);font-weight:600}.fechas-grid[_ngcontent-%COMP%]{display:grid;grid-template-columns:1fr 1fr;gap:16px}.fecha-item[_ngcontent-%COMP%]{display:flex;gap:12px;align-items:flex-start;padding:12px;background:var(--filey-bg-soft);border-radius:4px}.fecha-item[_ngcontent-%COMP%]   mat-icon[_ngcontent-%COMP%]{color:var(--filey-primary)}.fecha-label[_ngcontent-%COMP%]{font-size:12px;color:var(--filey-text-muted);text-transform:uppercase}.fecha-value[_ngcontent-%COMP%]{font-weight:600;color:var(--filey-primary)}.fecha-value.warn[_ngcontent-%COMP%]{color:var(--filey-secondary)}.stand-item[_ngcontent-%COMP%]{display:flex;align-items:center;gap:12px;padding:12px;border-bottom:1px solid var(--filey-border)}.stand-item[_ngcontent-%COMP%]:last-child{border-bottom:none}.stand-item[_ngcontent-%COMP%]   .clave[_ngcontent-%COMP%]{font-size:20px;font-weight:700;color:var(--filey-primary);min-width:50px}.stand-item[_ngcontent-%COMP%]   .info[_ngcontent-%COMP%]{flex:1}.stand-item[_ngcontent-%COMP%]   .precio[_ngcontent-%COMP%]{font-weight:600;color:var(--filey-secondary)}.discount[_ngcontent-%COMP%]{color:var(--filey-success)}.big-icon[_ngcontent-%COMP%]{font-size:64px;width:64px;height:64px;color:var(--filey-text-muted)}.text-center[_ngcontent-%COMP%]{text-align:center}.p-4[_ngcontent-%COMP%]{padding:32px}.pagos-content[_ngcontent-%COMP%]{padding-top:16px}.datos-bancarios[_ngcontent-%COMP%]{display:grid;grid-template-columns:repeat(auto-fit,minmax(280px,1fr));gap:12px;background:var(--filey-bg-soft);padding:16px;border-radius:8px;margin-top:8px}.dato[_ngcontent-%COMP%]{display:flex;flex-direction:column;padding:8px 0}.dato[_ngcontent-%COMP%]   .lbl[_ngcontent-%COMP%]{font-size:12px;color:var(--filey-text-muted);text-transform:uppercase}.dato[_ngcontent-%COMP%]   .val[_ngcontent-%COMP%]{font-weight:600;color:var(--filey-primary);font-size:15px}.grid-2[_ngcontent-%COMP%]{display:grid;grid-template-columns:1fr 1fr;gap:16px}.form-pago[_ngcontent-%COMP%]{max-width:700px}.comprobante-upload[_ngcontent-%COMP%]{margin:16px 0}.comprobante-upload[_ngcontent-%COMP%]   .lbl[_ngcontent-%COMP%]{display:block;font-weight:600;margin-bottom:8px;color:var(--filey-primary)}@media(max-width:1024px){.grid-layout[_ngcontent-%COMP%], .grid-2[_ngcontent-%COMP%], .fechas-grid[_ngcontent-%COMP%]{grid-template-columns:1fr}}"]})};export{lt as MiReservaComponent};
