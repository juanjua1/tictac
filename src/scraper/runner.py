from __future__ import annotations
from typing import Any, Dict, List, Optional
from pathlib import Path
from playwright.sync_api import Page, TimeoutError as PlaywrightTimeoutError
import time
from .extract import parse_number_es_ar


def _wait(page: Page, esperar: dict | None) -> None:
    if not esperar:
        return
    tipo = esperar.get("tipo")
    objetivo = esperar.get("objetivo", {})
    try:
        if tipo in ("elemento_visible", "elemento_habilitado"):
            texto = objetivo.get("por_texto")
            if texto:
                page.get_by_text(texto, exact=False).first.wait_for(state="visible", timeout=10000)
        elif tipo in ("lista_cargada", "tabla_visible"):
            titulo = objetivo.get("titulo_o_contenedor")
            if titulo:
                page.get_by_text(titulo, exact=False).first.wait_for(state="visible", timeout=15000)
        elif tipo == "navegacion":
            page.wait_for_load_state("networkidle", timeout=15000)
        else:
            page.wait_for_load_state("domcontentloaded", timeout=10000)
    except PlaywrightTimeoutError:
        pass


def _resolve_value(val: Any, context: Dict[str, Any]) -> Any:
    if isinstance(val, str):
        # reemplazos simples tipo {{dni}}
        return (
            val.replace("{{dni}}", str(context.get("dni", "")))
        )
    return val


def _do_action(page: Page, paso: dict, context: dict, dry_run: bool = False) -> None:
    accion = paso.get("accion")
    localizar = paso.get("localizar", {})

    if accion == "click":
        if not dry_run:
            _locate(page, localizar).click()
    elif accion == "select":
        # select puede ser en tab, radio, combobox
        elem = _locate(page, localizar)
        valor = paso.get("valor")
        role = localizar.get("role", "").lower()
        if not dry_run:
            if role == "combobox" and valor:
                elem.select_option(label=valor)
            else:
                elem.click()
    elif accion == "type":
        valor = _resolve_value(paso.get("valor", ""), context)
        if not dry_run:
            _locate(page, localizar).fill(str(valor))
    elif accion == "type_and_enter":
        valor = _resolve_value(paso.get("valor", ""), context)
        el = _locate(page, localizar)
        if not dry_run:
            el.fill(str(valor))
            el.press("Enter")
    elif accion == "press_enter":
        # si hay localizar, enfocar y Enter; si no, Enter global
        if not dry_run:
            if localizar:
                try:
                    _locate(page, localizar).focus()
                except Exception:
                    pass
            page.keyboard.press("Enter")
    elif accion == "select_index":
        # seleccionar item por indice dentro de una lista contenedora
        indice = paso.get("indice", 0)
        if not dry_run:
            _select_index(page, localizar, indice)


def _locate(page: Page, localizar: dict):
    # Estrategia simple basada en llaves del YAML ya presentes
    if not localizar:
        return page.locator("body")
    # Alternativas de localización (probar en orden)
    if "alternativas" in localizar and isinstance(localizar["alternativas"], list):
        for alt in localizar["alternativas"]:
            try:
                loc = _locate(page, alt)
                if loc and loc.count() > 0:
                    return loc
            except Exception:
                continue
        # si ninguna funcionó, caer a un fallback por texto si existe
    if "por_texto" in localizar:
        return page.get_by_text(localizar["por_texto"], exact=False).first
    # etiqueta/label (incluye aria-label)
    if "etiqueta" in localizar:
        role = (localizar.get("role") or "").split("|")[0]
        loc = page.get_by_label(localizar["etiqueta"], exact=False)
        if role:
            try:
                return loc.get_by_role(role)
            except Exception:
                return loc
        return loc
    if "aria_label" in localizar:
        return page.get_by_label(localizar["aria_label"], exact=False)
    if "tooltip" in localizar:
        tip = localizar["tooltip"]
        return page.locator(f"[title*='{tip}']").first
    if "role" in localizar and localizar.get("por_texto"):
        roles = str(localizar["role"]).split("|")
        for r in roles:
            try:
                return page.get_by_role(r, name=localizar["por_texto"], exact=False)
            except Exception:
                continue
    if "tabla" in localizar:
        # Simplificación: buscar por título de la tabla y luego el primer link/row
        tabla = localizar["tabla"]
        titulo = tabla.get("titulo")
        if titulo:
            cont = page.get_by_text(titulo, exact=False).first
            return cont
    if "lista" in localizar:
        lista = localizar["lista"]
        cont_titulo = lista.get("contenedor_por_titulo")
        if cont_titulo:
            return page.get_by_text(cont_titulo, exact=False).first
    # fallback
    return page.locator("*", has_text=localizar.get("por_texto", "")).first


def _select_index(page: Page, localizar: dict, indice: int = 0) -> None:
    cont = _locate(page, localizar)
    # buscar filas o items dentro del contenedor
    target = None
    try:
        rows = cont.get_by_role("row")
        if rows.count() > indice:
            target = rows.nth(indice)
    except Exception:
        target = None
    if target is None:
        try:
            items = cont.locator("tr, li, div[role='listitem']")
            if items.count() > indice:
                target = items.nth(indice)
        except Exception:
            target = None
    if target is None:
        # último intento: primer link o div clickable
        items = cont.locator("a, button, div, span")
        if items.count() > indice:
            target = items.nth(indice)
    if target is not None:
        target.click()


def _execute_alternatives(page: Page, paso: dict, context: dict, dry_run: bool = False) -> None:
    alternativas = paso.get("alternativas", []) or []
    preferencia = paso.get("preferencia")
    # reordenar si hay preferencia
    if preferencia:
        alternativas = sorted(alternativas, key=lambda a: 0 if a.get("tipo") == preferencia else 1)
    for alt in alternativas:
        tipo = alt.get("tipo")
        try:
            if tipo == "enter":
                if not dry_run:
                    # si hay localizar en la alternativa, enfocarlo
                    loc = alt.get("localizar")
                    if loc:
                        try:
                            _locate(page, loc).focus()
                        except Exception:
                            pass
                    page.keyboard.press("Enter")
                return
            elif tipo == "click":
                if not dry_run:
                    _locate(page, alt.get("localizar", {})).click()
                return
            elif tipo == "type_and_enter":
                val = _resolve_value(alt.get("valor", ""), context)
                el = _locate(page, alt.get("localizar", {}))
                if not dry_run:
                    el.fill(str(val))
                    el.press("Enter")
                return
        except Exception:
            # probar siguiente alternativa
            continue


def _screenshot_element(page: Page, objetivo: dict, path: str) -> None:
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    # Heurística: si hay etiquetas clave, tomamos el contenedor por el texto principal
    if objetivo and "region_por_anclas" in objetivo:
        # intentar por la primera ancla
        anchors = objetivo["region_por_anclas"]
        if anchors:
            label = anchors[0].get("etiqueta") or ""
            page.get_by_text(label, exact=False).first.screenshot(path=path)
            return
    page.screenshot(path=path, full_page=False)


def run_flow(page: Page, flow: Dict[str, Any], dni: str, dry_run: bool = False, step_delay_ms: int = 0) -> Dict[str, Any]:
    resultados: Dict[str, Any] = {"dni": dni, "resultados_cf": []}
    pasos: List[dict] = flow.get("pasos", [])

    i = 0
    while i < len(pasos):
        paso = pasos[i]
        pid = paso.get("id", f"paso_{i}")
        # Condiciones simples omitidas por ahora; ejecutar secuencia base
        if paso.get("tipo") == "loop":
            # Implementación específica para el loop de CF con saldo del flow_spect10
            # 1) Asumimos que la tabla ya está visible (Lista de Cuenta financiera)
            # 2) Simularemos una única iteración placeholder (hasta implementar selectores de filas reales)
            pasos_loop = paso.get("pasos_loop", [])
            # En un caso real: iterar filas filtradas; por ahora, intentamos 1 pasada segura
            for lp in pasos_loop:
                if lp.get("id") == "extraer_y_capturar_cf_actual":
                    # extraer saldo y cf_id si visibles; captura encabezado
                    extr = lp.get("extraccion", {})
                    cap = lp.get("captura", {})
                    cf_id = "CF"
                    saldo_txt = None
                    # Heurística: buscar texto visible "Saldo"
                    if not dry_run:
                        try:
                            saldo_txt = page.get_by_text("Saldo", exact=False).locator("xpath=following::*").first.inner_text(timeout=2000)
                        except Exception:
                            saldo_txt = None
                    saldo_num = parse_number_es_ar(saldo_txt or "") if saldo_txt else None
                    out_path = cap.get("archivo", f"capturas/{dni}_saldo_cf_{cf_id}.png")
                    if not dry_run:
                        _screenshot_element(page, cap.get("objetivo", {}), out_path)
                    resultados["resultados_cf"].append({
                        "cf_id": cf_id,
                        "cf_nombre": None,
                        "saldo_texto": saldo_txt,
                        "saldo_numero": saldo_num,
                        "screenshot_path": out_path,
                    })
                # delay entre subpasos del loop
                if step_delay_ms and not dry_run:
                    time.sleep(step_delay_ms / 1000.0)
                elif lp.get("id") == "abrir_cf_actual":
                    # Haríamos click en la fila filtrada; placeholder noop
                    pass
                elif lp.get("id") == "volver_a_resumen_y_reabrir_lista":
                    # Por ahora noop; el flujo real volverá y reabrirá lista
                    pass
            # Al terminar el loop, saltar a siguiente paso
            i += 1
            continue

        # Paso normal: localizar/accionar/esperar
        try:
            context = {"dni": dni}
            if paso.get("alternativas") and not paso.get("accion"):
                _execute_alternatives(page, paso, context, dry_run=dry_run)
            elif paso.get("localizar") and paso.get("accion"):
                _do_action(page, paso, context, dry_run=dry_run)
            if paso.get("esperar") and not dry_run:
                _wait(page, paso.get("esperar"))
        except Exception:
            # No frenamos por ahora, seguimos para completar skeleton
            pass
        # delay entre pasos
        if step_delay_ms and not dry_run:
            time.sleep(step_delay_ms / 1000.0)
        i += 1

    return resultados
