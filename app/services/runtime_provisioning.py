"""Provisionamento local, atômico e verificável dos runtimes Windows."""

from __future__ import annotations

import hashlib
import json
import os
import shutil
import stat
import subprocess
import threading
import urllib.error
import urllib.request
import uuid
import zipfile
from collections.abc import Callable
from pathlib import Path, PurePosixPath
from urllib.parse import urlparse

from app.config import default_data_dir
from app.services.runtime_manifest import (
    ComponentSpec,
    InstalledFile,
    RuntimeManifest,
    load_runtime_manifest,
)

ProgressCallback = Callable[[int, str], None]
DOWNLOAD_CHUNK_BYTES = 1024 * 1024
DOWNLOAD_TIMEOUT_SECONDS = 60
DISK_MARGIN_BYTES = 128 * 1024**2


class ProvisioningError(RuntimeError):
    """Falha segura e explicável no provisionamento."""


def default_runtime_dir() -> Path:
    return default_data_dir() / "runtime-v2"


def component_directory(component: ComponentSpec, runtime_dir: Path | None = None) -> Path:
    root = (runtime_dir or default_runtime_dir()).expanduser().resolve()
    return root / component.identifier / component.version


def _ensure_allowed_url(url: str, allowed_hosts: frozenset[str]) -> None:
    parsed = urlparse(url)
    if (
        parsed.scheme != "https"
        or not parsed.hostname
        or parsed.hostname.lower() not in allowed_hosts
        or parsed.username
        or parsed.password
    ):
        raise ProvisioningError("O servidor redirecionou para uma origem não permitida.")


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        while chunk := stream.read(DOWNLOAD_CHUNK_BYTES):
            digest.update(chunk)
    return digest.hexdigest()


def _remove_controlled_tree(path: Path, root: Path) -> None:
    resolved = path.resolve()
    resolved_root = root.resolve()
    if resolved == resolved_root or not resolved.is_relative_to(resolved_root):
        raise ProvisioningError("Recusa de remover diretório fora do runtime controlado.")
    if resolved.exists():
        shutil.rmtree(resolved)


def _atomic_json(path: Path, payload: object) -> None:
    temporary = path.with_name(f".{path.name}.{uuid.uuid4().hex}.tmp")
    try:
        with temporary.open("w", encoding="utf-8", newline="\n") as stream:
            json.dump(payload, stream, ensure_ascii=False, indent=2)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        temporary.replace(path)
    except Exception:
        temporary.unlink(missing_ok=True)
        raise


def download_verified_file(
    *,
    url: str,
    sha256: str,
    size_bytes: int,
    destination: Path,
    allowed_hosts: frozenset[str],
    cancel_event: threading.Event | None = None,
    progress: ProgressCallback | None = None,
    timeout: int = DOWNLOAD_TIMEOUT_SECONDS,
) -> Path:
    """Baixa para arquivo temporário e só promove após tamanho e SHA exatos."""
    if size_bytes <= 0 or len(sha256) != 64:
        raise ProvisioningError("Metadados de integridade incompletos.")
    _ensure_allowed_url(url, allowed_hosts)
    destination = destination.expanduser().resolve()
    destination.parent.mkdir(parents=True, exist_ok=True)
    temporary = destination.with_name(f".{destination.name}.{uuid.uuid4().hex}.part")
    callback = progress or (lambda _percent, _message: None)
    digest = hashlib.sha256()
    received = 0
    request = urllib.request.Request(  # noqa: S310 - HTTPS e host já validados
        url,
        headers={"User-Agent": "TropaTranscribeLocal/0.3.1-alpha"},
    )
    try:
        with (
            urllib.request.urlopen(request, timeout=timeout) as response,  # noqa: S310
            temporary.open("xb") as output,
        ):
            final_url = response.geturl()
            _ensure_allowed_url(final_url, allowed_hosts)
            declared = response.headers.get("Content-Length", "")
            if declared.isdigit() and int(declared) != size_bytes:
                raise ProvisioningError("O servidor informou tamanho diferente do manifesto.")
            while chunk := response.read(DOWNLOAD_CHUNK_BYTES):
                if cancel_event and cancel_event.is_set():
                    raise InterruptedError("Download cancelado; arquivo parcial removido.")
                received += len(chunk)
                if received > size_bytes:
                    raise ProvisioningError("O download excedeu o tamanho fixado no manifesto.")
                output.write(chunk)
                digest.update(chunk)
                callback(
                    min(99, int(received * 100 / size_bytes)),
                    f"{received / 1024**2:.1f} de {size_bytes / 1024**2:.1f} MiB",
                )
            output.flush()
            os.fsync(output.fileno())
        if received != size_bytes:
            raise ProvisioningError(
                f"Download incompleto: recebidos {received} de {size_bytes} bytes."
            )
        if digest.hexdigest() != sha256.lower():
            raise ProvisioningError("SHA-256 do download não corresponde ao manifesto.")
        temporary.replace(destination)
        callback(100, "Download validado.")
        return destination
    except (urllib.error.URLError, TimeoutError) as exc:
        raise ProvisioningError(
            "Falha de rede. Verifique conexão, proxy ou firewall e tente novamente."
        ) from exc
    finally:
        temporary.unlink(missing_ok=True)


def _safe_archive_name(name: str) -> str:
    if "\\" in name:
        raise ProvisioningError("Arquivo ZIP contém separador de caminho inseguro.")
    path = PurePosixPath(name)
    if path.is_absolute() or any(part in {"", ".", ".."} for part in path.parts):
        raise ProvisioningError("Arquivo ZIP contém path traversal.")
    if path.parts and ":" in path.parts[0]:
        raise ProvisioningError("Arquivo ZIP contém caminho absoluto do Windows.")
    return path.as_posix()


def _validate_archive_members(archive: zipfile.ZipFile) -> dict[str, zipfile.ZipInfo]:
    members: dict[str, zipfile.ZipInfo] = {}
    casefolded: set[str] = set()
    for item in archive.infolist():
        raw_name = item.filename.rstrip("/")
        if not raw_name and item.is_dir():
            continue
        name = _safe_archive_name(raw_name)
        folded = name.casefold()
        if folded in casefolded:
            raise ProvisioningError("Arquivo ZIP contém nomes duplicados ou ambíguos.")
        casefolded.add(folded)
        mode = (item.external_attr >> 16) & 0xFFFF
        if stat.S_ISLNK(mode):
            raise ProvisioningError("Arquivo ZIP contém link simbólico não permitido.")
        if item.flag_bits & 0x1:
            raise ProvisioningError("Arquivo ZIP criptografado não é aceito.")
        if not item.is_dir():
            members[name] = item
    return members


def _extract_one(
    archive: zipfile.ZipFile,
    member: zipfile.ZipInfo,
    record: InstalledFile,
    staging: Path,
    cancel_event: threading.Event | None,
) -> None:
    if member.file_size != record.size_bytes:
        raise ProvisioningError(f"Tamanho interno inesperado: {record.path}.")
    destination = staging.joinpath(*PurePosixPath(record.path).parts)
    if not destination.resolve().is_relative_to(staging.resolve()):
        raise ProvisioningError("Destino de extração saiu da área de staging.")
    destination.parent.mkdir(parents=True, exist_ok=True)
    digest = hashlib.sha256()
    written = 0
    with archive.open(member, "r") as source, destination.open("xb") as output:
        while chunk := source.read(DOWNLOAD_CHUNK_BYTES):
            if cancel_event and cancel_event.is_set():
                raise InterruptedError("Instalação cancelada; staging removido.")
            written += len(chunk)
            if written > record.size_bytes:
                raise ProvisioningError(f"Conteúdo expandido excedeu o limite: {record.path}.")
            output.write(chunk)
            digest.update(chunk)
        output.flush()
        os.fsync(output.fileno())
    if written != record.size_bytes or digest.hexdigest() != record.sha256:
        raise ProvisioningError(f"Integridade do arquivo instalado falhou: {record.path}.")


def _write_component_state(
    staging: Path,
    component: ComponentSpec,
    manifest: RuntimeManifest,
) -> None:
    _atomic_json(
        staging / "component.json",
        {
            "schema_version": 1,
            "manifest_sha256": manifest.digest,
            "manifest_verified_at": manifest.verified_at,
            "name": component.name,
            "identifier": component.identifier,
            "version": component.version,
            "architecture": component.architecture,
            "source_url": component.url,
            "archive_sha256": component.sha256,
            "archive_size_bytes": component.size_bytes,
            "license": component.license,
            "homepage": component.homepage,
            "source": component.source,
            "entry_point": component.entry_point,
            "diagnostic_command": list(component.diagnostic_command),
            "installed_files": [
                {
                    "path": item.path,
                    "size_bytes": item.size_bytes,
                    "sha256": item.sha256,
                }
                for item in component.files
            ],
        },
    )


def validate_component(
    identifier: str,
    *,
    runtime_dir: Path | None = None,
    manifest: RuntimeManifest | None = None,
) -> Path:
    trusted = manifest or load_runtime_manifest()
    try:
        component = trusted.components[identifier]
    except KeyError as exc:
        raise ProvisioningError(f"Componente desconhecido: {identifier}.") from exc
    directory = component_directory(component, runtime_dir)
    if not directory.is_dir():
        raise FileNotFoundError(f"{component.name} ainda não foi instalado.")
    expected = {item.path.casefold(): item for item in component.files}
    actual_files = {
        path.relative_to(directory).as_posix().casefold(): path
        for path in directory.rglob("*")
        if path.is_file() and path.name != "component.json"
    }
    if set(actual_files) != set(expected):
        raise ProvisioningError(f"{component.name} contém arquivos ausentes ou inesperados.")
    for relative, record in expected.items():
        candidate = actual_files[relative]
        if candidate.stat().st_size != record.size_bytes or _sha256(candidate) != record.sha256:
            raise ProvisioningError(f"{component.name} foi alterado: {record.path}.")
    state_path = directory / "component.json"
    try:
        state = json.loads(state_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ProvisioningError(f"Registro local de {component.name} é inválido.") from exc
    if (
        not isinstance(state, dict)
        or state.get("manifest_sha256") != trusted.digest
        or state.get("archive_sha256") != component.sha256
    ):
        raise ProvisioningError(f"Registro local de {component.name} não é confiável.")
    entry_point = directory.joinpath(*PurePosixPath(component.entry_point).parts)
    if not entry_point.is_file():
        raise ProvisioningError(f"Executável de {component.name} não foi localizado.")
    return entry_point.resolve()


def is_component_ready(
    identifier: str,
    *,
    runtime_dir: Path | None = None,
    manifest: RuntimeManifest | None = None,
) -> bool:
    try:
        validate_component(identifier, runtime_dir=runtime_dir, manifest=manifest)
        return True
    except (FileNotFoundError, OSError, ValueError, RuntimeError):
        return False


def install_component(
    identifier: str,
    *,
    runtime_dir: Path | None = None,
    repair: bool = False,
    cancel_event: threading.Event | None = None,
    progress: ProgressCallback | None = None,
    manifest: RuntimeManifest | None = None,
) -> Path:
    """Instala ou repara um componente sem compilador e sem privilégios de admin."""
    trusted = manifest or load_runtime_manifest()
    if trusted.platform != "windows" or trusted.architecture != "x86_64":
        raise ProvisioningError("Este manifesto não atende ao Windows x64.")
    try:
        component = trusted.components[identifier]
    except KeyError as exc:
        raise ProvisioningError(f"Componente desconhecido: {identifier}.") from exc
    if not repair:
        try:
            return validate_component(identifier, runtime_dir=runtime_dir, manifest=trusted)
        except (FileNotFoundError, OSError, ValueError, RuntimeError):
            pass
    root = (runtime_dir or default_runtime_dir()).expanduser().resolve()
    root.mkdir(parents=True, exist_ok=True)
    required = component.size_bytes + component.installed_size_bytes + DISK_MARGIN_BYTES
    if shutil.disk_usage(root).free < required:
        raise ProvisioningError(
            f"Espaço livre insuficiente. São necessários ao menos {required / 1024**2:.0f} MiB."
        )
    token = uuid.uuid4().hex
    staging = root / f".staging-{identifier}-{token}"
    archive_path = root / f".download-{identifier}-{token}.zip"
    final = component_directory(component, root)
    backup = root / f".backup-{identifier}-{token}"
    callback = progress or (lambda _percent, _message: None)
    staging.mkdir()
    promoted_backup = False
    try:
        download_verified_file(
            url=component.url,
            sha256=component.sha256,
            size_bytes=component.size_bytes,
            destination=archive_path,
            allowed_hosts=trusted.allowed_download_hosts,
            cancel_event=cancel_event,
            progress=lambda percent, message: callback(
                int(percent * 0.7), f"{component.name}: {message}"
            ),
        )
        try:
            with zipfile.ZipFile(archive_path) as archive:
                members = _validate_archive_members(archive)
                total = len(component.files)
                for index, record in enumerate(component.files, start=1):
                    try:
                        member = members[record.archive_path]
                    except KeyError as exc:
                        raise ProvisioningError(
                            f"Arquivo obrigatório ausente no ZIP: {record.archive_path}."
                        ) from exc
                    _extract_one(archive, member, record, staging, cancel_event)
                    callback(
                        70 + int(index * 25 / total),
                        f"{component.name}: validando {index}/{total}",
                    )
        except zipfile.BadZipFile as exc:
            raise ProvisioningError("O download não é um arquivo ZIP válido.") from exc
        _write_component_state(staging, component, trusted)
        final.parent.mkdir(parents=True, exist_ok=True)
        if final.exists():
            final.replace(backup)
            promoted_backup = True
        staging.replace(final)
        try:
            entry = validate_component(identifier, runtime_dir=root, manifest=trusted)
        except Exception:
            if final.exists():
                _remove_controlled_tree(final, root)
            if promoted_backup and backup.exists():
                backup.replace(final)
            raise
        if promoted_backup and backup.exists():
            _remove_controlled_tree(backup, root)
        callback(100, f"{component.name} instalado e validado.")
        return entry
    finally:
        archive_path.unlink(missing_ok=True)
        if staging.exists():
            _remove_controlled_tree(staging, root)
        if backup.exists() and not final.exists():
            backup.replace(final)


def remove_component(identifier: str, *, runtime_dir: Path | None = None) -> None:
    trusted = load_runtime_manifest()
    try:
        component = trusted.components[identifier]
    except KeyError as exc:
        raise ProvisioningError(f"Componente desconhecido: {identifier}.") from exc
    root = (runtime_dir or default_runtime_dir()).expanduser().resolve()
    directory = component_directory(component, root)
    _remove_controlled_tree(directory, root)


def run_component_diagnostic(
    identifier: str,
    *,
    runtime_dir: Path | None = None,
    timeout: int = 20,
) -> subprocess.CompletedProcess[str]:
    trusted = load_runtime_manifest()
    component = trusted.components[identifier]
    executable = validate_component(identifier, runtime_dir=runtime_dir, manifest=trusted)
    arguments = [str(executable), *component.diagnostic_command[1:]]
    bin_dir = executable.parent
    windows = Path(os.environ.get("SYSTEMROOT", r"C:\Windows"))
    clean_path = os.pathsep.join((str(bin_dir), str(windows / "System32"), str(windows)))
    environment = {
        key: value
        for key, value in os.environ.items()
        if key.upper()
        in {
            "SYSTEMROOT",
            "WINDIR",
            "TEMP",
            "TMP",
            "USERPROFILE",
            "LOCALAPPDATA",
            "APPDATA",
            "PATHEXT",
        }
    }
    environment["PATH"] = clean_path
    creation_flags = subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0
    return subprocess.run(
        arguments,
        check=False,
        capture_output=True,
        text=True,
        timeout=timeout,
        cwd=bin_dir,
        env=environment,
        creationflags=creation_flags,
    )
