# Tests manuales — HomeKit Areas

Gate de avance: **no pasar a la siguiente fase hasta que todos los tests de la fase actual estén marcados.**

Formato de cada test:
- `[ ]` Pendiente
- `[x]` Completado

---

## Fase 1 — Esqueleto

> Verificar que la integración aparece en Home Assistant, se instala, abre Config Flow, crea una Config Entry, se recarga correctamente.

### Test 1.1 — Añadir repositorio a HACS

- [x] **Paso 1:** En Home Assistant, ir a HACS
- [x] **Paso 2:** Pulsar los tres puntos (arriba a la derecha) → "Repositorios personalizados"
- [x] **Paso 3:** Pegar la URL del repositorio (`https://github.com/Seoane8/homekit-areas`)
- [x] **Paso 4:** Seleccionar categoría: "Integración"
- [x] **Paso 5:** Pulsar "Añadir"
- [x] **Resultado esperado:** El repositorio aparece en la lista de personalizados

### Test 1.2 — Instalar desde HACS

- [x] **Paso 1:** En HACS, buscar "HomeKit Areas"
- [x] **Paso 2:** Pulsar sobre la integración
- [x] **Paso 3:** Pulsar "Descargar"
- [x] **Paso 4:** Reiniciar Home Assistant cuando se solicite
- [x] **Resultado esperado:** La integración se instala correctamente

### Test 1.3 — Verificar que la integración aparece

- [x] **Paso 1:** Ir a Ajustes → Dispositivos y servicios
- [x] **Paso 2:** Pulsar "Añadir integración"
- [x] **Paso 3:** Buscar "HomeKit Areas"
- [x] **Resultado esperado:** La integración "HomeKit Areas" aparece en la lista

### Test 1.4 — Completar el Config Flow (Fase 1)

- [x] **Paso 1:** Seleccionar "HomeKit Areas" de la lista
- [x] **Paso 2:** Verificar que se muestra un formulario
- [x] **Paso 3:** Pulsar "Enviar"
- [x] **Resultado esperado:** Se crea la entrada con título "HomeKit Areas"

### Test 1.5 — Verificar que la entrada se creó

- [x] **Paso 1:** En "Dispositivos y servicios", pestaña "Integraciones"
- [x] **Paso 2:** Buscar "HomeKit Areas"
- [x] **Resultado esperado:** La entrada aparece con título "HomeKit Areas" y estado "Cargado"

### Test 1.6 — Verificar que solo se permite una instancia

- [x] **Paso 1:** Pulsar "Añadir integración" de nuevo
- [x] **Paso 2:** Buscar "HomeKit Areas"
- [x] **Paso 3:** Intentar añadir una segunda instancia
- [x] **Resultado esperado:** El flujo se aborta con el mensaje "Solo se permite una configuración de HomeKit Areas."

### Test 1.7 — Recargar la integración

- [x] **Paso 1:** En la entrada de "HomeKit Areas", pulsar el menú (tres puntos)
- [x] **Paso 2:** Seleccionar "Recargar"
- [x] **Resultado esperado:** La integración se recarga, no hay errores en el log

---

## Fase 2 — Config Flow

> Verificar el flujo completo de configuración (áreas, puerto, dominios, entidades excluidas).

### Test 2.1 — Eliminar la entrada de Fase 1

- [x] **Paso 1:** En "Dispositivos y servicios", eliminar la entrada de "HomeKit Areas"
- [x] **Paso 2:** Confirmar la eliminación
- [x] **Resultado esperado:** La entrada se elimina

### Test 2.2 — Config Flow: selección de áreas

- [x] **Paso 1:** Añadir integración → "HomeKit Areas"
- [x] **Paso 2:** Verificar que se muestra un selector de áreas (Todas / Seleccionar)
- [x] **Paso 3:** Seleccionar "Seleccionar"
- [x] **Paso 4:** Verificar que se muestra el selector de áreas
- [x] **Paso 5:** Marcar algunas áreas (ej: Salón, Cocina)
- [x] **Paso 6:** Pulsar "Siguiente"
- [x] **Resultado esperado:** Se avanza al paso de puerto

### Test 2.3 — Config Flow: puerto inicial

- [x] **Paso 1:** Verificar que se muestra un campo "Puerto inicial" con valor por defecto `21070`
- [x] **Paso 2:** Pulsar "Siguiente"
- [x] **Resultado esperado:** Se avanza al paso de dominios

### Test 2.4 — Config Flow: dominios

- [x] **Paso 1:** Verificar que se muestra un selector múltiple de dominios
- [x] **Paso 2:** Verificar que los dominios por defecto están marcados (light, switch, fan, cover)
- [x] **Paso 3:** Pulsar "Siguiente"
- [x] **Resultado esperado:** Se avanza al paso de entidades excluidas

### Test 2.5 — Config Flow: entidades excluidas

- [x] **Paso 1:** Verificar que se muestra un selector de entidades
- [x] **Paso 2:** Pulsar "Enviar"
- [x] **Resultado esperado:** Se crea la entrada con la configuración

### Test 2.6 — Verificar que la configuración se guardó

- [x] **Paso 1:** En la entrada de "HomeKit Areas", pulsar "Configurar"
- [x] **Paso 2:** Verificar que se muestran las opciones guardadas
- [x] **Resultado esperado:** Las opciones coinciden con lo configurado

---

## Fase 3 — Options Flow

> Verificar que se pueden modificar las opciones después de la configuración inicial.

### Test 3.1 — Verificar que existe la opción "Configurar"

- [x] **Paso 1:** En la entrada de "HomeKit Areas", verificar que aparece el botón "Configurar"
- [x] **Resultado esperado:** El botón "Configurar" está disponible

### Test 3.2 — Modificar áreas

- [x] **Paso 1:** Pulsar "Configurar"
- [x] **Paso 2:** Cambiar la selección de áreas (añadir/quitar alguna)
- [x] **Paso 3:** Pulsar "Guardar"
- [x] **Resultado esperado:** Las opciones se actualizan

### Test 3.3 — Modificar puerto inicial

- [x] **Paso 1:** Pulsar "Configurar"
- [x] **Paso 2:** Cambiar el puerto inicial
- [x] **Paso 3:** Pulsar "Guardar"
- [x] **Resultado esperado:** El puerto se actualiza

### Test 3.4 — Modificar dominios

- [x] **Paso 1:** Pulsar "Configurar"
- [x] **Paso 2:** Cambiar los dominios seleccionados
- [x] **Paso 3:** Pulsar "Guardar"
- [x] **Resultado esperado:** Los dominios se actualizan

### Test 3.5 — Modificar entidades excluidas

- [x] **Paso 1:** Pulsar "Configurar"
- [x] **Paso 2:** Cambiar las entidades excluidas
- [x] **Paso 3:** Pulsar "Guardar"
- [x] **Resultado esperado:** Las exclusiones se actualizan

---

## Fase 4 — Modelo de datos

> Verificar que el modelo de datos representa correctamente los bridges.

### Test 4.1 — Verificar estructura del modelo

- [x] **Paso 1:** Revisar `custom_components/homekit_areas/models.py`
- [x] **Paso 2:** Verificar que existe una clase `AreaBridge`
- [x] **Paso 3:** Verificar que tiene campos: `area_id`, `name`, `port`, `entities`
- [x] **Resultado esperado:** El modelo está definido correctamente

---

## Fase 5 — Area Manager

> Verificar que se descubren las áreas de Home Assistant correctamente.

### Test 5.1 — Descubrimiento de áreas

- [x] **Paso 1:** Configurar la integración con "Todas las áreas"
- [x] **Paso 2:** Verificar en los logs que se descubren todas las áreas de HA
- [x] **Resultado esperado:** Se listan todas las áreas con sus `area_id` y nombres

### Test 5.2 — Detección de nueva área

- [x] **Paso 1:** Crear una nueva área en HA (ej: "Oficina")
- [x] **Paso 2:** Verificar en los logs que se detecta la nueva área
- [x] **Resultado esperado:** La nueva área aparece en la lista de áreas gestionadas

### Test 5.3 — Detección de área eliminada

- [x] **Paso 1:** Eliminar un área en HA
- [x] **Paso 2:** Verificar en los logs que se detecta la eliminación
- [x] **Resultado esperado:** El área eliminada desaparece de la lista

### Test 5.4 — Detección de cambio de nombre

- [x] **Paso 1:** Renombrar un área en HA (ej: "Salón" → "Sala de estar")
- [x] **Paso 2:** Verificar en los logs que se detecta el cambio de nombre
- [x] **Resultado esperado:** El nombre se actualiza, el `area_id` permanece igual

---

## Fase 6 — Entity Filter

> Verificar que el filtrado de entidades funciona correctamente.

### Test 6.1 — Filtrado por dominios

- [x] **Paso 1:** Configurar dominios: `light`, `switch`
- [x] **Paso 2:** Verificar que solo se incluyen entidades de esos dominios
- [x] **Resultado esperado:** Entidades de otros dominios (ej: `sensor`) se excluyen

### Test 6.2 — Filtrado por entidades excluidas

- [x] **Paso 1:** Configurar entidades excluidas: `light.lampara_pie`
- [x] **Paso 2:** Verificar que esa entidad se excluye
- [x] **Resultado esperado:** La entidad excluida no aparece en el bridge

### Test 6.3 — Pipeline completo

- [x] **Paso 1:** Configurar dominios + exclusiones
- [x] **Paso 2:** Verificar que el pipeline funciona: entidades del área → dominios permitidos → entidades excluidas → entidades válidas
- [x] **Resultado esperado:** Solo las entidades válidas pasan el filtro

---

## Fase 7 — Bridge Manager

> Verificar que se crean los bridges HomeKit por área.

### Test 7.1 — Creación de ConfigEntry de HomeKit

- [ ] **Paso 1:** Configurar la integración con áreas seleccionadas
- [ ] **Paso 2:** Verificar en "Dispositivos y servicios" que aparecen entradas del dominio `homekit`
- [ ] **Paso 3:** Verificar que cada entrada tiene el nombre "HomeKit <área>"
- [ ] **Resultado esperado:** Se crea una entrada `homekit` por área gestionada

### Test 7.2 — Arranque del bridge

- [ ] **Paso 1:** Verificar en los logs que cada bridge arranca
- [ ] **Paso 2:** Verificar que se asigna un puerto a cada bridge
- [ ] **Resultado esperado:** Los bridges arrancan en los puertos esperados

---

## Fase 8 — Persistencia de puertos

> Verificar que los puertos persisten entre reinicios.

### Test 8.1 — Asignación de puertos

- [ ] **Paso 1:** Configurar puerto inicial `21070`
- [ ] **Paso 2:** Verificar que las áreas reciben puertos consecutivos (21070, 21071, 21072...)
- [ ] **Resultado esperado:** Los puertos se asignan correctamente

### Test 8.2 — Persistencia tras reinicio

- [ ] **Paso 1:** Reiniciar Home Assistant
- [ ] **Paso 2:** Verificar que los puertos se mantienen
- [ ] **Resultado esperado:** Los puertos no cambian tras reiniciar

### Test 8.3 — No reutilización de puertos liberados

- [ ] **Paso 1:** Eliminar un área (ej: Cocina, puerto 21071)
- [ ] **Paso 2:** Verificar que el puerto 21071 no se reasigna a otra área
- [ ] **Resultado esperado:** El puerto liberado no se reutiliza en V1

---

## Fase 9 — Primer Bridge

> Verificar que el primer bridge funciona completamente.

### Test 9.1 — Arranque del bridge

- [ ] **Paso 1:** Configurar una sola área (ej: Salón)
- [ ] **Paso 2:** Verificar que el bridge arranca en el puerto asignado
- [ ] **Resultado esperado:** El bridge está activo

### Test 9.2 — Pairing con Apple Home

- [ ] **Paso 1:** Abrir la app Casa en iOS/macOS
- [ ] **Paso 2:** Pulsar "+" → "Añadir accesorio"
- [ ] **Paso 3:** Escanear el código QR o introducir el PIN
- [ ] **Resultado esperado:** El bridge se empareja correctamente

### Test 9.3 — Luces independientes

- [ ] **Paso 1:** Verificar que las luces del área aparecen en Apple Home
- [ ] **Paso 2:** Verificar que cada luz es independiente (no agrupada)
- [ ] **Paso 3:** Controlar cada luz individualmente
- [ ] **Resultado esperado:** Las luces funcionan de forma independiente

### Test 9.4 — Reinicio conserva pairing

- [ ] **Paso 1:** Reiniciar Home Assistant
- [ ] **Paso 2:** Verificar en Apple Home que el bridge sigue disponible
- [ ] **Paso 3:** Verificar que no se requiere volver a emparejar
- [ ] **Resultado esperado:** El pairing se conserva

---

## Fase 10 — Múltiples Bridges

> Verificar que múltiples bridges funcionan simultáneamente.

### Test 10.1 — Múltiples bridges activos

- [ ] **Paso 1:** Configurar varias áreas (Salón, Cocina, Dormitorio)
- [ ] **Paso 2:** Verificar que cada bridge arranca en su puerto
- [ ] **Resultado esperado:** Todos los bridges están activos

### Test 10.2 — Pairing independiente

- [ ] **Paso 1:** Emparejar cada bridge en Apple Home
- [ ] **Paso 2:** Verificar que cada bridge tiene su propio PIN
- [ ] **Resultado esperado:** Cada bridge se empareja independientemente

### Test 10.3 — Entidades independientes

- [ ] **Paso 1:** Verificar que las entidades de cada área aparecen en su bridge correspondiente
- [ ] **Paso 2:** Verificar que no hay duplicados
- [ ] **Resultado esperado:** Cada entidad está en su bridge correcto

---

## Fase 11 — Detección de cambios

> Verificar que se detectan cambios en el registro de dispositivos.

### Test 11.1 — Detección de cambio de área

- [ ] **Paso 1:** Mover una entidad a otra área en HA
- [ ] **Paso 2:** Verificar en los logs que se detecta el evento `device_registry_updated`
- [ ] **Resultado esperado:** El cambio se detecta automáticamente

---

## Fase 12 — Cambio de área

> Verificar que mover una entidad entre áreas funciona sin reiniciar.

### Test 12.1 — Mover entidad entre áreas

- [ ] **Paso 1:** Mover `light.lampara_pie` de Salón a Dormitorio
- [ ] **Paso 2:** Verificar que desaparece del bridge Salón
- [ ] **Paso 3:** Verificar que aparece en el bridge Dormitorio
- [ ] **Paso 4:** Verificar que no se pierde el pairing de los bridges
- [ ] **Resultado esperado:** La entidad se mueve sin reiniciar HA

---

## Fase 13 — Nuevas entidades

> Verificar que las nuevas entidades se añaden automáticamente.

### Test 13.1 — Nueva entidad en un área

- [ ] **Paso 1:** Añadir una nueva luz al área Salón
- [ ] **Paso 2:** Verificar que aparece automáticamente en el bridge Salón
- [ ] **Resultado esperado:** La nueva entidad se añade sin reiniciar

---

## Fase 14 — Nuevas áreas

> Verificar que las nuevas áreas se gestionan automáticamente.

### Test 14.1 — Crear nueva área

- [ ] **Paso 1:** Crear un área "Oficina" en HA
- [ ] **Paso 2:** Verificar que se crea automáticamente un bridge "HomeKit Oficina"
- [ ] **Paso 3:** Verificar que se le asigna un puerto
- [ ] **Resultado esperado:** El nuevo bridge arranca automáticamente

---

## Fase 15 — Eliminación de áreas

> Verificar que los bridges se eliminan cuando se eliminan las áreas.

### Test 15.1 — Eliminar área

- [ ] **Paso 1:** Eliminar un área en HA
- [ ] **Paso 2:** Verificar que el bridge correspondiente se detiene
- [ ] **Paso 3:** Verificar que el puerto se libera (pero no se reutiliza)
- [ ] **Resultado esperado:** El bridge se elimina limpiamente

---

## Fase 16 — Cambios de nombre

> Verificar que renombrar un área no crea un bridge nuevo.

### Test 16.1 — Renombrar área

- [ ] **Paso 1:** Renombrar "Salón" a "Sala de estar"
- [ ] **Paso 2:** Verificar que el bridge cambia de nombre
- [ ] **Paso 3:** Verificar que el `area_id`, puerto y pairing se conservan
- [ ] **Paso 4:** Verificar que no se crea un bridge nuevo
- [ ] **Resultado esperado:** Solo cambia el nombre, todo lo demás se conserva

---

## Fase 17 — Apple Home

> Verificar la integración completa con Apple Home.

### Test 17.1 — Primer pairing

- [ ] **Paso 1:** Emparejar un bridge en Apple Home
- [ ] **Paso 2:** Verificar que funciona correctamente
- [ ] **Resultado esperado:** El pairing es exitoso

### Test 17.2 — Cambios posteriores

- [ ] **Paso 1:** Mover entidades entre áreas
- [ ] **Paso 2:** Verificar que no se pierde pairing
- [ ] **Paso 3:** Verificar que no aparecen duplicados
- [ ] **Paso 4:** Verificar que los accesorios se mueven al bridge correcto
- [ ] **Resultado esperado:** Todo funciona sin problemas

---

## Fase 18 — Tests + HACS + Release

> Verificación final antes del release.

### Test 18.1 — GitHub Actions

- [ ] **Paso 1:** Hacer push a la rama principal
- [ ] **Paso 2:** Verificar que GitHub Actions ejecuta pytest y ruff
- [ ] **Paso 3:** Verificar que todos los tests pasan
- [ ] **Resultado esperado:** CI verde

### Test 18.2 — Instalación vía HACS (nueva versión)

- [ ] **Paso 1:** Actualizar la integración desde HACS
- [ ] **Paso 2:** Reiniciar HA
- [ ] **Resultado esperado:** La integración se actualiza y funciona

### Test 18.3 — Criterios de aceptación v1.0.0

- [ ] **Paso 1:** Verificar Caso 1 — Configuración inicial
- [ ] **Paso 2:** Verificar Caso 2 — Mover una entidad
- [ ] **Paso 3:** Verificar Caso 3 — Crear un área
- [ ] **Paso 4:** Verificar Caso 4 — Renombrar un área
- [ ] **Paso 5:** Verificar Caso 5 — Reiniciar Home Assistant
- [ ] **Resultado esperado:** Todos los casos funcionan correctamente

---

## Resumen

| Fase | Tests | Completados |
|------|-------|-------------|
| 1 | 7 | 7/7 |
| 2 | 6 | 6/6 |
| 3 | 5 | 5/5 |
| 4 | 1 | 1/1 |
| 5 | 4 | 0/4 |
| 6 | 3 | 3/3 |
| 7 | 2 | 2/2 |
| 8 | 3 | 0/3 |
| 9 | 4 | 0/4 |
| 10 | 3 | 0/3 |
| 11 | 1 | 0/1 |
| 12 | 1 | 0/1 |
| 13 | 1 | 0/1 |
| 14 | 1 | 0/1 |
| 15 | 1 | 0/1 |
| 16 | 1 | 0/1 |
| 17 | 2 | 0/2 |
| 18 | 3 | 0/3 |
| **Total** | **49** | **24/49** |
