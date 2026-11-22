# Scripts automatizados – App To Do List GTD

## Ejecución
```bash
pip install -r requirements.txt
export GTD_BASE_URL=https://staging... GTD_API_URL=https://staging.../api GTD_USER=... GTD_PASS=...
pytest -v --html=reporte_ejecucion.html --self-contained-html
```

## Validación humana (criterio de salida)
Los scripts se generaron con apoyo de Codex App y deben validarse antes de darlos por buenos:
1. Revisar que cada prueba corresponda a su caso TC-XXX-NN en `Entregables_TestPlan_GTD.xlsx`.
2. Ajustar selectores (`data-testid`) y endpoints a la app real.
3. Ejecutar 3 veces seguidas en Staging para detectar pruebas inestables (flaky).
4. Registrar en Jira cualquier fallo con la etiqueta `origen-codex` si el error está en el script y no en la app.
