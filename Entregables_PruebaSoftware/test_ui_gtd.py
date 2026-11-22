"""Pruebas UI con Selenium (Python + pytest). Cubren casos TC-CAP, TC-CLA, TC-ORG, TC-EJE.
Selectores supuestos: atributos data-testid. Ajustar a la app real."""
import time
import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def tid(name):
    return (By.CSS_SELECTOR, f"[data-testid='{name}']")


def capture(driver, text):
    box = driver.find_element(*tid("capture-input"))
    box.clear()
    box.send_keys(text, Keys.ENTER)


def inbox_items(driver):
    return driver.find_elements(*tid("inbox-item"))


def wait_count(driver, expected, timeout=8):
    WebDriverWait(driver, timeout).until(lambda d: len(inbox_items(d)) == expected)


# ---------- CAPTURA ----------
def test_TC_CAP_01_captura_texto_simple(logged_driver):
    d = logged_driver
    antes = len(inbox_items(d))
    capture(d, "Llamar al dentista")
    wait_count(d, antes + 1)
    assert "Llamar al dentista" in inbox_items(d)[-1].text


def test_TC_CAP_03_captura_vacia(logged_driver):
    d = logged_driver
    antes = len(inbox_items(d))
    capture(d, "")
    time.sleep(1)
    assert len(inbox_items(d)) == antes


def test_TC_CAP_04_solo_espacios(logged_driver):
    d = logged_driver
    antes = len(inbox_items(d))
    capture(d, "     ")
    time.sleep(1)
    assert len(inbox_items(d)) == antes


def test_TC_CAP_07_caracteres_especiales(logged_driver):
    d = logged_driver
    texto = "Reunión ñ á #@&"
    antes = len(inbox_items(d))
    capture(d, texto)
    wait_count(d, antes + 1)
    assert texto in inbox_items(d)[-1].text


def test_TC_CAP_08_script_se_escapa(logged_driver):
    d = logged_driver
    antes = len(inbox_items(d))
    capture(d, "<script>alert(1)</script>")
    wait_count(d, antes + 1)
    # Si el script se ejecutara, aparecería una alerta
    from selenium.common.exceptions import NoAlertPresentException
    with pytest.raises(NoAlertPresentException):
        d.switch_to.alert
    assert "<script>" in inbox_items(d)[-1].text


def test_TC_CAP_13_persistencia_al_recargar(logged_driver):
    d = logged_driver
    capture(d, "Persistente QA")
    antes = len(inbox_items(d))
    d.refresh()
    WebDriverWait(d, 10).until(EC.visibility_of_element_located(tid("capture-input")))
    assert len(inbox_items(d)) == antes
    assert any("Persistente QA" in i.text for i in inbox_items(d))


# ---------- CLARIFICAR ----------
def test_TC_CLA_01_clarificar_como_proxima_accion(logged_driver):
    d = logged_driver
    capture(d, "Enviar informe")
    WebDriverWait(d, 8).until(EC.element_to_be_clickable(tid("inbox-item"))).click()
    d.find_element(*tid("clarify-next-action")).click()
    d.find_element(*tid("clarify-save")).click()
    d.get(d.current_url.split("#")[0] + "#/next-actions")
    WebDriverWait(d, 8).until(EC.visibility_of_element_located(tid("action-item")))
    assert any("Enviar informe" in a.text for a in d.find_elements(*tid("action-item")))


def test_TC_CLA_07_sin_destino_no_guarda(logged_driver):
    d = logged_driver
    capture(d, "Sin destino")
    WebDriverWait(d, 8).until(EC.element_to_be_clickable(tid("inbox-item"))).click()
    d.find_element(*tid("clarify-save")).click()
    assert d.find_element(*tid("clarify-error")).is_displayed()


# ---------- EJECUCIÓN ----------
def test_TC_EJE_01_completar_accion(logged_driver):
    d = logged_driver
    d.get(d.current_url.split("#")[0] + "#/next-actions")
    acciones = WebDriverWait(d, 8).until(lambda x: x.find_elements(*tid("action-item")))
    texto = acciones[0].text
    acciones[0].find_element(*tid("action-check")).click()
    WebDriverWait(d, 8).until(lambda x: texto not in [a.text for a in x.find_elements(*tid("action-item"))])


def test_TC_EJE_08_doble_clic_idempotente(logged_driver):
    d = logged_driver
    d.get(d.current_url.split("#")[0] + "#/next-actions")
    acciones = WebDriverWait(d, 8).until(lambda x: x.find_elements(*tid("action-item")))
    chk = acciones[0].find_element(*tid("action-check"))
    from selenium.webdriver import ActionChains
    ActionChains(d).double_click(chk).perform()
    time.sleep(1)
    # No debe haber error visible ni estado inconsistente
    assert not d.find_elements(*tid("error-banner"))


# ---------- INTERFAZ ----------
@pytest.mark.parametrize("ancho,alto", [(375, 800), (768, 1024), (1366, 900)])
def test_TC_UI_responsive_sin_desborde(logged_driver, ancho, alto):
    d = logged_driver
    d.set_window_size(ancho, alto)
    d.refresh()
    WebDriverWait(d, 10).until(EC.visibility_of_element_located(tid("capture-input")))
    scroll_w = d.execute_script("return document.documentElement.scrollWidth")
    assert scroll_w <= ancho + 1, f"Desborde horizontal a {ancho}px ({scroll_w}px)"
