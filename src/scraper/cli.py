from __future__ import annotations
import argparse
from rich import print
from pathlib import Path
from .flow_loader import load_flow
from .browser import launch_browser
from .runner import run_flow
from dotenv import load_dotenv


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Scraper T3.0 por DNI")
    p.add_argument("--dni", required=True, help="DNI a consultar, ej 2994****")
    p.add_argument("--flow", default="flow_spect10.yaml", help="Ruta al YAML de flujo (por defecto usa el empaquetado)")
    p.add_argument("--portal-url", dest="portal_url", default=None, help="URL del portal (sobrescribe meta.portal_url del YAML o .env)")
    p.add_argument("--head", dest="head", action="store_true", help="Mostrar navegador")
    p.add_argument("--no-head", dest="head", action="store_false", help="Headless")
    p.set_defaults(head=True)
    p.add_argument("--slowmo", type=int, default=0, help="Delay ms entre acciones")
    p.add_argument("--dry-run", action="store_true", help="No ejecutar acciones, solo simular y validar YAML")
    p.add_argument("--check-vpn", action="store_true", help="Verifica que el portal sea alcanzable (VPN activa)")
    p.add_argument("--vpn-wait", type=int, default=0, help="Esperar hasta N segundos a que el portal sea alcanzable")
    p.add_argument("--install-browsers", action="store_true", help="Instala navegadores de Playwright y sale")
    p.add_argument("--step-delay", type=int, default=0, help="Pausa fija (ms) entre pasos")
    p.add_argument("--visual", action="store_true", help="Ejecutar en modo visual (controlando AnyDesk con anclas en capturas/")
    return p.parse_args()


def main() -> int:
    args = parse_args()
    load_dotenv()
    # Cargar el flujo; si falla, informar rutas intentadas desde el loader
    try:
        flow = load_flow(args.flow)
    except FileNotFoundError as e:
        print(f"[red]{e}[/]")
        return 2
    # Resolver portal_url: prioridad CLI > .env > YAML
    env_portal = None
    try:
        import os
        env_portal = os.getenv("PORTAL_URL")
    except Exception:
        env_portal = None
    resolved_portal_url = args.portal_url or env_portal or flow.meta.get("portal_url")
    if args.install_browsers:
        print("[cyan]Instalando navegadores de Playwright...[/]")
        try:
            from playwright.__main__ import main as playwright_main
            playwright_main(["install", "--with-deps"])
            print("[green]OK[/] Navegadores instalados")
            return 0
        except Exception as e:
            print(f"[red]Error instalando navegadores:[/] {e}")
            return 2

    print(f"[bold cyan]Cargando flujo[/] {flow} - portal: {resolved_portal_url or '<sin url>'}")

    # Modo visual (automatización por pantalla, sin navegador)
    if args.visual:
        try:
            from ..visual.runner_visual import main as visual_main
        except Exception as e:
            print(f"[red]No se pudo cargar el runner visual:[/] {e}")
            print("Instalá dependencias: pyautogui, opencv-python y asegurá X11 activo.")
            return 2
        rc = visual_main()
        return rc

    # Apertura de navegador (validación de entorno VPN y Playwright)
    with launch_browser(head=args.head, slowmo=args.slowmo) as ((_, __, page)):
        portal_url = resolved_portal_url
        if not portal_url or portal_url == "<completar>":
            print("[yellow]Advertencia:[/] meta.portal_url no configurado; ejecutaré en modo dry-run.")
            args.dry_run = True
        else:
            # Pre-chequeo de VPN/portal si se solicita
            if args.check_vpn or args.vpn_wait > 0:
                import time

                def reachable(timeout_ms: int = 5000) -> bool:
                    try:
                        page.goto(portal_url, wait_until="domcontentloaded", timeout=timeout_ms)
                        return True
                    except Exception:
                        return False

                if args.vpn_wait > 0:
                    print(f"[cyan]Esperando VPN/portal hasta[/] {args.vpn_wait}s -> {portal_url}")
                    deadline = time.time() + args.vpn_wait
                    ok = False
                    while time.time() < deadline:
                        if reachable():
                            ok = True
                            break
                        time.sleep(5)
                    if not ok:
                        print("[red]No se pudo alcanzar el portal dentro del tiempo de espera.[/]")
                        return 2
                    print("[green]Portal alcanzable.[/]")
                else:
                    if not reachable():
                        print("[red]Portal no alcanzable. Conectá la VPN o revisá la URL.[/]")
                        return 2
                    print("[green]Portal alcanzable.[/]")
            else:
                print(f"[green]Abriendo[/] {portal_url}")
                page.goto(portal_url)
        resultados = run_flow(
            page,
            flow.data,
            dni=args.dry_run and "00000000" or args.dni,
            dry_run=args.dry_run,
            step_delay_ms=args.step_delay,
        )
        if args.dry_run:
            print("[bold cyan]Dry-run:[/] simulación completada, sin acciones reales.")
        else:
            print("[bold green]Finalizado[/] Flujo ejecutado")
        # Mostrar resumen breve
        rc = resultados.get("resultados_cf", [])
        print(f"[cyan]CF con saldo extraídas:[/] {len(rc)}")

    print("[bold green]OK[/] Sesión finalizada")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
