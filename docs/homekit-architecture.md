# HomeKit Areas — Arquitectura de la integración oficial de HomeKit

> Fase 0 — Investigación técnica.
>
> Versión objetivo de Home Assistant: **2026.8.x** (rama `dev` de `home-assistant/core` a fecha de 2026-08-21).
>
> Este documento responde a las 10 preguntas del §6 de `plan.md`, justifica la solución elegida para el `BridgeManager` y enumera las APIs internas utilizadas. **No se implementa ningún servidor HomeKit/HAP propio.**

---

## 1. Resumen ejecutivo y decisión

La integración oficial `homeassistant.components.homekit` está diseñada para soportar **múltiples instancias independientes**, cada una materializada como un `ConfigEntry` del dominio `homekit`. La propia integración genera instancias adicionales de forma programática (modo *accessory*), por lo que crear `ConfigEntry`-s del dominio `homekit` desde otra integración es un patrón sancionado y robusto.

**Decisión:** HomeKit Areas actuará como **orquestador de `ConfigEntry`-s del dominio `homekit`**:

- 1 `ConfigEntry` del dominio `homekit_areas` (la integración del usuario, con su Config/Options Flow).
- N `ConfigEntry`-s del dominio `homekit` (uno por área gestionada), creados, actualizados y eliminados por el `BridgeManager`.

De este modo se reutiliza **el 100 % del ciclo de vida oficial** (HAP, pairing, PIN, mDNS, accesorios, puertos, persistencia, servicios `homekit.reset_accessory` / `homekit.unpair`). HomeKit Areas no instancia clases internas de pyhap ni construye drivers: solo manipula `ConfigEntry`-s.

Se descarta como primaria la instanciación directa de `HomeKit`/`HomeDriver` (documentada en §12 como *alternativa*).

---

## 2. La integración oficial: modelo de datos

Cada instancia oficial de HomeKit se compone de:

| Pieza | Clase (interna) | Rol |
|-------|-----------------|-----|
| Instancia lógica | `HomeKit` (`__init__.py`) | Orquesta setup/stop/reload de un bridge |
| Driver HAP | `HomeDriver` (subclase de `pyhap.accessory_driver.AccessoryDriver`) | Servidor HAP, mDNS, pairing |
| Bridge | `HomeBridge` (subclase de `pyhap.accessory.Bridge`) | Contenedor de accesorios |
| Accesorio | `HomeAccessory` (subclase de `pyhap.accessory.Accessory`) | Una entidad de HA como accesorio |
| Almacén AID | `AccessoryAidStorage` (`aidmanager.py`) | `entity_id → aid` estable |
| Almacén IID | `AccessoryIIDStorage` (`iidmanager.py`) | IIDs estables por accesorio |

Cada instancia está ligada a **un `entry_id`** y genera **tres ficheros de persistencia** en `.storage/`:

```text
homekit.<entry_id>.state   # pairing, mac, paired clients (pyhap state)
homekit.<entry_id>.aids    # allocations{entity: aid}, accessory_types
homekit.<entry_id>.iids    # allocations de IIDs
```

**Consecuencia clave:** la identidad y el pairing de un bridge están anclados al `entry_id`. Mientras el `entry_id` sea estable, el pairing, los aids y los iids sobreviven a recargas y reinicios.

---

## 3. Respuestas a las 10 preguntas (plan.md §6)

### 1. ¿Cómo se crean actualmente las instancias HomeKit?

Como `ConfigEntry` del dominio `homekit` (`DOMAIN = "homekit"`). El flujo:

- `async_setup_entry` (`__init__.py`) construye un `HomeKit(...)`, lo guarda en `entry.runtime_data` (`HomeKitEntryData(homekit=...)`, `models.py`), registra el listener de actualización, el listener de `EVENT_HOMEASSISTANT_STOP` y, vía `async_at_started(hass, _async_start_homekit)`, arranca el driver cuando HA termina de iniciarse.
- Un `ConfigEntry` se crea por la UI (`HomeKitConfigFlow`) o por **importación programática** (`async_step_import`), que acepta un `data` completo y crea la entrada sin interacción.

La integración **genera instancias adicionales de forma programática** en `HomeKitConfigFlow._async_add_entries_for_accessory_mode_entities`:

```python
self.hass.async_create_task(
    self.hass.config_entries.flow.async_init(
        DOMAIN,
        context={"source": "accessory"},
        data={CONF_ENTITY_ID: entity_id, CONF_PORT: port},
    ),
)
```

→ Crear `ConfigEntry`-s de `homekit` desde código **es un patrón ya usado por la propia integración oficial**.

### 2. ¿Qué representa internamente cada Bridge?

Un `ConfigEntry` de `homekit` ↔ una instancia `HomeKit` ↔ un `HomeDriver` + un `HomeBridge` con sus accesorios. Cada uno tiene: `name`, `port`, `ip_address`/`advertise_ips`, `entity_filter`, `entity_config`, `homekit_mode` (`bridge`|`accessory`), `exclude_accessory_mode`, `devices`, y los tres ficheros de persistencia ligados a su `entry_id`.

### 3. ¿Pueden crearse dinámicamente?

**Sí.** El componente asume múltiples entradas desde el principio: `_async_all_homekit_instances`, `_has_all_unique_names_and_ports`, `_async_get_imported_entries_indices`, y el servicio `homekit.unpair` iteran `hass.config_entries.async_entries(DOMAIN)`. La creación programática (§1) demuestra que se diseñó para instancias dinámicas.

### 4. ¿Existe una API pública?

No hay API pública documentada para crear bridges desde terceros. La vía pública equivalente es el **`ConfigEntry`**: crear/actualizar/eliminar entradas del dominio `homekit` con el schema `BRIDGE_SCHEMA`.

### 5. ¿Existe una API interna razonablemente estable?

Sí, a través del **schema de `ConfigEntry`** (no de clases internas). Los campos son estables y forman parte de `BRIDGE_SCHEMA` (`__init__.py`) y `CONFIG_OPTIONS` (`const.py`):

```python
data / options:
  CONF_NAME            (str, 3..25)
  CONF_PORT            (int port)
  CONF_HOMEKIT_MODE    ("bridge" | "accessory")
  CONF_FILTER          (EntityFilter schema: include_domains/include_entities/exclude_domains/exclude_entities)
  CONF_ENTITY_CONFIG   (dict opcional)
  CONF_DEVICES         (list[str] opcional, device triggers)
  CONF_EXCLUDE_ACCESSORY_MODE (bool)   # data; True => excluir entidades que requieren modo accessory
  CONF_ADVERTISE_IP / CONF_IP_ADDRESS  # yaml-only; no usados por config flow
```

Estos campos son la interfaz contractual; no dependemos de los constructores internos de `HomeKit`/`HomeDriver`.

APIs internas auxiliares utilizadas (en `util.py`), estables y reexportadas por el componente:

- `async_find_next_available_port(hass, start_port)` — próximo puerto libre, excluyendo los ya asignados a entradas `homekit`.
- `async_port_is_available(port)` — test real de `bind` en un socket.
- `remove_state_files_for_entry_id(hass, entry_id)` — borra los 3 ficheros de persistencia.
- `get_persist_fullpath_for_entry_id(...)` y equivalentes para aids/iids.

Señal de dispatcher (`const.py`):

- `SIGNAL_RELOAD_ENTITIES.format(entry_id)` — recarga accesorios **sin reiniciar el driver** (preserva pairing y puerto). Útil para actualizaciones finas (§9).

### 6. ¿Cómo se conserva el pairing?

El estado de pairing (MAC, clients emparejados, config) vive en `.storage/homekit.<entry_id>.state`. `HomeKit.setup()` hace `self.driver.load()` si el fichero existe; `async_start` persiste en el primer arranque. Por tanto:

> **Mientras el `entry_id` asociado a un área sea estable, el pairing sobrevive** a recargas, a `async_reload`, a reinicios de HA y a actualizaciones del filtro.

`async_remove_entry` (que borra los ficheros) **solo** se ejecuta al eliminar el `ConfigEntry` desde HA. El `BridgeManager` no debe eliminar entradas para cambios de entidad; solo al desaparecer un área.

### 7. ¿Cómo se actualizan las entidades de una instancia?

Dos caminos, ambos preservan pairing:

1. **Recarga completa (robusta, usada en v1):** actualizar `options[CONF_FILTER]` con `hass.config_entries.async_update_entry(...)` y luego `hass.config_entries.async_reload(entry_id)`. `async_unload_entry` para el driver (esperando liberación de puerto hasta `SHUTDOWN_TIMEOUT`=30 s) y `async_setup_entry` lo rearma cargando el `.state` y reutilizando los aids del `.aids` → los accesorios conservan su identidad en Apple Home.
2. **Recarga fina (optimización futura):** `async_dispatcher_send(hass, SIGNAL_RELOAD_ENTITIES.format(entry_id), (entity_id, ...))` → `HomeKit.async_reload_accessories` elimina y recrea en caliente solo esos accesorios, **sin tocar el driver ni el puerto**. No añade entidades nuevas ni elimina entidades no pasadas; sirve para mover/refresh de entidades ya presentes.

Para añadir/quitar entidades del conjunto de un área, v1 usa el **camino 1** (recarga completa del `ConfigEntry` del área afectada).

### 8. ¿Cómo se inicia y detiene una instancia?

- **Inicio:** `async_at_started(hass, HomeKit.async_start)`. `async_start` inicializa `AccessoryAidStorage`/`AccessoryIIDStorage`, ejecuta `HomeKit.setup` (crea `HomeDriver`, carga `.state` o genera MAC), crea los accesorios (`async_configure_accessories` + filtro), registra el dispositivo-bridge en el *device registry* y arranca `driver.async_start()`.
- **Parada:** `HomeKit.async_stop()` → `driver.async_stop()`. `async_unload_entry` llama a `async_stop` y luego aguarda `async_port_is_available(port)` hasta `SHUTDOWN_TIMEOUT`. También está bound a `EVENT_HOMEASSISTANT_STOP`.

### 9. ¿Cómo se gestiona el puerto?

- Constantes: `DEFAULT_PORT = 21063`, `DEFAULT_CONFIG_FLOW_PORT = 21064`.
- `entry.data[CONF_PORT]` almacena el puerto.
- `async_find_next_available_port(hass, start)` devuelve el primer puerto `>= start` que (a) no esté en los `CONF_PORT` de otras entradas `homekit` y (b) pase un `bind` real en un socket.
- Para **V1**, HomeKit Areas mantiene su propio mapping `area_id → port` (plan §14) y, al asignar un puerto nuevo, parte del **puerto inicial configurable (por defecto 21070)** y elige el siguiente libre que no esté en nuestro mapping ni en uso (comprobado con `async_port_is_available`). El puerto se persiste y **no se recalcula** por orden de áreas; los puertos liberados no se reutilizan en V1.

### 10. ¿Cómo evitar conflictos con otras instancias?

- Empezar en `21070+` (rango distinto de los bridges oficiales del usuario, típicamente `21063`/`21064`).
- Al asignar un puerto: excluir los `CONF_PORT` de **todas** las entradas `homekit` existentes (oficiales + nuestras) y verificar `bind` real.
- **No tocar nunca** las entradas `homekit` que no hayan sido creadas por HomeKit Areas (distinguidas vía nuestro store de `area_id → entry_id`). El §24 del plan ("ignorar bridges existentes") se cumple por construcción.

---

## 4. Solución elegida — detalles

### 4.1 Dos dominios de `ConfigEntry`

```text
homekit_areas  → 1 ConfigEntry (orquestador, configurado por el usuario)
homekit        → N ConfigEntry (uno por área, gestionados por BridgeManager)
```

El `ConfigEntry` de `homekit` por área se crea con:

```python
data = {
    CONF_NAME: "HomeKit Salón",  # saneado, ≤ 25 chars
    CONF_PORT: 21070,  # del mapping area_id → port
    CONF_HOMEKIT_MODE: HOMEKIT_MODE_BRIDGE,  # "bridge"
    CONF_EXCLUDE_ACCESSORY_MODE: True,  # no incluir cámaras/cerres/TVs en el bridge
    CONF_FILTER: {
        "include_entities": [  # solo las entidades del área ya filtradas
            "light.lampara_piano",
            "light.lampara_pie",
            ...,
        ]
    },
    CONF_ENTITY_CONFIG: {},
}
```

Vía:

```python
await hass.config_entries.flow.async_init(
    "homekit",
    context={
        "source": SOURCE_IMPORT
    },  # async_step_import crea la entrada con data completo
    data=data,
)
```

`async_step_import` valida unicidad de nombre/puerto (`_async_is_unique_name_port`) y crea la entrada. Usar `SOURCE_IMPORT` es lo único que permite inyectar un `data` completo sin UI; sus efectos laterales son **aceptables y deseados** (ver §4.3).

### 4.2 Identidad y reconciliación

`BridgeManager` mantiene un store propio (HA `Store` en `.storage/`) con:

```text
area_id  →  { entry_id: <homekit ConfigEntry id>, port: <int> }
```

Al arrancar (y ante cambios), reconcilia:

1. Para cada `area_id` gestionado: si `entry_id` existe y es una entrada `homekit` viva → reutilizar (preserva pairing).
2. Si falta → crear con `flow.async_init(..., SOURCE_IMPORT, data)` y registrar el nuevo `entry_id`+`port`.
3. Si un `area_id` ya no aplica → `hass.config_entries.async_remove(entry_id)` (borra entry + ficheros de persistencia) y limpiar el mapping.
4. Si las entidades cambiaron → `async_update_entry(options={CONF_FILTER: ...})` + `async_reload(entry_id)`.

### 4.3 Efectos laterales de `SOURCE_IMPORT` (aceptados)

- `_async_update_listener` retorna antes para entradas `import` → **no hay autorecarga** al cambiar `options`. El `BridgeManager` recarga manualmente (`async_reload`), que es exactamente el control que queremos.
- El `OptionsFlow` oficial muestra el paso `yaml` (no editable por UI) → **impide que el usuario rompa el filtro** desde la UI de HomeKit. Correcto: estos bridges los controla HomeKit Areas.
- El servicio `homekit.reload` (yaml) podría machacar entradas `import` cuyo nombre/puerto coincida con YAML. Como nuestros nombres (`HomeKit <área>`) y puertos (`21070+`) no colisionan con los defaults (`Home Assistant Bridge`/`21063`), el riesgo es nulo en la práctica. Se documenta.

### 4.4 Servicios oficiales aprovechados

- `homekit.reset_accessory` y `homekit.unpair` iteran **todas** las entradas `homekit`, incluidas las nuestras → el usuario puede desemparejar un bridge de área concreta sin salir del ecosistema oficial. Deseado.

---

## 5. Ciclo de vida de un bridge de área

```text
create_bridge(area)
  ├── asignar/leer puerto del mapping (area_id → port)
  ├── flow.async_init("homekit", source=IMPORT, data={name,port,mode,filter,exclude_accessory_mode})
  ├── guardar entry_id en el mapping
  └── HA ejecuta async_setup_entry → async_at_started → HomeKit.async_start

start_bridge(area)   → implícito en el setup de la entrada; async_start arranca el driver
stop_bridge(area)    → hass.config_entries.async_unload_entry(entry_id)  (para driver, libera puerto)
update_bridge(area)  → async_update_entry(options={CONF_FILTER: nuevas_entidades}) + async_reload(entry_id)
remove_bridge(area)  → hass.config_entries.async_remove(entry_id)  (para driver + borra .state/.aids/.iids)
```

`async_reload` = `unload_entry` + `setup_entry`: el driver se detiene y rearma, pero al reutilizar el mismo `entry_id`, `load()` recupera el `.state` (pairing) y el `.aids` (identidad de accesorios). **No se pierde el emparejamiento** al actualizar entidades.

---

## 6. Comportamiento ante los casos del plan

| Caso (plan.md) | Mecanismo |
|----------------|-----------|
| Mover entidad Salón→Dormitorio (§12, §17) | Actualizar `CONF_FILTER` de ambas entradas (quitar de una, añadir a la otra) + `async_reload` de ambas. El accesorio desaparece de un bridge y aparece en el otro con un *aid* nuevo en su `.aids`. Pairing de los **bridges** inalterado. |
| Nueva entidad en un área (§13) | `update_bridge(area)` con el nuevo `include_entities`. |
| Nueva área (§14) | `create_bridge(area)` + persistir mapping. |
| Área eliminada (§15) | `remove_bridge(area)` (=`async_remove`) + limpiar mapping. No tocar otros bridges. |
| Cambio de nombre del área (§16) | `async_update_entry(data={CONF_NAME: nuevo})` (mismo `entry_id`, mismo puerto, mismo `.state`) → solo cambia el nombre mDNS. **No crear bridge nuevo.** Pairing conservado. |
| Reinicio de HA (§17 Caso 5) | Reconciliación al arrancar: cada `area_id` reutiliza su `entry_id` → pairing, puertos y aids se conservan. |
| Renombrado del ConfigEntry del usuario | No afecta a las entradas hijas `homekit`. |

---

## 7. Riesgos y mitigaciones

| Riesgo | Mitigación |
|--------|------------|
| `SOURCE_IMPORT` etiqueta las entradas como "gestionadas por YAML" en la UI | Aceptado; impide ediciones manuales que romperían el filtro. Documentado en README. |
| Recarga completa por área = breve parada del HAP (hasta `SHUTDOWN_TIMEOUT`) | V1: recargar **una área a la vez** (o concurrencia limitada) para no saturar puertos/CPU. Futuro: usar `SIGNAL_RELOAD_ENTITIES` para moves sin reiniciar driver. |
| El usuario borra manualmente una entrada `homekit` nuestra | Reconciliación la detecta → se recrea (pérdida de pairing de esa área, esperada). |
| Colisión de nombre/puerto si el usuario crea un bridge oficial con igual nombre/puerto | `async_find_next_available_port` + saneo de nombre + unicidad validada en `async_step_import`. |
| Inestabilidad de APIs internas en futuras versiones de HA | Dependemos solo del schema de `ConfigEntry` y de `util.*` reexportadas. No instanciamos `HomeKit`/`HomeDriver`. |
| Muchas áreas ⇒ muchos `ConfigEntry`-s en `homekit` | Aceptable: el componente ya itera listas. El device registry mostrará un dispositivo-bridge por área (deseado). |

---

## 8. Alternativa considerada (descartada como primaria)

**Instanciar directamente `HomeKit`/`HomeDriver`/`HomeBridge`** dentro de `homekit_areas`, con nuestros propios `entry_id`-s estables y llamadas a `setup()`/`async_start()`/`async_stop()`.

- *Ventajas:* UI limpia (todo bajo `HomeKit Areas`), control total, sin efectos laterales de `SOURCE_IMPORT`.
- *Desventajas:* acoplamiento fuerte a constructores y lifecycle internos (`HomeKit.__init__`, `setup`, `_async_create_accessories`, registro en device registry, espera de puerto, init de stores), que cambian entre versiones de HA; reimplementación del `async_setup_entry` oficial; mayor superficie de fallo. El plan exige reutilizar la integración oficial y no improvisar.

Se mantiene como **plan B** si en Fase 7 (`BridgeManager`) la vía del `ConfigEntry` presentara un bloqueo no anticipado.

---

## 9. Comprobaciones previas a implementar `BridgeManager` (Fase 7)

Antes de escribir `bridge_manager.py`, verificar en un HA `2026.8.x` real:

1. `await hass.config_entries.flow.async_init("homekit", context={"source": SOURCE_IMPORT}, data=...)` crea la entrada y el bridge arranca con entidades filtradas por `include_entities`.
2. Tras `async_update_entry` + `async_reload`, el `.state` persistente mantiene el pairing (re-pairing no requerido).
3. `async_find_next_available_port(hass, 21070)` y `async_port_is_available` se comportan como se espera con bridges oficiales ya corriendo.
4. `hass.config_entries.async_remove(entry_id)` libera puerto y elimina los 3 ficheros `.storage/homekit.<entry_id>.*`.
5. `homekit.unpair` / `homekit.reset_accessory` cubren nuestras entradas.

Si todas pasan, se procede con `BridgeManager` según §4 y §5 de este documento. Si alguna falla de forma bloqueante, se documenta y se evalúa el *plan B* (§8).

---

## 10. Referencias del código fuente (rama `dev`)

- `homeassistant/components/homekit/__init__.py` — `HomeKit`, `async_setup_entry`, `async_unload_entry`, `async_remove_entry`, `BRIDGE_SCHEMA`, `_async_all_homekit_instances`, servicios.
- `homeassistant/components/homekit/const.py` — `DEFAULT_PORT`, `DEFAULT_CONFIG_FLOW_PORT`, `CONFIG_OPTIONS`, `SIGNAL_RELOAD_ENTITIES`, `HOMEKIT_MODE_*`, `CONF_*`.
- `homeassistant/components/homekit/util.py` — `async_find_next_available_port`, `async_port_is_available`, `remove_state_files_for_entry_id`, `get_persist_fullpath_for_entry_id`, `state_needs_accessory_mode`.
- `homeassistant/components/homekit/accessories.py` — `HomeAccessory`, `HomeBridge`, `HomeDriver`.
- `homeassistant/components/homekit/aidmanager.py` — `AccessoryAidStorage` (persistencia de aids por `entry_id`).
- `homeassistant/components/homekit/models.py` — `HomeKitEntryData`, `HomeKitConfigEntry`.
- `homeassistant/components/homekit/config_flow.py` — `async_step_import`, `_async_add_entries_for_accessory_mode_entities` (patrón de creación programática).
