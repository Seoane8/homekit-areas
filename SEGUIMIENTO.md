# Seguimiento — HomeKit Areas

Estado del desarrollo fase por fase.

| Fase | Descripción | Estado | Commit | Notas |
|------|-------------|--------|--------|-------|
| 0 | Investigación técnica HomeKit | ✅ Completado | — | Orquestador de `ConfigEntry`-s del dominio `homekit` vía `SOURCE_IMPORT`. Ver `docs/homekit-architecture.md` |
| 1 | Esqueleto | ✅ Completado | — | Integración cargable: `manifest.json`, `__init__.py`, `const.py`, `config_flow.py`, `strings.json`, `translations/es.json`. Repo: `hacs.json`, `pyproject.toml`, CI, tests básicos. Ruff limpio. |
| 2 | Config Flow | ✅ Completado | — | Flujo completo: áreas (todas/seleccionar), puerto, dominios, entidades excluidas. Tests actualizados. |
| 3 | Options Flow | ✅ Completado | — | Options Flow implementado: permite modificar áreas, puerto, dominios y exclusiones |
| 4 | Modelo de datos | ✅ Completado | — | `models.py` con `AreaBridge` (area_id, name, port, entities). Identidad por `area_id`. |
| 5 | Area Manager | ✅ Completado | — | `area_manager.py` con descubrimiento de áreas, detección de cambios y obtención de entidades |
| 6 | Entity Filter | ✅ Completado | — | `entity_filter.py` con pipeline de filtrado (dominios, exclusiones, no soportados). Tests unitarios incluidos. |
| 7 | Bridge Manager | ✅ Completado | — | `bridge_manager.py` con create_bridge, start_bridge, stop_bridge, update_bridge. Usa ConfigEntry-s del dominio `homekit`. |
| 8 | Persistencia de puertos | ✅ Completado | — | `port_manager.py` con persistencia de mapping area_id→port. Puertos no se reutilizan. |
| 9 | Primer Bridge | ✅ Completado | — | Validado con 3 bridges simultáneos. Arranque, pairing, luces independientes y reinicio funcionan correctamente. |
| 10 | Múltiples Bridges | ✅ Completado | — | Validado con 3 bridges (Salón, Dormitorio, Entrada). Todos activos, pairing independiente, entidades segregadas. |
| 11 | Detección de cambios | ✅ Completado | — | Listener para `entity_registry_updated` y `area_registry_updated`. Callbacks para notificar cambios. |
| 12 | Cambio de área | ✅ Completado | — | Actualización dinámica de bridges cuando una entidad cambia de área. Sin reinicio. |
| 13 | Nuevas entidades | ✅ Completado | — | Detección y adición automática de nuevas entidades al bridge correspondiente. |
| 14 | Nuevas áreas | ⏳ Pendiente | — | |
| 15 | Eliminación de áreas | ⏳ Pendiente | — | |
| 16 | Cambios de nombre | ⏳ Pendiente | — | |
| 17 | Apple Home | ⏳ Pendiente | — | |
| 18 | Tests + HACS + Release | ⏳ Pendiente | — | |

## Leyenda

- ⏳ Pendiente
- 🔄 En curso
- ✅ Completado
- ⛔ Bloqueado

## Regla de avance

**No pasar a la siguiente fase hasta que todos los tests manuales de la fase actual estén marcados.** Ver `TESTS_MANUALES.md`.

## Bitácora

### 2026-08-21 — Inicio Fase 0

Objetivo: estudiar la implementación de HomeKit de Home Assistant (versión objetivo `2026.8.x`) para determinar cómo orquestar dinámicamente varios Bridges reutilizando la integración oficial.

Preguntas a resolver (plan.md §6):

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

Entregable: `docs/homekit-architecture.md`.

Restricción: no continuar con `BridgeManager` hasta resolver esta cuestión. No implementar un servidor HomeKit/HAP propio.

### 2026-08-21 — Fin Fase 0

Conclusión: **sí existe un mecanismo razonablemente seguro.** No es necesario detener la implementación.

- La integración oficial `homeassistant.components.homekit` soporta múltiples instancias (una por `ConfigEntry` del dominio `homekit`) y ella misma genera instancias adicionales de forma programática (modo *accessory*).
- **Solución elegida:** HomeKit Areas orquesta `ConfigEntry`-s del dominio `homekit` (uno por área), creados vía `flow.async_init("homekit", source=SOURCE_IMPORT, data=...)`. El `BridgeManager` mantiene un store `area_id → {entry_id, port}` y reconcilia al arrancar.
- Pairing/identidad conservados mientras el `entry_id` sea estable → persistencia en `.storage/homekit.<entry_id>.{state,aids,iids}`.
- Puertos desde `21070+`, no se recalculan por orden, no se reutilizan liberados (V1).
- Actualización de entidades: `async_update_entry(options[CONF_FILTER]) + async_reload(entry_id)` (recarga completa, pairing preservado). Optimización futura: `SIGNAL_RELOAD_ENTITIES` para moves sin reiniciar driver.
- Alternativa descartada como primaria: instanciar `HomeKit`/`HomeDriver` directamente (acoplamiento a APIs internas).
- Comprobaciones de validación enumeradas en §9 del documento. Se ejecutarán en HA real antes de Fase 7.

Entregable: `docs/homekit-architecture.md`.

### 2026-08-21 — Fin Fase 1 (Esqueleto)

Creado el esqueleto de la integración cargable en Home Assistant. Criterio de aceptación del plan §7 cubierto (aparece en "Añadir integración → HomeKit Areas", instala, recarga).

Archivos de la integración (`custom_components/homekit_areas/`):

- `manifest.json` — `domain=homekit_areas`, `config_flow=true`, `single_config_entry=true`, `version=0.1.0`, `iot_class=local_polling`.
- `__init__.py` — `async_setup` / `async_setup_entry` / `async_unload_entry` (stubs; el coordinador se cablea en fases posteriores).
- `const.py` — `DOMAIN`, `PLATFORMS=[]`, claves de opciones (`CONF_AREAS`, `CONF_INITIAL_PORT`, `CONF_DOMAINS`, `CONF_EXCLUDED_ENTITIES`) y defaults (`DEFAULT_INITIAL_PORT=21070`, `DEFAULT_DOMAINS=light,switch,fan,cover`).
- `config_flow.py` — `HomeKitAreasConfigFlow` con `async_step_user` que crea una entrada única con defaults. UI completa (áreas/puerto/dominios/excluidas) en Fase 2.
- `strings.json` + `translations/es.json` — textos del paso y del abort.

Infraestructura de repositorio:

- `hacs.json` (HACS, min HA 2026.8.0), `README.md`, `LICENSE` (MIT), `pyproject.toml` (deps de test: `homeassistant`, `pytest`, `pytest-asyncio`, `pytest-homeassistant-custom-component`, `ruff`; config ruff/pytest), `.gitignore`.
- `.github/workflows/tests.yml` — matrix Python 3.12/3.13, ruff + pytest.
- `tests/` — `__init__.py`, `conftest.py` (carga `pytest_homeassistant_custom_component` + `enable_custom_integrations`), `test_config_flow.py` (form mostrado, entry creada con defaults, single-instance abort).

Validación local: `python -m compileall` OK, JSON OK, `ruff check` + `ruff format --check` limpios. La suite de pytest requiere instalar el stack de HA (se delega al CI).

No se implementó HomeKit (cumple "Todavía no se implementará HomeKit").

### 2026-08-21 — Fin Fase 2 (Config Flow)

Implementado el flujo de configuración completo con 4 pasos:

1. **user** — Selector de modo de áreas (Todas / Seleccionar)
2. **select_areas** — Selector múltiple de áreas (solo si se elige "Seleccionar")
3. **port** — Puerto inicial (default 21070, rango 1024-65535)
4. **domains** — Selector múltiple de dominios (24 dominios soportados, defaults: light, switch, fan, cover)
5. **excluded** — Selector de entidades excluidas (filtrado por dominios seleccionados)

Archivos modificados:
- `const.py` — Añadidas constantes `CONF_AREA_MODE`, `AREA_MODE_ALL`, `AREA_MODE_SELECT`
- `config_flow.py` — Implementados los 4 pasos con selectores de HA
- `strings.json` + `translations/es.json` — Textos para todos los pasos
- `tests/test_config_flow.py` — Tests para flujo completo (all areas + select areas)

Validación: ruff check + format limpios.

### 2026-08-21 — Fin Fase 3 (Options Flow)

Implementado el flujo de opciones para modificar la configuración después de la instalación inicial.

**Archivos modificados:**
- `config_flow.py` — Añadida clase `HomeKitAreasOptionsFlow` con los mismos 5 pasos que el Config Flow:
  1. **init** — Selector de modo de áreas (Todas / Seleccionar)
  2. **select_areas** — Selector múltiple de áreas (precargado con valores actuales)
  3. **port** — Puerto inicial (precargado con valor actual)
  4. **domains** — Selector múltiple de dominios (precargado con valores actuales)
  5. **excluded** — Selector de entidades excluidas (precargado con valores actuales)
- `strings.json` + `translations/es.json` — Añadida sección `options` con textos para todos los pasos

**Validación:**
- Ruff check + format limpios
- Tests manuales completados (5/5):
  - ✅ Verificar que existe la opción "Configurar"
  - ✅ Modificar áreas
  - ✅ Modificar puerto inicial
  - ✅ Modificar dominios
  - ✅ Modificar entidades excluidas

**Nota:** Durante las pruebas manuales se detectó y corrigió un bug: el selector de áreas no se mostraba correctamente. Se ajustó el flujo para que `async_step_user` llame a `async_step_select_areas` cuando se selecciona el modo "Seleccionar".

### 2026-08-23 — Fin Fase 4 (Modelo de datos)

Implementado el modelo de datos para representar los bridges de HomeKit por área.

**Archivos creados:**
- `models.py` — Clase `AreaBridge` con campos:
  - `area_id: str` — Identificador único del área (identidad del bridge)
  - `name: str` — Nombre del bridge (ej: "HomeKit Salón")
  - `port: int` — Puerto asignado al bridge
  - `entities: set[str]` — Conjunto de entity_ids incluidas en el bridge

**Diseño:**
- La identidad del bridge es siempre `area_id`, nunca el nombre (plan §10)
- `__hash__` y `__eq__` basados en `area_id` para usar en sets/dicts
- `entities` como `set[str]` para operaciones eficientes de unión/diferencia

**Validación:**
- Ruff check + format limpios

### 2026-08-23 — Fin Fase 5 (Area Manager)

Implementado el AreaManager para descubrir y rastrear áreas de Home Assistant.

**Archivos creados:**
- `area_manager.py` — Clase `AreaManager` con responsabilidades:
  - `async_setup()` — Inicializa el manager y escucha cambios en el registro de áreas
  - `async_discover_areas()` — Descubre todas las áreas y retorna `AreaBridge` objects
  - `async_get_entities_for_area(area_id)` — Obtiene entidades asociadas a un área (directamente o vía dispositivo)
  - `_async_handle_area_registry_update()` — Detecta creación, eliminación y renombrado de áreas
  - `get_known_areas()` — Retorna áreas conocidas (area_id → name)
  - `async_shutdown()` — Limpia listeners

**Diseño:**
- Usa `area_registry`, `entity_registry`, `device_registry` de HA
- Escucha evento `area_registry_updated` para detectar cambios en tiempo real
- Las entidades se asocian a un área si:
  - La entidad tiene `area_id` directamente, O
  - El dispositivo de la entidad tiene `area_id`

**Validación:**
- Ruff check + format limpios

### 2026-08-23 — Fin Fase 6 (Entity Filter)

Implementado el EntityFilter con pipeline de filtrado para entidades de HomeKit.

**Archivos creados:**
- `entity_filter.py` — Clase `EntityFilter` con pipeline:
  1. `filter_entities()` — Aplica el pipeline completo
  2. `_filter_by_domain()` — Filtra por dominios permitidos
  3. `_filter_excluded()` — Excluye entidades específicas
  4. `_filter_unsupported()` — Excluye dominios no soportados por HomeKit
  5. `get_filtered_entities_for_area()` — Método de conveniencia para áreas

- `tests/test_entity_filter.py` — Tests unitarios independientes:
  - Test de filtrado por dominio
  - Test de exclusión de entidades
  - Test de dominios no soportados
  - Test del pipeline completo
  - Test de casos edge (vacío, todo excluido, etc.)

**Diseño:**
- Pipeline secuencial: área → dominios → exclusiones → no soportados
- `UNSUPPORTED_DOMAINS` incluye dominios que no tienen representación en HomeKit
- Integrado en `__init__.py` para filtrar entidades de cada área al cargar

**Validación:**
- Ruff check + format limpios
- Tests unitarios creados (10 tests)

### 2026-08-23 — Fin Fase 7 (Bridge Manager)

Implementado el BridgeManager para orquestar bridges HomeKit por área.

**Archivos creados:**
- `bridge_manager.py` — Clase `BridgeManager` con responsabilidades:
  - `create_bridge(bridge)` — Crea ConfigEntry del dominio `homekit` vía `flow.async_init(SOURCE_IMPORT)`
  - `start_bridge(area_id)` — Reinicia un bridge (reload del ConfigEntry)
  - `stop_bridge(area_id)` — Detiene un bridge (unload del ConfigEntry)
  - `update_bridge(bridge)` — Actualiza entidades del bridge y recarga
  - `remove_bridge(area_id)` — Elimina el ConfigEntry
  - `get_bridge_info(area_id)` — Obtiene info de un bridge
  - `get_all_bridges()` — Obtiene todos los bridges registrados

**Diseño:**
- Mantiene `_bridge_registry: dict[area_id → {entry_id, port}]` para persistencia
- Usa `SOURCE_IMPORT` para crear ConfigEntry-s del dominio `homekit` con data completo
- Cada bridge tiene: name, port, mode=bridge, filter (include_entities), exclude_accessory_mode=True
- Integrado en `__init__.py`: crea bridges automáticamente al cargar la integración
- Asigna puertos consecutivos desde `initial_port` (21070 por defecto)

**Archivos modificados:**
- `__init__.py` — Inicializa BridgeManager, crea bridges para cada área descubierta

**Validación:**
- Ruff check + format limpios

### 2026-08-24 — Fin Fase 8 (Persistencia de puertos)

Implementado el PortManager para persistir el mapping area_id → port.

**Archivos creados:**
- `port_manager.py` — Clase `PortManager` con responsabilidades:
  - `async_load()` — Carga mapping desde storage
  - `async_save()` — Guarda mapping en storage
  - `get_port(area_id)` — Obtiene puerto asignado
  - `allocate_port(area_id)` — Asigna puerto (reutiliza si ya existe)
  - `release_port(area_id)` — Libera puerto (NO se reutiliza en V1)
  - `get_all_mappings()` — Obtiene todos los mappings
  - `has_port(area_id)` — Verifica si un área tiene puerto

**Diseño:**
- Usa `Store` de Home Assistant para persistencia en `.storage/homekit_areas_port_mapping`
- Mantiene `_port_mapping: dict[area_id → port]` y `_next_port` para siguiente asignación
- Puertos liberados NO se reutilizan (V1): no hay lista de puertos libres
- Integrado en BridgeManager: `create_bridge` usa `allocate_port`, `remove_bridge` usa `release_port`
- Mapping se guarda automáticamente después de cada cambio

**Archivos modificados:**
- `bridge_manager.py` — Acepta `PortManager` en constructor, usa para asignar/liberar puertos
- `__init__.py` — Inicializa `PortManager`, lo pasa a `BridgeManager`

**Validación:**
- Ruff check + format limpios
- Tests manuales completados (3/3)

### 2026-08-24 — Fin Fases 9 y 10 (Primer Bridge y Múltiples Bridges)

Validación combinada de las fases 9 y 10 mediante pruebas reales con Apple Home.

**Configuración probada:**
- 3 bridges simultáneos: Salón (21070), Dormitorio (21071), Entrada (21072)
- Cada bridge con sus entidades filtradas por área
- Pairing independiente con Apple Home para cada bridge

**Tests validados:**

**Fase 9 — Primer Bridge (4/4 tests):**
- ✅ Test 9.1 — Arranque del bridge: Los 3 bridges arrancan correctamente en sus puertos asignados
- ✅ Test 9.2 — Pairing con Apple Home: Cada bridge se empareja correctamente con su PIN único
- ✅ Test 9.3 — Luces independientes: Las luces de cada área aparecen y funcionan independientemente en Apple Home
- ✅ Test 9.4 — Reinicio conserva pairing: El pairing se mantiene tras múltiples reinicios de Home Assistant

**Fase 10 — Múltiples Bridges (3/3 tests):**
- ✅ Test 10.1 — Múltiples bridges activos: Los 3 bridges están activos simultáneamente sin conflictos
- ✅ Test 10.2 — Pairing independiente: Cada bridge tiene su propio PIN y se empareja de forma independiente
- ✅ Test 10.3 — Entidades independientes: Las entidades están correctamente segregadas por área, sin duplicados

**Resultados clave:**
- Los bridges creados vía `SOURCE_IMPORT` funcionan correctamente con la integración oficial de HomeKit
- El pairing se conserva gracias a la persistencia de los ficheros `.state` en `.storage/`
- Las entidades se filtran correctamente por área usando `include_entities` en el filtro de HomeKit
- No hay conflictos entre múltiples bridges simultáneos
- El control desde Apple Home funciona correctamente para todas las entidades

**Conclusión:**
La arquitectura de orquestar ConfigEntry-s del dominio `homekit` funciona correctamente tanto para un solo bridge como para múltiples bridges simultáneos. La integración está lista para continuar con las fases de detección de cambios dinámicos.

### 2026-08-24 — Fin Fases 11, 12 y 13 (Detección de cambios dinámicos)

Implementada la detección y respuesta automática a cambios en el registro de entidades y áreas.

**Archivos modificados:**

**`area_manager.py`:**
- Añadido listener para `entity_registry_updated`
- Implementado sistema de callbacks para notificar cambios
- Tipos de cambios detectados:
  - `entity_area_changed`: Entidad movida entre áreas
  - `new_entity`: Nueva entidad en un área gestionada
  - `area_created`: Nueva área creada
  - `area_removed`: Área eliminada
  - `area_renamed`: Área renombrada

**`bridge_manager.py`:**
- Añadido `update_bridge_entities(area_id, entities)`: Actualiza entidades de un bridge sin recrearlo
- Añadido `rename_bridge(area_id, new_name)`: Renombra un bridge preservando puerto y pairing

**`__init__.py`:**
- Registrado callback de cambios en AreaManager
- Implementada lógica de respuesta a cambios:
  - `entity_area_changed`: Actualiza ambos bridges (origen y destino)
  - `new_entity`: Añade entidad al bridge del área
  - `area_renamed`: Renombra el bridge correspondiente
  - `area_created`: Crea nuevo bridge si el área está configurada
  - `area_removed`: Elimina bridge del área eliminada

**Comportamiento:**
- Los cambios se detectan automáticamente sin reiniciar Home Assistant
- Los bridges se actualizan preservando el pairing con Apple Home
- Las entidades se mueven entre bridges automáticamente
- Nuevas entidades se añaden automáticamente al bridge correspondiente

**Validación:**
- Ruff check + format limpios
- Tests manuales completados (3/3)
