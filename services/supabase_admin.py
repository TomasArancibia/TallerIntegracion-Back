import os

import requests


class SupabaseAdminError(Exception):
    """Error al interactuar con la API Admin de Supabase."""


def _get_base_url() -> str:
    base_url = os.getenv("SUPABASE_URL")
    if not base_url:
        raise SupabaseAdminError("SUPABASE_URL no está configurada.")
    return base_url.rstrip("/")


def _get_service_key() -> str:
    key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
    if not key:
        raise SupabaseAdminError("SUPABASE_SERVICE_ROLE_KEY no está configurada.")
    return key


def create_auth_user(email: str, password: str) -> dict:
    """
    Crea un usuario en Supabase Auth usando la API Admin.

    Retorna el diccionario con la información del usuario creado.
    """
    base_url = _get_base_url()
    service_key = _get_service_key()

    url = f"{base_url}/auth/v1/admin/users"
    payload = {
        "email": email,
        "password": password,
        "email_confirm": True,
    }

    headers = {
        "Content-Type": "application/json",
        "apikey": service_key,
        "Authorization": f"Bearer {service_key}",
    }

    try:
        response = requests.post(url, json=payload, headers=headers, timeout=10)
        response.raise_for_status()
    except requests.HTTPError as exc:
        detail = ""
        try:
            detail = response.json().get("message")  # type: ignore[union-attr]
        except Exception:  # noqa: BLE001
            detail = response.text  # type: ignore[union-attr]
        message = detail or str(exc)
        raise SupabaseAdminError(f"Error creando usuario en Supabase: {message}") from exc
    except requests.RequestException as exc:
        raise SupabaseAdminError(f"No se pudo conectar a Supabase: {exc}") from exc

    try:
        return response.json()
    except ValueError as exc:
        raise SupabaseAdminError("Respuesta inválida de Supabase") from exc


def delete_auth_user(user_id: str) -> None:
    """Elimina un usuario de Supabase Auth."""
    base_url = _get_base_url()
    service_key = _get_service_key()

    url = f"{base_url}/auth/v1/admin/users/{user_id}"
    headers = {
        "apikey": service_key,
        "Authorization": f"Bearer {service_key}",
    }

    try:
        response = requests.delete(url, headers=headers, timeout=10)
        if response.status_code == 404:
            return
        response.raise_for_status()
    except requests.HTTPError as exc:
        detail = ""
        try:
            detail = response.json().get("message")  # type: ignore[union-attr]
        except Exception:  # noqa: BLE001
            detail = response.text  # type: ignore[union-attr]
        message = detail or str(exc)
        raise SupabaseAdminError(f"Error eliminando usuario en Supabase: {message}") from exc
    except requests.RequestException as exc:
        raise SupabaseAdminError(f"No se pudo conectar a Supabase: {exc}") from exc


def update_auth_user(user_id: str, *, password: str | None = None) -> dict:
    """Actualiza atributos del usuario en Supabase Auth (actualmente solo contraseña)."""
    if password is None:
        return {}

    base_url = _get_base_url()
    service_key = _get_service_key()

    url = f"{base_url}/auth/v1/admin/users/{user_id}"
    payload = {"password": password}
    headers = {
        "Content-Type": "application/json",
        "apikey": service_key,
        "Authorization": f"Bearer {service_key}",
    }

    try:
        response = requests.put(url, json=payload, headers=headers, timeout=10)
        response.raise_for_status()
    except requests.HTTPError as exc:
        detail = ""
        try:
            detail = response.json().get("message")  # type: ignore[union-attr]
        except Exception:  # noqa: BLE001
            detail = response.text  # type: ignore[union-attr]
        message = detail or str(exc)
        raise SupabaseAdminError(f"Error actualizando usuario en Supabase: {message}") from exc
    except requests.RequestException as exc:
        raise SupabaseAdminError(f"No se pudo conectar a Supabase: {exc}") from exc

    try:
        return response.json()
    except ValueError as exc:
        raise SupabaseAdminError("Respuesta inválida de Supabase") from exc
