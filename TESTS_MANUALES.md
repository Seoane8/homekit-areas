# Tests manuales — HomeKit Areas

Gate de avance: **no pasar a la siguiente fase hasta que todos los tests de la fase actual estén marcados.**

Formato de cada test:
- `[ ]` Pendiente
- `[x]` Completado

---

## Fase 5 — Area Manager

> Verificar que se descubren las áreas de Home Assistant correctamente.

### Test 5.1 — Descubrimiento de áreas

- [ ] **Paso 1:** Configurar la integración con "Todas las áreas"
- [ ] **Paso 2:** Verificar en los logs que se descubren todas las áreas de HA
- [ ] **Resultado esperado:** Se listan todas las áreas con sus `area_id` y nombres

### Test 5.2 — Detección de nueva área

- [ ] **Paso 1:** Crear una nueva área en HA (ej: "Oficina")
- [ ] **Paso 2:** Verificar en los logs que se detecta la nueva área
- [ ] **Resultado esperado:** La nueva área aparece en la lista de áreas gestionadas

### Test 5.3 — Detección de área eliminada

- [ ] **Paso 1:** Eliminar un área en HA
- [ ] **Paso 2:** Verificar en los logs que se detecta la eliminación
- [ ] **Resultado esperado:** El área eliminada desaparece de la lista

### Test 5.4 — Detección de cambio de nombre

- [ ] **Paso 1:** Renombrar un área en HA (ej: "Salón" → "Sala de estar")
- [ ] **Paso 2:** Verificar en los logs que se detecta el cambio de nombre
- [ ] **Resultado esperado:** El nombre se actualiza, el `area_id` permanece igual

---

## Fase 6 — Entity Filter

> Verificar que el filtrado de entidades funciona correctamente.

### Test 6.1 — Filtrado por dominios

- [ ] **Paso 1:** Configurar dominios: `light`, `switch`
- [ ] **Paso 2:** Verificar que solo se incluyen entidades de esos dominios
- [ ] **Resultado esperado:** Entidades de otros dominios (ej: `sensor`) se excluyen

### Test 6.2 — Filtrado por entidades excluidas

- [ ] **Paso 1:** Configurar entidades excluidas: `light.lampara_pie`
- [ ] **Paso 2:** Verificar que esa entidad se excluye
- [ ] **Resultado esperado:** La entidad excluida no aparece en el bridge

### Test 6.3 — Pipeline completo

- [ ] **Paso 1:** Configurar dominios + exclusiones
- [ ] **Paso 2:** Verificar que el pipeline funciona: entidades del área → dominios permitidos → entidades excluidas → entidades válidas
- [ ] **Resultado esperado:** Solo las entidades válidas pasan el filtro

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

### Test 18.2 — Instalación vía HACS

- [ ] **Paso 1:** Añadir el repositorio a HACS
- [ ] **Paso 2:** Instalar la integración desde HACS
- [ ] **Paso 3:** Reiniciar HA
- [ ] **Resultado esperado:** La integración se instala y funciona

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
| 5 | 4 | 0/4 |
| 6 | 3 | 0/3 |
| 7 | 2 | 0/2 |
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
| **Total** | **30** | **0/30** |
