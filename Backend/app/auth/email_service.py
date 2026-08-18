from __future__ import annotations

import mimetypes
import os
import smtplib
import ssl
from dataclasses import dataclass
from email.message import EmailMessage
from pathlib import Path
from urllib.parse import urlencode


class EmailConfigurationError(RuntimeError):
    pass


class EmailDeliveryError(RuntimeError):
    pass


@dataclass(frozen=True)
class SMTPConfig:
    host: str
    port: int
    username: str
    password: str
    from_email: str
    from_name: str
    use_tls: bool
    timeout_seconds: int


@dataclass(frozen=True)
class GmailSMTPConfig(SMTPConfig):
    frontend_reset_url: str


def _get_required_env(name: str) -> str:
    value = os.getenv(name)
    if value is None or not value.strip():
                                      
        raise EmailConfigurationError(f"La variable de entorno {name} no está configurada")
         
    return value.strip()


def _get_int_env(name: str, default: int, minimum: int = 1) -> int:
    raw = (os.getenv(name) or "").strip()
    if not raw:
        return default
    try:
        value = int(raw)
    except ValueError as exc:
                                      
        raise EmailConfigurationError(f"{name} debe ser un número entero") from exc
                  
    if value < minimum:
                                      
        raise EmailConfigurationError(f"{name} debe ser mayor o igual a {minimum}")
         
    return value


def _get_bool_env(name: str, default: bool) -> bool:
    raw = (os.getenv(name) or "").strip().casefold()
    if not raw:
        return default
    if raw in {"1", "true", "yes", "si", "sí", "on"}:
        return True
    if raw in {"0", "false", "no", "off"}:
        return False
    raise EmailConfigurationError(f"{name} debe ser true/false")
                                     
     


def get_smtp_config() -> SMTPConfig:
    username = _get_required_env("SMTP_USERNAME")
    return SMTPConfig(
                           
        host=(os.getenv("SMTP_HOST") or "smtp.gmail.com").strip() or "smtp.gmail.com",
        port=_get_int_env("SMTP_PORT", 587),
        username=username,
        password=_get_required_env("SMTP_PASSWORD"),
        from_email=(os.getenv("SMTP_FROM_EMAIL") or username).strip() or username,
        from_name=(os.getenv("SMTP_FROM_NAME") or "Sakura Reclutamiento").strip() or "Sakura Reclutamiento",
                                  
        use_tls=_get_bool_env("SMTP_USE_TLS", True),
        timeout_seconds=_get_int_env("SMTP_TIMEOUT_SECONDS", 15),
    )


def get_gmail_smtp_config() -> GmailSMTPConfig:
    base = get_smtp_config()
    return GmailSMTPConfig(
        **base.__dict__,
        frontend_reset_url=_get_required_env("FRONTEND_RESET_PASSWORD_URL"),
    )


def build_password_reset_url(base_url: str, token: str) -> str:
    separator = "&" if "?" in base_url else "?"
    return f"{base_url}{separator}{urlencode({'token': token})}"


def _smtp_send(message: EmailMessage, config: SMTPConfig) -> None:
    context = ssl.create_default_context()
    try:
        with smtplib.SMTP(config.host, config.port, timeout=config.timeout_seconds) as smtp:
            smtp.ehlo()
            if config.use_tls:
                smtp.starttls(context=context)
                smtp.ehlo()
            smtp.login(config.username, config.password)
            smtp.send_message(message)
    except (smtplib.SMTPException, OSError) as exc:
        raise EmailDeliveryError("No fue posible enviar el correo") from exc


def send_email(
    *,
    to_emails: list[str],
    subject: str,
    body_text: str,
    cc_emails: list[str] | None = None,
    body_html: str | None = None,
    attachments: list[tuple[str, Path]] | None = None,
) -> None:
    if not to_emails:
        raise EmailConfigurationError("Debe existir al menos un destinatario")
    config = get_smtp_config()
    message = EmailMessage()
    message["Subject"] = subject
    message["From"] = f"{config.from_name} <{config.from_email}>"
    message["To"] = ", ".join(to_emails)
    if cc_emails:
        message["Cc"] = ", ".join(cc_emails)
    message.set_content(body_text)
    if body_html:
        message.add_alternative(body_html, subtype="html")

    for filename, raw_path in attachments or []:
        path = Path(raw_path)
        if not path.is_file():
            raise EmailDeliveryError(f"Adjunto no encontrado: {filename}")
        mime, _ = mimetypes.guess_type(filename)
        maintype, subtype = (mime.split("/", 1) if mime else ("application", "octet-stream"))
        with path.open("rb") as fh:
            message.add_attachment(fh.read(), maintype=maintype, subtype=subtype, filename=filename)

    _smtp_send(message, config)


def send_password_reset_email(*, to_email: str, token: str, expiration_minutes: int) -> None:
    config = get_gmail_smtp_config()
    reset_url = build_password_reset_url(config.frontend_reset_url, token)

    message = EmailMessage()
    message["Subject"] = "Restablecimiento de contraseña - Sakura"
    message["From"] = f"{config.from_name} <{config.from_email}>"
    message["To"] = to_email

    plain_text = f"""Hola,

Recibimos una solicitud para restablecer la contraseña de tu cuenta en Sakura.

Ingresa al siguiente enlace para definir una nueva contraseña:
{reset_url}

El enlace vence en {expiration_minutes} minutos y solo puede utilizarse una vez.

Si no solicitaste este cambio, puedes ignorar este correo.

Sakura Reclutamiento
"""

    html_text = f"""<html><body>
      
        
<p>Hola,</p>
<p>Recibimos una solicitud para restablecer la contraseña de tu cuenta en Sakura.</p>
<p><a href="{reset_url}">Restablecer contraseña</a></p>
<p>El enlace vence en <strong>{expiration_minutes} minutos</strong> y solo puede utilizarse una vez.</p>
<p>Si no solicitaste este cambio, puedes ignorar este correo.</p>
<p>Sakura Reclutamiento</p>
</body></html>"""
       
   

    message.set_content(plain_text)
    message.add_alternative(html_text, subtype="html")

                                          

    try:
        _smtp_send(message, config)
    except EmailDeliveryError as exc:
                        
                                           
                  
                       
                              
                                              
                           
                                                        
                                      
                                                   
                                 
        raise EmailDeliveryError("No fue posible enviar el correo de recuperación") from exc
                  
