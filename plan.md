# HomeKit Areas — Plan de desarrollo

## 0. Objetivo

Crear una custom integration para Home Assistant llamada **HomeKit Areas** que gestione automáticamente **un HomeKit Bridge independiente por cada área de Home Assistant**.

Ejemplo:

```text
Home Assistant
│
├── Salón
│   ├── light.lampara_piano
│   ├── light.lampara_pie
│   └── light.lampara_television
│
├── Cocina
│   ├── light.cocina
│   └── switch.cafetera
│
└── Dormitorio
    └── light.dormitorio
```

Debe producir:

```text
Apple Home

HomeKit Salón
├── Lámpara piano
├── Lámpara pie
└── Lámpara televisión

HomeKit Cocina
├── Luz cocina
└── Cafetera

HomeKit Dormitorio
└── Luz dormitorio
```

Las entidades deben permanecer **individuales e independientes** en Apple Home.

---

# 1. Repositorio GitHub

Crear un repositorio:

```text
homekit-areas
```

Estructura inicial:

```text
homekit-areas/
│
├── custom_components/
│   └── homekit_areas/
│       ├── __init__.py
│       ├── manifest.json
│       ├── const.py
│       ├── config_flow.py
│       ├── coordinator.py
│       ├── area_manager.py
│       ├── entity_filter.py
│       ├── bridge_manager.py
│       ├── models.py
│       ├── strings.json
│       └── translations/
│           └── es.json
│
├── tests/
│   ├── __init__.py
│   ├── test_config_flow.py
│   ├── test_area_manager.py
│   ├── test_entity_filter.py
│   └── test_bridge_manager.py
│
├── .github/
│   └── workflows/
│       └── tests.yml
│
├── hacs.json
├── README.md
├── LICENSE
└── pyproject.toml
```

---

# 2. Distribución

La integración debe ser compatible con **HACS**.

Flujo de instalación:

```text
GitHub
   ↓
HACS
   ↓
HomeKit Areas
   ↓
/config/custom_components/homekit_areas/
   ↓
Home Assistant
```

Durante el desarrollo también debe ser posible instalarla manualmente.

---

# 3. Versionado

Utilizar Semantic Versioning:

```text
0.1.0
0.2.0
0.3.0
...
1.0.0
```

Durante desarrollo se utilizarán versiones `0.x`.

La primera versión estable será:

```text
1.0.0
```

Cada release debe incluir changelog.

---

# 4. Arquitectura

La integración tendrá estas responsabilidades:

```text
┌───────────────────────────────┐
│        HomeKit Areas          │
├───────────────────────────────┤
│                               │
│ Config Flow                   │
│       ↓                       │
│ Coordinator                   │
│       ↓                       │
│ Area Manager                  │
│       ↓                       │
│ Entity Filter                 │
│       ↓                       │
│ Bridge Manager                │
│       ↓                       │
└───────────┬───────────────────┘
            ↓
    HomeKit Bridge oficial
            ↓
        Apple Home
```

---

# 5. Principio fundamental

**No implementar el protocolo HomeKit.**

La integración oficial:

```text
homeassistant.components.homekit
```

será responsable de:

* HAP.
* Pairing.
* PIN.
* mDNS.
* Accesorios.
* Características.
* Comunicación con Apple Home.
* Persistencia relacionada con HomeKit.

Nuestra integración será únicamente el **orquestador dinámico de los Bridges**.

---

# 6. Fase 0 — Investigación técnica

Antes de implementar `bridge_manager.py`, estudiar la implementación de HomeKit de la versión objetivo de Home Assistant.

Determinar:

1. Cómo se crean actualmente las instancias HomeKit.
2. Qué representa internamente cada Bridge.
3. Si pueden crearse dinámicamente.
4. Si existe una API pública.
5. Si existe una API interna razonablemente estable.
6. Cómo se conserva el pairing.
7. Cómo se actualizan las entidades de una instancia.
8. Cómo se inicia y detiene una instancia.
9. Cómo se gestiona el puerto.
10. Cómo evitar conflictos con otras instancias.

Crear:

```text
docs/homekit-architecture.md
```

El documento debe explicar la solución elegida y las APIs utilizadas.

### Restricción

No continuar con la implementación de `BridgeManager` hasta resolver esta cuestión.

Si no existe un mecanismo razonablemente seguro para gestionar dinámicamente el HomeKit Bridge oficial:

* detener la implementación;
* documentar el bloqueo;
* proponer una arquitectura alternativa.

**No implementar un servidor HomeKit/HAP propio como solución improvisada.**

---

# 7. Fase 1 — Esqueleto

Crear:

```text
manifest.json
__init__.py
const.py
config_flow.py
strings.json
translations/es.json
```

La integración debe:

* aparecer en Home Assistant;
* poder instalarse;
* abrir Config Flow;
* crear una Config Entry;
* descargarse correctamente;
* recargarse correctamente.

Todavía no se implementará HomeKit.

### Criterio de aceptación

Debe poder accederse a:

```text
Ajustes
→ Dispositivos y servicios
→ Añadir integración
→ HomeKit Areas
```

---

# 8. Fase 2 — Config Flow

La configuración se realizará desde la UI.

## Áreas

```text
Áreas a gestionar

● Todas
○ Seleccionar
```

Por defecto:

```text
Todas
```

Si se selecciona manualmente:

```text
☑ Salón
☑ Cocina
☑ Dormitorio
☐ Baño
☐ Garaje
```

## Puerto inicial

```text
Puerto inicial
[ 21070 ]
```

## Dominios

V1:

```text
☑ light
☑ switch
☑ fan
☑ cover
```

El diseño debe permitir añadir posteriormente:

```text
climate
lock
media_player
...
```

## Entidades excluidas

Selector de entidades:

```text
Entidades excluidas
[ Seleccionar entidades... ]
```

---

# 9. Fase 3 — Options Flow

Permitir modificar posteriormente:

* áreas;
* puerto inicial;
* dominios;
* entidades excluidas.

Los cambios deben provocar una sincronización de los Bridges.

No generar YAML.

No modificar `configuration.yaml`.

---

# 10. Fase 4 — Modelo de datos

Crear `models.py`.

Representar cada Bridge con información equivalente a:

```python
AreaBridge(area_id="abc123", name="HomeKit Salón", port=21070, entities=set(...))
```

La identidad será siempre:

```text
area_id
```

Nunca utilizar el nombre del área como identificador.

---

# 11. Fase 5 — Area Manager

Crear:

```text
AreaManager
```

Responsabilidades:

* descubrir áreas;
* obtener `area_id`;
* obtener nombres;
* detectar nuevas áreas;
* detectar áreas eliminadas;
* detectar cambios de nombre;
* obtener entidades asociadas a un área.

Debe utilizar las APIs de Home Assistant.

No debe duplicar manualmente la lógica de las funciones de áreas de Home Assistant.

---

# 12. Fase 6 — Entity Filter

Crear:

```text
EntityFilter
```

Pipeline:

```text
Entidades del área
        ↓
Dominios permitidos
        ↓
Entidades excluidas
        ↓
Entidades válidas para HomeKit
```

Ejemplo:

```text
light.lampara_piano
→ incluir

select.lampara_piano_power_on_behavior
→ excluir

update.lampara_piano
→ excluir
```

Debe disponer de tests unitarios independientes.

---

# 13. Fase 7 — Bridge Manager

Crear:

```text
BridgeManager
```

Responsabilidades:

```text
create_bridge()
start_bridge()
stop_bridge()
update_bridge()
```

Debe utilizar la integración oficial de HomeKit.

No debe:

* descubrir áreas;
* decidir qué entidades pertenecen a cada área;
* gestionar la configuración de usuario.

---

# 14. Fase 8 — Persistencia de puertos

Mantener un mapping:

```text
area_id → port
```

Ejemplo:

```text
abc123 → 21070
def456 → 21071
ghi789 → 21072
```

El mapping debe sobrevivir a reinicios.

No recalcular los puertos según el orden actual de las áreas.

Ejemplo:

```text
Salón      → 21070
Cocina     → 21071
Dormitorio → 21072
```

Si se elimina Cocina:

```text
Salón      → 21070
Dormitorio → 21072
```

Dormitorio no debe pasar automáticamente a `21071`.

En V1 no se reutilizarán automáticamente puertos liberados.

---

# 15. Fase 9 — Primer Bridge

Antes de implementar múltiples Bridges:

```text
Salón → 21070
```

Debe funcionar completamente.

Probar:

* arranque;
* pairing con Apple Home;
* luces independientes;
* reinicio;
* conservación del pairing.

No continuar hasta que este caso sea estable.

---

# 16. Fase 10 — Múltiples Bridges

Implementar:

```text
Salón      → 21070
Cocina     → 21071
Dormitorio → 21072
```

Cada Bridge debe tener:

* puerto independiente;
* configuración independiente;
* entidades independientes.

---

# 17. Fase 11 — Detección de cambios

Escuchar:

```text
device_registry_updated
```

En la instalación real se ha validado:

```yaml
event_type: device_registry_updated
data:
  action: update
  device_id: ...
  changes:
    area_id: despacho
```

El listener debe reaccionar únicamente a cambios relevantes.

---

# 18. Fase 12 — Cambio de área

Ejemplo:

```text
light.lampara_pie

Salón → Despacho
```

Resultado:

```text
HomeKit Salón
├── Lámpara piano
└── Lámpara televisión

HomeKit Despacho
└── Lámpara pie
```

Debe realizarse automáticamente y sin reiniciar Home Assistant.

---

# 19. Fase 13 — Nuevas entidades

Si aparece una entidad compatible:

```text
Salón
   +
light.lampara_nueva
```

debe añadirse automáticamente al Bridge correspondiente.

---

# 20. Fase 14 — Nuevas áreas

Si la configuración es:

```text
Áreas = Todas
```

y se crea:

```text
Oficina
```

la integración debe:

1. detectar la nueva área;
2. obtener su `area_id`;
3. asignarle un puerto;
4. crear su Bridge;
5. obtener sus entidades;
6. iniciar el Bridge.

Resultado:

```text
HomeKit Oficina
```

---

# 21. Fase 15 — Eliminación de áreas

Si un área desaparece:

```text
Área
 ↓
Bridge correspondiente
 ↓
stop
 ↓
cleanup
```

No se deben modificar otros Bridges.

El puerto liberado no se reutilizará automáticamente en V1.

---

# 22. Fase 16 — Cambios de nombre

Ejemplo:

```text
Salón
 ↓
Sala de estar
```

Debe conservar:

```text
area_id
port
pairing
```

Solo debe cambiar el nombre del Bridge.

No crear un Bridge nuevo.

---

# 23. Fase 17 — Apple Home

Probar específicamente:

### Primer pairing

```text
HomeKit Salón
    ↓
Apple Home
    ↓
Pair
```

### Cambios posteriores

Mover entidades entre áreas.

Comprobar:

* no se pierde pairing;
* no aparecen duplicados;
* los accesorios se mueven al Bridge correcto;
* los demás accesorios permanecen intactos.

---

# 24. Bridges existentes

La integración debe ignorar completamente los Bridges existentes del usuario:

```text
HASS Bridge      → 21064
HASS Bridge U8   → 21065
```

HomeKit Areas comenzará en:

```text
21070+
```

Nunca debe modificar los Bridges existentes.

---

# 25. Tests

## Config Flow

Probar:

* configuración válida;
* configuración inválida;
* valores por defecto;
* Options Flow;
* segunda configuración.

## Áreas

Probar:

* nueva área;
* área eliminada;
* área renombrada;
* cambio de área.

## Entidades

Probar:

* inclusión;
* exclusión;
* cambio de área;
* entidad nueva;
* entidad eliminada.

## Puertos

Probar:

* asignación;
* persistencia;
* reinicio;
* conflictos;
* eliminación de áreas.

## Bridges

Probar:

* creación;
* actualización;
* eliminación;
* múltiples Bridges;
* cleanup.

---

# 26. GitHub Actions

Cada push debe ejecutar:

```text
Push
 ↓
GitHub Actions
 ├── pytest
 ├── lint
 ├── type checking
 └── validaciones
```

No publicar releases que no superen las comprobaciones.

---

# 27. Documentación

Crear:

```text
README.md
docs/
├── architecture.md
└── homekit-architecture.md
```

El README debe explicar:

* qué hace HomeKit Areas;
* requisitos;
* instalación mediante HACS;
* configuración;
* funcionamiento;
* puertos;
* pairing con Apple Home;
* comportamiento ante cambios de área;
* troubleshooting;
* compatibilidad con Home Assistant.

---

# 28. Releases

Plan inicial:

### `v0.1.0`

* Esqueleto.
* Config Flow.
* Descubrimiento de áreas.

### `v0.2.0`

* Primer Bridge oficial funcional.

### `v0.3.0`

* Múltiples Bridges.

### `v0.4.0`

* Sincronización dinámica.

### `v0.5.0`

* Persistencia.
* Robustez.
* Tests completos.

### `v1.0.0`

Primera versión estable.

---

# 29. Criterios de aceptación de `v1.0.0`

## Caso 1 — Configuración inicial

Con:

```text
Salón
├── Piano
├── Pie
└── TV

Cocina
└── Techo
```

Apple Home debe mostrar:

```text
HomeKit Salón
├── Piano
├── Pie
└── TV

HomeKit Cocina
└── Techo
```

Cada accesorio debe ser independiente.

---

## Caso 2 — Mover una entidad

Mover:

```text
Pie
```

de:

```text
Salón → Dormitorio
```

debe producir automáticamente:

```text
HomeKit Salón
├── Piano
└── TV

HomeKit Dormitorio
└── Pie
```

Sin reiniciar Home Assistant.

---

## Caso 3 — Crear un área

Crear:

```text
Oficina
```

Debe aparecer automáticamente:

```text
HomeKit Oficina
```

---

## Caso 4 — Renombrar un área

Cambiar:

```text
Salón → Sala de estar
```

no debe crear un Bridge nuevo.

Debe conservar:

```text
area_id
port
pairing
```

---

## Caso 5 — Reiniciar Home Assistant

Después de reiniciar:

* los Bridges deben volver a estar disponibles;
* los puertos deben mantenerse;
* Apple Home no debe requerir volver a emparejar;
* no deben aparecer Bridges duplicados.

---

# 30. Orden obligatorio de desarrollo

El agente debe trabajar **fase por fase**:

```text
Fase 0
Investigación HomeKit
       ↓
Fase 1
Esqueleto
       ↓
Fase 2
Config Flow
       ↓
Fase 3
Area Manager
       ↓
Fase 4
Entity Filter
       ↓
Fase 5
Bridge Manager
       ↓
Fase 6
Primer Bridge
       ↓
Fase 7
Múltiples Bridges
       ↓
Fase 8
Eventos dinámicos
       ↓
Fase 9
Persistencia
       ↓
Fase 10
Apple Home
       ↓
Fase 11
Tests + HACS + Release
```

## Regla principal

**No implementar todo de golpe.**

Cada fase debe:

1. implementar únicamente su objetivo;
2. añadir sus tests;
3. comprobar que lo anterior sigue funcionando;
4. documentar cualquier decisión arquitectónica;
5. hacer commit independiente.

La **Fase 0 es especialmente importante**: antes de escribir el `BridgeManager`, el agente debe verificar cómo reutilizar correctamente el HomeKit Bridge oficial de Home Assistant 2026.8.x. Si no existe una interfaz adecuada, debe detenerse y documentar el problema en lugar de crear una implementación alternativa de HomeKit.
