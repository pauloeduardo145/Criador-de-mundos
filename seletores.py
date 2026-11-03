"""Seletores de arquivo/pasta do Criador de Mundos.

No Windows e no macOS o tkinter.filedialog já usa o diálogo nativo.
No Linux tenta Zenity (GTK) ou KDialog (Qt) e, se nenhum estiver
instalado, cai para o seletor do Tk.

Todas as funções retornam o caminho (str) ou None se o usuário cancelar.
"""

import os
import shutil
import subprocess
import sys
from tkinter import filedialog


def _linux() -> bool:
    return sys.platform.startswith("linux")


def _padroes(extensoes):
    """['png', 'jpg'] -> ['*.png', '*.PNG', '*.jpg', '*.JPG'] (Linux diferencia maiúsculas)."""
    padroes = []
    for ext in extensoes or []:
        ext = ext.lstrip(".*")
        if not ext:
            continue
        padroes += [f"*.{ext.lower()}", f"*.{ext.upper()}"]
    return padroes


def _ambiente_limpo():
    """Ambiente para programas externos.

    O PyInstaller aponta LD_LIBRARY_PATH para as bibliotecas embutidas no
    executável, o que pode quebrar o Zenity/KDialog do sistema. Aqui
    restauramos o valor original.
    """
    env = dict(os.environ)
    if getattr(sys, "frozen", False):
        original = env.pop("LD_LIBRARY_PATH_ORIG", None)
        if original is not None:
            env["LD_LIBRARY_PATH"] = original
        else:
            env.pop("LD_LIBRARY_PATH", None)
    return env


def _rodar(comando):
    """Executa o comando e devolve a saída limpa, ou None se cancelado/erro."""
    try:
        r = subprocess.run(comando, capture_output=True, text=True,
                           env=_ambiente_limpo())
    except OSError:
        return None
    saida = r.stdout.strip()
    return saida if r.returncode == 0 and saida else None


def _filtros_tk(descricao, extensoes):
    if not extensoes:
        return [("Todos os arquivos", "*.*")]
    return [(descricao, " ".join(f"*.{e.lstrip('.*')}" for e in extensoes)),
            ("Todos os arquivos", "*.*")]


def _inicio(pasta_inicial):
    pasta = pasta_inicial or os.path.expanduser("~")
    return pasta if pasta.endswith(os.sep) else pasta + os.sep


def _extra_tk(parent):
    return {"parent": parent} if parent is not None else {}


# --------------------------------------------------------------------------
def escolher_arquivo(titulo="Selecionar arquivo", extensoes=None,
                     descricao="Arquivos", pasta_inicial=None, parent=None):
    """Abre um arquivo existente. extensoes: ex. ['png', 'jpg']."""
    if _linux():
        padroes = _padroes(extensoes)
        if shutil.which("zenity"):
            cmd = ["zenity", "--file-selection", f"--title={titulo}",
                   f"--filename={_inicio(pasta_inicial)}"]
            if padroes:
                cmd.append(f"--file-filter={descricao} | {' '.join(padroes)}")
                cmd.append("--file-filter=Todos os arquivos | *")
            return _rodar(cmd)
        if shutil.which("kdialog"):
            filtro = f"{' '.join(padroes)}|{descricao}" if padroes else ""
            cmd = ["kdialog", "--title", titulo, "--getopenfilename",
                   _inicio(pasta_inicial)]
            if filtro:
                cmd.append(filtro)
            return _rodar(cmd)

    caminho = filedialog.askopenfilename(
        title=titulo,
        initialdir=pasta_inicial or os.path.expanduser("~"),
        filetypes=_filtros_tk(descricao, extensoes),
        **_extra_tk(parent),
    )
    return caminho or None


def salvar_arquivo(titulo="Salvar arquivo", extensoes=None,
                   descricao="Arquivos", nome_inicial="", pasta_inicial=None,
                   parent=None):
    """Escolhe onde salvar um arquivo."""
    ext_padrao = f".{extensoes[0].lstrip('.*')}" if extensoes else ""

    if _linux():
        padroes = _padroes(extensoes)
        inicio = os.path.join(pasta_inicial or os.path.expanduser("~"), nome_inicial)
        caminho = None
        if shutil.which("zenity"):
            cmd = ["zenity", "--file-selection", "--save", "--confirm-overwrite",
                   f"--title={titulo}", f"--filename={inicio}"]
            if padroes:
                cmd.append(f"--file-filter={descricao} | {' '.join(padroes)}")
            caminho = _rodar(cmd)
        elif shutil.which("kdialog"):
            cmd = ["kdialog", "--title", titulo, "--getsavefilename", inicio]
            if padroes:
                cmd.append(f"{' '.join(padroes)}|{descricao}")
            caminho = _rodar(cmd)
        else:
            caminho = ""  # nenhum seletor externo: usa o do Tk abaixo

        if caminho is None:
            return None  # usuário cancelou
        if caminho:
            if ext_padrao and not os.path.splitext(caminho)[1]:
                caminho += ext_padrao
            return caminho

    caminho = filedialog.asksaveasfilename(
        title=titulo,
        initialdir=pasta_inicial or os.path.expanduser("~"),
        initialfile=nome_inicial,
        defaultextension=ext_padrao,
        filetypes=_filtros_tk(descricao, extensoes),
        **_extra_tk(parent),
    )
    return caminho or None


def escolher_pasta(titulo="Selecionar pasta", pasta_inicial=None, parent=None):
    """Escolhe um diretório."""
    if _linux():
        if shutil.which("zenity"):
            return _rodar(["zenity", "--file-selection", "--directory",
                           f"--title={titulo}",
                           f"--filename={_inicio(pasta_inicial)}"])
        if shutil.which("kdialog"):
            return _rodar(["kdialog", "--title", titulo, "--getexistingdirectory",
                           _inicio(pasta_inicial)])

    caminho = filedialog.askdirectory(
        title=titulo, initialdir=pasta_inicial or os.path.expanduser("~"),
        **_extra_tk(parent))
    return caminho or None
