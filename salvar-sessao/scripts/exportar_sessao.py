#!/usr/bin/env python3
"""Exporta o transcript (.jsonl) de uma sessao do Claude Code para Markdown.

Uso:
  exportar_sessao.py DESTINO.md [--session-id UUID] [--cwd DIR] [--sobrescrever]
"""
import argparse
import json
import os
import re
import sys
from datetime import datetime
from pathlib import Path


def projeto_dir(cwd):
    nome = re.sub(r"[^A-Za-z0-9]", "-", os.path.abspath(cwd))
    return Path.home() / ".claude" / "projects" / nome


def achar_transcript(cwd, session_id):
    base = projeto_dir(cwd)
    if session_id:
        f = base / f"{session_id}.jsonl"
        if f.exists():
            return f
        achados = list(Path.home().glob(f".claude/projects/*/{session_id}.jsonl"))
        if achados:
            return achados[0]
        sys.exit(f"ERRO: transcript da sessao {session_id} nao encontrado")
    arquivos = sorted(base.glob("*.jsonl"), key=lambda p: p.stat().st_mtime, reverse=True)
    if not arquivos:
        sys.exit(f"ERRO: nenhum transcript em {base}")
    return arquivos[0]


def cerca(texto, lang=""):
    maior = max((len(m) for m in re.findall(r"`+", texto)), default=0)
    c = "`" * max(3, maior + 1)
    return f"{c}{lang}\n{texto}\n{c}"


def texto_de_resultado(conteudo):
    if isinstance(conteudo, str):
        return conteudo
    partes = []
    for b in conteudo or []:
        if not isinstance(b, dict):
            partes.append(str(b))
        elif b.get("type") == "text":
            partes.append(b.get("text", ""))
        else:
            partes.append(f"[{b.get('type', 'bloco')} omitido]")
    return "\n".join(partes)


def detalhes(titulo, corpo):
    return f"<details>\n<summary>{titulo}</summary>\n\n{corpo}\n\n</details>"


def render_bloco(b, papel):
    t = b.get("type")
    if t == "text":
        txt = b.get("text", "").strip()
        return txt or None
    if t == "tool_use":
        entrada = json.dumps(b.get("input", {}), ensure_ascii=False, indent=2)
        return detalhes(f"Ferramenta: <code>{b.get('name')}</code>", cerca(entrada, "json"))
    if t == "tool_result":
        txt = texto_de_resultado(b.get("content"))
        erro = " (erro)" if b.get("is_error") else ""
        return detalhes(f"Resultado da ferramenta{erro}", cerca(txt))
    if t == "image":
        return "[imagem omitida]"
    return None


def converter(transcript, cwd):
    linhas, sid, primeira = [], None, None
    ultima = None
    n_msgs = 0
    for raw in transcript.read_text(encoding="utf-8").splitlines():
        try:
            d = json.loads(raw)
        except json.JSONDecodeError:
            continue
        sid = sid or d.get("sessionId")
        tipo = d.get("type")
        if tipo == "system" and d.get("subtype") == "local_command":
            cmd = d.get("commandRun") or {}
            if cmd.get("command"):
                linhas.append(f"### Comando local\n\n`/{cmd['command']} {cmd.get('args', '')}`".rstrip())
            continue
        if tipo not in ("user", "assistant") or d.get("isSidechain"):
            continue
        msg = d.get("message") or {}
        conteudo = msg.get("content")
        if isinstance(conteudo, str):
            conteudo = [{"type": "text", "text": conteudo}]
        partes = [p for p in (render_bloco(b, tipo) for b in conteudo or [] if isinstance(b, dict)) if p]
        if not partes:
            continue
        ts = d.get("timestamp")
        primeira = primeira or ts
        ultima = ts or ultima
        eh_resultado = all(b.get("type") == "tool_result" for b in conteudo if isinstance(b, dict))
        if tipo == "assistant":
            rotulo = "Claude"
        elif eh_resultado:
            rotulo = "Resultado"
        else:
            rotulo = "Usuario" + (" (meta)" if d.get("isMeta") else "")
        corpo = "\n\n".join(partes)
        if d.get("isMeta") and tipo == "user":
            corpo = detalhes("Conteúdo injetado (meta)", corpo)
        n_msgs += 1
        hora = f" — {ts}" if ts else ""
        linhas.append(f"## {rotulo}{hora}\n\n" + corpo)

    cab = [
        "# Sessao Claude Code",
        "",
        f"- Session ID: `{sid}`",
        f"- Diretorio: `{os.path.abspath(cwd)}`",
        f"- Inicio: {primeira}",
        f"- Ultima mensagem: {ultima}",
        f"- Mensagens exportadas: {n_msgs}",
        f"- Exportado em: {datetime.now().isoformat(timespec='seconds')}",
        f"- Origem: `{transcript}`",
        "",
        "---",
        "",
    ]
    return "\n".join(cab) + "\n" + "\n\n".join(linhas) + "\n"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("destino")
    ap.add_argument("--session-id")
    ap.add_argument("--cwd", default=os.getcwd())
    ap.add_argument("--sobrescrever", action="store_true")
    a = ap.parse_args()

    destino = Path(os.path.expanduser(a.destino))
    if destino.is_dir():
        sys.exit(f"ERRO: {destino} e um diretorio; informe o caminho completo com nome do arquivo")
    if destino.suffix.lower() != ".md":
        destino = destino.with_name(destino.name + ".md")
    if destino.exists() and not a.sobrescrever:
        sys.exit(f"EXISTE: {destino} ja existe; confirme com o usuario e rode com --sobrescrever")

    transcript = achar_transcript(a.cwd, a.session_id)
    md = converter(transcript, a.cwd)
    destino.parent.mkdir(parents=True, exist_ok=True)
    destino.write_text(md, encoding="utf-8")
    print(f"OK: {destino} ({len(md.encode('utf-8'))} bytes) a partir de {transcript}")


if __name__ == "__main__":
    main()
