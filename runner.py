import json
import os
import pdfkit

footer = "Max Muster, 05-2024"
title = "Example"


def remove_prefix(filename):
    """
    Entfernt den Präfix vor dem ersten Unterstrich im Dateinamen.

    Args:
        filename (str): Der Dateiname.

    Returns:
        str: Der Dateiname ohne Präfix.
    """
    index = filename.find('_')
    return filename[index + 1:] if index != -1 else filename


def generate_inhaltsverzeichnis(data):
    """
    Generiert das Inhaltsverzeichnis als HTML.

    Args:
        data (list): Die Liste der Dateien und ihrer Inhalte.

    Returns:
        str: Das generierte HTML-Inhaltsverzeichnis.
    """
    html = """
    <h1 class="center">""" + title + """</h1>
    <h2>Inhaltsverzeichnis</h2>
    <ul>
    """

    for file in data:
        for cell in file:
            html += f"<li>{remove_prefix(cell)}</li>"

    html += """
    </ul>
    <p class="right">Heiner Giefers, 05-2024</p>
    <div class='page-break'></div>
    """
    return html


def create_pdf(filtered_content):
    """
    Erstellt eine PDF-Datei aus dem gefilterten Inhalt.

    Args:
        filtered_content (list): Der gefilterte Inhalt der Dateien.
    """
    html_content = """
    <head>
        <title>Lösungen</title>
        <meta charset="UTF-8">
        <style>
            .page-break { page-break-before: always; }
            hr { border: 1px solid black; margin: 20px 0; }
            .center { text-align: center; }
            .right { text-align: right; }
            body { user-select: none; }
        </style>
    </head>
    <body>
    """

    for file in filtered_content:
        for cell in file:
            html_content += f"<h1>{remove_prefix(cell)}</h1><hr/>"
            for number in file[cell]:
                for row in number['source']:
                    if "### BEGIN SOLUTION" not in row and "### END SOLUTION" not in row:
                        html_content += f"<pre>{row}</pre>"
                html_content += "<br/><hr/><br/>"
            html_content += "<p class='right'>" + footer +"</p><div class='page-break'></div>"

    html_content += "</body>"
    complete_html = generate_inhaltsverzeichnis(filtered_content) + html_content
    pdfkit.from_string(complete_html, "target/solutions.pdf")


def process_notebook_files_in_directory(directory):
    """
    Durchläuft alle Dateien im angegebenen Verzeichnis und sucht nach
    '### BEGIN SOLUTION' und '### END SOLUTION' Zellen in .ipynb Dateien.

    Args:
        directory (str): Das Verzeichnis, das durchsucht werden soll.

    Returns:
        list: Eine Liste mit gefundenen Lösungen.
    """
    solutions = []
    for root, _, files in os.walk(directory):
        for file_name in files:
            if file_name.endswith('.ipynb'):
                file_path = os.path.join(root, file_name)
                try:
                    found_solutions = []
                    with open(file_path, "r", encoding='utf-8') as file:
                        notebook_content = json.load(file)
                        if "cells" in notebook_content:
                            for cell in notebook_content["cells"]:
                                if "source" in cell:
                                    source = "".join(cell["source"])
                                    if "### BEGIN SOLUTION" in source and "### END SOLUTION" in source:
                                        found_solutions.append(cell)
                    solutions.append({file_name.replace(".ipynb", ""): found_solutions})
                except Exception as e:
                    print(f"Konnte Datei {file_path} nicht öffnen: {e}")
    return solutions


def read_paths_from_file(file_path):
    """
    Liest die relativen Pfade aus der angegebenen Datei und gibt sie als Liste zurück.

    Args:
        file_path (str): Der Pfad zur Datei, die die relativen Pfade enthält.

    Returns:
        list: Eine Liste der Pfade.
    """
    with open(file_path, 'r') as file:
        paths = file.readlines()
    return [path.strip() for path in paths]


def main():
    """
    Hauptfunktion des Programms. Liest die Pfade ein, verarbeitet die Notizbuchdateien
    und erstellt ein PDF-Dokument mit den gefundenen Lösungen.
    """
    paths_file = 'files.txt'
    paths = read_paths_from_file(paths_file)

    data = []
    for relative_path in paths:
        if os.path.isdir(relative_path):
            data.extend(process_notebook_files_in_directory(relative_path))
        else:
            print(f"{relative_path} ist kein gültiges Verzeichnis.")

    create_pdf(data)


if __name__ == "__main__":
    main()
