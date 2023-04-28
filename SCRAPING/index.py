from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium import webdriver
from bs4 import BeautifulSoup
import re
import pandas as pd
import time
import json
import traceback
from API.load_dateset import load as load_dataset



def main():
    scrape()

def scrape():
    # "form1:txtActorCedula"
    # "form1:txtDemandadoCedula"
    # authors = ["0968599020001", "0992339411001"]

    authors = ["0968599020001", "0992339411001"]

    # authors = ["0992339411001"]

    defendants = ["1791251237001", "0968599020001"]

    # defendants = []

    dataset = []
    for author in authors:
        process = search(author, "form1:txtActorCedula")
        dataset.append({
            "id": author,
            "type": "author",
            "process": process
        })

    for defendant in defendants:
        process = search(defendant ,"form1:txtDemandadoCedula")
        dataset.append({
            "id": defendant,
            "type": "defendant",
            "process": process
        })


    # Exportar los datos a un archivo JSON
    with open("../API/dataset.json", "w") as f:
        json.dump(dataset, f)

    load_dataset()


def search(id, input):
    # Crea una instancia del driver de Selenium y carga la página web
    driver = webdriver.Chrome()
    url = "https://consultas.funcionjudicial.gob.ec/informacionjudicial/public/informacion.jsf"
    driver.get(url)

    # Encuentra el input y el botón de búsqueda utilizando sus selectores CSS
    input_identification = driver.find_element(By.ID, input)
    boton_buscar = driver.find_element(By.ID, "form1:butBuscarJuicios")

    # Ingresa la identificación en el input y hace clic en el botón de búsqueda
    input_identification.send_keys(id)
    boton_buscar.click()

    # Espera a que se cargue la tabla de resultados antes de continuar
    wait = WebDriverWait(driver, 100)

    wait.until(EC.invisibility_of_element_located(
        (By.CSS_SELECTOR,
         "div.ui-dialog-titlebar.ui-widget-header.ui-helper-clearfix.ui-corner-top.ui-draggable-handle")))
    wait.until(EC.visibility_of_element_located((By.ID, "form1:dataTableJuicios2_paginator_bottom")))

    # Obtén el código HTML de la página y analízalo con BeautifulSoup
    html = driver.page_source
    soup = BeautifulSoup(html, "html.parser")

    # Encuentra la tabla de resultados utilizando su selector CSS
    table_result = soup.find("tbody", {"id": "form1:dataTableJuicios2_data"})

    # Extrae los datos de la tabla utilizando BeautifulSoup y convierte los datos en una lista de diccionarios
    data = []

    paginator = driver.find_element(By.XPATH, "/html/body/div[1]/div[4]/div/div/form[3]/div/div/div[5]/div/div/div[3]/span")

    num_a_tags = len(paginator.find_elements(By.TAG_NAME, "a"))

    for x in range(0, num_a_tags):
        try:

            wait = WebDriverWait(driver, 10)
            wait.until(EC.invisibility_of_element_located((By.CSS_SELECTOR,
                                                           "div.ui-dialog-titlebar.ui-widget-header.ui-helper-clearfix.ui-corner-top.ui-draggable-handle")))
            time.sleep(2)

            page_html = driver.page_source
            page_soup = BeautifulSoup(page_html, "html.parser")

            # Encuentra la tabla de resultados utilizando su selector CSS
            table_result = page_soup.find("tbody", {"id": "form1:dataTableJuicios2_data"})

            # Extrae los datos de la tabla utilizando BeautifulSoup y convierte los datos en una lista de diccionarios

            rows = table_result.findAll("tr")

            for row in rows:

                cols = row.find_all("td")
                cols = [col.text.strip() for col in cols]
                print("Registro :", cols[0])

                # details = []

                details = detail_data(row, driver)

                if len(cols) >= 4:  # Estos son los datos que quiero extraer

                    data.append({
                        "no": cols[0],
                        "date": cols[1],
                        "process": cols[2],
                        "action": cols[3],
                        "details": details
                    })

            # Encuentra el botón para ir a la siguiente página y haz clic en él

            next_button = driver.find_element(By.XPATH, "/html/body/div[1]/div[4]/div/div/form[3]/div/div/div[5]/div/div/div[3]/a[3]")

            if "ui-state-disabled" in next_button.get_attribute("class").split():
                break
            else:
                next_button.click()

        except NoSuchElementException:
            break

        except Exception as e:
            print(e)
            traceback.print_exc()
            print("Error en el scraping ")
            break

    return data




    # df = pd.DataFrame(data)

    # Cierra el driver de Selenium
    # driver.quit()



def detail_data(row, driver):
    # Encuentra el botón dentro de esa fila
    button_detail = row.find("button", {"class": "abrir"})

    detail_wait = WebDriverWait(driver, 100)


    # Encuentra el botón dentro del driver
    button_detail = driver.find_element(By.ID, button_detail["id"])

    button_detail.click()

    detail_wait.until(EC.visibility_of_element_located((By.XPATH, '//*[@id="formJuicioDialogo:juicioDialogo"]')))

    page_html = driver.page_source
    page_soup = BeautifulSoup(page_html, "html.parser")

    # Encuentra la tabla de resultados utilizando su selector CSS
    table_result = page_soup.find("tbody", {"id": "formJuicioDialogo:dataTableMovimiento_data"})

    # Extrae los datos de la tabla utilizando BeautifulSoup y convierte los datos en una lista de diccionarios

    rows = table_result.findAll("tr")

    details = []

    for row in rows:

        # detail = []

        cols = row.find_all('td')

        if len(cols) >= 3 :
            detail = process_detail(row, driver)

            values = [col.get_text(strip=True) for col in cols]
            details.append({
                "no": values[0],
                "date": values[1],
                "actor": values[2],
                "Defendant": values[3],
                "details": detail
            })

    try:
        close_modal_x = driver.find_element(By.XPATH, '/html/body/div[1]/div[4]/div/div/form[2]/div/div[1]/a')
        close_modal_x.click()
    except:
        time.sleep(2)
        close_modal_button = driver.find_element(By.XPATH, '//*[@id="formJuicioDialogo:btnCancelar"]')
        close_modal_button.click()


    # close_modal_x = driver.find_element(By.XPATH, '/html/body/div[1]/div[4]/div/div/form[2]/div/div[1]/a')
    # close_modal_x.click()

    detail_wait.until(EC.invisibility_of_element_located((By.XPATH, '//*[@id="formJuicioDialogo:juicioDialogo"]')))

    return details


def process_detail(row, driver):
    button_detail = row.find("button", {"class": "abrir"})
    # Encuentra el botón dentro del driver
    details = []
    button_detail = driver.find_element(By.ID, button_detail["id"])
    if button_detail is not None:

        button_detail.click()

        detail_wait = WebDriverWait(driver, 100)

        detail_wait.until(EC.visibility_of_element_located((By.XPATH, '//*[@id="juicioDetalleDialogo"]')))

        page_html = driver.page_source
        page_soup = BeautifulSoup(page_html, "html.parser")

        # Encuentra la tabla de resultados utilizando su selector CSS
        table_result = page_soup.find("tbody", {"id": "formJuicioDetalle:dataTable_data"})

        # Extrae los datos de la tabla utilizando BeautifulSoup y convierte los datos en una lista de diccionarios


        rows = table_result.findAll("tr")

        for row in rows:
            cols_content = row.find_all('td')
            if len(cols_content) >= 3:
                values = [col.get_text(strip=True) for col in cols_content]
                details.append({
                    "date": values[0],
                    "detail": values[1]
                })


        try:
            close_modal_x = driver.find_element(By.XPATH, '/html/body/div[1]/div[4]/div/div/div[1]/div[1]/a')
            close_modal_x.click()
        except:
            time.sleep(2)
            close_modal_button = driver.find_element(By.XPATH, '//*[@id="formJuicioDetalle:btnCerrar"]')
            close_modal_button.click()

        detail_wait.until(EC.invisibility_of_element_located((By.XPATH, '//*[@id="juicioDetalleDialogo"]')))

    return details


if __name__ == "__main__":
    main()
