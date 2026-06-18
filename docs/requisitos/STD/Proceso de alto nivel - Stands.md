---
estado: propuesta
version: 1.0
tags:
  - proceso
  - stands
fecha: 2026-06-18
---
# Proceso de alto nivel — Stands (reserva, pago y confirmación)

Diagrama del flujo de punta a punta para poner en contexto al equipo: desde que el
usuario **aplica a expositor** hasta que su reserva queda **pagada al 100%**, incluyendo
las ramas de vencimiento (liberación automática / decisión del administrador).

El color de cada nodo indica quién interviene: Usuario, Administrador, Sistema y estados
finales. El detalle por paso vive en los casos de uso (`CU-STD Índice.md`).

```mermaid
%% Proceso de alto nivel: Reserva, Pago y Confirmación de Stands — FILEY
flowchart TD
    A([Usuario aplica a expositor]) --> B{Admin revisa<br/>la aplicación}
    B -->|Rechazada con motivo| C[/Notifica al usuario/]
    C --> A2([Usuario edita y reenvía])
    A2 --> B
    B -->|Aceptada| D[Usuario habilitado<br/>para reservar]

    D --> E[Visualiza el mapa<br/>y agrega stands al carrito]
    E --> F[Realiza la reserva<br/>Stands → Reservado]
    F --> G[Inicia plazo de 30 días<br/>para cubrir el 50%]

    G --> H[Usuario registra pagos<br/>con comprobante]
    H --> I{Admin valida<br/>el abono}
    I -->|Rechaza| H
    I -->|Confirma abono| J{¿Se alcanzó<br/>el 50% en 30 días?}

    J -->|Sí| K[Reserva CONFIRMADA<br/>y bloqueada]
    K --> L[/Notifica: reserva confirmada/]
    L --> M[Usuario sigue abonando<br/>hasta la fecha de corte]
    M --> N{¿Se alcanzó<br/>el 100%?}
    N -->|Aún no| M
    N -->|Sí| O[Reserva PAGADA]
    O --> P[/Notifica: reserva pagada/]
    P --> Q([Fin])

    J -->|No, venció el plazo| R{¿Hubo algún abono?}
    R -->|No| S[Reserva LIBERADA<br/>automáticamente]
    S --> T([Stands vuelven a Disponible])
    R -->|Sí, abono parcial| U[/Notifica al admin y al usuario:<br/>posible cancelación/]
    U --> V{Admin decide}
    V -->|Prorroga: nueva fecha| M
    V -->|Cancela| W([Reserva CANCELADA])

    classDef usuario fill:#dbeafe,stroke:#2563eb,color:#1e3a8a;
    classDef admin fill:#fef3c7,stroke:#d97706,color:#7c2d12;
    classDef sistema fill:#dcfce7,stroke:#16a34a,color:#14532d;
    classDef fin fill:#f3f4f6,stroke:#6b7280,color:#111827;

    class A,A2,E,F,H,M usuario;
    class B,I,V admin;
    class C,D,G,J,K,L,N,O,P,R,S,U sistema;
    class Q,T,W,fin fin;
```
