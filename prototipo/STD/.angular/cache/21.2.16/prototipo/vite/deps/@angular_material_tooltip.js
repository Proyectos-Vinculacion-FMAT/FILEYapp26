import {
  MAT_TOOLTIP_DEFAULT_OPTIONS,
  MAT_TOOLTIP_SCROLL_STRATEGY,
  MatTooltip,
  SCROLL_THROTTLE_MS,
  TOOLTIP_PANEL_CLASS,
  TooltipComponent,
  getMatTooltipInvalidPositionError
} from "./chunk-4AUMNOAK.js";
import {
  OverlayModule
} from "./chunk-6M5CXMNB.js";
import "./chunk-OF5MFU5S.js";
import "./chunk-WZ5T2WXV.js";
import "./chunk-VON75VBJ.js";
import "./chunk-PLJ2QXBA.js";
import {
  CdkScrollableModule
} from "./chunk-5SD5GUE3.js";
import "./chunk-6ZBOXUC5.js";
import "./chunk-GUGIMSVJ.js";
import {
  A11yModule
} from "./chunk-ZB7URSOK.js";
import "./chunk-XA6252L2.js";
import "./chunk-JVS2HK3M.js";
import "./chunk-UN652PWY.js";
import "./chunk-TBEOAFZM.js";
import "./chunk-OD7KUCHS.js";
import "./chunk-YBUR2BQ5.js";
import "./chunk-N4DOILP3.js";
import "./chunk-WSS4P3VF.js";
import {
  BidiModule
} from "./chunk-NJWZL2IW.js";
import "./chunk-SI62FSGI.js";
import "./chunk-MWV3NF3V.js";
import "./chunk-A5KFWV2Z.js";
import "./chunk-ZVJTVNVA.js";
import "./chunk-62GBKEMX.js";
import {
  NgModule,
  setClassMetadata,
  ɵɵdefineInjector,
  ɵɵdefineNgModule
} from "./chunk-T2GKPQEW.js";
import "./chunk-4YCCEXQQ.js";
import "./chunk-J46EEYGT.js";
import "./chunk-U7EDC2PH.js";

// node_modules/@angular/material/fesm2022/tooltip.mjs
var MatTooltipModule = class _MatTooltipModule {
  static ɵfac = function MatTooltipModule_Factory(__ngFactoryType__) {
    return new (__ngFactoryType__ || _MatTooltipModule)();
  };
  static ɵmod = ɵɵdefineNgModule({
    type: _MatTooltipModule,
    imports: [A11yModule, OverlayModule, MatTooltip, TooltipComponent],
    exports: [MatTooltip, TooltipComponent, BidiModule, CdkScrollableModule]
  });
  static ɵinj = ɵɵdefineInjector({
    imports: [A11yModule, OverlayModule, BidiModule, CdkScrollableModule]
  });
};
(() => {
  (typeof ngDevMode === "undefined" || ngDevMode) && setClassMetadata(MatTooltipModule, [{
    type: NgModule,
    args: [{
      imports: [A11yModule, OverlayModule, MatTooltip, TooltipComponent],
      exports: [MatTooltip, TooltipComponent, BidiModule, CdkScrollableModule]
    }]
  }], null, null);
})();
export {
  MAT_TOOLTIP_DEFAULT_OPTIONS,
  MAT_TOOLTIP_SCROLL_STRATEGY,
  MatTooltip,
  MatTooltipModule,
  SCROLL_THROTTLE_MS,
  TOOLTIP_PANEL_CLASS,
  TooltipComponent,
  getMatTooltipInvalidPositionError
};
//# sourceMappingURL=@angular_material_tooltip.js.map
