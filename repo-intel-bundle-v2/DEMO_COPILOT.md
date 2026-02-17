# 🤖 Guía Práctica: Tu Primer "Fix" con Repo Intel + Copilot

Esta guía te llevará paso a paso para probar la sinergia entre **Repo Intel Bundle** (el diagnosticador) y **GitHub Copilot** (el cirujano).

## Prerrequisito
Asegúrate de tener instalado **GitHub Copilot** en tu VS Code.

---

## Paso 1: El Diagnóstico (Repo Intel)
Ya hemos ejecutado el análisis para el proyecto `jmgp_audit`. Vamos a usar el reporte de seguridad generado para **Flask** como ejemplo.

1.  En VS Code, navega y abre este archivo:
    👉 `outputs/jmgp_audit/agents/pallets_flask.vuln_detective.md`

2.  Observa el hallazgo bajo **Key Findings**:
    > "Missing Dependencies Lockfile (Low)"

    *Este es el contexto que le daremos a Copilot.*

---

## Paso 2: El Contexto (Tu Código)
Para que Copilot arregle el código, necesita ver el código.

1.  Abre una nueva terminal en VS Code.
2.  Clona el repositorio de Flask (si no lo tienes) para simular que es tu proyecto:
    ```bash
    git clone https://github.com/pallets/flask.git temp_flask
    code temp_flask
    ```
    *(O simplemente abre cualquier archivo `pyproject.toml` o `requirements.txt` de un proyecto tuyo).*

---

## Paso 3: La Magia (Context Injection)
Ahora vamos a conectar los puntos.

1.  **Divide tu pantalla (Split Editor)**:
    *   Izquierda: `pallets_flask.vuln_detective.md` (El reporte)
    *   Derecha: La terminal o el archivo raíz del proyecto Flask.

2.  Abre **Copilot Chat** (Ctrl+Cmd+I o clic en el icono de chat).

3.  **Escribe el siguiente Prompt**:
    > "@workspace Basado en el reporte de vulnerabilidad abierto 'pallets_flask.vuln_detective.md', genera el archivo de bloqueo de dependencias que falta para cumplir con la recomendación de seguridad."

4.  **Observa la respuesta**:
    Copilot leerá el archivo Markdown, entenderá que falta un `lockfile` (Poetry o Pipenv) y te generará los comandos o el archivo necesario (ej. `pip freeze > requirements.lock`).

---

## Paso 4: Exploración Profunda (UI)
Si Copilot necesita más contexto que el reporte Markdown:

1.  Ejecuta la UI del dashboard:
    ```bash
    python3.12 scripts/run_ui.py
    ```
2.  Ve a la pestaña **"Results Explorer"**.
3.  Selecciona el Finding de "Missing Lockfile".
4.  Copia la sección **"Remediation"** y pégala en Copilot Chat:
    > "Explícame por qué esto es un riesgo de seguridad según este texto: [Pegar Texto]"

---

## Resumen
La clave es: **Repo Intel genera el "Qué" (Markdown), y Copilot ejecuta el "Cómo" (Código).**
Mantén siempre los reportes (`outputs/...`) abiertos mientras trabajas para darle "Superpoderes de Contexto" a Copilot.
