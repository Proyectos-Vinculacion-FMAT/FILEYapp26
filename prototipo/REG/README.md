# Prototipo — REG (Acceso y módulos)

HTML/CSS estático demostrativo para el módulo de acceso compartido de FILEY.
REG no tiene dominio de contenido propio: su rol es autenticar al usuario (participante
o administrador) y dirigirlo al módulo correspondiente (EVT, VIS, TAL).

## Estructura

```text
prototipo/REG/
  styles.css           ← estilos del dominio (extiende ../common/styles-base.css)
  aplicantes/          ← acceso del participante externo
  administradores/     ← acceso del administrador general
```

## Cómo verlo

- **Participante:** abre `aplicantes/index.html`
- **Administrador:** abre `administradores/admin-login.html`
- Navega con los botones o con la barra de prototipo superior.

## Mapa de pantallas y flujo

Ver [mapas/REG.md](../mapas/REG.md)

## Decisiones de diseño

- **OTP para ambos roles:** el acceso usa código de un solo uso enviado por correo
  (CU-REG-002 para participantes, CU-REG-003 para administradores). No hay contraseña.
- **Registro solo en primer acceso:** si el correo no está registrado, se pide nombre
  y teléfono antes del OTP. Las visitas siguientes saltan directo al OTP.
- **Convocatorias cerradas visibles:** se atenúan con el estado "Convocatoria cerrada"
  pero no desaparecen; el participante puede ver a qué aplicó antes.
- **Admin no se auto-registra:** su cuenta la provisiona el administrador general
  (CU-REG-005, fuera del alcance de esta maqueta).
- **Selección de módulo post-login admin:** el administrador ve los módulos disponibles
  (Eventos, Infantil/Juvenil, Stands, Visitas…) y elige el suyo. Solo los módulos
  maquetados son navegables.

## Pendientes (fuera del alcance de esta maqueta)

- Gestión de cuentas administrativas / superadmin (CU-REG-005)
- Pantalla de perfil del participante (editar nombre/teléfono)
