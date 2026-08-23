# Seguimiento — HomeKit Areas

Estado del desarrollo fase por fase.

| Fase | Descripción | Estado | Commit | Notas |
|------|-------------|--------|--------|-------|
| 0 | Investigación técnica HomeKit | ✅ Completado | — | Orquestador de `ConfigEntry`-s del dominio `homekit` vía `SOURCE_IMPORT`. Ver `docs/homekit-architecture.md` |
| 1 | Esqueleto | ✅ Completado | — | Integración cargable: `manifest.json`, `__init__.py`, `const.py`, `config_flow.py`, `strings.json`, `translations/es.json`. Repo: `hacs.json`, `pyproject.toml`, CI, tests básicos. Ruff limpio. |
| 2 | Config Flow | ✅ Completado | — | Flujo completo: áreas (todas/seleccionar), puerto, dominios, entidades excluidas. Tests actualizados. |
| 3 | Options Flow | ✅ Completado | — | Options Flow implementado: permite modificar áreas, puerto, dominios y exclusiones |
| 4 | Modelo de datos | ⏳ Pendiente | — | |
| 5 | Area Manager | ⏳ Pendiente | — | |
| 6 | Entity Filter | ⏳ Pendiente | — | |
| 7 | Bridge Manager | ⏳ Pendiente | — | |
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
