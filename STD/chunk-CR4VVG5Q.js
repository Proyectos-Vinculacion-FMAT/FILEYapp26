import{a as wt,c as Dt,d as Et,e as St,f as kt,g as It}from"./chunk-F3BOCA2C.js";import{a as Rt}from"./chunk-EEF6MIFP.js";import{a as Bt}from"./chunk-ZW3YOC3T.js";import{a as _t}from"./chunk-AHU4U46R.js";import{a as ft}from"./chunk-UTMHQX2P.js";import{a as K}from"./chunk-XYCEQMSS.js";import{a as Ft}from"./chunk-QAW7Y32V.js";import{F as vt,G as yt,J as Mt,L as xt,M as Ct,v as bt}from"./chunk-YFX3RNMQ.js";import{B as ht,b as mt,n as ct,q as dt,r as ut,u as pt,y as gt}from"./chunk-QMLWXKMV.js";import{a as At,b as Ot}from"./chunk-JF3SS6UH.js";import{D as it,E as at,G as ot,H as ge,N as he,T as rt,V as st,X as lt,Y as fe,Z as _e,a as Ze,c as Je,d as I,e as de,f as ue,g as et,o as tt,p as nt,s as pe}from"./chunk-4YXYQSCY.js";import{a as Pt}from"./chunk-73ALEGO2.js";import{a as Tt}from"./chunk-TSHVXL4N.js";import{a as q}from"./chunk-7YINBZDF.js";import{d as Ke,i as $e}from"./chunk-JUEAZOHP.js";import{g as We,h as qe,j as ce}from"./chunk-57DNE6ZE.js";import{$ as A,A as L,Aa as C,Ab as ze,B as Ce,Ba as Ie,Bb as Ne,Fb as p,G as we,Gb as s,Hb as l,Hc as W,Ib as E,Jb as le,Kb as Le,Kc as k,Mb as He,Nb as je,Pb as U,Q as H,Qb as Ve,R as re,Rb as u,S as De,Sb as Ye,Tb as h,Ub as F,Vb as v,Wb as Q,Xa as d,Xb as Xe,Y as Ee,Yb as y,Z as x,Zb as M,a as ae,ab as Re,b as xe,ba as a,bb as Te,bc as Ue,d as z,db as Pe,dc as S,ec as G,fb as Ae,fc as m,ga as _,gb as Oe,gc as me,h as N,ha as b,hc as Qe,ia as Se,ka as j,kb as g,la as V,lb as w,mb as D,o as oe,oa as Y,pa as ke,pb as Fe,pc as Ge,qb as se,rb as Be,ta as X,zb as O}from"./chunk-RGBEC4WX.js";var Ut=["*",[["mat-toolbar-row"]]],Qt=["*","mat-toolbar-row"],Gt=(()=>{class i{static \u0275fac=function(t){return new(t||i)};static \u0275dir=D({type:i,selectors:[["mat-toolbar-row"]],hostAttrs:[1,"mat-toolbar-row"],exportAs:["matToolbarRow"]})}return i})(),zt=(()=>{class i{_elementRef=a(C);_platform=a(et);_document=a(V);color;_toolbarRows;constructor(){}ngAfterViewInit(){this._platform.isBrowser&&(this._checkToolbarMixedModes(),this._toolbarRows.changes.subscribe(()=>this._checkToolbarMixedModes()))}_checkToolbarMixedModes(){this._toolbarRows.length}static \u0275fac=function(t){return new(t||i)};static \u0275cmp=g({type:i,selectors:[["mat-toolbar"]],contentQueries:function(t,n,o){if(t&1&&Q(o,Gt,5),t&2){let r;y(r=M())&&(n._toolbarRows=r)}},hostAttrs:[1,"mat-toolbar"],hostVars:6,hostBindings:function(t,n){t&2&&(G(n.color?"mat-"+n.color:""),S("mat-toolbar-multiple-rows",n._toolbarRows.length>0)("mat-toolbar-single-row",n._toolbarRows.length===0))},inputs:{color:"color"},exportAs:["matToolbar"],ngContentSelectors:Qt,decls:2,vars:0,template:function(t,n){t&1&&(F(Ut),v(0),v(1,1))},styles:[`.mat-toolbar {
  background: var(--mat-toolbar-container-background-color, var(--mat-sys-surface));
  color: var(--mat-toolbar-container-text-color, var(--mat-sys-on-surface));
}
.mat-toolbar, .mat-toolbar h1, .mat-toolbar h2, .mat-toolbar h3, .mat-toolbar h4, .mat-toolbar h5, .mat-toolbar h6 {
  font-family: var(--mat-toolbar-title-text-font, var(--mat-sys-title-large-font));
  font-size: var(--mat-toolbar-title-text-size, var(--mat-sys-title-large-size));
  line-height: var(--mat-toolbar-title-text-line-height, var(--mat-sys-title-large-line-height));
  font-weight: var(--mat-toolbar-title-text-weight, var(--mat-sys-title-large-weight));
  letter-spacing: var(--mat-toolbar-title-text-tracking, var(--mat-sys-title-large-tracking));
  margin: 0;
}
@media (forced-colors: active) {
  .mat-toolbar {
    outline: solid 1px;
  }
}
.mat-toolbar .mat-form-field-underline,
.mat-toolbar .mat-form-field-ripple,
.mat-toolbar .mat-focused .mat-form-field-ripple {
  background-color: currentColor;
}
.mat-toolbar .mat-form-field-label,
.mat-toolbar .mat-focused .mat-form-field-label,
.mat-toolbar .mat-select-value,
.mat-toolbar .mat-select-arrow,
.mat-toolbar .mat-form-field.mat-focused .mat-select-arrow {
  color: inherit;
}
.mat-toolbar .mat-input-element {
  caret-color: currentColor;
}
.mat-toolbar .mat-mdc-button-base.mat-mdc-button-base.mat-unthemed {
  --mat-button-text-label-text-color: var(--mat-toolbar-container-text-color, var(--mat-sys-on-surface));
  --mat-button-outlined-label-text-color: var(--mat-toolbar-container-text-color, var(--mat-sys-on-surface));
}

.mat-toolbar-row, .mat-toolbar-single-row {
  display: flex;
  box-sizing: border-box;
  padding: 0 16px;
  width: 100%;
  flex-direction: row;
  align-items: center;
  white-space: nowrap;
  height: var(--mat-toolbar-standard-height, 64px);
}
@media (max-width: 599px) {
  .mat-toolbar-row, .mat-toolbar-single-row {
    height: var(--mat-toolbar-mobile-height, 56px);
  }
}

.mat-toolbar-multiple-rows {
  display: flex;
  box-sizing: border-box;
  flex-direction: column;
  width: 100%;
  min-height: var(--mat-toolbar-standard-height, 64px);
}
@media (max-width: 599px) {
  .mat-toolbar-multiple-rows {
    min-height: var(--mat-toolbar-mobile-height, 56px);
  }
}
`],encapsulation:2,changeDetection:0})}return i})();var Nt=(()=>{class i{static \u0275fac=function(t){return new(t||i)};static \u0275mod=w({type:i});static \u0275inj=x({imports:[I]})}return i})();var en=["mat-menu-item",""],tn=[[["mat-icon"],["","matMenuItemIcon",""]],"*"],nn=["mat-icon, [matMenuItemIcon]","*"];function an(i,c){i&1&&(Se(),s(0,"svg",2),E(1,"polygon",3),l())}var on=["*"];function rn(i,c){if(i&1){let e=U();le(0,"div",0),Ye("click",function(){_(e);let n=h();return b(n.closed.emit("click"))})("animationstart",function(n){_(e);let o=h();return b(o._onAnimationStart(n.animationName))})("animationend",function(n){_(e);let o=h();return b(o._onAnimationDone(n.animationName))})("animationcancel",function(n){_(e);let o=h();return b(o._onAnimationDone(n.animationName))}),le(1,"div",1),v(2),Le()()}if(i&2){let e=h();G(e._classList),S("mat-menu-panel-animations-disabled",e._animationsDisabled)("mat-menu-panel-exit-animation",e._panelAnimationState==="void")("mat-menu-panel-animating",e._isAnimating()),Ve("id",e.panelId),O("aria-label",e.ariaLabel||null)("aria-labelledby",e.ariaLabelledby||null)("aria-describedby",e.ariaDescribedby||null)}}var ve=new A("MAT_MENU_PANEL"),B=(()=>{class i{_elementRef=a(C);_document=a(V);_focusMonitor=a(pe);_parentMenu=a(ve,{optional:!0});_changeDetectorRef=a(W);role="menuitem";disabled=!1;disableRipple=!1;_hovered=new N;_focused=new N;_highlighted=!1;_triggersSubmenu=!1;constructor(){a(Ze).load(st),this._parentMenu?.addItem?.(this)}focus(e,t){this._focusMonitor&&e?this._focusMonitor.focusVia(this._getHostElement(),e,t):this._getHostElement().focus(t),this._focused.next(this)}ngAfterViewInit(){this._focusMonitor&&this._focusMonitor.monitor(this._elementRef,!1)}ngOnDestroy(){this._focusMonitor&&this._focusMonitor.stopMonitoring(this._elementRef),this._parentMenu&&this._parentMenu.removeItem&&this._parentMenu.removeItem(this),this._hovered.complete(),this._focused.complete()}_getTabIndex(){return this.disabled?"-1":"0"}_getHostElement(){return this._elementRef.nativeElement}_checkDisabled(e){this.disabled&&(e.preventDefault(),e.stopPropagation())}_handleMouseEnter(){this._hovered.next(this)}getLabel(){let e=this._elementRef.nativeElement.cloneNode(!0),t=e.querySelectorAll("mat-icon, .material-icons");for(let n=0;n<t.length;n++)t[n].remove();return e.textContent?.trim()||""}_setHighlighted(e){this._highlighted=e,this._changeDetectorRef.markForCheck()}_setTriggersSubmenu(e){this._triggersSubmenu=e,this._changeDetectorRef.markForCheck()}_hasFocus(){return this._document&&this._document.activeElement===this._getHostElement()}static \u0275fac=function(t){return new(t||i)};static \u0275cmp=g({type:i,selectors:[["","mat-menu-item",""]],hostAttrs:[1,"mat-mdc-menu-item","mat-focus-indicator"],hostVars:8,hostBindings:function(t,n){t&1&&u("click",function(r){return n._checkDisabled(r)})("mouseenter",function(){return n._handleMouseEnter()}),t&2&&(O("role",n.role)("tabindex",n._getTabIndex())("aria-disabled",n.disabled)("disabled",n.disabled||null),S("mat-mdc-menu-item-highlighted",n._highlighted)("mat-mdc-menu-item-submenu-trigger",n._triggersSubmenu))},inputs:{role:"role",disabled:[2,"disabled","disabled",k],disableRipple:[2,"disableRipple","disableRipple",k]},exportAs:["matMenuItem"],attrs:en,ngContentSelectors:nn,decls:5,vars:3,consts:[[1,"mat-mdc-menu-item-text"],["matRipple","",1,"mat-mdc-menu-ripple",3,"matRippleDisabled","matRippleTrigger"],["viewBox","0 0 5 10","focusable","false","aria-hidden","true",1,"mat-mdc-menu-submenu-icon"],["points","0,0 5,5 0,10"]],template:function(t,n){t&1&&(F(tn),v(0),s(1,"span",0),v(2,1),l(),E(3,"div",1),ze(4,an,2,0,":svg:svg",2)),t&2&&(d(3),p("matRippleDisabled",n.disableRipple||n.disabled)("matRippleTrigger",n._getHostElement()),d(),Ne(n._triggersSubmenu?4:-1))},dependencies:[rt],encapsulation:2,changeDetection:0})}return i})();var sn=new A("MatMenuContent");var ln=new A("mat-menu-default-options",{providedIn:"root",factory:()=>({overlapTrigger:!1,xPosition:"after",yPosition:"below",backdropClass:"cdk-overlay-transparent-backdrop"})}),be="_mat-menu-enter",Z="_mat-menu-exit",T=(()=>{class i{_elementRef=a(C);_changeDetectorRef=a(W);_injector=a(j);_keyManager;_xPosition;_yPosition;_firstItemFocusRef;_exitFallbackTimeout;_animationsDisabled=he();_allItems;_directDescendantItems=new Ie;_classList={};_panelAnimationState="void";_animationDone=new N;_isAnimating=X(!1);parentMenu;direction;overlayPanelClass;backdropClass;ariaLabel;ariaLabelledby;ariaDescribedby;get xPosition(){return this._xPosition}set xPosition(e){this._xPosition=e,this.setPositionClasses()}get yPosition(){return this._yPosition}set yPosition(e){this._yPosition=e,this.setPositionClasses()}templateRef;items;lazyContent;overlapTrigger=!1;hasBackdrop;set panelClass(e){let t=this._previousPanelClass,n=ae({},this._classList);t&&t.length&&t.split(" ").forEach(o=>{n[o]=!1}),this._previousPanelClass=e,e&&e.length&&(e.split(" ").forEach(o=>{n[o]=!0}),this._elementRef.nativeElement.className=""),this._classList=n}_previousPanelClass;get classList(){return this.panelClass}set classList(e){this.panelClass=e}closed=new Y;close=this.closed;panelId=a(ge).getId("mat-menu-panel-");constructor(){let e=a(ln);this.overlayPanelClass=e.overlayPanelClass||"",this._xPosition=e.xPosition,this._yPosition=e.yPosition,this.backdropClass=e.backdropClass,this.overlapTrigger=e.overlapTrigger,this.hasBackdrop=e.hasBackdrop}ngOnInit(){this.setPositionClasses()}ngAfterContentInit(){this._updateDirectDescendants(),this._keyManager=new ot(this._directDescendantItems).withWrap().withTypeAhead().withHomeAndEnd(),this._keyManager.tabOut.subscribe(()=>this.closed.emit("tab")),this._directDescendantItems.changes.pipe(H(this._directDescendantItems),re(e=>L(...e.map(t=>t._focused)))).subscribe(e=>this._keyManager.updateActiveItem(e)),this._directDescendantItems.changes.subscribe(e=>{let t=this._keyManager;if(this._panelAnimationState==="enter"&&t.activeItem?._hasFocus()){let n=e.toArray(),o=Math.max(0,Math.min(n.length-1,t.activeItemIndex||0));n[o]&&!n[o].disabled?t.setActiveItem(o):t.setNextItemActive()}})}ngOnDestroy(){this._keyManager?.destroy(),this._directDescendantItems.destroy(),this.closed.complete(),this._firstItemFocusRef?.destroy(),clearTimeout(this._exitFallbackTimeout)}_hovered(){return this._directDescendantItems.changes.pipe(H(this._directDescendantItems),re(t=>L(...t.map(n=>n._hovered))))}addItem(e){}removeItem(e){}_handleKeydown(e){let t=e.keyCode,n=this._keyManager;switch(t){case 27:at(e)||(e.preventDefault(),this.closed.emit("keydown"));break;case 37:this.parentMenu&&this.direction==="ltr"&&this.closed.emit("keydown");break;case 39:this.parentMenu&&this.direction==="rtl"&&this.closed.emit("keydown");break;default:(t===38||t===40)&&n.setFocusOrigin("keyboard"),n.onKeydown(e);return}}focusFirstItem(e="program"){this._firstItemFocusRef?.destroy(),this._firstItemFocusRef=Re(()=>{let t=this._resolvePanel();if(!t||!t.contains(document.activeElement)){let n=this._keyManager;n.setFocusOrigin(e).setFirstItemActive(),!n.activeItem&&t&&t.focus()}},{injector:this._injector})}resetActiveItem(){this._keyManager.setActiveItem(-1)}setElevation(e){}setPositionClasses(e=this.xPosition,t=this.yPosition){this._classList=xe(ae({},this._classList),{"mat-menu-before":e==="before","mat-menu-after":e==="after","mat-menu-above":t==="above","mat-menu-below":t==="below"}),this._changeDetectorRef.markForCheck()}_onAnimationDone(e){let t=e===Z;(t||e===be)&&(t&&(clearTimeout(this._exitFallbackTimeout),this._exitFallbackTimeout=void 0),this._animationDone.next(t?"void":"enter"),this._isAnimating.set(!1))}_onAnimationStart(e){(e===be||e===Z)&&this._isAnimating.set(!0)}_setIsOpen(e){if(this._panelAnimationState=e?"enter":"void",e){if(this._keyManager.activeItemIndex===0){let t=this._resolvePanel();t&&(t.scrollTop=0)}}else this._animationsDisabled||(this._exitFallbackTimeout=setTimeout(()=>this._onAnimationDone(Z),200));this._animationsDisabled&&setTimeout(()=>{this._onAnimationDone(e?be:Z)}),this._changeDetectorRef.markForCheck()}_updateDirectDescendants(){this._allItems.changes.pipe(H(this._allItems)).subscribe(e=>{this._directDescendantItems.reset(e.filter(t=>t._parentMenu===this)),this._directDescendantItems.notifyOnChanges()})}_resolvePanel(){let e=null;return this._directDescendantItems.length&&(e=this._directDescendantItems.first._getHostElement().closest('[role="menu"]')),e}static \u0275fac=function(t){return new(t||i)};static \u0275cmp=g({type:i,selectors:[["mat-menu"]],contentQueries:function(t,n,o){if(t&1&&Q(o,sn,5)(o,B,5)(o,B,4),t&2){let r;y(r=M())&&(n.lazyContent=r.first),y(r=M())&&(n._allItems=r),y(r=M())&&(n.items=r)}},viewQuery:function(t,n){if(t&1&&Xe(Te,5),t&2){let o;y(o=M())&&(n.templateRef=o.first)}},hostVars:3,hostBindings:function(t,n){t&2&&O("aria-label",null)("aria-labelledby",null)("aria-describedby",null)},inputs:{backdropClass:"backdropClass",ariaLabel:[0,"aria-label","ariaLabel"],ariaLabelledby:[0,"aria-labelledby","ariaLabelledby"],ariaDescribedby:[0,"aria-describedby","ariaDescribedby"],xPosition:"xPosition",yPosition:"yPosition",overlapTrigger:[2,"overlapTrigger","overlapTrigger",k],hasBackdrop:[2,"hasBackdrop","hasBackdrop",e=>e==null?null:k(e)],panelClass:[0,"class","panelClass"],classList:"classList"},outputs:{closed:"closed",close:"close"},exportAs:["matMenu"],features:[Ge([{provide:ve,useExisting:i}])],ngContentSelectors:on,decls:1,vars:0,consts:[["tabindex","-1","role","menu",1,"mat-mdc-menu-panel",3,"click","animationstart","animationend","animationcancel","id"],[1,"mat-mdc-menu-content"]],template:function(t,n){t&1&&(F(),Be(0,rn,3,12,"ng-template"))},styles:[`mat-menu {
  display: none;
}

.mat-mdc-menu-content {
  margin: 0;
  padding: 8px 0;
  outline: 0;
}
.mat-mdc-menu-content,
.mat-mdc-menu-content .mat-mdc-menu-item .mat-mdc-menu-item-text {
  -moz-osx-font-smoothing: grayscale;
  -webkit-font-smoothing: antialiased;
  flex: 1;
  white-space: normal;
  font-family: var(--mat-menu-item-label-text-font, var(--mat-sys-label-large-font));
  line-height: var(--mat-menu-item-label-text-line-height, var(--mat-sys-label-large-line-height));
  font-size: var(--mat-menu-item-label-text-size, var(--mat-sys-label-large-size));
  letter-spacing: var(--mat-menu-item-label-text-tracking, var(--mat-sys-label-large-tracking));
  font-weight: var(--mat-menu-item-label-text-weight, var(--mat-sys-label-large-weight));
}

@keyframes _mat-menu-enter {
  from {
    opacity: 0;
    transform: scale(0.8);
  }
  to {
    opacity: 1;
    transform: none;
  }
}
@keyframes _mat-menu-exit {
  from {
    opacity: 1;
  }
  to {
    opacity: 0;
  }
}
.mat-mdc-menu-panel {
  min-width: 112px;
  max-width: 280px;
  overflow: auto;
  box-sizing: border-box;
  outline: 0;
  animation: _mat-menu-enter 120ms cubic-bezier(0, 0, 0.2, 1);
  border-radius: var(--mat-menu-container-shape, var(--mat-sys-corner-extra-small));
  background-color: var(--mat-menu-container-color, var(--mat-sys-surface-container));
  box-shadow: var(--mat-menu-container-elevation-shadow, 0px 3px 1px -2px rgba(0, 0, 0, 0.2), 0px 2px 2px 0px rgba(0, 0, 0, 0.14), 0px 1px 5px 0px rgba(0, 0, 0, 0.12));
  will-change: transform, opacity;
}
.mat-mdc-menu-panel.mat-menu-panel-exit-animation {
  animation: _mat-menu-exit 100ms 25ms linear forwards;
}
.mat-mdc-menu-panel.mat-menu-panel-animations-disabled {
  animation: none;
}
.mat-mdc-menu-panel.mat-menu-panel-animating {
  pointer-events: none;
}
.mat-mdc-menu-panel.mat-menu-panel-animating:has(.mat-mdc-menu-content:empty) {
  display: none;
}
@media (forced-colors: active) {
  .mat-mdc-menu-panel {
    outline: solid 1px;
  }
}
.mat-mdc-menu-panel .mat-divider {
  border-top-color: var(--mat-menu-divider-color, var(--mat-sys-surface-variant));
  margin-bottom: var(--mat-menu-divider-bottom-spacing, 8px);
  margin-top: var(--mat-menu-divider-top-spacing, 8px);
}

.mat-mdc-menu-item {
  display: flex;
  position: relative;
  align-items: center;
  justify-content: flex-start;
  overflow: hidden;
  padding: 0;
  cursor: pointer;
  width: 100%;
  text-align: left;
  box-sizing: border-box;
  color: inherit;
  font-size: inherit;
  background: none;
  text-decoration: none;
  margin: 0;
  min-height: 48px;
  padding-left: var(--mat-menu-item-leading-spacing, 12px);
  padding-right: var(--mat-menu-item-trailing-spacing, 12px);
  -webkit-user-select: none;
  user-select: none;
  cursor: pointer;
  outline: none;
  border: none;
  -webkit-tap-highlight-color: transparent;
}
.mat-mdc-menu-item::-moz-focus-inner {
  border: 0;
}
[dir=rtl] .mat-mdc-menu-item {
  padding-left: var(--mat-menu-item-trailing-spacing, 12px);
  padding-right: var(--mat-menu-item-leading-spacing, 12px);
}
.mat-mdc-menu-item:has(.material-icons, mat-icon, [matButtonIcon]) {
  padding-left: var(--mat-menu-item-with-icon-leading-spacing, 12px);
  padding-right: var(--mat-menu-item-with-icon-trailing-spacing, 12px);
}
[dir=rtl] .mat-mdc-menu-item:has(.material-icons, mat-icon, [matButtonIcon]) {
  padding-left: var(--mat-menu-item-with-icon-trailing-spacing, 12px);
  padding-right: var(--mat-menu-item-with-icon-leading-spacing, 12px);
}
.mat-mdc-menu-item, .mat-mdc-menu-item:visited, .mat-mdc-menu-item:link {
  color: var(--mat-menu-item-label-text-color, var(--mat-sys-on-surface));
}
.mat-mdc-menu-item .mat-icon-no-color,
.mat-mdc-menu-item .mat-mdc-menu-submenu-icon {
  color: var(--mat-menu-item-icon-color, var(--mat-sys-on-surface-variant));
}
.mat-mdc-menu-item[disabled] {
  cursor: default;
  opacity: 0.38;
}
.mat-mdc-menu-item[disabled]::after {
  display: block;
  position: absolute;
  content: "";
  top: 0;
  left: 0;
  bottom: 0;
  right: 0;
}
.mat-mdc-menu-item:focus {
  outline: 0;
}
.mat-mdc-menu-item .mat-icon {
  flex-shrink: 0;
  margin-right: var(--mat-menu-item-spacing, 12px);
  height: var(--mat-menu-item-icon-size, 24px);
  width: var(--mat-menu-item-icon-size, 24px);
}
[dir=rtl] .mat-mdc-menu-item {
  text-align: right;
}
[dir=rtl] .mat-mdc-menu-item .mat-icon {
  margin-right: 0;
  margin-left: var(--mat-menu-item-spacing, 12px);
}
.mat-mdc-menu-item:not([disabled]):hover {
  background-color: var(--mat-menu-item-hover-state-layer-color, color-mix(in srgb, var(--mat-sys-on-surface) calc(var(--mat-sys-hover-state-layer-opacity) * 100%), transparent));
}
.mat-mdc-menu-item:not([disabled]).cdk-program-focused, .mat-mdc-menu-item:not([disabled]).cdk-keyboard-focused, .mat-mdc-menu-item:not([disabled]).mat-mdc-menu-item-highlighted {
  background-color: var(--mat-menu-item-focus-state-layer-color, color-mix(in srgb, var(--mat-sys-on-surface) calc(var(--mat-sys-focus-state-layer-opacity) * 100%), transparent));
}
@media (forced-colors: active) {
  .mat-mdc-menu-item {
    margin-top: 1px;
  }
}

.mat-mdc-menu-submenu-icon {
  width: var(--mat-menu-item-icon-size, 24px);
  height: 10px;
  fill: currentColor;
  padding-left: var(--mat-menu-item-spacing, 12px);
}
[dir=rtl] .mat-mdc-menu-submenu-icon {
  padding-right: var(--mat-menu-item-spacing, 12px);
  padding-left: 0;
}
[dir=rtl] .mat-mdc-menu-submenu-icon polygon {
  transform: scaleX(-1);
  transform-origin: center;
}
@media (forced-colors: active) {
  .mat-mdc-menu-submenu-icon {
    fill: CanvasText;
  }
}

.mat-mdc-menu-item .mat-mdc-menu-ripple {
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  position: absolute;
  pointer-events: none;
}
`],encapsulation:2,changeDetection:0})}return i})(),mn=new A("mat-menu-scroll-strategy",{providedIn:"root",factory:()=>{let i=a(j);return()=>dt(i)}});var R=new WeakMap,cn=(()=>{class i{_canHaveBackdrop;_element=a(C);_viewContainerRef=a(Oe);_menuItemInstance=a(B,{optional:!0,self:!0});_dir=a(Je,{optional:!0});_focusMonitor=a(pe);_ngZone=a(ke);_injector=a(j);_scrollStrategy=a(mn);_changeDetectorRef=a(W);_animationsDisabled=he();_portal;_overlayRef=null;_menuOpen=!1;_closingActionsSubscription=z.EMPTY;_menuCloseSubscription=z.EMPTY;_pendingRemoval;_parentMaterialMenu;_parentInnerPadding;_openedBy=void 0;get _menu(){return this._menuInternal}set _menu(e){e!==this._menuInternal&&(this._menuInternal=e,this._menuCloseSubscription.unsubscribe(),e&&(this._parentMaterialMenu,this._menuCloseSubscription=e.close.subscribe(t=>{this._destroyMenu(t),(t==="click"||t==="tab")&&this._parentMaterialMenu&&this._parentMaterialMenu.closed.emit(t)})),this._menuItemInstance?._setTriggersSubmenu(this._triggersSubmenu()))}_menuInternal=null;constructor(e){this._canHaveBackdrop=e;let t=a(ve,{optional:!0});this._parentMaterialMenu=t instanceof T?t:void 0}ngOnDestroy(){this._menu&&this._ownsMenu(this._menu)&&R.delete(this._menu),this._pendingRemoval?.unsubscribe(),this._menuCloseSubscription.unsubscribe(),this._closingActionsSubscription.unsubscribe(),this._overlayRef&&(this._overlayRef.dispose(),this._overlayRef=null)}get menuOpen(){return this._menuOpen}get dir(){return this._dir&&this._dir.value==="rtl"?"rtl":"ltr"}_triggersSubmenu(){return!!(this._menuItemInstance&&this._parentMaterialMenu&&this._menu)}_closeMenu(){this._menu?.close.emit()}_openMenu(e){if(this._triggerIsAriaDisabled())return;let t=this._menu;if(this._menuOpen||!t)return;this._pendingRemoval?.unsubscribe();let n=R.get(t);R.set(t,this),n&&n!==this&&n._closeMenu();let o=this._createOverlay(t),r=o.getConfig(),f=r.positionStrategy;this._setPosition(t,f),this._canHaveBackdrop?r.hasBackdrop=t.hasBackdrop==null?!this._triggersSubmenu():t.hasBackdrop:r.hasBackdrop=t.hasBackdrop??!1,o.hasAttached()||(o.attach(this._getPortal(t)),t.lazyContent?.attach(this.menuData)),this._closingActionsSubscription=this._menuClosingActions().subscribe(()=>this._closeMenu()),t.parentMenu=this._triggersSubmenu()?this._parentMaterialMenu:void 0,t.direction=this.dir,e&&t.focusFirstItem(this._openedBy||"program"),this._setIsMenuOpen(!0),t instanceof T&&(t._setIsOpen(!0),t._directDescendantItems.changes.pipe(De(t.close)).subscribe(()=>{f.withLockedPosition(!1).reapplyLastPosition(),f.withLockedPosition(!0)}))}focus(e,t){this._focusMonitor&&e?this._focusMonitor.focusVia(this._element,e,t):this._element.nativeElement.focus(t)}_destroyMenu(e){let t=this._overlayRef,n=this._menu;!t||!this.menuOpen||(this._closingActionsSubscription.unsubscribe(),this._pendingRemoval?.unsubscribe(),n instanceof T&&this._ownsMenu(n)?(this._pendingRemoval=n._animationDone.pipe(we(1)).subscribe(()=>{t.detach(),R.has(n)||n.lazyContent?.detach()}),n._setIsOpen(!1)):(t.detach(),n?.lazyContent?.detach()),n&&this._ownsMenu(n)&&R.delete(n),this.restoreFocus&&(e==="keydown"||!this._openedBy||!this._triggersSubmenu())&&this.focus(this._openedBy),this._openedBy=void 0,this._setIsMenuOpen(!1))}_setIsMenuOpen(e){e!==this._menuOpen&&(this._menuOpen=e,this._menuOpen?this.menuOpened.emit():this.menuClosed.emit(),this._triggersSubmenu()&&this._menuItemInstance._setHighlighted(e),this._changeDetectorRef.markForCheck())}_createOverlay(e){if(!this._overlayRef){let t=this._getOverlayConfig(e);this._subscribeToPositions(e,t.positionStrategy),this._overlayRef=gt(this._injector,t),this._overlayRef.keydownEvents().subscribe(n=>{this._menu instanceof T&&this._menu._handleKeydown(n)})}return this._overlayRef}_getOverlayConfig(e){return new ut({positionStrategy:pt(this._injector,this._getOverlayOrigin()).withLockedPosition().withGrowAfterOpen().withTransformOriginOn(".mat-menu-panel, .mat-mdc-menu-panel"),backdropClass:e.backdropClass||"cdk-overlay-transparent-backdrop",panelClass:e.overlayPanelClass,scrollStrategy:this._scrollStrategy(),direction:this._dir||"ltr",disableAnimations:this._animationsDisabled})}_subscribeToPositions(e,t){e.setPositionClasses&&t.positionChanges.subscribe(n=>{this._ngZone.run(()=>{let o=n.connectionPair.overlayX==="start"?"after":"before",r=n.connectionPair.overlayY==="top"?"below":"above";e.setPositionClasses(o,r)})})}_setPosition(e,t){let[n,o]=e.xPosition==="before"?["end","start"]:["start","end"],[r,f]=e.yPosition==="above"?["bottom","top"]:["top","bottom"],[ee,te]=[r,f],[ne,ie]=[n,o],P=0;if(this._triggersSubmenu()){if(ie=n=e.xPosition==="before"?"start":"end",o=ne=n==="end"?"start":"end",this._parentMaterialMenu){if(this._parentInnerPadding==null){let Me=this._parentMaterialMenu.items.first;this._parentInnerPadding=Me?Me._getHostElement().offsetTop:0}P=r==="bottom"?this._parentInnerPadding:-this._parentInnerPadding}}else e.overlapTrigger||(ee=r==="top"?"bottom":"top",te=f==="top"?"bottom":"top");t.withPositions([{originX:n,originY:ee,overlayX:ne,overlayY:r,offsetY:P},{originX:o,originY:ee,overlayX:ie,overlayY:r,offsetY:P},{originX:n,originY:te,overlayX:ne,overlayY:f,offsetY:-P},{originX:o,originY:te,overlayX:ie,overlayY:f,offsetY:-P}])}_menuClosingActions(){let e=this._getOutsideClickStream(this._overlayRef),t=this._overlayRef.detachments(),n=this._parentMaterialMenu?this._parentMaterialMenu.closed:oe(),o=this._parentMaterialMenu?this._parentMaterialMenu._hovered().pipe(Ce(r=>this._menuOpen&&r!==this._menuItemInstance)):oe();return L(e,n,o,t)}_getPortal(e){return(!this._portal||this._portal.templateRef!==e.templateRef)&&(this._portal=new mt(e.templateRef,this._viewContainerRef)),this._portal}_ownsMenu(e){return R.get(e)===this}_triggerIsAriaDisabled(){return k(this._element.nativeElement.getAttribute("aria-disabled"))}static \u0275fac=function(t){Ae()};static \u0275dir=D({type:i})}return i})(),jt=(()=>{class i extends cn{_cleanupTouchstart;_hoverSubscription=z.EMPTY;get _deprecatedMatMenuTriggerFor(){return this.menu}set _deprecatedMatMenuTriggerFor(e){this.menu=e}get menu(){return this._menu}set menu(e){this._menu=e}menuData;restoreFocus=!0;menuOpened=new Y;onMenuOpen=this.menuOpened;menuClosed=new Y;onMenuClose=this.menuClosed;constructor(){super(!0);let e=a(Pe);this._cleanupTouchstart=e.listen(this._element.nativeElement,"touchstart",t=>{nt(t)||(this._openedBy="touch")},{passive:!0})}triggersSubmenu(){return super._triggersSubmenu()}toggleMenu(){return this.menuOpen?this.closeMenu():this.openMenu()}openMenu(){this._openMenu(!0)}closeMenu(){this._closeMenu()}updatePosition(){this._overlayRef?.updatePosition()}ngAfterContentInit(){this._handleHover()}ngOnDestroy(){super.ngOnDestroy(),this._cleanupTouchstart(),this._hoverSubscription.unsubscribe()}_getOverlayOrigin(){return this._element}_getOutsideClickStream(e){return e.backdropClick()}_handleMousedown(e){tt(e)||(this._openedBy=e.button===0?"mouse":void 0,this.triggersSubmenu()&&e.preventDefault())}_handleKeydown(e){let t=e.keyCode;(t===13||t===32)&&(this._openedBy="keyboard"),this.triggersSubmenu()&&(t===39&&this.dir==="ltr"||t===37&&this.dir==="rtl")&&(this._openedBy="keyboard",this.openMenu())}_handleClick(e){this.triggersSubmenu()?(e.stopPropagation(),this.openMenu()):this.toggleMenu()}_handleHover(){this.triggersSubmenu()&&this._parentMaterialMenu&&(this._hoverSubscription=this._parentMaterialMenu._hovered().subscribe(e=>{e===this._menuItemInstance&&!e.disabled&&this._parentMaterialMenu?._panelAnimationState!=="void"&&(this._openedBy="mouse",this._openMenu(!1))}))}static \u0275fac=function(t){return new(t||i)};static \u0275dir=D({type:i,selectors:[["","mat-menu-trigger-for",""],["","matMenuTriggerFor",""]],hostAttrs:[1,"mat-mdc-menu-trigger"],hostVars:3,hostBindings:function(t,n){t&1&&u("click",function(r){return n._handleClick(r)})("mousedown",function(r){return n._handleMousedown(r)})("keydown",function(r){return n._handleKeydown(r)}),t&2&&O("aria-haspopup",n.menu?"menu":null)("aria-expanded",n.menuOpen)("aria-controls",n.menuOpen?n.menu==null?null:n.menu.panelId:null)},inputs:{_deprecatedMatMenuTriggerFor:[0,"mat-menu-trigger-for","_deprecatedMatMenuTriggerFor"],menu:[0,"matMenuTriggerFor","menu"],menuData:[0,"matMenuTriggerData","menuData"],restoreFocus:[0,"matMenuTriggerRestoreFocus","restoreFocus"]},outputs:{menuOpened:"menuOpened",onMenuOpen:"onMenuOpen",menuClosed:"menuClosed",onMenuClose:"onMenuClose"},exportAs:["matMenuTrigger"],features:[Fe]})}return i})();var Vt=(()=>{class i{static \u0275fac=function(t){return new(t||i)};static \u0275mod=w({type:i});static \u0275inj=x({imports:[lt,ht,I,ct]})}return i})();var Yt=(()=>{class i{static \u0275fac=function(t){return new(t||i)};static \u0275mod=w({type:i});static \u0275inj=x({imports:[it,I]})}return i})();var J=class i{aplicacionService=a(K);reservaService=a(Ot);movimientoService=a(Ft);carritoService=a(At);standService=a(Pt);parametrosService=a(Tt);authService=a(q);reiniciarDemo(){this.aplicacionService.resetear(),this.reservaService.resetear(),this.movimientoService.resetear(),this.standService.resetear(),this.parametrosService.resetear(),this.carritoService.limpiar(),this.authService.setRol("usuario"),this.authService.setEditorialActual("ED-005")}reiniciarYRecargar(){this.reiniciarDemo(),window.location.reload()}static \u0275fac=function(e){return new(e||i)};static \u0275prov=Ee({token:i,factory:i.\u0275fac,providedIn:"root"})};function un(i,c){if(i&1&&(s(0,"mat-option",16),m(1),l()),i&2){let e=c.$implicit;p("value",e.id),d(),Qe(" ",e.nombre," ")}}function pn(i,c){if(i&1){let e=U();He(0),s(1,"div",11)(2,"mat-icon",12),m(3,"account_circle"),l(),s(4,"mat-form-field",13)(5,"mat-select",14),u("selectionChange",function(n){_(e);let o=h();return b(o.cambiarEditorial(n.value))}),se(6,un,2,2,"mat-option",15),l()()(),je()}if(i&2){let e=h();d(5),p("value",e.editorialActualId()),d(),p("ngForOf",e.todasEditoriales)}}var ye=class i{ref=a(wt);cancelar(){this.ref.close(!1)}confirmar(){this.ref.close(!0)}static \u0275fac=function(e){return new(e||i)};static \u0275cmp=g({type:i,selectors:[["app-reset-confirm-dialog"]],decls:23,vars:0,consts:[["mat-dialog-title",""],[1,"warn-icon"],[1,"text-muted"],["align","end"],["mat-button","",3,"click"],["mat-raised-button","","color","warn",3,"click"]],template:function(e,t){e&1&&(s(0,"h2",0)(1,"mat-icon",1),m(2,"restart_alt"),l(),m(3," \xBFReiniciar el demo? "),l(),s(4,"mat-dialog-content")(5,"p"),m(6,"Esto restablecer\xE1 todo el estado del prototipo a sus valores iniciales:"),l(),s(7,"ul")(8,"li"),m(9,"Aplicaciones, reservas, pagos y movimientos vuelven a los datos mock"),l(),s(10,"li"),m(11,"El carrito de selecci\xF3n se vac\xEDa"),l(),s(12,"li"),m(13,'El rol vuelve a "Usuario" (Editorial Sureste Nueva)'),l()(),s(14,"p",2),m(15,"Esta acci\xF3n es \xFAtil entre demos para empezar desde cero."),l()(),s(16,"mat-dialog-actions",3)(17,"button",4),u("click",function(){return t.cancelar()}),m(18,"Cancelar"),l(),s(19,"button",5),u("click",function(){return t.confirmar()}),s(20,"mat-icon"),m(21,"refresh"),l(),m(22," S\xED, reiniciar "),l()())},dependencies:[ce,It,Et,kt,St,_e,fe,ue,de],styles:[".warn-icon[_ngcontent-%COMP%]{color:var(--filey-secondary);vertical-align:middle;margin-right:8px}ul[_ngcontent-%COMP%]{padding-left:20px;color:var(--filey-text-muted)}li[_ngcontent-%COMP%]{margin-bottom:4px}.text-muted[_ngcontent-%COMP%]{color:var(--filey-text-muted)}"]})},Xt=class i{authService=a(q);editorialService=a(Rt);resetService=a(J);aplicacionService=a(K);faseService=a(Bt);router=a(Ke);dialog=a(Dt);rolActual=this.authService.rol;editorialActualId=X(this.authService.editorialActual);todasEditoriales=this.editorialService.editoriales;constructor(){this.authService.editorialActual$.subscribe(c=>this.editorialActualId.set(c))}cambiarEditorial(c){if(c!==this.authService.editorialActual&&(this.authService.setEditorialActual(c),this.faseService.refrescar(),this.rolActual==="usuario")){let e=this.faseService.faseActual(),n={aplicacion:"/usuario/aplicacion",seleccion:"/usuario/seleccion",confirmar:"/usuario/confirmar",reserva:"/usuario/mi-reserva"}[e];n&&this.router.url!==n?this.router.navigate([n],{replaceUrl:!0}):this.router.navigate(["/usuario/aplicacion"])}}irAInicio(){this.rolActual==="usuario"?this.router.navigate(["/usuario/aplicacion"]):this.router.navigate(["/admin/aplicaciones"])}cambiarRol(c){this.authService.setRol(c),c==="usuario"?this.router.navigate(["/usuario/aplicacion"]):this.router.navigate(["/admin/aplicaciones"])}reiniciarDemo(){this.dialog.open(ye).afterClosed().subscribe(e=>{e&&this.resetService.reiniciarYRecargar()})}static \u0275fac=function(e){return new(e||i)};static \u0275cmp=g({type:i,selectors:[["app-navbar"]],decls:29,vars:6,consts:[["menuRol","matMenu"],["color","primary",1,"navbar"],["role","button","tabindex","0","aria-label","Ir al inicio",1,"logo",3,"click"],["src","assets/filey-logotipo.svg","alt","FILEY",1,"logo-img"],[1,"spacer"],[4,"ngIf"],["mat-button","","matTooltip","Reiniciar el estado del prototipo a los valores iniciales",1,"reset-btn",3,"click"],[1,"reset-label"],["mat-button","",1,"role-btn",3,"matMenuTriggerFor"],[1,"role-label"],["mat-menu-item","",3,"click","disabled"],[1,"editorial-selector"],[1,"editorial-icon"],["appearance","outline","subscriptSizing","dynamic",1,"editorial-field"],[3,"selectionChange","value"],[3,"value",4,"ngFor","ngForOf"],[3,"value"]],template:function(e,t){if(e&1&&(s(0,"mat-toolbar",1)(1,"span",2),u("click",function(){return t.irAInicio()}),E(2,"img",3),l(),E(3,"span",4),se(4,pn,7,2,"ng-container",5),s(5,"button",6),u("click",function(){return t.reiniciarDemo()}),s(6,"mat-icon"),m(7,"restart_alt"),l(),s(8,"span",7),m(9,"Reiniciar"),l()(),s(10,"button",8)(11,"mat-icon"),m(12),l(),s(13,"span",9),m(14),l(),s(15,"mat-icon"),m(16,"arrow_drop_down"),l()(),s(17,"mat-menu",null,0)(19,"button",10),u("click",function(){return t.cambiarRol("usuario")}),s(20,"mat-icon"),m(21,"person"),l(),s(22,"span"),m(23,"Usuario"),l()(),s(24,"button",10),u("click",function(){return t.cambiarRol("administrador")}),s(25,"mat-icon"),m(26,"admin_panel_settings"),l(),s(27,"span"),m(28,"Administrador"),l()()()()),e&2){let n=Ue(18);d(4),p("ngIf",t.rolActual==="usuario"),d(6),p("matMenuTriggerFor",n),d(2),me(t.rolActual==="usuario"?"person":"admin_panel_settings"),d(2),me(t.rolActual==="usuario"?"Usuario":"Administrador"),d(5),p("disabled",t.rolActual==="usuario"),d(5),p("disabled",t.rolActual==="administrador")}},dependencies:[ce,We,qe,$e,bt,Nt,zt,_e,fe,ue,de,Vt,T,B,jt,Yt,_t,ft,Ct,vt,xt,yt,Mt],styles:[".navbar[_ngcontent-%COMP%]{box-shadow:0 2px 4px #0000001a;position:sticky;top:0;z-index:1000;gap:8px}.logo[_ngcontent-%COMP%]{display:flex;align-items:center;cursor:pointer}.logo-img[_ngcontent-%COMP%]{height:34px;width:auto;display:block;filter:brightness(0) invert(1)}.editorial-selector[_ngcontent-%COMP%]{display:flex;align-items:center;gap:6px;margin-right:4px}.editorial-icon[_ngcontent-%COMP%]{color:#fffc}.editorial-field[_ngcontent-%COMP%]{width:200px}.editorial-field[_ngcontent-%COMP%]     .mat-mdc-form-field-subscript-wrapper{display:none}.editorial-field[_ngcontent-%COMP%]     .mat-mdc-text-field-wrapper{background:#ffffff26;border-radius:4px}.editorial-field[_ngcontent-%COMP%]     .mdc-text-field--outlined .mdc-notched-outline>*{border-color:#fff6}.editorial-field[_ngcontent-%COMP%]     .mat-mdc-select-value, .editorial-field[_ngcontent-%COMP%]     .mat-mdc-select-arrow{color:#fff!important}.role-btn[_ngcontent-%COMP%]{display:flex;align-items:center;gap:4px}.role-label[_ngcontent-%COMP%]{margin:0 4px}.reset-btn[_ngcontent-%COMP%]{margin-right:4px;border:1px solid rgba(255,255,255,.3)}@media(max-width:900px){.editorial-field[_ngcontent-%COMP%]{width:140px}.reset-label[_ngcontent-%COMP%], .role-label[_ngcontent-%COMP%]{display:none}}@media(max-width:600px){.editorial-selector[_ngcontent-%COMP%]{display:none}}"]})};export{Nt as a,Xt as b};
