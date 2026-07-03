export interface Documento {
  id: string;
  tipo: 'comprobante_pago' | 'carta_representacion' | 'lista_titulos' | 'constancia_fiscal' | 'doc_abono' | 'otro';
  nombreArchivo: string;
  url: string;
  fechaCarga: Date;
  entidadTipo?: string;
  entidadId?: string;
}
