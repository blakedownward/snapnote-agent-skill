#!/usr/bin/env python3
"""Validate a SnapNote packet and optionally decode/crop its screenshot.

The helper writes decoded images only to the operating system temp directory.
It never writes generated image files into the repository.
"""

from __future__ import annotations

import argparse
import base64
import json
import mimetypes
import re
import sys
import tempfile
from pathlib import Path
from typing import Any


DATA_URI_RE = re.compile(r"^data:(?P<mime>image/[a-zA-Z0-9.+-]+);base64,(?P<data>.*)$", re.DOTALL)
SUPPORTED_IMAGE_ENCODINGS = {"base64"}


def fail(message: str) -> int:
    print(f"ERROR: {message}", file=sys.stderr)
    return 1


def load_packet(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise ValueError("packet root must be a JSON object")
    return data


def validate_packet(packet: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    for field in ["schemaVersion", "kind", "id", "createdAt", "source", "target", "note"]:
        if field not in packet:
            errors.append(f"missing top-level field: {field}")

    source = packet.get("source")
    target = packet.get("target")
    note = packet.get("note")

    if packet.get("kind") != "snapnote":
        errors.append("kind must be 'snapnote'")
    if not isinstance(source, dict):
        errors.append("source must be an object")
    elif source.get("type") != "screenshot":
        errors.append("source.type must be 'screenshot'")
    if not isinstance(target, dict):
        errors.append("target must be an object")
    else:
        if target.get("type") != "rect":
            errors.append("target.type must be 'rect'")
        if target.get("coordinateSpace") != "sourceImagePixels":
            errors.append("target.coordinateSpace must be 'sourceImagePixels'")
        for field in ["x", "y", "width", "height"]:
            if not isinstance(target.get(field), (int, float)):
                errors.append(f"target.{field} must be a number")
    if not isinstance(note, dict):
        errors.append("note must be an object")
    elif not isinstance(note.get("text"), str) or not note.get("text", "").strip():
        errors.append("note.text must be present and non-empty")

    return errors


def temp_output_path(packet_id: str, suffix: str) -> Path:
    safe_id = re.sub(r"[^a-zA-Z0-9_.-]+", "-", packet_id).strip("-") or "snapnote"
    temp_dir = Path(tempfile.mkdtemp(prefix=f"snapnote-{safe_id}-"))
    return temp_dir / f"{safe_id}{suffix}"


def source_image_payload(packet: dict[str, Any]) -> tuple[str, str] | None:
    source = packet.get("source")
    if not isinstance(source, dict):
        return None

    image = source.get("image")
    if isinstance(image, dict):
        data = image.get("data")
        if not isinstance(data, str) or not data.strip():
            return None

        encoding = image.get("encoding", "base64")
        if not isinstance(encoding, str) or encoding.lower() not in SUPPORTED_IMAGE_ENCODINGS:
            raise ValueError("source.image.encoding must be 'base64'")

        mime = image.get("mimeType", "image/png")
        if not isinstance(mime, str) or not mime.strip():
            mime = "image/png"
        return data.strip(), mime.strip()

    if isinstance(image, str) and image.strip():
        print("WARNING: source.image is a legacy string shape; use source.image.data with mimeType and encoding.", file=sys.stderr)
        return image.strip(), "image/png"

    return None


def decode_source_image(packet: dict[str, Any]) -> Path | None:
    image_payload = source_image_payload(packet)
    if image_payload is None:
        return None

    payload, mime = image_payload
    match = DATA_URI_RE.match(payload)
    if match:
        mime = match.group("mime")
        payload = match.group("data")

    suffix = mimetypes.guess_extension(mime) or ".img"
    output_path = temp_output_path(str(packet.get("id", "snapnote")), suffix)
    output_path.write_bytes(base64.b64decode(payload, validate=True))
    return output_path


def resolve_image_ref(packet_path: Path, packet: dict[str, Any]) -> Path | None:
    source = packet.get("source")
    if not isinstance(source, dict):
        return None
    image_ref = source.get("imageRef")
    if not isinstance(image_ref, str) or not image_ref.strip():
        return None

    ref_path = Path(image_ref)
    candidates = [ref_path]
    if not ref_path.is_absolute():
        candidates = [packet_path.parent / ref_path, Path.cwd() / ref_path]
    for candidate in candidates:
        if candidate.exists():
            return candidate.resolve()
    return None


def crop_target(packet: dict[str, Any], image_path: Path) -> Path | None:
    try:
        from PIL import Image
    except ImportError:
        print("Crop skipped: Pillow is not installed. Install/use existing Pillow if the target repo already has it.")
        return None

    target = packet["target"]
    x = int(round(target["x"]))
    y = int(round(target["y"]))
    width = int(round(target["width"]))
    height = int(round(target["height"]))
    output_path = temp_output_path(str(packet.get("id", "snapnote")), ".crop.png")

    with Image.open(image_path) as image:
        image.crop((x, y, x + width, y + height)).save(output_path)
    return output_path


def print_context_hints(packet: dict[str, Any]) -> None:
    context = packet.get("context")
    if not isinstance(context, dict):
        print("Context: none")
        return

    for key in ["route", "page", "component", "componentHints", "selectedElement"]:
        if key in context:
            print(f"Context {key}: {json.dumps(context[key], ensure_ascii=True)}")


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description="Validate a SnapNote packet and optionally decode/crop its screenshot.")
    parser.add_argument("packet", type=Path, help="Path to a .snapnote.json packet")
    parser.add_argument("--decode", action="store_true", help="Decode source.image.data to an OS temp file when present")
    parser.add_argument("--crop", action="store_true", help="Crop target rect to an OS temp file when Pillow is available")
    args = parser.parse_args(argv)

    try:
        packet = load_packet(args.packet)
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        return fail(f"could not read packet: {exc}")

    errors = validate_packet(packet)
    if errors:
        for error in errors:
            print(f"INVALID: {error}", file=sys.stderr)
        return 1

    print(f"Valid SnapNote: {packet['id']}")
    print(f"Note: {packet['note']['text']}")
    print_context_hints(packet)

    image_path: Path | None = None
    if args.decode or args.crop:
        try:
            image_path = decode_source_image(packet)
        except (ValueError, OSError) as exc:
            return fail(f"could not decode source.image data: {exc}")
        if image_path:
            print(f"Decoded source.image: {image_path}")
        else:
            image_path = resolve_image_ref(args.packet, packet)
            if image_path:
                print(f"Using source.imageRef: {image_path}")
            else:
                print("No decodable source.image.data or accessible source.imageRef found.")

    if args.crop and image_path:
        try:
            crop_path = crop_target(packet, image_path)
        except Exception as exc:
            return fail(f"could not crop target rect: {exc}")
        if crop_path:
            print(f"Cropped target rect: {crop_path}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
