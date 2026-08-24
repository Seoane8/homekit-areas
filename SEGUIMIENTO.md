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
| 8 | Persistencia de puertos | ⏳ Pendiente | — | |
| 9 | Primer Bridge | ⏳ Pendiente | — | |
| 10 | Múltiples Bridges | ⏳ Pendiente | — | |
| 11 | Detección de cambios | ⏳ Pendiente | — | |
| 12 | Cambio de área | ⏳ Pendiente | — | |
| 13 | Nuevas entidades | ⏳ Pendiente | — | |
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
